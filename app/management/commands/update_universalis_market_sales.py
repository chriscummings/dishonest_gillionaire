""" Fetches market board item sales from Universalis API. 
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


API_ENDPOINT = "http://universalis.app/api/v2/history/North-America/"
UNIVERSALIS_MAX_CALLS_PER_SECOND = 13 # Universalis 25 max
UNIVERSALIS_MAX_CONNECTIONS = 6 # Universalis 8 max
ITEMS_PER_API_CALL = 100 # Universalis 100 max
HOURS_AGO_TO_UPDATE = 0
MAX_SALES_PER_ITEM = 20


@sleep_and_retry
@limits(calls=UNIVERSALIS_MAX_CALLS_PER_SECOND, period=1)
def fetch_and_process_item_sales(item_ids_querystring):
	api_resp = fetch_json(API_ENDPOINT+item_ids_querystring+"?entriesToReturn="+str(MAX_SALES_PER_ITEM))

	# Handle items unknown by Universalis..
	for item_id in api_resp['unresolvedItems']:
		Item.flag_universalis_unresolved(item_id)

	for key in api_resp['items'].keys():
		item_id = key

		print("Processing item "+str(item_id))

		sales_json = api_resp['items'][key]['entries']

		item = Item.objects.get(guid=item_id)

		#FIXME: handle/log this...
		if not item: raise "OH SNAP, ITEM "+str(item_guid)+" NOT FOUND"

		new_sales = []

		for s in sales_json:
			sale = Sale.objects.filter(sold_at=datetime.datetime.utcfromtimestamp(s['timestamp']), buyer_name=s['buyerName'])

			# Ignore existing sales.
			if sale: continue

			sale                = Sale()
			sale.item           = item
			sale.region         = api_resp['items'][key]['regionName']
			sale.world          = s['worldName']
			sale.price_per_unit = s['pricePerUnit']
			sale.quantity       = s['quantity']
			sale.buyer_name     = s['buyerName']
			sale.sold_at        = datetime.datetime.fromtimestamp(s['timestamp'], timezone.utc)

			new_sales.append(sale)

		Sale.objects.bulk_create(new_sales)
		item.northamerica_sales_updated_at = datetime.datetime.now(tz=timezone.utc)
		item.save()

def fetch_sales():
	start_time = datetime.datetime.now()

	print("Building list..")

	items = Item.objects.filter( 
		Q(northamerica_sales_updated_at__lt=(datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(hours = HOURS_AGO_TO_UPDATE))) | 
		Q(northamerica_sales_updated_at__isnull=True), Q(universalis_unresolved=False) ).order_by('guid')

	paginator = Paginator(items, ITEMS_PER_API_CALL)

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
			for _ in executor.map(fetch_and_process_item_sales, item_query_strings):
				pass 

	print(datetime.datetime.now() - start_time)


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		fetch_sales()
