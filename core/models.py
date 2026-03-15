from django.db import models
from django.contrib.auth.models import User



class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class Service(models.Model):
    service_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.service_name


class Bill(models.Model):
    invoice_number = models.CharField(max_length=20, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_bill = Bill.objects.order_by('id').last()
            if last_bill:
                last_id = last_bill.id + 1
            else:
                last_id = 1
            self.invoice_number = f"INV-{last_id:04d}"

        super().save(*args, **kwargs)

    def get_total_amount(self):
        total = sum(item.total_amount for item in self.items.all())
        return total

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.price = self.service.price
        self.total_amount = self.service.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill.invoice_number} - {self.service.service_name}"