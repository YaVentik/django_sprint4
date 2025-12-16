from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    """Главная страница с пагинацией."""
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')  # Подсчет комментариев
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    """Страница категории с пагинацией."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')  # Подсчет комментариев
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )


def post_detail(request, id):
    """Детальное отображение поста с комментариями."""
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=id
    )

    # Для не автора проверяем доступность поста
    if not (request.user == post.author):
        if (not post.is_published
            or not post.category.is_published
                or post.pub_date > timezone.now()):
            raise Http404("Пост не найден")

    form = CommentForm() if request.user.is_authenticated else None

    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all().order_by('created_at'),
    }
    return render(request, 'blog/detail.html', context)


def profile(request, username):
    """Страница профиля пользователя с всеми его постами."""
    profile = get_object_or_404(User, username=username)

    # Для автора показываем все его посты
    if request.user == profile:
        post_list = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            author=profile,
        ).order_by('-pub_date')
    else:
        post_list = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            author=profile,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    # Пагинация
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/profile.html',
        {'profile': profile, 'page_obj': page_obj}
    )


class UserEditForm(forms.ModelForm):
    """Форма для редактирования основных данных пользователя."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


@login_required
def edit_profile(request):
    """Страница редактирования профиля пользователя."""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'blog/edit_profile.html', {'form': form})


@login_required
def post_create(request):
    """Создание новой публикации."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование существующей публикации."""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_delete(request, post_id):
    """Удаление публикации."""
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что пользователь - автор поста
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    # Проверяем, что пользователь - автор комментария
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    return render(request, 'blog/comment.html', {'comment': comment})


def test_email(request):
    """Тестовая страница для проверки отправки email."""
    if request.user.is_authenticated:
        try:
            send_mail(
                'Тестовое письмо от Blogicum',
                f'Привет, {request.user.username}!\nЭто тестовое письмо.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            return
            HttpResponse('Письмо отправлено! Проверьте папку sent_emails/')
        except Exception as e:
            return HttpResponse(f'Ошибка: {e}')
    return HttpResponse('Войдите, чтобы протестировать')
