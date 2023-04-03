from paho.mqtt import client as mqtt_client
import logging
import time as tt
import random
import json


class VictronMQTTClient:
    __broker = ''
    __port = 0
    __topic = ''
    # generate client ID with pub prefix randomly
    __client_id = f'python-mqtt-{random.randint(0, 1000)}'

    __client = None
    __call_back = None

    __connected = False

    def __init__(self, broker, port, topic, call_back):
        self.__broker = broker
        self.__port = port
        self.__topic = topic
        self.__call_back = call_back

        self.__client = self.connect_mqtt()

    def start(self):
        self.__client.loop_start()


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.__topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        print("Client Got Disconnected")
        if rc != 0:
            print('Unexpected MQTT disconnection. Will auto-reconnect')

        else:
            print('rc value:' + str(rc))

        try:
            print("Trying to Reconnect")
            self.connect_mqtt()
            self.__connected = True
        except Exception as e:
            logging.exception("Error in Retrying to Connect with Broker")
            print("Error in Retrying to Connect with Broker")
            self.__connected = False
            print(e)

    def connect_mqtt(self):
        client = mqtt_client.Client(self.__client_id)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.__call_back
        client.connect(self.__broker, self.__port)

        return client

# def publish(self,client):
    #     msg_count = 0
    #     while True:
    #         time.sleep(1)
    #         msg = f"messages: {msg_count}"
    #         result = client.publish(topic, msg)
    #         # result: [0, 1]
    #         status = result[0]
    #         if status == 0:
    #             print(f"Send `{msg}` to topic `{topic}`")
    #         else:
    #             print(f"Failed to send message to topic {topic}")
    #         msg_count += 1

    # def subscribe(self, client: mqtt_client):
    #     def on_message(client, userdata, msg):
    #         print(
    #             f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    #     client.subscribe(self.topic)
    #     client.on_message = on_message
