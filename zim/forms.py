import datetime

from django import forms
from django.forms import SelectDateWidget

from .models import ShippingDetails
years = [year for year in range(datetime.date.today().year-100, datetime.date.today().year-13)]


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    date_of_birth = forms.DateField(
        required=False,
        widget=SelectDateWidget(
            empty_label=('Year', 'Month', 'Day'),
            years=years
        ),

    )
    mobile_number = forms.CharField(max_length=15)


class SaleForm(forms.ModelForm):
    class Meta:
        model = ShippingDetails
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input'


