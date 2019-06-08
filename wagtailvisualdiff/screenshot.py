from future import standard_library
standard_library.install_aliases()
from builtins import str
from wagtail.wagtailcore.models import Page, PageRevision
import requests
from django.core.files.base import ContentFile
import urllib.request, urllib.parse, urllib.error
import hashlib
import json
from PIL import Image
from django.conf import settings
from celery.decorators import task
from io import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from socket import error as SocketError
import errno
from jsondiff import diff

@task
def process_page_published(instance_id, revision_id):
	instance = Page.objects.get(pk=instance_id)
	revision = PageRevision.objects.get(pk=revision_id)

	page_url = instance.full_url

	from .models import PageRevisionScreenshot
	prs = PageRevisionScreenshot.objects.create(page_revision=revision)

	# Call Screenshotlayer with Desktop Settings
	params = {
		'fullpage': '1',
		'width': '700',
		'delay': '5',
		'force': '1'
	}

	retrynum = 0
	while True:
		fp = urllib.request.urlopen(screenshotlayer(page_url, params))
		retrynum += 1
		if fp.getcode() == 200:
			try:
				prs.screenshot.save(str(revision.id) + ".png", ContentFile(fp.read()))
				break
			except SocketError as e:
				if e.errno not in [errno.ECONNRESET, errno.ETIMEDOUT, errno.EHOSTDOWN]:
					raise e
				pass
		else:
			import time
			time.sleep(retrynum*6)
			if retrynum == 9:
				raise Exception("Screenshotlayer did not return Image")

	# Call Screenshotlater with Mobile Settings
	params = {
		'fullpage': '1',
		'width': '250',
		'viewport': '375x667',
		'delay': '5',
		'force': '1',
		'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A366 Safari/600.1.4'
	}
	retrynum = 0
	while True:
		fp2 = urllib.request.urlopen(screenshotlayer(page_url, params))
		retrynum += 1
		if fp2.getcode() == 200:
			try:
				prs.mobile_screenshot.save(str(revision.id) + "_mobile.png", ContentFile(fp2.read()))
				break
			except SocketError as e:
				if e.errno not in [errno.ECONNRESET, errno.ETIMEDOUT, errno.EHOSTDOWN]:
					raise e
				pass
		else:
			import time
			time.sleep(retrynum*6)
			if retrynum == 9:
				raise Exception("Screenshotlayer did not return Image")

	diff_filename = str(revision.id) + "_diff.png"
	try:
		prs.diff.save(diff_filename, get_diff(prs))
	except IOError:
		prs.diff.save(diff_filename, ContentFile(fp.read()))
	send_slack_notification(instance.title, revision.user.get_full_name(), prs)

def get_changes(previous_id, revision_id):
	changes = []
	revision = PageRevision.objects.get(pk=revision_id)
	page_2 = revision.content_json
	prev_revision = PageRevision.objects.get(pk=previous_id)
	page_1 = prev_revision.content_json
	p1_dict = json.loads(page_1)['body']
	p2_dict = json.loads(page_2)['body']
	a_json = json.loads(p1_dict.encode("utf-8"))
	b_json = json.loads(p2_dict.encode("utf-8"))
	raw_diff = diff(a_json, b_json, syntax='symmetric')
	for element in raw_diff:
		if str(element) == "$insert":
			fields = []
			for block in raw_diff[element]:
				fields.append({
						"value": "#" +  str(block[0]) + ": " + block[1]['type'],
						"short": True
					})
			changes.append(
				{
					"title": "Added Blocks",
					"fields": fields,
					"color": "good"
				}
				)
		elif str(element) == "$delete":
			fields = []
			for block in raw_diff[element]:
				fields.append({
						"value": "#" +  str(block[0]) + ": " + block[1]['type'],
						"short": True
					})
			changes.append(
				{
					"title": "Removed Blocks",
					"fields": fields,
					"color": "danger"
				}
				)
		else:
			block_diff = raw_diff[element]['value']
			fields = []
			try:
				for value in block_diff:
					fields.append(
						{
							"value": str(value),
							"short": True
						})
				block_type = str(b_json[element]['type'])
			except:
				block_type = str(raw_diff[element]['type'][0])+" to: "+str(raw_diff[element]['type'][1])
				fields.append(
					{
						"value": "Complicated Changes: Details in Link"
					})
			changes.append(
				{
					"title": "Changed Block #" + str(element) + ": " + block_type,
					"fields": fields,
					"color": "warning"
				}
				)
	if not changes:
		changes.append(
			{
				"title": "No fields were changed",
				"color": "good"
			})
	return changes

def screenshotlayer(url, args):
	# set your access key, secret keyword and target URL
	access_key = settings.SCREENSHOTLAYER_ACCESS_KEY
	secret_keyword = settings.SCREENSHOTLAYER_SECRET_KEYWORD

	# encode URL
	query = urllib.parse.urlencode(dict(url=url, **args))
	# generate md5 secret key
	secret_key = hashlib.md5('{}{}'.format(url, secret_keyword)).hexdigest()

	return settings.SCREENSHOTLAYER_URL + "?access_key=%s&secret_key=%s&%s" % (access_key, secret_key, query)

