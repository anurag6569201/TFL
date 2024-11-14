from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()


class Item(models.Model):
    item_image = models.ImageField(upload_to='items/')
    item_name = models.CharField(max_length=100)
    item_description = models.TextField()
    item_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.item_name
    
class Menu_Board_items(models.Model):
    item_name = models.CharField(max_length=100)
    def __str__(self):
        return self.item_name

class LunchMenu(models.Model):
    items = models.ManyToManyField(Item, related_name='lunch_menus')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Lunch Menu {self.id}"

class DinnerMenu(models.Model):
    items = models.ManyToManyField(Item, related_name='dinner_menus')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Dinner Menu {self.id}"
    
class DeliciousMenu(models.Model):
    items = models.ManyToManyField(Item, related_name='delicious_menus')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Dinner Menu {self.id}"

class WeeklyMenu(models.Model):
    DAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    MEAL_CHOICES = [
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
    ]

    CATEGORY_CHOICES = [
        ("veg", "veg"),
        ("non_veg", "non_veg"),
    ]

    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    item_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    items = models.ManyToManyField(Menu_Board_items, related_name='weekly_menu')
    price = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal_type} Menu for {self.day_of_week} ({self.date})"


class Scanner(models.Model):
    scanner_image = models.ImageField(upload_to='scanner/')

    def __str__(self):
        return "Scanner"


class DeliveryAddress(models.Model):
    ADDRESS_CHOICES = [
        ('IIIT', 'IIIT'),
        ('STPI', 'STPI'),
        ('KIIT', 'KIIT'),
    ]
    
    CITY_CHOICES = [
        ('Bhubaneswar', 'Bhubaneswar'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    address_line1 = models.CharField(max_length=255, choices=ADDRESS_CHOICES, default='IIIT')
    city = models.CharField(max_length=100, choices=CITY_CHOICES, default='Bhubaneswar')
    phone_number = models.CharField(max_length=10, default='XXXXXXXXXX')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.address_line1}, {self.city}"
    

class Order(models.Model):
    order_id = models.CharField(max_length=12, unique=True, blank=True, null=True)
    payment_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    pdf_invoice = models.FileField(upload_to='invoices/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    payment_mode = models.CharField(max_length=10, choices=[('online', 'Online'), ('cash', 'Cash')], default='online')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_otp = models.IntegerField(default=0, null=True, blank=True)
    delivery_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('delivered', 'Delivered')], default='pending')

    expiration_time = models.DateTimeField(null=True, blank=True)  # New expiration field

    def is_expired(self):
        """Check if the order has expired."""
        if self.expiration_time and timezone.now() > self.expiration_time:
            return True
        return False
    
    def __str__(self):
        return f"Order {self.order_id} - Payment {self.payment_id}"