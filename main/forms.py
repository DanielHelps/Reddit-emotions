from django import forms


class Emotion_Search(forms.Form):
    search_query = forms.CharField(max_length=200, label="Search query")
    # check = forms.BooleanField(required=False)
