from django.template import Library
from django.utils.safestring import mark_safe
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Graphics import GenomeDiagram
from reportlab.lib import colors
from reportlab.lib.units import cm

register = Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_keys(dictionary):
    return dictionary.keys()

@register.filter
def regulation_diagram(regulations, site_instance):
    """Given a site instance and regulation objects, output HTML diagram"""
    gdd = GenomeDiagram.Diagram('Regulation Diagram')
    gdt_features = gdd.new_track(1, greytrack=False)
    gds_features = gdt_features.new_set()

    # draw genes
    for reg in regulations:
        feature = SeqFeature(FeatureLocation(reg.gene.start, reg.gene.end), strand=reg.gene.strand)
        gds_features.add_feature(feature, name=reg.gene.name, label=True,
                                 label_size=14, label_angle=0,
                                 sigil="ARROW", arrowshaft_height=1.0,
                                 color=colors.green if reg.evidence_type=="exp_verified" else colors.grey)
        
    # draw binding site
    feature = SeqFeature(FeatureLocation(site_instance.start, site_instance.end), strand=site_instance.strand)
    gds_features.add_feature(feature, color=colors.red, name="site", label=True, label_size=12)

    gdd.draw(format='linear', fragments=1,
             start=min(map(lambda r: r.gene.start, regulations)) - 50,
             end = max(map(lambda r: r.gene.end, regulations)) + 50,
             pagesize = (3*cm, 25*cm))
    
    return mark_safe(gdd.write_to_string('svg'))
    
def site_match_diagram(site_match):
    gdd = GenomeDiagram.Diagram('Site Match diagram')
    gdt_features = gdd.new_track(1, greytrack=False)
    gds_features = gdt_features.new_set()

    # draw genes
    for g in site_match.nearby_genes:
        feature = SeqFeature(FeatureLocation(g.start, g.end), strand=g.strand)
        gds_features.add_feature(feature, name=g.name, label=True,
                                 label_size=14, label_angle=0,
                                 sigil="ARROW", arrowshaft_height=1.0,
                                 color=colors.lightblue)
    # draw binding site
    feature = SeqFeature(FeatureLocation(site_match.match.start, site_match.match.end),
                         strand=site_match.match.strand)
    gds_features.add_feature(feature, color=colors.red, name="site", label=True, label_size=12)
        
    gdd.draw(format='linear', fragments=1,
             start=min(map(lambda g: g.start, site_match.nearby_genes))-50,
             end = max(map(lambda g: g.end, site_match.nearby_genes))+50,
             pagesize = (3*cm, 25*cm))
    return mark_safe(gdd.write_to_string('svg'))


    

