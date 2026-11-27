from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Feedback, StatusHistory


class FeedbackSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = get_user_model().objects.create_user(
            username='student',
            password='safe-test-password-42',
            role='student',
        )
        cls.category = Category.objects.get(slug='infrastructure')

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('feedback:create'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('feedback:create')}",
        )

    def test_student_can_submit_feedback(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse('feedback:create'), {
            'kind': Feedback.Kind.PROBLEM,
            'category': self.category.pk,
            'title': 'Освещение в аудитории',
            'description': 'Не работает свет в аудитории 12.',
            'location': 'Корпус A, аудитория 12',
            'is_anonymous': 'on',
        })

        self.assertRedirects(response, reverse('home'))
        feedback = Feedback.objects.get(title='Освещение в аудитории')
        self.assertEqual(feedback.created_by, self.student)
        self.assertTrue(feedback.is_anonymous)
        self.assertEqual(feedback.status, Feedback.Status.NEW)
        self.assertTrue(StatusHistory.objects.filter(
            feedback=feedback,
            new_status=Feedback.Status.NEW,
            changed_by=self.student,
        ).exists())

    def test_invalid_submission_is_not_saved(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse('feedback:create'), {
            'kind': Feedback.Kind.PROPOSAL,
            'category': self.category.pk,
            'title': '',
            'description': 'Описание предложения.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обязательное поле.')
        self.assertEqual(Feedback.objects.count(), 0)

    def test_staff_user_cannot_submit_student_feedback(self):
        staff_user = get_user_model().objects.create_user(
            username='moderator',
            password='safe-test-password-42',
            role='moderator',
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('feedback:create'))

        self.assertEqual(response.status_code, 403)
