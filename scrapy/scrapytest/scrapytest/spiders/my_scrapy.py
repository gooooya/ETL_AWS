#!/usr/bin/env python
# coding: utf-8

import os
import boto3
import scrapy
import json
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from urllib.parse import urljoin


timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')# ファイル名およびデータ取得年月日に使用
base_url = 'https://suumo.jp'
bucket_path = os.environ['MY_S3_BUCKET_PATH']
s3_client = boto3.client('s3')

class SuumoSpider(scrapy.Spider):
    #
    name = "suumo" 
    start_urls = [
        'https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&ta=13&tj=0&bknlistmodeflg=2&pc=100'
    ]
    # spiderの処理定義
    def parse(self, response):
        for property in response.css('div.property_unit'):
            yield {
                'name': property.css('h2.property_unit-title_wide a::text').get(),
                'price': property.css('span.dottable-value--2::text').get(),
                'area' : property.css('div.dottable-line table tbody tr td dl dd::text').re_first(r'(\d*.\d*?)m'),
                'address': property.css('dt:contains("所在地") + dd::text').get(),
                'station_info' : property.css('dt:contains("沿線・駅") + dd::text').get(),
                'layout' : property.css('dt:contains("間取り") + dd::text').get(),
                'built_year_month' : property.css('dt:contains("築年月") + dd::text').get(),
                'time' : timestamp_str,
                'URL' : urljoin(base_url, property.css('h2.property_unit-title_wide a::attr(href)').get()),
                # 'details': property.css('div.property_inner-info li::text').extract()
            }
            # TODO:主キーを見つけられない。nameは変更されることがある模様。代理キーでは意味がない。このままだと過去の情報と照合できない。
            # TBL結合必要な情報入れるなら代理キー入れる
            # そもそも過去の情報いる？
        next_page = response.css('div.pagination_set p.pagination-parts a:contains("次へ")::attr(href)').get() # 次へボタンのrefに遷移
        if next_page:
            yield response.follow(next_page, self.parse)


def lambda_handler(event='', context=''):
    # クロウラーのプロセス定義。
    # 書いてないオプションは"SUUMO\Scrapy\scrapeTest\scrapeTest\settings.py"を参照。
    # 両方にあるとソース側(ここ)が優先される。
    # 所要時間はDELAY1秒で15分ちょい
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0',
        'FEED_FORMAT': 'csv',
        'FEED_URI': f'file:///tmp/{timestamp_str}.csv',
        'DOWNLOAD_DELAY': 0.01,
        'DEPTH_LIMIT' : 0,
        'CONCURRENT_REQUESTS' : 256
    })

    # クロウラーにspider突っ込んで処理開始
    process.crawl(SuumoSpider) 
    process.start()
    
    # ファイルをS3にアップロード
    with open(f"/tmp/{timestamp_str}.csv", "rb") as f:
        s3_client.upload_fileobj(f, bucket_path, f"outputs/{timestamp_str}.csv")

    return {
        'statusCode': 200,
        'body': json.dumps('Data saved to S3 successfully')
    }

def main():
    lambda_handler()

if __name__ == "__main__":
    main()
