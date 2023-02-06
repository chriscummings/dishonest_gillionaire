from django import template

register = template.Library()

# https://realpython.com/django-template-custom-tags-filters/#building-tags-and-filters
# https://www.pluralsight.com/guides/create-custom-template-tags-and-filters-in-django

@register.simple_tag
def render_recipes(obj):
	print(obj)
	return "FUCK"