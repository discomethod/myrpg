from django.db import models

# Game definitions

"""
ATTRIBUTES:
    Strength        Vitality
    Dexterity       Charisma
    Intelligence    Wisdom
"""

"""
ELEMENTS:
    Physical    Spell
    Shadow      Arcane
    Lightning   Poison
    Fire        Ice
    Psychic     Chaos
"""

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

class Modifier(models.Model):
    # choice of attribute
    ATTRIBUTES = ['Strength', 'Dexterity', 'Intelligence', 'Vitality', 'Charisma', 'Wisdom', ]
    ELEMENTS = ['Physical Damage', 'Spell Damage', 'Shadow Damage', 'Arcane Damage', 'Lightning Damage', 'Poison Damage', 'Fire Damage', 'Ice Damage', 'Psychic Damage', 'Chaos Damage', ]
    MODIFIABLE_CHOICES = []
    MODIFIABLES = ATTRIBUTES + ELEMENTS
    for MODIFIABLE in MODIFIABLES:
        MODIFIABLE_CHOICES.append((MODIFIABLE[:3].upper(),MODIFIABLE))
    modifiable = models.CharField(max_length=3, choices=MODIFIABLE_CHOICES, default=MODIFIABLE_CHOICES[0][0])
    
    # choice of dependency
    DEPENDENCIES = ['None', 'CharacterLevel', 'SkillLevel','ItemLevel',]
    DEPENDENCY_CHOICES = []
    for DEPENDENCY in DEPENDENCIES:
        DEPENDENCY_CHOICES.append((DEPENDENCY[:3].upper(),DEPENDENCY))
    dependency = models.CharField(max_length=3, choices=DEPENDENCY_CHOICES, default=DEPENDENCY_CHOICES[0][0])
    
    # description of modification
    flat_min = models.IntegerField(default=0)
    flat_max = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    total_min = models.IntegerField(default=0)
    total_max = models.IntegerField(default=0)
    bound_lower = models.BooleanField(default=False)
    bound_upper = models.BooleanField(default=False)
    
    def __unicode__( self ):
        # cook up string representation of this modifier
        description = ""
        if self.flat_min != 0 or self.flat_max != 0:
            # there is a flat modifier
            if self.flat_min != self.flat_max:
                description += str("+" if self.flat_min>=0 else "-" + abs(self.flat_min)) + " to " + str("+" if self.flat_max>=0 else "-" + abs(self.flat_max))
            else:
                description += str("+" if self.flat_min>=0 else "-" + abs(self.flat_min))
        if self.percentage != 0:
            if description != "":
                description += ", "
            if self.percentage > 0:
                description += "+"
            else:
                discription += "-"
            description += str(abs(self.percentage)) + "%"
            if self.dependency=='None':
                description += " some dependency"
        description += " " + self.modifiable
        return description
    
# Advanced models
    
class Character(models.Model):
    # character name
    name = models.CharField(max_length=64)
    # character level
    level = models.IntegerField(default=1)
    # character experience
    experience = models.IntegerField(default=0)
    
    modification = models.ManyToManyField(Modifier)
    
    
class ItemPrefix(models.Model):
    name = models.CharField(max_length=64)
    modification = models.ManyToManyField(Modifier)

class ItemSuffix(models.Model):
    name = models.CharField(max_length=64)
    modification = models.ManyToManyField(Modifier)
    
class Item(models.Model):    
    ilevel = models.IntegerField(default=0)
    itype = models.ForeignKey('ItemType') # an item can only have one item type
    prefixes = models.ManyToManyField(ItemPrefix)
    suffixes = models.ManyToManyField(ItemSuffix)
    slots = models.ManyToManyField(ItemSlot) # an item can occupy multiple slots
    modification = models.ManyToManyField(Modifier)
