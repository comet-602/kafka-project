from confluent_kafka import Producer
import sys
import time
import flask
import pandas as pd
import numpy as np
from twitter import *
import pymysql.cursors
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR,INT
import datetime
import t_search
import t_tok

# 用來接收從Producer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)
    

# 主程式進入點
if __name__ == '__main__':
    # 步驟1. 設定要連線到Kafka集群的相關設定
    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': 'localhost:9092',    # <-- 置換成要連接的Kafka集群
        'error_cb': error_cb                        # 設定接收error訊息的callback函數
    }

    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)

    # 步驟3. 指定想要發佈訊息的topic名稱
    topicName = 'twitter'
    msgCount = 100000  # 10萬筆

    try:
        while True:
            #twitter token 需申請，token放別處
            tok=t_tok.t_tok()
            twitter = Twitter(auth = OAuth(tok[0],tok[1],tok[2],tok[3]))

            #設定爬取發文數量
            tweets_count=2

            #設定爬取條件，人名、評論數、喜好數、內文
            statuses = twitter.statuses.user_timeline(screen_name = "@realDonaldTrump",count=tweets_count,tweet_mode='extended')

            created_at=[]
            for data in statuses:
                dt_time=datetime.datetime.strptime(data['created_at'].replace('+0000',''),'%a %b %d %H:%M:%S %Y')
                created_at.append(dt_time)
            #print(created_at)
            retweet=[data['retweet_count'] for data in statuses]
            favorite_count=[data['favorite_count'] for data in statuses]
            text=[data["full_text"].replace("“","_").replace("’","_") for data in statuses]

            value=[]
            value.append(created_at)
            value.append(retweet)
            value.append(favorite_count)
            value.append(text)
            print(value[0])

            value=str(value)
            
            # produce(topic, [value], [key], [partition], [on_delivery], [timestamp], [headers])
            producer.produce(topicName,value=bytes(value,encoding="utf8"))
            time.sleep(180)

    except BufferError as e:
        # 錯誤處理
        sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                         .format(len(producer)))
    except Exception as e:
        print('error:',e)
    # 步驟5. 確認所有在Buffer裡的訊息都己經送出去給Kafka了
    producer.flush(10)
    print('Message sending completed!')
