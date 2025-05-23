from django.contrib import admin
from .models import Family, Cohort, Member, PaymentCategory, Payment

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    search_fields = ('name', 'year')
    ordering = ('-year',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'family', 'cohort', 'phone_number', 'is_amo', 'is_alo')
    list_filter = ('family', 'cohort', 'is_amo', 'is_alo')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'payment_type', 'amount', 'payment_date', 'status', 'mpesa_receipt_number')
    list_filter = ('payment_type', 'status', 'payment_date')
    search_fields = ('member__user__username', 'transaction_id', 'mpesa_receipt_number')
    ordering = ('-payment_date',) 