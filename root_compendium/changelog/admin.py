from django.contrib import admin
from .models import (
    ChangeRequest,
    ChangeRequestNotification,
    ChangeRequestTag,
    ChangeRequestTagAssignment,
    UpdateChangeRequestLink,
    Update,
)


class UpdateChangeRequestLinkInline(admin.TabularInline):
    model = UpdateChangeRequestLink
    extra = 0
    readonly_fields = ['linked_at']
from .models import Update, ChangeRequest

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
    inlines = [UpdateChangeRequestLinkInline]


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
    list_display = ['request_number', 'subject', 'email', 'status', 'created']
    list_filter = ['status', 'created', 'accepted_at', 'completed_at']
    search_fields = ['subject', 'email', 'request_text']
