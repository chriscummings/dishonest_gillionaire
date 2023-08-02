from app.models import *
from app.utils import captute_runtime
from datetime import datetime, timedelta
import statistics
from pprint import pprint as p
import json

HOURS_AGO_TO_UPDATE = 24 # !!!!!!!!!!!!!!!!!!!!!!!!!!!

def _to_world_dict(collection):
	'''Organizes objects by world name.
	'''
	world_dict = {}
	for obj in collection:
		world = obj.world
		if world.name not in world_dict.keys():
			world_dict[world.name] = []
		world_dict[world.name].append(obj)
	return world_dict

def _compute_listings_facts(collection):

	# should sellers counts be a set? This does list the unique sellers count but not the listings count...

	hq_listings = []
	hq_sellers = set()
	nq_listings = []
	nq_sellers = set()

	for listing in collection:
		if listing.hq:
			hq_listings.append(listing.price_per_unit)
			hq_sellers.add(listing.retainer_guid)
		else:
			nq_listings.append(listing.price_per_unit)
			nq_sellers.add(listing.retainer_guid)

	listings_fact = {
		# NQ
		'nq_list_mean': None,
		'nq_list_median': None,
		'nq_list_mode': None,
		'nq_list_high': None,
		'nq_list_low': None,
		'nq_list_count': None,
		'nq_sellers_count': None,
		# HQ
		'hq_list_mean': None,
		'hq_list_median': None,
		'hq_list_mode': None,
		'hq_list_high': None,
		'hq_list_low': None,
		'hq_list_count': None,
		'hq_sellers_count': None,
	}

	if hq_listings:
		listings_fact['hq_list_mean'] = statistics.mean(hq_listings)
		listings_fact['hq_list_median'] = statistics.median(hq_listings)
		listings_fact['hq_list_mode'] = min(statistics.multimode(hq_listings))
		listings_fact['hq_list_high'] = max(hq_listings)
		listings_fact['hq_list_low'] = min(hq_listings)
		listings_fact['hq_list_count'] = len(hq_listings)
		listings_fact['hq_sellers_count'] = len(hq_sellers)

	if nq_listings:
		listings_fact['nq_list_mean'] = statistics.mean(nq_listings)
		listings_fact['nq_list_median'] = statistics.median(nq_listings)
		listings_fact['nq_list_mode'] = min(statistics.multimode(nq_listings))
		listings_fact['nq_list_high'] = max(nq_listings)
		listings_fact['nq_list_low'] = min(nq_listings)
		listings_fact['nq_list_count'] = len(nq_listings)
		listings_fact['nq_sellers_count'] = len(nq_sellers)

	return listings_fact

def _compute_sales_facts(collection):
	hq_sales = []
	nq_sales = []

	# TODO: get last sold price for hq and nq, sort and then just grab last items form hq&nq_sales lists.
	collection.sort(key=lambda x: x.sold_at)

	# Seperate HQ & NQ
	for sale in collection:
		if sale.hq:
			hq_sales.append(sale.price_per_unit)
		else:
			nq_sales.append(sale.price_per_unit)

	sales_fact = {
		# NQ
		'nq_sold_mean': None,
		'nq_sold_median': None,
		'nq_sold_mode': None,
		'nq_sold_high': None,
		'nq_sold_low': None,
		'nq_sold_count': None,
		'nq_last_sold_value': None,
		# HQ
		'hq_sold_mean': None,
		'hq_sold_median': None,
		'hq_sold_mode': None,
		'hq_sold_high': None,
		'hq_sold_low': None,
		'hq_sold_count': None,
		'hq_last_sold_value': None,			
	}

	if hq_sales:
		sales_fact['hq_sold_mean'] = statistics.mean(hq_sales)
		sales_fact['hq_sold_median'] = statistics.median(hq_sales)
		sales_fact['hq_sold_mode'] = max(statistics.multimode(hq_sales))
		sales_fact['hq_sold_high'] = max(hq_sales)
		sales_fact['hq_sold_low'] = min(hq_sales)
		sales_fact['hq_sold_count'] = len(hq_sales)
		sales_fact['hq_last_sold_value'] = hq_sales[-1]

	if nq_sales:
		sales_fact['nq_sold_mean'] = statistics.mean(nq_sales)
		sales_fact['nq_sold_median'] = statistics.median(nq_sales)
		sales_fact['nq_sold_mode'] = max(statistics.multimode(nq_sales))
		sales_fact['nq_sold_high'] = max(nq_sales)
		sales_fact['nq_sold_low'] = min(nq_sales)
		sales_fact['nq_sold_count'] = len(nq_sales)
		sales_fact['nq_last_sold_value'] = nq_sales[-1]

	return sales_fact

