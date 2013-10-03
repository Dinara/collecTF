from browse_base import *
from django import forms
from django.contrib.formtools.wizard.views import CookieWizardView
import search
import view_results


class MotifComparisonForm(forms.Form):
    pass

FORMS = [("motif_a", MotifComparisonForm),
         ("motif_b", MotifComparisonForm),
         ("search_results", MotifComparisonForm),
         ("comparison_results", MotifComparisonForm)]

TEMPLATES = {"motif_a": "motif_compare_search.html",
             "motif_b": "motif_compare_search.html",
             "search_results": "motif_compare_search_results.html",
             "comparison_results": "motif_compare_comparison_results.html"}

FORM_TITLES = {"motif_a": "Search for the first motif.",
               "motif_b": "Search for the second motif.",
               "search_results": "Search results are ready for comparison",
               "comparison_results": "Motif comparison results"}
FORM_DESCRIPTIONS = {
    "motif_a": """Search in CollecTF is fully customizable. Just select a taxonomic
               unit (e.g. the Vibrio genus), a transcription factor family or
               instance (e.g. LexA) and the set of experimental techniques that
               reported sites should be backed by and proceed.""",

    "motif_b": """Search for the second motif to be compared. Just select a taxonomic
               unit (e.g. the Vibrio genus), a transcription factor family or
               instance (e.g. LexA) and the set of experimental techniques that
               reported sites should be backed by and proceed.""",
    
    "search_results": "",

    "comparison_results": "",
    }

class MotifComparisonWizard(CookieWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        # update context to include search form in the first two steps of motif
        # comparison
        c = super(MotifComparisonWizard, self).get_context_data(form=form, **kwargs)
        # Update title and description
        c["form_title"] = FORM_TITLES[self.steps.current]
        c["form_description"] = FORM_DESCRIPTIONS[self.steps.current]

        # If it is motif search step, generate the search form
        if self.steps.current in ["motif_a", "motif_b"]:
            template = search.search_get_template()
            c.update(template)

        if self.steps.current == "search_results":
            c.update({"motif_a": self.request.session["motif_a"],
                      "motif_b": self.request.session["motif_b"]})

        if self.steps.current == "comparison_results":
            motif_a_csi_list = self.request.session["motif_a"]["view_all_csis"]
            motif_a_ncsi_list = self.request.session["motif_a"]["view_all_ncsis"]
            motif_b_csi_list = self.request.session["motif_b"]["view_all_csis"]
            motif_b_ncsi_list = self.request.session["motif_b"]["view_all_ncsis"]
            motif_a_data = view_results.prepare_results(motif_a_csi_list, motif_a_ncsi_list)
            motif_b_data = view_results.prepare_results(motif_b_csi_list, motif_b_ncsi_list)
            # put list of TF and species names in template
            get_TF_name = lambda reports: list(set(map(lambda rep: rep["TF_name"], reports)))
            get_sp_name = lambda reports: list(set(map(lambda rep: rep["species_name"], reports)))
            motif_a_data["TFs"] = get_TF_name(self.request.session["motif_a"]["reports"])
            motif_b_data["TFs"] = get_TF_name(self.request.session["motif_b"]["reports"])
            motif_a_data["species"] = get_sp_name(self.request.session["motif_a"]["reports"])
            motif_b_data["species"] = get_sp_name(self.request.session["motif_b"]["reports"])
            c.update({"motif_a": motif_a_data,
                      "motif_b": motif_b_data})

        return c

    def process_step(self, form):
        """Process data after each step.
        Used to perform searches for both motifs before comparison step
        """
        if self.steps.current in ["motif_a", "motif_b"]: # if one of the motif search steps
            # get motif and non-motif -associated sites
            motif_csis, non_motif_csis = search.search_post_helper(self.request)
            search_results = search.group_search_results(motif_csis, non_motif_csis)
            # store search results
            self.request.session[self.steps.current] = search_results
            self.request.session.modified = True
            
        return self.get_form_step_data(form)

    def done(self, form_list, **kwargs):
        return render_to_response("success.html")


    
