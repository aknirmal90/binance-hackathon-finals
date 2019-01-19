from django.shortcuts import render
from django.views.generic.base import TemplateView
from forms import QueryForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.models import get_address_risk_metrics
from django.shortcuts import redirect
from lenders import get_lenders
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models.glyphs import Step
from bokeh.models import ColumnDataSource, Plot, LinearAxis
from bokeh.models.annotations import Title
from graph import nodes_by_address


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
		amount = request.POST['transaction_amount']

		risk_metrics = get_address_risk_metrics(address)
		risk_score = risk_metrics['risk_score']
		risk_features = risk_metrics['risk_features']
		lenders_features = get_lenders(amount=amount)
		script, div = self._components(lenders_features)

		context = {
			'form': form, 
			'risk_score': risk_score, 
			'risk_features': risk_features,
			'script': script,
			'div': div,
			'destination_address': address
		}
		return render(request, self.template_name, context)

	def _components(self, lenders_features):		
		x = [feature[0] for feature in lenders_features]
		y = [feature[1] for feature in lenders_features]

		source = ColumnDataSource(dict(x=x, y=y))
		t = Title()
		t.text = 'Risk Profile for Lenders'

		plot = Plot(
		    title=t, plot_width=500, plot_height=300,
		    h_symmetry=False, v_symmetry=False, min_border=0, toolbar_location=None)

		glyph1 = Step(x="x", y="y", line_color="#f46d43", mode="before")
		plot.add_glyph(source, glyph1)		
		plot.xaxis.ticker = x
		plot.yaxis.ticker = y

		xaxis = LinearAxis(axis_label="Risk Score")
		plot.add_layout(xaxis, 'below')

		yaxis = LinearAxis(axis_label="% Premium Payable")
		plot.add_layout(yaxis, 'left')

		plot.xgrid.grid_line_color = None
		plot.y_range.start = 0
		script, div = components(plot)
		return script, div


def api_view(request):
	address = request.GET['destination_address']
	risk_metrics = get_address_risk_metrics(address)
	risk_score = risk_metrics['risk_score']
	risk_features = risk_metrics['risk_features']
	return JsonResponse({
		'risk_score': risk_score,
		'risk_features': risk_features,
	})

def graph_view(request):
	address = request.GET['destination_address']
	return JsonResponse(nodes_by_address(address), safe=False)
