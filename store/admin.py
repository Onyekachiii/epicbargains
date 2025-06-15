from django.contrib import admin
from store import models as store_models
from .models import Order, OrderItem
from django.utils.html import format_html


admin.site.site_header = "EpicBargains"
admin.site.site_title = "EpicBargains"
admin.site.index_title = "Welcome to EpicBargains Dashboard"

class GalleryInline(admin.TabularInline):
    model = store_models.Gallery

class VariantInline(admin.TabularInline):
    model = store_models.Variant

class VariantItemInline(admin.TabularInline):
    model = store_models.VariantItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image']
    list_editable = ['image']
    prepopulated_fields = {'slug': ('title',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'regular_price', 'stock', 'status', 'featured', 'date']
    search_fields = ['name', 'category__title']
    list_filter = ['status', 'featured', 'category']
    inlines = [GalleryInline, VariantInline]
    prepopulated_fields = {'slug': ('name',)}

class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    search_fields = ['product__name', 'name']
    inlines = [VariantItemInline]
    
class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'content']
    search_fields = ['variant__name', 'title']

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product', 'gallery_id']
    search_fields = ['product__name', 'gallery_id']

class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'product', 'user', 'qty', 'price', 'total', 'date']
    search_fields = ['cart_id', 'product__name', 'user__username']
    list_filter = ['date', 'product']

    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0



class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'get_customer_name', 'get_customer_phone',
        'total', 'payment_status', 'order_status', 'get_payment_method',
        'receipt_uploaded', 'date'
    ]
    list_editable = ['payment_status', 'order_status']
    search_fields = ['order_id', 'full_name', 'email', 'phone']
    list_filter = ['payment_status', 'order_status', 'payment_method', 'date']
    inlines = [OrderItemInline]

    def get_customer_name(self, obj):
        return obj.full_name or "-"
    get_customer_name.short_description = 'Customer Name'

    def get_customer_phone(self, obj):
        return obj.phone or "-"
    get_customer_phone.short_description = 'Phone Number'

    def get_payment_method(self, obj):
        return obj.get_payment_method_display() if obj.payment_method else "-"
    get_payment_method.short_description = "Payment Method"

    def receipt_uploaded(self, obj):
        if obj.bank_receipt:
            return format_html('<a href="{}" target="_blank">View Receipt</a>', obj.bank_receipt.url)
        return "No"
    receipt_uploaded.short_description = "Bank Receipt"

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'order', 'product', 'qty', 'price', 'total']
    search_fields = ['item_id', 'order__order_id', 'product__name']
    list_filter = ['order__date']
    

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'active', 'date']
    search_fields = ['user__username', 'product__name']
    list_filter = ['active', 'rating']

admin.site.register(store_models.Category, CategoryAdmin)
admin.site.register(store_models.Product, ProductAdmin)
admin.site.register(store_models.Variant, VariantAdmin)
admin.site.register(store_models.VariantItem, VariantItemAdmin)
admin.site.register(store_models.Gallery, GalleryAdmin)
admin.site.register(store_models.Cart, CartAdmin)
admin.site.register(store_models.Order, OrderAdmin)
admin.site.register(store_models.OrderItem, OrderItemAdmin)
admin.site.register(store_models.Review, ReviewAdmin)
