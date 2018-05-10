from django import forms

class SiteForm(forms.Form):
    site_id = forms.CharField(label='nombre del site',required= True,  max_length= 100)
    site_name = forms.CharField(label='nombre del site', max_length=100)