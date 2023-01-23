from django.db import models

class Item(models.Model):
	name = models.TextField()
	icon = models.TextField()
	guid = models.IntegerField() # Source/official item ID.

class Recipe(models.Model):
	name = models.TextField()
	icon = models.TextField()
	guid = models.IntegerField() # Source/official item ID.

	#item = models.ForeignKey(Item, null=True)#?













