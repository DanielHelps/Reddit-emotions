from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=request.POST["username"], password=request.POST["password1"])
            login(request, user)
            # Redirect to home page after registering
            return redirect("/")
        
    else:
        form = RegisterForm()
    
    return render(request, "register/register.html", {"form": form})