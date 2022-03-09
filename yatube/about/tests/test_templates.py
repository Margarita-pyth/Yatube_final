from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_uses_correct_template(self):
        """Проверка шаблона для адреса /page/about_author/."""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /page/about_tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
