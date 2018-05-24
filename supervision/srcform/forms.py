from django import forms


CAT_CHOICES = (
    (0, 'No urgente'),
    (1,'semiurgente'),
    (2, 'critica'),
)

class SiteForm(forms.Form):
    site_id = forms.CharField(label='id del site',required= True,  max_length= 100)
    site_name = forms.CharField(label='nombre del site', max_length=100)
    site_ip = forms.CharField(label = 'ip del site', max_length= 50)

    alarm1 = forms.CharField(label = "alarma1", required= False, max_length= 100)
    alarmcat_1 = forms.ChoiceField(choices= CAT_CHOICES)
    alarm2 = forms.CharField(label="alarma2", required=False, max_length=100)
    alarmcat_2 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm3 = forms.CharField(label="alarma3", required=False, max_length=100)
    alarmcat_3 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm4 = forms.CharField(label="alarma4", required=False, max_length=100)
    alarmcat_4 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm5 = forms.CharField(label="alarma5", required=False, max_length=100)
    alarmcat_5 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm6 = forms.CharField(label="alarma6", required=False, max_length=100)
    alarmcat_6 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm7 = forms.CharField(label="alarma7", required=False, max_length=100)
    alarmcat_7 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm8 = forms.CharField(label="alarma8", required=False, max_length=100)
    alarmcat_8 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm9 = forms.CharField(label="alarma9", required=False, max_length=100)
    alarmcat_9 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm10 = forms.CharField(label="alarma10", required=False, max_length=100)
    alarmcat_10 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm11 = forms.CharField(label="alarma11", required=False, max_length=100)
    alarmcat_11 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm12 = forms.CharField(label="alarma12", required=False, max_length=100)
    alarmcat_12 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm13 = forms.CharField(label="alarma13", required=False, max_length=100)
    alarmcat_13 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm14 = forms.CharField(label="alarma14", required=False, max_length=100)
    alarmcat_14 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm15 = forms.CharField(label="alarma15", required=False, max_length=100)
    alarmcat_15 = forms.ChoiceField(choices=CAT_CHOICES)
    alarm16 = forms.CharField(label="alarma16", required=False, max_length=100)
    alarmcat_16 = forms.ChoiceField(choices=CAT_CHOICES)
