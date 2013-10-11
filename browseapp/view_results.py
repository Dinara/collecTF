from browse_base import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import collectfapp.views

def prepare_results(motif_csi_list, non_motif_csi_list, integrate_non_motif=False):
    """
    Given lists of motif-associated and non-motif-associated curation site
    instances, pass them to the view results function.
    """
    # get curation_site_instances
    csis = models.Curation_SiteInstance.objects.filter(pk__in=motif_csi_list)
    # get non-motif-associated curation-site-instances
    # if non_motif_csi_list is empty filter doesn't work!
    if integrate_non_motif and non_motif_csi_list:
        non_motif_csis = models.Curation_SiteInstance.objects.filter(pk__in=non_motif_csi_list)
    else:
        non_motif_csis = models.Curation_SiteInstance.objects.none()
    # get data, associated with curation-site-instances
    values = csis.values('curation__TF','site_instance__genome__taxonomy').distinct()

    # create all reports
    reports = []
    for val in values:
        TF = val['curation__TF']
        species = val['site_instance__genome__taxonomy']
        filtered_csis = csis.filter(site_instance__genome__taxonomy=species, curation__TF=TF)
        filtered_non_motif_csis=None
        if integrate_non_motif:
            filtered_non_motif_csis = non_motif_csis.filter(site_instance__genome__taxonomy=species, curation__TF=TF)
                                                            
        if filtered_csis:
            print 'TF:', models.TF.objects.get(pk=TF).name, 'sp:', models.Taxonomy.objects.get(pk=species).name
            report = get_sites_by_TF_and_species(filtered_csis,filtered_non_motif_csis)
            report['TF'] = models.TF.objects.get(pk=TF)
            report['species'] = models.Taxonomy.objects.get(pk=species)
            reports.append(report)
    reports.sort(key=lambda x: x['TF'].name)
    
    # ensemble report
    ensemble_meta_sites = []
    for report in reports:
        ensemble_meta_sites.extend(report['meta_sites'].values())
    # lasagna alignment for ensemble
    trimmed = bioutils.call_lasagna(map(lambda s: s[0].site_instance, ensemble_meta_sites))
    # create weblogo for the list of sites
    ensemble_report = {'meta_sites': ensemble_meta_sites,
                       'aligned_sites': trimmed,
                       'weblogo_image_data': 'x'}

    return {'reports': reports,
            'ensemble_report': ensemble_report,
            'motif_csi_list': ','.join(map(str, motif_csi_list)),
            'non_motif_csi_list': ','.join(map(str, non_motif_csi_list)) if non_motif_csi_list else ""}
    
def view_results(request):
    #assert request.POST, '
    if not request.POST:
        #no GET handler for this function
        return HttpResponseRedirect(reverse(collectfapp.views.home))
        
    csi_list = request.POST['motif_csi_list'].strip().split(',')
    non_motif_csi_list = None
    if request.POST['non_motif_csi_list']:
        non_motif_csi_list = request.POST['non_motif_csi_list'].strip().split(',')
    integrate_non_motif = bool('integrate_non_motif' in request.POST)
    template = prepare_results(csi_list, non_motif_csi_list, integrate_non_motif)
    return render(request,
                  'view_report.html',
                  template,
                  context_instance=RequestContext(request))

def get_sites_by_TF_and_species(curation_site_instances, non_motif_curation_site_instances):
    if not curation_site_instances: return None
    (meta_sites,
     meta_site_curation_dict,
     meta_site_regulation_dict,
     meta_site_technique_dict,
     meta_site_genome_accession_dict) = group_curation_site_instances(curation_site_instances, non_motif_curation_site_instances)
    # Use LASAGNA to align sites
    trimmed = bioutils.call_lasagna(map(lambda s: s[0].site_instance, meta_sites.values()))

    site_instances_qs = models.SiteInstance.objects.filter(pk__in=[meta_sites[k][0].site_instance.pk for k in meta_sites])
    site_instance_genome_dict = dict((v['site_id'], v['genome__genome_accession'])
                                     for v in site_instances_qs.values('site_id', 'genome__genome_accession'))
    
    return {
        'meta_sites': meta_sites,
        'meta_site_genome_accession_dict': dict((k, site_instance_genome_dict[meta_sites[k][0].site_instance.site_id]) for k in meta_sites),
        'meta_site_protein_accession_dict': dict((k, meta_sites[k][0].curation.TF_instance.protein_accession) for k in meta_sites),
        'meta_site_curation_dict': meta_site_curation_dict,
        'meta_site_regulation_dict': meta_site_regulation_dict,
        'meta_site_technique_dict': meta_site_technique_dict,
        'weblogo_image_data': 'x',
        'aligned_sites': trimmed
    }
    
