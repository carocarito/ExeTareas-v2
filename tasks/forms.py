from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    weekdays_select = forms.MultipleChoiceField(
        choices=[("0", "Lun"), ("1", "Mar"), ("2", "Mié"), ("3", "Jue"), ("4", "Vie"), ("5", "Sáb"), ("6", "Dom")],
        widget=forms.CheckboxSelectMultiple, required=False, label="Repetir en")

    class Meta:
        model = Task
        fields = ["title", "description", "category", "start_date", "end_date", "start_time", "end_time", "interval_days"]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"}),
                   "start_time": forms.TimeInput(attrs={"type": "time"}), "end_time": forms.TimeInput(attrs={"type": "time"}),
                   "description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk: self.fields["weekdays_select"].initial = self.instance.weekdays.split(",") if self.instance.weekdays else []

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("weekdays_select") and not cleaned.get("interval_days"):
            self.add_error("weekdays_select", "Elige uno o más días, o una periodicidad.")
        if cleaned.get("end_date") and cleaned["end_date"] < cleaned.get("start_date"):
            self.add_error("end_date", "Debe ser posterior a la fecha de inicio.")
        return cleaned

    def save(self, commit=True):
        task = super().save(commit=False); task.weekdays = ",".join(self.cleaned_data["weekdays_select"])
        if commit: task.save()
        return task
