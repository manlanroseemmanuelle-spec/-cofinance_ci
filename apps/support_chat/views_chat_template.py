from django.shortcuts import render


def chat_page(request):
    return render(request, 'chat.html')


def dashboard_page(request):
    return render(request, 'base.html')
