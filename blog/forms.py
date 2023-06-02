from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comments


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        # The fields attribute specifies that only the 'comment'
        # field should be displayed in the form.
        fields = ['comment']
        # The widgets attribute is used to customize the
        # rendering of the form fields. In this case, the
        # 'username' and 'date_of_comment' fields are set as readonly,
        #  which prevents them from being edited by users.
        widgets = {
            'username': forms.TextInput(attrs={'readonly': True}),
            'date_of_comment': forms.DateTimeInput(attrs={'readonly': True}),
        }

    # In the __init__ method, the username and date_of_comment
    # fields are disabled to ensure they are not editable.
    # This prevents users from modifying these fields in the form.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['date_of_comment'].disabled = True


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


from .models import RequestToBeBlogger, Blog

class BloggerRequestForm(forms.ModelForm):
    class Meta:
        model = RequestToBeBlogger
        fields = ['first_name', 'last_name', 'bio']  
        

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name', 'description']
