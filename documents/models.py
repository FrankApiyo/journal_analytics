from django.db import models
import uuid


class UserDocument(models.Model):
    user_id = models.IntegerField(null=False, blank=False, default=-1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50000)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (User ID: {self.user_id})"
