from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=200)
    title_name = models.CharField(max_length=200)

    def __str__(self):
        return self.title_name
