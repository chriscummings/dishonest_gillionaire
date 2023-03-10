from django.urls import path
from .views import HomePageView
from .views import item_index, item_show, results_view


urlpatterns = [
	path('', HomePageView.as_view(), name='home'),

	path('items/', item_index, name='items'),
	path('items/<int:item_guid>', item_show, name='item'),

	path('results/', results_view, name='search_results')

]
