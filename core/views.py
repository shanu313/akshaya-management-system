from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from openpyxl import Workbook

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

from .models import Customer, Service, Bill, BillItem
from .forms import CustomerForm, ServiceForm, BillForm, BillItemForm

import os



def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    total_customers = Customer.objects.count()
    total_services = Service.objects.count()
    total_bills = Bill.objects.count()

    today = timezone.now().date()

    today_bills = Bill.objects.filter(date__date=today)

    today_income = sum(bill.get_total_amount() for bill in today_bills)

    monthly_bills = Bill.objects.annotate(month=TruncMonth('date')).order_by('month')

    month_map = {}

    for bill in monthly_bills:
        month_name = bill.date.strftime('%b %Y')
        month_map[month_name] = month_map.get(month_name, 0) + float(bill.get_total_amount())

    months = list(month_map.keys())
    totals = list(month_map.values())

    context = {
        'total_customers': total_customers,
        'total_services': total_services,
        'total_bills': total_bills,
        'today_income': today_income,
        'months': months,
        'totals': totals,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_customer(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')

    return render(request, 'add_customer.html', {'form': form})

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

@login_required
def add_service(request):
    form = ServiceForm()
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    return render(request, 'add_service.html', {'form': form})


@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})


@login_required
def create_bill(request):
    form = BillForm()

    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.save()
            return redirect('bill_list')

    return render(request, 'create_bill.html', {'form': form})

@login_required
def bill_list(request):
    bills = Bill.objects.all()
    return render(request, 'bill_list.html', {'bills': bills})

@login_required
def daily_report(request):
    today = timezone.now().date()
    today_bills = Bill.objects.filter(date__date=today)

    total_bills = today_bills.count()
    total_income = sum(bill.get_total_amount() for bill in today_bills)

    context = {
        'total_income': total_income,
        'total_bills': total_bills,
    }

    return render(request, 'daily_report.html', context)

def invoice(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    return render(request, 'invoice.html', {'bill': bill})

def download_invoice_pdf(request, bill_id):
    bill = Bill.objects.get(id=bill_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{bill.invoice_number}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles['Title']
    normal_style = styles['Normal']
    heading_style = styles['Heading2']

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'core/static/logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.8 * inch, height=0.9 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Spacer(1, 0.15 * inch))

    # Shop title
    elements.append(Paragraph("<b>AKSHAYA DIGITAL CENTER</b>", title_style))
    elements.append(Paragraph("Phone: 9999999999", normal_style))
    elements.append(Paragraph("Address: Your Shop Address Here", normal_style))
    elements.append(Spacer(1, 0.25 * inch))

    # Invoice details
    invoice_info = [
        ["Invoice No", bill.invoice_number],
        ["Date", bill.date.strftime("%d-%m-%Y %H:%M")],
        ["Customer Name", bill.customer.name],
        ["Phone", bill.customer.phone],
        ["Created By", bill.created_by.username if bill.created_by else "-"],
    ]

    info_table = Table(invoice_info, colWidths=[1.8 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25 * inch))

    # Service table
    data = [["Service", "Qty", "Price", "Total"]]

    for item in bill.items.all():
        data.append([
            item.service.service_name,
            str(item.quantity),
            f"Rs. {item.price}",
            f"Rs. {item.total_amount}",
        ])

    service_table = Table(data, colWidths=[2.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    elements.append(service_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Grand total
    total_table = Table(
        [["Grand Total", f"Rs. {bill.get_total_amount()}"]],
        colWidths=[4.8 * inch, 1.2 * inch]
    )
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Thank you for your business!", heading_style))
    elements.append(Paragraph("This is a computer-generated invoice.", normal_style))

    doc.build(elements)
    return response

@login_required
def monthly_report(request):
    bills = Bill.objects.all().order_by('date')

    month_map = {}

    for bill in bills:
        month_name = bill.date.strftime('%b %Y')
        month_map[month_name] = month_map.get(month_name, 0) + float(bill.get_total_amount())

    months = list(month_map.keys())
    totals = list(month_map.values())

    context = {
        'months': months,
        'totals': totals,
    }

    return render(request, 'monthly_report.html', context)




def edit_customer(request, id):
    customer = Customer.objects.get(id=id)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')

    return render(request, 'add_customer.html', {'form': form})


def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    return redirect('customer_list')

def edit_service(request, id):
    service = Service.objects.get(id=id)
    form = ServiceForm(instance=service)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')

    return render(request, 'add_service.html', {'form': form})


def delete_service(request, id):
    service = Service.objects.get(id=id)
    service.delete()
    return redirect('service_list')

@login_required
def export_bills_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Bills Report"

    # Header row
    ws.append([
        "Bill ID",
        "Date",
        "Customer",
        "Phone",
        "Service",
        "Quantity",
        "Price",
        "Total Amount"
    ])

    bills = Bill.objects.all()
    
    for bill in bills:
       for item in bill.items.all():

        ws.append([
            bill.id,
            bill.date.strftime("%d-%m-%Y %H:%M"),
            bill.customer.name,
            bill.customer.phone,
            bill.service.service_name,
            bill.quantity,
            float(bill.service.price),
            float(bill.get_total_amount()),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=bills_report.xlsx'

    wb.save(response)
    return response

@login_required
def bill_list(request):
    bills = Bill.objects.all()

    # 🔎 Search by customer name
    search_query = request.GET.get('search')
    if search_query:
        bills = bills.filter(customer__name__icontains=search_query)

    # 📅 Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        bills = bills.filter(date__date__range=[start_date, end_date])

    context = {
        'bills': bills
    }

    return render(request, 'bill_list.html', context)


@login_required
def edit_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    if request.method == "POST":
        bill.quantity = request.POST.get("quantity")
        bill.total_amount = request.POST.get("total_amount")
        bill.save()
        return redirect('bill_list')

    return render(request, "edit_bill.html", {"bill": bill})


@login_required
def delete_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.delete()
    return redirect('bill_list')


@login_required
def create_bill(request):
    form = BillForm()

    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.save()
            return redirect('add_bill_items', bill_id=bill.id)

    return render(request, 'create_bill.html', {'form': form})


@login_required
def add_bill_items(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    form = BillItemForm()

    if request.method == 'POST':
        form = BillItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.bill = bill
            item.save()
            return redirect('add_bill_items', bill_id=bill.id)

    items = bill.items.all()

    return render(request, 'add_bill_items.html', {
        'bill': bill,
        'form': form,
        'items': items,
        'total_amount': bill.get_total_amount()
    })