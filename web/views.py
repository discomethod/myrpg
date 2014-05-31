from copy import copy
from itertools import combinations
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
        # define some characteristics of generating prefix/suffixes
        CORE_PREFIX_MAX = 3 # absolute maximum number of prefixes
        CORE_SUFFIX_MAX = 3 # absolute maximum number of suffixes
        CORE_FIXES_FROM_AFFIXGROUP = 3 # how many of the top affixes to pick from each fixgroup
        CORE_FIX_DISCREPANCY = 1 # maxmimum difference between number of fixes
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
        # sort affixgroup lists by the id of the affixgroup
        prefixgroup_list.sort(key = lambda x: x.pk)
        suffixgroup_list.sort(key = lambda x: x.pk)
        # get all the data for the affixgroups
        prefixes_possible_bygroup = dict()
        suffixes_possible_bygroup = dict()
        for prefixgroup in prefixgroup_list:
            prefixes_possible_bygroup[prefixgroup.pk] = ItemPrefix.objects.filter(group=prefixgroup)[:CORE_FIXES_FROM_AFFIXGROUP]
        for suffixgroup in suffixgroup_list:
            suffixes_possible_bygroup[suffixgroup.pk] = ItemSuffix.objects.filter(group=suffixgroup)[:CORE_FIXES_FROM_AFFIXGROUP]
        # max CORE_PREFIX_MAX prefixes, less if there aren't enough to choose from, and no more than CORE_FIX_DISCREPANCY more than the number of suffixes
        prefix_max = min(CORE_PREFIX_MAX,len(prefixgroup_list),len(suffixgroup_list)+CORE_FIX_DISCREPANCY)
        # max CORE_SUFFIX_MAX suffixes, less if there aren't enough to choose from, and no more than CORE_FIX_DISCREPANCY more than the number of prefixes
        suffix_max = min(CORE_SUFFIX_MAX,len(suffixgroup_list),len(prefixgroup_list)+CORE_FIX_DISCREPANCY)
        for prefix_num in range(prefix_max+1): # number of prefixes from 0 to prefix_max INCLUSIVE
            for suffix_num in range(suffix_max+1):# number of suffixes from 0 to prefix_max INCLUSIVE
                # degenerate case if prefix and suffix are both 0
                if prefix_num + suffix_num == 0:
                    continue
                # generate all possible items with prefix_num prefixes and suffix_num suffixes
                for prefixgroup_combination in combination(prefixgroup_list,prefix_num):
                    for sufixgroup_combination in combination(suffixgroup_list,suffix_num):
                        # affixgroup_combination is a list of the primary keys of the affixgroups we are going to add
                        # e.g., [P1,P3,P7,]
                        # if the affixgroup list is empty, or affixgroup_num is 0, we get an empty list []
                        prefixes_possible = [[None,] for ii in range(CORE_PREFIX_MAX)]
                        suffixes_possible = [[None,] for ii in range(CORE_PREFIX_MAX)]
                        for pindex, prefixgroup in enumerate(prefixgroup_combination):
                            prefixes_possible[pindex] = prefixes_possible_bygroup[prefixgroup.pk]
                        for sindex, suffixgroup in enumerate(suffixgroup_combination):
                            suffixes_possible[sindex] = suffixes_possible_bygroup[suffixgroup.pk]
                        
                        # WORK IN PROGRESS HERE #
                        """ 
                       # shallow copy the base_item
                                new_item = copy(base_item)
                                # remove the primary key, so it will be CREATE rather than UPDATE
                                new_item.pk = None
                                # add base item relationship
                                new_item.base = base_item
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
                                new_item = copy(base_item)
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
                                        RARE_PREFIXES = ["Agony", "Apocalypse", "Armageddon",
                                                            "Beast", "Behemoth", "Blight",
                                                            "Blood", "Bramble", "Brimstone",
                                                            "Brood", "Carrion", "Cataclysm",
                                                            "Chimeric", "Corpse", "Corruption",
                                                            "Damnation", "Death", "Demon",
                                                            "Dire", "Dragon", "Dread",
                                                            "Doom", "Dusk", "Eagle", "Empire",
                                                            "Empyrean", "Fate", "Foe",
                                                            "Gale", "Ghoul", "Gloom",
                                                            "Glyph", "Golem", "Grim",
                                                            "Hate", "Havoc", "Honor",
                                                            "Horror", "Hypnotic", "Kraken",
                                                            "Loath", "Maelstrom", "Mind",
                                                            "Miracle", "Morbid", "Oblivion",
                                                            "Onslaught", "Pain", "Pandemonium",
                                                            "Phoenix", "Plague", "Rage",
                                                            "Rapture", "Rune", "Skull",
                                                            "Sol", "Soul", "Sorrow",
                                                            "Spirit", "Storm", "Tempest",
                                                            "Torment", "Vengeance", "Victory",
                                                            "Viper", "Vortex", "Woe", "Wrath",]
                                        RARE_SUFFIXES = new_item.itype.rarenames.all()
                                        rare_prefix = str(RARE_PREFIXES[randrange(len(RARE_PREFIXES))])
                                        rare_suffix = str(RARE_SUFFIXES[randrange(len(RARE_SUFFIXES))])
                                        temp_name = rare_prefix + " " + rare_suffix
                                    new_item.name = temp_name
                                # save this new item
                                new_item.save()
                        """

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
