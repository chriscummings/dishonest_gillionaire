""" Fetches market board item listings from Universalis API. 
"""

import json
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from ratelimit import limits, RateLimitException, sleep_and_retry

from app.models import *
from app.utils import fetch_json


#TODO: Only dealing with North-America rn. See also: "Japan", "Europe" and "Oceania"


API_ENDPOINT = "http://universalis.app/api/v2/North-America/"
UNIVERSALIS_MAX_CALLS_PER_SECOND = 13 # 25 max
UNIVERSALIS_MAX_CONNECTIONS = 6 # 8 max
LISTINGS_PER_API_CALL = 500 # Universalis no max.

@sleep_and_retry
@limits(calls=UNIVERSALIS_MAX_CALLS_PER_SECOND, period=1)
def fetch_and_process_item_listings(item_ids_querystring):
	api_resp = fetch_json(API_ENDPOINT+item_ids_querystring+"?listings="+str(LISTINGS_PER_API_CALL))

	# Handle items unknown by Universalis..
	for item_id in api_resp['unresolvedItems']:
		Item.flag_universalis_unresolved(item_guid)

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
			listing = Listing.objects.filter(listing_guid=l['listingID'])

			# Ignore existing listing.
			if listing: continue

			listing                = Listing()
			listing.item           = item
			listing.region         = api_resp['regionName']
			listing.world          = l['worldName']
			listing.listing_guid   = l['listingID']
			listing.retainer_guid  = l['retainerID']
			listing.retainer_name  = l['retainerName']
			listing.price_per_unit = l['pricePerUnit']
			listing.quantity       = l['quantity']
			listing.total          = l['total']

			new_listings.append(listing)

		Listing.objects.bulk_create(new_listings)
		item.northamerica_listings_updated_at = datetime.datetime.now(tz=timezone.utc)
		item.save()

def fetch_market_listings():
	start_time = datetime.datetime.now()

	print("Building list..")

	items = Item.objects.filter( 
		Q(northamerica_listings_updated_at__lt=(datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(hours = 0))) | 
		Q(northamerica_listings_updated_at__isnull=True), Q(universalis_unresolved=False) ).order_by('guid')

	print(len(items))

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
		with PoolExecutor(max_workers=UNIVERSALIS_MAX_CONNECTIONS) as executor:
			for _ in executor.map(fetch_and_process_item_listings, item_query_strings):
				pass 

	print(datetime.datetime.now() - start_time)


class Command(BaseCommand):
	""" Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		fetch_market_listings()
