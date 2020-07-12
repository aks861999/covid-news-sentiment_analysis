from ip2geotools.databases.noncommercial import DbIpCity
import plotly.graph_objects as go
from textblob import TextBlob
import json
import requests
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc

def segment(df):
    counts = df.label.value_counts(normalize=True) * 100
    counts=counts.to_frame()
    counts['col']=counts.index
    counts.sort_values(by=['col'],inplace=True)
    fig = go.Figure(data=[go.Pie(labels=['Negative','Neutral','Positive'], values=counts['label'])])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0),template='plotly_dark')
    positive=list(df[df['label'] ==  1].headlines)
    negative=list(df[df['label'] == -1].headlines)
    return (fig,positive,negative)

def sentiment(headlines):
    df=pd.DataFrame(columns=['headlines','value'])
    for line in range(len(headlines)):
        analysis=TextBlob(headlines[line])
        df.loc[line]=[headlines[line],analysis.sentiment[0]]
    df['label'] = 0
    df.loc[df['value'] > 0, 'label'] = 1
    df.loc[df['value'] < 0, 'label'] = -1
    return(segment(df))

def get_news():
    #########   go to https://newsapi.org/ and grab your api key   ##########
    url=('https://newsapi.org/v2/everything?q=covid19 in india&q=corona virus in india&q=death due to corona in india&apiKey=xxxxxxxxxxxxxxxxxxxxxxx')
    response = requests.get(url)
    y=response.text
    jsonData = json.loads(y)
    z=jsonData['articles']
    z=pd.DataFrame(z)
    f=z['description']
    f=f.dropna(how='all')
    f=f.reset_index(drop=True)
    p=list()

    for i in range(len(f)):
        p.append(f[i])
    
    ########### go to https://smartable.ai to grab your Subscription key ################
    headers = {
    'Subscription-Key': 'xxxxxxxxxxxxxxxxxxxxxxxxxx',
    }

    response = requests.get('https://api.smartable.ai/coronavirus/news/IN', headers=headers)
    
    x=response.text
    jsonData = json.loads(x)

    data=jsonData['news']
    df=pd.DataFrame(data)
    df=df['excerpt']
    for i in range(len(df)):
        p.append(df[i])
    
    return(sentiment(p),'India')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid-News-by-AK'
server=app.server
x=get_news()
    
fig=x[0][0]
pos=x[0][1]
neg=x[0][2]
country_name=x[1]
   
app.layout = html.Div([
    html.Div([
    html.H1(children='COVID-19 Related Realtime News and Sentiment Classification For ('+country_name+')'),
    html.H2(children='The Positive News in '+country_name+' Is\n'),
    ],style={'textAlign': 'center','font-weight': 'bold'}),
    
    html.Div(
    className="trend",
        children=[
            html.Ul(id='my-list', children=[html.Li(i) for i in pos])
        ],
        style={'font-weight': 'bold'}
    ),
        
    html.Br(),
    html.Br(),
    html.Br(),

    html.Div([html.H2(children='The Visualisation Of Sentiment Classification Based On News in '+country_name+' \n')],
    style={'textAlign': 'center','font-weight': 'bold'}),

    html.Div([
    dcc.Graph(figure=fig)],
    style={'background-color': '#1e2130'}),
    
    html.Br(),
    html.Br(),
    html.Br(),

    html.Div([html.H2(children='The Negative News in '+country_name+' Is\n')],style={'textAlign': 'center','font-weight': 'bold'}),
    html.Div(
        className="trend1",
        children=[
            html.Ul(id='my-list1', children=[html.Li(i) for i in neg])
        ],
        style={'font-weight': 'bold'}
    ),
    

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    
    
    html.Div([
    html.Footer(children='Made With 💖 by Akash Biswas, Only for You'),],style={'background-color': '#000000','color':'#f3f5f4','textAlign': 'center','font-weight': 'bold'})
],style={'background-color': '#000000','color':'#f3f5f4'})

if __name__ == '__main__':
    app.run_server(debug=False)
