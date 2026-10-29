from django.contrib import admin
from .models import User, Category, Product, Cart, Order, OrderItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'is_blocked', 'created_at')
    list_filter = ('role', 'is_blocked')
    search_fields = ('name', 'email')
    actions = ['block_users', 'unblock_users']

    @admin.action(description='Block selected users')
    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description='Unblock selected users')
    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'rating')
    list_filter = ('category',)
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    inlines = [OrderItemInline]
