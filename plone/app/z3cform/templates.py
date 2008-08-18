# -*- coding: utf-8 -*-
"""
plone.app.z3cform

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id$
"""

import os.path

import plone.z3cform.interfaces
import plone.z3cform.templates

import zope.app.pagetemplate.viewpagetemplatefile

from Products.CMFDefault.interfaces import ICMFDefaultSkin

import plone.app.z3cform
path = lambda p: os.path.join(os.path.dirname(plone.app.z3cform.__file__), p)

layout_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path('layout.pt'),
    form=plone.z3cform.interfaces.IFormWrapper,
    request=ICMFDefaultSkin)

class Macros(plone.z3cform.templates.Macros):
    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]
