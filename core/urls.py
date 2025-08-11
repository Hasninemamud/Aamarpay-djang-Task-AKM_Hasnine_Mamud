from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from django.contrib.auth import views as auth_views


router = DefaultRouter()
router.register(r'files', views.FileUploadViewSet, basename='fileupload')
router.register(r'transactions', views.PaymentTransactionViewSet, basename='paymenttransaction')
router.register(r'activity', views.ActivityLogViewSet, basename='activitylog')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('api/payment/success/', views.payment_success, name='payment_success'),
    path('api/payment/fail/', views.payment_fail, name='payment_fail'),
    path('api/payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('api/auth-token/', obtain_auth_token, name='auth_token'),
    # path('api/get-token/', views.get_auth_token, name='get_auth_token'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   
       
]
    

