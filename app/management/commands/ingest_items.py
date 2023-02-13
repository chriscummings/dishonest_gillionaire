from django.core.management.base import BaseCommand, CommandError
from app.api_handling import XivApi


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		handler = XivApi()
		handler.ingest_item_details()
