from wagtail.wagtailcore.models import Page, PageRevision
import requests
from django.core.files.base import ContentFile
import urllib
import hashlib
import json
from PIL import Image
from django.conf import settings
from celery.decorators import task
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

@task
def process_page_published(instance_id, revision_id):
	print "Hello"
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
		fp = urllib.urlopen(screenshotlayer(page_url, params))
		retrynum += 1
		if fp.getcode() == 200:
			prs.screenshot.save(str(revision.id) + ".png", ContentFile(fp.read()))
			break
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
		fp2 = urllib.urlopen(screenshotlayer(page_url, params))
		retrynum += 1
		if fp2.getcode() == 200:
			prs.mobile_screenshot.save(str(revision.id) + "_mobile.png", ContentFile(fp2.read()))
			break
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

def screenshotlayer(url, args):
	# set your access key, secret keyword and target URL
	access_key = settings.SCREENSHOTLAYER_ACCESS_KEY
	secret_keyword = settings.SCREENSHOTLAYER_SECRET_KEYWORD

	# encode URL
	query = urllib.urlencode(dict(url=url, **args))
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
	if has_previous:
		values = {
			"channel": "#schools-cms",
			"username": "the tail wagger",
			"icon_url": settings.SCREENSHOT_DIFF_URL + "tailwagger2.png",
			"attachments": [
				{
					"fallback": "Click the Link to see the full diff",
					"color": "warning",
					"title": name + " was published by " + user,
					"title_link": "%s/wagtailvisualdiff/%s/to_previous" % (settings.HOSTNAME, str(prs.page_revision.id)),
					"text": "Difference between Revision Number " + str(previous.page_revision.id) + " and " + str(prs.page_revision.id),
					"image_url": prs.diff.url,
				}
			],
		}
	else:
		values = {
			"channel": "#schools-cms",
			"username": "the tail wagger",
			"icon_url": settings.SCREENSHOT_BOT_SLACK_ICON,
			"attachments": [
				{
					"fallback": "Click the Link to see the full diff",
					"color": "warning",
					"title": name + " was published by " + user,
					"title_link": settings.HOSTNAME + "/wagtailvisualdiff/%d/to_current" % str(prs.page_revision.id),
					"text": str(prs.page_revision.id) + " has no screenshot of the previous Version saved",
				}
			],
		}
	headers = {'Content-type' : 'application/json'}
	requests.post(settings.SCREENSHOT_SLACK_WEBHOOK, data=json.dumps(values), headers=headers)

def process_page_published_async(**kwargs):
	process_page_published.delay(kwargs['instance'].pk, kwargs['revision'].pk)
