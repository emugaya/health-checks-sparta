from django import forms
from hc.api.models import Channel


class NameTagsForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    tags = forms.CharField(max_length=500, required=False)

    def clean_tags(self):
        l = []

        for part in self.cleaned_data["tags"].split(" "):
            part = part.strip()
            if part != "":
                l.append(part)

        return " ".join(l)

class PriorityForm(forms.Form):
    priority = forms.IntegerField()

class EscalationMatrixForm(forms.Form):
    enabled = forms.BooleanField()
    interval = forms.IntegerField(min_value=60, max_value=2592000)
    emails = forms.CharField()

class TimeoutForm(forms.Form):
    timeout = forms.IntegerField(min_value=60, max_value=15552000)
    grace = forms.IntegerField(min_value=60, max_value=15552000)


class AddChannelForm(forms.ModelForm):

    class Meta:
        model = Channel
        fields = ['kind', 'value']

    def clean_value(self):
        value = self.cleaned_data["value"]
        return value.strip()

class AddBlogPostForm(forms.Form):
    blog_title = forms.CharField(max_length=200, required=True)
    CHOICES = (
        ("Technology", "Technology"),
        ("Science", "Science"),
        ("Food", "Food"),
        ("Art", "Art"),
        ("Travel", "Travel"),
        ("Health", "Health"),
        ("Education", "Education")
    )
    category = forms.ChoiceField(choices=CHOICES)
    story = forms.CharField(max_length=None, required=True)


class AddWebhookForm(forms.Form):
    error_css_class = "has-error"

    value_down = forms.URLField(max_length=1000, required=False)
    value_up = forms.URLField(max_length=1000, required=False)

    def get_value(self):
        return "{value_down}\n{value_up}".format(**self.cleaned_data)
