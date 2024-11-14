from django.shortcuts import render
from .models import Item, LunchMenu, DinnerMenu, Scanner, DeliciousMenu,WeeklyMenu
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,Http404,HttpResponse
import razorpay
from django.conf import settings
import json
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order,Scanner
import uuid
from allauth.account.models import EmailAddress
from .forms import DeliveryAddressForm,ContactForm
from .models import DeliveryAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import datetime


def user_profile(request):
    user = request.user
    email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()

    try:
        addresses = user.delivery_addresses.all()
    except:
        addresses = None 

    # Handle POST requests for form submissions
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.user = request.user
            delivery_address.save()
            return redirect('home:user_profile')

    else:
        form = DeliveryAddressForm()

    # Handle address deletion
    if 'delete_address' in request.GET:
        address_id = request.GET.get('delete_address')
        address_to_delete = get_object_or_404(DeliveryAddress, id=address_id, user=user)
        address_to_delete.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('home:user_profile')

    # Handle setting primary address
    if 'set_primary' in request.GET:
        address_id = request.GET.get('set_primary')
        # Unset the previous primary address
        user.delivery_addresses.update(is_primary=False)
        address_to_set = get_object_or_404(DeliveryAddress, id=address_id, user=user)
        address_to_set.is_primary = True
        address_to_set.save()
        messages.success(request, 'Primary address set successfully.')
        return redirect('home:user_profile')

    context = {
        'user': user,
        'email_verified': email_verified,
        'form': form,
        'addresses': addresses,
    }
    return render(request, 'apps/home/user_profile.html', context)


