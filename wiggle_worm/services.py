from _ast import Store

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
        item_id, item_weight, item_price = item['Item Id'], item['Item Weight'], item['Item Price']
        item_name = item_id.replace('_', ' ').title()
        item = Item(item_id=item_id, name=item_name, weight=item_weight, price=item_price)
        item.save()
        print(item.name)

def generate_new_stores_file(file = 'media/Wiggle_Worm-Stores.xlsx'):
    wiggle_worm_stores = pandas.read_excel(file)
    if wiggle_worm_stores.empty:
        print('empty')
    else:
        wiggle_worm_stores = wiggle_worm_stores.to_dict(orient='records')
    for store in wiggle_worm_stores:
        store_id, store_owner_email, store_location = store['Store id'], store['Store Owner'], store['Store Location']
        store_name = store_id.replace('_', ' ').title()
        store_owner = User.objects.filter(email=store_owner_email).first()
        if store_owner:
            if User.objects.filter(email=store_owner_email).first().role != 'Supplier':
                store_owner = None
                print(f'not supplier at {store_owner_email}')
        else:
            store_owner = None
            print(f'no owner at {store_owner_email}')

        store = Store(store_id=store_id, name=store_name, owner=store_owner, location=store_location)
        store.save()
        print(store.name)


def add_item(item_name: str, item_weight = 0, item_price = 0):
    if Item.objects.filter(item_name=item_name).exists():
        print('Item already exists')
    else:
        item_name = item_name.replace('_', ' ').title()
        item_id = item_name.replace(' ', '_').lower()
        item = Item(item_id=item_id, name=item_name, weight=item_weight, price=item_price)
        item.save()
        print(Item.objects.all())

