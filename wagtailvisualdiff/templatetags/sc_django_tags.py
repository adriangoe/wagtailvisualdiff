# from django.core.exceptions import ObjectDoesNotExist
from wagtail.core.models import PageRevision
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
    html = ""

    page_revision = PageRevision.objects.get(id=revision_id)
    if page_revision.page.get_latest_revision().pk != revision_id:
        html += (
            "<a href='/wagtailvisualdiff/%d/to_current'>Diff to Current</a>"
            % revision_id
        )
    revisions = page_revision.page.revisions.order_by("-created_at")
    aslist = list(revisions.values_list("id", flat=True))
    if aslist[-1] != revision_id:
        html += (
            "</br><a href='/wagtailvisualdiff/%d/to_previous'>Diff to Previous</a>"
            % revision_id
        )

    try:
        sc = PageRevisionScreenshot.objects.get(page_revision=revision_id)
        html += (
            "</br><img style='max-height: 100px; max-width: 300px;' src='%s' />"
            % sc.diff.url
        )
    except:
        pass
    return html


@register.filter
def to_space(value):
    return value.replace("_", " ")
