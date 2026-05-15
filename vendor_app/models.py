from django.db import models
from django.utils import timezone
from decimal import Decimal
import math


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Vendor(models.Model):
    PAYMENT_TERMS = [
        ('7', '7 Days'),
        ('15', '15 Days'),
        ('30', '30 Days'),
        ('45', '45 Days'),
        ('60', '60 Days'),
        ('0', 'Immediate'),
    ]

    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True, verbose_name="GSTIN")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    payment_terms = models.CharField(max_length=5, choices=PAYMENT_TERMS, default='30')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company_name})" if self.company_name else self.name

    @property
    def total_purchases(self):
        return self.purchase_set.aggregate(
            total=models.Sum('total_amount'))['total'] or Decimal('0')

    @property
    def total_paid(self):
        return self.payment_set.aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')

    @property
    def outstanding_balance(self):
        return self.total_purchases - self.total_paid

    @property
    def risk_score(self):
        """AI-like Risk Vendor Score (0–100)"""
        score = 0
        purchases = self.purchase_set.filter(payment_status__in=['pending', 'partial'])

        # Factor 1: Overdue days (max 40 pts)
        overdue_purchases = [p for p in purchases if p.days_overdue > 0]
        if overdue_purchases:
            avg_overdue = sum(p.days_overdue for p in overdue_purchases) / len(overdue_purchases)
            score += min(40, avg_overdue * 1.5)

        # Factor 2: Outstanding ratio vs credit limit (max 25 pts)
        if self.credit_limit > 0:
            ratio = float(self.outstanding_balance) / float(self.credit_limit)
            score += min(25, ratio * 25)

        # Factor 3: Pending count (max 20 pts)
        pending_count = purchases.count()
        score += min(20, pending_count * 4)

        # Factor 4: Payment frequency (max 15 pts)
        total = self.purchase_set.count()
        paid = self.purchase_set.filter(payment_status='paid').count()
        if total > 0:
            unpaid_ratio = 1 - (paid / total)
            score += unpaid_ratio * 15

        return round(min(100, score))

    @property
    def risk_level(self):
        score = self.risk_score
        if score <= 30:
            return 'LOW'
        elif score <= 60:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def predict_next_payment(self):
        """Predict next payment date based on payment history"""
        payments = self.payment_set.order_by('payment_date')
        if payments.count() < 2:
            terms = int(self.payment_terms) if self.payment_terms != '0' else 7
            return timezone.now().date() + timezone.timedelta(days=terms)

        # Average days between payments
        dates = list(payments.values_list('payment_date', flat=True))
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps)
        last_payment = dates[-1]
        return last_payment + timezone.timedelta(days=avg_gap)


class Item(models.Model):
    GST_CHOICES = [
        ('0', '0%'),
        ('5', '5%'),
        ('12', '12%'),
        ('18', '18%'),
        ('28', '28%'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=20, default='piece')
    default_gst_rate = models.CharField(max_length=3, choices=GST_CHOICES, default='18')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        help_text="MRP / Selling price for profit calc")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    GST_CHOICES = [
        ('0', '0%'), ('5', '5%'), ('12', '12%'), ('18', '18%'), ('28', '28%'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.CharField(max_length=3, choices=GST_CHOICES, default='18')
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"INV-{self.invoice_number} | {self.vendor.name}"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    @property
    def days_overdue(self):
        if self.due_date and self.payment_status != 'paid':
            delta = (timezone.now().date() - self.due_date).days
            return max(0, delta)
        return 0

    def save(self, *args, **kwargs):
        # Auto-calculate GST and total
        rate = Decimal(self.gst_rate) / 100
        self.gst_amount = self.subtotal * rate
        self.total_amount = self.subtotal + self.gst_amount

        # Auto due date from vendor terms
        if not self.due_date and self.vendor_id:
            try:
                vendor = Vendor.objects.get(pk=self.vendor_id)
                terms = int(vendor.payment_terms)
                self.due_date = self.purchase_date + timezone.timedelta(days=terms)
            except Vendor.DoesNotExist:
                pass

        # Auto update payment status
        if self.amount_paid >= self.total_amount:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'

        super().save(*args, **kwargs)


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=20, default='piece')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.CharField(max_length=3, default='18')
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    @property
    def estimated_profit(self):
        if self.item and self.item.selling_price > 0:
            revenue = self.quantity * self.item.selling_price
            cost = self.line_total
            return revenue - cost
        return Decimal('0')


class Payment(models.Model):
    PAYMENT_MODES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='bank_transfer')
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment ₹{self.amount} to {self.vendor.name} on {self.payment_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update purchase amount_paid
        if self.purchase:
            total_paid = Payment.objects.filter(
                purchase=self.purchase).aggregate(
                total=models.Sum('amount'))['total'] or 0
            self.purchase.amount_paid = total_paid
            self.purchase.save()