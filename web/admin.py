from django.contrib import admin
from web.models import Modifier, Item, ItemPrefix, ItemSuffix, ItemType, ItemSlot

class ItemPrefixAdmin(admin.ModelAdmin):
    list_display = ('name','get_modifications_display')

admin.site.register(Modifier)
admin.site.register(Item)
admin.site.register(ItemType)
admin.site.register(ItemSlot)
admin.site.register(ItemPrefix, ItemPrefixAdmin)
admin.site.register(ItemSuffix)

