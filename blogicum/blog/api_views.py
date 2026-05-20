# blog/api_views.py
import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment

User = get_user_model()


def json_response(data, status=200):
    """Утилита для JSON-ответа"""
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})



@require_http_methods(["GET"])
def api_posts(request):
    """Список постов (аналог FastAPI GET /posts/)"""
    posts = Post.objects.select_related('author', 'category', 'location').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    data = {
        'items': [
            {
                'id': p.id,
                'title': p.title,
                'text': p.text[:200],
                'author': p.author.username,
                'author_id': p.author.id,
                'category': p.category.title if p.category else None,
                'category_id': p.category.id if p.category else None,
                'location': p.location.name if p.location else None,
                'pub_date': p.pub_date.isoformat(),
                'image': p.image.url if p.image else None,
                'comments_count': p.comments.count()
            } for p in page
        ],
        'total': paginator.count,
        'page': page.number,
        'pages': paginator.num_pages
    }
    return json_response(data)


@require_http_methods(["GET"])
def api_post_detail(request, post_id):
    """Детальный пост (аналог FastAPI GET /posts/{id})"""
    try:
        post = Post.objects.select_related('author', 'category', 'location').get(id=post_id)
    except Post.DoesNotExist:
        return json_response({'error': 'Post not found'}, 404)

    data = {
        'id': post.id,
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'author_id': post.author.id,
        'category': post.category.title if post.category else None,
        'category_id': post.category.id if post.category else None,
        'location': post.location.name if post.location else None,
        'pub_date': post.pub_date.isoformat(),
        'image': post.image.url if post.image else None,
        'comments': [
            {
                'id': c.id,
                'text': c.text,
                'author': c.author.username,
                'author_id': c.author.id,
                'created_at': c.created_at.isoformat()
            } for c in post.comments.all().order_by('created_at')
        ]
    }
    return json_response(data)


@require_http_methods(["GET"])
def api_category_posts(request, category_slug):
    """Посты категории (аналог FastAPI GET /categories/{slug}/posts)"""
    try:
        category = Category.objects.get(slug=category_slug, is_published=True)
    except Category.DoesNotExist:
        return json_response({'error': 'Category not found'}, 404)

    posts = Post.objects.select_related('author', 'category', 'location').filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    data = {
        'category': category.title,
        'category_slug': category.slug,
        'items': [
            {
                'id': p.id,
                'title': p.title,
                'author': p.author.username,
                'pub_date': p.pub_date.isoformat()
            } for p in page
        ],
        'total': paginator.count,
        'page': page.number,
        'pages': paginator.num_pages
    }
    return json_response(data)


@require_http_methods(["GET"])
def api_user_posts(request, username):
    """Посты пользователя (аналог FastAPI GET /users/{username}/posts)"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return json_response({'error': 'User not found'}, 404)

    posts = Post.objects.select_related('author', 'category', 'location').filter(
        author=user,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    data = {
        'user': user.username,
        'user_id': user.id,
        'items': [
            {
                'id': p.id,
                'title': p.title,
                'category': p.category.title if p.category else None,
                'pub_date': p.pub_date.isoformat()
            } for p in page
        ],
        'total': paginator.count,
        'page': page.number,
        'pages': paginator.num_pages
    }
    return json_response(data)


@require_http_methods(["GET"])
def api_users(request):
    """Список пользователей (аналог FastAPI GET /users/)"""
    users = User.objects.all().only('id', 'username', 'email', 'first_name', 'last_name')

    data = {
        'items': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name
            } for u in users
        ],
        'total': users.count()
    }
    return json_response(data)


@require_http_methods(["GET"])
def api_user_detail(request, user_id):
    """Детальная информация о пользователе (аналог FastAPI GET /users/{id})"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json_response({'error': 'User not found'}, 404)

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat()
    }
    return json_response(data)



@csrf_exempt
@require_http_methods(["POST"])
def api_create_post(request):
    """Создание поста (аналог FastAPI POST /posts/)"""
    # if not request.user.is_authenticated:
    #     return json_response({'error': 'Unauthorized'}, 401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return json_response({'error': 'Invalid JSON'}, 400)

    required_fields = ['title', 'text']
    for field in required_fields:
        if field not in data:
            return json_response({'error': f'Missing field: {field}'}, 400)

    post = Post.objects.create(
        title=data['title'],
        text=data['text'],
        pub_date=timezone.now(),
        author=request.user,
        category_id=data.get('category_id'),
        location_id=data.get('location_id')
    )

    return json_response({
        'id': post.id,
        'title': post.title,
        'message': 'Post created successfully'
    }, 201)


@csrf_exempt
@require_http_methods(["POST"])
def api_delete_post(request, post_id):
    """Удаление поста (аналог FastAPI DELETE /posts/{id})"""
    # if not request.user.is_authenticated:
    #     return json_response({'error': 'Unauthorized'}, 401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return json_response({'error': 'Post not found'}, 404)

    if post.author != request.user and not request.user.is_superuser:
        return json_response({'error': 'Forbidden'}, 403)

    post.delete()
    return json_response({'message': 'Post deleted successfully'}, 200)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_comment(request, post_id):
    """Создание комментария (аналог FastAPI POST /comments/)"""
    # if not request.user.is_authenticated:
    #     return json_response({'error': 'Unauthorized'}, 401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return json_response({'error': 'Post not found'}, 404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return json_response({'error': 'Invalid JSON'}, 400)

    if 'text' not in data:
        return json_response({'error': 'Missing field: text'}, 400)

    comment = Comment.objects.create(
        text=data['text'],
        post=post,
        author=request.user
    )

    return json_response({
        'id': comment.id,
        'text': comment.text,
        'author': comment.author.username,
        'created_at': comment.created_at.isoformat(),
        'message': 'Comment created successfully'
    }, 201)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """Регистрация пользователя (аналог FastAPI POST /users/register)"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return json_response({'error': 'Invalid JSON'}, 400)

    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if field not in data:
            return json_response({'error': f'Missing field: {field}'}, 400)

    if User.objects.filter(username=data['username']).exists():
        return json_response({'error': 'Username already exists'}, 400)

    if User.objects.filter(email=data['email']).exists():
        return json_response({'error': 'Email already exists'}, 400)

    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )

    return json_response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'message': 'User registered successfully'
    }, 201)