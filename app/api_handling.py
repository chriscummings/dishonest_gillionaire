import json
import os
from glob import glob
import shutil
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from ratelimit import limits, RateLimitException, sleep_and_retry
from app.utils import fetch_json, captute_runtime
from app.models import *
import logging


class Universalis():
	# FIXME: hard-coded north america
	API_ENDPOINT = "http://universalis.app/api/v2/"
	UNIVERSALIS_MAX_CALLS_PER_SECOND = 13 # 25 max
	UNIVERSALIS_MAX_CONNECTIONS = 6 # 8 max
	LISTINGS_PER_API_CALL = 100 # Universalis no max.
	ITEMS_PER_API_CALL = 100 # Universalis 100 max
	HOURS_AGO_TO_UPDATE = 0
	MAX_SALES_PER_ITEM = 20 # How many historic sales to ask for

	def __init__(self):
		self.logger = logging.getLogger(__name__)

	def fetch_and_flag_market_updates(self):
		api_resp = fetch_json(self.API_ENDPOINT+"extra/stats/recently-updated")

		for item_id in api_resp['items']:
			item = Item.objects.get(guid=item_id)
			item.market_updated_at = datetime.now()
			item.save()

	@sleep_and_retry
	@limits(calls=UNIVERSALIS_MAX_CALLS_PER_SECOND, period=1)
	def fetch_and_process_item_sales(self, item_ids_querystring, json_file=None):
		"""
		json_file - used for testing 
		"""

		new_sale_count = 0

		if json_file:
			f = open(json_file)
			api_resp = json.load(f)
		else:
			# FIXME: hard-coded north america
			api_resp = fetch_json(self.API_ENDPOINT+"history/North-America/"+item_ids_querystring+"?entriesToReturn="+str(self.MAX_SALES_PER_ITEM))

		# Handle items unknown by Universalis..
		for item_id in api_resp['unresolvedItems']:
			Item.flag_universalis_unresolved(item_id)

		for key in api_resp['items'].keys():
			item_id = key

			print("Processing item "+str(item_id))

			sales_json = api_resp['items'][key]['entries']

			item = Item.objects.get(guid=item_id)

			new_sales = []

			for s in sales_json:
				sale = Sale.objects.filter(sold_at=datetime.utcfromtimestamp(s['timestamp']), buyer_name=s['buyerName']).last()

				# Ignore existing sales.
				if sale:
					sale.updated_at = datetime.now()
					sale.save()
					continue

				world = World.objects.get(name=s['worldName'])

				sale                = Sale()
				sale.item           = item
				sale.price_per_unit = s['pricePerUnit']
				sale.quantity       = s['quantity']
				sale.buyer_name     = s['buyerName']
				sale.sold_at        = datetime.fromtimestamp(s['timestamp'], timezone.utc)
				sale.world          = world
				sale.datacenter     = world.data_center
				sale.updated_at = datetime.now()

				if s['hq']:
					sale.hq = True

				new_sales.append(sale)

			new_sale_count += len(new_sales)

			Sale.objects.bulk_create(new_sales)

			item.northamerica_sales_updated_at = datetime.now(tz=timezone.utc)
			item.save()

		self.logger.info(f"Created {new_sale_count} new Sales.")

	@captute_runtime
	def fetch_sales(self, get_all=False):
		start_time = datetime.now()

		print("Building list..")

		if get_all:
			items = Item.objects.filter( 
				Q(northamerica_sales_updated_at__lt=(datetime.now(tz=timezone.utc) - timedelta(hours = self.HOURS_AGO_TO_UPDATE))) | 
				Q(northamerica_sales_updated_at__isnull=True), Q(universalis_unresolved=False), Q(is_marketable=True) ).order_by('guid')
		else:
			# FIXME: write query
			items = None


		paginator = Paginator(items, self.ITEMS_PER_API_CALL)

		# Build a list of URL querystrings that are comma-separated item IDs.
		item_query_strings = []
		for page_number in paginator.page_range:
			item_id_list = []

			# TODO: make this block better...
			page = paginator.page(page_number)
			for obj in page.object_list:
				item_id_list.append(obj.guid)

			# TODO: make this block better...
			item_id_string = ""
			for item_id in item_id_list:
				item_id_string = item_id_string+","+str(item_id)

			item_query_strings.append(item_id_string)

		self.logger.info("List complete. "+str(items.count())+" items to handle in "+str(len(item_query_strings))+" batches.")

		if items.count() > 0:
			with PoolExecutor(max_workers=self.UNIVERSALIS_MAX_CONNECTIONS) as executor:
				for _ in executor.map(self.fetch_and_process_item_sales, item_query_strings):
					pass 

		print(datetime.now() - start_time)

	@sleep_and_retry
	@limits(calls=UNIVERSALIS_MAX_CALLS_PER_SECOND, period=1)
	def fetch_and_process_item_listings(self, item_ids_querystring, json_file=None):
		"""
		json_file - used for testing 
		"""

		if json_file:
			f = open(json_file)
			api_resp = json.load(f)
		else:
			api_resp = fetch_json(self.API_ENDPOINT+"North-America/"+item_ids_querystring+"?listings="+str(self.LISTINGS_PER_API_CALL)+"&noGst=1")

		# Handle items unknown by Universalis..

		if 'unresolvedItems' in api_resp.keys():
			for item_id in api_resp['unresolvedItems']:
				Item.flag_universalis_unresolved(item_id)

		for key in api_resp['items'].keys():
			item_id = key
			print("Processing item "+str(item_id))

			listings_json = api_resp['items'][key]['listings']

			# Get the item this recipe creates.
			item = Item.objects.get(guid=item_id)

			#FIXME: handle/log this...
			if not item: raise "OH SNAP, ITEM "+str(item_guid)+" NOT FOUND"

			new_listings = []

			for l in listings_json:
				listing = Listing.objects.filter(listing_guid=l['listingID']).last()

				# Ignore existing listing.
				if listing: 
					listing.updated_at = datetime.now()
					listing.save()
					continue

				world = World.objects.get(name=l['worldName'])

				listing                = Listing()
				listing.item           = item
				listing.listing_guid   = l['listingID']
				listing.retainer_guid  = l['retainerID']
				listing.retainer_name  = l['retainerName']
				listing.price_per_unit = l['pricePerUnit']
				listing.quantity       = l['quantity']
				listing.total          = l['total']
				listing.world          = world
				listing.datacenter     = world.data_center

				if l['hq']:
					listing.hq = True

				listing.updated_at = datetime.now()

				new_listings.append(listing)

			Listing.objects.bulk_create(new_listings)
			item.northamerica_listings_updated_at = datetime.now(tz=timezone.utc)
			item.save()

	# TODO: add "all" argument (bool) and conditionally change the items queryset.
	@captute_runtime
	def fetch_listings(self, get_all=False):
		start_time = datetime.now()

		print("Building list..")

		# All or those with "updated flag"

		if get_all:
			items = Item.objects.filter( 
				Q(northamerica_listings_updated_at__lt=(datetime.now(tz=timezone.utc) - timedelta(hours = self.HOURS_AGO_TO_UPDATE))) | 
				Q(northamerica_listings_updated_at__isnull=True), Q(universalis_unresolved=False), Q(is_marketable=True) ).order_by('guid')
		else:
			# FIXME: write query
			items = None

		# Universalis API has a 100 items limit.
		paginator = Paginator(items, 100)

		# Build a list of URL querystrings that are comma-separated item IDs.
		item_query_strings = []
		for page_number in paginator.page_range:
			item_id_list = []

			# TODO: make this block better...
			page = paginator.page(page_number)
			for obj in page.object_list:
				item_id_list.append(obj.guid)

			# TODO: make this block better...
			item_id_string = ""
			for item_id in item_id_list:
				item_id_string = item_id_string+","+str(item_id)

			item_query_strings.append(item_id_string)

		print("List complete. "+str(items.count())+" items to handle in "+str(len(item_query_strings))+" batches.")

		if items.count() > 0:
			with PoolExecutor(max_workers=self.UNIVERSALIS_MAX_CONNECTIONS) as executor:
				for _ in executor.map(self.fetch_and_process_item_listings, item_query_strings):
					pass 

		print(datetime.now() - start_time)


