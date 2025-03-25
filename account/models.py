import os
from django.db import models
from account.managers import *
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

def user_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'profile_images/user_{slugify(instance.name)}_{instance.phone_number}{file_extension}'

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    image = ProcessedImageField(
        upload_to=user_image_path,
        processors=[ResizeToFill(720, 720)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(User, self).save(*args, **kwargs)
    
    def get_full_name(self):
        """
        Returns the user's full name.
        """
        return self.name

    def get_short_name(self):
        """
        Returns the user's short name.
        """
        return self.name.split()[0] if self.name else self.email