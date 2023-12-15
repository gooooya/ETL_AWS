import boto3
import time
import datetime
import re
from pyspark.sql.functions import udf, regexp_replace
from pyspark.sql.types import StringType, IntegerType
from pyspark.context import SparkContext
from pyspark.ml.feature import StringIndexer
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame

glueContext = GlueContext(SparkContext.getOrCreate())

def start_crawler(crawler_name):
    glue_client = boto3.client('glue')
    glue_client.start_crawler(Name=crawler_name)

    # クローラの状態をチェックする
    while True:
        crawler_info = glue_client.get_crawler(Name=crawler_name)
        crawler_status = crawler_info['Crawler']['State']
        if crawler_status in ['READY', 'FAILED']:
            break
        time.sleep(60)  # 1分間待機

def run_etl_process():
    # TODO:データカタログのテーブル名を指定。リテラルやめたい
    database_name = 'my_database'
    table_name = 'outputs'

    # データカタログからDynamicFrameを作成
    dynamic_frame = glueContext.create_dynamic_frame.from_catalog(database=database_name, table_name=table_name)

    # ここで必要なデータ変換を実行
    transformed_dynamic_frame = transform_data(dynamic_frame)

    # 変換後のデータをS3に保存するなど、必要な処理を行う
    save_data(transformed_dynamic_frame)

def transform_data(dynamic_frame):
    # データ変換ロジック
    # udf登録
    convert_date = udf(convert_date_udf, StringType())
    yen_to_int = udf(yen_to_int_udf, IntegerType())
    
    # DynamicFrameをDataFrameに変換
    df = dynamic_frame.toDF()

    # ラベルエンコーディングの適用
    indexer = StringIndexer(inputCol="layout", outputCol="layout_indexed")
    df = indexer.fit(df).transform(df)

    # 住所の変換
    df = df.withColumn("address", regexp_replace("address", r'[0-9０-９-－‐]+', ''))
    indexer = StringIndexer(inputCol="address", outputCol="address_indexed")
    df = indexer.fit(df).transform(df)

    # 築年月と価格の変換
    df = df.withColumn("built_year_month", convert_date(df["built_year_month"]))
    df = df.withColumn("price", yen_to_int(df["price"]))

    # DataFrameをDynamicFrameに変換して戻す
    return DynamicFrame.fromDF(df, glueContext, "transformed_df")

# 築年月をyyyymmddに変換するUDF
def convert_date_udf(date_str):
    match = re.match(r'(\d+)年(\d+)月', date_str)
    if match:
        year, month = match.groups()
        return f"{year}{int(month):02}01"
    else:
        return None

# 価格を整数に変換するUDF
def yen_to_int_udf(yen_str):
    match = re.match(r'(?:(\d+)億)?(?:(\d+)万)?(?:(\d+))?円', yen_str)
    if match:
        oku, man, low = match.groups()

        oku = int(oku) if oku else 0
        man = int(man) if man else 0
        low = int(low) if low else 0

        return oku * 10**8 + man * 10**4 + low
    else:
        return 0

def save_data(dynamic_frame):
    # 出力先のS3バケットとパスを指定
    dt_now = datetime.datetime.now()
    output_bucket = 'my-common-output'
    # output_path = 's3://{}/etl_output/{}/'.format(output_bucket, dt_now.strftime('%Y%m%d%H%M%S'))
    output_path = 's3://{}/etl_outputs/'.format(output_bucket)

    # DynamicFrameをS3に書き出す
    glueContext.write_dynamic_frame.from_options(
        frame = dynamic_frame,
        connection_type = 's3',
        connection_options = {'path': output_path},
        format = 'parquet'
    )

def backup_s3_files(source_prefix):
    s3 = boto3.client('s3')
    source_bucket = 'my-common-output'  # ソースバケット名
    dest_bucket   = 'my-common-output'  # 移動先バケット名
    dest_prefix = 'backup/{}'.format(source_prefix)           # 移動先のプレフィックス
    # 指定されたプレフィックスの下にあるオブジェクトをリストアップ
    objects = s3.list_objects_v2(Bucket=source_bucket, Prefix=source_prefix)

    if 'Contents' in objects:
        for obj in objects['Contents']:
            # ファイルの移動先のキーを決定
            old_key = obj['Key']
            new_key = old_key.replace(source_prefix, dest_prefix, 1)
            
            # ファイルを新しい場所にコピー
            s3.copy_object(Bucket=dest_bucket, CopySource={'Bucket': source_bucket, 'Key': old_key}, Key=new_key)
            
            # 元のファイルを削除
            s3.delete_object(Bucket=source_bucket, Key=old_key)

def main():
    start_crawler('my_crawler_before_etl')
    backup_s3_files('etl_outputs')
    run_etl_process()
    backup_s3_files('outputs')
    start_crawler('my_crawler_after_etl')
    
if __name__ == "__main__":
    main()
