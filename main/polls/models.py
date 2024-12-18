from django.db import models
from django.contrib.auth.models import User
from django.db.models import CharField
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = CharField(max_length=250, blank=True, null=False)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    title = models.CharField(max_length=250, blank=True, null=False)
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
