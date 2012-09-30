from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import models


# Create your views here.

# home view
@login_required
def home(request):
    """Home view function to choose an action.
    The user can submit paper for curation, curate a paper or edit one of their
    own previous curations.
    """
    curator,created = models.Curator.objects.get_or_create(user=request.user)
    curations = curator.curation_set.all()
    template_vals = {"user": request.user,
                     "curator": curator,
                     "curations": curations}
    return render_to_response("choose.html", template_vals)


def success(request):
    """Success view handler"""
    return render_to_response("success.html")