def _generate_item_market_stats(item, sales, listings):
	"""
	"""
	new_facts = []

	sales_by_world = _to_world_dict(sales)
	listings_by_world = _to_world_dict(listings)

	for world in World.objects.all():
		fact = WorldItemFact(calculated_at=datetime.now())

		if world.name in sales_by_world.keys():
			sales_facts = _compute_sales_facts(sales_by_world[world.name])

			# NQ
			fact.nq_sold_mean = sales_facts['nq_sold_mean']
			fact.nq_sold_median = sales_facts['nq_sold_median']
			fact.nq_sold_mode = sales_facts['nq_sold_mode']
			fact.nq_sold_high = sales_facts['nq_sold_high']
			fact.nq_sold_low = sales_facts['nq_sold_low']
			fact.nq_sold_count = sales_facts['nq_sold_count']
			fact.nq_last_sold_value = sales_facts['nq_last_sold_value']

			# HQ
			fact.hq_sold_mean = sales_facts['hq_sold_mean']
			fact.hq_sold_median = sales_facts['hq_sold_median']
			fact.hq_sold_mode = sales_facts['hq_sold_mode']
			fact.hq_sold_high = sales_facts['hq_sold_high']
			fact.hq_sold_low = sales_facts['hq_sold_low']
			fact.hq_sold_count = sales_facts['hq_sold_count']
			fact.hq_last_sold_value = sales_facts['hq_last_sold_value']

		if world.name in listings_by_world.keys():
			listings_facts = _compute_listings_facts(listings_by_world[world.name])

			# NQ
			fact.nq_list_mean = listings_facts['nq_list_mean']
			fact.nq_list_median = listings_facts['nq_list_median']
			fact.nq_list_mode = listings_facts['nq_list_mode']
			fact.nq_list_high = listings_facts['nq_list_high']
			fact.nq_list_low = listings_facts['nq_list_low'] #
			fact.nq_list_count = listings_facts['nq_list_count'] #
			fact.nq_sellers_count = listings_facts['nq_sellers_count']
			# HQ
			fact.hq_list_mean = listings_facts['hq_list_mean']
			fact.hq_list_median = listings_facts['hq_list_median']
			fact.hq_list_mode = listings_facts['hq_list_mode']
			fact.hq_list_high = listings_facts['hq_list_high']
			fact.hq_list_low = listings_facts['hq_list_low'] #
			fact.hq_list_count = listings_facts['hq_list_count'] #
			fact.hq_sellers_count = listings_facts['hq_sellers_count']

		fact.item = item
		fact.world = world
		fact.datacenter = world.data_center

		fact.save()
		new_facts.append(fact)

	return new_facts

