import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

spacex_data = pd.read_csv('spacex_launch_dash.csv')
complex_options = ([{'label': 'Все стартовые комплексы', 'value': 'all'}] +
                   [{'label': complex, 'value': complex} for complex in spacex_data['Launch Site'].unique()])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H1("SpaceX Launch Data Visualization")
    ], className="header-box"),

    html.Div([
        html.Div([
            html.Label("Выберите стартовые комплексы:")
        ], className="input-box-title"),
        html.Div([
            dcc.Dropdown(
                id='complex-dropdown',
                options=complex_options,
                value='all',
                multi=True,
            )
        ], style={'width': '38em'}),
    ], className="input-box"),

    dcc.Graph(id='pie-chart'),

    html.Label("Выберите диапазон полезной нагрузки:"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=2000,
        value=[0, 10000]
    ),

    dcc.Graph(id='scatter-plot')
])


@app.callback(
    [
        Output('pie-chart', 'figure'),
        Output('complex-dropdown', 'value')
    ],
    Input('complex-dropdown', 'value')
)
def update_pie_chart(selected_complexes):
    if "all" in selected_complexes or selected_complexes == "all":
        filtered_data = spacex_data[["Launch Site", "class"]].where(spacex_data["class"] == 1).dropna()
        filtered_data = filtered_data.groupby("Launch Site").count()
        filtered_data = filtered_data / filtered_data.sum() * 100

        fig = px.pie(filtered_data, names=filtered_data.index, values="class",
                     title='Распределение успешных запусков по всем стартовым комплексам')
        return fig, filtered_data.index.to_list()
    elif len(selected_complexes) == 1:
        filtered_data = spacex_data.where(spacex_data["Launch Site"].isin(selected_complexes)).dropna()
        filtered_data = filtered_data.value_counts("class") / filtered_data["class"].count() * 100

        fig = px.pie(filtered_data, names=filtered_data.index, values="count",
                     title=f'Распределение запусков по комплексу {selected_complexes[0]}')
        return fig, dash.no_update
    else:
        filtered_data = (spacex_data.where(spacex_data["Launch Site"].isin(selected_complexes)).dropna())
        filtered_data = filtered_data[["Launch Site", "class"]].where(filtered_data["class"] == 1).dropna()
        filtered_data = filtered_data.groupby("Launch Site").count()
        filtered_data = filtered_data / filtered_data.sum() * 100

        if len(selected_complexes) == spacex_data["Launch Site"].nunique():
            title='Распределение успешных запусков по всем стартовым комплексам'
        else:
            title = f'Распределение успешных запусков по комплексам {", ".join(selected_complexes)}'

        fig = px.pie(filtered_data, names=filtered_data.index, values="class", title=title)
        return fig, dash.no_update


@app.callback(
    Output('scatter-plot', 'figure'),
    Input('payload-slider', 'value')
)
def update_scatter_plot(payload_range):
    print(payload_range)
    filtered_data = spacex_data[
        (spacex_data['Payload Mass (kg)'] >= payload_range[0]) & (spacex_data['Payload Mass (kg)'] <= payload_range[1])]

    fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color='Launch Site',
                     title='Зависимость успешности запуска от полезной нагрузки')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
