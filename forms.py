from django import forms
from material import Layout, Row


class QueryForm(forms.Form):

    destination_address = forms.CharField(
        label='Destination Address',
        widget=forms.TextInput(attrs={'size': '40'}),
        max_length=100
    )
    transaction_value = forms.CharField(
        label='Amount',
        widget=forms.TextInput(attrs={'size': '40'}),
        max_length=100
    )

    layout = Layout(Row('destination_address', 'transaction_value'),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination_address'].widget.attrs.update({
            'placeholder': 'Destination Address'
        })
        self.fields['transaction_value'].widget.attrs.update({
            'placeholder': 'Amount, ETH'
        })
