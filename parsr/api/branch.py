from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from annoying.decorators import ajax_request

from parsr.models import Branch


def get_branch(branch_id):
    return get_object_or_404(Branch, pk=branch_id)


@login_required
@ajax_request
def info(request, branch_id):
    branch = get_branch(branch_id)

    return branch.json()


@ajax_request
def contributors(request, branch_id):
    branch = get_branch(branch_id)

    page = request.GET.get("page")

    return branch.contributors(page=page)
