from django.db import models
from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailcore.models import PageRevision
from django.core.exceptions import ObjectDoesNotExist
from .custom_storages import ScreenshotStorage
from . import screenshot

# Create your models here.

class PageRevisionScreenshot(models.Model):
	#associates each page revision with a screenshot URL
	page_revision = models.ForeignKey(PageRevision)
	screenshot = models.ImageField(null=True, blank=True, max_length=254, storage=ScreenshotStorage())
	mobile_screenshot = models.ImageField(null=True, blank=True, max_length=254, storage=ScreenshotStorage())
	diff = models.ImageField(null=True, blank=True, max_length=254, storage=ScreenshotStorage())

	def get_current(self):
		current = PageRevision.objects.get(pk=self.page_revision.id).page.get_latest_revision()
		try:
			current_screenshot = PageRevisionScreenshot.objects.get(page_revision=current.pk)
			if current.id != self.page_revision.id:
				return True, current_screenshot
			else:
				return False, current_screenshot
		except ObjectDoesNotExist:
			return False, current

	def get_previous(self):
		page = 	PageRevision.objects.get(pk=self.page_revision.id).page
		revisions = page.revisions.order_by('-created_at')
		aslist = list(revisions.values_list('id', flat=True))
		index = aslist.index(self.page_revision.id)
		if index < len(aslist)-1:
			previous = aslist[index+1]
			try:
				return True, PageRevisionScreenshot.objects.get(page_revision=previous)
			except ObjectDoesNotExist:
				return False, self
		else:
			return False, self

# Trigger notification every time page is published
page_published.connect(screenshot.process_page_published_async)

page_unpublished.connect(screenshot.process_page_unpublished_async)

