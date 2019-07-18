from django.urls import path

__author__ = "A$ AP xiaoma"

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# AuthMiddlewareStack用于websocket认证，继承了cookiemiddleware，sessionmiddleware， authmiddleware，兼容django认证系统

from zanhu.messager.consumer import MessagesConsumer

# self.scope['type']获取协议类型
# self.scope['url_route']['kwargs']['username']获取url中关键字参数
# channels routing是scope级别的，一个连接只能由一个consumer接收和处理

# AllowedHostsOriginValidator可以防止csrf攻击，直接读取setting里面的allowhosts参数
# OriginValidator需要自己添加allowhosts。如：
# application = ProtocolTypeRouter({
#     "websocket": OriginValidator(
#         AuthMiddlewareStack(
#             URLRouter([
#                 path('ws/<str:username>/', MessagesConsumer)
#             ])
#         ),
#         [".imooc.com", "http://.imooc.com:80", "http://muke.site.com"]
#     )
# })


application = ProtocolTypeRouter({
    # 普通的HTTP请求不需要我们手动在这里添加，框架会自动加载
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # path('ws/notifications/', NotificationsConsumer),
                path('ws/<str:username>/', MessagesConsumer)
            ])
        )
    )
})
