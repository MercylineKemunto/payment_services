from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Family, Cohort, Member, PaymentCategory, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'

class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    family_name = serializers.CharField(source='family.name', read_only=True)
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)

    class Meta:
        model = Member
        fields = '__all__'

class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    family_name = serializers.CharField(source='member.family.name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'

class MpesaPaymentSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPES)
    mission_payment_type = serializers.ChoiceField(choices=Payment.MISSION_PAYMENT_TYPES, required=False)
    account_reference = serializers.CharField(required=False) 