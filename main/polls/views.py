from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.db import IntegrityError

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Проверка существования пользователя с таким именем
        if User.objects.filter(username=username).exists():
            return render(request, 'user/register.html', {'error': 'Это имя пользователя уже занято.'})

        try:
            # Создаем пользователя
            user = User.objects.create_user(username=username, email=email, password=password)
            # Создаем профиль пользователя
            Profile.objects.create(user=user, full_name=full_name)
            return redirect('login')
        except IntegrityError:
            return render(request, 'user/register.html', {'error': 'Ошибка при создании пользователя. Попробуйте снова.'})

    return render(request, 'user/register.html')


def user_login(request):  # Переименован для избежания конфликта имен
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Используем auth_login вместо login
            messages.success(request, 'Вы успешно вошли в систему')
            return redirect('home')  # Исправлено на правильный вызов redirect
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'user/login.html')  # Возврат HttpResponse при GET-запросе и ошибке

def home(request):
    return render(request, 'post/home.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')