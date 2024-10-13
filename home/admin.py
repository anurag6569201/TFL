from django.contrib import admin
from .models import Item, LunchMenu, DinnerMenu, Scanner,DeliciousMenu,Menu_Board_items,TodayLunchMenu,TodayDinnerMenu,Order

# Admin for Item model
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_price', 'item_description')
    search_fields = ('item_name',)
    list_filter = ('item_price',)


@admin.register(Menu_Board_items)
class Menu_Board_itemsAdmin(admin.ModelAdmin):
    list_display = ('item_name',)
    search_fields = ('item_name',)


# Admin for LunchMenu model
@admin.register(LunchMenu)
class LunchMenuAdmin(admin.ModelAdmin):
    list_display = ('id',)  # Display the ID of the Lunch Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

# Admin for LunchMenu model
@admin.register(TodayLunchMenu)
class TodayLunchMenuAdmin(admin.ModelAdmin):
    list_display = ('id','item_category')  # Display the ID of the Lunch Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

# Admin for LunchMenu model
@admin.register(TodayDinnerMenu)
class TodayDinnerMenuAdmin(admin.ModelAdmin):
    list_display = ('id','item_category')  # Display the ID of the Lunch Menu
    filter_horizontal = ('items',)  # Easy selection of many-to-many items

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