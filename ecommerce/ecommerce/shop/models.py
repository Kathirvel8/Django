from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount = models.FloatField()
    thumbnail = models.URLField()
    quantity = models.PositiveIntegerField(default=1)

    def final_price(self):
        return self.price - (self.price * self.discount/100)