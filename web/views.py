from copy import copy
from itertools import combinations
from random import randrange

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext, loader
from django.utils.html import escape

from web.forms import LoginForm, CharacterCreateForm
from web.models import Item, ItemAffix, ItemAffixGroup, ItemRarePrefix, ItemRareSuffix
from web.models import trim_net_modifiables, display_net_modifiable

# Create your views here.
def index(request):
    # not used...
    return HttpResponse("Hello, world. You're at the web index.")

def affix(request, affix_id):
    affix = get_object_or_404(ItemAffix, pk=affix_id)
    found_on = Item.objects.filter(affixes=affix).annotate(affix_sum=Sum('affixes__ilevel')).order_by('itype__name','-base__ilevel','base__name','-affix_sum','name')
    context = {'header_tab': 'affixes',
               'affix': affix,
               'found_on': found_on,
               }
    return render(request, 'web/affix.html', context)

def affix_group(request, affix_group_id):
    affix_group = get_object_or_404(ItemAffixGroup, pk=affix_group_id)
    affixes = affix_group.itemaffix_set.order_by('-ilevel','name')
    context = {'header_tab': 'affixes',
               'affix_group': affix_group,
               'affixes': affixes,
               }
    return render(request, 'web/affixgroup.html', context)

def affix_list(request):
    prefix_group_list = ItemAffixGroup.objects.filter(prefix=True).order_by('name').annotate(affixes=Count('itemaffix'))
    suffix_group_list = ItemAffixGroup.objects.filter(prefix=False).order_by('name').annotate(affixes=Count('itemaffix'))
    context = {'header_tab': 'affixes',
               'prefix_group_list': prefix_group_list,
               'suffix_group_list': suffix_group_list,
               }
    return render(request, 'web/affixlist.html', context)

