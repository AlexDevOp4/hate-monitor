from django.test import TestCase

from monitoring.models import Post, PostAnalysis


class HealthEndpointTests(TestCase):
    def test_health_returns_ok(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class PostCreateEndpointTests(TestCase):
    def test_valid_post_creates_post(self):
        payload = {
            'platform': 'TWITTER',
            'platform_post_id': '3001',
            'account_handle': 'user_one',
            'url': 'https://x.com/user_one/status/3001',
            'published_at': '2026-11-01T12:00:00Z',
        }
        response = self.client.post('/api/posts/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['platform_post_id'], '3001')
        self.assertEqual(Post.objects.count(), 1)

    def test_invalid_payload_returns_400(self):
        response = self.client.post('/api/posts/', {'platform': 'TWITTER'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Post.objects.count(), 0)

    def test_duplicate_platform_post_id_returns_400(self):
        payload = {
            'platform': 'TWITTER',
            'platform_post_id': '3002',
            'account_handle': 'user_one',
            'url': 'https://x.com/user_one/status/3002',
            'published_at': '2026-11-01T12:00:00Z',
        }
        self.client.post('/api/posts/', payload, content_type='application/json')
        response = self.client.post('/api/posts/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Post.objects.count(), 1)

    def test_client_collected_at_is_ignored(self):
        payload = {
            'platform': 'TWITTER',
            'platform_post_id': '3003',
            'account_handle': 'user_one',
            'url': 'https://x.com/user_one/status/3003',
            'published_at': '2026-11-01T12:00:00Z',
            'collected_at': '2000-01-01T00:00:00Z',
        }
        response = self.client.post('/api/posts/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        post = Post.objects.get()
        self.assertNotEqual(post.collected_at.year, 2000)


class PostListEndpointTests(TestCase):
    def test_list_returns_existing_posts(self):
        Post.objects.create(
            platform=Post.Platform.TWITTER,
            platform_post_id='4001',
            account_handle='user_one',
            url='https://x.com/user_one/status/4001',
            published_at='2026-11-01T12:00:00Z',
        )
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['platform_post_id'], '4001')

    def test_list_empty_database_returns_empty_list(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class PostAnalysisCreateEndpointTests(TestCase):
    def test_valid_analysis_creates_analysis(self):
        post = Post.objects.create(
            platform=Post.Platform.TWITTER,
            platform_post_id='5001',
            account_handle='user_one',
            url='https://x.com/user_one/status/5001',
            published_at='2026-11-01T12:00:00Z',
        )
        payload = {'post': str(post.pk), 'category': 'HOSTILITY', 'confidence': 0.8}
        response = self.client.post('/api/analyses/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PostAnalysis.objects.get().post, post)

    def test_invalid_category_returns_400(self):
        post = Post.objects.create(
            platform=Post.Platform.TWITTER,
            platform_post_id='5002',
            account_handle='user_one',
            url='https://x.com/user_one/status/5002',
            published_at='2026-11-01T12:00:00Z',
        )
        payload = {'post': str(post.pk), 'category': 'NOT_A_CATEGORY', 'confidence': 0.8}
        response = self.client.post('/api/analyses/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PostAnalysis.objects.count(), 0)

    def test_nonexistent_post_returns_400(self):
        payload = {'post': '00000000-0000-0000-0000-000000000000', 'category': 'NONE', 'confidence': 0.5}
        response = self.client.post('/api/analyses/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PostAnalysis.objects.count(), 0)

    def test_confidence_out_of_range_returns_400(self):
        post = Post.objects.create(
            platform=Post.Platform.TWITTER,
            platform_post_id='5003',
            account_handle='user_one',
            url='https://x.com/user_one/status/5003',
            published_at='2026-11-01T12:00:00Z',
        )
        for confidence in (-0.01, 1.01):
            with self.subTest(confidence=confidence):
                payload = {'post': str(post.pk), 'category': 'NONE', 'confidence': confidence}
                response = self.client.post('/api/analyses/', payload, content_type='application/json')
                self.assertEqual(response.status_code, 400)
        self.assertEqual(PostAnalysis.objects.count(), 0)