@captute_runtime
def summarize_market_stats():

	for item in Item.objects.filter(is_marketable=True):

		# Get recent related sales & listings & sort by world
		hours_ago = datetime.now() - timedelta(hours = HOURS_AGO_TO_UPDATE)

		sales = Sale.objects.filter(updated_at__gte=hours_ago, item_id=item.id)
		listings = Listing.objects.filter(updated_at__gte=hours_ago, item_id=item.id)

		new_facts = _generate_item_market_stats(item, sales, listings)

		##
		# Best NQ price in region (homeworld doesn't matter)
		best_regional_nq_price = None
		best_regional_nq_world = None
		f = list(filter(lambda x: x.nq_list_low, new_facts))
		nq_l = sorted(f, key=lambda x: x.nq_list_low)
		if nq_l:
			best_nq_pricing = nq_l[0]
			best_regional_nq_price = best_nq_pricing.nq_list_low
			best_regional_nq_world = best_nq_pricing.world

		##
		# Best HQ price in region (homeworld doesn't matter)
		best_regional_hq_price = None
		best_regional_hq_world = None	
		f = list(filter(lambda x: x.hq_list_low, new_facts))
		hq_l = sorted(f, key=lambda x: x.hq_list_low)
		if hq_l:
			best_hq_pricing = hq_l[0]
			best_regional_hq_price = best_hq_pricing.hq_list_low
			best_regional_hq_world = best_hq_pricing.world

		##
		# Handle home-world-dependent numbers
		for home_world in World.objects.all():

			datacenter = home_world.data_center
			dc_worlds = list(filter(lambda fact: fact.datacenter == datacenter, new_facts))

			##
			# Best NQ price in DC
			best_nq_listing_in_dc_price = None
			best_nq_listing_in_dc_world = None
			nq_dc_worlds = list(filter(lambda x: x.nq_list_low, dc_worlds))
			nq_l = sorted(nq_dc_worlds, key=lambda x: x.nq_list_low)
			if nq_l:
				best_nq_pricing = nq_l[0]
				best_nq_listing_in_dc_price = best_nq_pricing.nq_list_low
				best_nq_listing_in_dc_world = best_nq_pricing.world

			##
			# Best HQ price in DC
			best_hq_listing_in_dc_price = None
			best_hq_listing_in_dc_world = None
			hq_dc_worlds = list(filter(lambda x: x.hq_list_low, dc_worlds))
			hq_l = sorted(hq_dc_worlds, key=lambda x: x.hq_list_low)
			if hq_l:
				best_hq_pricing = hq_l[0]
				best_hq_listing_in_dc_price = best_hq_pricing.hq_list_low
				best_hq_listing_in_dc_world = best_hq_pricing.world

			# what if none??
			homeworld_fact = list(filter(lambda x: x.world == home_world, new_facts))[0]

			##
			# Best NQ price on homeworld
			best_home_nq_price = homeworld_fact.nq_list_low

			##
			# Best HQ price on homeworld
			best_home_hq_price = homeworld_fact.hq_list_low




			# generate BestPurchasePricing -------------------------------
			best_purchase_pricing = BestPurchasePricing()
			best_purchase_pricing.item = item
			best_purchase_pricing.home = home_world
			best_purchase_pricing.datacenter = home_world.data_center
			best_purchase_pricing.region = home_world.data_center.region

			# home competition
			best_purchase_pricing.home_nq_sold_mean = homeworld_fact.nq_sold_mean
			best_purchase_pricing.home_nq_sold_median = homeworld_fact.nq_sold_median
			best_purchase_pricing.home_nq_sold_mode =  homeworld_fact.nq_sold_mode
			best_purchase_pricing.home_nq_sold_high = homeworld_fact.nq_sold_high
			best_purchase_pricing.home_nq_sold_low = homeworld_fact.nq_sold_low
			best_purchase_pricing.home_nq_sold_count = homeworld_fact.nq_sold_count
			best_purchase_pricing.home_nq_sellers_count = homeworld_fact.nq_sellers_count
			best_purchase_pricing.home_hq_sold_mean = homeworld_fact.hq_sold_mean
			best_purchase_pricing.home_hq_sold_median = homeworld_fact.hq_sold_median
			best_purchase_pricing.home_hq_sold_mode = homeworld_fact.hq_sold_mode
			best_purchase_pricing.home_hq_sold_high = homeworld_fact.hq_sold_high
			best_purchase_pricing.home_hq_sold_low = homeworld_fact.hq_sold_low
			best_purchase_pricing.home_hq_sold_count = homeworld_fact.hq_sold_count
			best_purchase_pricing.home_hq_sellers_count = homeworld_fact.hq_sellers_count

			# home availability
			best_purchase_pricing.home_nq_list_mean = homeworld_fact.nq_list_mean
			best_purchase_pricing.home_nq_list_median = homeworld_fact.nq_list_median
			best_purchase_pricing.home_nq_list_mode = homeworld_fact.nq_list_mode
			best_purchase_pricing.home_nq_list_high = homeworld_fact.nq_list_high
			best_purchase_pricing.home_nq_list_low = homeworld_fact.nq_list_low
			best_purchase_pricing.home_nq_list_count = homeworld_fact.nq_list_count
			best_purchase_pricing.home_hq_list_mean = homeworld_fact.hq_list_mean
			best_purchase_pricing.home_hq_list_median = homeworld_fact.hq_list_mean
			best_purchase_pricing.home_hq_list_mode = homeworld_fact.hq_list_mean
			best_purchase_pricing.home_hq_list_high = homeworld_fact.hq_list_mean
			best_purchase_pricing.home_hq_list_low = homeworld_fact.hq_list_low
			best_purchase_pricing.home_hq_list_count = homeworld_fact.hq_list_count

			# remote availability
			best_purchase_pricing.best_nq_listing_in_region_price = best_regional_nq_price
			best_purchase_pricing.best_nq_listing_in_region_world = best_regional_nq_world

			best_purchase_pricing.best_hq_listing_in_region_price = best_regional_hq_price
			best_purchase_pricing.best_hq_listing_in_region_world = best_regional_hq_world

			best_purchase_pricing.best_nq_listing_in_datacenter_price = best_nq_listing_in_dc_price
			best_purchase_pricing.best_nq_listing_in_datacenter_world = best_nq_listing_in_dc_world

			best_purchase_pricing.best_hq_listing_in_datacenter_price = best_hq_listing_in_dc_price
			best_purchase_pricing.best_hq_listing_in_datacenter_world = best_hq_listing_in_dc_world

			best_purchase_pricing.save()

