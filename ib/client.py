from ibapi.client import EClient,ClientException
from ibapi.wrapper import EWrapper, OrderId, BarData
from ibapi import __version__ as ibapi_version
import threading
import datetime
import time

class IBClient(EClient, EWrapper):
    """
    Implements the EClient and EWrapper interface.
    Defines methods to handle data received back from IBKR.
    
    Aside from the EClient initialisation, the remaining 
    methods implement the interface from the EWrapper to receive 
    and handle data, which is mandatory when calling corresponding
    req* EClient methods.
    """
    def __init__(self):
        EClient.__init__(self, self)
        self.api_version = ibapi_version
        self.data = []
        self.error_codes = []
        self.earliest_timestamp = None
        self.isHistoricalDataEnded = False

    def nextValidId(self, orderId: OrderId):
        """Receive and store the orderId returned from IBKR"""
        self.orderId = orderId
    
    def nextId(self):
        """Increments the last orderId value"""
        self.orderId += 1
        return self.orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderReject=""):
        """
        Receives errors, warnings and information from IBKR over the socket.
        The response is printed to the terminal including connection state,
        availablity or IBKR API data farms, and response data from the server.
        """
        self.error_codes.append(errorCode)
        print(reqId, errorTime, errorCode, errorString, advancedOrderReject)
    
    def historicalData(self, reqId, bar: BarData):
        """
        Receives historical data from IBKR initiated by the EClient
        reqHistoricalData method, and stores it to the instance.

        The `bar` is of type BarData containing the OHLCV, WAP, and BarCount
        which is the count of trades transacted within a single bar worth of time.
        The date is normalised to datetime isoformat, and the bar data is 
        stored to the instance.
        """
        date = datetime.datetime.fromtimestamp(int(bar.date)).isoformat()
        self.data.append([
            date, 
            bar.open, 
            bar.high, 
            bar.low, 
            bar.close,
            bar.volume, 
            bar.wap, 
            bar.barCount
        ])
    
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical Data Ended for {reqId}. Started at {start}, ending at {end}")
        self.isHistoricalDataEnded = True
        self.cancelHistoricalData(reqId)

    def headTimestamp(self, reqId, headTimeStamp):
        """
        Receives the earliest date/time of historical data that IBKR
        has for the contract. 
        """
        self.earliest_timestamp = int(headTimeStamp)
        self.cancelHeadTimeStamp(reqId)

    def ibapiConnect(self, HOST = "127.0.0.1", PORT = 4002, CLIENT_ID = 0):
        try:
            print("Connecting to IBKR ...")
            self.connect(HOST, PORT, CLIENT_ID)
            print(f"Connected: {HOST}:{PORT}:{CLIENT_ID}")
            threading.Thread(target=self.run).start()
            time.sleep(1)
        except (ClientException, TypeError) as e:
            print(e)

