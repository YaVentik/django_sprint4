from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category


def index(request):
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )[:5]
    return render(request, 'blog/index.html', {'post_list': post_list})


def category_posts(request, category_slug):
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
    )
    return render(
        request,
        'blog/category.html',
        {'category': category, 'post_list': post_list}
    )


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    return render(request, 'blog/detail.html', {'post': post})
