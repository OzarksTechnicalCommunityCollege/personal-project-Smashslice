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
            super().get_queryset().filter(status=ChangeRequest.Status.PENDING)
        )
        
# Manager for showing accepted changes
class AcceptedChangeManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=ChangeRequest.Status.IN_PROGRESS)
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

    change_requests = models.ManyToManyField(
        'ChangeRequest',
        through='UpdateChangeRequestLink',
        related_name='updates',
        blank=True,
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
        PENDING = 'P', 'Pending'
        IN_PROGRESS = 'I', 'In Progress'
        DENIED = 'D', 'Denied'
        COMPLETED = 'C', 'Completed'
    
    # Properties
    request_number = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=25)
    email = models.EmailField()
    request_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_requests'
    )
    accepted_at = models.DateTimeField(null=True, blank=True) # We want these to be allowed to be empty as they will update programatically elsewhere
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PENDING
    )

    tags = models.ManyToManyField(
        'ChangeRequestTag',
        through='ChangeRequestTagAssignment',
        related_name='change_requests',
        blank=True,
    )

    ALLOWED_STATUS_TRANSITIONS = {
        Status.PENDING: {Status.IN_PROGRESS, Status.DENIED},
        Status.IN_PROGRESS: {Status.COMPLETED},
        Status.DENIED: set(),
        Status.COMPLETED: set(),
    }
    
    # Managers
    objects = models.Manager()
    accepted_requests = AcceptedChangeManager()
    requested_requests = RequestedChangeManager()
    
    # Meta
    class Meta:
        ordering = ['-updated']
        indexes = [
            models.Index(fields=['-updated'])
        ]
        
    def __str__(self):
        return f'Requested at {self.created}'
    # Only allows specific status' to transition between each other
    def can_transition_to(self, next_status):
        return next_status in self.ALLOWED_STATUS_TRANSITIONS.get(self.status, set())
    # If trying to move from completed > denied it would fail and hit this
    def apply_status(self, next_status):
        if not self.can_transition_to(next_status):
            raise ValueError(
                f'Cannot transition from {self.get_status_display()} '
                f'to {ChangeRequest.Status(next_status).label}.'
            )
        self.status = next_status


class ChangeRequestTag(models.Model):
    code = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=32)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label

# Tag assignment for change requests
class ChangeRequestTagAssignment(models.Model):
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE)
    tag = models.ForeignKey(ChangeRequestTag, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_change_request_tags',
    )

    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['change_request', '-assigned_at']),
        ]

    def __str__(self):
        return f'{self.change_request_id} -> {self.tag.label}'

class ChangeRequestNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='change_request_notifications',
    )
    change_request = models.ForeignKey(
        ChangeRequest,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    related_update = models.ForeignKey(
        Update,
        on_delete=models.SET_NULL,
        related_name='change_request_notifications',
        null=True,
        blank=True,
    )
    previous_status = models.CharField(max_length=1, choices=ChangeRequest.Status)
    new_status = models.CharField(max_length=1, choices=ChangeRequest.Status)
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Notification for {self.user_id} on request {self.change_request_id}'


class UpdateChangeRequestLink(models.Model):
    update = models.ForeignKey(
        Update,
        on_delete=models.CASCADE,
        related_name='change_request_links',
    )
    change_request = models.ForeignKey(
        ChangeRequest,
        on_delete=models.CASCADE,
        related_name='update_links',
    )
    linked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_update_change_requests',
    )
    marks_completed = models.BooleanField(default=False)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-linked_at']
        constraints = [
            models.UniqueConstraint(
                fields=['update', 'change_request'],
                name='unique_update_change_request_link',
            )
        ]
        indexes = [
            models.Index(fields=['change_request', '-linked_at']),
        ]

    def __str__(self):
        return f'Update {self.update_id} -> request {self.change_request_id}'
        
    
# Model for storing synced GitHub commits
class GitHubCommit(models.Model):
    """
    Represents a commit fetched from a GitHub repository for changelog integration.
    Stores commit SHA, message, author, date, and repository info.
    """
    sha = models.CharField(max_length=40, unique=True, help_text="Commit SHA (unique per repo)")
    message = models.TextField(help_text="Commit message")
    author_name = models.CharField(max_length=100, help_text="Author's GitHub username")
    author_email = models.EmailField(blank=True, null=True, help_text="Author's email (if available)")
    date = models.DateTimeField(help_text="Commit date/time (UTC)")
    repo_owner = models.CharField(max_length=100, help_text="GitHub repository owner")
    repo_name = models.CharField(max_length=100, help_text="GitHub repository name")
    raw_data = models.JSONField(blank=True, null=True, help_text="Raw commit data from GitHub API")
    fetched_at = models.DateTimeField(auto_now_add=True, help_text="When this commit was fetched from GitHub")

    class Meta:
        unique_together = ("sha", "repo_owner", "repo_name")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["repo_owner", "repo_name"]),
        ]

    def __str__(self):
        return f"{self.sha[:7]}: {self.message[:50]}... ({self.repo_owner}/{self.repo_name})"