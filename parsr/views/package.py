from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import Package


def get_package(package_id):
    return get_object_or_404(Package, pk=package_id)


@render_to("package.html")
def view(request, package_id):
    pkg = get_package(package_id)

    return { "package": pkg }


@ajax_request
def info(request, package_id):
    f = get_package(package_id)

    return f.json()
