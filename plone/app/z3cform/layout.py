# -*- coding: utf-8 -*-
import zope.deferredimport


zope.deferredimport.deprecated(
    'Import from plone.z3cform.layout instead.',
    FormWrapper='plone.z3cform.layout:FormWrapper',
    wrap_form='plone.z3cform.layout:wrap_form',
)
