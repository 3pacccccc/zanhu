from test_plus import TestCase

from zanhu.news.models import News


class NewsModelsTest(TestCase):

    def setUp(self):
        # 创建用户
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')

        # 创建第一条动态
        self.first_news = News.objects.create(
            user=self.user,
            content='第一条动态'
        )

        # 创建第二条动态
        self.second_news = News.objects.create(
            user=self.user,
            content='第二条动态'
        )

        # 第二个用户评论第一条动态
        self.third_news = News.objects.create(
            user=self.other_user,
            content='评论第一条动态',
            reply=True,
            parent=self.first_news
        )

    def test_switch_like(self):
        # 测试点赞功能
        self.first_news.switch_like(self.user)
        assert self.first_news.count_likers() == 1
        assert self.user in self.first_news.get_likers()

        # 测试取消赞功能
        self.first_news.switch_like(self.user)
        assert self.first_news.count_likers() == 0
        assert self.user not in self.first_news.get_likers()

    def test_reply_this(self):
        initial_count = News.objects.count()
        self.first_news.reply_this(self.other_user, '第二次评论第一条动态')
        assert News.objects.count() == initial_count + 1
        assert self.third_news in self.first_news.get_thread()

    def test__str__(self):
        self.assertEqual(self.first_news.__str__(), '第一条动态')
