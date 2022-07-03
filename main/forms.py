from django import forms


class Emotion_Search(forms.Form):
    search_query = forms.CharField(max_length=200, label="Topic of interest", widget=forms.TextInput(attrs={'placeholder':"Search query"}))
