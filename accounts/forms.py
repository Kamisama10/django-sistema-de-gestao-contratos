from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Seu usuário',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Sua senha',
        })
    )


class CadastroForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Seu nome',
        })
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Seu sobrenome',
        })
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class':       'auth-input',
            'placeholder': 'seu@email.com',
        })
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Crie uma senha',
        })
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class':       'auth-input',
            'placeholder': 'Repita a senha',
        })
    )

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email',
                  'username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class':       'auth-input',
                'placeholder': 'Escolha um usuário',
            })
        }
        labels = {'username': 'Nome de usuário'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Este e-mail já está cadastrado.'
            )
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'As senhas não coincidem.')
        return cleaned

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user