from django.core.management.base import BaseCommand, CommandError
from app.utils import seed_region_dc_world

class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		seed_region_dc_world()
