
from django.test.utils import override_settings

from hc.front.models import Blog
from hc.test import BaseTestCase

@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class EditBlogTestCase(BaseTestCase):
    def setUp(self):
        super(EditBlogTestCase, self).setUp()
        url = "/blog/add/"
        form = {"blog_title": "Blog Post Title",
                "category": "Technology", "story": "This is a story"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

    def test_it_edits_blog_post(self):
        "Should test if blog is edited"
        id = Blog.objects.all()[0].id
        url = "/blog/edit/%s/" % id
        form = {"blog_title": "Blog Post Title edited",
                "category": "Technology",
                "story": "This is a story edited"}

        r = self.client.post(url, form)

        self.assertRedirects(r, "/blog/")
        assert Blog.objects.get(id=id).title == "Blog Post Title edited"

    def test_it_edits_blog_post_which_doesnt_exists(self):
        "Should test status code for non existing blog"
        id = (Blog.objects.all()[0].id) + 1
        url = "/blog/edit/%s/" % id
        form = {"blog_title": "Blog Post Title edited",
                "category": "Technology",
                "story": "This is a story edited"}

        r = self.client.post(url, form)
        assert r.status_code == 302


