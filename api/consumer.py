from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .signals import message_signal
from django.dispatch import receiver
import json


class APIWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message = "message"
        # Join the group
        await self.channel_layer.group_add(self.message, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.message, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        #print("receive", data)
        # Echo the received data back to the client
        await self.send(text_data=json.dumps({"message": "Received data"}))

    async def send_new_sms(self, event):
        # data = event['data']
        await self.send(text_data=json.dumps({
            'new_sms': event
        }))


@receiver(message_signal)
def handle_message(sender, **kwargs):
    #print(kwargs)
    values = kwargs.get("values", {})

    #print("Signal received:", values)

    channel_layer = get_channel_layer()

    
    async_to_sync(channel_layer.group_send)(
        "message",  # Send to the 'plc_status' group
        {
            "type": "send_new_sms",  # Matches the method name in MyConsumer
            "data": values,
        },
    )