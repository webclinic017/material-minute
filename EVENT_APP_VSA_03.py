import logging
from pubsubKeys import PUBSUB_KEYS
from redisPubsub import RedisPublisher, RedisSubscriber
from redisTimeseriesData import RealTimeBars
from redisUtil import RedisTimeFrame
import pandas as pd
from filterVolumeSpreadAnalysis import volumeSpreadAnalysis

class EventBarFilterVolumeSpreadAnalysis:

    def __init__(self, pubKeyStack=None, pubTrade=None):
        # StoreStack: class to access the redis Stack.
        self.publisher = RedisPublisher(
            PUBSUB_KEYS.EVENT_BAR_STACK_ADD) if pubKeyStack is None else pubKeyStack
        self.subscriber = RedisSubscriber(
            PUBSUB_KEYS.EVENT_BAR_FILTER_VSA, None, self.filterCheck)
        self.rtb = RealTimeBars()

    def filterCheck(self, data):
        try:
            symbol = data['symbol']
            period = data['period']
            logging.info(
                f'EventBarFilterVolumeSpreadAnalysis.filterCheck {symbol} - {period} - {data}')
            content = data['data']
            df = pd.DataFrame(content)
            df.rename(columns={'c': 'Close', 'o': 'Open', 'h': 'High', 'l': 'Low', 'v': 'Volume', 't': 'Date'}, inplace=True)
            app = volumeSpreadAnalysis()
            vsa = app.Run(symbol, df)
            self.publisher.publish({'datatype': 'A001', 'symbol': symbol, 'timeframe': period, 'vsa': vsa})
        except Exception as e:
            logging.warning(
                f'Error EventBarFilterVolumeSpreadAnalysis.filterCheck - {data} {e}')

    def start(self):
        try:
            self.subscriber.start()
        except KeyboardInterrupt:
            self.subscriber.stop()
        except Exception as e:
            logging.warning(
                f'Error EventBarFilterVolumeSpreadAnalysis.start - {e}')

    @staticmethod
    def run():
        logging.info(
            'EventBarFilterVolumeSpreadAnalysis.run')
        app = EventBarFilterVolumeSpreadAnalysis()
        app.start()


if __name__ == "__main__":
    pass
