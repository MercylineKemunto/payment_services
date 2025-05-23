from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FamilyViewSet, CohortViewSet, MemberViewSet,
    PaymentCategoryViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'families', FamilyViewSet)
router.register(r'cohorts', CohortViewSet)
router.register(r'members', MemberViewSet)
router.register(r'payment-categories', PaymentCategoryViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 