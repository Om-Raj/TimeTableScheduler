from django import forms

class RunSchedulerForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Confirm running the scheduler",
    )
    time_limit = forms.IntegerField(
        required=True,
        label="Time limit (in seconds)",
        initial=10
    )