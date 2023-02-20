from app.models import *
from pprint import pprint as p
from django.core.management.base import BaseCommand, CommandError
from django.urls import re_path as url

from django.conf import settings

from app.api_handling import *
from app.utils import fetch_json
import logging
import time
from app.facts_handling import *

class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		logger = logging.getLogger(__name__)
		



		# ## Recipes
		# data = []
		# for objectID in [3451,3626,3627,3612,3640,3641,1141]:
		# 	data.append(fetch_json(f"https://xivapi.com/recipe/{objectID}?private_key={getattr(settings, 'XIVAPI_KEY', None)}"))
		# with open("./junk.recipes.json", "w") as json_file:
		# 	json_file.write(json.dumps(data, indent=4))

		# ## Items
		# data = []
		# for objectID in [19584,11,8,19947,19957,5116,9,19928,10,19933,19983,19984,12,7,5518,19985,19986,5491,5522]:
		# 	data.append(fetch_json(f"https://xivapi.com/item/{objectID}?private_key={getattr(settings, 'XIVAPI_KEY', None)}"))
		# with open("./junk.items.json", "w") as json_file:
		# 	json_file.write(json.dumps(data, indent=4))


#--
		
		# item=Item.objects.get(guid=19584)	
		# p(item.summary())		
		# process(item.summary())

#--
		min_sleep = 60
		handler = Universalis()
		while True:

			handler.fetch_sales()
			print("Going to sleep...")

			handler.fetch_listings()
			print("Going to sleep...")

			compute_item_facts()
			print("Going to sleep...")

			time.sleep(60 * min_sleep)










