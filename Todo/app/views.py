from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views import View
import jwt
from Todo.settings import SECRET_KEY

# Create your views here.
User  = get_user_model()


class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')
    

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')  
        

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})     
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')
    

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            token = jwt.encode({'username': user.username}, SECRET_KEY, algorithm='HS256')
            return redirect('dashboard')
            # return render(request, 'dashboard.html', {'token': token, 'username': user.username})
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    

@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Task

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        return render(request, 'dashboard.html', {'tasks': tasks})

    def post(self, request):
        task_name = request.POST.get('task')
        if task_name:
            Task.objects.create(user=request.user, name=task_name)
        return redirect('dashboard')

@login_required
def complete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.completed = not task.completed  
    task.save()
    return redirect('dashboard')

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.delete()
    return redirect('dashboard')
