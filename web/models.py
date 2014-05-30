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
    def __unicode__( self ):
        return self.name

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
    def __unicode__( self ):
        return self.name

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
                description += ("+" if self.flat_min>=0 else "-") + str(abs(self.flat_min)) + " to " + ("+" if self.flat_max>=0 else "-") + str(abs(self.flat_max))
            else:
                description += ("+" if self.flat_min>=0 else "-") + str(abs(self.flat_min))
        if self.percentage != 0:
            if description != "":
                description += ", "
            if self.get_dependency_display()!='None':
                description += "+"
            description += str(abs(self.percentage)) + "%"
            if self.get_dependency_display()=='CharacterLevel':
                description += " of your level"
            elif self.get_dependency_display()=='SkillLevel':
                description += " of your skill level"
            elif self.get_dependency_display()=='ItemLevel':
                description += " of your item level"
            elif self.get_dependency_display()=='None':
                if self.percentage > 0:
                    description += " increased"
                else:
                    discription += " decreased"
        description += " " + self.get_modifiable_display().lower()
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
    modification = models.ManyToManyField(Modifier, blank=True)
    def __unicode__( self ):
        return self.name
    def get_modifications_display(self):
        result = ""
        for modification in self.modification.all():
            result += str(modification) + ", "
        result = result[:-2]
        return result

class ItemSuffix(models.Model):
    name = models.CharField(max_length=64)
    modification = models.ManyToManyField(Modifier, blank=True)
    def __unicode__( self ):
        return self.name
    
class Item(models.Model):
    name = models.CharField(max_length=64)
    ilevel = models.IntegerField(default=0)
    itype = models.ForeignKey('ItemType') # an item can only have one item type
    prefixes = models.ManyToManyField(ItemPrefix,blank=True) # possible to have no prefixes
    suffixes = models.ManyToManyField(ItemSuffix, blank=True) # possible to have no suffixes
    slots = models.ManyToManyField(ItemSlot, blank=True) # an item can occupy multiple slots, or no slot
    modification = models.ManyToManyField(Modifier, blank=True) # an item can have no modifications
    def __unicode__( self ):
        return self.name

