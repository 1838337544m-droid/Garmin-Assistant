import importlib.util
import unittest


class EndpointTests(unittest.TestCase):
    def test_queries_select_official_wrappers_with_correct_arguments(self):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.provider'), 'Provider not implemented')
        from garmin_assistant.provider import dispatch
        class Client:
            def get_daily_summaries(self, start, end):
                return {'range': [start, end]}
            def get_daily_sleep(self, day):
                return {'sleep_date': day}
            def search_activities(self, *, start, limit, start_date=None, end_date=None):
                return {'offset': start, 'limit': limit, 'range': [start_date, end_date]}
        self.assertEqual(dispatch(Client(), 'summary', {'date': '2026-10-27'}),
                         {'range': ['2026-10-27', '2026-10-27']})
        self.assertEqual(dispatch(Client(), 'sleep', {'date': '2026-10-27'}),
                         {'sleep_date': '2026-10-27'})
        self.assertEqual(dispatch(Client(), 'activities', {'start': 20, 'limit': 10}),
                         {'offset': 20, 'limit': 10, 'range': [None, None]})


if __name__ == '__main__':
    unittest.main()
