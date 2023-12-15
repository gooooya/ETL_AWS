#!/usr/bin/env python
# coding: utf-8

# In[1]:


# DBよりデータ取得

import pandas as pd
from sqlalchemy import create_engine

# PostgreSQLへの接続設定
# 本来環境変数に設定して読み出すべき情報。
# TODO;そもそもDBじゃなくてAthena使ったほうがコスト的に良さそう。AWSに変更するときにデータ取得方法を修正。
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/suumo"
engine = create_engine(DATABASE_URL)

# SQLクエリ
# そもそもこれ最新だけ出すなら古いの消したほうがAWS S3のコスト的にはいい。
sql_query = "WITH getTime AS ("\
            "    SELECT MAX(time) AS latestTime FROM data"\
            ")"\
            "SELECT * FROM data "\
            "WHERE time = (SELECT latestTime FROM getTime);"

# DataFrameに読み込み
df = pd.read_sql(sql_query, engine)

df.head()


# ###  前処理

# In[2]:


# ラベルエンコーディングの適用
from sklearn.preprocessing import LabelEncoder
import numpy as np
import re


# In[3]:


#レイアウトを変換
labelencoder = LabelEncoder()
df['layout'] = labelencoder.fit_transform(df['layout'])


# In[4]:


# 住所を変換。この時地番を削除し、考慮しない
df['address'] = df['address'].str.replace(r'[0-9０-９-－‐]+', '', regex=True)
df['address'] = labelencoder.fit_transform(df['address'])


# In[5]:


# 築年月をyyyymmddに変換
def convert_date_format(date_str):
    match = re.match(r'(\d+)年(\d+)月', date_str)
    if match:
        year, month = match.groups()
        return f"{year}{int(month):02}01"
    else:
        print(date_str)
        return None

df['built_year_month'] = df['built_year_month'].apply(convert_date_format)


# In[6]:


# princeをint形式に変換
def yen_to_int(yen_str):
    match = re.match(r'(?:(\d+)億)?(?:(\d+)万)?(?:(\d+))?円', yen_str)
    if match:
        oku, man, low = match.groups()

        oku = int(oku) if oku else 0  # 億の部分
        man = int(man) if man else 0  # 万の部分
        low = int(low) if low else 0  # 万より後ろの部分

        return oku * 10**8 + man * 10**4 + low  # 合計額を計算

df['price'] = df['price'].apply(yen_to_int)


# In[7]:


df.head()


# In[ ]:





# ### 可視化

# In[8]:


import seaborn as sns


# In[9]:


df[df.isnull().any(axis=1)]


# In[10]:


df.isnull().sum()


# In[11]:


df.describe()


# In[12]:


sns.pairplot(df)


# In[ ]:


from ydata_profiling import ProfileReport

profile = ProfileReport(df)
profile.to_file('EDA.html')

import pandas as pd
import pandas_profiling

# データフレームを作成
data = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': [6, 7, 8, 9, 10]})

# pandas-profilingのProfileReportオブジェクトを作成
profile = pandas_profiling.ProfileReport(data)

# インタラクティブなウィジェットとしてプロファイルレポートを表示
profile.to_widgets()

# ### データ分割

# In[ ]:


from sklearn.model_selection import train_test_split

feature_names = ['area', 'address', 'layout', 'built_year_month']
X = df[feature_names] # station_infoはいったん保留で。
y = df['price']
X_train, X_test,  y_train, y_test = train_test_split(X, y, test_size=0.3)


# In[ ]:


from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def predict(model):
    """
    model:fit済みのモデル
    """
    predicted = model.predict(X_test)
    mse = mean_squared_error(y_test, predicted) 
    result = np.sqrt(mse)# 平方根平均二乗誤差 (RMSE)を返却
    return result


# In[ ]:


from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


# In[ ]:


all_model = [ LogisticRegression(),
              SVC(),
              GaussianNB()
            ]

