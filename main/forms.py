from django import forms


class Emotion_Search(forms.Form):
    search_query = forms.CharField(max_length=200, label="Search query", widget=forms.TextInput(attrs={'class':"mr-5",'placeholder':"Search query", "cols":"1"}))
    # check = forms.BooleanField(required=False)
