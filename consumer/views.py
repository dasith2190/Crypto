from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse

def create_money_order(request):
	return render(request, 'moneyorder.html', context={})


