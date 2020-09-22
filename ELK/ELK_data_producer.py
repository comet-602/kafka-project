from confluent_kafka import Producer
import sys
import time
from datetime import datetime
import random

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
    producer1 = Producer(props)
    producer2 = Producer(props)
    # 步驟3. 指定想要發佈訊息的topic名稱
    #topicName = 'testdb'

    msgCount = 100000  # 10萬筆

    try:
        num=10
        while True:
            device_id = "001"
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp = round(random.uniform(18, 30), 2)
            humidity = random.randint(0, 100)
            millis = int(round(time.time() * 1000))

            tt = {"device_id": device_id, "timestamp": t, "Temperature": temp, "rd":millis}
            hh = {"device_id": device_id, "timestamp": t, "Humidity": humidity, "rd":millis }
            
            # 產生要發佈到Kafka的訊息
    #         producer1.send(topic="temperature", value=tt)
    #         producer2.send(topic="humidity", value=hh)
            # producer.send(topic=topicName, key=msgKey, value=msgValue)
            producer1.produce(topic="temperature", value=str(tt))
            producer2.produce(topic="humidity", value=str(hh))
            print("Message ts: %s, rd: %s sending completed!"%(t,millis))
            time.sleep(1)
    except BufferError as e:
        # 錯誤處理
        sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                         .format(len(producer)))
    except Exception as e:
        print('error:',e)
    # 步驟5. 確認所有在Buffer裡的訊息都己經送出去給Kafka了
    producer.flush(10)
    print('Message sending completed!')
