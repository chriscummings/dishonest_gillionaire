from app.models import *
from django.core.management.base import BaseCommand, CommandError
import json

class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):

		marketable_item_ids = json.load(open("3rd_party_sample_data/universalis-marketable-items.json"))
		item_details = json.load(open("data/xivapi_items.json"))
		values_set = set()


		# for i in item_details:
		# 	values_set.add(i['FilterGroup'])

		# print(values_set)





		for i in item_details:
			if i['ID'] in marketable_item_ids:
				if i['ItemSearchCategory']:
					values_set.add(i['ItemSearchCategory']['Name'])
				else:
					print("f")
		print(values_set)















		# for item_id in marketable_item_ids:
		# 	item = Item.objects.get(guid=item_id)
		# 	print(item.is_untradable)

		# 	values_set.add()





