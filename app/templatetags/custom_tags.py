from django import template

register = template.Library()

# https://realpython.com/django-template-custom-tags-filters/#building-tags-and-filters
# https://www.pluralsight.com/guides/create-custom-template-tags-and-filters-in-django




def _format_summary_recipes(item, indent=0):
	formatted_string = ""

	indention = ""

	for i in range(0, indent):
		indention += "\t"

	# Ignore top-level item that's without a material_count.
	if 'material_count' in item:
		formatted_string += f"\n<a href=\"/items/{item['guid']}\">{item['name']}</a> x{item['material_count']}\n"

	formatted_string += f"<ul>\n"
	for recipe in item['recipes']:
		formatted_string += f"<li>\n"
		formatted_string += f"Recipe: ({recipe['profession']}):\n"
		formatted_string += f"<ul>\n"
		for ingredient in recipe['ingredients']:
		 	formatted_string += f"<li>{_format_summary_recipes(ingredient, indent+1)}</li>\n"
		formatted_string += f"</ul>\n"
		formatted_string += f"</li>\n"
	formatted_string += f"</ul>\n"
	return formatted_string

@register.simple_tag
def render_recipes(obj):
	return _format_summary_recipes(obj)
