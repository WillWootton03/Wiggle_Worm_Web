from django.contrib import admin

from wiggle_worm.models import Item, Store, User, Stock,StockItem

# Register your models here.
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Store)
admin.site.register(StockItem)

class StockItemInline(admin.TabularInline):
    model = StockItem
    extra = 0

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    inlines = [StockItemInline]