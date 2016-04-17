=====
Wagtailvisualdiff
=====

Wagtailvisualdiff is a simple Django app to extend wagtail.
Whenever a new PageRevision is published, a PageRevisionScreenshot Object is created, in which a screenshot of the Desktop and Mobile page is saved.
When a previous PageRevisionScreenshot for the page is available, a Visual Diff will be created and saved with the object.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "wagtailvisualdiff" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'wagtailvisualdiff',
    ]

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
    SCREENSHOT_SLACK_WEBHOOK = 'XXXXXXXXXXXXX' # Configure a new Slack Webhook and paste the URL here if you want to receive notifications in Slakc
    SCREENSHOT_BOT_SLACK_ICON = HOSTNAME + "/public/wagtailvisualdiff/images/tailwagger.png" # Option to customize Slack Picture
    SCREENSHOT_DIFF_MAX_HEIGHT = 600 # Set a Maximum Pixel Height for the Diff Screenshots sent to Slack (For very long Websites)
    SCREENSHOTLAYER_ACCESS_KEY = 'XXXXXXXXXXXXXXXXX' # Configure on https://screenshotlayer.com/
    SCREENSHOTLAYER_SECRET_KEYWORD = 'XXXXXXXXXXXXXXXXX' # If you want encription
    SCREENSHOTLAYER_URL = 'https://api.screenshotlayer.com/api/capture'

5. Publish a new Page. (Visual Diff will only be available the second time you publish a page)
