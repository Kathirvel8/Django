from django.contrib import admin
from .models import Post, Category, AboutUs

# Register your models here.
class postAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')

admin.site.register(Post, postAdmin)
admin.site.register(Category)
admin.site.register(AboutUs)