from django.db import models

# Game definitions

"""
ATTRIBUTES:
    Strength        Vitality
    Dexterity       Charisma
    Intelligence    Wisdom
"""
class Attribute(models.Model):
    name = models.CharField(max_length=64)
    abbr = models.CharField(max_length=8)

"""
ELEMENTS:
    Physical    Spell
    Shadow      Arcane
    Lightning   Poison
    Fire        Ice
    Psychich    Chaos
"""
class Element(models.Model):
    name = models.CharField(max_length=64)
    abbr = models.CharField(max_length=8)

"""
SLOTS:
    Head
    Neck
    Chest
    Cape
    MainHand
    OffHand
    Waist
    Legs
    Feet
    Rings 1-2
    Accessories 1-3
"""
class ItemSlot(models.Model):
    name = models.CharField(max_length=64)

"""
ITEM TYPES:
    WEAPONS:
        Bow
        Sword
        Axe
        Spear
        Shield
    ARMOR:
        Light
        Medium
        Heavy
"""
class ItemType(models.Model):
    name = models.CharField(max_length=64)

# Core models
    
class CommonStats(models.Model):
    attribute_flat = dict() # flat bonuses to attributes
    attribute_percentage = dict() # integer values, +25 => +25%
    for attribute in Attribute.objects.all():
        attribute_flat[attribute.name] = models.IntegerField(default=0)
        attribute_percentage[attribute.name] = models.IntegerField(default=0)

    # spells only benefit from bonuses of the same element, or spell
    damage_flat_min = dict() # bonus minimum damage applied to all attacks
    damage_flat_max = dict() # bonus maximum damage applied to all attacks
    damage_percentage = dict() # integer values, +25 => +25%
    for element in Element.objects.all():
        damage_flat_min[element.name] = models.IntegerField(default=0)
        damage_flat_max[element.name] = models.IntegerField(default=0)
        damage_percentage[element.name] = models.IntegerField(default=0)
    class Meta:
        abstract = True
    
# Extension models
    
class Character(CommonStats):
    # character name
    name = models.CharField(max_length=64)
    # character level
    level = models.IntegerField(default=1)
    # character experience
    experience = models.IntegerField(default=0)
    
    # store base character attribute values
    attribute_base = dict()
    for attribute in Attribute.objects.all():
        attribute_base[attribute.name] = models.IntegerField(default=0)
    
    def effective_attribute(attribute):
        return int(round((1.0 + attribute_percentage[attribute]/100.0) * (attribute_base[attribute]+attribute_flat[attribute]),0))
    
class ItemPrefix(CommonStats):
    name = models.CharField(max_length=64)

class ItemSuffix(CommonStats):
    name = models.CharField(max_length=64)
    
class Item(CommonStats):
    ITEM_TYPES = ('Light','Medium','Heavy','Bow','Sword','Shield','Axe','Spear',)
    ITEM_TYPE_CHOICES = {}
    for ITEM_TYPE in ITEM_TYPES:
        ITEM_TYPE_CHOICES.append((ITEM_TYPE[:3].upper(),ITEM_TYPE))
        
    ilevel = models.IntegerField(default=0)
    itype = models.CharField(max_length=3, choices=ITEM_TYPE_CHOICES, default=LIGHT)
    prefixes = models.ManyToManyField(ItemPrefix)
    suffixes = models.ManyToManyField(ItemSuffix)
    slots = models.ManyToManyField(ItemSlot) # an item can occupy multiple slots
