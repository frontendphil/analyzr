from django.db import models

class Repo(models.Model):

    url = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
