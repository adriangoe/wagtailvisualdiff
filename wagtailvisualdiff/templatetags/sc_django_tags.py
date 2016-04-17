from django.core.exceptions import ObjectDoesNotExist
from wagtailvisualdiff.models import PageRevisionScreenshot
from django import template
register = template.Library()

@register.simple_tag
def get_diff(revision_id):
	"""
	If available:
		prints link to Diff with Current Version of Page
		print link to Diff with previous Version of Page
		print image of diff screenshot to previos screenshot
	"""
	try:
		html = ''
		sc = PageRevisionScreenshot.objects.get(page_revision=revision_id)
		has_current, current = sc.get_current()
		if has_current:
			html += "<a href='/wagtailvisualdiff/%d/to_current'>Diff to Current</a>" % revision_id
		has_previous, previous = sc.get_previous()
		if has_previous:
			html += "</br><a href='/wagtailvisualdiff/%d/to_previous'>Diff to Previous</a>" % revision_id
			try:
				html += "</br><img style='max-height: 100px; max-width: 300px;' src='%s' />" % sc.diff.url
			except:
				pass
		return html
	except ObjectDoesNotExist:
		pass
