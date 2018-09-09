from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from uploads.core.models import CustomUser
from uploads.core.models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document')
        widgets={
        'description': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter a friendly description of the file'
        })
        }



class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)
        widgets={
        # 'username': forms.TextInput(attrs={
        # 'class': 'form-control',
        # 'placeholder': 'Enter your username'
        # }),
        'email': forms.EmailInput(attrs={
        'class':'form-control'
        })
        }

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)
        widgets={
        # 'username': forms.TextInput(attrs={
        # 'class': 'form-control',
        # 'placeholder': 'Enter your username'
        # }),
        'email': forms.EmailInput(attrs={
        'class':'form-control'
        })
        }

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email','password')
        widgets={
        'email': forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class':'form-control'
        }),
        'password': forms.PasswordInput(attrs={
        'class': 'form-control',
        })
        }
    # email = forms.EmailInput(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


