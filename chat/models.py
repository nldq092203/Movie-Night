from django.db import models
from django.contrib.auth import get_user_model
import shortuuid
from PIL import Image
import os
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVector
 
UserModel = get_user_model()

class ChatGroup(models.Model):
    group_name = models.SlugField(max_length=128, unique=True, blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    members = models.ManyToManyField(UserModel, related_name='chat_groups', blank=True, through='Membership')
    is_private = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.group_name:
            base_slug = slugify(self.groupchat_name or shortuuid.uuid())
            slug = base_slug
            num = 1
            # Ensure uniqueness by checking existing ChatGroups
            while ChatGroup.objects.filter(group_name=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.group_name = slug
        super().save(*args, **kwargs)

class Membership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_index=True)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, db_index=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    last_read_at = models.DateTimeField(null=True, blank=True, db_index=True)  # Timestamp of last read message

    class Meta:
        unique_together = ('user', 'chat_group')

    def __str__(self):
        return f"{self.user.email} ({self.nickname}) in {self.chat_group.group_name}"
            
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE, db_index=True)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_index=True)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                name='search_body_idx',
                fields=['body'],
                opclasses=['gin']
            )
        ]    

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    
    def __str__(self):
        if self.body:
            return f'{self.author.email} : {self.body}'
        elif self.file:
            return f'{self.author.email} : {self.filename}'
    
    class Meta:
        ordering = ['-created']
        
    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False