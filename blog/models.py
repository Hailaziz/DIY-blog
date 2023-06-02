from django.db import models
from datetime import date
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.


class Blog(models.Model):
    '''model representing a blog'''
    name = models.CharField(
        max_length=200, help_text='Write the title of your blog here')
    blogger = models.ForeignKey(
        'Blogger', on_delete=models.SET_NULL, null=True)
    time_of_upload = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=2000, help_text='write your blog here', blank=True)
    date_uploaded = models.DateField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['name', 'blogger']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this blog."""
        return reverse('blog-detail', args=[str(self.id)])

    @property
    def get_comments(self):
        return Comments.objects.filter(blog=self)


class Blogger(models.Model):
    '''model representing a blog creator'''
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(default=date.today)
    bio = models.TextField(
        max_length=2000, help_text='tell us a little about yourself')

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this blogger."""
        return reverse('blogger-detail', args=[str(self.id)])


class Comments(models.Model):
    '''the comments of user's in the miniblog'''
    username = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=False)
    date_of_comment = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(
        max_length=1000, help_text='write your comments here')
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_of_comment']

    def __str__(self):

        comment_length = 75
        if len(self.comment) > comment_length:
            string = self.comment[:75] + '...'
        else:
            string = self.comment
        return string


class RequestToBeBlogger(models.Model):
    '''if a user/reader wants to become a blogger'''
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(
        max_length=2000, help_text='tell us a little about yourself')
    request_date = models.DateTimeField()
    
    request_status = [
        ('A', 'Accepted'),
        ('P', 'Pending'),
        ('R', 'Rejected'),
    ]

    status = models.CharField(max_length=1,
        choices=request_status,
        blank=True,
        default='P',
        help_text='status of your request',
        )
    
    def __str__(self):
        return f'{self.user.username} request to be a blogger'
    
    class Meta:
        
        ordering = ['request_date']
        permissions = (('can_approve_request', 'set user as blogger'), )