class XivApi():
	MAX_CONNECTIONS = 4 # Actual limit unknown
	XIPAPI_MAX_CALLS_PER_SECOND = 15 # 20 max

	# Items
	ITEM_ENDPOINT = 'https://xivapi.com/item'
	ITEM_LIST_TEMP_DIR = 'data/items'
	ITEM_DETAILS_TEMP_DIR = 'data/item_details'

	# Recipes
	RECIPE_ENDPOINT = 'https://xivapi.com/recipe'
	RECIPE_LIST_TEMP_DIR = 'data/recipes'
	RECIPE_DETAILS_TEMP_DIR = 'data/recipe_details'

	def __init__(self):
		self.api_key =  getattr(settings, 'XIVAPI_KEY', None)
		self.logger = logging.getLogger(__name__)

	@sleep_and_retry
	@limits(calls=XIPAPI_MAX_CALLS_PER_SECOND, period=1)
	def _fetch_and_store_items_page(self, page_number):
		endpoint = f"{self.ITEM_ENDPOINT}?private_key={self.api_key}"

		api_resp = fetch_json(endpoint+"&page="+str(page_number))

		results = api_resp["Results"]

		with open(os.path.join(self.ITEM_LIST_TEMP_DIR, f"{page_number}.json"), "w") as json_file:
			json_file.write(json.dumps(results, indent=4))

	@captute_runtime
	def fetch_item_list(self, start_page=1):
		# Clean out old data
		if os.path.exists(self.ITEM_LIST_TEMP_DIR):
			shutil.rmtree(self.ITEM_LIST_TEMP_DIR)

		# Create temp dir for JSON
		os.makedirs(self.ITEM_LIST_TEMP_DIR)

		# Get initial page to determine total page count.
		endpoint = f"{self.ITEM_ENDPOINT}?private_key={self.api_key}"
		api_resp = fetch_json(endpoint)
		last_page = api_resp["Pagination"]["PageTotal"]

		with PoolExecutor(max_workers=self.MAX_CONNECTIONS) as executor:
			for _ in executor.map(self._fetch_and_store_items_page, range(start_page, last_page)):
				pass 

	@sleep_and_retry
	@limits(calls=XIPAPI_MAX_CALLS_PER_SECOND, period=1)
	def _fetch_and_store_item_details_page(self, id):
		endpoint = f"{self.ITEM_ENDPOINT}/{id}?private_key={self.api_key}"

		api_resp = fetch_json(endpoint)

		with open(os.path.join(self.ITEM_DETAILS_TEMP_DIR, f"{id}.json"), "w") as json_file:
			json_file.write(json.dumps(api_resp, indent=4))

	@captute_runtime
	def fetch_item_details(self, recovery_mode=False):
		if not recovery_mode:
			# Clean out old data
			if os.path.exists(self.ITEM_DETAILS_TEMP_DIR):
				shutil.rmtree(self.ITEM_DETAILS_TEMP_DIR)

			# Create temp dir for JSON
			os.makedirs(self.ITEM_DETAILS_TEMP_DIR)

		# Grab all item IDs from every JSON file.
		ids = []
		item_json_files = glob(f"{self.ITEM_LIST_TEMP_DIR}/*.json")
		for json_file in item_json_files:
			f = open(json_file)
			data = json.load(f)
			ids += map(lambda item_json: item_json["ID"], data)

		# Remove None items
		ids = [x for x in ids if x is not None]

		if recovery_mode:
			existing_ids = []
			item_details_json_files = glob(f"{self.ITEM_DETAILS_TEMP_DIR}/*.json")
			for json_file in item_details_json_files:
				f = open(json_file)
				data = json.load(f)
				existing_ids.append(data["ID"])

			for id in existing_ids:
				if id in ids:
					ids.remove(id)

		with PoolExecutor(max_workers=self.MAX_CONNECTIONS) as executor:
			for _ in executor.map(self._fetch_and_store_item_details_page, ids):
				pass 

	@sleep_and_retry
	@limits(calls=XIPAPI_MAX_CALLS_PER_SECOND, period=1)
	def _fetch_and_store_recipes_page(self, page_number):
		endpoint = f"{self.RECIPE_ENDPOINT}?private_key={self.api_key}"

		api_resp = fetch_json(endpoint+"&page="+str(page_number))
		results = api_resp["Results"]

		with open(os.path.join(self.RECIPE_LIST_TEMP_DIR, f"{page_number}.json"), "w") as json_file:
			json_file.write(json.dumps(results, indent=4))

	@sleep_and_retry
	@limits(calls=XIPAPI_MAX_CALLS_PER_SECOND, period=1)
	def _fetch_and_store_recipe_details_page(self, id):
		endpoint = f"{self.RECIPE_ENDPOINT}/{id}?private_key={self.api_key}"

		api_resp = fetch_json(endpoint)

		with open(os.path.join(self.RECIPE_DETAILS_TEMP_DIR, f"{id}.json"), "w") as json_file:
			json_file.write(json.dumps(api_resp, indent=4))

	@captute_runtime
	def fetch_recipe_list(self, start_page=1):
		# Clean out old data
		if os.path.exists(self.RECIPE_LIST_TEMP_DIR):
			shutil.rmtree(self.RECIPE_LIST_TEMP_DIR)

		# Create temp dir for JSON
		os.makedirs(self.RECIPE_LIST_TEMP_DIR)

		# Get initial page to determine total page count.
		endpoint = f"{self.RECIPE_ENDPOINT}?private_key={self.api_key}"
		api_resp = fetch_json(endpoint)
		last_page = api_resp["Pagination"]["PageTotal"]

		with PoolExecutor(max_workers=self.MAX_CONNECTIONS) as executor:
			for _ in executor.map(self._fetch_and_store_recipes_page, range(start_page, last_page)):
				pass 

		##########


		# with open(self.RECIPE_LIST_OUTPUT_FILE, "w") as json_file:
		# 	json_file.write(json.dumps(recipes, indent=4))

	@captute_runtime
	def fetch_recipe_details(self, recovery_mode=False):

		if not recovery_mode:
			# Clean out old data
			if os.path.exists(self.RECIPE_DETAILS_TEMP_DIR):
				shutil.rmtree(self.RECIPE_DETAILS_TEMP_DIR)

			# Create temp dir for JSON
			os.makedirs(self.RECIPE_DETAILS_TEMP_DIR)

		# Grab all item IDs from every JSON file.
		ids = []
		item_json_files = glob(f"{self.RECIPE_LIST_TEMP_DIR}/*.json")
		for json_file in item_json_files:
			f = open(json_file)
			data = json.load(f)
			ids += map(lambda recipe_json: recipe_json["ID"], data)
		
		# Remove None items
		ids = [x for x in ids if x is not None]

		if recovery_mode:
			existing_ids = []
			recipe_details_json_files = glob(f"{self.RECIPE_DETAILS_TEMP_DIR}/*.json")
			for json_file in recipe_details_json_files:
				f = open(json_file)
				data = json.load(f)
				existing_ids.append(data["ID"])

			for id in existing_ids:
				if id in ids:
					ids.remove(id)

		with PoolExecutor(max_workers=self.MAX_CONNECTIONS) as executor:
			for _ in executor.map(self._fetch_and_store_recipe_details_page, ids):
				pass 

	@captute_runtime
	def ingest_item_details(self, src_dir=None):

		if src_dir:
			json_files = glob(f"{src_dir}/*.json")
		else:
			json_files = glob(f"{self.ITEM_DETAILS_TEMP_DIR}/*.json")
	
		for f in json_files:
			i = json.load(open(f))

			# Ignore bs items
			if i['Name'] == '' or i['Name'] == 'Other':
				continue

			try:
				item = Item.objects.get(guid=i['ID'])
			except Item.DoesNotExist:
				item = Item()
				item.guid          = i['ID']

			item.name          = i['Name'].lower()
			item.display_name  = i['Name']
			item.icon          = i['Icon']
			item.item_level    = i['LevelItem']
			item.equip_level   = i['LevelEquip']
			item.can_be_hq     = True if i['CanBeHq'] == 1 else False
			item.stack_size    = i['StackSize']
			item.vendor_price  = i['PriceLow']

			if i['ClassJobCategory']:
				item.jobs = i['ClassJobCategory']['Name']

			if i['ItemUICategory']:
				item.ui_category   = i['ItemUICategory']['Name']

			if i['ItemSearchCategory']:
				item.search_category = i['ItemSearchCategory']['Name']
				item.is_marketable = True

			item.is_dyeable    = True if i['CanBeHq'] == 1 else False
			item.is_glamourous = True if i['CanBeHq'] == 1 else False
			item.is_untradable = True if i['CanBeHq'] == 1 else False
			item.is_unique     = True if i['CanBeHq'] == 1 else False

			item.save()

			print(item)

	def _create_ingredient(self, recipe, item, count):
		ingredient = Ingredient()
		ingredient.count = count
		ingredient.item = item
		ingredient.recipe = recipe
		ingredient.save()

	@captute_runtime
	def ingest_recipe_details(self, src_dir=None):

		if src_dir:
			json_files = glob(f"{src_dir}/*.json")
		else:
			json_files = glob(f"{self.RECIPE_DETAILS_TEMP_DIR}/*.json")

		for f in json_files:
			r = json.load(open(f))

			try:
				recipe = Recipe.objects.get(guid=r['ID'])
			except Recipe.DoesNotExist as e:

				# Ignore old/invalid recipes.
				if r['AmountResult'] == 0: continue
				if not r['ItemResult']: continue

				# Get the item this recipe creates.
				item = Item.objects.get(guid=r['ItemResult']['ID'])

				# FIXME: handle this.
				if not item:
					raise "OH SNAP, ITEM "+str(item_guid)+" NOT FOUND"

				recipe               = Recipe()
				recipe.name          = r['Name']
				recipe.icon          = r['ItemResult']['Icon']
				recipe.guid          = r['ID']
				recipe.level 		 = r['RecipeLevelTable']['ClassJobLevel']
				recipe.profession    = r['ClassJob']['Name']
				recipe.item          = item
				recipe.result_amount = r['AmountResult']
				recipe.save()

				print(recipe)

				# There are 10 (0-9) recipe ingredients max. There are always "static" keys for each of the 10 possible ingredients.
				for i in range(0,10):
					if r['AmountIngredient'+str(i)] > 0:
						count     = r['AmountIngredient'+str(i)]
						item_guid = r['ItemIngredient'+str(i)]['ID']

						try:
							item = Item.objects.get(guid=item_guid)
							self._create_ingredient(recipe, item, count)
						except Item.DoesNotExist as e:
							print(e)
							print(item_guid)
