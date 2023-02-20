from app.models import *
from app.utils import captute_runtime
from datetime import datetime, timedelta
import statistics
from pprint import pprint as p
HOURS_AGO_TO_UPDATE = 2

def _to_world_dict(collection):
	print(f"collection:{len(collection)}")
	p(collection)
	world_dict = {}

	for obj in collection:
		world = obj.world

		if world.name not in world_dict.keys():
			world_dict[world.name] = []

		world_dict[world.name].append(obj)

	p(world_dict)
	return world_dict

def _compute_listings_facts(collection):
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
		'nq_list_mean': None,
		'nq_list_median': None,
		'nq_list_mode': None,
		'nq_list_high': None,
		'nq_list_low': None,
		'nq_list_count': None,
		'nq_sellers_count': None,

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

	for sale in collection:
		if sale.hq:
			hq_sales.append(sale.price_per_unit)
		else:
			nq_sales.append(sale.price_per_unit)

	sales_fact = {
		'nq_sold_mean': None,
		'nq_sold_median': None,
		'nq_sold_mode': None,
		'nq_sold_high': None,
		'nq_sold_low': None,
		'nq_sold_count': None,
		'nq_last_sold_value': None,
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

@captute_runtime
def compute_item_facts():

	marketable_items = Item.objects.filter(is_marketable=True)

	for item in marketable_items:
		print(f"Item: {item.name}")

		hours_ago = datetime.now() - timedelta(hours = HOURS_AGO_TO_UPDATE)

		sales = Sale.objects.filter(updated_at__gte=hours_ago, item_id=item.id)
		sales_by_world = _to_world_dict(sales)

		listings = Listing.objects.filter(updated_at__gte=hours_ago, item_id=item.id)
		listings_by_world = _to_world_dict(listings)

		for world in World.objects.all():
			print(f"{world.name}")

			fact = WorldItemFact(calculated_at=datetime.now())

			if world.name in sales_by_world.keys():
				sales_facts = _compute_sales_facts(sales_by_world[world.name])

				fact.nq_sold_mean = sales_facts['nq_sold_mean']
				fact.nq_sold_median = sales_facts['nq_sold_median']
				fact.nq_sold_mode = sales_facts['nq_sold_mode']
				fact.nq_sold_high = sales_facts['nq_sold_high']
				fact.nq_sold_low = sales_facts['nq_sold_low']
				fact.nq_sold_count = sales_facts['nq_sold_count']
				fact.hq_sold_mean = sales_facts['hq_sold_mean']
				fact.hq_sold_median = sales_facts['hq_sold_median']
				fact.hq_sold_mode = sales_facts['hq_sold_mode']
				fact.hq_sold_high = sales_facts['hq_sold_high']
				fact.hq_sold_low = sales_facts['hq_sold_low']
				fact.hq_sold_count = sales_facts['hq_sold_count']

				fact.hq_last_sold_value = sales_facts['hq_last_sold_value']
				fact.nq_last_sold_value = sales_facts['nq_last_sold_value']



			if world.name in listings_by_world.keys():
				listings_facts = _compute_listings_facts(listings_by_world[world.name])

				fact.nq_list_mean = listings_facts['nq_list_mean']
				fact.nq_list_median = listings_facts['nq_list_median']
				fact.nq_list_mode = listings_facts['nq_list_mode']
				fact.nq_list_high = listings_facts['nq_list_high']
				fact.nq_list_low = listings_facts['nq_list_low']
				fact.nq_list_count = listings_facts['nq_list_count']
				fact.hq_list_mean = listings_facts['hq_list_mean']
				fact.hq_list_median = listings_facts['hq_list_median']
				fact.hq_list_mode = listings_facts['hq_list_mode']
				fact.hq_list_high = listings_facts['hq_list_high']
				fact.hq_list_low = listings_facts['hq_list_low']
				fact.hq_list_count = listings_facts['hq_list_count']

				fact.hq_sellers_count = listings_facts['hq_sellers_count']
				fact.nq_sellers_count = listings_facts['nq_sellers_count']

			fact.item = item
			fact.world = world
			fact.save()
			print(fact)


