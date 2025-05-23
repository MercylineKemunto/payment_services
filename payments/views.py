from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Family, Cohort, Member, PaymentCategory, Payment
from .serializers import (
    FamilySerializer, CohortSerializer, MemberSerializer,
    PaymentCategorySerializer, PaymentSerializer, MpesaPaymentSerializer
)
from .mpesa import MpesaClient
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured

class MemberRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, help_text='Enter your M-Pesa phone number')
    family = forms.ModelChoiceField(queryset=Family.objects.all(), required=True, help_text='Select your family')
    cohort = forms.ModelChoiceField(queryset=Cohort.objects.all(), required=True, help_text='Select your cohort')
    is_amo = forms.BooleanField(required=False, label='Are you an AMO?')
    is_alo = forms.BooleanField(required=False, label='Are you an ALO?')
    
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Member
        fields = ['phone_number', 'family', 'cohort']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

@login_required
def profile_update(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = Member.objects.create(
            user=request.user,
            phone_number=request.user.username
        )
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=member)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # Save Member model fields
            form.save()
            
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=member)
    
    return render(request, 'profile_update.html', {
        'form': form,
        'families': Family.objects.all(),
        'cohorts': Cohort.objects.all()
    })

def register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated Member object with additional fields
            Member.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                family=form.cleaned_data['family'],
                cohort=form.cleaned_data['cohort'],
                is_amo=form.cleaned_data['is_amo'],
                is_alo=form.cleaned_data['is_alo']
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MemberRegistrationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'families': Family.objects.all(),
        'cohorts': Cohort.objects.all()
    })

def home(request):
    """Home page view"""
    return render(request, 'home.html')

@login_required
def dashboard(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        # Create a basic member profile if it doesn't exist
        member = Member.objects.create(
            user=request.user,
            phone_number=request.user.username  # Temporary, user should update this
        )
        messages.warning(request, 'Please update your profile with your correct phone number.')
    
    payments = Payment.objects.filter(member=member).order_by('-payment_date')
    return render(request, 'dashboard.html', {
        'member': member,
        'payments': payments
    })

@login_required
def payment_history(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        # Create a basic member profile if it doesn't exist
        member = Member.objects.create(
            user=request.user,
            phone_number=request.user.username  # Temporary, user should update this
        )
        messages.warning(request, 'Please update your profile with your correct phone number.')
    
    payments = Payment.objects.filter(member=member)
    
    # Apply filters
    payment_type = request.GET.get('payment_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    if status:
        payments = payments.filter(status=status)
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            payments = payments.filter(payment_date__date__gte=date_from)
        except ValueError:
            pass
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            payments = payments.filter(payment_date__date__lte=date_to)
        except ValueError:
            pass
    
    payments = payments.order_by('-payment_date')
    
    return render(request, 'payment_history.html', {
        'payments': payments
    })

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        try:
            member = get_object_or_404(Member, user=request.user)
            amount = request.POST.get('amount')
            payment_type = request.POST.get('payment_type')
            mission_type = request.POST.get('mission_payment_type')

            if not amount:
                messages.error(request, 'Please enter a valid amount.')
                return redirect('dashboard')

            if not member.phone_number:
                messages.error(request, 'Please update your profile with a valid phone number.')
                return redirect('profile_update')

            try:
                mpesa_client = MpesaClient()
                response = mpesa_client.initiate_stk_push(
                    phone_number=member.phone_number,
                    amount=amount,
                    account_reference=f"MMUSDA_{payment_type}"
                )

                if response.get('ResponseCode') == '0':
                    messages.success(request, 'Payment initiated. Please check your phone to complete the transaction.')
                else:
                    error_message = response.get('errorMessage', 'Failed to initiate payment. Please try again.')
                    messages.error(request, error_message)
            except ImproperlyConfigured as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

        except Member.DoesNotExist:
            messages.error(request, 'Please complete your profile before making a payment.')
            return redirect('profile_update')

    return redirect('dashboard')

# API ViewSets
class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer

class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class PaymentCategoryViewSet(viewsets.ModelViewSet):
    queryset = PaymentCategory.objects.all()
    serializer_class = PaymentCategorySerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        serializer = MpesaPaymentSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            amount = serializer.validated_data['amount']
            payment_type = serializer.validated_data['payment_type']
            
            # Format account reference
            account_reference = f"MMUSDA_{payment_type}"
            if payment_type == 'MISSION':
                mission_type = serializer.validated_data.get('mission_payment_type')
                if mission_type:
                    account_reference = f"{account_reference}_{mission_type}"

            # Initialize M-Pesa payment
            mpesa_client = MpesaClient()
            response = mpesa_client.initiate_stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference=account_reference
            )

            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def mpesa_callback(self, request):
        """Handle M-Pesa callback"""
        callback_data = request.data
        
        # Extract relevant data from callback
        result_code = callback_data.get('ResultCode')
        if result_code == 0:  # Successful payment
            member = get_object_or_404(Member, phone_number=callback_data.get('PhoneNumber'))
            
            # Create payment record
            payment = Payment.objects.create(
                member=member,
                payment_type=callback_data.get('TransactionType'),
                amount=callback_data.get('Amount'),
                transaction_id=callback_data.get('TransactionID'),
                status='COMPLETED',
                mpesa_receipt_number=callback_data.get('MpesaReceiptNumber')
            )
            
            return Response({'status': 'success', 'payment_id': payment.id})
        
        return Response({'status': 'failed', 'message': 'Payment failed'})

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = ['name', 'year', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

@login_required
def add_family(request):
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Family added successfully!')
            return redirect('family_list')
    else:
        form = FamilyForm()
    
    return render(request, 'payments/family_form.html', {
        'form': form,
        'title': 'Add New Family'
    })

@login_required
def family_list(request):
    families = Family.objects.all().order_by('name')
    return render(request, 'payments/family_list.html', {
        'families': families
    })

@login_required
def add_cohort(request):
    if request.method == 'POST':
        form = CohortForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cohort added successfully!')
            return redirect('cohort_list')
    else:
        form = CohortForm()
    
    return render(request, 'payments/cohort_form.html', {
        'form': form,
        'title': 'Add New Cohort'
    })

@login_required
def cohort_list(request):
    cohorts = Cohort.objects.all().order_by('-year', 'name')
    return render(request, 'payments/cohort_list.html', {
        'cohorts': cohorts
    }) 