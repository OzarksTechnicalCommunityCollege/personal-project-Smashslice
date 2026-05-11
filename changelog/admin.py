from django.contrib import admin, messages
from .models import (
    ChangeRequest,
    ChangeRequestNotification,
    ChangeRequestTag,
    ChangeRequestTagAssignment,
    UpdateChangeRequestLink,
    Update,
    GitHubCommit,
    UpdateTag,
    UpdateUpdateTagAssignment,
)
from .services.github_api import GitHubAPIService

class UpdateUpdateTagAssignmentInline(admin.TabularInline):
    model = UpdateUpdateTagAssignment
    extra = 0
    readonly_fields = ['assigned_at']



class UpdateChangeRequestLinkInline(admin.TabularInline):
    model = UpdateChangeRequestLink
    extra = 0
    readonly_fields = ['linked_at']

# Render updates on admin page for update creation and editing

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [UpdateChangeRequestLinkInline, UpdateUpdateTagAssignmentInline]
@admin.register(UpdateTag)
class UpdateTagAdmin(admin.ModelAdmin):
    list_display = ['label', 'code']
    search_fields = ['label', 'code']


class ChangeRequestTagAssignmentInline(admin.TabularInline):
    model = ChangeRequestTagAssignment
    extra = 0
    readonly_fields = ['assigned_at']


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'subject', 'status', 'email', 'updated']
    list_filter = ['status', 'updated', 'created']
    search_fields = ['subject', 'email', 'request_text']
    readonly_fields = ['created', 'updated', 'accepted_at', 'completed_at']
    inlines = [ChangeRequestTagAssignmentInline]
    ordering = ['-updated']


@admin.register(ChangeRequestTag)
class ChangeRequestTagAdmin(admin.ModelAdmin):
    list_display = ['label', 'code']
    search_fields = ['label', 'code']


@admin.register(ChangeRequestNotification)
class ChangeRequestNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'change_request', 'related_update', 'previous_status', 'new_status', 'created', 'is_read']
    list_filter = ['is_read', 'new_status', 'created']
    search_fields = ['message', 'user__username', 'change_request__subject']
    ordering = ['-created']


@admin.register(UpdateChangeRequestLink)
class UpdateChangeRequestLinkAdmin(admin.ModelAdmin):
    list_display = ['update', 'change_request', 'marks_completed', 'linked_by', 'linked_at']
    list_filter = ['marks_completed', 'linked_at']
    search_fields = ['update__title', 'change_request__subject']
    ordering = ['-linked_at']


@admin.register(GitHubCommit)
class GitHubCommitAdmin(admin.ModelAdmin):
    list_display = [
        'sha', 'message', 'author_name', 'date', 'repo_owner', 'repo_name', 'fetched_at'
    ]
    search_fields = ['sha', 'message', 'author_name', 'repo_owner', 'repo_name']
    list_filter = ['repo_owner', 'repo_name', 'date']
    ordering = ['-date']
    actions = ['sync_github_commits']

    def sync_github_commits(self, request, queryset):
        """
        Admin action to fetch and store recent commits from a configured GitHub repository.
        """
        # For demonstration purposes, hardcoded repo
        owner = 'Smashslice'  # TODO: Make dynamic/configurable
        repo = 'Changelog'  # TODO: Make dynamic/configurable
        service = GitHubAPIService()
        try:
            commits = service.fetch_commits(owner, repo, per_page=10)
            created, skipped = 0, 0
            for c in commits:
                sha = c['sha']
                defaults = {
                    'message': c['commit']['message'],
                    'author_name': c['commit']['author'].get('name', ''),
                    'author_email': c['commit']['author'].get('email', ''),
                    'date': c['commit']['author']['date'],
                    'repo_owner': owner,
                    'repo_name': repo,
                    'raw_data': c,
                }
                obj, was_created = GitHubCommit.objects.get_or_create(
                    sha=sha, repo_owner=owner, repo_name=repo, defaults=defaults
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
            self.message_user(request, f"Fetched {created} new commits, {skipped} already existed.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error fetching commits: {e}", messages.ERROR)
    sync_github_commits.short_description = "Sync latest commits from GitHub (demo repo)"

# admin.site.register(GitHubCommit, GitHubCommitAdmin)
