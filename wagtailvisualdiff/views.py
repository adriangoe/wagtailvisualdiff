from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from models import PageRevisionScreenshot

def index(request):
	return HttpResponse("This is the visual-diff page")
# Create your views here.
def visual_diff_current(request, revision_id1):
	template = loader.get_template('visual-diff/index.html')
	revision = get_object_or_404(PageRevisionScreenshot, page_revision=revision_id1)
	old_version, current = revision.get_current()
	if old_version:
		context = {
			'revision1': revision,
			'revision2': current,
			'show_all': True,
		}
		return HttpResponse(template.render(context, request))
	else:
		return HttpResponse("Revision %s is the current revision for this page" % revision_id1)

def visual_diff_previous(request, revision_id1):
	template = loader.get_template('visual-diff/index.html')
	revision = get_object_or_404(PageRevisionScreenshot, page_revision=revision_id1)
	has_previous, previous = revision.get_previous()
	if has_previous:
		context = {
			'revision1': previous,
			'revision2': revision,
			'show_all': True,
		}
		return HttpResponse(template.render(context, request))
	else:
		return HttpResponse("This is the oldest Revision")

def visual_diff_only(request, revision_id1):
	template = loader.get_template('visual-diff/index.html')
	revision = get_object_or_404(PageRevisionScreenshot, page_revision=revision_id1)
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