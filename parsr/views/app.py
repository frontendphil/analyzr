from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import redirect

from annoying.decorators import render_to


# @login_required
@render_to("index.html")
def index(request):
    return {}


@render_to("login.html")
def login(request):
    if request.method == "GET":
        return {}

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = auth.authenticate(username=username, password=password)

    if user is None:
        return { "error": "Username or password incorrect." }

    if not user.is_active:
        return { "error": "This user is not active in the system." }

    auth.login(request, user)

    return redirect(request.GET.get("next") or "parsr.views.app.index")


def logout(request):
    auth.logout(request)

    return redirect("parsr.views.app.login")
