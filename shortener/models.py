import string
import secrets
from django.db import models


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


class Link(models.Model):
    original_url = models.URLField(max_length=2048)
    code = models.CharField(max_length=32, unique=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, blank=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            code = generate_short_code()
            while Link.objects.filter(code=code).exists():
                code = generate_short_code()
            self.code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} -> {self.original_url}"
