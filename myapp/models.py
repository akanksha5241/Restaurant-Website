from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class User(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'customer'),
        ('manager', 'manager'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES,default='customer')
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=90,default='')
    email=models.EmailField()
    mobile=models.PositiveIntegerField()
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=50)
    pincode=models.PositiveIntegerField()
    password=models.CharField(max_length=12)
    profile_pic=models.ImageField(upload_to="profile_pic/")

    def __str__(self):
        return self.fname
	
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Menu(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='food_images/')
    price1 = models.DecimalField(max_digits=8, decimal_places=2)
    price2 = models.DecimalField(max_digits=8, decimal_places=2)
    # inventory_item = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.category}"
    
class Cart(models.Model):
    food_item=models.ForeignKey(Menu,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)
    time = models.TimeField(default=datetime.now)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} - {self.user.fname} ({self.date})"
    
class Leave_A_Comment(models.Model):
    name = models.CharField(max_length=100)
    email=models.EmailField()
    message = models.TextField(max_length=100)

    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    name=models.CharField(max_length=90,default='')
    email=models.EmailField()
    mobile=models.PositiveIntegerField()
    person=models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=datetime.now)
    message = models.TextField(max_length=100)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    rating = models.IntegerField(choices=[
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ])
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.rating}"
    

class Wishlist(models.Model):
    food_item=models.ForeignKey(Menu,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)
    time = models.TimeField(default=datetime.now)

    def __str__(self):
        return self.user.fname+" - "+self.food_item.name

class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=100)
    profile_pic=models.ImageField(upload_to="profile_pic/")

    def __str__(self):
        return self.name
                            
class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class MyOrder(models.Model):
    food_item = models.ForeignKey(InventoryItem, on_delete=models.SET_DEFAULT, default=2)
    ordered_quantity = models.PositiveIntegerField()  # ✅ renamed to avoid conflict

    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=90)
    email = models.EmailField()
    phone = models.PositiveIntegerField(null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    pincode = models.PositiveIntegerField()

    food_item_name = models.CharField(max_length=255)
    price = models.CharField(max_length=400)
    quantity = models.CharField(max_length=400)  # You can rename or remove this if unnecessary

    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=40)
    date = models.DateField(default=datetime.today)
    time = models.TimeField(default=datetime.now)

    delivery_person = models.ForeignKey(DeliveryPerson, null=True, blank=True, on_delete=models.SET_NULL)

    status_choices = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='PENDING')

    def __str__(self):
        return f"{self.fname} - {self.date} x {self.time}"




@receiver(post_save, sender=MyOrder)
def update_inventory(sender, instance, **kwargs):
    """ Updates inventory when an order is placed """

    # 🔍 Check if food_item exists
    if not instance.food_item_id:
        print(f"⚠ Warning: No linked inventory item for '{instance.food_item_name}'. No update performed.")
        return

    # Fetch the InventoryItem object directly
    item = InventoryItem.objects.filter(id=instance.food_item_id).first()
    
    if not item:
        print(f"⚠ Warning: Inventory item '{instance.food_item_name}' (ID: {instance.food_item_id}) not found. No update performed.")
        return

    print(f"🔹 Updating Inventory for: {item.name}, Current Stock: {item.quantity}")

    try:
        # Ensure quantity is a valid integer
        ordered_quantity = instance.quantity

        # If `quantity` is a list, extract the first value
        if isinstance(ordered_quantity, list):
            ordered_quantity = ordered_quantity[0]

        # Convert to integer
        ordered_quantity = int(ordered_quantity)

        # 🛑 Prevent negative stock
        if item.quantity < ordered_quantity:
            print(f"⚠ Warning: Not enough stock for {item.name}. Order: {ordered_quantity}, Available: {item.quantity}")
            return

        # ✅ Reduce inventory
        item.quantity -= ordered_quantity
        item.save()
        print(f"✅ Updated Inventory: {item.name}, New Stock: {item.quantity}")

        # 🚨 Send alert if inventory is low
        if item.quantity <= 5:
            send_mail(
                '⚠ Low Inventory Alert!',
                f'Inventory for {item.name} is running low (Only {item.quantity} left). Please restock!',
                'admin@example.com',
                ['manager@example.com'],
                fail_silently=False,
            )
            print(f"📧 Low stock alert sent for {item.name}")

    except ValueError:
        print(f"❌ Error: Invalid quantity '{instance.quantity}'")
