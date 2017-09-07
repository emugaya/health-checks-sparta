from django.test.utils import override_settings

from hc.front.models import Blog
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class DeleteBlogsTestCase(BaseTestCase):
    def setUp(self):
        super(DeleteBlogsTestCase, self).setUp()
        url = "/blog/add/"
        form = {"blog_title": "Blog Post Title",
                "category": "Technology", "story": "This is a story"}

        form2 = {"blog_title": "Blog Post Title 2",
                "category": "Technology", "story": "This is a story 2"}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)
        self.client.post(url, form2)

    def tests_deletes_blog_posts(self):
        # Delete first blog post
        id = Blog.objects.all()[0].id
        url = "/blog/delete/%s/" % id
        self.client.get(url)
        assert Blog.objects.count() == 1

        # Delete second blog post
        id = Blog.objects.all()[0].id
        url = "/blog/delete/%s/" % id
        self.client.get(url)
        assert Blog.objects.count() == 0
