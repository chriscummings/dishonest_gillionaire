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

	context = {
		'item_summary':item.summary()
	}

	return render(request, 'item_show.html', context)

def results_view(request):
	form = SearchBarForm(request.POST)
	if form.is_valid():
		items = Item.objects.filter(name__contains=form.cleaned_data['item_name'].lower())

	context = {'items': items}
	return render(request, 'search_results.html', context)

