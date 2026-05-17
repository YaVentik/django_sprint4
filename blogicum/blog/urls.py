from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import api_views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.post_create, name='create_post'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='delete_post'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('accounts/profile/', RedirectView.as_view(url='/', permanent=False)),
    path('test-email/', views.test_email, name='test_email'),
    # API маршруты для нагрузочного тестирования
    path('api/posts/', api_views.api_posts, name='api_posts'),
    path('api/posts/<int:post_id>/', api_views.api_post_detail, name='api_post_detail'),
    path('api/posts/create/', api_views.api_create_post, name='api_create_post'),
    path('api/posts/<int:post_id>/delete/', api_views.api_delete_post, name='api_delete_post'),
    path('api/posts/<int:post_id>/comment/', api_views.api_create_comment, name='api_create_comment'),
    path('api/category/<slug:category_slug>/', api_views.api_category_posts, name='api_category_posts'),
    path('api/user/<str:username>/posts/', api_views.api_user_posts, name='api_user_posts'),
    path('api/users/', api_views.api_users, name='api_users'),
    path('api/users/<int:user_id>/', api_views.api_user_detail, name='api_user_detail'),
    path('api/register/', api_views.api_register, name='api_register'),
]
