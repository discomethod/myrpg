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
    
    def generate_affix_list( current_state, prefixgroup_combination, suffixgroup_combination, prefixes_possible, suffixes_possible ):
        # current_state is the list of the current sequence, e.g. [P1, P2, P3, S1,]
        # affixgroup_combination is a list [AG1, AG2, AG3,]
        # affixes_possible is a list [[P1, P2, P3,], [P4, P5, P6,], [P7, P8, P9],]
        
        # calculate how many more affixes still need to be added
        toadd = len(prefixgroup_combination)+len(suffixgroup_combination)-len(current_state)
        current_state_new = []
        return_masterlist = []
        return_sublist = []
        
        # check if we're on the last level of recursion
        # this occurs when only one last affix needs to be added
        if toadd == 1:
            # exit case
            # determine if we should add prefix or suffix
            if len(current_state) >= len(prefixgroup_combination):
                # all prefixes have been added, we need to add a suffix
                for suffix_possible in suffixes_possible[-1]:
                    return_sublist = current_state + suffix_possible
                    return_masterlist.append(return_sublist)
            else:
                # last thing to add is a prefix
                for prefix_possible in prefixes_possible[-1]:
                    return_sublist = current_state + suffix_possible
                    return_masterlist.append(return_sublist)
            return return_masterlist
        else:
            # there is more than one affix that still needs to be added
            if len(current_state) < len(prefixgroup_combination):
                # we still need to add prefixes
                for prefix_possible in prefixes_possible[len(current_state)]:
                    current_state_new = current_state + prefix_possible
                    return_masterlist += generate_affix_list( current_state_new, prefixgroup_combination, suffixgroup_combination, prefixes_possible, suffixes_possible)
                return return_masterlist
            else:
                # we still need to add suffixes
                for suffix_possible in suffixes_possible[len(current_state)-len(prefixgroup_combination)]:
                    current_state_new = current_state + suffix_possible
                    return_masterlist += generate_affix_list( current_state_new, prefixgroup_combination, suffixgroup_combination, prefixes_possible, suffixes_possible)
                return return_masterlist
    
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
                if prefix_num+1 < suffix_num or suffix_num+1 < prefix_num:
                    continue
                # generate all possible items with prefix_num prefixes and suffix_num suffixes
                for prefixgroup_combination in combination(prefixgroup_list,prefix_num):
                    for sufixgroup_combination in combination(suffixgroup_list,suffix_num):
                        # affixgroup_combination is a list of the primary keys of the affixgroups we are going to add
                        # e.g., [AG1,AG3,AG7,] or [AG1, AG3,] (i.e., no padding)
                        # if the affixgroup list is empty, or affixgroup_num is 0, we get an empty list []
                        prefixes_possible = [[None,] for ii in range(CORE_PREFIX_MAX)]
                        suffixes_possible = [[None,] for ii in range(CORE_SUFFIX_MAX)]
                        for pindex, prefixgroup in enumerate(prefixgroup_combination):
                            prefixes_possible[pindex] = prefixes_possible_bygroup[prefixgroup.pk]
                        for sindex, suffixgroup in enumerate(suffixgroup_combination):
                            suffixes_possible[sindex] = suffixes_possible_bygroup[suffixgroup.pk]
                        current_state = []
                        affixes_list = generate_affix_list( current_state, prefixgroup_combination, suffixgroup_combination, prefixes_possible, suffixes_possible )
                        for affix_list in affixes_list:
                            # affix_list is a list containing [P1, P3, P8, S1, S3,], etc.
                            # split it into a prefix_list and an suffix_list
                            prefix_list = affix_list[:len(prefixgroup_combination)]
                            suffix_list = affix_list[len(prefixgroup_combination):]
                            # check if the item we are about to create already exists
                            temp = Item.objects.filter(base=base_item).annotate(num_prefixes=Count('prefixes'),num_suffixes=Count('suffixes')).filter(num_prefixes=len(prefixgroup_combination)).filter(num_suffixes=len(suffixgroup_combination))
                            for prefix in prefix_list:
                                temp = temp.filter(prefixes=prefix)
                            for suffix in suffix_list:
                                temp = temp.filter(suffixes=suffix)
                            if len(temp) > 0:
                                # this item already exists
                                continue
                            # this item doesn't already exist
                            new_item = copy(base_item)
                            # remove the primary key, so it will be CREATE rather than UPDATE
                            new_item.pk = None
                            # add base item relationship
                            new_item.base = base_item
                            new_item.name="NEWITEM"
                            new_item.save()
                            # copy slots from base item
                            for slot in base_item.slots:
                                new_item.slots.add(slot)
                            # copy base modifications form base item
                            for mod in base_item.modification:
                                new_item.modification.add(mod)
                            # add the new item's affixes
                            for prefix in prefix_list:
                                new_item = new_item.prefixes.add(prefix)
                            for suffix in suffix_list:
                                new_item = new_item.suffixes.add(suffix)
                            # generate the new item's rarity
                            if len(affix_list) > 2:
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
                                    """
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
                                    """
                                    RARE_PREFIXES = ItemRarePrefix.objects.all()
                                    RARE_SUFFIXES = new_item.itype.raresuffixes.all()
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
