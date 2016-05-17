from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from models import PageRevisionScreenshot
from wagtail.wagtailcore.models import Page, PageRevision
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from jsondiff import diff
import json

def index(request):
	return HttpResponse("This is the visual-diff page. Pick a Revision number and compare it to it's previous or current public version through the URL: </br> /wagtailvisualdiff/1234/to_previous </br> /wagtailvisualdiff/1234/to_current")

def visual_diff_current(request, revision_id):
	template = loader.get_template('visual-diff/index.html')

	page_revision = get_object_or_404(PageRevision, pk=revision_id)
	current_revision = page_revision.page.get_latest_revision()
	if page_revision.pk != current_revision.pk:
		page_1 = page_revision.content_json
		page_2 = current_revision.content_json
		p1_dict = json.loads(page_1)['body']
		p2_dict = json.loads(page_2)['body']
		difference = diff_json(p1_dict,p2_dict)
		try:
			this_revision_sc = PageRevisionScreenshot.objects.get(page_revision=revision_id)
			current_revision_sc = PageRevisionScreenshot.objects.get(page_revision=current_revision.pk)
			context = {
				'revision1': this_revision_sc,
				'revision2': current_revision_sc,
				'show_all': True,
				'difference': difference,
			}
			return HttpResponse(template.render(context, request))
		except ObjectDoesNotExist:
			template = loader.get_template('visual-diff/simple_diff.html')
			context = {
				'revision1': page_revision,
				'revision2': current_revision,
				'show_all': True,
				'difference': difference,
			}
			return HttpResponse(template.render(context, request))
	else:
		return HttpResponse("<h1>Revision %s is the current revision for this page</h1>" % revision_id)

def visual_diff_previous(request, revision_id):
	template = loader.get_template('visual-diff/index.html')

	page_revision = get_object_or_404(PageRevision, pk=revision_id)
	revisions = page_revision.page.revisions.order_by('-created_at')
	aslist = list(revisions.values_list('id', flat=True))
	index = aslist.index(int(revision_id))
	if index < len(aslist)-1:
		previous_id = aslist[index+1]
		page_2 = page_revision.content_json
		prev_revision = PageRevision.objects.get(pk=previous_id)
		page_1 = prev_revision.content_json
		p1_dict = json.loads(page_1)['body']
		p2_dict = json.loads(page_2)['body']
		difference = diff_json(p1_dict,p2_dict)
		try:
			this_revision_sc = PageRevisionScreenshot.objects.get(page_revision=revision_id)
			prev_revision_sc = PageRevisionScreenshot.objects.get(page_revision=previous_id)
			context = {
				'revision1': prev_revision_sc,
				'revision2': this_revision_sc,
				'show_all': True,
				'difference': difference,
			}
			return HttpResponse(template.render(context, request))
		except ObjectDoesNotExist:
			template = loader.get_template('visual-diff/simple_diff.html')
			context = {
				'revision1': prev_revision,
				'revision2': page_revision,
				'show_all': True,
				'difference': difference,
			}
			return HttpResponse(template.render(context, request))
	else:
		return HttpResponse("<h1>Revision %s is the oldest revision for this page</h1>" % revision_id)

def visual_diff_only(request, revision_id):
	template = loader.get_template('visual-diff/index.html')
	revision = get_object_or_404(PageRevisionScreenshot, page_revision=revision_id)
	has_previous, previous = revision.get_previous()
	if has_previous:
		context = {
			'revision1': previous,
			'revision2': revision,
			'show_all': False,
		}
		return HttpResponse(template.render(context, request))
	else:
		return HttpResponse("This is the oldest Revision")
	return HttpResponse(template.render(context, request))

def diff_json(a, b):
	a_json = json.loads(a.encode("utf-8"))
	b_json = json.loads(b.encode("utf-8"))
	raw_diff = diff(a_json, b_json, syntax='symmetric')

	good_diff = {}
	for element in raw_diff:
		if str(element) == "$insert":
			for block in raw_diff[element]:
				good_diff[block[0]] = ["",block[1]]
		elif str(element) == "$delete":
			for block in raw_diff[element]:
				good_diff[block[0]] = [block[1],""]
		else:
			block_diff = raw_diff[element]['value']
			old = {}
			new = {}
			old_dict = {}
			new_dict = {}
			try:
				for value in block_diff:
					old[value] = block_diff[value][0]
					new[value] = block_diff[value][1]
				old_dict['type'] = b_json[element]['type']
				new_dict['type'] = b_json[element]['type']
				old_dict['value'] = old
				new_dict['value'] = new
				good_diff[element] = [old_dict, new_dict]
			except TypeError:
				old_dict['type'] = "Changed Blocktype"
				new_dict['type'] = "Changed Blocktype"
				old = {}
				new = {}
				old_str = ""
				for (key, val) in block_diff[0].items():
					if isinstance(val, str):
						old_str += key + ":    " + val.encode('ascii', 'xmlcharrefreplace') + "\n"
					elif isinstance(val, int):
						old_str += key + ":    " + str(val).encode('ascii', 'xmlcharrefreplace') + "\n"
					else:
						old_str += key + ":    Empty\n"
				old[raw_diff[element]['type'][0]] = old_str
				new_str = ""
				for (key, val) in block_diff[1].items():
					if isinstance(val, str):
						new_str += key + ":    " + val.encode('ascii', 'xmlcharrefreplace') + "\n"
					elif isinstance(val, int):
						new_str += key + ":    " + str(val).encode('ascii', 'xmlcharrefreplace') + "\n"
					else:
						new_str += key + ":    Empty\n"
				new[raw_diff[element]['type'][1]] = new_str
				old_dict['value'] = old
				new_dict['value'] = new
				good_diff[element] = [old_dict, new_dict]
				print good_diff[element]
			except:
				if 'type' in raw_diff[element]:
					old_dict['type'] = raw_diff[element]['type']
					new_dict['type'] = raw_diff[element]['type']
				old = {}
				new = {}
				old['Complicated Changes'] = block_diff
				new['Complicated Changes'] = block_diff
				old_dict['value'] = old
				new_dict['value'] = new
				good_diff[element] = [old_dict, new_dict]

	return good_diff
