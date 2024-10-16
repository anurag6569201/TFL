from django.urls import path
from home import views
from .views import save_pdf, download_invoice
from django.views.generic import TemplateView


app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('save-pdf/', save_pdf, name='save_pdf'),
    path('save-pdf/offline/', views.save_pdf_offline, name='save_pdf_offline'),
    path('cart/success/', views.success_cart, name='success_cart'),
    path('download-invoice/<str:order_id>/', download_invoice, name='download_invoice'), 
    path('checkout/', views.checkout, name='checkout'), 
    path('razorpay/', views.razorpay_view, name='razorpay'), 
    path('profile/', views.user_profile, name='user_profile'),
    path('past_orders/', views.past_orders, name='past_orders'),
    path('delivery/', views.delivery_page, name='delivery_page'),
    path('verify-delivery-otp/', views.verify_delivery_otp, name='verify_delivery_otp'),
    path('offline-payment/', views.offline_payment_view, name='offline_payment'),
    path('confirm-order/<str:order_id>/', views.confirm_order_view, name='confirm_order'),
    path('cancel-order/<str:order_id>/', views.cancel_order_view, name='cancel_order'),
]
