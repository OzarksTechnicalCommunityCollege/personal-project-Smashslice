from django.conf import settings
from django.db import models
from django.utils import timezone

from django.urls import reverse

#Managers

# Manager for handling post status
class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Update.Status.PUBLISHED)
        )

# Manager for showering requested changes
class RequestedChangeManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=ChangeRequest.Status.REQUESTED)
        )
        
# Manager for showing accepted changes
class AcceptedChangeManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=ChangeRequest.Status.ACCEPTED)
        )

class Update(models.Model):

    #Properties

    # Subclass for handling Status
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
        ROLLBACK = 'RB', 'Rolled Back'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    major_version = models.IntegerField()
    current_patch = models.IntegerField()
    bug_fix = models.CharField(max_length=1)
    automated_post = models.BooleanField(default=False)
    
    # Managers
    objects = models.Manager()
    published = PublishedManager()
    

    # List of change types for use in automatic versioning later on
    CHANGE_TYPES = [
        ('M', 'Major'),
        ('P', 'Patch'),
        ('B', 'Bug'),
    ]

    # Keep track of the change type for this log post
    change_type = models.CharField(max_length=7, choices=CHANGE_TYPES, default='Other')

    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    
    # Meta rule for handling sorting
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]
        
    def __str__(self):
        return self.title
    
    # Kind of like def string, we are defining a property that is a return, because we want it to be a formatted string that is a combination of other existing properties.
    @property
    def version(self):
        """Returns formatted version string like 1.2a"""
        return f"{self.major_version}.{self.current_patch}{self.bug_fix}"
    
    def get_absolute_url(self):
        return reverse(
            'changelog:update_detail', 
            args=[
                self.major_version,
                self.current_patch,
                self.bug_fix]
        )
        
class ChangeRequest(models.Model):
    
    # Sub classes
    class Status(models.TextChoices):
        REQUESTED = 'R', 'Requested'
        ACCEPTED = 'A', 'Accepted'
        DENIED = 'D', 'Denied'
        COMPLETED = 'C', 'Completed'
    
    # Properties
    request_number = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=25)
    email = models.EmailField()
    request_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True) # We want these to be allowed to be empty as they will update programatically elsewhere
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.REQUESTED
    )
    
    # Managers
    objects = models.Manager()
    accepted_requests = AcceptedChangeManager()
    requested_requests = RequestedChangeManager()
    
    # Meta
    class Meta:
        ordering = ['accepted_at']
        indexes = [
            models.Index(fields=['accepted_at'])
        ]
        
    def __str__(self):
        return f'Requested at {self.created}'
        
    
