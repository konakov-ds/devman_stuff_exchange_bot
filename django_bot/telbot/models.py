from django.db import models


# Пользователи телеграмм приложения
class Photo(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='uploads/')


class Profile(models.Model):
    tg_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    liked_stuff = models.ManyToManyField(Photo)


class Message(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    photo = models.ManyToManyField(Photo)