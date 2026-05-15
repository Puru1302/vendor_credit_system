from django.contrib import admin
from .models import Vendor, Purchase, PurchaseItem, Payment, Item, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'phone', 'category', 'payment_terms', 'is_active']
    list_filter = ['category', 'is_active', 'payment_terms']
    search_fields = ['name', 'company_name', 'phone', 'gstin']


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'vendor', 'purchase_date', 'total_amount', 'payment_status']
    list_filter = ['payment_status', 'gst_rate']
    search_fields = ['invoice_number', 'vendor__name']
    inlines = [PurchaseItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'payment_date', 'payment_mode', 'reference_number']
    list_filter = ['payment_mode']
    search_fields = ['vendor__name', 'reference_number']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'default_gst_rate', 'selling_price', 'is_active']
    list_filter = ['category', 'default_gst_rate', 'is_active']
    search_fields = ['name']