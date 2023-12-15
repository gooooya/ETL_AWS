#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import re
import boto3
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder

# DataFrameに読み込み
df = pd.read_sql(sql_query, engine)

# ###  前処理
# ラベルエンコーディングの適用

#レイアウトを変換
labelencoder = LabelEncoder()
df['layout'] = labelencoder.fit_transform(df['layout'])

# 住所を変換。この時地番を削除し、考慮しない
df['address'] = df['address'].str.replace(r'[0-9０-９-－‐]+', '', regex=True)
df['address'] = labelencoder.fit_transform(df['address'])

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


# S3に保存
timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')# ファイル名に使用

# DataFrameをCSVフォーマットの文字列に変換
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

# S3にアップロードするためのクライアントを初期化
s3_client = boto3.client('s3')

# CSVデータをS3にアップロード
bucket_name = os.environ['BUCKET_NAME']  # S3バケット名
file_name = timestamp_str + ".csv"  # S3に保存するファイル名
s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())