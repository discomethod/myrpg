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
    for TYPE in TYPES:
        TYPE_CHOICES.append((TYPE[:5].upper(),TYPE))
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])
    def __unicode__(self):
        return self.name

def calculate_net_modifiables(modifiers=None, characterlevel=None, itemlevel=None):
    # assume basic default values for each of the parameters:
    # modifiers = no modifiers
    # if no character/skill/item level is given,
    #   assume our modifiers aren't being used by a character, or with an item
    #   therefore, display dependence on those values
    if modifiers == None:
        # no modifiers were passed in
        return None
    else:
        # modifiers is a list of Modifier objects
        net_modifiables = dict()
        local_percentage = dict()
        modifiables_list = Modifiable.objects.all()
        for modifiable in modifiables_list:
            for combat_type in ("offensive","defensive",):
                net_modifiables[str(modifiable).lower()+"_"+combat_type+"_min"] = 0
                net_modifiables[str(modifiable).lower()+"_"+combat_type+"_max"] = 0
                # store the global percentage modifiers
                # local modifiers will be baked into the flat values
                net_modifiables[str(modifiable).lower()+"_"+combat_type+"_percentage"] = 0
                local_percentage[str(modifiable).lower()+"_"+combat_type] = 0 # list of local percentage modifiers
        
        for modifier in modifiers:
            # process each individual modifier
            # construct the modifiable_name, e.g. psychic_offensive_min, or arcane_defensive_max
            modifiable_name = str(modifier.modifies).lower()
            if modifier.offensive:
                modifiable_name += "_offensive"
            else:
                modifiable_name += "_defensive"
            # process flat modifiers
            net_modifiables[modifiable_name+"_min"] += modifier.flat_min
            net_modifiables[modifiable_name+"_max"] += modifier.flat_max
            # process percentage modifiers
            if modifier.local:
                local_percentage[modifiable_name] += modifier.percentage
            else:
                net_modifiables[modifiable_name+"_percentage"] += modifier.percentage

        # calculate the effects of local modifiers
        for modifiable in modifiables_list:
            for combat_type in ("offensive","defensive",):
                modifiable_name = str(modifiable).lower() + "_" + combat_type
                net_modifiables[modifiable_name+"_min"] = round(net_modifiables[modifiable_name+"_min"] * (1.0 + local_percentage[modifiable_name]/100.0))
                net_modifiables[modifiable_name+"_max"] = round(net_modifiables[modifiable_name+"_max"] * (1.0 + local_percentage[modifiable_name]/100.0))
        return net_modifiables


# Core models

class Modifier(models.Model):
    # choice of attribute
    modifies = models.ForeignKey(Modifiable, blank=True, null=True)
    
    # would this modification be considered a BONUS or a MALUS?
    # if it's a good thing, beneficial = True
    # if it's a bad thing, beneficial = False
    beneficial = models.BooleanField(default=True)
    
    # is this mod for offensive rolls?
    # e.g. lightning damage defensive would be lightning resistance
    offensive = models.BooleanField(default=True)
    
    # does this mod affect local or global properties?
    # usually for percentage modifiers of armor, damage, etc.
    local = models.BooleanField(default=True)

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
            description += "+" + str(abs(self.percentage)) + "%"
            if self.percentage > 0:
                description += " increased"
            else:
                discription += " decreased"
            description += " " + ("local" if self.local else "global")
        description += " " + str(self.modifies).lower()
        if self.modifies:
            if self.modifies.type=="DAMAG":
                # modifying a damage type
                if self.offensive:
                    description += " damage"
                else:
                    description += " resistance"
            elif self.modifies.type=="ATTAC":
                # modifying an attack type
                if self.offensive:
                    description += " attack"
                else:
                    description += " defense"
        return unicode(description)
    def is_beneficial(self):
        return self.beneficial
    is_beneficial.boolean = True
    is_beneficial.short_description = "Beneficial?"
    def is_offensive(self):
        return self.offensive
    is_offensive.boolean = True
    is_offensive.short_description = "Beneficial?"

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
    def call_calculate_net_modifiables(self):
        # makes a call to calculate_net_modifiables with appropriate parameters for this affix scope
        modifiers_to_pass = list()
        for modification in self.modifications.all():
            modifiers_to_pass.append(modification)
        return calculate_net_modifiables(modifiers_to_pass)
    def get_modifications_display(self):
        # returns a single-line human-friendly description of this affix's modifications
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
        RARITY_CHOICES.append((RARITY[:5].upper(),RARITY))
    rarity = models.CharField(max_length=5, choices=RARITY_CHOICES, default=RARITY_CHOICES[0][0])
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
    attack_type = models.ForeignKey(Modifiable, related_name='attack_type', default=lambda: Modifiable.objects.filter(type="ATTAC")[0])
    success_roll_primary = models.ForeignKey(Modifiable, related_name='success_roll_primary')
    success_roll_secondary = models.ForeignKey(Modifiable, related_name='success_roll_secondary')
    effect_roll_primary = models.ForeignKey(Modifiable, related_name='effect_roll_primary')
    effect_roll_secondary = models.ForeignKey(Modifiable, related_name='effect_roll_secondary')
    def __unicode__( self ):
        return self.name
