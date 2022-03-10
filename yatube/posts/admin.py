from django.contrib import admin
from .models import Follow, Post, Group, Comment


class PostAdmin(admin.ModelAdmin):

    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text')


admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)

admin.site.register(Follow, FollowAdmin)

admin.site.register(Comment, CommentAdmin)
