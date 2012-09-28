from collectfapp.models import *
from django.contrib import admin
from django.db.models import get_models
from django.db.models import get_app

# curation admin view
class CurationAdmin(admin.ModelAdmin):
    filter_horizontal = ("experimental_techniques",)
admin.site.register(Curation, CurationAdmin) # register Curation

# register rest of models
app = get_app("collectfapp")
for model in get_models(app):
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
