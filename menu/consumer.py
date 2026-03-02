from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .signals import menu_status
from django.dispatch import receiver
import json



class MenuWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_menu_status = "menu_status"
        await self.channel_layer.group_add(self.group_menu_status, self.channel_name)
        # new group
        await self.accept()  ######################### Accept for all groups

    async def disconnect(self, close_code):
        # Remove the connection from the 'plc_status' group
        await self.channel_layer.group_discard(self.group_menu_status, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        #print("receive", data)
        # Handle incoming data
        await self.send(text_data=json.dumps({"message": "Received data"}))



    async def send_menu_status(self, event):
        data = event['data']
        # #print('send_plc_status', data)
        await self.send(text_data=json.dumps({
            'menu_status': data
        }))


@receiver(menu_status)
def handle_plc_connected(sender, **kwargs):
    menu_status = kwargs.get("values", {})

    # menu_status =  menu_status.get('data',False

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "menu_status",  # Send to the 'plc_status' group
        {
            "type": "send_menu_status",  # Matches the method name in MyConsumer
            "data": menu_status,
        },
    )




