from django.conf.urls import url

from . import views

urlpatterns = [
	# ex: /wagtailvisualdiff/
	url(r'^$', views.index, name='index'),
	# ex: /wagtailvisualdiff/1234/to_current/
	url(r'^(?P<revision_id>[0-9]+)/to_current/$', views.visual_diff_current, name='diff'),
	# ex: /wagtailvisualdiff/1234/to_previous/
	url(r'^(?P<revision_id>[0-9]+)/to_previous/$', views.visual_diff_previous, name='diff'),
	# ex: /wagtailvisualdiff/1234/for_sc
	url(r'^(?P<revision_id>[0-9]+)/for_sc/$', views.visual_diff_only, name='diff_only'),
]