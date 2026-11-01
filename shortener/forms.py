import re
from django import forms
from .models import Link


class LinkForm(forms.ModelForm):
    custom_code = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Кастомный код (например: my-link)",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Link
        fields = ["original_url", "title"]
        widgets = {
            "original_url": forms.URLInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "https://example.com/very/long/url...",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Название или метка (необязательно)",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_custom_code(self):
        code = self.cleaned_data.get("custom_code", "").strip()
        if not code:
            return ""
        if not re.match(r"^[a-zA-Z0-9_-]+$", code):
            raise forms.ValidationError(
                "Код может содержать только латинские буквы, цифры, дефис и подчеркивание."
            )
        reserved = [
            "admin",
            "api",
            "info",
            "qr",
            "static",
            "media",
            "delete",
            "favicon.ico",
        ]
        if code.lower() in reserved:
            raise forms.ValidationError("Этот код зарезервирован системой.")
        if Link.objects.filter(code=code).exists():
            raise forms.ValidationError("Такой короткий код уже занят.")
        return code
