from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache

from .models import (
    ChangeRequest,
    ChangeRequestNotification,
    ChangeRequestTag,
    ChangeRequestTagAssignment,
    UpdateChangeRequestLink,
)


STATUS_TAG_MAP = {
    ChangeRequest.Status.PENDING: "pending",
    ChangeRequest.Status.IN_PROGRESS: "in-progress",
    ChangeRequest.Status.DENIED: "denied",
    ChangeRequest.Status.COMPLETED: "complete",
}

DEFAULT_TAGS = [
    {"code": "pending", "label": "Pending"},
    {"code": "in-progress", "label": "In Progress"},
    {"code": "denied", "label": "Denied"},
    {"code": "complete", "label": "Complete"},
]

# Runs after migrations, makes sure we have the expected tags in the changelog app by using get or create
# This does exactly what it sounds like, it checks if a tag exists and creates it if not, making it safe to run every migration
@receiver(post_migrate)
def create_default_change_request_tags(sender, **kwargs):
    if sender.name != "changelog":
        return

    for tag_data in DEFAULT_TAGS:
        ChangeRequestTag.objects.get_or_create(
            code=tag_data["code"], defaults={"label": tag_data["label"]}
        )

# Whenever a changelog request is updated, this checks the previous status, sets it and then marks the instances accepted or completed date
@receiver(pre_save, sender=ChangeRequest)
def capture_status_before_save(sender, instance, **kwargs):
    previous_status = None
    if instance.pk:
        previous_status = (
            sender.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )

    instance._previous_status = previous_status

    if previous_status and previous_status != instance.status:
        if instance.status == ChangeRequest.Status.IN_PROGRESS and not instance.accepted_at:
            instance.accepted_at = timezone.now()
        if instance.status == ChangeRequest.Status.COMPLETED and not instance.completed_at:
            instance.completed_at = timezone.now()

# This is the main notification logic for our tags, we get the previous status
# Checks previous status against current, if they differ, create a change request notification for the requester
@receiver(post_save, sender=ChangeRequest)
def sync_change_request_tags_and_notify(sender, instance, created, **kwargs):
    previous_status = getattr(instance, "_previous_status", None)
    status_changed = created or (previous_status and previous_status != instance.status)
    changed_by = getattr(instance, "_status_changed_by", None)
    related_update = getattr(instance, "_status_source_update", None)

    if not status_changed:
        return

    tag_code = STATUS_TAG_MAP.get(instance.status)
    if tag_code:
        tag = ChangeRequestTag.objects.filter(code=tag_code).first()
        if tag:
            ChangeRequestTagAssignment.objects.create(
                change_request=instance,
                tag=tag,
                assigned_by=changed_by,
            )

    if (
        previous_status
        and previous_status != instance.status
        and instance.requester is not None
    ):
        previous_label = ChangeRequest.Status(previous_status).label
        next_label = instance.get_status_display()
        ChangeRequestNotification.objects.create(
            user=instance.requester,
            change_request=instance,
            related_update=related_update,
            previous_status=previous_status,
            new_status=instance.status,
            message=(
                f"Your change request '{instance.subject}' moved from "
                f"{previous_label} to {next_label}."
            ),
        )
        cache.delete(f'user:{instance.requester_id}:dashboard_notifications')


@receiver(post_save, sender=UpdateChangeRequestLink)
def complete_request_from_update_link(sender, instance, created, **kwargs):
    if not created or not instance.marks_completed:
        return

    change_request = instance.change_request
    if not change_request.can_transition_to(ChangeRequest.Status.COMPLETED):
        return

    change_request.apply_status(ChangeRequest.Status.COMPLETED)
    change_request._status_changed_by = instance.linked_by
    change_request._status_source_update = instance.update
    change_request.save()
