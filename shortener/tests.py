import json
from django.test import TestCase
from django.urls import reverse
from .models import Link


class LinkModelTests(TestCase):
    def test_auto_generate_code(self):
        link = Link.objects.create(original_url="https://example.com")
        self.assertTrue(len(link.code) >= 6)
        self.assertEqual(link.clicks, 0)

    def test_str_representation(self):
        link = Link.objects.create(original_url="https://example.com", code="custom")
        self.assertEqual(str(link), "custom -> https://example.com")


class LinkViewsTests(TestCase):
    def setUp(self):
        self.link = Link.objects.create(
            original_url="https://example.com/target",
            code="testlink",
            title="Test Title",
        )

    def test_index_get(self):
        response = self.client.get(reverse("shortener:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testlink")

    def test_index_post_create_link(self):
        response = self.client.post(
            reverse("shortener:index"),
            {
                "original_url": "https://python.org",
                "custom_code": "pycode",
                "title": "Python Org",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Link.objects.filter(code="pycode").first()
        self.assertIsNotNone(created)
        self.assertEqual(created.title, "Python Org")

    def test_redirect_view(self):
        response = self.client.get(reverse("shortener:redirect", args=["testlink"]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://example.com/target")
        self.link.refresh_from_db()
        self.assertEqual(self.link.clicks, 1)
        self.assertIsNotNone(self.link.last_accessed)

    def test_info_view(self):
        response = self.client.get(reverse("shortener:info", args=["testlink"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data:image/png;base64,")

    def test_qr_download_view(self):
        response = self.client.get(reverse("shortener:qr_download", args=["testlink"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(len(response.content) > 0)

    def test_delete_view(self):
        response = self.client.post(reverse("shortener:delete", args=["testlink"]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Link.objects.filter(code="testlink").exists())


class LinkApiTests(TestCase):
    def test_api_list(self):
        Link.objects.create(original_url="https://example.com", code="link1")
        response = self.client.get(reverse("shortener:api_links"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_api_create(self):
        payload = {
            "original_url": "https://djangoproject.com",
            "custom_code": "dj123",
            "title": "Django",
        }
        response = self.client.post(
            reverse("shortener:api_links"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["code"], "dj123")

    def test_api_detail(self):
        Link.objects.create(original_url="https://example.com", code="api1")
        response = self.client.get(reverse("shortener:api_link_detail", args=["api1"]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], "api1")
