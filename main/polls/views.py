from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile,  Post, Comment
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

def profile(request):
    profiles = Profile.objects.all()  # Получаем все профили из базы данных
    user_profile = None
    user_posts = []  # Список для хранения постов текущего пользователя

    if request.user.is_authenticated:
        try:
            user_profile = Profile.objects.get(user=request.user)  # Получаем профиль текущего пользователя
            user_posts = Post.objects.filter(author=request.user)  # Получаем посты текущего пользователя
        except Profile.DoesNotExist:
            user_profile = None  # Профиль не существует
    return render(request, 'user/profile.html', {'profiles': profiles,'user_profile': user_profile,'user_posts': user_posts})

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')


def edit_profile(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        user_profile.full_name = request.POST.get('full_name', user_profile.full_name)
        user_profile.birth_date = request.POST.get('birth_date', user_profile.birth_date)

        # Проверяем, что файл загружен
        if request.FILES.get('avatar'):  # Убедитесь, что используете 'avatar'
            user_profile.avatar = request.FILES['avatar']  # Убедитесь, что используете 'avatar'

        user_profile.save()
        return redirect('profile')  # Перенаправление на страницу профиля после сохранения

    return render(request, 'user/edit_profile.html', {'user_profile': user_profile})





from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Like
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Получаем файл изображения

        if title and content:  # Проверяем, что заголовок и содержание не пустые
            post = Post(author=request.user, title=title, content=content, image=image)
            post.save()
            return redirect('post_detail', post_id=post.id)  # Перенаправляем на страницу поста

    return render(request, 'post/create_post.html')  # Отображаем страницу создания поста

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()  # Извлечение комментариев

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, content=content, author=request.user)
            return redirect('post_detail', post_id=post.id)  # Перенаправление на страницу поста

    return render(request, 'post/post_detail.html', {
        'post': post,
        'comments': comments,
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Проверяем, существует ли уже лайк для этого поста и пользователя
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        # Если лайк уже существует, удаляем его
        like.delete()

    return redirect('post_detail', post_id=post.id)


def post_list(request):
    # Извлекаем все посты из базы данных, сортируя их по дате создания
    posts = Post.objects.all().order_by('-created_at')

    # Передаем список постов в шаблон
    return render(request, 'post/post_list.html', {'posts': posts})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.contrib.auth.decorators import login_required

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, является ли текущий пользователь автором поста
    if request.user != post.author:
        return redirect('post_detail', post_id=post.id)  # Перенаправление, если не автор

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.image = request.FILES.get('image', post.image)  # Сохраняем старое изображение, если новое не загружено
        post.save()
        return redirect('post_detail', post_id=post.id)  # Перенаправление на страницу поста

    return render(request, 'post/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, является ли текущий пользователь автором поста
    if request.user != post.author:
        return redirect('post_detail', post_id=post.id)  # Перенаправление, если не автор

    if request.method == 'POST':
        post.delete()  # Удаление поста
        return redirect('home')  # Перенаправление на домашнюю страницу или список постов

    return render(request, 'post/confirm_delete.html', {'post': post})
