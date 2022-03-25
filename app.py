import logging
import sys
import time
from multiprocessing import Process
from RedisTimeseriesTable import TimeseriesTable
from EVENT_REALTIME_DATA_01 import RealTimeData
from EVENT_BAR_HANDLE_REALTIME_DATA_02 import EventBarHandleRealtimeData
from EVENT_APP_VSA_03 import EventBarFilterVolumeSpreadAnalysis
from EVENT_BAR_STACK_ADD_04 import RedisStack
from EVENT_BAR_POST_TO_SERVER_05 import EventBarPostToServer


def ThreadRun():
    # multi threading class
    time.sleep(5)  # give the initial connection time to be established
    EventBarHandleRealtimeData.run()
    EventBarFilterVolumeSpreadAnalysis.run()
    RedisStack.run()
    EventBarPostToServer.run()
    while 1:
        time.sleep(1)

def run(isCreateTable=True):
    if (isCreateTable):
        tables = TimeseriesTable()
        tables.run()
    p01 = Process(target=RealTimeData)
    p01.start()
    p02 = Process(target=ThreadRun)
    p02.start()
    while 1:
        time.sleep(1)

if __name__ == "__main__":
    formatter = '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s'
    logging.basicConfig(level=logging.INFO, format=formatter,
                        datefmt='%d-%b-%y %H:%M:%S', filename="three-bar.log")
    logging.warning("app.py started")
    args = sys.argv[1:]
    if len(args) > 0 and (args[0] == "--t" or args[0] == "--table"):
        run(True)
    else:
        run(False)
