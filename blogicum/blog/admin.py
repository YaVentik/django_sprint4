from django.contrib import admin
from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'is_published',
    )
    search_fields = (
        'title',
    )
    prepopulated_fields = {"slug": ("title",)}


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'is_published',
    )
    search_fields = (
        'name',
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'location',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'is_published',
        'category',
        'location',
    )
    search_fields = (
        'title',
        'text',
    )
    list_display_links = ('title',)
    date_hierarchy = 'pub_date'
    filter_horizontal = ()


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
