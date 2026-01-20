from django.conf import settings
from django.db import models
from django.utils import timezone

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

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    version = models.CharField(max_length=10)

    # For if a post is posted VIA pipeline automation 
    automated_post = models.BooleanField(default=False)

    # List of change types for use in automatic versioning later on
    CHANGE_TYPES = [
        ('M', 'Major'),
        ('F', 'Feature'),
        ('W', 'Weekly'),
        ('B', 'Bug'),
        ('O', 'Other')
    ]

    # Keep track of the change type for this log post
    change_type = models.CharField(max_length=7, choices=CHANGE_TYPES, default='Other')

    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    

    objects = models.Manager()
    published = PublishedManager()

    # Meta rule for handling sorting
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]
    
# String function
def __str__(self):
    return self.title