def item_gen(request):
    
    def generate_affix_list( current_state, prefix_group_combination, suffix_group_combination, prefixes_possible, suffixes_possible ):
        # current_state is the list of the current sequence, e.g. [P1, P2, P3, S1,]
        # affix_group_combination is a list [AG1, AG2, AG3,]
        # affixes_possible is a list [[P1, P2, P3,], [P4, P5, P6,], [P7, P8, P9],]
        if current_state is None:
            current_state = []
        # calculate how many more affixes still need to be added
        to_add = len(prefix_group_combination)+len(suffix_group_combination)-len(current_state)
        current_state_new = []
        return_masterlist = []
        return_sublist = []
        
        # check if we're on the last level of recursion
        # this occurs when only one last affix needs to be added
        if to_add == 1:
            # exit case
            # determine if we should add prefix or suffix
            if len(current_state) >= len(prefix_group_combination):
                # all prefixes have been added
                # we need to add a suffix
                for suffix_possible in suffixes_possible[len(current_state)-len(prefix_group_combination)]:
                    return_sublist = current_state[:]
                    return_sublist.append(suffix_possible.pk)
                    return_masterlist.append(return_sublist)
            else:
                # not all prefixes have been added
                # we need to add a prefix
                for prefix_possible in prefixes_possible[len(current_state)]:
                    return_sublist = current_state[:]
                    return_sublist.append(prefix_possible.pk)
                    return_masterlist.append(return_sublist)
            return return_masterlist
        else:
            # there is more than one affix that still needs to be added
            if len(current_state) < len(prefix_group_combination):
                # we still need to add prefixes
                for prefix_possible in prefixes_possible[len(current_state)]:
                    current_state_new = current_state[:]
                    current_state_new.append(prefix_possible.pk)
                    return_masterlist += generate_affix_list( current_state_new, prefix_group_combination, suffix_group_combination, prefixes_possible, suffixes_possible)
            else:
                # we still need to add suffixes
                for suffix_possible in suffixes_possible[len(current_state)-len(prefix_group_combination)]:
                    current_state_new = current_state[:]
                    current_state_new.append(suffix_possible.pk)
                    return_masterlist += generate_affix_list( current_state_new, prefix_group_combination, suffix_group_combination, prefixes_possible, suffixes_possible)
            return return_masterlist
    
    try:
        base_item = Item.objects.get(pk=request.POST['base_item'])
    except (KeyError, Item.DoesNotExist) as e:
        # KeyError => base item was not provided
        # Item.DoesNotExist => base item id was not found
        item_list = Item.objects.filter(base__isnull=True).order_by('name')
        prefix_list = ItemAffixGroup.objects.filter(prefix=True).order_by('name')
        suffix_list = ItemAffixGroup.objects.filter(prefix=False).order_by('name')
        context = {'header_tab': 'items',
                   'item_list': item_list,
                   'prefix_list': prefix_list,
                   'suffix_list': suffix_list,
                   }
        return render(request, 'web/itemgen.html', context)
    else:
        # define some characteristics of generating prefix/suffixes
        CORE_PREFIX_MAX = 2 # absolute maximum number of prefixes
        CORE_SUFFIX_MAX = 2 # absolute maximum number of suffixes
        CORE_FIXES_FROM_AFFIXGROUP = 3 # how many of the top affixes to pick from each fixgroup
        CORE_AFFIX_DISCREPANCY = 1 # maximum difference between number of fixes
        # we now have a base item to work with
        # get all the possible prefixes
        prefix_group_post_list = request.POST.getlist('prefixgroup')
        suffix_group_post_list = request.POST.getlist('suffixgroup')
        prefix_group_list = list()
        suffix_group_list = list()
        # convert POST data to objects
        for prefix_group_post in prefix_group_post_list:
            prefix_group_list.append(ItemAffixGroup.objects.get(pk=prefix_group_post))
        for suffix_group_post in suffix_group_post_list:
            suffix_group_list.append(ItemAffixGroup.objects.get(pk=suffix_group_post))
        # sort affix_group lists by the id of the affix_group
        prefix_group_list.sort(key = lambda x: x.pk)
        suffix_group_list.sort(key = lambda x: x.pk)
        # get all the data for the affixgroups
        prefixes_possible_bygroup = dict()
        suffixes_possible_bygroup = dict()
        for prefix_group in prefix_group_list:
            prefixes_possible_bygroup[prefix_group.pk] = ItemAffix.objects.filter(group=prefix_group).filter(ilevel__lte=base_item.ilevel).order_by('-ilevel')[:CORE_FIXES_FROM_AFFIXGROUP]
        for suffix_group in suffix_group_list:
            suffixes_possible_bygroup[suffix_group.pk] = ItemAffix.objects.filter(group=suffix_group).filter(ilevel__lte=base_item.ilevel).order_by('-ilevel')[:CORE_FIXES_FROM_AFFIXGROUP]
        # max CORE_PREFIX_MAX prefixes, less if there aren't enough to choose from, and no more than CORE_AFFIX_DISCREPANCY more than the number of suffixes
        prefix_max = min(CORE_PREFIX_MAX,len(prefix_group_list),len(suffix_group_list)+CORE_AFFIX_DISCREPANCY)
        # max CORE_SUFFIX_MAX suffixes, less if there aren't enough to choose from, and no more than CORE_AFFIX_DISCREPANCY more than the number of prefixes
        suffix_max = min(CORE_SUFFIX_MAX,len(suffix_group_list),len(prefix_group_list)+CORE_AFFIX_DISCREPANCY)
        for prefix_num in range(prefix_max+1): # number of prefixes from 0 to prefix_max INCLUSIVE
            for suffix_num in range(suffix_max+1):# number of suffixes from 0 to prefix_max INCLUSIVE
                # degenerate case if prefix and suffix are both 0
                if prefix_num + suffix_num == 0:
                    continue
                if prefix_num+CORE_AFFIX_DISCREPANCY < suffix_num or suffix_num+CORE_AFFIX_DISCREPANCY < prefix_num:
                    continue
                # generate all possible items with prefix_num prefixes and suffix_num suffixes
                for prefix_group_combination in combinations(prefix_group_list,prefix_num):
                    for suffix_group_combination in combinations(suffix_group_list,suffix_num):
                        # affix_group_combination is a list of the primary keys of the affix_groups we are going to add
                        # e.g., [AG1,AG3,AG7,] or [AG1, AG3,] (i.e., no padding)
                        # if the affix_group list is empty, or affix_group_num is 0, we get an empty list []
                        prefixes_possible = [[None,] for ii in range(CORE_PREFIX_MAX)]
                        suffixes_possible = [[None,] for ii in range(CORE_SUFFIX_MAX)]
                        for pindex, prefix_group in enumerate(prefix_group_combination):
                            prefixes_possible[pindex] = prefixes_possible_bygroup[prefix_group.pk]
                        for sindex, suffix_group in enumerate(suffix_group_combination):
                            suffixes_possible[sindex] = suffixes_possible_bygroup[suffix_group.pk]
                        current_state = []
                        affixes_list = generate_affix_list( current_state, prefix_group_combination, suffix_group_combination, prefixes_possible, suffixes_possible )
                        if len(affixes_list) == 0:
                            # this will sometimes occur if the only affix group has no affixes with low enough ilevel
                            continue   
                        for affix_list in affixes_list:
                            # affix_list is a list containing [P1, P3, P8, S1, S3,], etc.
                            # split it into a prefix_list and an suffix_list
                            prefix_list_pks = affix_list[:len(prefix_group_combination)]
                            suffix_list_pks = affix_list[len(prefix_group_combination):]
                            prefix_list = []
                            suffix_list = []
                            # convert from PKs back into affix objects
                            for prefix_pk in prefix_list_pks:
                                prefix_list.append(ItemAffix.objects.get(pk=prefix_pk))
                            for suffix_pk in suffix_list_pks:
                                suffix_list.append(ItemAffix.objects.get(pk=suffix_pk))
                            # check if the item we are about to create already exists
                            affix_total = len(prefix_group_combination)+len(suffix_group_combination)
                            temp = Item.objects.filter(base=base_item).annotate(num_affixes=Count('affixes')).filter(num_affixes=affix_total)
                            for affix in affix_list:
                                temp = temp.filter(affixes=affix)
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
                            new_item.description=""
                            new_item.save()
                            # copy slots from base item
                            for slot in base_item.slots.all():
                                new_item.slots.add(slot)
                            # copy base modifications form base item
                            for mod in base_item.modifications.all():
                                new_item.modifications.add(mod)
                            # add the new item's affixes
                            for affix in affix_list:
                                new_item.affixes.add(affix)
                            # generate the new item's rarity
                            # the only criteria for a rare item is having more than one suffix
                            if len(suffix_list) > 1:
                                new_item.rarity = "RARE"
                            else:
                                new_item.rarity = "UNCOM"
                            
                            # generate this item's name
                            if new_item.rarity == "UNCOM":
                                new_item.name = base_item.name
                                # just prepend prefix and append suffix
                                for prefix in prefix_list:
                                    new_item.name = str(prefix).lower() + " " +  new_item.name
                                if len(suffix_list) > 0:
                                    new_item.name = new_item.name + " " + str(suffix_list[0]).lower()
                            else:
                                # rare name
                                temp_name = base_item.name
                                rare_prefixes = ItemRarePrefix.objects.all()
                                rare_suffixes = new_item.itype.raresuffixes.all()
                                while len(Item.objects.filter(name=temp_name)) > 0:
                                    rare_prefix = str(rare_prefixes[randrange(len(rare_prefixes))])
                                    rare_suffix = str(rare_suffixes[randrange(len(rare_suffixes))])
                                    temp_name = rare_prefix + " " + rare_suffix + ", " + base_item.name.title()
                                new_item.name = temp_name
                            # save this new item
                            new_item.save()

        item_list = Item.objects.filter(base__isnull=True).order_by('name')
        prefix_list = ItemAffixGroup.objects.filter(prefix=True).order_by('name')
        suffix_list = ItemAffixGroup.objects.filter(prefix=False).order_by('name')
        context = {'header_tab': 'items',
                   'item_list': item_list,
                   'prefix_list': prefix_list,
                   'suffix_list': suffix_list,
                   }
        return render(request, 'web/itemgen.html', context)

