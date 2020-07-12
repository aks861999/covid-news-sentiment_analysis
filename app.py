import json
import requests
import pandas as pd
import dash
import nltk
nltk.data.path.append('./nltk.txt')
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go

def segment(df):
    ## Form a pandas series with all value counts in the "Label" column in the Dataframe "df" ##
    counts = df.label.value_counts(normalize=True) * 100
    
    ## Convert pandas series to a dataframe ##
    counts=counts.to_frame()
    
    ## Form a column named 'Segment' that consist of '+1', '-1' and  '0'  for positive , negative , neutral respectively ##
    counts['segment']=counts.index
    counts.sort_values(by=['segment'],inplace=True)
    
    ## Build the Figure basically a pie chart with graph object of plotly ## 
    fig = go.Figure(data=[go.Pie(labels=['Negative','Neutral','Positive'], values=counts['label'])])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0),template='plotly_dark')
    
    ## make two lists for positive and negative news ##
    positive=list(df[df['label'] ==  1].headline)
    negative=list(df[df['label'] == -1].headline)
    
    return (fig,positive,negative)


def sentiment(headlines):
    
    
    from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
    sia = SIA()
    
    results = []
    
    
    for line in headlines:
        pol_score = sia.polarity_scores(line)
        pol_score['headline'] = line
        results.append(pol_score)
    
    df = pd.DataFrame.from_records(results)
    
    df['label'] = 0
    df.loc[df['compound'] > 0.17, 'label'] = 1
    df.loc[df['compound'] < -0.17, 'label'] = -1
    
    return(segment(df))


def get_news():
    
    p=list()

    url=('https://gnews.io/api/v3/search?country=in&q=corona&q=covid-19&max=100&token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    response=requests.get(url)
    news=response.text
    jsondata=json.loads(news)
    jsondata['articles']
    df=pd.DataFrame(jsondata)
    for i in range(len(df)):
        p.append(df['articles'][i]['description'])







    #########   go to https://newsapi.org/ and grab your api key   ##########
    url=('https://newsapi.org/v2/everything?q=covid19 in india&q=corona virus in india&q=death due to corona in india&apiKey=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    response = requests.get(url)
    y=response.text
    jsonData = json.loads(y)
    
    z=jsonData['articles']
    z=pd.DataFrame(z)
    f=z['description']
    f=f.dropna(how='all')
    f=f.reset_index(drop=True)
    
    
    
    
    ## form a list that consists of news extarcted from NewsAPI ##
    for i in range(len(f)):
        p.append(f[i])
    
    ########### go to https://smartable.ai to grab your Subscription key ################
    headers = {
    'Subscription-Key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    }

    response = requests.get('https://api.smartable.ai/coronavirus/news/IN', headers=headers)
    
    x=response.text
    jsonData = json.loads(x)

    data=jsonData['news']
    df=pd.DataFrame(data)
    df=df['excerpt']
    
    ## Again add all the news extracted from SmartableAI to the previously created list ##
    for i in range(len(df)):
        p.append(df[i])
    
    ## Go to the 'sentiment' function for sentiment classification ##
    return(sentiment(p),'India')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid-News-by-AK'
server=app.server


## Get the Figure, List of Positive News and Negative News ##
x=get_news()


## the object 'x' gets list consist of a tuple (figure,positive news,negative news) and the country name ##
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
    html.Footer(children='Made With 💖 by Akash Biswas, Only for You'),],style={'background-color': '#0000FF','color':'#f3f5f4','textAlign': 'center','font-weight': 'bold'})
],style={'background-color': '#000000','color':'#f3f5f4'})

if __name__ == '__main__':
    app.run_server(debug=False)
