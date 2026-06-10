from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu usuário",
            "autofocus": True,
        })
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha",
        })
    )

    error_messages = {
        "invalid_login": "Usuário ou senha inválidos.",
        "inactive": "Esta conta está inativa.",
    }


class TrocaSenhaInicialForm(forms.Form):
    nova_senha = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite a nova senha",
        })
    )

    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme a nova senha",
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_nova_senha(self):
        nova_senha = self.cleaned_data.get("nova_senha")

        if self.user:
            validate_password(nova_senha, self.user)

        return nova_senha

    def clean(self):
        cleaned_data = super().clean()

        nova_senha = cleaned_data.get("nova_senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if nova_senha and confirmar_senha and nova_senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["nova_senha"])
        self.user.save()

        if hasattr(self.user, "perfil"):
            self.user.perfil.senha_temporaria = False
            self.user.perfil.save(update_fields=["senha_temporaria"])

        return self.user