def group_curation_site_instances(curation_site_instances, non_motif_curation_site_instances):
    # Group curation_site_instance objects by meta site-instances
    # integrate non-motif curation-site-instances into exp and regulation fields
    meta_sites = dict()
    meta_site_curation_dict = {}
    meta_site_regulation_dict = {}
    meta_site_technique_dict = {}
    meta_sites_genome_ids = dict()
    
    # group all curation_site_instances into meta-sites    
    for csi in curation_site_instances.iterator():
        # search for a meta-site-instance
        genome_id = models.Curation_SiteInstance.objects.filter(pk=csi.pk).values_list('site_instance__genome__genome_id', flat=True)
        assert len(genome_id) == 1
        genome_id = int(genome_id[0])
        
        for i in meta_sites.keys():
            # if they belong to the same genome and locations overlap
            if (genome_id == meta_sites_genome_ids[i] and
                csi.curation.TF_instance == meta_sites[i][0].curation.TF_instance and
                bioutils.overlap_site_meta_site(csi, meta_sites[i])):
                meta_sites[i].append(csi)
                break
        else:
            # it doesn't overlap with any of the existing metasites
            # create a new metasite
            index=len(meta_sites)+1
            meta_sites[index] = [csi]
            meta_sites_genome_ids[index]=genome_id
            
    # integrate non-motif-associated-curation-site-instances
    if non_motif_curation_site_instances:
        for ncsi in non_motif_curation_site_instances.iterator():
            genome_id = models.Curation_SiteInstance.objects.filter(pk=ncsi.pk).values_list('site_instance__genome__genome_id', flat=True)
            assert len(genome_id) == 1
            genome_id = int(genome_id[0])
            for i in meta_sites.keys():
                # if they belong to the same genome and locations overlap
                if (genome_id == meta_sites_genome_ids[i] and
                    #ncsi.site_instance.genome == meta_sites[i][0].site_instance.genome and
                    ncsi.curation.TF_instance == meta_sites[i][0].curation.TF_instance and
                    bioutils.overlap_non_motif_site_meta_site(ncsi, meta_sites[i])):
                    meta_sites[i].append(ncsi)
            else:
                pass
                    
    # group curations, regulations and techniques for each meta-site
    for ms_id in meta_sites:
        meta_site_curation_dict[ms_id] = [csi.curation for csi in meta_sites[ms_id]]
        meta_site_technique_dict[ms_id] = models.ExperimentalTechnique.objects.filter(preset_function__in=['binding', 'expression'],
                                                                                      curation__in=meta_site_curation_dict[ms_id])

        regs =  models.Regulation.objects.filter(curation_site_instance__in=meta_sites[ms_id]).distinct()
        regs_exp_verified = regs.filter(evidence_type="exp_verified")
        genes_exp_verified = regs_exp_verified.values_list('gene', flat=True)
        regs_inferred = regs.filter(evidence_type="inferred")
        genes_inferred = regs_inferred.values_list('gene', flat=True)

        meta_site_regulation_dict[ms_id] = []
        for i, (g,r) in enumerate(zip(genes_exp_verified, regs_exp_verified)):
            if g in genes_exp_verified[:i]:
                continue
            meta_site_regulation_dict[ms_id].append(r)
        for i, (g,r) in enumerate(zip(genes_inferred, regs_inferred)):
            if g in genes_exp_verified or g in genes_inferred[:i]:
                continue
            meta_site_regulation_dict[ms_id].append(r)
        
        meta_site_curation_dict[ms_id] = list(set(meta_site_curation_dict[ms_id]))
        meta_site_technique_dict[ms_id] = list(set(meta_site_technique_dict[ms_id]))
            
    return (meta_sites,
            meta_site_curation_dict,
            meta_site_regulation_dict,
            meta_site_technique_dict,
            meta_sites_genome_ids)
