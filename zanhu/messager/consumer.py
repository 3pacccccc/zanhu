import json

from channels.generic.websocket import AsyncWebsocketConsumer


# __author__ = "MaRuiMin"


class MessagesConsumer(AsyncWebsocketConsumer):
    """
    处理私信应用中的websocket请求(异步)
    """
    async def connect(self):
        if self.scope['user'].is_anonymous:
            # 未登陆用户拒绝连接
            await self.close()
        else:
            # 加入聊天组
            await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """
        接收私信
        """
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """
        离开聊天组
        """
        await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)




#
# class MessagesConsumer(AsyncWebsocketConsumer):
#     """
#     处理私信应用中的websocket请求(同步)
#     """
#     def connect(self):
#         if self.scope['user'].is_anoymous:
#             # 未登陆用户拒绝连接
#             self.close()
#         else:
#             # 加入聊天组
#             self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
#             self.accept()
#
#     def receive(self, text_data=None, bytes_data=None):
#         """
#         接收私信
#         """
#         self.send(text_data=json.dumps(text_data))
#
#     def disconnect(self, code):
#         """
#         离开聊天组
#         """
#         self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)
#

# class EchoConsumer(SyncConsumer):
#     """
#     同步Echo
#     """
#     def websocket_connect(self, event):
#         import requests
#         requests.get("url")
#         self.send({
#             "type": "websocket.accept"
#         })
#
#     def websocket_receive(self, event):
#         user = self.scope['user']
#         path = self.scope['path']           # requests请求的路径,http, websocket
#
#         self.send({
#             "type": "websocket.send",
#             "text": event['text']
#         })
#
#
# class EchoAsyncConsumer(AsyncConsumer):
#     """
#     异步Echo
#     """
#     async def websocket_connect(self, event):
#         await self.send({
#             "type": "websocket.accept"
#         })
#
#     async def websocket_receive(self, event):
#
#         # django ORM异步查询语句：
#         # 方法1：
#         # user = User.objects.get(username=username)
#         # from channels.db import database_sync_to_async
#         # user = await database_sync_to_async(User.objects.get(username=username))
#         # 方法二:
#         # @database_sync_to_async
#         # def get_username(username):
#         #     return User.objects.get(username=username)
#
#         await self.send({
#             "type": "websocket.send",
#             "text": event['text']
#         })



