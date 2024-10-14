from django.db import models
from django.contrib.auth import get_user_model
import shortuuid
from PIL import Image
import os

UserModel = get_user_model()

class ChatGroup(models.Model):
    group_name = models.SlugField(max_length=128, unique=True, blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ManyToManyField(UserModel, related_name='groupchats', blank=True, null=True)
    members = models.ManyToManyField(UserModel, related_name='chat_groups', blank=True, through='Membership')
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = shortuuid.uuid()
        super().save(*args, **kwargs)

class Membership(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    last_read_at = models.DateTimeField(null=True, blank=True)  # Timestamp of last read message

    class Meta:
        unique_together = ('user', 'chat_group')

    def __str__(self):
        return f"{self.user.username} ({self.nickname}) in {self.chat_group.group_name}"
            
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    
    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'
    
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
