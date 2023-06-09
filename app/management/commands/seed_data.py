from django.core.management.base import BaseCommand, CommandError
from app.models import *

# https://na.finalfantasyxiv.com/lodestone/worldstatus/
SERVER_TOPOLOGY = {
	'regions': [
		{
			'name': 'North-America',
			'data_centers': [
				{
					'name': 'Aether',
					'worlds': [
						'Adamantoise',
						'Cactuar',
						'Faerie',
						'Gilgamesh',
						'Jenova',
						'Midgardsormr',
						'Sargatanas',
						'Siren'		
					]
				},
				{
					'name': 'Crystal',
					'worlds': [
						'Balmung',
						'Brynhildr',
						'Coeurl',
						'Diabolos',
						'Goblin',
						'Malboro',
						'Mateus',
						'Zalera'
					]
				},
				{
					'name': 'Dynamis',
					'worlds': [
						'Halicarnassus',
						'Maduin',
						'Marilith',
						'Seraph'
					]
				},
				{
					'name': 'Primal',
					'worlds': [
						'Behemoth',
						'Excalibur',
						'Exodus',
						'Famfrit',
						'Hyperion',
						'Lamia',
						'Leviathan',
						'Ultros'
					]
				}												
			]
		}
	]
}

def seed_region_dc_world():
	for r in SERVER_TOPOLOGY['regions']:
		region_name = r['name']

		try:
			region = Region.objects.get(name=region_name)
			print(region.id)
		except Region.DoesNotExist as error:
			region = Region()
			region.name = region_name
			region.save()

		for dc in r['data_centers']:
			dc_name = dc['name']

			try:
				data_center = DataCenter.objects.get(name=dc_name)
			except DataCenter.DoesNotExist as error:
				data_center = DataCenter()
				data_center.name = dc_name
				data_center.region = region
				data_center.save()

			for world_name in dc['worlds']:

				try:
					world = World.objects.get(name=world_name)
				except World.DoesNotExist as error:
					world = World()
					world.name = world_name
					world.data_center = data_center
					world.save()


class Command(BaseCommand):
	"""Required class for using manage.py to invoke tasks.
	"""
	help = ''

	def handle(self, *args, **options):
		seed_region_dc_world()
