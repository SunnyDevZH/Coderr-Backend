"""
URL configuration for mein_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import RegisterView, LoginView, BaseInfoView, UserViewSet, ReviewViewSet
from offers.views import OfferDetailViewSet
from orders.views import OrderViewSet, OrderCountView, CompletedOrderCountView 
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    # Admin #

    path('admin/', admin.site.urls),

    # Accounts #

    path('api/registration/', RegisterView.as_view(), name='registration'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/base-info/', BaseInfoView.as_view(), name='base-info'),
    path('api/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='reviews'), 
    path('api/', include('accounts.urls')),

    path('api/profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile'),
    path('api/profiles/business/', UserViewSet.as_view({'get': 'list_business'}), name='profiles-business'),
    path('api/profiles/customer/', UserViewSet.as_view({'get': 'list_customer'}), name='profiles-customer'),

    # Orders / Offers #

    path('api/orders/', include('orders.urls')),
    path('api/order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('api/completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),

    path('api/offers/', include('offers.urls')),
    path('api/offerdetails/<int:pk>/', OfferDetailViewSet.as_view({'get': 'retrieve'}), name='offerdetails'),

    # Token Authentication #

    path('api/token/', obtain_auth_token, name='api_token_auth'),
]
