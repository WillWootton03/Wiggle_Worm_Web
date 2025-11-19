from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Store, Stock, Item

@receiver(post_save, sender=Store)
def create_stock_for_store(sender, instance, created, **kwargs):
    if created:
        Stock.objects.create(store=instance)