def home(request):
    current_date = datetime.now()
    day_of_week_c = current_date.strftime("%A")
    formatted_date = current_date.strftime("%d-%m-%Y")

    print(day_of_week_c)
    cart = request.session.get('cart', {})
    request.session.modified = True
    
    scanner=Scanner.objects.first()

    lunch_add_ons = LunchMenu.objects.order_by('id').first()
    dinner_add_ons = DinnerMenu.objects.order_by('id').first()
    crousal_menu_items=DeliciousMenu.objects.order_by('id').first()

    today_veg_lunch_menu=WeeklyMenu.objects.order_by('id').filter(item_category="veg",meal_type='Lunch',day_of_week=day_of_week_c).first()
    today_nonveg_lunch_menu=WeeklyMenu.objects.order_by('id').filter(item_category="non_veg",meal_type='Lunch',day_of_week=day_of_week_c).first()

    today_veg_dinner_menu=WeeklyMenu.objects.order_by('id').filter(item_category="veg",meal_type='Dinner',day_of_week=day_of_week_c).first()
    today_nonveg_dinner_menu=WeeklyMenu.objects.order_by('id').filter(item_category="non_veg",meal_type='Dinner',day_of_week=day_of_week_c).first()

    user_email = request.user.email if request.user.is_authenticated else ''
    print(user_email)
    if request.method == 'POST':
        print("recieved POST request")
        form = ContactForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            print(user_message)

            subject = 'Query from User'
            email_template = 'apps/email/query.html'
            context = {
                'user_message': user_message,
                'user_email': user_email,
            }
            email_body = render_to_string(email_template, context)
            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [user_email])
            email.attach_alternative(email_body, "text/html")
            
            logo_path = os.path.join(settings.MEDIA_ROOT, 'scanner/tfl_logo.webp') 
            with open(logo_path, 'rb') as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header('Content-ID', '<logo_image>')
                email.attach(logo)

            email.send()
            print("Email sent")
            messages.success(request, 'Message sent successfully.')

    form = ContactForm()

    context = {
        'formatted_date':formatted_date,
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
        'scanner':scanner,
        'contactform':form,
    }
    return render(request, 'apps/home/index.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        meal_type = request.POST.get('meal_type') 
        quantity = int(request.POST.get('quantity', 1)) 
        item = get_object_or_404(Item, item_name=item_name)
        
        cart = request.session.get('cart', {})
        request.session.modified = True
        
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
        request.session.modified = True
        return JsonResponse({'success': True, 'cart': cart})
    
    return JsonResponse({'error': 'Invalid request method'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
def remove_from_cart(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        cart = request.session.get('cart', {})
        request.session.modified = True

        # Check if the item exists in the cart
        if item_name in cart:
            # Remove the item from the cart
            del cart[item_name]
            
            # Update the session with the modified cart
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({'success': True, 'cart': cart})
        
        return JsonResponse({'error': 'Item not found in cart'})
    
    return JsonResponse({'error': 'Invalid request method'})


def view_cart(request):
    try:
        user = request.user
        email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
    except:
        email_verified= False

    try:
        addresses = user.delivery_addresses.filter(is_primary=True).all()
    except AttributeError: 
        addresses = None
    current_date = datetime.now()
    day_of_week_c = current_date.strftime("%A")
    formatted_date = current_date.strftime("%d-%m-%Y")

    cart = request.session.get('cart', {})
    request.session.modified = True
    items = {}
    
    today_veg_lunch_menu=WeeklyMenu.objects.order_by('id').filter(item_category="veg",meal_type='Lunch',day_of_week=day_of_week_c).first()
    today_nonveg_lunch_menu=WeeklyMenu.objects.order_by('id').filter(item_category="non_veg",meal_type='Lunch',day_of_week=day_of_week_c).first()

    today_veg_dinner_menu=WeeklyMenu.objects.order_by('id').filter(item_category="veg",meal_type='Dinner',day_of_week=day_of_week_c).first()
    today_nonveg_dinner_menu=WeeklyMenu.objects.order_by('id').filter(item_category="non_veg",meal_type='Dinner',day_of_week=day_of_week_c).first()

    cart_total_amount = 0  

    for cart_key, item_data in cart.items():
        if item_data.get('quantity', 0) > 0:
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
        "addresses":addresses,
    }
    return render(request, 'apps/home/view_cart.html', context)


@csrf_exempt
def save_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        customer_email = request.POST.get('customer_email')  
        payment_mode = request.POST.get('payment_mode', 'online') 
        order_id = generate_order_id()

        user = request.user
        primary_address = user.delivery_addresses.filter(is_primary=True).first()

        if pdf_file:
            temp_pdf_path = save_temp_pdf(pdf_file)

            request.session['order_data'] = {
                'order_id': order_id,
                'customer_email': customer_email,
                'payment_mode': payment_mode,
                'pdf_path': temp_pdf_path,
                'delivery_address_id': primary_address.id
            }
            request.session.modified = True
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def save_pdf_offline(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        customer_email = request.POST.get('customer_email')  
        payment_mode = request.POST.get('payment_mode', 'cash') 
        order_id = generate_order_id()

        user = request.user
        primary_address = user.delivery_addresses.filter(is_primary=True).first()

        if pdf_file:
            temp_pdf_path = save_temp_pdf(pdf_file)

            request.session['order_data'] = {
                'order_id': order_id,
                'customer_email': customer_email,
                'payment_mode': payment_mode,
                'pdf_path': temp_pdf_path,
                'delivery_address_id': primary_address.id
            }
            request.session.modified = True
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})




import os
def save_temp_pdf(pdf_file):
    file_name = f"{str(uuid.uuid4())}.pdf"
    temp_path = os.path.join(settings.MEDIA_ROOT, 'tmp', file_name)
    with open(temp_path, 'wb+') as destination:
        for chunk in pdf_file.chunks():
            destination.write(chunk)
    return temp_path

def generate_order_id():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]


from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.core.files import File
def success_cart(request):
    order_data = request.session.get('order_data')
    request.session.modified = True
    payment_id = request.POST.get('razorpay_payment_id')

    order_id = order_data.get('order_id') if order_data else None
    delivery_otp = random.randint(100000, 999999)

    if order_data and payment_id:
        delivery_address = None
        if 'delivery_address_id' in order_data:
            try:
                delivery_address = DeliveryAddress.objects.get(id=order_data['delivery_address_id'])
            except DeliveryAddress.DoesNotExist:
                delivery_address = None

        order = Order.objects.create(
            order_id=order_data['order_id'],
            customer_email=order_data['customer_email'],
            payment_mode=order_data['payment_mode'],
            payment_id=payment_id,
            payment_status='paid',
            delivery_address=delivery_address,
            delivery_otp=delivery_otp
        )

        # Save the PDF invoice
        temp_pdf_path = order_data['pdf_path']
        with open(temp_pdf_path, 'rb') as temp_pdf_file:
            order.pdf_invoice.save(f"invoice_{order.order_id}.pdf", File(temp_pdf_file), save=True)

        # Prepare email details
        subject = 'Your Order Confirmation'
        email_template = 'apps/email/order_confirmation.html'
        context = {
            'order': order,
            'delivery_otp': delivery_otp,
            'delivery_address': delivery_address,
            'invoice_url': request.build_absolute_uri(order.pdf_invoice.url),  # Dynamic invoice URL
        }

        # Render the email body
        email_body = render_to_string(email_template, context)
        email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [order.customer_email])
        email.attach_alternative(email_body, "text/html")  # Attach HTML content

        # Attach the PDF invoice
        pdf_file_path = order.pdf_invoice.path
        email.attach_file(pdf_file_path)

        logo_path = os.path.join(settings.MEDIA_ROOT, 'scanner/tfl_logo.webp') 
        with open(logo_path, 'rb') as logo_file:
            logo = MIMEImage(logo_file.read())
            logo.add_header('Content-ID', '<logo_image>')
            email.attach(logo)

        # Send the email
        email.send()

        # Clean up session and temporary files
        del request.session['order_data']
        request.session.modified = True

        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

        context = {
            'delivery_otp': delivery_otp,
            'order_id': order.order_id,
        }

        return render(request, 'apps/home/checkout_success.html', context)

    context = {
        'order_id': order_id,
        'delivery_otp': delivery_otp,
    }
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
        
        try:
            total_amount = float(total_amount)
            request.session['total_amount'] = total_amount
            request.session.modified = True
            return JsonResponse({'status': 'success', 'message': 'Total received', 'total': total_amount})
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid total amount'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def razorpay_view(request):
    total_amount = request.session.get('total_amount', 0)
    request.session.modified = True

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


