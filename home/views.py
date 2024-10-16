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
from .forms import DeliveryAddressForm
from .models import DeliveryAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

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
    try:
        user = request.user
        email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
    except:
        email_verified= False

    try:
        addresses = user.delivery_addresses.filter(is_primary=True).all()
    except AttributeError: 
        addresses = None

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

        # Attach logo if it exists
        logo_path = os.path.join(settings.STATIC_ROOT, 'img/home', 'tfl_logo.webp')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_image = MIMEImage(logo_file.read())
                logo_image.add_header('Content-ID', '<logo_image>')
                logo_image.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_path))
                email.attach(logo_image)

        # Send the email
        email.send()

        # Clean up session and temporary files
        del request.session['order_data']

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
    pending_orders = Order.objects.order_by('-created_at').filter(delivery_status='pending').select_related('delivery_address')

    context = {
        'pending_orders': pending_orders,
    }
    return render(request, 'apps/home/delivery.html', context)


@login_required
@permission_required('home.can_change_order', raise_exception=True)
def verify_delivery_otp(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        entered_otp = int(request.POST.get('delivery_otp')) 
        order = get_object_or_404(Order, order_id=order_id)

        if order.delivery_otp == entered_otp:
            if order.payment_status=="pending":
                order.payment_status = 'paid'
                order.save()
                
            order.delivery_status = 'delivered'
            order.save()

            subject = 'Your Order Has Been Delivered!'
            email_template = 'apps/email/order_delivery_confirmation.html'  # Path to the HTML email template
            context = {
                'order_id': order.order_id,
                'customer_email': order.customer_email,
                'delivery_address': order.delivery_address,
            }
            
            email_body = render_to_string(email_template, context)
            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [order.customer_email])
            email.attach_alternative(email_body, "text/html")

            logo_path = os.path.join(settings.STATIC_ROOT, 'img/home', 'tfl_logo.webp')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as logo_file:
                    logo_image = MIMEImage(logo_file.read())
                    logo_image.add_header('Content-ID', '<logo_image>')
                    logo_image.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_path))
                    email.attach(logo_image)

            email.send()

            return JsonResponse({'status': 'success', 'message': 'OTP verified, order delivered!'})

        else:
            return JsonResponse({'status': 'failure', 'message': 'Invalid OTP, please try again.'})

    return render(request, 'apps/home/delivery.html')





from datetime import timedelta
def create_order(order_data):
    """ Helper function to create an order. """
    delivery_otp = random.randint(100000, 999999)
    expiration_time = timezone.now() + timedelta(minutes=2) 
    return Order.objects.create(
        order_id=order_data['order_id'],
        customer_email=order_data['customer_email'],
        payment_status='pending',
        payment_mode=order_data['payment_mode'],
        delivery_address_id=order_data['delivery_address_id'],
        pdf_invoice=order_data['pdf_path'],
        delivery_otp=delivery_otp,
        expiration_time=expiration_time,
    )

def offline_payment_view(request):
    order_data = request.session.get('order_data')
    total_amount = request.session.get('total_amount', 0)

    if not order_data:
        return redirect('home:view_cart')

    # Create the order and set its expiration time
    order = create_order(order_data)
    temp_pdf_path = order_data['pdf_path']
    with open(temp_pdf_path, 'rb') as temp_pdf_file:
        order.pdf_invoice.save(f"invoice_{order.order_id}.pdf", File(temp_pdf_file), save=True)

    scanner = Scanner.objects.first()

    return render(request, 'apps/home/offline_payment.html', {
        'order': order,
        'scanner': scanner,
        'total_amount': total_amount,
    })
from django.utils import timezone
def cancel_order_view(request, order_id):
    try:
        order = get_object_or_404(Order, order_id=order_id)
        if order.expiration_time and timezone.now() < order.expiration_time:
            if order.payment_status == 'pending':
                order.delete()  # Delete the order
                return JsonResponse({'success': True, 'message': 'Order canceled successfully.'})
            else:
                return JsonResponse({'success': False, 'error': 'Order is already processed.'})
        else:
            return JsonResponse({'success': False, 'error': 'The 2-minute cancel window has passed.'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found.'})



def confirm_order_view(request, order_id):
    try:
        order = get_object_or_404(Order, order_id=order_id)

        if order.payment_status == 'pending' and not order.is_expired():

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
            pdf_file_path = order.pdf_invoice.path
            email.attach_file(pdf_file_path)

            email.send()

            return JsonResponse({'success': True, 'message': 'Order confirmed successfully.'})
        else:
            return JsonResponse({'success': False, 'error': 'Order is already processed or expired.'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found.'})