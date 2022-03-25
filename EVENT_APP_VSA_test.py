from unittest import mock, TestCase
from testUtil import TestPublisher
from EVENT_BAR_HANDLE_REALTIME_DATA_02 import EventBarHandleRealtimeData
from RedisTimeseriesTable import TimeseriesTable
from redisUtil import TimeStamp, RedisTimeFrame
from redisTimeseriesData import RealTimeBars
from EVENT_APP_VSA_03 import EventBarFilterVolumeSpreadAnalysis

class TextEventAppVolumeSpreadAnalysis(TestCase):

    def setUp(self) -> None:
        self.app = EventBarFilterVolumeSpreadAnalysis()

    def test_event_bar_candidate_pass(self):
        symbol = 'AAPL'
        period = RedisTimeFrame.MIN15
        data = {'symbol': symbol, 'period': period}
        data = self.app.filterCheck(data)
        self.assertEqual(data, 5)
