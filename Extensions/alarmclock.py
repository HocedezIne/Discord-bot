from email import message
from urllib import response
from discord.ext import commands
import paho.mqtt.client as mqtt
from json import loads, dumps
import pickle
import logging
import os

datapath = os.path.join(os.path.dirname(__file__),'../data/alarms.pickle')
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# mqtt functions
def on_connect(client, userdata,flags, rc):
    logging.info(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("data-requests")
    client.subscribe("alarm-altered-data")

def on_message(client, userdata, msg):
    if msg._topic == "data-requests":
        data = __read_file()
        client.publish("alarmclock/data", dumps(data))

    if msg._topic == "alarm-altered-data":
        message = loads(msg.payload.decode("utf-8", "ignore"))
        __write_file(message)

# discord class
class Alarmclock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # mqtt initialization
        self.mqttclient = mqtt.Client()
        self.mqttclient.on_connect = on_connect
        self.mqttclient.on_message = on_message
        # self.mqttclient.connect(os.getenv('MQTT_BROKER_IP'), int(os.getenv('MQTT_BROKER_PORT')))

    # file control
    def __read_file(self):
        return pickle.load(open(datapath, "rb"))

    def __write_file(self, data):
        pickle.dump(data, open(datapath, "wb"))


    @commands.command(name='add', help='Adds given time to list of alarms')
    async def add_alarm(self, ctx, time:str, repeats:bool, *dates):
        time = ":".join([i.zfill(2) for i in time.split(":")]) # reformat time

        # validate dates
        requested = []
        if dates[0] == "": requested = weekdays
        else: [requested.append(day) if day in weekdays else await ctx.reply(f'{day} is not recognised. Maybe check your spelling.') for day in dates]

        # check for existing data
        alarmlist = self.__read_file()
        print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA {alarmlist}")
        for new in requested:
            i = {"day":new, "time":time, "repeats":repeats}
            if i not in alarmlist:
                alarmlist.append(i)
            
        self.__write_file(alarmlist)

        # discord reply
        response = f'{time} on {",".join(requested)} and alarm will {"not" if repeats == False else ""} repeat'
        await ctx.reply(f'Added {response}')

        # mqtt publish
        # self.mqttclient.publish("data", dumps(alarmlist))

    @commands.command(name='del', help="Remove specified alarm")
    async def del_alarm(self, ctx, time, *dates):
        if time == "*":
            data = []
            self.__write_file(data)
            response = "all alarms"
        else:
            time = ":".join([i.zfill(2) for i in time.split(":")])

            # validate dates
            requested = []
            if dates[0] == "": requested = weekdays
            else: [requested.append(day) if day in weekdays else await ctx.reply(f'{day} is not recognised. Maybe check your spelling.') for day in dates]

            # if in list yeet
            alarmlist = self.__read_file()
            for day in requested:
                if {"day":day, "time":time, "repeats":True} in alarmlist: alarmlist.remove({"day":day, "time":time, "repeats":True})
                elif {"day":day, "time":time, "repeats":False} in alarmlist: alarmlist.remove({"day":day, "time":time, "repeats":False})

            self.__write_file(alarmlist)
            response = f'{time} on {",".join(requested)}'

        await ctx.reply(f'Removed {response}')

    @commands.command(name='list', help="List all saved alarms")
    async def list_alarms(self, ctx):
        data = self.__read_file()

        response = ""
        for alarm in data:
            response += f"{alarm['day']} at {alarm['time']}, {'not' if alarm['repeats'] == False else ''} repeating\n"

        await ctx.reply(response if response else "No alarms set")


def setup(bot):
    bot.add_cog(Alarmclock(bot))