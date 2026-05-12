

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Update, ChangeRequest

class UpdateModelTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create(username='tester')

	def test_version_property(self):
		update = Update(
			title='Test', slug='test', body='Body',
			major_version=1, current_patch=2, bug_fix='a',
			author=self.user
		)
		self.assertEqual(update.version, '1.2a')

class ChangeRequestStatusTests(TestCase):
	def setUp(self):
		self.cr = ChangeRequest.objects.create(
			subject='Test', email='a@b.com', request_text='text',
		)

	def test_allowed_status_transitions(self):
		self.assertTrue(self.cr.can_transition_to(ChangeRequest.Status.IN_PROGRESS))
		self.assertTrue(self.cr.can_transition_to(ChangeRequest.Status.DENIED))
		self.assertFalse(self.cr.can_transition_to(ChangeRequest.Status.COMPLETED))
		self.cr.status = ChangeRequest.Status.IN_PROGRESS
		self.assertTrue(self.cr.can_transition_to(ChangeRequest.Status.COMPLETED))
		self.assertFalse(self.cr.can_transition_to(ChangeRequest.Status.DENIED))
