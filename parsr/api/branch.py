from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.gzip import gzip_page

from annoying.decorators import ajax_request

from parsr.models import Branch

from parsr.views.author import parse_filters


def get_branch(branch_id):
    return get_object_or_404(Branch, pk=branch_id)


@ajax_request
def list(request, repository_id):
    return [branch.json() for branch in Branch.objects.filter(repo=repository_id)]


# @login_required
@ajax_request
def info(request, repository_id, branch_id):
    branch = get_branch(branch_id)

    return branch.json()


# @login_required
@ajax_request
def contributors(request, repository_id, branch_id):
    branch = get_branch(branch_id)

    page = request.GET.get("page")

    return branch.contributors(page=page)


# @login_required
@ajax_request
def punchcard(request, repository_id, branch_id):
    branch = get_branch(branch_id)

    return branch.punchcard()

# @login_required
@gzip_page
@ajax_request
def churn(request, repository_id, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.churn(language=language, package=package, start=start, end=end)
