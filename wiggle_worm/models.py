import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password, check_password, verify_password
from django.shortcuts import render, redirect

import pandas as pd
from django.template.defaultfilters import slugify


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def authenticate_user(self, email, password):
        if email and password:
            email = self.normalize_email(email)
            login_user = User.objects.get(email=email)
            if check_password(password, login_user.password):
                return login_user
        return None

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (

        ('Customer', 'Customer'),
        ('Supplier', 'Supplier'),
        ('Administrator', 'Administrator')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, default='')
    role = models.CharField(choices=ROLES, default='Customer')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        db_table = 'wiggle_worm_user'

    def __str__(self):
        return self.email

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_id = models.CharField(unique=True)
    name = models.CharField(max_length=255, default='')
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def set_owner(self, owner_email):
        owner = User.objects.get(email=owner_email)
        if owner:
            self.owner = owner
            self.save()
            return True
        return False


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, default='')
    weight = models.FloatField()
    price = models.FloatField()

    def __str__(self):
        return self.name

class Stock(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='stock')

    def __str__(self):
        return f'{self.store.name} - Stock'

class StockItem(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)

    class Meta:
        unique_together = (('stock', 'item'),)

    def __str__(self):
        return f'{self.stock.store.name} - {self.item.name}: {self.quantity}'





