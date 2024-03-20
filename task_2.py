import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
import requests


def get_exchange_rates(base_currency):
    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
    response = requests.get(url)
    data = response.json()
    return data['rates']


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Курсы валют и конвертер"),

    html.Label("Выберите базовую валюту:"),
    dcc.Dropdown(
        id='base-currency-dropdown',
        options=[
            {'label': currency, 'value': currency} for currency in ['USD', 'EUR', 'GBP', 'RUB']
        ],
        value='USD'
    ),

    dcc.Graph(id='exchange-rates-histogram'),

    html.Label("Количество в исходной валюте:"),
    dcc.Input(id='input-amount', type='number', value=1),

    html.Label("Выберите целевую валюту:"),
    dcc.Dropdown(
        id='target-currency-dropdown',
        options=[
            {'label': currency, 'value': currency} for currency in ['USD', 'EUR', 'GBP', 'RUB']
        ],
        value='USD'
    ),

    html.Div(id='converted-amount')
])


@app.callback(
    Output('exchange-rates-histogram', 'figure'),
    Input('base-currency-dropdown', 'value')
)
def update_exchange_rates_histogram(base_currency):
    rates = get_exchange_rates(base_currency)
    df = pd.DataFrame(list(rates.items()), columns=['Валюта', 'Курс'])
    fig = px.histogram(df, x="Валюта", y="Курс", log_y=True)
    fig.update_layout(title=f"Курсы валют относительно {base_currency}", xaxis_title="Валюта", yaxis_title="Курс")
    return fig


@app.callback(
    Output('converted-amount', 'children'),
    [Input('input-amount', 'value'),
     Input('base-currency-dropdown', 'value'),
     Input('target-currency-dropdown', 'value')]
)
def convert_currency(input_amount, base_currency, target_currency):
    if input_amount is None:
        return ''

    rates = get_exchange_rates(base_currency)
    conversion_rate = rates.get(target_currency)

    converted_amount = input_amount * conversion_rate

    return f"{input_amount} {base_currency} = {converted_amount:.2f} {target_currency}"


if __name__ == '__main__':
    app.run_server(debug=True)
