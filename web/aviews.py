from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from web.models import ItemType, ItemRareSuffix

@login_required
@permission_required('web.edit_itemraresuffix')
def rare_suffixes(request):
    itemTypes = ItemType.objects.order_by("name")
    itemRareSuffixes = ItemRareSuffix.objects.order_by("name")
    itemMatrix = [[False for x in range(len(itemRareSuffixes))] for x in range(len(itemTypes))]
    for sindex, itemRareSuffix in enumerate(itemRareSuffixes):
        for tindex, itemType in enumerate(itemTypes):
            if itemRareSuffix in itemType.raresuffixes:
                itemMatrix[sindex][tindex] = True
    context = {'header_tab': 'items',
                'itemTypes': itemTypes,
                'itemRaresuffixes': itemRareSuffixes,
                'itemMatrix': itemMatrix,}
    