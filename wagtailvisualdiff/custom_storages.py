from builtins import str
from storages.backends.s3boto import S3BotoStorage
from django.conf import settings
from django.utils.deconstruct import deconstructible

@deconstructible
class ScreenshotStorage(S3BotoStorage):
	if settings.SCREENSHOT_BUCKET:
		bucket_name = str(settings.SCREENSHOT_AWS_BUCKET_NAME)