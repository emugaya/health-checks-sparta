
from django.test.utils import override_settings

from hc.front.models import Blog
from hc.test import BaseTestCase

@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class AddBlogTestCase(BaseTestCase):
    "Should test if blog is added"
    def test_it_adds_blog_post(self):
        url = "/blog/add/"
        form = {"blog_title": "Blog Post Title",
                "category": "Technology", "story": "This is a story"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        self.assertRedirects(r, "/blog/")
        assert Blog.objects.count() == 1

    def test_add_blog_with_required_fields_empty(self):
        "Should test that blog is not added when some fields are empty"
        url = "/blog/add/"
        form = {"blog_title": "Blog Post Title"
            , "category": "Technology", "story": ""}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        assert Blog.objects.count() == 0
