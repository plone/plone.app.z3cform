from Products.CMFCore import utils as cmfutils
from zope import interface
import persistent.wref
import z3c.formwidget.query.interfaces
import zope.schema.interfaces
import zope.schema.vocabulary
import logging


logger = logging.getLogger('plone.app.z3cform')


class ArchetypesContentSource(object):
    interface.implements(z3c.formwidget.query.interfaces.IQuerySource)

    def __init__(self, context):
        logger.warn("Deprecation Warning\nplone.app.z3cform.queryselect.ArchetypesContentSource "
                    "is deprecated and will be removed in Plone 4.1")
        self.context = context

    def __contains__(self, uid):
        """Verify the item exists."""
        return bool(self.catalog(uid=uid))

    def __iter__(self):
        return [].__iter__()

    @property
    def catalog(self):
        return cmfutils.getToolByName(self.context, 'portal_catalog')

    def getTermByToken(self, token):
        uid = token
        brains = self.catalog(UID=uid)
        if len(brains) > 0:
            return self._term_for_brain(brains[0])
        raise LookupError(token)

    def getTerm(self, value):
        uid = value
        brains = self.catalog(UID=uid)
        if len(brains) > 0:
            return self._term_for_brain(brains[0])
        raise LookupError(value)

    def search(self, query_string, limit=20):
        brains = self.catalog(SearchableText=query_string)[:limit]
        return map(self._term_for_brain, brains)

    def _term_for_brain(self, brain):
        return zope.schema.vocabulary.SimpleTerm(
            brain.UID,
            brain.UID,
            brain.Title
        )


class ArchetypesContentSourceBinder(object):
    interface.implements(zope.schema.interfaces.IContextSourceBinder)

    def __call__(self, context):
        return ArchetypesContentSource(context)


def uid2wref(field):
    class Adapter(object):
        interface.implements(field.interface)

        def __init__(self, context):
            self.context = context

    def _get_items(self):
        items = filter(None, (wref() for wref in self.context.items))
        return [item.UID() for item in items]

    def _set_items(self, uids):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=tuple(uids))
        items = [brain.getObject() for brain in brains]
        self.context.items = map(persistent.wref.WeakRef, items)

    setattr(Adapter, field.__name__, property(_get_items, _set_items))
    return Adapter
