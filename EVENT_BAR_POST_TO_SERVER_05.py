import logging
import requests
import json
from redisPubsub import RedisSubscriber
from pubsubKeys import PUBSUB_KEYS
from environ import EnvFile

class EventBarPostToServer:
    def __init__(self):
        self.subscriber = RedisSubscriber(
            PUBSUB_KEYS.EVENT_BAR_POST_TO_SERVER, None, self.PushToServer)

    def PushToServer(self, content, dest=None):
        print('start push.')
        try:
            url = EnvFile.Get('PUSH_REALTIME_URL', 'https://simp-admin.herokuapp.com/api/realtimes') if dest is None else dest
            url = 'http://localhost:1337/api/realtimes'
            data = content
            r = requests.post(url, json=data)
            # print(f"Status Code: {r.status_code}, Response: {r.json()}")
            logging.info(f"PushToServer. Status Code: {r.status_code}")
            print(f"PushToServer Status Code: {r.status_code}")
        except Exception as e:
            logging.error(f"PushToServer. Exception: {e}")
            print(f"PushToServer. Exception: {e}")

    def start(self):
        try:
            self.subscriber.start()
        except KeyboardInterrupt:
            self.subscriber.stop()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def run():
        logging.info("EVENT_TRADE_ADD.EventBarPostToServer.run")
        candidate = EventBarPostToServer()
        candidate.start()
