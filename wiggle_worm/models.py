from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
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


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (

        ('Customer', 'Customer'),
        ('Supplier', 'Supplier'),
        ('Administrator', 'Administrator')
    )
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(choices=ROLES, default='Customer')

    class Meta:
        db_table = 'wiggle_worm_user'

    def __str__(self):
        return self.email

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Item(models.Model):
    item_id = models.CharField(max_length=100, primary_key=True)
    item_name = models.CharField(max_length=255)
    item_weight = models.FloatField()
    item_price = models.FloatField()





class Stock(models.Model):
    owner = models.ForeignKey(Company, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='items')




