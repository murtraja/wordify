from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Word(models.Model):
    word = models.CharField(max_length = 25, unique=True, null = False)
    def __str__(self):
        return self.word
    
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    picture=models.ImageField(upload_to='profile_images', blank = True)
    def __str__(self):
        return self.user.username