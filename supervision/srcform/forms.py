from django import forms

class SiteForm(forms.Form):
    site_id = forms.CharField(label='id del site',required= True,  max_length= 100)
    site_name = forms.CharField(label='nombre del site', max_length=100)
    site_ip = forms.IntegerField(label = 'ip del site')