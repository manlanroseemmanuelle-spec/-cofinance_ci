from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings


def chat_page(request):
    return render(request, 'chat.html')
