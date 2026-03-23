from django.db import migrations


def remap_legacy_status_codes(apps, schema_editor):
    ChangeRequest = apps.get_model("changelog", "ChangeRequest")

    ChangeRequest.objects.filter(status="R").update(status="P")
    ChangeRequest.objects.filter(status="A").update(status="I")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("changelog", "0002_changerequestnotification_changerequesttag_and_more"),
    ]

    operations = [
        migrations.RunPython(remap_legacy_status_codes, noop_reverse),
    ]
