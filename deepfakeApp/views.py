from django.shortcuts import render, HttpResponse, redirect
import sys
sys.path.append(r"E:\mjp-main\deepfakeApp\CViT-main")

from predict import prediction


def HomePage(request):
    return render(request, "1.html")

def Real(request):
    return render(request, "2.html")

def Fake(request):
    return render(request, "3.html")


def check(request):
    z=prediction()
    if z==True:
        return redirect("Real")
    else:
        return redirect("Fake")

 