""" Parse XIVAPI item JSON and create/update item models. 
"""

import json
import time
import datetime

from django.core.management.base import BaseCommand, CommandError
import requests

from app.models import *


INPUT_FILE = "data/xivapi_items.json"


import pdb
def ingest_items():
	start_time = datetime.datetime.now()

	print("Loading file...")
	item_json = json.load(open(INPUT_FILE))

	print("Parsing file...")
	for i in item_json:

		if i['Name'] == '' or i['Name'] == 'Other':
			continue

		try:
			item = Item.objects.get(guid=i['ID'])
		except Item.DoesNotExist:
			item = Item()


		try:
			item.name          = i['Name']
			item.icon          = i['Icon']
			item.guid          = i['ID']
			item.can_be_hq     = True if i['CanBeHq'] == 1 else False
			item.stack_size    = i['StackSize']
			item.vendor_price  = i['PriceLow']

			if i['ClassJobCategory']:
				item.jobs = i['ClassJobCategory']['Name']

			if i['ItemUICategory']:
				item.ui_category   = i['ItemUICategory']['Name']

			item.is_dyeable    = True if i['CanBeHq'] == 1 else False
			item.is_glamourous = True if i['CanBeHq'] == 1 else False
			item.is_untradable = True if i['CanBeHq'] == 1 else False
			item.is_unique     = True if i['CanBeHq'] == 1 else False
			item.save()
		except Exception as e:
			print(e)
			pdb.set_trace()

		print(item)

	print(datetime.datetime.now() - start_time)


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		ingest_items()
