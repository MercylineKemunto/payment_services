from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from payments.views import (
    dashboard, payment_history, initiate_payment, home, register,
    profile_update, add_family, family_list, add_cohort, cohort_list
)

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('payment-history/', payment_history, name='payment_history'),
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('profile/update/', profile_update, name='profile_update'),
    
    # Family management
    path('families/', family_list, name='family_list'),
    path('families/add/', add_family, name='add_family'),
    
    # Cohort management
    path('cohorts/', cohort_list, name='cohort_list'),
    path('cohorts/add/', add_cohort, name='add_cohort'),
    
    path('admin/', admin.site.urls),
    path('api/', include('payments.urls')),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register, name='register'),
] 