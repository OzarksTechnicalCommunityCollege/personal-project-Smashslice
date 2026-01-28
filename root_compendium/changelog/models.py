from django.conf import settings
from django.db import models
from django.utils import timezone

from django.urls import reverse

# Manager for handling post status
class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Update.Status.PUBLISHED)
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
    objects = models.Manager()
    published = PublishedManager()
    major_version = models.IntegerField()
    current_patch = models.IntegerField()
    bug_fix = models.CharField(max_length=1)
    automated_post = models.BooleanField(default=False)

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
