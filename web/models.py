from django.db import models

CHARACTER_ATTRIBUTES = ("Strength","Dexterity","Intelligence","Charisma","Vitality","Wisdom",)

# Create your models here.


class Character(models.Model):
    for attribute in CHARACTER_ATTRIBUTES:
        character_attribute[attribute] = models.IntegerField(default=1)

class ItemSlot(models.Model):
    itemslot_name = models.CharField(max_length=64)
class ItemPrefix(models.Model):
    itemprefix_name = models.CharField(max_length=64)
    itemprefix_flat_strength = models.IntegerField(default=0)
class ItemType(models.Model):
    itemtype_name = models.CharField(max_length=64)
class Item(models.Model):
    item_level = models.IntegerField(default=0)
    item_type = models.ForeignKey('ItemType')
    item_prefixes = models.ManyToManyField(ItemPrefix)
    item_itemslot = models.ManyToManyField(ItemSlot) # an item can occupy multiple slots
