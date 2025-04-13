from django import forms

class RunSchedulerForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Confirm running the scheduler",
        help_text="This will assign slots to all sections in the timetable."
    )