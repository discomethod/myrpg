from django.db import models

# Create your models here.
class ItemPrefix(models.Model):
    itemprefix_name = models.CharField()
    itemprefix_flat_strength = models.IntegerField(default=0)
class ItemType(models.Model):
    itemtype_name = models.CharField()
class Item(models.Model):
    item_level = models.IntegerField(default=0)
    item_type = models.ForeignKey('ItemType')
    item_prefixes = models.ManyToManyField(ItemPrefix)
