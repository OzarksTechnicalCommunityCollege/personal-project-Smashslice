from django import forms


class RequestChangeForm(forms.Form):
    summary = forms.CharField(max_length=25)
    email = forms.EmailField()
    # For use later once there is more than one project, WIP
    # project = forms.ChoiceField()
    # project = forms.ChoiceWidget()
    request_text = forms.CharField(
        required=False,
        widget=forms.Textarea
    )