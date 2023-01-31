# Dishonest Gilionaire

A FFXIV market data tool.

![Money](tataru.gif "Money")

[JoCat](https://www.youtube.com/watch?v=ZGWUkDk8eWo)

## Building/Updating the database

* (Optional) To truncate item, recipe and market data run the drop_data command. 
`poetry run python manage.py drop_data`

### Item Data

* To download all game items from XIVAPI (only needed on game update, downloads JSON to ./data):
`poetry run python manage.py fetch_xivapi_item_list`
* To ingest the items downloaded from XIVAPI:
`poetry run python manage.py ingest_xivapi_item_list`

### Recipe Data

* To download all recipes from XIVAPI (only needed on game update, downloads JSON to ./data):
`poetry run python manage.py fetch_xivapi_recipe_list`
* To download all recipe details from XIVAPI (only needed on game update, downloads JSON to ./data):
`poetry run python manage.py fetch_ffxivapi_recipes`
* To ingest the recipes downloaded from XIVAPI:
`poetry run python manage.py ingest_xivapi_recipes`

### Market Data

* To update market listings from Universalis:
`poetry run python manage.py update_universalis_market_listings`
* To update market sales from Universalis:
`poetry run python manage.py update_universalis_market_sales`

# Useful links:

* https://na.finalfantasyxiv.com/lodestone/playguide/db - Lodestone Database
* https://xivapi.com
* https://universalis.app/
* https://github.com/Universalis-FFXIV/Universalis
* https://github.com/DeltaBreaker/Lolorito
* https://lumina.xiv.dev/docs/intro.html
* https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json
* https://raw.githubusercontent.com/xivapi/ffxiv-datamining/master/csv/Item.csv
* https://ffxiv.pf-n.co/ - lulu's tools
