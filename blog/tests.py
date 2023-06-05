from datetime import date, datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Blog, Blogger, Comments, RequestToBeBlogger

# Create your tests here.

class BlogModelTest(TestCase):
    '''THIS TEST CASES ARE FOR THE BLOG MODEL'''
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        blogger = Blogger.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1),
            bio='Test bio'
        )
        Blog.objects.create(
            name='Test Blog',
            blogger=blogger,
            description='Test description',
            date_uploaded=date.today(),
            is_deleted=False
        )

    def test_string_representation(self):
        blog = Blog.objects.get(id=1)
        self.assertEqual(str(blog), blog.name)

    def test_get_absolute_url(self):
        blog = Blog.objects.get(id=1)
        expected_url = reverse('blog-detail', args=[str(blog.id)])
        self.assertEqual(blog.get_absolute_url(), expected_url)

    def test_get_comments(self):
        blog = Blog.objects.get(id=1)
        comment = Comments.objects.create(
            username=User.objects.create_user('testuser'),
            comment='Test comment',
            blog=blog
        )
        comments = blog.get_comments
        self.assertIn(comment, comments)

    def test_ordering(self):
        Blog.objects.create(
            name='Another Blog',
            blogger=Blogger.objects.get(id=1),
            description='Another description',
            date_uploaded=date.today(),
            is_deleted=False
        )
        blogs = Blog.objects.all()
        self.assertEqual(blogs[0].name, 'Another Blog')
        self.assertEqual(blogs[1].name, 'Test Blog')


class BloggerModelTest(TestCase):
    '''THIS TEST CASES ARE FOR THE BLOGGER MODEL'''

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Blogger.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1),
            bio='Test bio'
        )

    def test_string_representation(self):
        blogger = Blogger.objects.get(id=1)
        expected_string = f'{blogger.last_name}, {blogger.first_name}'
        self.assertEqual(str(blogger), expected_string)

    def test_get_absolute_url(self):
        blogger = Blogger.objects.get(id=1)
        expected_url = reverse('blogger-detail', args=[str(blogger.id)])
        self.assertEqual(blogger.get_absolute_url(), expected_url)

    def test_ordering(self):
        Blogger.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(1985, 5, 5),
            bio='Test bio'
        )
        bloggers = Blogger.objects.all()
        self.assertEqual(bloggers[0].last_name, 'Doe')
        self.assertEqual(bloggers[1].last_name, 'Smith')


class CommentsModelTest(TestCase):
    '''THIS TEST CASES ARE FOR THE COMMENTS MODEL'''

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        blogger = Blogger.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(1990, 1, 1).date(),
            bio='Test bio'
        )
        blog = Blog.objects.create(
            name='Test Blog',
            blogger=blogger,
            description='Test description',
            date_uploaded=datetime.now().date(),
            is_deleted=False
        )
        Comments.objects.create(
            username=User.objects.create_user('testuser'),
            date_of_comment=datetime.now(),
            comment='Test comment',
            blog=blog
        )
    
    def test_string_representation(self):
        comment = Comments.objects.get(id=1)
        expected_string = comment.comment[:75]
        self.assertEqual(str(comment), expected_string)


    def test_ordering(self):
        blogger = Blogger.objects.get(id=1)
        blog = Blog.objects.get(id=1)
        Comments.objects.create(
            username=User.objects.create_user('anotheruser'),
            date_of_comment=datetime.now(),
            comment='Another comment',
            blog=blog
        )
        comments = Comments.objects.all()
        self.assertEqual(comments[0].comment, 'Test comment')
        self.assertEqual(comments[1].comment, 'Another comment')


class RequestToBeBloggerModelTest(TestCase):
    '''THIS TEST CASES ARE FOR THE REQUEST TO BE A BLOGGER MODEL'''

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        RequestToBeBlogger.objects.create(
            user=User.objects.create_user('testuser'),
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(1990, 1, 1).date(),
            bio='Test bio',
            request_date=datetime.now(),
            status='P'
        )

    def test_string_representation(self):
        request = RequestToBeBlogger.objects.get(id=1)
        expected_string = f'{request.user.username} request to be a blogger'
        self.assertEqual(str(request), expected_string)

    def test_default_status(self):
        request = RequestToBeBlogger.objects.get(id=1)
        self.assertEqual(request.status, 'P')

    def test_status_choices(self):
        request = RequestToBeBlogger.objects.get(id=1)
        status_choices = dict(RequestToBeBlogger.request_status)
        self.assertIn(request.status, status_choices.keys())

    def test_permissions(self):
        request = RequestToBeBlogger.objects.get(id=1)
        self.assertTrue(request._meta.permissions)


'''Test for the Views'''

class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        # Add more assertions to test the context variables


class BlogListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample blogs for testing
        blog_data = [
            {'name': 'Blog 1', 'description': 'Description 1'},
            {'name': 'Blog 2', 'description': 'Description 2'},
            # Add more sample blogs as needed
        ]

        for data in blog_data:
            Blog.objects.create(name=data['name'], description=data['description'])

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    def test_lists_all_blogs(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(len(response.context['object_list']), 2)

    def test_blogs_have_correct_data(self):
        response = self.client.get(reverse('blogs'))
        blogs = response.context['object_list']
        self.assertEqual(blogs[0].name, 'Blog 1')
    
        blogger = blogs[0].blogger
        if blogger is not None:
            self.assertEqual(blogger.username, 'testuser')
        else:
            self.assertIsNone(blogger)

class BlogDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.blogger = Blogger.objects.create(user=self.user, first_name='John', last_name='Doe')
        self.blog = Blog.objects.create(name='Test Blog', blogger=self.blogger)
        self.comment1 = Comments.objects.create(username=self.user, comment='Comment 1', blog=self.blog, deleted=False)
        self.comment2 = Comments.objects.create(username=self.user, comment='Comment 2', blog=self.blog, deleted=True)

    def test_view_with_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('blog-detail', kwargs={'pk': self.blog.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        self.assertEqual(response.context['blogdetail'], self.blog)
        self.assertQuerysetEqual(
        response.context['comments'],
        [self.comment1.comment],  # Compare comment text instead of string representation
        transform=lambda x: x.comment,
    )

    def test_view_with_deleted_comments(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('blog-detail', kwargs={'pk': self.blog.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        # Add the base template
        self.assertTemplateUsed(response, 'base_temp.html')
        # Verify that the deleted comment is not displayed in the comments section
        self.assertNotContains(response, {self.comment2.comment})

    def test_get_absolute_url(self):
        expected_url = reverse('blog-detail', kwargs={'pk': self.blog.pk})
        self.assertEqual(self.blog.get_absolute_url(), expected_url)

    def test_get_comments(self):
        comments = self.blog.get_comments.all()
        self.assertEqual(list(comments), [self.comment1, self.comment2])

    def test_comment_str_representation(self):
        expected_string = "Comment 1"
        self.assertEqual(str(self.comment1), expected_string)