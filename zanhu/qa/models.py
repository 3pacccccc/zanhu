import uuid
from collections import Counter

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from taggit.managers import TaggableManager
from slugify import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

User = get_user_model()


@python_2_unicode_compatible
class Vote(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='qa_vote', on_delete=models.CASCADE,
                             verbose_name='用户')
    value = models.BooleanField(default=True, verbose_name='赞同或返回')  # true:赞同， false:反对
    content_type = models.ForeignKey(ContentType, related_name='votes_on', on_delete=models.CASCADE, blank=True,
                                     null=True)
    object_id = models.CharField(max_length=255)
    vote = GenericForeignKey()

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '投票'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'content_type', 'object_id']  # 联合唯一键
        index_together = ('content_type', 'object_id')


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    """自定义QuerySet， 提高模型的可用性"""

    def get_answered(self):
        return self.filter(has_answer=True)

    def get_unanswered(self):
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        """
        统计所有已发表的文章中，每一个标签的数量(大于0的)
        :return:
        """
        tag_dict = {}
        # annotate(tagged=models.Count('tags'))表示根据tag字段来聚和分组
        query = self.all().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1

        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (('O', 'Open'), ('C', 'Close'), ('D', 'Draft'))

    user = models.ForeignKey(User, related_name='q_author', on_delete=models.CASCADE,
                             verbose_name="提问者")
    title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL别名)')
    status = models.CharField(max_length=1, choices=STATUS, default='O', verbose_name='问题状态')
    content = MarkdownxField(verbose_name='内容')
    tags = TaggableManager(help_text='多个标签使用,(英文)隔开', verbose_name='标签')
    has_answer = models.BooleanField(verbose_name='接受回答', default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    votes = GenericRelation(Vote, verbose_name='投票情况')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def get_markdown(self):
        """
        将markdown文本转换成HTML
        """
        return markdownify(self.content)

    def total_votes(self):
        """
        获取得票数
        """
        dic = Counter(self.votes.values_list('value', flat=True))
        votes = dic[True] - dic[False]
        return votes if votes > 0 else 0

    def count_answers(self):
        # 获取所有的回答个数
        return Answer.objects.filter(question=self).count()

    def get_answers(self):
        """
        获取所有的回答
        :return:
        """
        return Answer.objects.filter(question=self)

    def get_upvoters(self):
        """
        赞同的用户
        :return:
        """
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """
        不赞同的用户
        :return:
        """
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accepted_answer(self):
        return Answer.objects.get(is_answer=True, question=self)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='问题')
    user = models.ForeignKey(User, related_name='a_author', on_delete=models.CASCADE,
                             verbose_name='用户')
    content = MarkdownxField(verbose_name='内容')
    is_answer = models.BooleanField(verbose_name='回答是否被接受', default=False)
    votes = GenericRelation(Vote, verbose_name='投票情况')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-is_answer', '-created_at']  # 多字段排序，先排是否为回答，再排创建时间
        verbose_name = '回答'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """
        获取得票数
        """
        dic = Counter(self.votes.values_list('value', flat=True))
        votes = dic[True] - dic[False]
        return votes if votes > 0 else 0

    def get_upvoters(self):
        """
        赞同的用户
        :return:
        """
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """
        不赞同的用户
        :return:
        """
        return [vote.user for vote in self.votes.filter(value=False)]

    def accept_answer(self):
        """
        采纳回答，先将本问题下所有的问题都置为is_answer=False，再将现在的答案置为采纳回答
        :return:
        """
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)

        self.is_answer = True
        self.save()

        self.question.has_answer = True
        self.question.save()


"""
扩展知识：
以知乎为例，假设model.py下面有三个表，娱乐、科技、政治，使得三个表下面的数据保持统一按照时间顺序排列的方法
将三张表返回为一张表，例如想要获得article下面的数据，则可以self.content_object.content
"""


# class Index(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#
#     pub_date = models.DateTimeField()
#
#     class Meta:
#         ordering = ['-pub_date']
#
# class News(models.Model):
#     content = models.CharField(max_length=255)
#     pub_date = models.DateTimeField(auto_now_add=True)
#
# class Article(models.Model):
#     content = models.CharField(max_length=255)
#     pub_date = models.DateTimeField(auto_now_add=True)
#
# class Question(models.Model):
#     title = models.TextField()
#     pub_date = models.DateTimeField(auto_now_add=True)
#
#
# def create_index(sender, instance, **kwargs):
#     if 'created' in kwargs:
#         ct = ContentType.objects.get_for_model(instance)
#         Index.objects.get_or_create(content_type=ct, object_id=instance.id, pub_date=instance.pub_date)
#
# post_save.connect(create_index, sender=News)
# post_save.connect(create_index, sender=Article)
# post_save.connect(create_index, sender=Question)
