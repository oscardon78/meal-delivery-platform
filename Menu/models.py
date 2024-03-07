from django.db import models
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Restaurant(models.Model):
    name=models.CharField( max_length=50)
    address=models.CharField(max_length=150)
    description=models.CharField(max_length=200,null=True,blank=True)
    rating=models.FloatField()
    image=models.ImageField(upload_to='restaurant_images')
    def __str__(self):
        return self.name

class Category(models.Model):
    catagory=models.CharField(max_length=50)
    def __str__(self):
        return self.catagory

class Food(models.Model):
    restaurant=models.ForeignKey(Restaurant,related_name='restaurant_name',on_delete=models.CASCADE)
    name=models.CharField(max_length=50)
    catagory=models.ForeignKey(Category,related_name='category',on_delete=models.CASCADE)
    cost=models.FloatField()
    image=models.ImageField(upload_to='food_images')
    def __str__(self):
        return self.name

class OrderInfo(models.Model):
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=250, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    # Add more fields as needed (e.g., order_date, notes)

class Orders(models.Model):
    order_info = models.ForeignKey(OrderInfo, related_name='orders', on_delete=models.CASCADE)
    foods = models.ManyToManyField(Food, related_name='orders', through='OrderItem')
    total = models.FloatField(default=0)
    date_created=models.DateField(auto_now=False, auto_now_add=True)
    status=models.CharField(max_length=10,default='Pending')
    def __str__(self):
        return f"Order {self.id}"

    def calculate_total(self):
        total = sum(item.calculate_item_total() for item in self.order_items.all())
        self.total = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Orders, related_name='order_items', on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.food.name} - {self.quantity}"

    def calculate_item_total(self):
        return self.food.cost * self.quantity

    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Food, through='CartItem')
    total = models.FloatField(default=0)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def cart_total(self):
        total = round(sum(item.cart_item_total() for item in self.cart_items.all()),2)
        if self.total != total:  # Check if the total has changed
            self.total = total
            self.save()  # Save the Cart instance only if the total has changed
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cart_items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    def cart_item_total(self):
        return self.food.cost * self.quantity