def get_diff(prs):
	# requests a Diff screenshot for two IDs and returns the image as a Django File
	diff_url = settings.HOSTNAME + "/wagtailvisualdiff/%s/for_sc" % str(prs.page_revision.id)
	params = {
		'fullpage': '1',
		'width': '900',
		'viewport': '1200x100',
		'delay': '15',
		'force': '1',
		'user_agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
	}
	url = screenshotlayer(diff_url, params)
	retrynum = 0
	while True:
		response = requests.get(url, stream=True)
		retrynum += 1
		if response.status_code == 200:
			img = Image.open(StringIO(response.content))
			break
		else:
			import time
			time.sleep(retrynum*6)
			if retrynum == 9:
				raise Exception("Screenshotlayer did not return Image")

	# resize
	if img.size[0] > settings.SCREENSHOT_DIFF_MAX_HEIGHT:
		baseheight = settings.SCREENSHOT_DIFF_MAX_HEIGHT
		height_proportion = (baseheight / float(img.size[1]))
		width_resized = int( float(img.size[0]) * float(height_proportion) )
		img = img.resize((width_resized, baseheight), Image.ANTIALIAS)

	# Create a file-like object to write thumb data
	thumb_io = StringIO()
	img.save(thumb_io, format='JPEG')

	# Create a new Django file-like object to be used in models as ImageField using
	# InMemoryUploadedFile.
	return InMemoryUploadedFile(thumb_io, None, 'diff.png', 'image/jpeg', thumb_io.len, None)

def send_slack_notification(name, user, prs):
	has_previous, previous = prs.get_previous()

	revision = prs.page_revision
	revisions = revision.page.revisions.order_by('-created_at')
	aslist = list(revisions.values_list('id', flat=True))
	index = aslist.index(int(prs.page_revision.id))
	if index < len(aslist)-1:
		previous_id = aslist[index+1]
		prev_revision = PageRevision.objects.get(pk=previous_id)

		try:
			from .models import PageRevisionScreenshot
			PageRevisionScreenshot.objects.get(page_revision=previous_id)
			values = {
				"channel": settings.SLACK_CHANNEL,
				"username": "the tail wagger",
				"icon_url": settings.SCREENSHOT_BOT_SLACK_ICON,
				"text": name + " was published by " + user,
				"attachments": [
					{
						"fallback": "Click the Link to see the full diff",
						"title": "Diff between Revision " + str(previous.page_revision.id) + " and " + str(prs.page_revision.id),
						"title_link": "%s/wagtailvisualdiff/%s/to_previous" % (settings.HOSTNAME, str(prs.page_revision.id)),
						"image_url": prs.diff.url,
					}
				] + get_changes(previous_id, prs.page_revision.id),
			}
		except ObjectDoesNotExist:
			values = {
				"channel": settings.SLACK_CHANNEL,
				"username": "the tail wagger",
				"icon_url": settings.SCREENSHOT_BOT_SLACK_ICON,
				"text": name + " was published by " + user + ". Unfortunately we are missing a screenshot, but here is the detailed Diff: %s/wagtailvisualdiff/%s/to_previous" % (settings.HOSTNAME, str(prs.page_revision.id)),
				"attachments": get_changes(previous_id, prs.page_revision.id),
			}
	else:
		values = {
			"channel": settings.SLACK_CHANNEL,
			"username": "the tail wagger",
			"icon_url": settings.SCREENSHOT_BOT_SLACK_ICON,
			"text": "New Page: " + name + " was published by " + user + ". " + prs.page_revision.page.url,
			"attachments": [
				{
					"fallback": "Click the Link to see the new page",
					"image_url": prs.screenshot.url,
				}
			],
		}
	headers = {'Content-type' : 'application/json'}
	requests.post(settings.SCREENSHOT_SLACK_WEBHOOK, data=json.dumps(values), headers=headers)

@task
def process_page_unpublished(instance_id):
	instance = Page.objects.get(pk=instance_id)

	values = {
			"channel": settings.SLACK_CHANNEL,
			"username": "the tail wagger",
			"icon_url": settings.SCREENSHOT_BOT_SLACK_ICON,
			"text": instance.title + " was unpublished! %s/cms/admin/pages/%s/edit/" % (settings.HOSTNAME, instance_id),
		}
	headers = {'Content-type' : 'application/json'}
	requests.post(settings.SCREENSHOT_SLACK_WEBHOOK, data=json.dumps(values), headers=headers)

def process_page_published_async(**kwargs):
	process_page_published.delay(kwargs['instance'].pk, kwargs['revision'].pk)

def process_page_unpublished_async(**kwargs):
	process_page_unpublished.delay(kwargs['instance'].pk)
