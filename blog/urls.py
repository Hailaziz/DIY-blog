from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blogs/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('bloggers/<int:pk>', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('blogs/<int:pk>/comment-create', views.CommentsCreate.as_view(), name='comment-detail'),
    path('blogs/<int:pk>/comment-edit', views.CommentUpdateView.as_view(), name='comment-edit'),
    path('blogs/<int:pk>/comment-delete', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('blogs/<int:pk>/blogger/', views.Bloggers_BlogsView.as_view(), name='blogs-by-blogger'),
    path('request-to-be-blogger/', views.RequestToBeBloggerView.as_view(), name='request-to-be-blogger'),
    path('request-success/', views.request_success_view, name='request-success'),
    path('blogger-request-list/', views.blogger_request_list, name='list-of-requests'),
    path('approved-request/', views.approve_blogger_request, name='request-approved'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('create-blog/', views.CreateBlogView.as_view(), name='create-blog'),
    path('edit-blog/', views.UpdateBlogView.as_view(), name='edit-blog'),
    path('delete-blog/', views.DeleteBlogView.as_view(), name='delete-blog'),
]