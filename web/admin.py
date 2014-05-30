from django.contrib import admin
from web.models import Modifier, Item, ItemPrefix, ItemSuffix, ItemType, ItemSlot, ItemPrefixGroup, ItemSuffixGroup

class ItemPrefixAdmin(admin.ModelAdmin):
    list_display = ('name','get_modifications_display','group')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_base','base')
    list_filter = ['base']

admin.site.register(Modifier)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemType)
admin.site.register(ItemSlot)
admin.site.register(ItemPrefix, ItemPrefixAdmin)
admin.site.register(ItemSuffix)
admin.site.register(ItemPrefixGroup)
admin.site.register(ItemSuffixGroup)

