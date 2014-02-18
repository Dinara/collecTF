from django.contrib import admin
from django.db.models import get_models
from django.db.models import get_app
from base.models import *

# Register your models here.

class GenomeAdmin(admin.ModelAdmin):
    list_display = ('genome_accession', 'organism')

# Curation admin view
class CurationSiteInstanceInline(admin.StackedInline):
    model = Curation_SiteInstance
    extra = 0
    
class CurationAdmin(admin.ModelAdmin):
    def PMID(self, obj):
        return obj.publication.pmid
    filter_horizontal = ('TF_instances',)
    list_display = ('curation_id', 'TF_species', 'PMID', 'curator')
    list_filter = ('curator', 'NCBI_submission_ready', 'requires_revision')
    ordering = ('-curation_id',)
    inlines = (CurationSiteInstanceInline,)

class CuratorAdmin(admin.ModelAdmin):
    def username(self, obj):
        return obj.user.username
    def email(self, obj):
        return obj.user.email
    def name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name
    list_display = ('username', 'email', 'name')

class SiteInstanceAdmin(admin.ModelAdmin):
    list_display = ('site_id',)
    #list_filter = ('genome__genome_accession',)
    ordering = ('-site_id', )

class Curation_SiteInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', )
    list_filter = ('site_type',)
    filter_horizontal = ("experimental_techniques",)
    ordering = ('-id',)

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('publication_id', 'pmid', 'title', 'assigned_to')
    list_filter = ('assigned_to', 'curation_complete', 'reported_TF', 'reported_species')
    search_fields = ('pmid',)
    #actions = [assign_papers]

class ExperimentalTechniqueAdmin(admin.ModelAdmin):
    list_display = ('name', )
    filter_horizontal = ('categories',)

class GeneAdmin(admin.ModelAdmin):
    list_display = ('gene_accession', 'name')
    list_filter = ('genome__genome_accession',)

class GenomeAdmin(admin.ModelAdmin):
    list_display = ('genome_accession', 'organism')

class TFFamilyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    
class TFAdmin(admin.ModelAdmin):
    list_display = ('name', 'family')
    list_filter = ('family',)
    ordering = ('name',)

class TFInstance(admin.ModelAdmin):
    list_display = ('protein_accession', 'name')
    list_filter = ('')
    ordering = ('name')

class NCBISubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'genome_submitted_to', 'submission_time', 'curation_site_instance')
    

def register_rest():
    """Register all models that have not been registered explicitly."""
    app = get_app("base")
    for model in get_models(app):
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass

def unregister_regulation():
    """Unregister Regulation table. Don't show any field. Gene field in the
    Regulation model ruins everything. As default behavior, Django tries to
    generate a dropdown box with __ALL__ genes in the database, which kills the
    server."""
    admin.site.unregister(Regulation)

# Register models
admin.site.register(Curator, CuratorAdmin)
admin.site.register(Curation, CurationAdmin)
admin.site.register(SiteInstance, SiteInstanceAdmin)
admin.site.register(Curation_SiteInstance, Curation_SiteInstanceAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(ExperimentalTechnique, ExperimentalTechniqueAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Genome, GenomeAdmin)
admin.site.register(TFFamily, TFFamilyAdmin)
admin.site.register(TF, TFAdmin)
admin.site.register(NCBISubmission, NCBISubmissionAdmin)
register_rest()
unregister_regulation()

