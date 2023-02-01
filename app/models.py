from django.db import models

class Item(models.Model):
	""" And in-game item.
	"""
	name                             = models.TextField()
	icon                             = models.TextField()
	guid                             = models.IntegerField() # Source/official item ID.
	northamerica_listings_updated_at = models.DateTimeField(null=True)
	northamerica_sales_updated_at    = models.DateTimeField(null=True)
	universalis_unresolved           = models.BooleanField(default=False)

	class Meta:
		indexes = [models.Index(fields=['guid'])]

	@staticmethod
	def flag_universalis_unresolved(item_guid):
		item = Item.objects.get(guid=item_guid)

		# FIXME: handle this?
		if not item: raise "Item "+str(item_guid)+" not found."

		item.universalis_unresolved = True 
		item.save()

	def __str__(self):
		return f'({self.guid}) {self.name}'

class Recipe(models.Model):
	""" Resulting item(s) and ingredients.
	"""
	name          = models.TextField()
	icon          = models.TextField(null=True)
	guid          = models.IntegerField() # Source/official recipe ID.
	result_amount = models.IntegerField()

	# Relationships
	item        = models.ForeignKey(Item, related_name="recipe", on_delete=models.CASCADE)
	ingredients = models.ManyToManyField(Item, related_name="recipes", through="RecipeItemIngredient")

	class Meta:
		indexes = [models.Index(fields=['guid'])]	

	def __str__(self):
		return f'({self.guid}) {self.name} (recipe)'

class RecipeItemIngredient(models.Model):
	""" Many-to-many Recipe/Item through model.
	"""
	count  = models.IntegerField(null=True)

	# Relationships
	item   = models.ForeignKey(Item, related_name="enrollments", on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, related_name="enrollments", on_delete=models.CASCADE)

class Listing(models.Model):
	""" A market board listing.
	"""
	region         = models.TextField()
	world          = models.TextField()
	listing_guid   = models.TextField() # Source/official listing ID.
	retainer_guid  = models.TextField() # Source/official retainer ID.
	retainer_name  = models.TextField()
	price_per_unit = models.IntegerField()
	quantity       = models.IntegerField()
	total          = models.IntegerField()
	created_at     = models.DateTimeField(auto_now_add=True)

	# Relationships
	item = models.ForeignKey(Item, related_name='listings', on_delete=models.CASCADE)

	class Meta:
		indexes = [models.Index(fields=['listing_guid'])]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} from {self.retainer_name}'

class Sale(models.Model):
	""" A sold market board listing.
	"""
	region         = models.TextField()
	world          = models.TextField()
	price_per_unit = models.IntegerField()
	quantity       = models.IntegerField()
	buyer_name     = models.TextField()
	sold_at        = models.DateTimeField()

	# Relationships
	item = models.ForeignKey(Item, related_name='sales', on_delete=models.CASCADE)

	class Meta:
		indexes = [models.Index(fields=['sold_at', 'buyer_name'])]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} by {self.buyer_name}'

