from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class Word(models.Model):
    word = models.CharField(max_length = 25, unique=True, null = False)
    def __str__(self):
        return self.word
    def __unicode__(self):
        return self.word
    
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    picture=models.ImageField(upload_to='profile_images', blank = True)
    def __str__(self):
        return self.user.username



class GroupFinalResult(models.Model):
    re_user=models.ForeignKey(User,default=0)
    groupname=models.CharField(max_length=100)
    marks=models.IntegerField(default=0)
    starttime= models.DateTimeField(default=timezone.now(), blank=False)
    endtime=models.DateTimeField(blank=False,default=timezone.now())
    def __str__(self):
            return self.re_user.username+str(self.groupname)

class GroupResultTable(models.Model):
    usertest=models.ForeignKey(GroupFinalResult,default=0)
    correct_ans=models.CharField(max_length=25,null=False)
    ans=models.CharField(max_length=25,null=False)
    marks=models.IntegerField(default=0)

    def __str__(self):
        return str(self.usertest.groupname)+str(" ")+str(self.usertest.re_user.username)+str(self.correct_ans)

class FinalResult(models.Model):
    re_user=models.ForeignKey(User,default=0)
    session_id=models.IntegerField(default=0)
    marks=models.IntegerField(default=0)
    starttime= models.DateTimeField(default=timezone.now(), blank=False)
    endtime=models.DateTimeField(blank=False,default=timezone.now())
    def __str__(self):
            return self.re_user.username+str(self.session_id)


class ResultTable(models.Model):
    re_user=models.ForeignKey(User,default=0)
    session_id=models.IntegerField(default=0)
    correct_ans=models.CharField(max_length=25,null=False)
    ans=models.CharField(max_length=25,null=False)
    marks=models.IntegerField(default=0)

    def __str__(self):
        return self.re_user.username+str(self.session_id)

