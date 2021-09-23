from django.db import models


# Пользователи телеграмм приложения
class Profile(models.Model):
    tg_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)


class Message(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    text = models.TextField()
    #upload = models.FileField(upload_to='uploads/')