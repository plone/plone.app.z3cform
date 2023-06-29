from Acquisition import aq_base
from copy import deepcopy
from plone.base.navigationroot import get_navigation_root_object
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ISiteRoot
from z3c.form.interfaces import IForm
from zope.component import providedBy
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

import urllib


def closest_content(context=None):
    """Try to find a usable context, with increasing aggression"""
    # Normally, we should be given a useful context (e.g the page)
    c = context
    c = _valid_context(c)
    if c is not None:
        return c
    # Subforms (e.g. DataGridField) may not have a context set, find out
    # what page is being published
    c = getattr(getRequest(), "PUBLISHED", None)
    c = _valid_context(c)
    if c is not None:
        return c
    # During widget traversal nothing is being published yet, use getSite()
    c = getSite()
    c = _valid_context(c)
    if c is not None:
        return c
    raise ValueError("Cannot find suitable context to bind to source")


def _valid_context(context):
    """Walk up until finding a content item."""
    # Avoid loops. The object id is used as context may not be hashable
    seen = set()
    while context is not None and id(aq_base(context)) not in seen:
        seen.add(id(aq_base(context)))
        if IContentish.providedBy(context) or IFolderish.providedBy(context):
            return context
        parent = getattr(context, "__parent__", None)
        if parent is None:
            parent = getattr(context, "context", None)
        context = parent

    return None


def call_callables(value, *args, **kwargs):
    """Walk recursively through data structure and call all callables, passing
    the arguments and keyword arguments to it.
    """
    ret = value
    if callable(value):
        ret = value(*args, **kwargs)
    elif isinstance(value, list):
        ret = [call_callables(v, *args, **kwargs) for v in value]
    elif isinstance(value, tuple):
        ret = tuple(call_callables(v, *args, **kwargs) for v in value)
    elif isinstance(value, dict):
        ret = {k: call_callables(v, *args, **kwargs) for k, v in value.items()}
    return ret


def replace_link_variables_by_paths(context, url):
    """Take an `url` and replace the variables "${navigation_root_url}" and
    "${portal_url}" by the corresponding paths. `context` is the acquisition
    context.
    """

    def _replace_variable_by_path(url, variable, obj):
        path = "/".join(obj.getPhysicalPath())
        return url.replace(variable, path)

    if not url:
        return url

    portal_state = context.restrictedTraverse("@@plone_portal_state")

    if "${navigation_root_url}" in url:
        url = _replace_variable_by_path(
            url,
            "${navigation_root_url}",
            portal_state.navigation_root(),
        )

    if "${portal_url}" in url:
        url = _replace_variable_by_path(
            url,
            "${portal_url}",
            portal_state.portal(),
        )

    return url


def is_absolute(url):
    """Return ``True``, if url is an absolute url.
    See: https://stackoverflow.com/a/8357518/1337474
    """
    return bool(urllib.parse.urlparse(url).netloc)


def is_same_domain(url1, url2):
    """Return ``True``, if url1 is on the same protocol and domain than url2."""
    purl1 = urllib.parse.urlparse(url1)
    purl2 = urllib.parse.urlparse(url2)
    return purl1.scheme == purl2.scheme and purl1.netloc == purl2.netloc


def dict_merge(dict_a, dict_b):
    """Helper method which merges two dictionaries.

    Recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.

    http://www.xormedia.com/recursively-merge-dictionaries-in-python

    :param dict_a: [required] First dictiornary.
    :type dict_a: dict

    :param dict_b: [required] Second dictiornary.
    :type dict_b: dict

    :returns: Merged dictionary.
    :rtype: dict
    """

    if not isinstance(dict_b, dict):
        return dict_b
    result = deepcopy(dict_a)
    for k, v in dict_b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def get_widget_form(widget):
    form = getattr(widget, "form", None)
    if getattr(aq_base(form), "parentForm", None) is not None:
        form = form.parentForm
    return form


def get_portal():
    closest_site = getSite()
    if closest_site is not None:
        for potential_portal in closest_site.aq_chain:
            if ISiteRoot in providedBy(potential_portal):
                return potential_portal


def get_portal_url(context):
    portal = get_portal()
    if portal:
        root = get_navigation_root_object(context, portal)
        if root:
            try:
                return root.absolute_url()
            except AttributeError:
                return portal.absolute_url()
        else:
            return portal.absolute_url()
    return ""


def get_context_url(context):
    if IForm.providedBy(context):
        # Use the request URL if we are looking at an addform
        url = context.request.get("URL")
    elif hasattr(context, "absolute_url"):
        url = context.absolute_url
        if callable(url):
            url = url()
    else:
        url = get_portal_url(context)
    return url


# Invalid XML unicode control characters
# NOTE: these control characters are allowed:
# chr(9) = "\t"
# chr(10) = "\n"
# chr(13) = "\r"

_unicode_ctl_chr_map = dict.fromkeys([x for x in range(32) if x not in (9, 10, 13)])


def remove_invalid_xml_characters(txt):
    # remove occurrences of the unicode "control characters"
    # as they are invalid XML characters
    # see https://en.wikipedia.org/wiki/Valid_characters_in_XML and
    # https://en.wikipedia.org/wiki/C0_and_C1_control_codes
    return txt.translate(_unicode_ctl_chr_map)
