# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtailvisualdiff.models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageRevisionScreenshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('screenshot', models.ImageField(storage=wagtailvisualdiff.models.ScreenshotStorage(), max_length=254, null=True, upload_to=b'', blank=True)),
                ('mobile_screenshot', models.ImageField(storage=wagtailvisualdiff.models.ScreenshotStorage(), max_length=254, null=True, upload_to=b'', blank=True)),
                ('diff', models.ImageField(storage=wagtailvisualdiff.models.ScreenshotStorage(), max_length=254, null=True, upload_to=b'', blank=True)),
                ('page_revision', models.ForeignKey(to='wagtailcore.PageRevision')),
            ],
        ),
    ]
