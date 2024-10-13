from django.shortcuts import render
from .models import Item, LunchMenu, DinnerMenu, Scanner, DeliciousMenu,TodayLunchMenu,TodayDinnerMenu
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,Http404,HttpResponse
import razorpay
from django.conf import settings
import json
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
import uuid
from allauth.account.models import EmailAddress



def user_profile(request):
    user = request.user
    email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
    
    context = {
        'user': user,
        'email_verified': email_verified
    }
    return render(request, 'apps/home/user_profile.html', context)


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
        meal_type = request.POST.get('meal_type') 
        quantity = int(request.POST.get('quantity', 1)) 
        item = get_object_or_404(Item, item_name=item_name)
        
        cart = request.session.get('cart', {})
        
        cart_key = f"{item_name}_{meal_type}"
        
        if quantity > 0:
            
            cart[cart_key] = {
                'item_name': item_name, 
                'price': str(item.item_price),
                'quantity': quantity,
                'meal_type': meal_type 
            }
        elif cart_key in cart:
            del cart[cart_key]  
        
        request.session['cart'] = cart
        return JsonResponse({'success': True, 'cart': cart})
    
    return JsonResponse({'error': 'Invalid request method'})

def view_cart(request):
    user = request.user
    email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()

    cart = request.session.get('cart', {})
    items = {}
    
    today_veg_lunch_menu = TodayLunchMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_lunch_menu = TodayLunchMenu.objects.order_by('id').filter(item_category="non_veg").first()
    
    today_veg_dinner_menu = TodayDinnerMenu.objects.order_by('id').filter(item_category="veg").first()
    today_nonveg_dinner_menu = TodayDinnerMenu.objects.order_by('id').filter(item_category="non_veg").first()

    cart_total_amount = 0  

    for cart_key, item_data in cart.items():
        try:
            item = get_object_or_404(Item, item_name=item_data['item_name'])  # Fetch using the original item name
            item_total_price = item_data['quantity'] * item.item_price
            items[cart_key] = {
                'item_name': item.item_name,
                'price': item.item_price,
                'meal_type': item_data['meal_type'],
                'quantity': item_data['quantity'],
                'total_price': item_total_price,
                'image_url': item.item_image.url if item.item_image else '',  # Assuming your Item model has an image field
            }
            cart_total_amount += item_total_price
        except Http404:
            continue

    context = {
        'today_veg_lunch_menu_price': today_veg_lunch_menu,
        'today_nonveg_lunch_menu_price': today_nonveg_lunch_menu,
        'today_veg_dinner_menu_price': today_veg_dinner_menu,
        'today_nonveg_dinner_menu_price': today_nonveg_dinner_menu,
        'cart': items, 
        'cart_total_amount': cart_total_amount,
        "email_verified":email_verified,
    }
    return render(request, 'apps/home/view_cart.html', context)


@csrf_exempt
def save_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        customer_email = request.POST.get('customer_email')  
        payment_mode = request.POST.get('payment_mode', 'online') 
        order_id = generate_order_id()

        if pdf_file:
            order = Order.objects.create(
                order_id=order_id,
                pdf_invoice=pdf_file,
                customer_email=customer_email,
                payment_mode=payment_mode, 
            )

            request.session['order_id'] = order.order_id
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def generate_order_id():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]

def success_cart(request):
    order_id = request.session.get('order_id') 
    payment_id = request.POST.get('razorpay_payment_id') 
    context = {
        'order_id': order_id,
    }
    if order_id and payment_id:
        order = get_object_or_404(Order, order_id=order_id)
        order.payment_id = payment_id 
        order.payment_status = 'paid'  
        order.save()
        return render(request, 'apps/home/checkout_success.html', context)

    return render(request, 'apps/home/checkout_success.html', context)


def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    if order.pdf_invoice:
        with open(order.pdf_invoice.path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{order_id}_invoice.pdf"'
            return response
    else:
        return HttpResponse("No invoice found", status=404)


@csrf_exempt 
def checkout(request):
    if request.method == 'POST':
        total_amount = request.POST.get('total', 0)
        print(total_amount)
        
        try:
            total_amount = float(total_amount)
            request.session['total_amount'] = total_amount
            return JsonResponse({'status': 'success', 'message': 'Total received', 'total': total_amount})
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid total amount'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def razorpay_view(request):
    total_amount = request.session.get('total_amount', 0)
    print(total_amount)

    amountt = float(total_amount)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
    
    payment = client.order.create({
        'amount': int(amountt * 100), 
        'currency': 'INR',
        'payment_capture': 1 
    })
    context = {
        'payment': payment,
    }
    return render(request, 'apps/home/razorpay.html', context)