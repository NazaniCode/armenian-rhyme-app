import unittest

from backend import app


class SeoRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage_contains_seo_metadata_and_links(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Հայերեն հանգերի որոնիչ | Հանգավորում</title>", html)
        self.assertIn('name="description"', html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn('application/ld+json', html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn('/hy/rhymes/սեր', html)
        self.assertIn("Armenian rhyme finder", html)

    def test_rhyme_landing_page_is_server_rendered(self):
        response = self.client.get("/hy/rhymes/սեր")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>սեր բառի հանգերը | Հանգավորում</title>", html)
        self.assertIn("«սեր» բառի հայերեն հանգերը", html)
        self.assertIn("window.__INITIAL_WORD__", html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('id="wordInput"', html)
        self.assertIn('id="resultsSection"', html)
        self.assertIn('id="seoFallback"', html)
        self.assertIn('class="seo-fallback-result"', html)
        self.assertIn("BreadcrumbList", html)

    def test_unknown_rhyme_page_is_noindex_404(self):
        response = self.client.get("/hy/rhymes/not-a-word")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 404)
        self.assertIn('name="robots" content="noindex,follow"', html)

    def test_discovery_files(self):
        robots = self.client.get("/robots.txt")
        sitemap = self.client.get("/sitemap.xml")

        self.assertEqual(robots.status_code, 200)
        self.assertIn("Allow: /", robots.get_data(as_text=True))
        self.assertIn("Sitemap:", robots.get_data(as_text=True))

        self.assertEqual(sitemap.status_code, 200)
        xml = sitemap.get_data(as_text=True)
        self.assertIn("<urlset", xml)
        self.assertIn("/hy/rhymes/", xml)


if __name__ == "__main__":
    unittest.main()
