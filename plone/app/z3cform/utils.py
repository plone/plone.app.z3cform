# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from zope.component.hooks import getSite


try:
    from zope.globalrequest import getRequest
    getRequest  # pyflakes
except ImportError:
    # Fake it
    getRequest = object


def closest_content(context=None):
    """Try to find a usable context, with increasing agression"""
    # Normally, we should be given a useful context (e.g the page)
    c = context
    c = _valid_context(c)
    if c is not None:
        return c
    # Subforms (e.g. DataGridField) may not have a context set, find out
    # what page is being published
    c = getattr(getRequest(), 'PUBLISHED', None)
    c = _valid_context(c)
    if c is not None:
        return c
    # During widget traversal nothing is being published yet, use getSite()
    c = getSite()
    c = _valid_context(c)
    if c is not None:
        return c
    raise ValueError('Cannot find suitable context to bind to source')


def _valid_context(context):
    """Walk up until finding a content item."""
    # Avoid loops. The object id is used as context may not be hashable
    seen = set()
    while context is not None and id(aq_base(context)) not in seen:
        seen.add(id(aq_base(context)))
        if (IContentish.providedBy(context) or IFolderish.providedBy(context)):
            return context
        parent = getattr(context, '__parent__', None)
        if parent is None:
            parent = getattr(context, 'context', None)
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
        ret = [
            call_callables(v, *args, **kwargs)
            for v in value
        ]
    elif isinstance(value, tuple):
        ret = tuple(
            call_callables(v, *args, **kwargs)
            for v in value
        )
    elif isinstance(value, dict):
        ret = {
            k: call_callables(v, *args, **kwargs)
            for k, v in value.items()
        }
    return ret
