from django.contrib import admin
from .models import Item, LunchMenu, DinnerMenu, Scanner,DeliciousMenu,Menu_Board_items,WeeklyMenu,Order,DeliveryAddress
from import_export.admin import ImportExportModelAdmin

# Admin for Item model
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_price', 'item_description')
    search_fields = ('item_name',)
    list_filter = ('item_price',)


@admin.register(Menu_Board_items)
class Menu_Board_itemsAdmin(ImportExportModelAdmin):
    list_display = ('item_name',)
    search_fields = ('item_name',)


# Admin for LunchMenu model
@admin.register(LunchMenu)
class LunchMenuAdmin(admin.ModelAdmin):
    list_display = ('id',)  # Display the ID of the Lunch Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(ImportExportModelAdmin):
    list_display = ("day_of_week", "meal_type", "item_category", "price")
    list_filter = ("day_of_week", "meal_type", "item_category")
    search_fields = ("day_of_week", "meal_type", "item_category")
    filter_horizontal = ("items",)  # Enables a horizontal filter widget for ManyToMany fields
    date_hierarchy = "date"
    ordering = ("day_of_week", "meal_type")

    fieldsets = (
        (None, {
            "fields": ("day_of_week", "meal_type", "item_category", "price")
        }),
        ("Items", {
            "fields": ("items",),
        }),
    )
    
# Admin for DinnerMenu model
@admin.register(DinnerMenu)
class DinnerMenuAdmin(admin.ModelAdmin):
    list_display = ('id',)  # Display the ID of the Dinner Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

# Admin for Scanner model
@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    list_display = ('scanner_image',)


@admin.register(DeliciousMenu)
class DeliciousMenu(admin.ModelAdmin):
    list_display = ('id',)  # Display the ID of the Lunch Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

from .models import Order
admin.site.register(Order)
admin.site.register(DeliveryAddress)