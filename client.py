import time
from umqtt.robust import MQTTClient
import json
from machine import UART
import select
import ntptime
import utime

uart = UART(1, 9600)                         # init with given baudrate
uart.init(9600, bits=8, rx=16, tx=17, parity=None, stop=1) # init with given parameters
poll = select.poll()
poll.register(uart, select.POLLIN)
buf = []


class Client:
    """
    Represents an MQTT client which publishes temperature data on an interval
    """
    def __init__(self, client_id, server, buf=None, topic=None,
                 **kwargs):
        """
        Instantiates an MQTTClient; connects to the
        MQTT broker.
        Arguments `server` and `client_id` are required.

        :param client_id: Unique MQTT client ID
        :type client_id: str
        :param server: MQTT broker domain name / IP
        :type server: str
        :param topic: Topic to publish temperature on
        :type topic: str
        :param kwargs: Arguments for MQTTClient constructor
        """
        self.buf = None
        self.commsActive = True
        self.errorMsg = {
            "commsErrorRaised": { 
                "C_ID": client_id, 
                "Error": {
                    "Code": 100,
                    "Status": True
                }
            },
            "commsErrorResolved": { 
                "C_ID": client_id, 
                "Error": {
                    "Code": 100,
                    "Status": False
                }
            }
        }
        self.client = MQTTClient(client_id, server, **kwargs)
        if not topic:
            self.topic = 'ebike/' + self.client.client_id
        else:
            self.topic = topic
 
        self.client.connect()
        ntptime.settime()
        self.heartBeatTime = utime.time() #Seconds since epoch
        self.connectionStatusTopic = self.topic + '/connectionStatus'
        self.ebikeDataTopic = self.topic + '/ebikeData'
    def publishData(self, topic, msg):
        """
        Reads the data and publishes it on the configured topic.
        """
        try:
            print("Publishing ", msg," to topic: ", topic)
            self.client.publish(topic, msg)
            pass
        except Exception as e:
            pass
        
    def read_data(self):
        events = poll.poll(1000)
        #print('events =', events)
        bytes_string = uart.readline();
        try:
            jsonstr = str(bytes_string, 'utf-8', 'ignore')
            msg = json.loads(jsonstr);
            if 'RPM' in msg and 'Battery' in msg:
                # msg is in a valid format
                obj = {
                    "C_ID": self.client.client_id,
                    "RPM": msg["RPM"],
                    "Battery": msg["Battery"] 
                }
                self.buf = json.dumps(obj)
                print("Received: ", self.buf)
            else:
                print("Invalid Format!")
        except:
            jsonstr = str(bytes_string, 'utf-8', 'ignore')
            print(jsonstr)
            self.buf = json.dumps(self.errorMsg["commsErrorRaised"])
            self.commsActive = False
        else:
            if (self.commsActive == False):
                self.commsActive = True;
                self.buf = json.dumps(self.errorMsg["commsErrorResolved"])

    def start(self):
        """
        Begins to publish data on an interval (in seconds).
        This function will not exit! Consider using deep sleep instead.
        :param interval: How often to publish temperature data (60s default)
        :type interval: int
        """
        self.heartBeatTime = utime.time()
        self.publishData(self.ebikeDataTopic, self.buf)
        self.publishData(self.connectionStatusTopic, '{\"C_ID\": \"' + str(self.client.client_id)  + '\", \"HeartBeatTime\": \"' + str(self.heartBeatTime) + '\"}')
         



