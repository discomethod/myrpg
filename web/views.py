from copy import copy, deepcopy
from random import randrange

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader

from web.models import Item, ItemPrefix, ItemSuffix, ItemPrefixGroup, ItemSuffixGroup

# Create your views here.
def index(request):
    # not used...
    return HttpResponse("Hello, world. You're at the web index.")

def itemgen(request):
    try:
        base_item = Item.objects.get(pk=request.POST['baseItem'])
    except (KeyError):
        # base item was not provided
        item_list = Item.objects.filter(base__isnull=True).order_by('name')
        prefix_list = ItemPrefixGroup.objects.order_by('name')
        suffix_list = ItemSuffixGroup.objects.order_by('name')
        context = {'item_list': item_list,
                   'prefix_list': prefix_list,
                   'suffix_list': suffix_list,
                   }
        return render(request, 'web/itemgen.html', context)
    except Item.DoesNotExist:
        # base item id was not found
        item_list = Item.objects.filter(base__isnull=True).order_by('name')
        prefix_list = ItemPrefixGroup.objects.order_by('name')
        suffix_list = ItemSuffixGroup.objects.order_by('name')
        context = {'item_list': item_list,
                   'prefix_list': prefix_list,
                   'suffix_list': suffix_list,
                   }
        return render(request, 'web/itemgen.html', context)
    else:
        # we now have a base item to work with
        # get all the possible prefixes
        prefixgroup_post_list = request.POST.getlist('prefixgroup')
        suffixgroup_post_list = request.POST.getlist('suffixgroup')
        prefixgroup_list = list()
        suffixgroup_list = list()
        # convert POST data to objects
        for prefixgroup_post in prefixgroup_post_list:
            prefixgroup_list.append(ItemPrefix.objects.get(pk=prefixgroup_post))
        for suffixgroup_post in suffixgroup_post_list:
            suffixgroup_list.append(ItemSuffix.objects.get(pk=suffixgroup_post))
        # iterate through all possible prefix/suffix combinations
        for prefixgroup1 in prefixgroup_list:
            for prefixgroup2 in prefixgroup_list:
                for prefixgroup3 in prefixgroup_list:
                    for suffixgroup1 in suffixgroup_list:
                        for suffixgroup2 in suffixgroup_list:
                            for suffixgroup3 in suffixgroup_list:
                                prefixgroup_set = set()
                                prefixgroup_set.add(prefixgroup1)
                                prefixgroup_set.add(prefixgroup2)
                                prefixgroup_set.add(prefixgroup3)
                                suffixgroup_set = set()
                                suffixgroup_set.add(suffixgroup1)
                                suffixgroup_set.add(suffixgroup2)
                                suffixgroup_set.add(suffixgroup3)
                                # don't allow mismatches amounts of prefixes and suffixes
                                if len(prefixgroup_set)+1 < len(suffixgroup_set) or len(suffixgroup_set)+1 < len(prefixgroup_set):
                                    continue

                                # now we are ready to make a new item
                                # base item in base_item
                                # add all prefixes in prefixgroup_set
                                # add all suffixes in suffixgroup_set
                                
                                # shallow copy the base item
                                new_item = deepcopy(base_item)
                                # erase the primary key
                                new_item.pk = None
                                # add base relation
                                new_item.base = base_item
                                # find the best prefix/suffix in each group to add
                                prefix_list = []
                                suffix_list = []
                                for prefixgroup in prefixgroup_set:
                                    # only add best prefix
                                    try:
                                        prefix_list.append(ItemPrefix.objects.filter(group=prefixgroup).filter(ilevel__lte=new_item.ilevel).order_by('-ilevel')[0])
                                    except IndexError:
                                        # no prefix in this prefix group is suitable for this item
                                        continue
                                for suffixgroup in suffixgroup_set:
                                    # only add best suffix
                                    try:
                                        suffix_list.append(ItemSuffix.objects.filter(group=suffixgroup).filter(ilevel__lte=new_item.ilevel).order_by('-ilevel')[0])
                                    except IndexError:
                                        # no suffix in this suffix group is suitable for this item
                                        continue
                                
                                # check if we found enough to add
                                if len(prefix_list) + len(suffix_list) < 1:
                                    continue
                                # check if the item we are about to create already exists
                                temp = Item.objects.filter(base=base_item).annotate(num_prefixes=Count('prefixes'),num_suffixes=Count('suffixes')).filter(num_prefixes=len(prefix_list)).filter(num_suffixes=len(suffix_list))
                                for prefix in prefix_list:
                                    temp = temp.filter(prefixes=prefix)
                                for suffix in suffix_list:
                                    temp = temp.filter(suffixes=suffix)
                                if len(temp) > 0:
                                    # this item already exists
                                    # implement override by setting new_item pk to the found item's pk
                                    continue
                                # this item doesn't already exist
                                # save this item to get its pk
                                new_item.name="NEWITEM"
                                new_item.save()
                                for prefix in prefix_list:
                                    new_item.prefixes.add(prefix)
                                for suffix in suffix_list:
                                    new_item.suffixes.add(suffix)
                                # generate this item's rarity
                                if len(prefix_list) + len(suffix_list) > 2:
                                    new_item.rarity = "RAR"
                                else:
                                    new_item.rarity = "UNC"
                                # generate this item's name
                                if new_item.rarity == "UNC":
                                    new_item.name = base_item.name
                                    # just prepend prefix and append suffix
                                    if len(prefix_list) > 0:
                                        new_item.name = str(prefix_list[0]).lower() + " " +  new_item.name
                                    if len(suffix_list) > 0:
                                        new_item.name = new_item.name + " " + str(suffix_list[0]).lower()
                                else:
                                    # rare name
                                    temp_name = base_item.name
                                    while len(Item.objects.filter(name=temp_name)) > 0:
                                        RARE_PREFIXES = ["Glory", "Kraken", "Final",]
                                        RARE_SUFFIXES = new_item.itype.rarenames.all()
                                        rare_prefix = str(RARE_PREFIXES[randrange(len(RARE_PREFIXES))])
                                        rare_suffix = str(RARE_SUFFIXES[randrange(len(RARE_SUFFIXES))])
                                        temp_name = rare_prefix + " " + rare_suffix
                                    new_item.name = temp_name
                                # save this new item
                                new_item.save()

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

