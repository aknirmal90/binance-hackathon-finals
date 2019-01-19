from django.shortcuts import render
from django.views.generic.base import TemplateView
from forms import QueryForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.models import get_address_risk_metrics
from django.shortcuts import redirect


class QueryFormView(TemplateView):

	template_name = 'form-preconfirm.html'

	def get(self, request):
		context = {'form': QueryForm(), 'risk_score': None}
		return render(request, self.template_name, context)

	def post(self, request):		
		form = QueryForm(request.POST)
		if not form.is_valid():
			context = {'form': QueryForm(), 'risk_score': None}
			return render(request, self.template_name, context)

		address = request.POST['destination_address']
		risk_metrics = get_address_risk_metrics(address)
		risk_score = risk_metrics['risk_score']
		risk_features = risk_metrics['risk_features']

		context = {
			'form': form, 
			'risk_score': risk_score, 
			'risk_features': risk_features,
			'destination_address': address
		}
		return render(request, self.template_name, context)


def api_view(request):
	address = request.GET['destination_address']
	risk_metrics = get_address_risk_metrics(address)
	risk_score = risk_metrics['risk_score']
	risk_features = risk_metrics['risk_features']
	return JsonResponse({
		'risk_score': risk_score,
		'risk_features': risk_features,
	})
