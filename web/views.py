from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader

from web.models import Item

# Create your views here.
def index(request):
    # not used...
    return HttpResponse("Hello, world. You're at the web index.")

def itemgen(request):
    item_list = Item.objects.filter(base__isnull=True).order_by('name')
    prefix_list = ItemPrefixGroup.objects.order_by('name')
    suffix_list = ItemSuffixGroup.objects.order_by('name')
    context = {'item_list': item_list,
               'prefix_list': prefix_list,
               'suffix_list': suffix_list,
               }
    return render(request, 'web/itemgen.html', context)

def itemlist(request):
    item_list = Item.objects.order_by('name')
    context = {'item_list': item_list}
    return render(request, 'web/itemlist.html', context)

def item(request, item_id):
    item = Item.objects.get(pk=item_id)
    context = {'item': item}
    return render(request, 'web/item.html', context)

