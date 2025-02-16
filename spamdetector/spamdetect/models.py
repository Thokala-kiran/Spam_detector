from django.db import models

# Create your models here.
class userprofile(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    spam = models.BooleanField(default= False)

    def __str__(self):
        return self.name
    
    
