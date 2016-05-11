=====
Wagtailvisualdiff
=====

Wagtailvisualdiff is a simple Django app to extend the wagtail revisions module.
Whenever a new PageRevision is published, a PageRevisionScreenshot Object is created, in which a screenshot of the Desktop and Mobile page is saved.
When a previous PageRevisionScreenshot for the page is available, a Visual Diff will be created and saved with the object.

All screenshots, visual diffs and block by block diff of field changes between revisions can be accessed from /cms/admin/pages/XXXX/revisions/.

A celery task will send the newest visual diff and a quick summary of field changes to the configured slack channel after every new publish event.


Quick start
-----------

1. Add "wagtailvisualdiff" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'wagtailvisualdiff',
        'wagtail.wagtailadmin'
    ]

    Needs to be inculded before wagtailadmin, so we can override the revisions template.

2. Include the wagtailvisualdiff URLconf in your project urls.py like this::

    url(r'^wagtailvisualdiff/', include('wagtailvisualdiff.urls')),

3. Run `python manage.py migrate` to create the PageRevisionScreenshot model.

4. Add the necessary setting in your config/settings.py::

    # A AWS Bucket with CORS permission and unrestricted Headers
    SCREENSHOT_AWS_ACCESS_KEY_ID = 'XXXXXXXXX'
    SCREENSHOT_AWS_SECRET_ACCESS_KEY = 'XXXXXXXXX'
    SCREENSHOT_AWS_BUCKET_NAME = 'XXXXXXXXXX'
    SCREENSHOT_AWS_LOCATION = 'XXXXXXX' # Folder in which to save
    SCREENSHOT_BUCKET = True
    SCREENSHOT_STORAGE_URL = "https://%s.s3.amazonaws.com/%s" % (SCREENSHOT_AWS_BUCKET_NAME, SCREENSHOT_AWS_LOCATION)
    SCREENSHOT_SLACK_WEBHOOK = 'XXXXXXXXXXXXX' # Configure a new Slack Webhook and paste the URL here if you want to receive notifications in Slack
    SLACK_CHANNEL = '#XXXXXXXXXX'
    SCREENSHOT_BOT_SLACK_ICON = HOSTNAME + "/public/wagtailvisualdiff/images/tailwagger.png" # Option to customize Slack Picture
    SCREENSHOT_DIFF_MAX_HEIGHT = 600 # Set a Maximum Pixel Height for the Diff Screenshots sent to Slack (For very long Websites)
    SCREENSHOTLAYER_ACCESS_KEY = 'XXXXXXXXXXXXXXXXX' # Configure on https://screenshotlayer.com/
    SCREENSHOTLAYER_SECRET_KEYWORD = 'XXXXXXXXXXXXXXXXX' # If you want encription
    SCREENSHOTLAYER_URL = 'https://api.screenshotlayer.com/api/capture'

5. Visit the Revisions list for any page: /cms/admin/pages/XXXX/revisions/ and you will get access to field by field diff information.

5. Publish a new Page to receive a notification about it in slack (Visual Diff will only be available the second time you publish a page)
