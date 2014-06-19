from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

@login_required
@permission_required('web.edit_itemraresuffix')
def rare_suffixes(request):
	pass
