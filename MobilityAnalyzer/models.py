from django.db import models


# MovementItem model holds the extracted appointment data
class MovementItem(models.Model):
    name = models.CharField(max_length=180)
    fromCity = models.CharField(max_length=180)
    toCity = models.CharField(max_length=180)
    fromTitle = models.CharField(max_length=180)
    toTitle = models.CharField(max_length=180)
    salary = models.CharField(max_length=180)
    education = models.CharField(max_length=180)
    date = models.DateField()
    source = models.CharField(max_length=180)
    notes = models.CharField(max_length=200, default='No notes.')


def __str__(self):
    return self.name
