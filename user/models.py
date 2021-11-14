from django.db import models

# Create your models here.
# Model for storage login informations
class LoginLog(models.Model):
    username = models.CharField(max_length=100)
    user_agent = models.TextField()
    ip_adress = models.CharField(max_length=100)