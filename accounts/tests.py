from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from feedback.models import Category, Feedback


class StudentProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.student = user_model.objects.create_user(
            username='student-one',
            password='safe-test-password-42',
            role=user_model.Role.STUDENT,
        )
        cls.other_student = user_model.objects.create_user(
            username='student-two',
            password='safe-test-password-42',
            role=user_model.Role.STUDENT,
        )
        cls.new_student = user_model.objects.create_user(
            username='student-three',
            password='safe-test-password-42',
            role=user_model.Role.STUDENT,
        )
        cls.category = Category.objects.get(slug='infrastructure')
        cls.own_feedback = Feedback.objects.create(
            created_by=cls.student,
            category=cls.category,
            kind=Feedback.Kind.PROBLEM,
            title='Моё обращение',
            description='Описание моего обращения.',
        )
        Feedback.objects.create(
            created_by=cls.other_student,
            category=cls.category,
            kind=Feedback.Kind.PROPOSAL,
            title='Чужое обращение',
            description='Описание чужого обращения.',
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )

    def test_student_sees_only_their_own_feedback(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(list(response.context['my_feedback']), [self.own_feedback])
        self.assertContains(response, 'Моё обращение')
        self.assertNotContains(response, 'Чужое обращение')

    def test_student_without_feedback_sees_empty_state(self):
        self.client.force_login(self.new_student)

        response = self.client.get(reverse('accounts:profile'))

        self.assertContains(response, 'Вы ещё не отправляли обращений')
