from django.test import TestCase
from app.models import *
from app.api_handling import *
from glob import glob

class ApiHandlingTest(TestCase):
	def test_ingest_item_details(self):
		handler = XivApi()
		handler.ingest_item_details(src_dir="./app/test_data/items")
		self.assertEqual(19, len(Item.objects.all()))

	def test_ingest_recipe_details(self):
		handler = XivApi()
		handler.ingest_item_details(src_dir="./app/test_data/items")
		handler.ingest_recipe_details(src_dir="./app/test_data/recipes")
		self.assertEqual(7, len(Recipe.objects.all()))
		#self.assertEqual(999, len(Ingredient.objects.all()))

	def test_fetch_and_process_item_listings(self):
		handler = Universalis()

		listing_json_files = glob("./app/test_data/listings/*.json")

		for f in listing_json_files:
			handler.fetch_and_process_item_listings("", json_file=f)



'''
ITEM: Molybdenum Awl i(19584) 
	RECIPE: Molybdenum Awl r(3451)
		ITEM: Earth Crystal x5 i(11)
		ITEM: Fire Crystal x6 i(8)
		ITEM: Molybdenum Ingot x2 i(19947) 
			RECIPE: Molybdenum Ingot r(3626)
				ITEM: Molybdenum Ore x4 i(19957)
				ITEM: Cobalt Ore x1 i(5116)
				ITEM: Fire Crystal x? i(8)
			RECIPE: Molybdenum Ingot r(3627)
				ITEM: Molybdenum Ore x4 i(19957)
				ITEM: Cobalt Ore x1 i(5116)
				ITEM: Ice Crystal x? i(9)
		ITEM: Zelkova Lumber x1 i(19928) #
			RECIPE: Zelkova Lumber r(3612)
				ITEM: Wind Crystal x5 i(10)
				ITEM: Zelkova Log x4 i(19933)
		ITEM: Steppe Serge x1 i(19983) 
			RECIPE: Steppe Serge r(3640)
				ITEM: Lightning Crystal x3 i()
				ITEM: Worsted Yarn x3 i(19984) 
				RECIPE: Worsted Yarn r(3641)
					ITEM: Lightning Crystal x2 i(12)
					ITEM: Water Shard x2 i(7)
					ITEM: Rock Salt x1 i(5518)
					ITEM: Halgai Mane x2 i(19985)
					ITEM: Manzasiri Hair x2 i(19986)
					ITEM: Effevescent Water x1 i(5491)
					ITEM: Natron x1 i(5522) 
						RECIPE: Natron r(1141)
							ITEM: Water Shard x2 i(7)
							ITEM: Rock Salt x1 i(5518)
							ITEM: Effervescent Water x1 i(5491)



item=Item.objects.get(guid=19584)	


recipe=Recipe.objects.get(guid=3627)	


items=Item.objects.filter(name__contains="Fire Crystal")
items





'''