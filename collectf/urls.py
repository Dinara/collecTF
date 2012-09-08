from django.conf.urls import patterns, include, url
from collectfapp.signupview import *
from django.contrib.auth.decorators import login_required

import collectfapp.views as views
import collectfapp.signupview as signupview
import collectfapp.pubview as pubview

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'collectf.views.home', name='home'),
    # url(r'^collectf/', include('collectf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # registration
    url(r'^accounts/register/$', signupview.register),
    # login
    url(r'^accounts/login/$', signupview.login, {'extra_context': {'next': '/'}}),
    # logout
    url(r'^accounts/logout/$', signupview.logout),
    # main page
    url(r'^$', login_required(views.home)),
    # pubmed publication submission
    url(r'^pubmed_submission/$', login_required(pubview.pubmed_submission)),

)

print login
