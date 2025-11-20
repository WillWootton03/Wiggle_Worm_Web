from _ast import Store
from http.client import CannotSendRequest

import pandas
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import User
from .forms import LoginForm, Register
from .models import *

import json

def index(request):
    return render(request, 'base.html',)

@login_required()
def home(request):
    if request.user.role == 'Administrator':
        return redirect('admin_homepage')
    return render(request, 'front_page.html')


def register(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_success')
        else:
            print(form.errors)
    else:
        form = Register()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or 'home'
                return redirect(next_url)
            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = LoginForm()

    context = {'form' : form}
    return render(request, 'registration/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

def register_confirm(request):
    return render(request, 'register_success.html')

from .services import generate_new_items_file, add_item

@login_required()
def admin_homepage(request):
    user = request.user
    print(user.role)
    if user.role == 'Administrator':
        print('administrator')
        items = Item.objects.all()
        stores = Store.objects.all()
        context = {'user': user, 'items': items, 'stores': stores}
        return render(request, 'admin/admin_homepage.html', context)
    else:
        print(user.role)
        context = {'user': user}
        return redirect('home')

@login_required()
def supplier_homepage(request):
    user = request.user
    if user.role == 'Supplier':
        items = Item.objects.all()
        store = Store.objects.get(owner=user)
        if store:
            stock_items = Stock.objects.get(store=store).stock_items.all()
            context = {'user': user, 'items': items, 'stock_items': stock_items, 'store': store}
            return render(request, 'supplier_homepage.html', context)
        else:
            print('Not a Supplier of a store')
    return redirect('home')




def update_item_data(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = Item.objects.get(id=item_id)
            item.weight = float(data.get('weight', item.weight))
            item.price = float(data.get('price', item.price))
            item.save()
            return JsonResponse({'success': True})
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error' : 'Item not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error' : str(e)})
    return JsonResponse({'success': False, 'error' : 'Invalid request.'})


def delete_item_data(request, item_id):
    if request.method == 'POST':
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except Item.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_stock_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            stock_item_id = data.get('id')
            stock_item_uuid = uuid.UUID(stock_item_id)
            stock_item = StockItem.objects.get(id=stock_item_uuid)
            stock_item.quantity = int(data.get('quantity'))
            stock_item.price = float(data.get('price'))
            stock_item.save()
            return JsonResponse({'success': True})
        except StockItem.DoesNotExist:
            return JsonResponse({'success': False, 'error' : 'Item not found.'})

    return JsonResponse({'success': False, 'error' : 'Invalid request.'})

@csrf_exempt
def upload_stock_file(request):
    if request.method == 'POST':
        stock_file = request.FILES.get('stock_file')
        store_id = request.POST.get('store_id')

        if not stock_file:
            return HttpResponse('Empty file.', status=400)

        if not store_id:
            return HttpResponse('No Store id.', status=400)

        if not stock_file.name.endswith('.xlsx'):
            return HttpResponse('Incorrect file-type', status=400)

        # Get the new stock df and clean the columns to fit our conventional styles
        new_stock_items_df = pd.read_excel(stock_file)
        new_stock_items_df.columns = (
            new_stock_items_df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace('-', '_')
        )

        # Clear the current stores stock, get variables for the store and the store_stock
        store = Store.objects.get(id=store_id)
        store_stock = Stock.objects.get(store=store)
        StockItem.objects.filter(stock=store_stock).delete()

        # For each new stock item, get the item by referencing its item_id, and set its quantity and price
        # Add the item to the db
        for _, row in new_stock_items_df.iterrows():
            item = Item.objects.filter(item_id=row['item_id']).first()
            if not item:
                print(f'No such item at {row['item_id']}')
            else:
                item_quantity = int(row['quantity'])
                item_price = float(row['price'])
                item_to_add = StockItem.objects.create(stock=store_stock, item=item, quantity=item_quantity, price=item_price)
                item_to_add.save()
                print('item added')
        return redirect('/supplier_homepage/?uploaded=true')
    return redirect('/supplier_homepage')

@require_POST
def remove_items(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if ids:
            StockItem.objects.filter(id__in=ids).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error' : str(e)})