from django.forms import ModelForm
from .models import Brokerage

class BrokerageForm(ModelForm):
	class Meta:
		model = Brokerage
		fields = '__all__'