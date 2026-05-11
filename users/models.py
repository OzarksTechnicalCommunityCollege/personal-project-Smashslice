from django.db import models
from django.conf import settings


# Models start

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    user_type = models.CharField(default='User')
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.username}\'s profile'