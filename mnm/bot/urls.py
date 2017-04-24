# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^help$',
        view=views.HelpView.as_view(),
        name='help'
    ),
]
