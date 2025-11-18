import pandas

from .models import *

import pandas as pd
from xlsxwriter import Workbook


def generate_new_items_file(file = 'media/Wiggle_Worm-Items.xlsx'):
    """Returns the pd.Dataframe of all items added in the media/Wiggle_Worm-Items.xlsx File, unless other file specified."""
    wiggle_worm_items = pandas.read_excel(file)
    if wiggle_worm_items.empty:
        print('empty')
    else:
        wiggle_worm_items = wiggle_worm_items.to_dict(orient='records')
    for item in wiggle_worm_items:
        item_name, item_weight, item_price = item['Item Name'], item['Item Weight'], item['Item Price']
        item_name.replace('_', ' ').title()
        item_id = item_name.replace(' ', '_').lower()
        item = Item(item_id=item_id, item_name=item_name, item_weight=item_weight, item_price=item_price)
        item.save()
    print(Item.objects.all())

def add_item(item_name: str, item_weight = 0, item_price = 0):
    if Item.objects.filter(item_name=item_name).exists():
        print('Item already exists')
    else:
        item_name = item_name.replace('_', ' ').title()
        item_id = item_name.replace(' ', '_').lower()
        item = Item(item_id=item_id, item_name=item_name, item_weight=item_weight, item_price=item_price)
        item.save()
        print(Item.objects.all())
