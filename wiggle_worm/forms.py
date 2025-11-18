from django import forms
from django.forms.models import ModelForm

from django.core import validators

from .models import User

from django.contrib.auth.password_validation import validate_password


class LoginForm(forms.Form):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'aria-label': 'Email',
                'aria-required': 'true',
                'aria-describedby': 'email-addon',
            }
        )
    )
    password = (forms.CharField
        (widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
                'aria-label': 'Password',
                'aria-required': 'true',
                'aria-describedby': 'password-addon',
            }
        )
    ))


class Register(ModelForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'aria-label': 'Email',
                'aria-required': 'true',
                'aria-describedby': 'email-addon',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
                'aria-label': 'Password',
                'aria-required': 'true',
                'aria-describedby': 'password-addon',
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean_username(self):
        email = self.cleaned_data['username']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Username already exists')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user





