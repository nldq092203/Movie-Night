from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()

# Create your models here.
class UserProfile(models.Model):
    """
    UserProfile model stores additional information for the user such as bio.
    Each user has a one-to-one relationship with their profile.
    """
    GENDER_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Custom', 'Custom'),
    ]

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    custom_gender = models.CharField(max_length=64, blank=True, null=True, help_text="If you select 'Custom', please specify here")


    def __str__(self):
        """
        Returns a string representation of the user profile.
        """
        return f"{self.__class__.__name__} object for {self.user}"