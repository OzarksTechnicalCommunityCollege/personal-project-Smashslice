from django import forms

from .models import ChangeRequest, Update, UpdateTag



class ChangeRequestForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = ['subject', 'email', 'request_text']


class UpdateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=UpdateTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Tags",
    )

    class Meta:
        model = Update
        fields = [
            'title', 'slug', 'body', 'major_version', 'current_patch', 'bug_fix',
            'automated_post', 'change_type', 'status', 'author', 'tags'
        ]