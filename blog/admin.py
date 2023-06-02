from django.contrib import admin
from .models import Blog, Blogger, Comments

# Register your models here.

# defining the admin class


class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'blogger', 'time_of_upload')
    list_filter = ('date_uploaded', 'time_of_upload')


# registering the admin class with the associated model
admin.site.register(Blog, BlogAdmin)

# defining the admin class


class BloggerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user',
                    'date_of_birth', 'date_joined', 'bio')


# registering the admin class with the associated model
admin.site.register(Blogger, BloggerAdmin)

admin.site.register(Comments)