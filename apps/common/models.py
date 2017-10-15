from django.db import models

# Create your models here.


class CommonInfoModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
