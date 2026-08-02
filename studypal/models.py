from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=False)
    password= models.CharField()

    def __str__(self):
        return f"{self.name}"

class Profile(models.Model):
    avatar = models.ImageField()
