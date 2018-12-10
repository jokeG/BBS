from django.db import models


# Create your models here.
class UserInfo(models.Model):
    nid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
