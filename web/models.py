from django.db import models

# --- ENGINE MODELS --- #

class Modifiable(models.Model):
    name = models.CharField(max_length=64)
    # type of modifiable
    TYPE_CHOICES = []
    TYPES = ["Primary Attribute", "Secondary Attribute", "Damage Type", "Attack Type",]
    for TYPE in TYPES:
        TYPE_CHOICES.append((TYPE[:5].upper(),TYPE))
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])
    def __unicode__(self):
        return self.name

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

# --- HELPER FUNCTIONS --- #

def get_modifiable_name(modifiable, combat_type=None):
    """Returns the standardized dictionary lookup for modifiables.

    Examples: ice_defensive, mana-regeneration_offensive, momentum-regneration
    Affects how display_net_modifiable reverse parses the modifiable name.
    """
    return_string = str(modifiable).replace(" ","-").lower()
    if combat_type is not None:
        return_string += "_" + combat_type
    return return_string

def get_net_modifiables(modifiers=None, characterlevel=None, itemlevel=None):
    """Parses a list of modifiers and returns a verbose dictionary of all net modifiables.

    The returned dictionary will hold values of 0 for unmodified attributes.
    """
    if modifiers == None:
        # no modifiers were passed in
        return None
    else:
        # modifiers is a list of Modifier objects
        # if no character/skill/item level is given,
        #   assume our modifiers aren't being used by a character or with an item
        #   therefore, display dependence on those values
        net_modifiables = dict() # this will be our return dictionary
        local_percentage = dict() # this dictionary is used only within the scope of this function - it stores local modifiers

        for modifiable in Modifiable.objects.all():
            for combat_type in ("offensive","defensive",):
                modifiable_name = get_modifiable_name(modifiable,combat_type)
                net_modifiables[modifiable_name+"_min"] = 0
                net_modifiables[modifiable_name+"_max"] = 0
                # store the global percentage modifiers
                # local modifiers will be baked into the flat values
                net_modifiables[modifiable_name+"_percentage"] = 0
                local_percentage[modifiable_name] = 0 # list of local percentage modifiers
        
        for modifier in modifiers:
            # process each individual modifier
            # construct the modifiable_name, e.g. psychic_offensive_min, or arcane_defensive_max
            if modifier.offensive:
                combat_type = "offensive"
            else:
                combat_type = "defensive"
            modifiable_name = get_modifiable_name(modifier.modifies,combat_type)
            # process flat modifiers
            net_modifiables[modifiable_name+"_min"] += modifier.flat_min
            net_modifiables[modifiable_name+"_max"] += modifier.flat_max
            # process percentage modifiers
            if modifier.local:
                local_percentage[modifiable_name] += modifier.percentage
            else:
                net_modifiables[modifiable_name+"_percentage"] += modifier.percentage

        # calculate the effects of local modifiers
        for modifiable in Modifiable.objects.all():
            for combat_type in ("offensive","defensive",):
                modifiable_name = get_modifiable_name(modifiable,combat_type)
                net_modifiables[modifiable_name+"_min"] = int(round(net_modifiables[modifiable_name+"_min"] * (1.0 + local_percentage[modifiable_name]/100.0)))
                net_modifiables[modifiable_name+"_max"] = int(round(net_modifiables[modifiable_name+"_max"] * (1.0 + local_percentage[modifiable_name]/100.0)))
        return net_modifiables

def trim_net_modifiables(net_modifiables):
    """Parses a dictionary of net modifiables and returns a list of non-zero net modifiables as dictionaries.

    The returned dictionary will not hold any unmodified attributes.
    """
    # takes a raw net_modifiables dictionary and filters out the important (i.e., non-zero) elements
    # this will assume local modifiers to all elements
    result = list()
    for modifiable in Modifiable.objects.all():
        for combat_type in ("offensive","defensive",):
            modifiable_name = get_modifiable_name(modifiable,combat_type)
            if net_modifiables[modifiable_name+"_min"] is not 0 or net_modifiables[modifiable_name+"_max"] is not 0 or net_modifiables[modifiable_name+"_percentage"] is not 0:
                # there is a flat modifier or a percentage modifier
                # append (modifiable_name, min, min, percentage)
                result.append(dict(modifiable=modifiable,combat_type=combat_type,min=net_modifiables[modifiable_name+"_min"],max=net_modifiables[modifiable_name+"_max"],percentage=net_modifiables[modifiable_name+"_percentage"]))
    return result

