from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
import json
import csv
import io
from datetime import datetime, timedelta

from .models import Vendor, Purchase, PurchaseItem, Payment, Item, Category
from .forms import VendorForm, PurchaseForm, PurchaseItemFormSet, PaymentForm, ItemForm


# ─── Dashboard ──────────────────────────────────────────────
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Summary cards
    total_vendors = Vendor.objects.filter(is_active=True).count()
    monthly_purchases = Purchase.objects.filter(
        purchase_date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    total_outstanding = sum(
        v.outstanding_balance for v in Vendor.objects.filter(is_active=True)
    )

    overdue_count = Purchase.objects.filter(
        payment_status__in=['pending', 'partial'],
        due_date__lt=today
    ).count()

    # Today's purchases
    today_purchases = Purchase.objects.filter(purchase_date=today).select_related('vendor')

    # Risk alerts (high risk vendors)
    all_vendors = Vendor.objects.filter(is_active=True).prefetch_related('purchase_set', 'payment_set')
    high_risk = [v for v in all_vendors if v.risk_level == 'HIGH'][:5]

    # Monthly trend (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_data = Purchase.objects.filter(
        purchase_date__gte=six_months_ago
    ).annotate(month=TruncMonth('purchase_date')).values('month').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')

    monthly_labels = [m['month'].strftime('%b %Y') for m in monthly_data]
    monthly_totals = [float(m['total']) for m in monthly_data]

    # Category-wise purchases
    cat_data = PurchaseItem.objects.values(
        'item__category__name'
    ).annotate(total=Sum('line_total')).order_by('-total')[:6]

    # Pending reminders
    reminders = Purchase.objects.filter(
        payment_status__in=['pending', 'partial'],
        due_date__lte=today + timedelta(days=7)
    ).select_related('vendor').order_by('due_date')[:10]

    # Profit estimation
    profit_items = PurchaseItem.objects.filter(item__isnull=False)
    total_estimated_profit = sum(p.estimated_profit for p in profit_items)

    context = {
        'total_vendors': total_vendors,
        'monthly_purchases': monthly_purchases,
        'total_outstanding': total_outstanding,
        'overdue_count': overdue_count,
        'today_purchases': today_purchases,
        'high_risk_vendors': high_risk,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_totals': json.dumps(monthly_totals),
        'cat_data': list(cat_data),
        'reminders': reminders,
        'total_estimated_profit': total_estimated_profit,
        'today': today,
    }
    return render(request, 'vendor_app/dashboard.html', context)


# ─── Vendor CRUD ────────────────────────────────────────────
def vendor_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    risk = request.GET.get('risk', '')

    vendors = Vendor.objects.filter(is_active=True).select_related('category').prefetch_related('purchase_set', 'payment_set')

    if query:
        vendors = vendors.filter(
            Q(name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(gstin__icontains=query)
        )
    if category:
        vendors = vendors.filter(category__id=category)

    # Annotate risk — done in Python
    vendor_list_data = []
    for v in vendors:
        if risk and v.risk_level != risk:
            continue
        vendor_list_data.append(v)

    categories = Category.objects.all()
    return render(request, 'vendor_app/vendor_list.html', {
        'vendors': vendor_list_data,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_risk': risk,
    })


def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" added successfully!')
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm()
    return render(request, 'vendor_app/vendor_form.html', {'form': form, 'title': 'Add Vendor'})


def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor updated!')
            return redirect('vendor_detail', pk=pk)
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'vendor_app/vendor_form.html', {'form': form, 'title': 'Edit Vendor', 'vendor': vendor})


def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    purchases = vendor.purchase_set.all().order_by('-purchase_date')
    payments = vendor.payment_set.all().order_by('-payment_date')

    # Monthly purchases chart for this vendor
    monthly = purchases.annotate(month=TruncMonth('purchase_date')).values('month').annotate(
        total=Sum('total_amount')).order_by('month')

    context = {
        'vendor': vendor,
        'purchases': purchases,
        'payments': payments,
        'monthly_labels': json.dumps([m['month'].strftime('%b %Y') for m in monthly]),
        'monthly_totals': json.dumps([float(m['total']) for m in monthly]),
        'predicted_payment': vendor.predict_next_payment(),
    }
    return render(request, 'vendor_app/vendor_detail.html', context)


def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.is_active = False
        vendor.save()
        messages.success(request, f'Vendor "{vendor.name}" deactivated.')
        return redirect('vendor_list')
    return render(request, 'vendor_app/confirm_delete.html', {'object': vendor, 'type': 'Vendor'})


