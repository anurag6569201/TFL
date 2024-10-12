from django.shortcuts import render
from .models import Item, LunchMenu, DinnerMenu, Scanner, DeliciousMenu,TodayLunchMenu,TodayDinnerMenu
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,Http404

def home(request):
    cart = request.session.get('cart', {})

    lunch_add_ons = LunchMenu.objects.order_by('id').first()
    dinner_add_ons = DinnerMenu.objects.order_by('id').first()
    crousal_menu_items=DeliciousMenu.objects.order_by('id').first()

    today_veg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="non_veg").first()

    today_veg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="non_veg").first()


    context = {
        'today_veg_lunch_menu_price': today_veg_lunch_menu,
        'today_nonveg_lunch_menu_price': today_nonveg_lunch_menu,
        'today_veg_dinner_menu_price': today_veg_dinner_menu,
        'today_nonveg_dinner_menu_price': today_nonveg_dinner_menu,

        'lunch_add_ons': lunch_add_ons.items.all() if lunch_add_ons else [],
        'dinner_add_ons': dinner_add_ons.items.all() if dinner_add_ons else [],
        'crousal_menu_items': crousal_menu_items.items.all() if crousal_menu_items else [],
        'today_veg_lunch_menu': today_veg_lunch_menu.items.all() if today_veg_lunch_menu else [],
        'today_nonveg_lunch_menu': today_nonveg_lunch_menu.items.all() if today_nonveg_lunch_menu else [],
        'today_veg_dinner_menu': today_veg_dinner_menu.items.all() if today_veg_dinner_menu else [],
        'today_nonveg_dinner_menu': today_nonveg_dinner_menu.items.all() if today_nonveg_dinner_menu else [],
        'cart': cart,
    }
    return render(request, 'apps/home/index.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        meal_type = request.POST.get('meal_type')  # Get the meal type
        quantity = int(request.POST.get('quantity', 1))  # Default quantity to 1
        item = get_object_or_404(Item, item_name=item_name)
        
        cart = request.session.get('cart', {})
        
        # Create a unique key for the item and meal type
        cart_key = f"{item_name}_{meal_type}"
        
        if quantity > 0:
            # Save item in cart with meal type
            cart[cart_key] = {
                'item_name': item_name,  # Store the original item name as well
                'price': str(item.item_price),
                'quantity': quantity,
                'meal_type': meal_type  # Store meal type in cart
            }
        elif cart_key in cart:
            del cart[cart_key]  # Remove item if quantity is zero
        
        request.session['cart'] = cart
        return JsonResponse({'success': True, 'cart': cart})
    
    return JsonResponse({'error': 'Invalid request method'})


def view_cart(request):
    cart = request.session.get('cart', {})
    items = {}

    today_veg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_lunch_menu=TodayLunchMenu.objects.order_by('id').filter(item_category="non_veg").first()

    today_veg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_dinner_menu=TodayDinnerMenu.objects.order_by('id').filter(item_category="non_veg").first()

    
    # Fetch item details for each item in the cart
    for cart_key, item_data in cart.items():
        try:
            item = get_object_or_404(Item, item_name=item_data['item_name'])  # Fetch using the original item name
            items[cart_key] = {
                'item_name': item.item_name,
                'price': item.item_price,
                'meal_type': item_data['meal_type'],
                'quantity': item_data['quantity'],
                'total_price': item_data['quantity'] * item.item_price,
                'image_url': item.item_image.url if item.item_image else '',  # Assuming your Item model has an image field
            }
        except Http404:
            # Handle the case where the item does not exist (optional)
            continue

    context = {
        'today_veg_lunch_menu_price': today_veg_lunch_menu,
        'today_nonveg_lunch_menu_price': today_nonveg_lunch_menu,
        'today_veg_dinner_menu_price': today_veg_dinner_menu,
        'today_nonveg_dinner_menu_price': today_nonveg_dinner_menu,
        'cart': items,  # Updated to use the fetched item details
    }
    return render(request, 'apps/home/view_cart.html', context)
