from django.contrib import admin

from .models import Item
admin.site.register(Item)

from .models import Recipe
admin.site.register(Recipe)

from .models import Listing
admin.site.register(Listing)

from .models import Sale
admin.site.register(Sale)
