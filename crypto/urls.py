"""crypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    url(r'^deposit_check$', 'bank.views.merchant_deposit_bank'),#3 merchant, input bank signed money order and the message
    url(r'^reveal_id$', 'bank.views.show_id'),
    url(r'^check_sign$', 'bank.views.merchant_verify'),
    url(r'^verify', 'bank.views.verify_issue'),#####
    url(r'^test', 'bank.views.test_alice'),#####	
    url(r'^wallet', 'bank.views.wallet_unblind'),#####	
    url(r'^verify', 'bank.views.verify_issue'),#####
    url(r'^create', 'bank.views.bank_create'),

    url(r'^get_blind_code', 'bank.views.get_codes'),#####
    url(r'^input', 'bank.views.create_account'),#####1 create money order view
    url(r'^deposit$', 'bank.views.validate'),
    url(r'^merchant', 'bank.views.merchant_deposit'),#2 merchant view, input bank signed money order and the message

    #url(r'^encrypt3', 'bank.views.encrypt_mess2'),
    url(r'^money', 'consumer.views.create_money_order'),
    url(r'^encrypt', 'bank.views.process_data'),
    url(r'public_key', 'bank.views.create_user'),

    url(r'^bank/', 'bank.views.create_account'),
    url(r'^admin/', include(admin.site.urls)),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
