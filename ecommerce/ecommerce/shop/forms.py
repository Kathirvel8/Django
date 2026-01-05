from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=50, label="Username", required=True)
    email = forms.EmailField(max_length=50, label="Email", required=True)
    password = forms.CharField(max_length=50, label="Password", required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=50, label="ConfirmPassword", required=True, widget=forms.PasswordInput)

    class Meta():
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(message="Password do not match")
        
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label="Username", required=True)
    password = forms.CharField(max_length=20, label="Password", required=True, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid Credentials")