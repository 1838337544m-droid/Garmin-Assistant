import importlib.util
import tempfile
import unittest
from pathlib import Path


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def service(self, fetch):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.service'), 'Cache service has not been implemented')
        from garmin_assistant.service import GarminService
        return GarminService(Path(self.tmp.name) / 'cache.sqlite3', fetch, clock=lambda: 2000)

    def test_cache_persists_and_avoids_duplicate_fetch(self):
        calls = []
        def fetch(kind, params):
            calls.append(kind)
            return {'steps': 123}
        first = self.service(fetch).query('summary', date='2026-10-27')
        second = self.service(fetch).query('summary', date='2026-10-27')
        self.assertEqual(first['source'], 'garmin_api')
        self.assertEqual(second['source'], 'local_cache')
        self.assertEqual(second['data'], {'steps': 123})
        self.assertEqual(calls, ['summary'])

    def test_failed_refresh_preserves_cache_without_disclosing_exception(self):
        s = self.service(lambda *args: {'steps': 123})
        s.query('summary', date='2026-10-27')
        def fail(*args):
            raise RuntimeError('SECRET credential in exception')
        s.fetch = fail
        result = s.query('summary', refresh=True, date='2026-10-27')
        self.assertEqual(result['status'], 'stale')
        self.assertEqual(result['data'], {'steps': 123})
        self.assertNotIn('SECRET', str(result))
        self.assertEqual(self.service(fail).query('summary', date='2026-10-27')['data'], {'steps': 123})

    def test_expired_cache_is_refetched(self):
        s = self.service(lambda *args: [1])
        s.query('summary', date='2026-10-27')
        s.clock = lambda: 3000
        s.fetch = lambda *args: [2]
        result = s.query('summary', date='2026-10-27')
        self.assertEqual(result['source'], 'garmin_api')
        self.assertEqual(result['data'], [2])

    def test_no_cache_failure_is_error_not_zero(self):
        def fail(*args):
            raise RuntimeError('SECRET')
        result = self.service(fail).query('sleep', date='2026-10-27')
        self.assertEqual(result['status'], 'error')
        self.assertIsNone(result['data'])
        self.assertNotIn('SECRET', str(result))

    def test_invalid_queries_never_reach_provider(self):
        def fail(*args):
            self.fail('Invalid input reached provider')
        s = self.service(fail)
        for kind, params in [
            ('summary', {'date': '2026-02-30'}),
            ('steps', {'start_date': '2026-10-28', 'end_date': '2026-10-01'}),
            ('steps', {'start_date': '2026-01-01', 'end_date': '2026-10-28'}),
            ('activities', {'start': -1, 'limit': 10}),
            ('activities', {'start': 0, 'limit': 1001}),
            ('activity', {'activity_id': -1}),
            ('not_an_endpoint', {}),
        ]:
            with self.subTest(kind=kind, params=params), self.assertRaises(ValueError):
                s.query(kind, **params)

    def test_empty_response_explicitly_reports_no_data(self):
        result = self.service(lambda *args: []).query('sleep', date='2026-10-27')
        self.assertEqual(result['status'], 'no_data')
        self.assertEqual(result['data'], [])

    def test_status_excludes_health_payload_and_credentials(self):
        s = self.service(lambda *args: {'private_health': 123})
        s.query('summary', date='2026-10-27')
        result = s.status()
        self.assertEqual(result['cached_queries'], 1)
        self.assertIsNotNone(result['last_successful_fetch'])
        self.assertNotIn('private_health', str(result))


if __name__ == '__main__':
    unittest.main()
