from django.shortcuts import render


def home(request):
    return render(request, 'sheets/home.html')

def author(request):
    return render(request, 'sheets/author.html')

def theme(request):
    return render(request, 'sheets/theme.html')
