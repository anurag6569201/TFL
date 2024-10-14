from django.db import models
from django.contrib.auth import get_user_model
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

class TodayLunchMenu(models.Model):
    options = (
        ("veg","veg"),
        ("non_veg","non_veg"),
    )
    item_category=models.CharField(max_length=100,choices=options)
    items = models.ManyToManyField(Menu_Board_items, related_name='today_lunch_menu')
    price = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Menu for {self.date}"
    
class TodayDinnerMenu(models.Model):
    options = (
        ("veg","veg"),
        ("non_veg","non_veg"),
    )
    item_category=models.CharField(max_length=100,choices=options)
    items = models.ManyToManyField(Menu_Board_items, related_name='today_dinner_menu')
    price = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Menu for {self.date}"

class Scanner(models.Model):
    scanner_image = models.ImageField(upload_to='scanner/')

    def __str__(self):
        return "Scanner"


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    address_line1 = models.CharField(max_length=255,default="Address Line 1")
    city = models.CharField(max_length=100,default="City A")
    phone_number = models.CharField(max_length=15,default="9999900000")
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

    def __str__(self):
        return f"Order {self.order_id} - Payment {self.payment_id}"