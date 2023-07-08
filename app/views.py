import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone
from .models import *
from .forms import SearchBarForm

class HomePageView(TemplateView):
	template_name = 'home.html'



def item_index(request):
	items = Item.objects.filter(northamerica_listings_updated_at__gte=(
		datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(hours = 24)
	))[0:10]

	context = {'items': items}
	return render(request, 'item_index.html', context)

def item_show(request, item_guid):
	item = Item.objects.get(guid=item_guid)

	home_name = request.COOKIES.get('dishonest')
	home = World.objects.filter(name=home_name)[0]

	purchase_pricing = BestPurchasePricing.objects.filter(home=home, item=item).last()
	craft_pricing = BestCraftPricing.objects.filter(home=home, item=item).last()

	facts = {}
	x = []

	region = Region.objects.last()
	for datacenter in region.data_centers.all():
		for world in datacenter.worlds.all():
			if world.name not in facts.keys():

				fact = WorldItemFact.objects.filter(item_id=item.id, world_id=world.id).last()
				facts[world.name] = fact


			if world.name == 'Malboro':
				x = WorldItemFact.objects.filter(item_id=item.id, world_id=world.id)


	icon = f"icon/{item.summary()['icon'].split('/')[-1]}"

	context = {
		'icon':icon,
		'facts': facts,
		'item_summary':item.summary(world=home),
		'x':x,
		'purchase_pricing':purchase_pricing,
		'craft_pricing':craft_pricing,
	}

	return render(request, 'item_show.html', context)

def results_view(request):
	form = SearchBarForm(request.POST)
	if form.is_valid():
		items = Item.objects.filter(name__contains=form.cleaned_data['item_name'].lower())

	context = {'items': items}
	return render(request, 'search_results.html', context)

def pricing_view(request):

	item_id = request.GET.get('item')
	home_world = request.GET.get('home')



	if item_id == None or home_world == None:
		raise Exception("FIXME: handle this...")

	##
	# BestPurchasePricing.objects.filter(item_id=item_id, home_id=home_world).last()
	##
	context = {"item_id":item_id, "home_world":home_world}
	return render(request, 'item_pricing.html', context)
