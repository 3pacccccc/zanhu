import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

User = get_user_model()


@python_2_unicode_compatible
class MessageQuerySet(models.query.QuerySet):

    def get_conversation(self, sender, recipient):
        """
        用户间的私信会话
        """
        qs_one = self.filter(sender=sender, recipient=recipient)
        qs_two = self.filter(sender=recipient, recipient=sender)
        return qs_one.union(qs_two).order_by('created_at')

    def get_most_recent_conversation(self, recipient):
        """
        获取最近一次私信互动的用户
        """
        try:
            qs_sent = self.filter(sender=recipient)
            qs_recieved = self.filter(recipient=recipient)
            #latest使用需要在Message的class Meta里面定义ordering规则
            qs = qs_sent.union(qs_recieved).latest('created_at')
            if qs.sender == recipient:
                # 如果当前用户有发送消息，则返回消息的接受者
                return qs.recipient
            # 否则返回消息的发送者
            return qs.sender
        except self.model.DoesNotExist:
            # 如果模型实例不存在，返回当前用户
            return User.objects.get(username=recipient.username)


@python_2_unicode_compatible
class Message(models.Model):
    """
    用户间私信
    """
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages', blank=True, null=True, on_delete=models.SET_NULL,
                               verbose_name="消息发送者")
    recipient = models.ForeignKey(User, related_name="received_messages", blank=True, null=True,
                                  on_delete=models.SET_NULL, verbose_name="消息接受者")
    message = models.TextField(blank=True, null=True, verbose_name="内容")
    unread = models.BooleanField(default=True, db_index=True, verbose_name="是否未读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    objects = MessageQuerySet.as_manager()

    class Meta:
        verbose_name = "私信"
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.message

    def make_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

