import json

from channels.generic.websocket import AsyncWebsocketConsumer


# __author__ = "MaRuiMin"


class NotificationsConsumer(AsyncWebsocketConsumer):
    """
    处理通知应用中的WebSoket请求
    """

    async def connect(self):
        if self.scope['user'].is_anonymous:
            # 未登陆用户拒绝连接
            await self.close()
        else:
            await self.channel_layer.group_add("notifications", self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps(text_data))