# ─── Purchase CRUD ──────────────────────────────────────────
def purchase_list(request):
    status = request.GET.get('status', '')
    vendor_id = request.GET.get('vendor', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    purchases = Purchase.objects.select_related('vendor').order_by('-purchase_date')

    if status:
        purchases = purchases.filter(payment_status=status)
    if vendor_id:
        purchases = purchases.filter(vendor__id=vendor_id)
    if date_from:
        purchases = purchases.filter(purchase_date__gte=date_from)
    if date_to:
        purchases = purchases.filter(purchase_date__lte=date_to)

    vendors = Vendor.objects.filter(is_active=True)
    return render(request, 'vendor_app/purchase_list.html', {
        'purchases': purchases,
        'vendors': vendors,
        'status': status,
        'vendor_id': vendor_id,
    })


def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            messages.success(request, f'Purchase {purchase.invoice_number} added!')
            return redirect('purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseForm()
    return render(request, 'vendor_app/purchase_form.html', {'form': form, 'title': 'New Purchase'})


def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    items = purchase.items.select_related('item')
    payments = Payment.objects.filter(purchase=purchase)
    return render(request, 'vendor_app/purchase_detail.html', {
        'purchase': purchase,
        'items': items,
        'payments': payments,
    })


def purchase_edit(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase updated!')
            return redirect('purchase_detail', pk=pk)
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, 'vendor_app/purchase_form.html', {'form': form, 'title': 'Edit Purchase', 'purchase': purchase})


# ─── Payment ────────────────────────────────────────────────
def payment_create(request, purchase_pk=None):
    purchase = None
    if purchase_pk:
        purchase = get_object_or_404(Purchase, pk=purchase_pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment of ₹{payment.amount} recorded!')
            if purchase:
                return redirect('purchase_detail', pk=purchase.pk)
            return redirect('vendor_detail', pk=payment.vendor.pk)
    else:
        initial = {}
        if purchase:
            initial = {'vendor': purchase.vendor, 'purchase': purchase, 'amount': purchase.balance_due}
        form = PaymentForm(initial=initial)

    return render(request, 'vendor_app/payment_form.html', {'form': form, 'purchase': purchase})


# ─── Analytics ──────────────────────────────────────────────
def analytics(request):
    today = timezone.now().date()

    # Last 12 months data
    twelve_months_ago = today - timedelta(days=365)

    monthly = Purchase.objects.filter(
        purchase_date__gte=twelve_months_ago
    ).annotate(month=TruncMonth('purchase_date')).values('month').annotate(
        purchases=Sum('total_amount'),
        gst=Sum('gst_amount'),
        count=Count('id')
    ).order_by('month')

    # Payment mode breakdown
    payment_modes = Payment.objects.values('payment_mode').annotate(
        total=Sum('amount'), count=Count('id')
    )

    # Top vendors by purchase
    top_vendors = Vendor.objects.filter(is_active=True).annotate(
        total=Sum('purchase__total_amount')
    ).filter(total__isnull=False).order_by('-total')[:10]

    # Category wise
    cat_wise = PurchaseItem.objects.values(
        'item__category__name'
    ).annotate(total=Sum('line_total'), count=Count('id')).order_by('-total')

    # GST summary
    gst_total = Purchase.objects.aggregate(total=Sum('gst_amount'))['total'] or 0

    context = {
        'monthly_labels': json.dumps([m['month'].strftime('%b %Y') for m in monthly]),
        'monthly_purchases': json.dumps([float(m['purchases']) for m in monthly]),
        'monthly_gst': json.dumps([float(m['gst']) for m in monthly]),
        'payment_modes': list(payment_modes),
        'top_vendors': top_vendors,
        'cat_wise': list(cat_wise),
        'gst_total': gst_total,
    }
    return render(request, 'vendor_app/analytics.html', context)


# ─── Export CSV ─────────────────────────────────────────────
def export_purchases_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchases_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice No', 'Vendor', 'Date', 'Due Date', 'Subtotal',
                     'GST Rate', 'GST Amount', 'Total', 'Paid', 'Balance', 'Status'])

    for p in Purchase.objects.select_related('vendor').order_by('-purchase_date'):
        writer.writerow([
            p.invoice_number, p.vendor.name, p.purchase_date,
            p.due_date, p.subtotal, f"{p.gst_rate}%",
            p.gst_amount, p.total_amount, p.amount_paid,
            p.balance_due, p.get_payment_status_display()
        ])

    return response


def export_vendors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendors_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Company', 'Phone', 'Email', 'GSTIN',
                     'Category', 'Payment Terms', 'Total Purchases',
                     'Total Paid', 'Outstanding', 'Risk Score', 'Risk Level'])

    for v in Vendor.objects.filter(is_active=True).select_related('category'):
        writer.writerow([
            v.name, v.company_name, v.phone, v.email, v.gstin,
            v.category.name if v.category else '',
            f"{v.payment_terms} days", v.total_purchases,
            v.total_paid, v.outstanding_balance,
            v.risk_score, v.risk_level
        ])

    return response


# ─── API Endpoints ──────────────────────────────────────────
def api_vendor_search(request):
    q = request.GET.get('q', '')
    vendors = Vendor.objects.filter(
        Q(name__icontains=q) | Q(company_name__icontains=q),
        is_active=True
    ).values('id', 'name', 'company_name', 'phone')[:10]
    return JsonResponse({'results': list(vendors)})


def api_gst_calc(request):
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    rate = request.GET.get('rate', '18')
    gst = subtotal * Decimal(rate) / 100
    total = subtotal + gst
    return JsonResponse({
        'gst_amount': float(gst),
        'total': float(total)
    })


def api_risk_score(request, vendor_pk):
    vendor = get_object_or_404(Vendor, pk=vendor_pk)
    return JsonResponse({
        'score': vendor.risk_score,
        'level': vendor.risk_level,
        'predicted_payment': str(vendor.predict_next_payment()),
        'outstanding': float(vendor.outstanding_balance),
    })


# ─── Items ──────────────────────────────────────────────────
def item_list(request):
    items = Item.objects.filter(is_active=True).select_related('category')
    return render(request, 'vendor_app/item_list.html', {'items': items})


def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added!')
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'vendor_app/item_form.html', {'form': form})