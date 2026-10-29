from django.db import models

class User(models.Model):
    ROLE_CHOICES = (('customer', 'Customer'), ('admin', 'Admin'))
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='category_id')
    image_url = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.50)
    reviews_count = models.IntegerField(default=0)
    stock = models.IntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'carts'
        unique_together = ('user', 'product')


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.RESTRICT, db_column='user_id')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, default='Stripe')
    payment_status = models.CharField(max_length=30, default='Paid')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, db_column='product_id')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
