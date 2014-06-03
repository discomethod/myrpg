from django.db import models

# Game definitions

"""
PRIMARY_ATTRIBUTES:
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
    class Meta:
        verbose_name = "item slot"

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
    raresuffixes = models.ManyToManyField('ItemRareSuffix', blank=True)
    equippable = models.BooleanField(default=False)
    def __unicode__( self ):
        return self.name
    def is_equippable(self):
        return self.equippable
    is_equippable.boolean = True
    is_equippable.short_description = 'Equippable?'
    class Meta:
        verbose_name = "item type"

class ItemRarePrefix(models.Model):
    name = models.CharField(max_length=64)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "rare item prefix"
        verbose_name_plural = "rare item prefixes"

class ItemRareSuffix(models.Model):
    name = models.CharField(max_length=64)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "rare item suffix"
        verbose_name_plural = "rare item suffixes"

class Modifiable(models.Model):
    name = models.CharField(max_length=64)
    # type of modifiable
    TYPE_CHOICES = []
    TYPES = ['Primary Attribute', 'Secondary Attribute', 'Damage Type', 'Attack Type',]
    offensive = models.BooleanField(default=True)
    for TYPE in TYPES:
        TYPE_CHOICES.append((TYPE[:3].upper(),TYPE))
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])
    def __unicode__(self):
        return self.name

# Core models

class Modifier(models.Model):
    # choice of attribute
    PRIMARY_ATTRIBUTES = ['Strength', 'Dexterity', 'Intelligence', 'Vitality', 'Charisma', 'Wisdom', ]
    SECONDARY_ATTRIBUTES = ['Health', 'Mana', 'Energy', 'Fury', 'Initiative', 'Actions',]
    ELEMENTS = ['Physical Damage', 'Spell Damage', 'Shadow Damage', 'Arcane Damage', 'Lightning Damage', 'Poison Damage', 'Fire Damage', 'Ice Damage', 'Psychic Damage', 'Chaos Damage', ]
    ATTACKS = ['Melee Attack', 'Ranged Attack', 'Social Attack', 'Magic Attack', 'Curse Attack', ]
    modifies = models.ForeignKey(Modifiable, blank=True, null=True)
    
    # choice of dependency
    DEPENDENCIES = ['None', 'CharacterLevel', 'SkillLevel','ItemLevel',]
    DEPENDENCY_CHOICES = []
    for DEPENDENCY in DEPENDENCIES:
        DEPENDENCY_CHOICES.append((DEPENDENCY[:3].upper(),DEPENDENCY))
    dependency = models.CharField(max_length=3, choices=DEPENDENCY_CHOICES, default=DEPENDENCY_CHOICES[0][0])
    
    # would this modification be considered a BONUS or a MALUS?
    # if it's a good thing, beneficial = True
    # if it's a bad thing, beneficial = False
    beneficial = models.BooleanField(default=True)
    
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
        description += " " + str(self.modifies).lower()
        if self.modifies:
            if self.modifies.type=="DAM":
                # modifying a damage type
                if self.modifies.offensive:
                    description += " damage"
                else:
                    description += " resistance"
            elif self.modifies.type=="ATT":
                # modifying an attack type
                if self.modifies.offensive:
                    description += " attack"
                else:
                    description += " defense"
        return unicode(description)
    
# Advanced models

class CharacterClass(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    base = models.ForeignKey('self', blank=True, null=True)
    modification = models.ManyToManyField(Modifier, blank=True) # a class can have no modifications
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "character class"
        verbose_name_plural = "character classes"

class CharacterRace(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    modification = models.ManyToManyField(Modifier, blank=True) # a race can have no modifications
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "character race"

class Character(models.Model):
    # character name
    name = models.CharField(max_length=64)
    # character level
    level = models.IntegerField(default=1)
    # character experience
    experience = models.IntegerField(default=0)
    # character class
    character_class = models.ForeignKey(CharacterClass, blank=True, null=True)
    # character race
    character_race = models.ForeignKey(CharacterRace, blank=True, null=True)
    
    modification = models.ManyToManyField(Modifier)
    
class ItemAffixGroup(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    prefix = models.BooleanField(default=True)
    def __unicode__( self ):
        return self.name
    class Meta:
        verbose_name = "item affix group"

class ItemAffix(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    group = models.ForeignKey(ItemAffixGroup)
    prefix = models.BooleanField(default=True)
    modifications = models.ManyToManyField(Modifier, blank=True)
    ilevel = models.IntegerField(default=0)
    def __unicode__( self ):
        return self.name
    def get_modifications_display(self):
        result = ""
        for modification in self.modifications.all():
            result += str(modification) + ", "
        result = result[:-2]
        return result
    class Meta:
        verbose_name = "item affix"
        verbose_name_plural = "item affixes"

class Item(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    ilevel = models.IntegerField(default=0)
    itype = models.ForeignKey(ItemType) # an item has exactly one item type
    base = models.ForeignKey('self', blank=True, null=True) # an item may or may not be based on another item
    affixes = models.ManyToManyField(ItemAffix, blank=True) # possible to have zero or more affixes
    slots = models.ManyToManyField(ItemSlot, blank=True) # an item can occupy multiple slots, or no slot
    modification = models.ManyToManyField(Modifier, blank=True) # an item can have no modifications
    RARITIES = ['Common', 'Uncommon', 'Rare','Epic',]
    RARITY_CHOICES = []
    for RARITY in RARITIES:
        RARITY_CHOICES.append((RARITY[:3].upper(),RARITY))
    rarity = models.CharField(max_length=3, choices=RARITY_CHOICES, default=RARITY_CHOICES[0][0])
    def __unicode__( self ):
        return self.name
    def is_base(self):
        return not self.base
    is_base.admin_order_field = 'base'
    is_base.boolean = True
    is_base.short_description = 'Base Item'

class Skill(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    classes = models.ManyToManyField(CharacterClass, blank=True) # which classes can use this skill
    attack_type = models.ForeignKey(Modifiable, related_name='attack_type', default=lambda: Modifiable.objects.filter(type="ATT")[0])
    success_roll_primary = models.ForeignKey(Modifiable, related_name='success_roll_primary')
    success_roll_secondary = models.ForeignKey(Modifiable, related_name='success_roll_secondary')
    effect_roll_primary = models.ForeignKey(Modifiable, related_name='effect_roll_primary')
    effect_roll_secondary = models.ForeignKey(Modifiable, related_name='effect_roll_secondary')
    def __unicode__( self ):
        return self.name
