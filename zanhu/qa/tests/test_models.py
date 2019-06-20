from test_plus import TestCase

from qa.models import Question, Answer


class QAModelTest(TestCase):

    def setUp(self):
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')
        self.question_one = Question.objects.create(
            user=self.user,
            title='问题1',
            content='问题1的内容',
            tags='测试1, 测试2'
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title='问题2',
            content='问题2的内容',
            has_answer=True,
            tags='测试1， 测试2'
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content='问题2的正确回答',
            is_answer=True
        )

    def test_can_vote_question(self):
        """
        给问题投票
        """

        self

    def test_can_vote_answer(self):
        """
        给回答投票
        """

    def test_get_question_voters(self):
        """
        问题的投票用户
        """

    def test_get_answer_voters(self):
        """
        回答的投票用户
        """

    def test_get_question_voters(self):
        """
        问题的投票用户
        """
