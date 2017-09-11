from django.test.utils import override_settings

from hc.front.models import Blog
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class GetSingleBlogTestCase(BaseTestCase):
    def setUp(self):
        super(GetSingleBlogTestCase, self).setUp()
        url = "/blog/add/"
        form = {"blog_title": "Blog Post Title",
                "category": "Technology", "story": "This is a story"}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)

    def test_it_gets_a_single_blog_post(self):
        id = Blog.objects.all()[0].id
        url = "/blog/%s" % id
        r = self.client.get(url)
        self.assertContains(r, "Blog Post Title")

    def test_when_bucket_id_doent_exist(self):
        id = Blog.objects.all()[0].id + 1
        url = "/blog/%s" % id
        r = self.client.get(url)
        self.assertContains(r, "Page Not Found")
