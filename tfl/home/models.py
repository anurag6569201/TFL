from django.db import models

# Reusable item model for both lunch and dinner
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

# Lunch menu, referring to items
class LunchMenu(models.Model):
    items = models.ManyToManyField(Item, related_name='lunch_menus')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Lunch Menu {self.id}"

# Dinner menu, referring to items
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

# Today's menu combining lunch and dinner
class TodayLunchMenu(models.Model):
    options = (
        ("veg","veg"),
        ("non_veg","non_veg"),
    )
    item_category=models.CharField(max_length=100,choices=options)
    items = models.ManyToManyField(Menu_Board_items, related_name='today_lunch_menu')
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
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Menu for {self.date}"

# Scanner model, as needed for QR code or similar
class Scanner(models.Model):
    scanner_image = models.ImageField(upload_to='scanner/')

    def __str__(self):
        return "Scanner"
