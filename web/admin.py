from django.contrib import admin
from web.models import Modifier, Item, ItemPrefix, ItemSuffix, ItemType, ItemSlot

admin.site.register(Modifier)
admin.site.register(Item)
admin.site.register(ItemType)
admin.site.register(ItemSlot)
admin.site.register(ItemPrefix)
admin.site.register(ItemSuffix)
