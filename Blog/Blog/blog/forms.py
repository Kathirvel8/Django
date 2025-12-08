from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from blog.models import Category, Post

class ContactForm(forms.Form):

    name = forms.CharField(label='Name', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    message = forms.CharField(max_length=200, label='Message', required=True)
    
class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="Username", max_length=50, required=True)
    email = forms.CharField(label="Email", max_length=50, required=True)
    password = forms.CharField(label="Password", max_length=50, required=True)
    confirm_password = forms.CharField(label="Confirm Password", max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        # if not password:
        #     raise forms.ValidationError("Password should not be empty")
        if password and len(password) < 8:
            raise forms.ValidationError("Password length should be more than 8 Characters")
        
class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50, required=True)
    password = forms.CharField(label="Password", max_length=50, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username = username, password = password)
            if user is None:
                raise forms.ValidationError("Invalid username and password")
            
class ForgotPassword(forms.Form):
    email = forms.CharField(label='email', max_length=50)
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("User doesn't exist")
        
class ResetPassword(forms.Form):
    new_password = forms.CharField(label='New Password', min_length=8)
    confirm_password = forms.CharField(label='Confirm Password', min_length=8)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords doesn't match")

class NewPostForm(forms.ModelForm):
    title = forms.CharField(max_length=20, label="Title", required=True)
    content = forms.CharField(label="Content", required=True)
    category = forms.ModelChoiceField(label="Category", required=True, queryset=Category.objects.all())
    img_url = forms.ImageField(label='Upload Image', required=False)

    class Meta():
        model = Post
        fields = ['title', 'content', 'category', 'img_url']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')

        if title and len(title) < 5:
            raise forms.ValidationError("Title must be atlease 5 characters long")
        
        if content and len(content) < 10:
            raise forms.ValidationError("Content must be 10 characters long")
        
    def save(self, commit = ...):
        post = super().save(commit)
        cleaned_data = super().clean()

        if cleaned_data.get('img_url'):
            post.img_url = cleaned_data.get('img_url')
        else:
            img_url = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
            post.img_url = img_url
            
        if commit == True:
            post.save()
        return post