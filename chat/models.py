"""
This module defines the models for the chat application, including chat groups, memberships,
and messages. These models define the structure of the database tables used to manage 
group chats, members, and their messages. The models also include custom save logic, 
string representations, and helper methods for each class.

Key models:
1. **ChatGroup**: Represents a chat group, with a unique group name and a list of members.
2. **Membership**: Manages the relationship between users and chat groups, including roles and nicknames.
3. **GroupMessage**: Stores individual messages in chat groups, with support for attachments and message ordering.
"""

from django.db import models
from django.contrib.auth import get_user_model
import shortuuid
from PIL import Image
import os
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVector
 
UserModel = get_user_model()

class ChatGroup(models.Model):
    """
    Represents a chat group where users can communicate.
    
    Fields:
    - group_name: A unique slugified name for the group.
    - groupchat_name: A user-friendly name for the group (optional).
    - members: Many-to-many relationship to `UserModel` via `Membership`.
    - is_private: Boolean to indicate if the group is private or public.
    - created_at: Timestamp indicating when the group was created.

    The `save` method automatically generates a unique `group_name` slug if one is not provided.
    """
    group_name = models.SlugField(max_length=128, unique=True, blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    members = models.ManyToManyField(UserModel, related_name='chat_groups', blank=True, through='Membership')
    is_private = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """
        Returns a string representation of the chat group, which is the group name.
        """
        return self.group_name

    def save(self, *args, **kwargs):
        """
        Custom save method to automatically generate a unique `group_name` 
        slug if it is not already set.
        """
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
    """
    Represents the relationship between a user and a chat group.
    
    Fields:
    - role: The role of the user in the group (admin or member).
    - user: The user who is a member of the group.
    - chat_group: The chat group the user is a member of.
    - nickname: An optional nickname for the user in the group.
    - last_read_at: Timestamp of when the user last read the messages in the group.

    Ensures that a user cannot belong to the same group more than once with a unique constraint on `(user, chat_group)`.
    """
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
        """
        Returns a string representation of the membership, showing the user's email and nickname (if any).
        """
        return f"{self.user.email} ({self.nickname}) in {self.chat_group.group_name}"
            
class GroupMessage(models.Model):
    """
    Represents a message sent in a chat group.
    
    Fields:
    - group: The chat group where the message was sent.
    - author: The user who authored the message.
    - body: The content of the message (optional).
    - file: An optional file attachment.
    - created: Timestamp indicating when the message was created.

    Includes properties to get the filename if a file is attached and to check if the file is an image.
    """
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
        """
        Returns the filename of the attached file, if any.
        """
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    
    def __str__(self):
        """
        Returns a string representation of the message, showing the author and either the message content or the filename.
        """
        if self.body:
            return f'{self.author.email} : {self.body}'
        elif self.file:
            return f'{self.author.email} : {self.filename}'
    
    class Meta:
        ordering = ['-created']  # Orders messages by creation time (newest first)
        
    @property    
    def is_image(self):
        """
        Checks if the attached file is an image.
        """
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""