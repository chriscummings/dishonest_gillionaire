from django.db import models
import pdb


class Item(models.Model):
	name                             = models.TextField()
	display_name                     = models.TextField(null=True)
	icon                             = models.TextField()
	guid                             = models.IntegerField() # Source/official item ID.
	can_be_hq                        = models.BooleanField(default=True)
	stack_size                       = models.IntegerField(null=True)
	jobs                             = models.TextField(null=True)
	is_dyeable                       = models.BooleanField(default=False)
	is_glamourous                    = models.BooleanField(default=False) #?
	is_untradable                    = models.BooleanField(default=False)
	is_unique                        = models.BooleanField(default=False)
	ui_category                      = models.TextField(null=True)
	vendor_price                     = models.IntegerField(null=True)

	northamerica_listings_updated_at = models.DateTimeField(null=True)
	northamerica_sales_updated_at    = models.DateTimeField(null=True)
	universalis_unresolved           = models.BooleanField(default=False)

	class Meta:
		indexes = [models.Index(fields=['guid'])]

	@staticmethod
	def flag_universalis_unresolved(item_guid):
		item = Item.objects.get(guid=item_guid)
		item.universalis_unresolved = True 
		item.save()

	def __str__(self):
		return f'({self.guid}) {self.name}'

	# the short argument prevents recursion from related models.
	def summary(self, sale_limit=3, listing_limit=3, short=False):
		summary = {}
		summary['klass'] = 'item',
		summary['id'] = self.id,
		summary['name'] = self.name
		summary['icon'] = self.icon
		summary['guid'] = self.guid

		summary['can_be_hq'] = self.can_be_hq
		summary['stack_size'] = self.stack_size
		summary['jobs'] = self.jobs
		summary['is_dyeable'] = self.is_dyeable
		summary['is_glamourous'] = self.is_glamourous
		summary['is_untradable'] = self.is_untradable
		summary['is_unique'] = self.is_unique
		summary['ui_category'] = self.ui_category
		summary['vendor_price'] = self.vendor_price

		summary['sales'] = []
		if not short:
			for sale in self.sales.all()[0:sale_limit]:
				summary['sales'].append(sale.summary())

		summary['listings'] = []
		if not short:
			for listing in self.listings.all()[0:listing_limit]:
				summary['listings'].append(listing.summary())		

		summary['recipes'] = []
		if not short:
			for recipe in self.recipes.all():
				summary['recipes'].append(recipe.summary())
				continue # REMOVE ME!

		return summary


class Recipe(models.Model):
	name          = models.TextField()
	icon          = models.TextField(null=True)
	guid          = models.IntegerField() # Source/official recipe ID.
	result_amount = models.IntegerField()
	profession    = models.TextField(null=True)

	# Relationships
	item      = models.ForeignKey(Item, related_name="recipes", on_delete=models.CASCADE)
	materials = models.ManyToManyField(Item, related_name="xxx", through="Ingredient")

	class Meta:
		indexes = [models.Index(fields=['guid'])]	

	def __str__(self):
		return f'({self.guid}) {self.name} (recipe)'

	def summary(self):
		summary = {
			'name': self.name,
			'icon': self.icon,
			'guid': self.guid,
			'profession': self.profession,
			'result_amount': self.result_amount,
			'ingredients': []
		}

		for ingredient in self.ingredients.all():
			# TODO: !!? calling short summary on this to prevent recursive action... maybe the argument should be long=False??
			summary['ingredients'].append(ingredient.summary(short=False, sale_limit=0, listing_limit=0))

		return summary


class Ingredient(models.Model):
	""" Many-to-many Recipe/Item through model. """

	count  = models.IntegerField(null=True)

	# Relationships
	item   = models.ForeignKey(Item, related_name="ingredients", on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)


	def summary(self, short=False, sale_limit=0, listing_limit=0):
		item_summary = {}

		item_summary = self.item.summary()

		item_summary["material_count"] = self.count

		return item_summary


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
	hq             = models.BooleanField(default=False)

	# Relationships
	item = models.ForeignKey(Item, related_name='listings', on_delete=models.CASCADE)

	class Meta:
		indexes = [models.Index(fields=['listing_guid'])]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} from {self.retainer_name}'

	def summary(self):
		return {
			'id': self.id,
			'region': self.region,
			'world': self.world,
			'guid': self.listing_guid,
			'retainer_guid': self.retainer_guid,
			'retainer_name': self.retainer_name,
			'price_per_unit': self.price_per_unit,
			'quantity': self.quantity,
			'total': self.total,
			'created_at': self.created_at
		}


class Region(models.Model):
	name = models.TextField()


class DataCenter(models.Model):
	name = models.TextField()

	# Relationships
	region = models.ForeignKey(Region, related_name='data_centers', on_delete=models.CASCADE)


class World(models.Model):
	name = models.TextField()

	# Relationships
	data_center = models.ForeignKey(DataCenter, related_name='worlds', on_delete=models.CASCADE)

class WorldItemFact(models.Model):
	sold_mean      = models.FloatField()
	sold_median    = models.FloatField()
	sold_avg       = models.FloatField()
	sold_high      = models.IntegerField()
	sold_low       = models.IntegerField()
	sold_count     = models.IntegerField()

	sellers_count  = models.IntegerField()

	list_mean   = models.FloatField()
	list_median = models.FloatField()
	list_avg    = models.FloatField()
	list_high   = models.IntegerField()
	list_low    = models.IntegerField()
	list_count  = models.IntegerField()

	hq = models.BooleanField(default=False)

	calculated_at = models.DateTimeField()

class RunTime(models.Model):
	""" Tracking process runtimes.
	"""
	process_name = models.TextField()
	process_caller = models.TextField()
	started_at = models.DateTimeField()
	ended_at = models.DateTimeField(null=True)
	run_time = models.TextField(null=True)


class Sale(models.Model):
	""" A sold market board listing.
	"""
	region         = models.TextField()
	world          = models.TextField()
	price_per_unit = models.IntegerField()
	quantity       = models.IntegerField()
	buyer_name     = models.TextField()
	sold_at        = models.DateTimeField()
	hq             = models.BooleanField(default=False)

	# Relationships
	item = models.ForeignKey(Item, related_name='sales', on_delete=models.CASCADE)

	class Meta:
		indexes = [models.Index(fields=['sold_at', 'buyer_name'])]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} by {self.buyer_name}'

	def summary(self):
		return {
			'id': self.id,		
			'region': self.region,
			'world': self.world,
			'price_per_unit': self.price_per_unit,
			'quantity': self.quantity,
			'buyer_name': self.buyer_name,
			'sold_at': self.sold_at
		}

