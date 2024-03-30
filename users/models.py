from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(null=True, blank=True, max_length=100)
    first_name = models.CharField(null=True, blank=True, max_length=100)
    last_name = models.CharField(null=True, blank=True, max_length=100)
    public_name = models.CharField(null=True, blank=True, max_length=100)
    language_preference = models.CharField(null=True, blank=True, max_length=100)

    is_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_profile_public = models.BooleanField(default=False)

    avatar_url = models.URLField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    contact = models.CharField(null=True, blank=True, max_length=200)
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    thumbnail_image_url = models.URLField(null=True, blank=True)
    small_image_url = models.URLField(null=True, blank=True)
    icon_image_url = models.URLField(null=True, blank=True)
    original_image_url = models.URLField(null=True, blank=True)
    facebook_id = models.CharField(null=True, blank=True, max_length=200)
    facebook_login_hash = models.CharField(null=True, blank=True, max_length=500)
    is_marketer = models.BooleanField(default=False)
    is_sales_admin = models.BooleanField(default=False)
    was_registered_with_order = models.BooleanField(default=False)

    billing_additional_info = models.TextField(null=True, blank=True)
    billing_address = models.CharField(null=True, blank=True, max_length=200)
    billing_city = models.CharField(null=True, blank=True, max_length=200)
    billing_contact_name = models.CharField(null=True, blank=True, max_length=200)
    billing_country = models.CharField(null=True, blank=True, max_length=200)
    billing_phone = models.CharField(null=True, blank=True, max_length=200)
    billing_tax_info = models.CharField(null=True, blank=True, max_length=200)
    billing_zip_code = models.CharField(null=True, blank=True, max_length=200)
    billing_state = models.CharField(null=True, blank=True, max_length=200)

    company = models.CharField(null=True, blank=True, max_length=200)
    rocket_chat_token = models.CharField(null=True, blank=True, max_length=200)

class Exhibitor(models.Model):
    username = models.OneToOneField(CustomUser, on_delete =models.CASCADE, related_name = 'exhibitors', null=False, blank = False)
    description = models.TextField(null = True, blank = True)
    website = models.URLField(null=False, blank = False)

    def verify(self):
        return self.username.is_verified 
    
    def update_exhibtor(self,description=None, website = None):
        if description is not None:
            self.description = description
        if website is not None:
            self.website = website
        self.save()
    
    def __str__(self) -> str:
        return self.username.username or "Exhibtors"
