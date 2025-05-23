from django.db import models
from django.contrib.auth.models import User

class Family(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Families"

    def __str__(self):
        return self.name

class Cohort(models.Model):
    year = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.year}"

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=15)
    is_amo = models.BooleanField(default=False)
    is_alo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.family}"

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Payment Categories"

    def __str__(self):
        return self.name

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('OFFERING', 'Offering'),
        ('TITHE', 'Tithe'),
        ('CONTRIBUTION', 'Contribution'),
        ('MISSION', 'Mission'),
        ('LUNCH', 'Lunch Money'),
        ('FUNDRAISING', 'Fundraising'),
    ]

    MISSION_PAYMENT_TYPES = [
        ('20_BOB', '20 Bob Challenge'),
        ('50_BOB', '50 Bob Challenge'),
        ('COHORT', 'Cohort Payment'),
        ('FAMILY', 'Family Payment'),
        ('MINI_CONCERT', 'Mini Fundraiser Concert'),
        ('MEGA_FUNDRAISER', 'Mega Fundraiser'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    mission_payment_type = models.CharField(max_length=20, choices=MISSION_PAYMENT_TYPES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='PENDING')
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.member} - {self.payment_type} - {self.amount}" 