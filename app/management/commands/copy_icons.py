from django.core.management.base import BaseCommand, CommandError
from app.models import *
import os 
import shutil

icon_export_folder = 'data/all_icons'
icon_assets_folder = 'static/icon'

class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = 'Digs out icons for marketable items'

	def handle(self, *args, **options):
		marketable_items = Item.objects.filter(is_marketable=True)
		for item in marketable_items:
			folder, file = item.icon.replace('/i/', '').split('/')

			src_path = os.path.join(icon_export_folder,folder,file )
			dst_path = os.path.join(icon_assets_folder,file )

			if os.path.exists(src_path):
				shutil.copyfile(src_path, dst_path)












