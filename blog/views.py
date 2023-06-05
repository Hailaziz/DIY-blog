from typing import Any, Dict
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Blogger, Comments, RequestToBeBlogger
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import BloggerRequestForm, SignupForm, BlogForm
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
# Create your views here.


def index(request):
    '''view for the homepage'''

    # generate the amount of some objects
    num_blogs = Blog.objects.all().count()
    num_bloggers = Blogger.objects.all().count()

    # total number of comments
    num_comments = Comments.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_blogs': num_blogs,
        'num_bloggers': num_bloggers,
        'num_comments': num_comments,
        'num_visits': num_visits,
    }

    # render the html template index.html
    return render(request, 'index.html', context=context)


class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 5
    # setting my name for the list as a template variable
    context_object_name = 'blogg'

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_deleted=False)


class BlogDetailView(LoginRequiredMixin, generic.DetailView):
    model = Blog
    # setting my name for the list as a template variable
    context_object_name = 'blogdetail'

    # this shows only the comments whose is_deleted field is False
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['comments'] = blog.comments_set.filter(deleted=False)
        return context


class BloggerListView(LoginRequiredMixin, generic.ListView):
    model = Blogger
    paginate_by = 5


class BloggerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Blogger

class Bloggers_BlogsView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name = 'blog/blogs_by_blogger.html'

    def get_queryset(self) -> QuerySet[Any]:
        id = self.kwargs['pk']
        
        # get the original blogger via the pk
        # and assign it to a variable
        original_author = get_object_or_404(Blogger, pk=id)

        # return the blogs written by the specific blogger
        # that hasn't been deleted
        return Blog.objects.filter(blogger=original_author, is_deleted=False)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['blogger'] = get_object_or_404(Blogger, pk=self.kwargs['pk'])
        return context

class CommentsCreate(LoginRequiredMixin, CreateView):
    model = Comments
    fields = ['comment',]
    template_name = 'blog/create_comment.html'

    def get_context_data(self, **kwargs: Any):
        # call the base implementation of the context already derived
        context = super(CommentsCreate, self).get_context_data(**kwargs)
        # get the blog using the pk and add it to the context
        context['blog'] = get_object_or_404(Blog, pk=self.kwargs['pk'])
        # return the updated context
        return context

    def form_valid(self, form):
        '''
        Add the Username of the person that created the comment
        and the blog it's commenting on, to Form data before
        setting it as valid (hence it is saved to the model)
        '''
        # Add the logged-in user as the username of comment
        form.instance.username = self.request.user
        # Associate the comment with the specific blog based on pk
        form.instance.blog = get_object_or_404(Blog, pk=self.kwargs['pk'])
        # Call super-class form validation behaviour
        return super(CommentsCreate, self).form_valid(form)

    def get_success_url(self):
        '''after posting the comment, return to the associated blog'''
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'],})

class CommentUpdateView(UpdateView):
    model = Comments
    fields = ['comment',]
    template_name = 'blog/update_comment.html'
    success_url = reverse_lazy('blogs')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        # checking if the comment is editable
        if (self.request.user == obj.username and obj.date_of_comment >= timezone.now() - timedelta(minutes=5)):
            return obj
        
        # if not, raise a permission error
        raise PermissionDenied
    
    def form_valid(self, form):
        form.instance.username = self.request.user
        return super().form_valid(form)
    
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comments
    fields = ['deleted']
    template_name = 'blog/comment_confirm_delete.html'
    success_url = reverse_lazy('blogs')

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.blog.author == self.request.user

    def form_valid(self, form):
        comment = self.get_object()
        comment.deleted = True
        comment.save()
        return HttpResponseRedirect(self.get_success_url())

class RequestToBeBloggerView(LoginRequiredMixin, View):
    '''handles the author request form,
    checks if a request already exists for the user,
    sends email notifications to editors,
    and saves the request to the database.'''
    
    # specifies the form to use for the view
    form_class = BloggerRequestForm

    # the path of the template file that will be rendered
    template_name = 'blog/blogger_request.html'


    def get(self, request):
        ''' handles the HTTP GET request'''

        # creates an instance of the BloggerRequestForm form class
        # and renders the template specified by template_name,
        # passing the form as a context variable.
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        '''handles the HTTP POST request'''

        form = self.form_class(request.POST)

        # checks if the form is valid
        if form.is_valid():
            # Check if an AuthorRequest already exists for the user
            if RequestToBeBlogger.objects.filter(user=request.user).exists():

                blogger_request = RequestToBeBlogger.objects.get(user=request.user)
                status = blogger_request.status
                if status == 'Rejected':
                    message = 'Your author request has been rejected.'
                else:
                    message = 'Your author request already exists and is pending.'
                return render(request, self.template_name, {'form': form, 'message': message})

            # if it is a new request,
            # save the form explicitly
            author_request = form.save(commit=False)

            # assigning the user attribute of the author_request
            # object with the currently logged-in user (request.user).
            author_request.user = request.user
            author_request.save()

            # a variable that holds the group object representing a group named "Editors".
            editors_group = Group.objects.get(name='Editors')

            # retrieve all the users who belong to the 'Editors' group
            editors = editors_group.user_set.all()
            for editor in editors:
                editor_email = editor.email
                send_mail(
                    "New Author Request",
                    f"{request.user} has requested to become an Author",
                    settings.EMAIL_HOST_USER,
                    [editor_email]
                )
            return redirect('request_success')  # Redirect to a success page

        return render(request, self.template_name, {'form': form})
    
def request_success_view(request):
    return render(request, 'blog/request_success.html')


def blogger_request_list(request):
    blogger_requests = RequestToBeBlogger.objects.filter(status='P')  # Get pending requests from users
    return render(request, 'blog/blogger_request_list.html', {'blogger_requests': blogger_requests})

def approve_blogger_request(request, pk):
    blogger_request = get_object_or_404(RequestToBeBlogger, pk=pk)
    blogger_request.status = 'A'
    blogger_request.save()
    send_mail(
        "Blogger Request Acceted",
        f"CONGRATULATIONS {blogger_request.first_name} {blogger_request.last_name}, Your Request to become an author has been approved. Happy writing",
        settings.EMAIL_HOST_USER,
        [blogger_request.user.email]
    )
    # Create a new Author instance based on the approved request
    if blogger_request.status == 'A':
        Blogger.objects.create(
            user=blogger_request.user,
            first_name=blogger_request.first_name,
            last_name=blogger_request.last_name,
            bio=blogger_request.bio
        )

    return redirect('author_request_list')


class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'blog/signup.html'
    success_url = reverse_lazy('login')

class CreateBlogView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/create_blog.html'
    success_url = '/blog/blogs/'

    def form_valid(self, form):
        form.instance.blogger = self.request.user.blogger
        return super().form_valid(form)


class UpdateBlogView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['name', 'description']
    template_name = 'blog/edit_blog.html'
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.blogger == request.user.blogger:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
class DeleteBlogView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['is_deleted']
    success_url = reverse_lazy('blogs')
    template_name = 'blog/blog_confirm_delete.html'

    def form_valid(self, form) -> HttpResponse:
        blog = self.get_object()
        blog.is_deleted = True
        blog.save()
        return HttpResponseRedirect(self.get_success_url())