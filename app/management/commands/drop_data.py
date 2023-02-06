from django.core.management.base import BaseCommand, CommandError

from app.models import *


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		Sale.objects.all().delete()
		Listing.objects.all().delete()
		Ingredient.objects.all().delete()
		Recipe.objects.all().delete()
		Item.objects.all().delete()
