from django import forms
from website.settings import ALGO_TIME_LIMIT

class RunSchedulerForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Confirm running the scheduler",
    )
    time_limit = forms.IntegerField(
        required=True,
        label=f"Time limit (Max: {ALGO_TIME_LIMIT} seconds)",
        initial=10
    )