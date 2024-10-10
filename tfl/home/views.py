from django.shortcuts import render
from .models import Item, LunchMenu, DinnerMenu, Scanner, DeliciousMenu,TodayLunchMenu,TodayDinnerMenu

def home(request):
    lunch_add_ons = LunchMenu.objects.order_by('id').first()
    dinner_add_ons = DinnerMenu.objects.order_by('id').first()
    crousal_menu_items=DeliciousMenu.objects.order_by('id').first()

    today_veg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="non_veg").first()

    today_veg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="non_veg").first()


    context = {
        'lunch_add_ons': lunch_add_ons.items.all() if lunch_add_ons else [],
        'dinner_add_ons': dinner_add_ons.items.all() if dinner_add_ons else [],
        'crousal_menu_items': crousal_menu_items.items.all() if crousal_menu_items else [],
        'today_veg_lunch_menu': today_veg_lunch_menu.items.all() if today_veg_lunch_menu else [],
        'today_nonveg_lunch_menu': today_nonveg_lunch_menu.items.all() if today_nonveg_lunch_menu else [],
        'today_veg_dinner_menu': today_veg_dinner_menu.items.all() if today_veg_dinner_menu else [],
        'today_nonveg_dinner_menu': today_nonveg_dinner_menu.items.all() if today_nonveg_dinner_menu else [],
    }
    return render(request, 'apps/home/index.html', context)

def add_to_cart(request):
    return render(request, 'apps/home/add_to_cart.html')