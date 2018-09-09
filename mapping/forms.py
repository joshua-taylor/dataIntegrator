from django import forms
from mapping.models import Requests, Template, Response

dtypes= [
    ('Text', 'Text'),
    ('Date', 'Date'),
    ('Number', 'Number')
    ]


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields=('field_name','type','desc','max_len','manditory' )
        widgets={
                'field_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the field name'
                }),
                'type': forms.Select(choices=dtypes, attrs={
                'class':'form-control bootstrap-select',
                }),
                'desc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a description'
                }),
                'max_len': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max length allowed'
                }),
                'manditory': forms.CheckboxInput(attrs={
                'class': 'checkbox'
                })
                }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Requests
        fields = ('name', 'desc','send_to','deadline_date')
        labels = {
            'name': 'Title - enter a short title',
            'desc': 'Description - give details on what you are requesting and why here',
            'send_to': 'Send to (enter email addresses seperated by a comma here)',
            'deadline_date': 'Deadline date (format is YYYY-MM-DD)'
        }
        widgets={
                'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Make it snappy - you only have 40 characters!'
                }),
                'desc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a description to let people know what you are requesting and why'
                }),
                'send_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IMPORTANT! Enter valid email addresses here seperated by a comma'
                }),
                'deadline': forms.SelectDateWidget(attrs={
                'placeholder': 'Add a deadline date'
                })
                }


class MappingForm(forms.ModelForm):
    class Meta:
        model = Response
        fields=('mapped_field_name', 'field_name','type','desc','max_len','manditory' )