def display_net_modifiable(net_modifiable):
    """Parses a dictionary of net modifiable values and returns a list human-friendly display string.

    The length of the return list should be either 1 or 2, 1 if there is only flat or percentage, 2 if there is both.
    Example: (<Modifiable: Ice>,"offensive","1","2","0") will yield ["+1 to 2 ice damage",]
    Example: (<Modifiable: Poison>,"defensive","2","2","50") will yield ["+2 poison resistance","+50% poison resistance",]"""
    result = list()
    modifiable = net_modifiable["modifiable"]
    combat_type = net_modifiable["combat_type"]
    if net_modifiable["min"] is not 0 or net_modifiable["max"] is not 0:
        # flat values are not 0
        description = ""
        if net_modifiable["min"] != net_modifiable["max"]:
            description += ("+" if net_modifiable["min"]>=0 else "-") + str(abs(net_modifiable["min"])) + " to " + ("+" if net_modifiable["max"]>=0 else "-") + str(abs(net_modifiable["max"]))
        else:
            description += ("+" if net_modifiable["min"]>=0 else "-") + str(abs(net_modifiable["min"]))
        description += " " + str(modifiable).lower()
        if modifiable.type=="DAMAG":
            # modifying a damage type
            if combat_type=="offensive":
                description += " damage"
            else:
                description += " resistance"
        elif modifiable.type=="ATTAC":
            # modifying an attack type
            if combat_type=="offensive":
                description += " attack"
            else:
                description += " defense"
        result.append(description)
    if net_modifiable["percentage"] is not 0:
        # percentage value is not 0
        description = ""
        description += "+" + str(abs(net_modifiable["percentage"])) + "%"
        if net_modifiable["percentage"] > 0:
            description += " increased"
        else:
            discription += " decreased"
        description += " global" # all local mods are already baked into the flat values
        description += " " + str(modifiable).lower()
        if modifiable.type=="DAMAG":
            # modifying a damage type
            if combat_type=="offensive":
                description += " damage"
            else:
                description += " resistance"
        elif modifiable.type=="ATTAC":
            # modifying an attack type
            if combat_type=="offensive":
                description += " attack"
            else:
                description += " defense"
        result.append(description)
    return result

# --- GAME MODELS --- #

class CharacterClass(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    base = models.ForeignKey('self', blank=True, null=True)
    modifications = models.ManyToManyField(Modifier, blank=True) # a class can have no modifications
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "character class"
        verbose_name_plural = "character classes"

class CharacterRace(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    modifications = models.ManyToManyField(Modifier, blank=True) # a race can have no modifications
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
    
    modifications = models.ManyToManyField(Modifier)

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
    def __unicode__(self):
        return self.name
    def is_equippable(self):
        return self.equippable
    is_equippable.boolean = True
    is_equippable.short_description = "Equippable?"
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
    def call_get_net_modifiables(self):
        # makes a call to get_net_modifiables with appropriate parameters for this affix scope
        modifiers_to_pass = list()
        for modification in self.modifications.all():
            modifiers_to_pass.append(modification)
        return get_net_modifiables(modifiers_to_pass)
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
    modifications = models.ManyToManyField(Modifier, blank=True) # an item can have no modifications
    RARITIES = ["Common", "Uncommon", "Rare", "Epic",]
    RARITY_CHOICES = []
    for RARITY in RARITIES:
        RARITY_CHOICES.append((RARITY[:5].upper(),RARITY))
    rarity = models.CharField(max_length=5, choices=RARITY_CHOICES, default=RARITY_CHOICES[0][0])
    def __unicode__( self ):
        return self.name
    def call_get_net_modifiables(self):
        # makes a call to get_net_modifiables with appropriate parameters for this item scope
        modifiers_to_pass = list()
        for modification in self.modifications.all():
            modifiers_to_pass.append(modification)
        for affix in self.affixes.all():
            for modification in affix.modifications.all():
                modifiers_to_pass.append(modification)
        return get_net_modifiables(modifiers_to_pass)
    def is_base(self):
        return not self.base or self.base is self
    is_base.admin_order_field = "base"
    is_base.boolean = True
    is_base.short_description = "Base Item"

class Skill(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    classes = models.ManyToManyField(CharacterClass, blank=True) # which classes can use this skill
    attack_type = models.ForeignKey(Modifiable, related_name='attack_type', default=lambda: Modifiable.objects.filter(type="ATTAC")[0])
    success_roll_primary = models.ForeignKey(Modifiable, related_name='success_roll_primary')
    success_roll_secondary = models.ForeignKey(Modifiable, related_name='success_roll_secondary')
    effect_roll_primary = models.ForeignKey(Modifiable, related_name='effect_roll_primary')
    effect_roll_secondary = models.ForeignKey(Modifiable, related_name='effect_roll_secondary')
    def __unicode__(self):
        return self.name
