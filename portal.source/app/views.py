from django.contrib.auth import logout
from django.template import loader
from django.http import HttpResponse
from users.views import get_roles


def index(request):
    context = {}
    logout(request)
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render(context, request))


def success(request):
    context = {'roles': get_roles(request)}
    template = loader.get_template('app/main.html')
    return HttpResponse(template.render(context, request))


def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))

