# forms.py
from django import forms

class DBUploadForm(forms.Form):
    file = forms.FileField(label="Upload your SQLite DB file (.db)")