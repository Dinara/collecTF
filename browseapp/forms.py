from django import forms
import models
from django.utils.safestring import mark_safe

class BrowseForm(forms.Form):
    TF = forms.ModelChoiceField(queryset=models.TF.objects.all(),
                                label="TF",
                                initial=0)
    species = forms.ModelChoiceField(queryset=models.Strain.objects.all(),
                                     label="species",
                                     initial=0)

    
    # generate techniques field
    # get available techniques from db
    choices = []
    # used twitter-bootstrap tooltip for exp technique description
    description_markup = u'<span data-toggle="tooltip" title="%s">%s</span>'
    for t in models.ExperimentalTechnique.objects.order_by('name'):
        choices.append((t.technique_id,
                        mark_safe(description_markup % (t.description, t.name))))
    techniques = forms.MultipleChoiceField(choices = choices,
                                           label = "Techniques",
                                           widget = forms.CheckboxSelectMultiple())

    
