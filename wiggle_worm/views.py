from _ast import Store

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.template import Context

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
        return render(request, '/', context)





def update_item(request, item_id):
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


def delete_item(request, item_id):
    if request.method == 'POST':
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except Item.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)