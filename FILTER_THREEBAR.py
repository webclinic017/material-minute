import os
import logging
# Filter_ThreeBar
from redisUtil import RedisTimeFrame


class Filter_ThreeBar:
    _MinimumPriceJump = 0.2
    # convert string to integer

    _MinimumPrice = float(os.environ.get(
        'THREEBAR_LIMIT_PRICE_LOW', '5.0'))
    _MaximumPrice = float(os.environ.get(
        'THREEBAR_LIMIT_PRICE_HIGH', '20.0'))
    _MinimumPercent = float(os.environ.get(
        'THREEBAR_LIMIT_PERCENT_LOW', '0.3'))
    _MaximumPercent = float(os.environ.get(
        'THREEBAR_LIMIT_PERCENT_HIGH', '0.7'))

    #
    # return a column in a array matrix
    #

    @staticmethod
    def _column(matrix, i):
        return [row[i] for row in matrix]

    # In 3 bar play, it looks for a pattern like this.
    # price = [2, 4, 3].  There is a sharp rise of price from 2 to 4.
    # and it follows a drop to 3 (or 50% retrace).  This pattern may happen
    # across 3 or 4 bars.  We are looking for that pattern between 3 prices passed in.
    #

    @staticmethod
    def _isFirstTwoBars(price0, price1, price2):
        if (price0 < Filter_ThreeBar._MinimumPrice) or (price0 > Filter_ThreeBar._MaximumPrice):
            return False
        first = price0 - price2
        second = price1 - price2
        if (abs(second) < Filter_ThreeBar._MinimumPriceJump):
            return False
        percentage = 0 if second == 0 else first / second
        if percentage >= Filter_ThreeBar._MinimumPercent and percentage < Filter_ThreeBar._MaximumPercent:
            return True
        return False

    # This is the data format for the Stack.
    @staticmethod
    def barCandidate(firstPrice, secondPrice, timeframe, ts, op):
        return {"indicator": "price",
                "timeframe": timeframe,
                "filter": [firstPrice, secondPrice],
                "timestamp": ts,
                "operation": op
                }

    # It looks for 3 bar patterns on 3 or 4 bars.
    @staticmethod
    def potentialList(symbol, prices, timeframe):
        try:
            timestamp = prices[0][0]
            price0 = prices[0][1]
            price1 = prices[1][1]
            price2 = prices[2][1]
            price3 = prices[3][1]
            if len(prices) > 2 and Filter_ThreeBar._isFirstTwoBars(price0, price1, price2):
                return True, Filter_ThreeBar.barCandidate(price0, price1, timeframe, timestamp, 'ADD')
            elif len(prices) > 3 and Filter_ThreeBar._isFirstTwoBars(price0, price2, price3):
                return True, Filter_ThreeBar.barCandidate(price0, price2, timeframe, timestamp, 'ADD')
            else:
                return False, Filter_ThreeBar.barCandidate(0, 0, timeframe, timestamp, 'DEL')
        except Exception as e:
            logging.error(e)
            return False, Filter_ThreeBar.barCandidate(0, 0, timeframe, prices[0][0], 'DEL')
        # else:
        #     return {'symbol': symbol, 'value': {
        #         'firstPrice': 14.00,
        #         'secondPrice': 15.00,
        #         'thirdPrice': 14.52,
        #     }}

    @staticmethod
    def run(prices, timeframe):
        return Filter_ThreeBar.potentialList("NONE", prices, timeframe)

    @staticmethod
    def closes(prices, timeframe):
        return Filter_ThreeBar.potentialList("NONE", prices, timeframe)


class Filter_3Bars:
    _MinimumPriceJump = 0.2
    # convert string to integer

    _MinimumPrice = float(os.environ.get(
        'THREEBAR_LIMIT_PRICE_LOW', '5.0'))
    _MaximumPrice = float(os.environ.get(
        'THREEBAR_LIMIT_PRICE_HIGH', '20.0'))
    _MinimumPercent = float(os.environ.get(
        'THREEBAR_LIMIT_PERCENT_LOW', '0.3'))
    _MaximumPercent = float(os.environ.get(
        'THREEBAR_LIMIT_PERCENT_HIGH', '0.7'))
    _MinVolume = float(os.environ.get('THREEBAR_LIMIT_VOLUME', '50000'))

    def __init__(self, data, timeframe):
        self.data = data
        self.timeframe = timeframe

    def getColumneData(self, data, column):
        result = []
        for item in data:
            item = (item['t'], item[column])
            result.append(item)
        return result

    def getVolumeData(self, data):
        return self.getColumneData(data, 'v')

    def getCloseData(self, data):
        return self.getColumneData(data, 'c')

    def getCloses(self, dataList=None):
        if (dataList == None):
            dataList = self.data
        closes = self.getCloseData(dataList)

    def getVolumes(self, timeframe, dataList=None):
        if (dataList == None):
            dataList = self.data
        volumes = self.getVolumeData(dataList)

    def priceCheck(self, price0, price1, price2):
        if (price0 < Filter_3Bars._MinimumPrice) or (price0 > Filter_3Bars._MaximumPrice):
            return False
        first = price0 - price2
        second = price1 - price2
        if (abs(second) < Filter_3Bars._MinimumPriceJump):
            return False
        percentage = 0 if second == 0 else first / second
        if percentage >= Filter_3Bars._MinimumPercent and percentage < Filter_3Bars._MaximumPercent:
            return True
        return False

    # This is the data format for the Stack.
    def barCandidate(self, firstPrice, secondPrice, timeframe, ts, op):
        return {"indicator": "price",
                "timeframe": timeframe,
                "filter": [firstPrice, secondPrice],
                "timestamp": ts,
                "operation": op
                }

    # It looks for 3 bar patterns on 3 or 4 bars.
    def closePriceCheck(self, prices, timeframe):
        try:
            price0 = prices[0][1]
            price1 = prices[1][1]
            price2 = prices[2][1]
            price3 = prices[3][1]
            timestamp = prices[0][0]
            if len(prices) > 2 and self.priceCheck(price0, price1, price2):
                return True, self.barCandidate(price0, price1, timeframe, timestamp, 'ADD')
            elif len(prices) > 3 and self.priceCheck(price0, price2, price3):
                return True, self.barCandidate(price0, price2, timeframe, timestamp, 'ADD')
            else:
                return False, self.barCandidate(0, 0, timeframe, timestamp, 'DEL')
        except Exception as e:
            logging.error(e)
            timestamp = prices[0][0]
            return False, self.barCandidate(0, 0, timeframe, timestamp, 'DEL')

    def volumeCheck(self, volumes, timeframe):
        switcher = {
            RedisTimeFrame.MIN1: 1,
            RedisTimeFrame.MIN2: 2,
            RedisTimeFrame.MIN5: 5
        }
        tfMultiple = switcher.get(timeframe)
        v = volumes[0][1]
        minVolume = tfMultiple * Filter_3Bars._MinVolume
        return (len(volumes) > 2 and v > minVolume)

    def run(self, data=None, timeframe=None):
        if data == None:
            data = self.data
        if timeframe == None:
            timeframe = self.timeframe
        volumes = self.getVolumeData(data)
        if (self.volumeCheck(volumes, timeframe)):
            closes = self.getCloseData(data)
            return self.closePriceCheck(closes, timeframe)
        else:
            timestamp = data[0]['t']
            return False, self.barCandidate(0, 0, timeframe, timestamp, 'DEL')