@login_required
def past_orders(request):
    past_orders = Order.objects.filter(customer_email=request.user.email).order_by('-created_at')
    context = {
        'past_orders': past_orders,
    }
    return render(request, 'apps/home/past_orders.html',context)



@login_required
@permission_required('home.can_change_order', raise_exception=True)
def delivery_page(request):
    # Fetch all pending orders
    scanner=Scanner.objects.first()
    pending_orders = Order.objects.filter(delivery_status='pending').select_related('delivery_address')

    context = {
        'pending_orders': pending_orders,
        'scanner':scanner,
    }
    return render(request, 'apps/home/delivery.html', context)







@login_required
@permission_required('home.can_change_order', raise_exception=True)
def verify_delivery_otp(request):
    if request.method == 'POST':
        entered_otp = int(request.POST.get('delivery_otp')) 
        try:
            order = get_object_or_404(Order, delivery_otp=entered_otp)
        except:
            response_data = {
                'status': 'failure',
                'message': 'Invalid OTP, please try again.'
            }
            return JsonResponse(response_data)

        if order.delivery_otp == entered_otp:
            # OTP verified, send delivery details
            response_data = {
                'status': 'success',
                'order_id': order.order_id,
                'customer_email': order.customer_email,
                'phone_number': order.delivery_address.phone_number,
                'address_line1': order.delivery_address.address_line1,
                'city': order.delivery_address.city,
                'payment_mode':order.payment_mode,
                'payment_status':order.payment_status,
                'delivery_status':order.delivery_status,
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'status': 'failure',
                'message': 'Invalid OTP, please try again.'
            }
            return JsonResponse(response_data)

    return render(request, 'apps/home/delivery.html')

