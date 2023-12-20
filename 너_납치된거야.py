#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_auth


# In[3]:


# Read the CSV file
df = pd.read_csv('c:/analysis/리얼 찐최종vds사고결합.csv', encoding='cp949')

# Convert '발생년월일시' to datetime format
df['발생년월일시'] = pd.to_datetime(df['발생년월일시'], format='%Y%m%d%H')

# Calculate seasonal death counts
seasonal_traffic_counts = df.groupby('계절')['교통량'].sum()
seasonal_death_counts = df.groupby('계절')['사망자수'].sum()

# Calculate accident ratios by season
season_counts = df['계절'].value_counts()
total_accidents = season_counts.sum()
season_ratios = seasonal_death_counts / seasonal_traffic_counts * 1000


# Calculate monthly death counts
monthly_death_counts = df.resample('M', on='발생년월일시')['사망자수'].sum().reset_index()
monthly_death_counts['Year'] = monthly_death_counts['발생년월일시'].dt.year.astype(str)

# Calculate weekday death counts
weekday_death_counts = df.groupby(df['발생년월일시'].dt.weekday)['사망자수'].sum().reset_index()
weekday_death_counts['weekday'] = weekday_death_counts['발생년월일시'].map({
    0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'
})
weekday_death_counts_sorted = weekday_death_counts.sort_values(by='사망자수', ascending=False)

# Normalize values for plotting
normed_values = (monthly_death_counts['사망자수'] - monthly_death_counts['사망자수'].min()) / (
        monthly_death_counts['사망자수'].max() - monthly_death_counts['사망자수'].min())

# Calculate hourly death counts
hourly_death_counts = df.groupby(df['발생년월일시'].dt.hour)['사망자수'].sum().reset_index()
normed_values_hourly = (hourly_death_counts['사망자수'] - hourly_death_counts['사망자수'].min()) / (
        hourly_death_counts['사망자수'].max() - hourly_death_counts['사망자수'].min())

# Create pie chart
fig_pie = px.pie(season_ratios, labels=season_ratios.index, values=season_ratios.values,
                 title='계절별 사고 비율', template="plotly_dark", names=season_ratios.index)
fig_pie.update_layout(showlegend=True)

# Create bar chart for monthly death counts
fig_bar_monthly = px.bar(monthly_death_counts, x='발생년월일시', y='사망자수',
                         color='Year', color_discrete_sequence=['yellow', 'orange'],
                         labels={'발생년월일시': '월', '사망자수': '사망자 수'},
                         title='월별 사망자수', template="plotly_dark")
fig_bar_monthly.update_layout(showlegend=True)

# Create bar chart for weekday death counts
fig_bar_weekday_sorted = px.bar(weekday_death_counts_sorted, x='weekday', y='사망자수',
                                labels={'weekday': '요일', '사망자수': '사망자 수'},
                                title='요일별 사망자수', template="plotly_dark",
                                color_discrete_sequence=['blue'])
fig_bar_weekday_sorted.update_layout(showlegend=True)

# Create bar chart for hourly death counts
fig_bar_hourly = px.bar(hourly_death_counts, x='발생년월일시', y='사망자수',
                        labels={'발생년월일시': '시간대', '사망자수': '사망자 수'},
                        title='시간대별 사망자수', color=normed_values_hourly,
                        template="plotly_dark", color_continuous_scale='Reds')