def item_list(request):
    raw_item_list = Item.objects.annotate(affix_sum=Sum('affixes__ilevel')).order_by('itype__name','-base__ilevel','base__name','-affix_sum','name')
    item_list = list()
    current_sublist = list()
    last_item_type = None
    for raw_item in raw_item_list:
        if raw_item.itype != last_item_type:
            # new item type
            if len(current_sublist)>0:
                item_list.append(current_sublist)
            current_sublist = list()
            last_item_type = raw_item.itype
        current_sublist.append(raw_item)
    if len(current_sublist)>0:
        item_list.append(current_sublist)
    context = {'header_tab': 'items',
                'item_list': item_list}
    return render(request, 'web/itemlist.html', context)

def item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item_net_modifiables = trim_net_modifiables(item.call_get_net_modifiables())
    item_net_modifiables.sort(key=lambda net_modifiable: net_modifiable['max'], reverse=True) # sorts net modifiables by their maximum value descending
    display_modifiables_list = list() # list of strings to display
    for item_net_modifiable in item_net_modifiables:
        display_modifiables_list += display_net_modifiable(item_net_modifiable)
    if not item.description and item.base and item.base.description:
        # if this item is a generated item with no description, use the description of the base item
        item.description = item.base.description + " There's something different about this " + str(item.base) + " though."
    context = {'header_tab': 'items',
                'item': item,
                'display_modifiables_list': display_modifiables_list,
                }
    return render(request, 'web/item.html', context)

def character_create(request):
    # check if the form has been submitted
    if request.method == 'POST':
        # do stuff related to the form
        pass
    else:
        # no form was submitted
        form = CharacterCreateForm()
        context = {'header_tab': 'character',
                    'form': form,
                    }
        return render(request,'web/characters/create.html', context)

def login_view(request):
    # check if the form has been submitted
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to a success page.
                    return redirect('item_list')
                else:
                    # Return a 'disabled account' error message
                    context = {'header_tab': 'account',
                                'form': form,
                                }
                    return render(request, 'web/accounts/login.html', context)
            else:
                # Return an 'invalid login' error message
                context = {'header_tab': 'account',
                            'form': form,
                            }
                return render(request, 'web/accounts/login.html', context)
        else:
            # Return an 'invalid form' error message
            context = {'header_tab': 'account',
                        'form': form,
                        }
            return render(request, 'web/accounts/login.html', context)
    else:
        # Return the login form
        character_class = CharacterClass.objects.all()
        form = LoginForm()
        context = {'header_tab': 'account',
                    'form': form,
                    }
        return render(request,'web/accounts/login.html', context)

def logout_view(request):
    if request.user.is_authenticated():
        # user is logged in, so now we log out
        form = LoginForm()
        success_messages = list()
        success_message = request.user.username + ", you have successfully logged out."
        success_messages.append(success_message)
        context = {'header_tab': 'account',
                    'form': form,
                    'success_messages': success_messages,
                    }
        logout(request)
        return render(request,'web/accounts/login.html', context)
    else:
        # user is not logged in, so we redirect to login
        return redirect('login')
