from django.db import models
import pdb


class Item(models.Model):
	name                             = models.TextField()
	display_name                     = models.TextField()
	icon                             = models.TextField()
	guid                             = models.IntegerField() # Source/official item ID.
	can_be_hq                        = models.BooleanField(default=False)
	stack_size                       = models.IntegerField()
	jobs                             = models.TextField()
	is_dyeable                       = models.BooleanField(default=False)
	is_glamourous                    = models.BooleanField(default=False)
	is_untradable                    = models.BooleanField(default=False)
	is_marketable                    = models.BooleanField(default=False)
	is_unique                        = models.BooleanField(default=False)
	game_ui_category                 = models.TextField()
	vendor_price                     = models.IntegerField()
	game_search_category             = models.TextField()
	universalis_unresolved           = models.BooleanField(default=False)


	northamerica_listings_updated_at = models.DateTimeField(null=True)
	northamerica_sales_updated_at    = models.DateTimeField(null=True)

	market_updated_at = models.DateTimeField(null=True)
	listsings_updated_at = models.DateTimeField(null=True)
	sales_updated_at = models.DateTimeField(null=True)
	facts_updated_at = models.DateTimeField(null=True)



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
		summary['game_ui_category'] = self.game_ui_category
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
	icon          = models.TextField()
	guid          = models.IntegerField() # Source/official recipe ID.
	result_amount = models.IntegerField()
	profession    = models.TextField()
	level         = models.IntegerField()

	# Relationships
	item      = models.ForeignKey(Item, related_name="recipes", on_delete=models.CASCADE)
	materials = models.ManyToManyField(Item, through="Ingredient")

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

	count  = models.IntegerField()

	# Relationships
	item   = models.ForeignKey(Item, related_name="ingredients", on_delete=models.CASCADE)
	recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)


	def summary(self, short=False, sale_limit=0, listing_limit=0):
		item_summary = {}

		item_summary = self.item.summary()

		item_summary["material_count"] = self.count

		return item_summary
		

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


class Listing(models.Model):
	""" A market board listing.
	"""
	listing_guid   = models.TextField() # Source/official listing ID.
	retainer_guid  = models.TextField() # Source/official retainer ID.
	retainer_name  = models.TextField()
	price_per_unit = models.IntegerField()
	quantity       = models.IntegerField()
	total          = models.IntegerField()
	created_at     = models.DateTimeField(auto_now_add=True)
	hq             = models.BooleanField(default=False)
	updated_at     = models.DateTimeField()

	# Relationships
	item = models.ForeignKey(Item, related_name='listings', on_delete=models.CASCADE)
	world = models.ForeignKey(World, related_name='listings', on_delete=models.CASCADE)

	class Meta:
		indexes = [
			models.Index(fields=['listing_guid']),
			models.Index(fields=['item_id']),
			models.Index(fields=['created_at']),
		]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} from {self.retainer_name}'

	def summary(self):
		return {
			'id': self.id,
			'world': self.world.name,
			'guid': self.listing_guid,
			'retainer_guid': self.retainer_guid,
			'retainer_name': self.retainer_name,
			'price_per_unit': self.price_per_unit,
			'quantity': self.quantity,
			'total': self.total,
			'created_at': self.created_at
		}


class WorldItemFact(models.Model):
	nq_sold_mean      = models.FloatField(null=True)
	nq_sold_median    = models.FloatField(null=True)
	nq_sold_mode      = models.FloatField(null=True)
	nq_sold_high      = models.IntegerField(null=True)
	nq_sold_low       = models.IntegerField(null=True)
	nq_sold_count     = models.IntegerField(null=True)
	nq_sellers_count  = models.IntegerField(null=True)
	nq_list_mean   = models.FloatField(null=True)
	nq_list_median = models.FloatField(null=True)
	nq_list_mode   = models.FloatField(null=True)
	nq_list_high   = models.IntegerField(null=True)
	nq_list_low    = models.IntegerField(null=True)
	nq_list_count  = models.IntegerField(null=True)

	hq_last_sold_value = models.IntegerField(null=True)
	nq_last_sold_value = models.IntegerField(null=True)

	hq_sold_mean      = models.FloatField(null=True)
	hq_sold_median    = models.FloatField(null=True)
	hq_sold_mode      = models.FloatField(null=True)
	hq_sold_high      = models.IntegerField(null=True)
	hq_sold_low       = models.IntegerField(null=True)
	hq_sold_count     = models.IntegerField(null=True)
	hq_sellers_count  = models.IntegerField(null=True)
	hq_list_mean   = models.FloatField(null=True)
	hq_list_median = models.FloatField(null=True)
	hq_list_mode   = models.FloatField(null=True)
	hq_list_high   = models.IntegerField(null=True)
	hq_list_low    = models.IntegerField(null=True)
	hq_list_count  = models.IntegerField(null=True)

	calculated_at = models.DateTimeField(null=True)

	# Relationships
	item = models.ForeignKey(Item, related_name='facts', on_delete=models.CASCADE)
	world = models.ForeignKey(World, related_name='facts', on_delete=models.CASCADE)


	def __str__(self):
		return f'({self.id}) {self.nq_list_count} {self.hq_list_count} {self.hq_sold_count} {self.nq_sold_count}'



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
	price_per_unit = models.IntegerField()
	quantity       = models.IntegerField()
	buyer_name     = models.TextField()
	sold_at        = models.DateTimeField()
	hq             = models.BooleanField(default=False)
	updated_at     = models.DateTimeField()
	created_at     = models.DateTimeField(auto_now_add=True)

	# Relationships
	item = models.ForeignKey(Item, related_name='sales', on_delete=models.CASCADE)
	world = models.ForeignKey(World, related_name='sales', on_delete=models.CASCADE)


	class Meta:
		indexes = [
			models.Index(fields=['sold_at', 'buyer_name']),
			models.Index(fields=['item_id']),
			models.Index(fields=['sold_at']),			
		]

	def __str__(self):
		return f'({self.id}) {self.price_per_unit}x{self.quantity} by {self.buyer_name}'

	def summary(self):
		return {
			'id': self.id,		
			'world': self.world.name,
			'price_per_unit': self.price_per_unit,
			'quantity': self.quantity,
			'buyer_name': self.buyer_name,
			'sold_at': self.sold_at
		}