def _create_to_buy_json(objs):
	return json.dumps(objs)



@captute_runtime
def derive_to_craft_pricing():

	source_template = {
		'count': 0,       # Redundantly in every dict but useful
		'item_name': '',  # Redundantly in every dict but useful
		'item_guid': '',  # Redundantly in every dict but useful
		'world': '',
		'datacenter': '',
		'region':'na',
		'price_per':0,
		'quality':''
	}

	for recipe in Recipe.objects.all().order_by('level'):
		material_sources = {}

		for ingredient in recipe.ingredients.all():
			count = ingredient.count
			item = ingredient.item

			# Create source 'entry' for ingredient
			if item.guid not in material_sources.keys():
				material_sources[item.guid] = {
					'sources': []
				} # should just be a list?

			for world in World.objects.all():
				fact = WorldItemFact.objects.filter(item_id=item, world=world).last()

				if not fact:
					# FIXME: handle this..
					print(f"not found {item}")
					continue

				if fact.nq_list_count:
					src = source_template.copy()
					src['count'] = count
					src['item_name'] = item.name
					src['item_guid'] = item.guid
					src['world'] = world.name
					src['datacenter'] = world.data_center.name
					src['price_per'] = fact.nq_list_low
					src['quality'] = 'nq'
					material_sources[item.guid]['sources'].append(src)

				if fact.hq_list_count:
					src = source_template.copy()
					src['count'] = count
					src['item_name'] = item.name
					src['item_guid'] = item.guid
					src['world'] = world.name
					src['datacenter'] = world.data_center.name
					src['price_per'] = fact.hq_list_low
					src['quality'] = 'hq'
					material_sources[item.guid]['sources'].append(src)

		for world in World.objects.all():
			nq_home_list = {'partial':False, 'materials':[]}
			nq_dc_list = {'partial':False, 'materials':[]}
			nq_reg_list = {'partial':False, 'materials':[]}

			hq_home_list = {'partial':False, 'materials':[]}
			hq_dc_list = {'partial':False, 'materials':[]}
			hq_reg_list = {'partial':False, 'materials':[]}

			datacenter = world.data_center
			region = datacenter.region

			for item_guid in material_sources.keys():
				sources = material_sources[item_guid]['sources']

				nq = list(filter(lambda x: x['quality']=='nq', sources))

				# NQ on Homeworld
				x = list(filter(lambda x: x['world']==world.name, nq))
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					nq_home_list['partial'] = True
				else:
					nq_home_list['materials'].append(s[0])

				# NQ on DC
				x = list(filter(lambda x: x['datacenter']==datacenter.name, nq))
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					nq_dc_list['partial'] = True
				else:
					nq_dc_list['materials'].append(s[0])

				# NQ on Region
				x = list(filter(lambda x: x['region']=='na', nq)) # FIXME: hardcorded region name
		
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					nq_reg_list['partial'] = True
				else:
					nq_reg_list['materials'].append(s[0])

				hq = list(filter(lambda x: x['quality']=='hq', sources))

				# HQ, Homeworld
				x = list(filter(lambda x: x['world']==world.name, hq))
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					hq_home_list['partial'] = True
				else:
					hq_home_list['materials'].append(s[0])

				# HQ, DC
				x = list(filter(lambda x: x['datacenter']==datacenter.name, hq))
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					hq_dc_list['partial'] = True
				else:
					hq_dc_list['materials'].append(s[0])

				# HQ, Region
				x = list(filter(lambda x: x['region']=='na', hq)) # FIXME: hardcorded region name
			
				s = sorted(x, key=lambda x: x['price_per'])
				if len(s) == 0:
					hq_reg_list['partial'] = True
				else:
					hq_reg_list['materials'].append(s[0])

			# NQ
			craftlist = CraftList()
			craftlist.item = item
			craftlist.recipe = recipe
			craftlist.homeworld = world
			craftlist.quality = 'nq'
			craftlist.home_price = sum(item['price_per']*item['count'] for item in nq_home_list['materials'])
			craftlist.home_price_partial = nq_home_list['partial']
			craftlist.dc_price = sum(item['price_per']*item['count'] for item in nq_dc_list['materials'])
			craftlist.dc_price_partial = nq_dc_list['partial']
			craftlist.reg_price = sum(item['price_per']*item['count'] for item in nq_reg_list['materials'])
			craftlist.reg_price_partial = nq_reg_list['partial']
			craftlist.dc_shopping_list = _create_to_buy_json(nq_dc_list['materials'])
			craftlist.reg_shopping_list = _create_to_buy_json(nq_reg_list['materials'])
			craftlist.save()

			# HQ
			craftlist = CraftList()
			craftlist.item = recipe.item
			craftlist.recipe = recipe
			craftlist.homeworld = world
			craftlist.quality = 'hq'
			craftlist.home_price = sum(item['price_per']*item['count'] for item in hq_home_list['materials'])
			craftlist.home_price_partial = hq_home_list['partial']
			craftlist.dc_price = sum(item['price_per']*item['count'] for item in hq_dc_list['materials'])
			craftlist.dc_price_partial = hq_dc_list['partial']
			craftlist.reg_price = sum(item['price_per']*item['count'] for item in hq_reg_list['materials'])
			craftlist.reg_price_partial = hq_reg_list['partial']
			craftlist.dc_shopping_list = _create_to_buy_json(hq_dc_list['materials'])
			craftlist.reg_shopping_list = _create_to_buy_json(hq_reg_list['materials'])
			craftlist.save()