@login_required
@permission_required('home.can_change_order', raise_exception=True)
def confirm_delivery(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, order_id=order_id)

        # Update order as delivered
        if order.payment_status == 'pending':
            order.payment_status = 'paid'
        order.delivery_status = 'delivered'
        order.save()
        current_datetime = datetime.now()
        # Send confirmation email
        subject = 'Your Order Has Been Delivered!'
        email_template = 'apps/email/order_delivery_confirmation.html'  # Email template
        context = {
            'order_id': order.order_id,
            'customer_email': order.customer_email,
            'delivery_address': order.delivery_address,
            'delivery_date':current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        }

        email_body = render_to_string(email_template, context)
        email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [order.customer_email])
        email.attach_alternative(email_body, "text/html")

        logo_path = os.path.join(settings.MEDIA_ROOT, 'scanner/tfl_logo.webp') 
        with open(logo_path, 'rb') as logo_file:
            logo = MIMEImage(logo_file.read())
            logo.add_header('Content-ID', '<logo_image>')
            email.attach(logo)

        email.send()

        return JsonResponse({'status': 'success', 'message': 'Delivery confirmed successfully!'})

    return render(request, 'apps/home/delivery.html')



def create_order(order_data):
    """ Helper function to create an order. """
    delivery_otp = random.randint(100000, 999999)
    return Order.objects.create(
        order_id=order_data['order_id'],
        customer_email=order_data['customer_email'],
        payment_status='pending',
        payment_mode=order_data['payment_mode'],
        delivery_address_id=order_data['delivery_address_id'],
        pdf_invoice=order_data['pdf_path'],
        delivery_otp=delivery_otp,
    )

def offline_payment_view(request):
    total_amount = request.session.get('total_amount', 0)
    order_data = request.session.get('order_data')
    request.session.modified = True
    order_id = order_data['order_id']

    # Retrieve the first scanner object (assuming this exists in your setup)
    scanner = Scanner.objects.first()

    return render(request, 'apps/home/offline_payment.html', {
        'scanner': scanner,
        'order_id': order_id,
        'total_amount': total_amount,
    })

def confirm_order_view(request, order_id):
    print(f"Order ID received: {order_id}")
    order_data = request.session.get('order_data')
    request.session.modified = True
    if request.method == 'POST':
        try:
            order = create_order(order_data)
            
            # Save PDF invoice
            temp_pdf_path = order_data['pdf_path']
            with open(temp_pdf_path, 'rb') as temp_pdf_file:
                order.pdf_invoice.save(f"invoice_{order.order_id}.pdf", File(temp_pdf_file), save=True)
            
            # Send confirmation email
            subject = 'Your Order Confirmation'
            email_template = 'apps/email/order_confirmation.html'
            context = {
                'order': order,
                'delivery_otp': order.delivery_otp,
                'delivery_address': order.delivery_address,
                'invoice_url': order.pdf_invoice.url,
            }
            email_body = render_to_string(email_template, context)
            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [order.customer_email])
            email.attach_alternative(email_body, "text/html")

            # Attach the PDF invoice
            email.attach_file(order.pdf_invoice.path)
            logo_path = os.path.join(settings.MEDIA_ROOT, 'scanner/tfl_logo.webp') 
            with open(logo_path, 'rb') as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header('Content-ID', '<logo_image>')
                email.attach(logo)

            email.send()
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

            return JsonResponse({'success': True, 'message': 'Order confirmed successfully.'})

        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found.'})
    

def cancel_order_view(request):
    # Redirect to the cart page and remove session data related to the order
    if 'order_data' in request.session:
        del request.session['order_data']
        request.session.modified = True
    return redirect('cart:cart_page')




@csrf_exempt  # Only if you're using POST and not handling CSRF in headers
def update_cart_badge(request):
    if request.method == 'POST':
        item_count = request.POST.get('item_count', 0)
        # Perform necessary actions with the item_count
        return JsonResponse({'item_count': item_count})

    return JsonResponse({'error': 'Invalid request'}, status=400)