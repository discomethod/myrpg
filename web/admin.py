from django.contrib import admin
from web.models import Modifier, Item, ItemAffix, ItemType, ItemSlot, ItemAffixGroup, ItemRarePrefix, ItemRareSuffix

class ItemAffixAdmin(admin.ModelAdmin):
    list_display = ('name','get_modifications_display','group')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_base','base')
    list_filter = ['base']

admin.site.register(Modifier)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemType)
admin.site.register(ItemRarePrefix)
admin.site.register(ItemRareSuffix)
admin.site.register(ItemSlot)
admin.site.register(ItemAffix, ItemAffixAdmin)
admin.site.register(ItemAffixGroup)
