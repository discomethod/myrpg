from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader

from web.models import Item

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the web index.")

def itemlist(request):
    item_list = Item.objects.order_by('name')
    template = loader.get_template('web/index.html')
    context = RequestContext(request, {
        'item_list': item_list,
    })
    return HttpResponse(template.render(context))

def item(request, item_id):
    return HttpResponse("You are looking at item %s." % item_id)

