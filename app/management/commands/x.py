from app.models import *
from pprint import pprint as p
from django.core.management.base import BaseCommand, CommandError
from django.urls import re_path as url


def process(item, indent=0):
	indention = ""

	for i in range(0, indent):
		indention += "\t"

	print(f"{indention}* Item: {item['name']}")

	indent += 1

	for recipe in item['recipes']:
		print(f"{indention}Recipe: {recipe['profession']} profession:")
		for ingredient in recipe['ingredients']:
			process(ingredient, indent)


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		i=Item.objects.get(guid=19584)
		s=i.summary(sale_limit=0, listing_limit=0)
		p(s)
		print("-------------------")
		process(s)
