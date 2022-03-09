from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /page/about_author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /page/about_tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
