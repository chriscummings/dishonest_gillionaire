
	# To-Craft Pricing ----------------------------
	for recipe in Recipe.objects.all().order_by('level'):
		dataz = {}

		for ingredient in recipe.ingredients.all():
			count = ingredient.count
			item = ingredient.item

			for world in World.objects.all():

				#print(f"{count} {item} {world}")

				best_world_price = BestPurchasePricing.objects.filter(item_id=item, home_id=world).last()
		
				if not best_world_price:
					# FIXME: handle this..
					print(f"not found {item}")
					continue

				if world.name not in dataz.keys():
					dataz[world.name] = {'ingredients':[]}


	# {
	# 	'world':{
	# 		'ingredients':[{
	# 			'item_id':2341,
	# 			'nq_low_listing_region_price':none,
	# 			'nq_low_listing_dc_price':none,
	# 			'nq_low_listing_home_price':none,
	# 			'hq_low_listing_region_price':none,
	# 			'hq_low_listing_dc_price':none,
	# 			'hq_low_listing_home_price':none,
	# 		}]
	# 	},
	# }

				dataz[world.name]['ingredients'].append({
					'item':item.guid,
					'count':count,
					'nq_low_listing_region_price':best_world_price.best_nq_listing_in_region_price,
					'nq_low_listing_dc_price':best_world_price.best_nq_listing_in_datacenter_price,
					'nq_low_listing_home_price':best_world_price.home_nq_list_low,
					'hq_low_listing_region_price':best_world_price.best_hq_listing_in_region_price,
					'hq_low_listing_dc_price':best_world_price.best_hq_listing_in_datacenter_price,
					'hq_low_listing_home_price':best_world_price.home_hq_sold_low,					
				})
		
		#p(dataz)

		for world_name in dataz.keys():

			nq_home_craft_price = 0
			nq_home_craft_price_is_partial = True
			nq_dc_craft_price = 0
			nq_dc_craft_price_is_partial = True
			nq_region_craft_price = 0
			nq_region_craft_price_is_partial = True
			#
			hq_home_craft_price = 0
			hq_home_craft_price_is_partial = True
			hq_dc_craft_price = 0
			hq_dc_craft_price_is_partial = True
			hq_region_craft_price = 0
			hq_region_craft_price_is_partial = True

			for ingredient in dataz[world_name]['ingredients']:
				nq_home_craft_price += (ingredient['nq_low_listing_home_price'] or 0) * count
				nq_dc_craft_price += (ingredient['nq_low_listing_dc_price'] or 0) * count
				nq_region_craft_price += (ingredient['nq_low_listing_region_price'] or 0) * count
				hq_home_craft_price += (ingredient['hq_low_listing_home_price'] or 0) * count
				hq_dc_craft_price += (ingredient['hq_low_listing_dc_price'] or 0) * count
				hq_region_craft_price += (ingredient['hq_low_listing_region_price'] or 0) * count

			if nq_home_craft_price:nq_home_craft_price_is_partial = False
			if nq_dc_craft_price:nq_dc_craft_price_is_partial = False
			if nq_region_craft_price:nq_region_craft_price_is_partial = False
			if hq_home_craft_price:hq_home_craft_price_is_partial = False
			if hq_dc_craft_price:hq_dc_craft_price_is_partial = False
			if hq_region_craft_price:hq_region_craft_price_is_partial = False

			craft_price = BestCraftPricing()

			world = World.objects.filter(name=world_name).first()

			craft_price.item = recipe.item
			craft_price.home = world
			craft_price.datacenter = world.data_center
			craft_price.region = world.data_center.region
			craft_price.nq_home_craft_price = nq_home_craft_price
			craft_price.nq_home_craft_price_is_partial = nq_home_craft_price_is_partial
			craft_price.nq_dc_craft_price = nq_dc_craft_price
			craft_price.nq_dc_craft_price_is_partial = nq_dc_craft_price_is_partial
			craft_price.nq_region_craft_price = nq_region_craft_price
			craft_price.nq_region_craft_price_is_partial = nq_region_craft_price_is_partial
			craft_price.hq_home_craft_price = hq_home_craft_price
			craft_price.hq_home_craft_price_is_partial = hq_home_craft_price_is_partial
			craft_price.hq_dc_craft_price = hq_dc_craft_price
			craft_price.hq_dc_craft_price_is_partial = hq_dc_craft_price_is_partial
			craft_price.hq_region_craft_price = hq_region_craft_price
			craft_price.hq_region_craft_price_is_partial = hq_region_craft_price_is_partial

			#p(craft_price)

			craft_price.save()

			# return