def alltest_rep(count=10):
    """
    各modelで指定回数分テストし、スコアの平均値と標準偏差を出力
        スコアはテストデータで算出
    トレーニングデータ、テストデータはループごとにランダムに決定される
    """
    for model in all_model:
        score = []
        for j in range(count):
            model.fit(X_train, y_train)
            score.append(predict(model))
        print(f'mean:{np.mean(score):.4f}, std:{np.std(score):.4f}, model:{model}')


# ## Grid Search
%%time
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import load_iris

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search.fit(X_train, y_train)

print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)

# ### Random Search
%%time
from sklearn.model_selection import RandomizedSearchCV
from sklearn.datasets import load_iris
import numpy as np

param_distributions = {
    'n_estimators': np.arange(50, 201, 50),
    'max_depth': [None] + list(np.arange(10, 31, 10)),
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

random_search = RandomizedSearchCV(RandomForestClassifier(), param_distributions, n_iter=50, cv=5)
random_search.fit(X_train, y_train)

print("Best Parameters:", random_search.best_params_)
print("Best Score:", random_search.best_score_)

# ### Bayesian Optimization

# In[ ]:


from skopt import BayesSearchCV
from sklearn.ensemble import RandomForestRegressor

# 所要時間は30分ほど。重いからとりあえず実行しない方向で

param_space = {
    'n_estimators': (50, 200),
    'max_depth': (10, 30),
    'min_samples_split': (2, 10),
    'min_samples_leaf': (1, 4)
}

bayes_search = BayesSearchCV(RandomForestRegressor(), param_space, n_iter=50, cv=5, scoring='neg_root_mean_squared_error')
bayes_search.fit(X, y)

print("Best Parameters:", bayes_search.best_params_)
print("Best Score:", bayes_search.best_score_)

# In[ ]:


# model = RandomForestRegressor(max_depth=bayes_search.best_params_['max_depth'], 
#                                min_samples_leaf=bayes_search.best_params_['min_samples_leaf'],
#                                min_samples_split=bayes_search.best_params_['min_samples_split'], 
#                                n_estimators=bayes_search.best_params_['n_estimators']
#                               )
model = RandomForestRegressor()
model.fit(X_train, y_train)
result = predict(model)
result


# In[ ]:


# 変数の重要度を取得
importances = model.feature_importances_

# 重要度をDataFrameとして表示
feature_importances = pd.DataFrame({'feature': X.columns, 'importance': importances})
print(feature_importances.sort_values(by='importance', ascending=False))

広さ→築年数→住所→レイアウトの順。参考程度に
# In[ ]:


predicted = model.predict(X)


# In[ ]:


import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.graph_objects as go

# Dashアプリの初期化
app = dash.Dash(__name__)

scatter = go.Scatter(x=y, y=predicted, mode='markers', customdata=df['url'], name='Value point')
line = go.Scatter(x=[min(predicted), max(predicted)], y=[min(predicted), max(predicted)], mode='lines', name='correct line') # この線より上なら予想される金額より価値がある(と判断されている)

layout = go.Layout(
    title="金額",
    xaxis=dict(
        title="Actual Value",
        range=[0, max(predicted)+1]  # x軸の範囲を0から最大値までに設定
    ),
    yaxis=dict(
        title="Predicted Value",
        range=[0, max(y)+1000]  # y軸の範囲を0から最大値までに設定
    )
)

app.layout = html.Div([
    dcc.Graph(id='scatter-plot', figure={'data': [scatter, line], 'layout': layout}),
    html.Div(id='hidden-div', style={'display':'none'})
])

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='open_tab'
    ),
    Output('hidden-div', 'children'),
    [Input('scatter-plot', 'clickData')]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)

!jupyter nbconvert --to python Untitled.ipynb --output Transform.py
!jupyter nbconvert --to python Untitled.ipynb --output visualization.py
!jupyter nbconvert --to python Untitled.ipynb --output learn.py
# In[ ]:




