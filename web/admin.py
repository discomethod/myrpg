from django.contrib import admin
from web.models import CharacterRace, CharacterClass
from web.models import Modifiable, Modifier
from web.models import Item, ItemAffix, ItemType, ItemSlot, ItemAffixGroup, ItemRarePrefix, ItemRareSuffix

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_base','base')
    list_filter = ['base']

class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name','is_equippable')

class ItemAffixAdmin(admin.ModelAdmin):
    list_display = ('name','get_modifications_display','group')
    list_filter = ['group']

class ModifiableAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ['type']


admin.site.register(CharacterRace)
admin.site.register(CharacterClass)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemType, ItemTypeAdmin)
admin.site.register(ItemRarePrefix)
admin.site.register(ItemRareSuffix)
admin.site.register(ItemSlot)
admin.site.register(ItemAffix, ItemAffixAdmin)
admin.site.register(ItemAffixGroup)

admin.site.register(Modifier)
admin.site.register(Modifiable, ModifiableAdmin)