# Chart background color
chart_bg_color = '#000000'  # Black background

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the Dash layout
app.layout = html.Div(children=[
    html.Div([
        
        # Dropdown for toggling charts
        dcc.Dropdown(
            id='chart-toggle',
            options=[
                {'label': '계절별 사고 비율', 'value': 'pie'},
                {'label': '월별 사망자수', 'value': 'monthly'},
                {'label': '요일별 사망자수', 'value': 'weekday'},
                {'label': '시간대별 사망자수', 'value': 'hourly'},
            ],
            value=['pie', 'monthly', 'weekday', 'hourly'],
            multi=True,
            style={'position': 'fixed', 'top': 10, 'right': 10, 'width': '23%', 'margin': '5px', 'z-index': '99'}
        ),
    ]),
    html.Div([
        # Pie chart
        dcc.Graph(
            id='seasonal-death-pie-chart',
            figure=fig_pie
        ),
    ], id='pie-chart-container', style={'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}),
    html.Div([
        # Monthly death bar chart
        dcc.Graph(
            id='monthly-death-bar-chart',
            figure=fig_bar_monthly
        ),
    ], id='monthly-chart-container', style={'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}),
    html.Div([
        # Weekday death bar chart
        dcc.Graph(
            id='weekday-death-bar-chart',
            figure=fig_bar_weekday_sorted
        ),
    ], id='weekday-chart-container', style={'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}),
    html.Div([
        # Hourly death bar chart
        dcc.Graph(
            id='hourly-death-bar-chart',
            figure=fig_bar_hourly
        ),
    ], id='hourly-chart-container', style={'width': '100%', 'display': 'inline-block', 'background-color': chart_bg_color}),
])

# Callback to toggle chart visibility
@app.callback(
    [Output('pie-chart-container', 'style'),
     Output('monthly-chart-container', 'style'),
     Output('weekday-chart-container', 'style'),
     Output('hourly-chart-container', 'style')],
    [Input('chart-toggle', 'value')]
)
def toggle_charts(selected_charts):
    styles = [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    for chart in selected_charts:
        if chart == 'pie':
            styles[0] = {'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}
        elif chart == 'monthly':
            styles[1] = {'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}
        elif chart == 'weekday':
            styles[2] = {'width': '33%', 'display': 'inline-block', 'background-color': chart_bg_color}
        elif chart == 'hourly':
            styles[3] = {'width': '100%', 'display': 'inline-block', 'background-color': chart_bg_color}
    return styles

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8056)


# In[3]:


import pandas as pd
import geopandas as gpd
from shapely import wkt
import pydeck as pdk

# 데이터 불러오기
csv_file_path = "c:/analysis/black spot 2021e,s.csv"
df = pd.read_csv(csv_file_path)

# LINESTRING 좌표를 GeoDataFrame으로 변환
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# black-spot 값에 따라 라인 색상 설정
max_spot_value = gdf['black-spot'].max()
min_spot_value = gdf['black-spot'].min()

def calculate_color(value):
    if value == max_spot_value:
        return [255, 0, 0, 255]  # 빨간색
    elif value == min_spot_value:
        return [255, 255, 255, 255]  # 흰색
    else:
        green_to_red_ratio = (value - min_spot_value) / (max_spot_value - min_spot_value)
        green_value = int(255 * (1 - green_to_red_ratio))
        return [255, green_value, 0, 255]

gdf['line_color'] = gdf['black-spot'].apply(calculate_color)

# 'Start or End' 속성에 따라 라인 두께 설정
def calculate_width(row):
    base_width = 2
    if 'E' in row['Start or End']:
        return base_width * 48
    elif 'S' in row['Start or End']:
        return base_width * 38
    else:
        return base_width

gdf['line_width'] = gdf.apply(calculate_width, axis=1)

# black-spot 값이 가장 높은 지점 찾기
max_spot_row = gdf.loc[gdf['black-spot'].idxmax()]
max_spot_point = max_spot_row.geometry.centroid

# 중심 좌표를 black-spot 값이 가장 높은 지점으로 설정
initial_view_state = pdk.ViewState(
    latitude=max_spot_point.y,
    longitude=max_spot_point.x,
    zoom=12  # 확대 레벨 설정
)

# PathLayer 생성
layer = pdk.Layer(
    "PathLayer",
    gdf,
    get_path="geometry.coordinates",
    get_color="line_color",
    get_width="line_width",
    pickable=True,
    auto_highlight=True
)

# Deck 생성
r = pdk.Deck(
    layers=[layer],
    initial_view_state=initial_view_state,
    tooltip={
        "html": "<b>VDS_CD:</b> {VDS_CD}<br><b>Count:</b> {count}<br><b>Speed:</b> {SPD_AVG}<br><b>Traffic Volume:</b> {TRFFCVLM}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
)

# HTML 파일로 렌더링
r.to_html("korea_path2021_layer.html")


# In[4]:


html_file_path = "korea_path2021_layer.html"
with open(html_file_path, "r", encoding="utf-8") as file:
    srcDoc_content = file.read()

# Dash 앱 초기화
app = dash.Dash(__name__)

# 대시보드 레이아웃 정의
app.layout = html.Div([
    html.Iframe(
        id="deck-iframe",
        srcDoc=srcDoc_content,
        style={"width": "100%", "height": "80vh"},
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True,port=8871)


# In[5]:


import pandas as pd
import geopandas as gpd
from shapely import wkt
import pydeck as pdk

# 데이터 불러오기
csv_file_path = "c:/analysis/black spot 2022e,s.csv"
df = pd.read_csv(csv_file_path)

# LINESTRING 좌표를 GeoDataFrame으로 변환
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# black-spot 값에 따라 라인 색상 설정
max_spot_value = gdf['black-spot'].max()
min_spot_value = gdf['black-spot'].min()

def calculate_color(value):
    if value == max_spot_value:
        return [255, 0, 0, 255]  # 빨간색
    elif value == min_spot_value:
        return [255, 255, 255, 255]  # 흰색
    else:
        green_to_red_ratio = (value - min_spot_value) / (max_spot_value - min_spot_value)
        green_value = int(255 * (1 - green_to_red_ratio))
        return [255, green_value, 0, 255]

gdf['line_color'] = gdf['black-spot'].apply(calculate_color)

# 'Start or End' 속성에 따라 라인 두께 설정
def calculate_width(row):
    base_width = 2
    if 'E' in row['Start or End']:
        return base_width * 48
    elif 'S' in row['Start or End']:
        return base_width * 38
    else:
        return base_width

gdf['line_width'] = gdf.apply(calculate_width, axis=1)

# black-spot 값이 가장 높은 지점 찾기
max_spot_row = gdf.loc[gdf['black-spot'].idxmax()]
max_spot_point = max_spot_row.geometry.centroid

# 중심 좌표를 black-spot 값이 가장 높은 지점으로 설정
initial_view_state = pdk.ViewState(
    latitude=max_spot_point.y,
    longitude=max_spot_point.x,
    zoom=12  # 확대 레벨 설정
)

# PathLayer 생성
layer = pdk.Layer(
    "PathLayer",
    gdf,
    get_path="geometry.coordinates",
    get_color="line_color",
    get_width="line_width",
    pickable=True,
    auto_highlight=True
)

# Deck 생성
r = pdk.Deck(
    layers=[layer],
    initial_view_state=initial_view_state,
    tooltip={
        "html": "<b>VDS_CD:</b> {VDS_CD}<br><b>Count:</b> {count}<br><b>Speed:</b> {SPD_AVG}<br><b>Traffic Volume:</b> {TRFFCVLM}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
)

# HTML 파일로 렌더링
r.to_html("korea_path2022_layer.html")


# In[6]:


html_file_path = "korea_path2022_layer.html"
with open(html_file_path, "r", encoding="utf-8") as file:
    srcDoc_content = file.read()

# Dash 앱 초기화
app = dash.Dash(__name__)

# 대시보드 레이아웃 정의
app.layout = html.Div([
    html.Iframe(
        id="deck-iframe",
        srcDoc=srcDoc_content,
        style={"width": "100%", "height": "80vh"},
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True,port=8872)


# In[7]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import pydeck as pdk

# CSV 파일 읽기
CSV_FILE_PATH = "c:/analysis/final.csv"
df = pd.read_csv(CSV_FILE_PATH, encoding='cp949') 

# ScatterplotLayer 정의
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["x좌표값", "y좌표값"],  # x 및 y 좌표값의 열 이름을 사용자의 데이터에 맞게 변경
    get_radius="사상자수",  # 사상자수 열 이름을 사용자의 데이터에 맞게 변경
    radius_scale=30,  # 원하는 크기 조절을 위해 필요한 경우 수정
    radius_min_pixels=5,
    radius_max_pixels=100,
    get_fill_color=[255, 140, 0],
    pickable=True,
    auto_highlight=True,
)

# Deck 정의
deck = pdk.Deck(
    layers=[scatterplot_layer],
    initial_view_state=pdk.ViewState(
        latitude=df["y좌표값"].mean(),  # 데이터에 따라 변경
        longitude=df["x좌표값"].mean(),  # 데이터에 따라 변경
        zoom=10,
        pitch=0,
    ),
   tooltip={"text": "사상자수: {사상자수},사망자수: {사망자수},중상자수: {중상자수}, 경상자수: {경상자수}, 부상신고자수: {부상신고자수}"}
    )
# 렌더링
deck.to_html("scatterplot_layer.html")
html_file_path = "scatterplot_layer.html"
with open(html_file_path, "r", encoding="utf-8") as file:
    srcDoc_content = file.read()

    # CSV 파일 읽기
CSV_FILE_PATH = "c:/analysis/final.csv"
df = pd.read_csv(CSV_FILE_PATH, encoding='cp949') 

# ScatterplotLayer 정의
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["x좌표값", "y좌표값"],  # x 및 y 좌표값의 열 이름을 사용자의 데이터에 맞게 변경
    get_radius="사상자수",  # 사상자수 열 이름을 사용자의 데이터에 맞게 변경
    radius_scale=30,  # 원하는 크기 조절을 위해 필요한 경우 수정
    radius_min_pixels=5,
    radius_max_pixels=100,
    get_fill_color=[255, 140, 0],
    pickable=True,
    auto_highlight=True,
)

# Deck 정의
deck = pdk.Deck(
    layers=[scatterplot_layer],
    initial_view_state=pdk.ViewState(
        latitude=df["y좌표값"].mean(),  # 데이터에 따라 변경
        longitude=df["x좌표값"].mean(),  # 데이터에 따라 변경
        zoom=10,
        pitch=0,
    ),
   tooltip={"text": "사상자수: {사상자수},사망자수: {사망자수},중상자수: {중상자수}, 경상자수: {경상자수}, 부상신고자수: {부상신고자수}"}
    )
# 렌더링
deck.to_html("scatterplot_layer.html")
html_file_path = "scatterplot_layer.html"
with open(html_file_path, "r", encoding="utf-8") as file:
    srcDoc_content = file.read()


# In[8]:


# Dash 앱 초기화
app = dash.Dash(__name__)

# 대시보드 레이아웃 정의
app.layout = html.Div([
    html.Iframe(
        id="deck-iframe",
        srcDoc=srcDoc_content,
        style={"width": "100%", "height": "80vh"},
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True,port=8870)


# In[10]:


import dash
from dash import dcc, html

# Function to read HTML content from file
def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Read HTML content for each PyDeck visualization
srcDoc_content_2021 = read_html_file("korea_path2021_layer.html")
srcDoc_content_2022 = read_html_file("korea_path2022_layer.html")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the dashboard layout with two tabs
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='2021년 고속도로 black-spot', children=[
            html.Iframe(
                id="iframe-2021",
                srcDoc=srcDoc_content_2021,
                style={"width": "100%", "height": "80vh"}
            )
        ]),
        dcc.Tab(label='2022년 고속도로 black-spot', children=[
            html.Iframe(
                id="iframe-2022",
                srcDoc=srcDoc_content_2022,
                style={"width": "100%", "height": "80vh"}
            )
        ]),
        dcc.Tab(label='사망지점 분석', children=[
            html.Iframe(
                id="iframe-death-analysis",
                srcDoc=srcDoc_content,  # 이 부분에서 두 번째 코드의 HTML 내용을 사용
                style={"width": "100%", "height": "80vh"}
            )
        ]),
    ])
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8850)


# In[11]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Import other necessary libraries
import pandas as pd
import plotly.express as px
from shapely.wkt import loads as wkt_loads
import geopandas as gpd
import pydeck as pdk
import dash_auth

# Set up username and password
VALID_USERNAME_PASSWORD_PAIRS = {'urban': '1012'}

# Add basic authentication
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# Read the CSV file for PyDeck visualization
csv_file_path = "c:/analysis/black spot 2021e,s.csv"
df = pd.read_csv(csv_file_path)
df['geometry'] = df['geometry'].apply(wkt_loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')
max_spot_value = gdf['black-spot'].max()
min_spot_value = gdf['black-spot'].min()

def calculate_color(value):
    if value == max_spot_value:
        return [255, 0, 0, 255]  # Red
    elif value == min_spot_value:
        return [255, 255, 255, 255]  # White
    else:
        green_to_red_ratio = (value - min_spot_value) / (max_spot_value - min_spot_value)
        green_value = int(255 * (1 - green_to_red_ratio))
        return [255, green_value, 0, 255]

gdf['line_color'] = gdf['black-spot'].apply(calculate_color)

def calculate_width(row):
    base_width = 2
    if 'E' in row['Start or End']:
        return base_width * 48
    elif 'S' in row['Start or End']:
        return base_width * 38
    else:
        return base_width

gdf['line_width'] = gdf.apply(calculate_width, axis=1)

max_spot_row = gdf.loc[gdf['black-spot'].idxmax()]
max_spot_point = max_spot_row.geometry.centroid

initial_view_state = pdk.ViewState(
    latitude=max_spot_point.y,
    longitude=max_spot_point.x,
    zoom=12
)

layer = pdk.Layer(
    "PathLayer",
    gdf,
    get_path="geometry.coordinates",
    get_color="line_color",
    get_width="line_width",
    pickable=True,
    auto_highlight=True
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=initial_view_state,
    tooltip={
        "html": "<b>VDS_CD:</b> {VDS_CD}<br><b>Count:</b> {count}<br><b>Speed:</b> {SPD_AVG}<br><b>Traffic Volume:</b> {TRFFCVLM}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
)

r.to_html("korea_path2021_layer.html")

srcDoc_content_2021 = read_html_file("korea_path2021_layer.html")

# Read the CSV file for death analysis
df = pd.read_csv('c:/analysis/final.csv', encoding='cp949')
df['발생년월일시'] = pd.to_datetime(df['발생년월일시'], format='%Y%m%d%H')

season_counts = df['계절'].value_counts()
total_accidents = season_counts.sum()
season_ratios = season_counts / total_accidents * 100
seasonal_death_counts = df.groupby('계절')['사망자수'].sum()

monthly_death_counts = df.resample('M', on='발생년월일시')['사망자수'].sum().reset_index()
monthly_death_counts['Year'] = monthly_death_counts['발생년월일시'].dt.year.astype(str)

weekday_death_counts = df.groupby(df['발생년월일시'].dt.weekday)['사망자수'].sum().reset_index()
weekday_death_counts['weekday'] = weekday_death_counts['발생년월일시'].map({
    0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'
})
weekday_death_counts_sorted = weekday_death_counts.sort_values(by='사망자수', ascending=False)

normed_values = (monthly_death_counts['사망자수'] - monthly_death_counts['사망자수'].min()) / (
        monthly_death_counts['사망자수'].max() - monthly_death_counts['사망자수'].min())

hourly_death_counts = df.groupby(df['발생년월일시'].dt.hour)['사망자수'].sum().reset_index()
normed_values_hourly = (hourly_death_counts['사망자수'] - hourly_death_counts['사망자수'].min()) / (
        hourly_death_counts['사망자수'].max() - hourly_death_counts['사망자수'].min())

fig_pie = px.pie(season_ratios, labels=season_ratios.index, values=season_ratios.values,
                 title='계절별 사고 비율', template="plotly_dark", names=season_ratios.index)
fig_pie.update_layout(showlegend=True)

fig_bar_monthly = px.bar(monthly_death_counts, x='발생년월일시', y='사망자수',
                         color='Year', color_discrete_sequence=['yellow', 'orange'],
                         labels={'발생년월일시': '월', '사망자수': '사망자 수'},
                         title='월별 사망자수', template="plotly_dark")
fig_bar_monthly.update_layout(showlegend=True)

fig_bar_weekday_sorted = px.bar(weekday_death_counts_sorted, x='weekday', y='사망자수',
                                labels={'weekday': '요일', '사망자수': '사망자 수'},
                                title='요일별 사망자수', template="plotly_dark",
                                color_discrete_sequence=['blue'])
fig_bar_weekday_sorted.update_layout(showlegend=True)

fig_bar_hourly = px.bar(hourly_death_counts, x='발생년월일시', y='사망자수',
                        labels={'발생년월일시': '시간대', '사망자수': '사망자 수'},
                        title='시간대별 사망자수', color=normed_values_hourly,
                        template="plotly_dark", color_continuous_scale='Reds')

app = dash.Dash(__name__)

# ... (Previous code)

# Define the dashboard layout with two dropdowns
# ... (이전 코드)

# Define the dashboard layout with two dropdowns
app.layout = html.Div([
    html.H1("고속도로 사망교통사고 분석", style={'text-align': 'center'}),  # 제목 추가
    html.H6("made by. 너 납치된거야 조", style={'text-align': 'center'}),  # 작은 부제목 추가
    html.Div(
        children=[
            # 드롭다운 박스와 차트를 각각 별도의 Div로 감싸서 레이아웃 조정
            html.Div(
                dcc.Dropdown(
                    id='analysis-type-dropdown',
                    options=[
                        {'label': '블랙스팟', 'value': 'black-spot'},
                        {'label': '사망데이터 분석', 'value': 'death-analysis'},
                    ],
                    value='black-spot',  # Default selected value
                    style={'width': '100%', 'margin': '5px'}
                ),
                style={'float': 'right', 'width': '30%', 'margin-right': '5px', 'margin-top': '5px'}
            ),
            html.Div(
                dcc.Dropdown(
                    id='chart-dropdown',
                    value=['black-spot-2021'],  # Default selected values
                    multi=True,
                    style={'width': '100%', 'margin': '2px', 'height': '3px'}
                ),
                style={'float': 'right', 'width': '30%', 'margin-right': '5px', 'margin-top': '5px'}
            ),
        ],
        style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between'}
    ),
    html.Div(id='chart-container')
])

# ... (이후 코드)


# ... (Remaining code)
# ... (Previous code)

# Define callback to update options of the second dropdown
@app.callback(
    [Output('chart-dropdown', 'options'),
     Output('chart-dropdown', 'value')],
    [Input('analysis-type-dropdown', 'value')]
)
def update_chart_dropdown_options(selected_analysis_type):
    options = []
    value = []

    if selected_analysis_type == 'black-spot':
        options.extend([
            {'label': '21년 블랙스팟', 'value': 'black-spot-2021'},
            {'label': '22년 블랙스팟', 'value': 'black-spot-2022'},
            {'label': '사망지점 분석', 'value': 'death-analysis'},
        ])
        value = ['black-spot-2021']
    elif selected_analysis_type == 'death-analysis':
        options.extend([
            {'label': '파이차트', 'value': 'pie-chart'},
            {'label': '시간대별 바차트', 'value': 'hourly-bar-chart'},
            {'label': '요일별 바차트', 'value': 'weekday-bar-chart'},
            {'label': '월별 바차트', 'value': 'monthly-bar-chart'},
        ])
        value = ['pie-chart']

    return options, value

# Define callback to update charts based on selections
@app.callback(
    Output('chart-container', 'children'),
    [Input('analysis-type-dropdown', 'value'),
     Input('chart-dropdown', 'value')]
)
def update_charts(analysis_type, selected_charts):
    chart_components = []

    if analysis_type == 'black-spot':
        for chart in selected_charts:
            if chart in ['black-spot-2021', 'black-spot-2022']:
                chart_components.append(
                    html.Iframe(
                        id=f"iframe-{chart}",
                        srcDoc=globals().get(f"srcDoc_content_{chart[-4:]}"),  # Get srcDoc_content dynamically
                        style={"width": "100%", "height": "80vh"}
                    )
                )
            elif chart == 'death-analysis':
                chart_components.extend([
                    html.Iframe(
                        id="deck-iframe",
                        srcDoc=globals().get("srcDoc_content"),
                        style={"width": "100%", "height": "50vh"},  # Adjust height as needed
                    ),
                ])

    elif analysis_type == 'death-analysis':
        for chart in selected_charts:
            if chart == 'pie-chart':
                chart_components.append(
                    dcc.Graph(
                        id='seasonal-death-pie-chart',
                        figure=fig_pie,
                        style={'width': '33%', 'display': 'inline-block'}  # Adjust width and margin as needed
                    )
                )
            elif chart == 'monthly-bar-chart':
                chart_components.append(
                    dcc.Graph(
                        id='monthly-death-bar-chart',
                        figure=fig_bar_monthly,
                        style={'width': '34%', 'display': 'inline-block'}  # Adjust width and margin as needed
                    )
                )
            elif chart == 'weekday-bar-chart':
                chart_components.append(
                    dcc.Graph(
                        id='weekday-death-bar-chart',
                        figure=fig_bar_weekday_sorted,
                        style={'width': '33%', 'display': 'inline-block'}  # Adjust width as needed
                    )
                )
            elif chart == 'hourly-bar-chart':
                chart_components.append(
                    dcc.Graph(
                        id='hourly-death-bar-chart',
                        figure=fig_bar_hourly,
                        style={'width': '100%', 'float': 'left'}  # Full width and float left
                    )
                )

    return chart_components



if __name__ == '__main__':
    app.run_server(debug=True, port=8879)

