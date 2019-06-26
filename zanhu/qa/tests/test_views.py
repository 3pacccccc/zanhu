import json
from django.test import RequestFactory
from test_plus.test import CBVTestCase
from django.contrib.messages.storage.fallback import FallbackStorage

from zanhu.qa.models import Question, Answer
from zanhu.qa import views

"""
使用TestClient和RequestFactory测试视图的区别：
testclient:走django框架的整个请求响应流程，经过WSGI handler、中间件、URL路由、上下文处理器，返回response
更像是集成测试。特点：使用简单，测试一步到位
requestfactory: 生成WSGIRequest供使用，与django代码无关，单元测试的最佳时间，但使用难度高
"""


class BaseQATest(CBVTestCase):

    def setUp(self):
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')
        self.question_one = Question.objects.create(
            user=self.user,
            title="问题1",
            content="问题1的内容",
            tags="测试1，测试2"
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="问题2",
            content="问题2的内容",
            has_answer=True,
            tags="测试1，测试2"
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="问题2被采纳的回答",
            is_answer=True
        )

        self.request = RequestFactory().get('/fake-url')  # 由于不经过django的url路由，fake-url可以换成任意地址，都可以对视图进行访问
        self.request.user = self.user  # 需要登录才能访问，故赋予request账户


class TestQuestionListView(BaseQATest):
    # 测试QuestionListView

    def get_context_data(self):
        response = self.get(views.QuestionListView, request=self.request)

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context_data['questions'],
                                 map(repr, [self.question_one, self.question_two]), ordered=False)

        self.assertContext('popular_tags', Question.objects.get_counted_tags())

        self.assertContext('active', 'all')


class TestAnsweredQuestionListView(BaseQATest):
    """
    测试已回答问题列表
    """

    def test_context_data(self):
        # response = self.get(views.AnsweredQuestionListView, request=self.request) 方式1
        response = views.AnsweredQuestionListView.as_view()(self.request)  # 方式二，均可

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['questions'], [repr(self.question_two)])
        self.assertEqual(response.context_data['active'], 'answered')  # 对应方式二
        self.assertContext('active', 'answered')  # 对应方式1


class TestUnansweredQuestionListView(BaseQATest):
    """
    测试未回答问题列表
    """

    def test_context_data(self):
        response = self.get(views.UnAnsweredQuestionListView, request=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['questions'], [repr(self.question_one)])
        self.assertContext('active', 'unanswered')


class TestCreateQuestionView(BaseQATest):
    """
    测试创建问题
    """

    def test_get(self):
        response = self.get(views.CreateQuestionVIew, request=self.request)
        self.response_200(response)

        self.assertContains(response, "标题")
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertContains(response, "标签")
        self.assertIsInstance(response.context_data['view'], views.CreateQuestionVIew)

    def get_post(self):
        data = {'title': 'title', 'content': 'content', 'tags': 'tag1,tag2', 'status': 'O'}
        request = RequestFactory().post('/fake-url', data=data)
        request.user = self.user

        # 由于消息要经过django中间件，而RequestFactory不经过中间件，所以去除message
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateQuestionVIew, request=request)
        assert response.status_code == 302
        assert response.url == '/qa/'


class TestQuestionDetailView(BaseQATest):
    """
    测试问题详情
    """

    def get_context_data(self):
        response = self.get(views.QuestionDetailView, request=self.request, pk=self.question_one.id)
        self.response_200(response)
        self.assertEqual(response.context_data['question'], self.question_one)


class TestCreateAnswerView(BaseQATest):
    """
    测试创建回答
    """
    def test_get(self):
        response = self.get(views.CreateAnswerView, request=self.request, question_id=self.question_one.id)
        self.response_200(response)
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertIsInstance(response.context_data['view'], views.CreateAnswerView)

    def test_post(self):
        data = {'content': 'content'}
        request = RequestFactory().post('/fake-url', data=data)
        request.user = self.user

        # 由于消息要经过django中间件，而RequestFactory不经过中间件，所以去除message
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateAnswerView, request=request)
        assert response.status_code == 302
        assert response.url == '/qa/question-detail/{0}'.format(self.question_one.id)


class TestQAVote(BaseQATest):

    def setUp(self):
        super(TestQAVote, self).setUp()
        self.request = RequestFactory().post('/fake-url', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.request.user = self.other_user
        # querydict instance is immutable, request.POST是querydict对象，不可更改，故copy之后可以更改
        self.request.POST = self.request.POST.copy()

    def  test_question_upvote(self):
        """
        赞同问题
        :return:
        """
        self.request.POST['question'] = self.question_one.id
        self.request.POST['value'] = 'U'

        response = views.question_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == 1

    def test_question_downvote(self):
        """
        反对问题
        :return:
        """
        self.request.POST['question'] = self.question_two.id
        self.request.POST['value'] = 'D'

        response = views.question_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1

    def test_answer_upvote(self):
        """
        赞同回答
        :return:
        """
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'U'

        response = views.answer_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == 1

    def test_answer_downvote(self):
        """
        反对回答
        :return:
        """
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'D'

        response = views.question_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1

    def test_accept_answer(self):
        """
        接受回答
        :return:
        """
        self.request.user = self.user
        self.request.POST['answer'] = self.answer.uuid_id

        response = views.accept_answer(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['status'] == 'true'

