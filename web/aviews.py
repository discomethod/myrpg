from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render

from web.models import ItemType, ItemRareSuffix

def can_view_admin_pages(user):
    if not user:
        return False
    if user.has_perm('web.edit_itemraresuffix'):
        return True
    return False

@login_required
@user_passes_test(lambda user: can_view_admin_pages(user))
def index(request):
    context = {'header_tab': 'admin',}
    return render(request,'web/admin/index.html', context)

@login_required
@permission_required('web.edit_itemraresuffix')
def rare_suffixes(request):
    item_types = ItemType.objects.order_by("name")
    item_rare_suffixes = ItemRareSuffix.objects.order_by("name")
    item_matrix = [[False for x in range(len(item_types))] for x in range(len(item_rare_suffixes))]
    for sindex, item_rare_suffix in enumerate(item_rare_suffixes):
        for tindex, item_type in enumerate(item_types):
            if item_type.raresuffixes.filter(pk=item_rare_suffix.pk).exists():
                item_matrix[sindex][tindex] = True
    context = {'header_tab': 'admin',
                'item_types': item_types,
                'item_types_len': len(item_types),
                'item_rare_suffixes': item_rare_suffixes,
                'item_rare_suffixes_len': len(item_rare_suffixes),
                'item_matrix': item_matrix,}
    return render(request,'web/admin/raresuffixes.html', context)
