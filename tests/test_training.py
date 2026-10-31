import importlib.util
import tempfile
import unittest
from pathlib import Path
from datetime import date, timedelta


class TrainingTests(unittest.TestCase):
    def ready(self):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.readiness'), 'Readiness not implemented')
        from garmin_assistant.readiness import assess
        return assess

    def history(self):
        result = {'daily_summaries': [], 'sleep_summaries': [], 'hrv_summaries': [], 'activities': []}
        for i in range(40):
            d = (date(2026,10,28)-timedelta(days=i)).isoformat()
            result['daily_summaries'].append({'calendarDate':d,'heartRate':{'restingValue':50}})
            result['sleep_summaries'].append({'calendarDate':d,'sleepTimeSeconds':28800})
            result['hrv_summaries'].append({'calendarDate':d,'lastNightAvg':50})
        for i in (3,6,10,13,17,20,24,27):
            result['activities'].append({'activityId':i,'startTimeLocal':(date(2026,10,28)-timedelta(days=i)).isoformat()+' 18:00:00','activityType':{'typeKey':'running'},'distance':5000,'duration':2100,'aerobicTrainingEffect':2.0})
        return result

    def test_empty_data_does_not_clear_running(self):
        r=self.ready()({}, '2026-10-28')
        self.assertEqual(r['decision'],'insufficient_data')
        self.assertFalse(r['quality_session_eligible'])

    def test_walking_pain_overrides_good_wearables(self):
        r=self.ready()(self.history(),'2026-10-28',subjective={'pain_with_walking':True})
        self.assertEqual(r['decision'],'avoid_running')

    def test_unknown_subjective_state_is_conditional(self):
        r=self.ready()(self.history(),'2026-10-28')
        self.assertTrue(r['provisional'])
        self.assertIn('subjective_check',r['missing'])
        self.assertFalse(r['quality_session_eligible'])
        self.assertEqual(r['target_date'],'2026-10-29')

    def test_two_recovery_signals_reduce_training(self):
        h=self.history()
        h['sleep_summaries'][0]['sleepTimeSeconds']=18000
        for i in range(3):h['hrv_summaries'][i]['lastNightAvg']=30
        r=self.ready()(h,'2026-10-28')
        self.assertEqual(r['decision'],'recovery')
        self.assertEqual(r['metrics']['hrv_baseline'],50)
        self.assertIn('hrv_trend_low',[f['code'] for f in r['flags']])

    def test_one_hrv_dip_does_not_automatically_require_rest(self):
        h=self.history();h['hrv_summaries'][0]['lastNightAvg']=30
        r=self.ready()(h,'2026-10-28')
        self.assertNotEqual(r['decision'],'recovery')

    def test_proposed_distance_surge_is_flagged(self):
        r=self.ready()(self.history(),'2026-10-28',planned_km=10)
        self.assertIn('single_run_jump',[f['code'] for f in r['flags']])
        self.assertFalse(r['quality_session_eligible'])

    def test_future_dated_rows_are_not_used(self):
        h=self.history()
        h['sleep_summaries'].append({'calendarDate':'2026-10-29','sleepTimeSeconds':3600})
        r=self.ready()(h,'2026-10-28')
        self.assertEqual(r['metrics']['latest_sleep_hours'],8)

    def test_null_hrv_and_old_sleep_are_missing_not_normal(self):
        h=self.history();h['hrv_summaries']=[];h['sleep_summaries']=h['sleep_summaries'][4:]
        r=self.ready()(h,'2026-10-28')
        self.assertEqual(r['decision'],'insufficient_data')
        self.assertFalse(r['quality_session_eligible'])

    def test_invalid_self_report_rejected(self):
        with self.assertRaises(ValueError):self.ready()(self.history(),'2026-10-28',subjective={'pain_0_10':20})

    def test_nullable_nested_fields_become_missing_not_crashes(self):
        h=self.history()
        for row in h['daily_summaries']:row['heartRate']=None
        h['activities'].append({'startTimeLocal':'2026-10-28','activityType':None})
        r=self.ready()(h,'2026-10-28')
        self.assertIn('resting_hr_baseline_or_recent',r['missing'])

    def test_zero_current_hrv_is_missing_even_with_two_valid_prior_nights(self):
        h=self.history();h['hrv_summaries'][0]['lastNightAvg']=0
        r=self.ready()(h,'2026-10-28')
        self.assertIn('hrv_current_and_baseline',r['missing'])


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)

    def components(self):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.history'), 'History not implemented')
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.sync'), 'Sync not implemented')
        from garmin_assistant.history import HistoryStore
        from garmin_assistant.sync import SyncManager
        return HistoryStore(Path(self.tmp.name)/'history.sqlite3'),SyncManager

    def provider(self, failure=False):
        class Service:
            def query(self,kind,refresh=False,**p):
                if failure and kind=='hrv_summaries':return {'status':'error','error':'offline','data':None}
                day=p.get('start_date','2026-10-28')
                data=[{'calendarDate':day}]
                if kind=='daily_summaries':data={'data':data}
                if kind=='hrv_summaries':data={'hrvSummaries':data}
                if kind=='activities':
                    data=[{'activityId':1,'startTimeLocal':'2026-10-28 18:00:00','activityType':{'typeKey':'running'}}] if p['start']==0 else []
                return {'status':'ok' if data else 'no_data','data':data,'fetched_at':'2026-10-28T12:00:00+00:00','error':None}
        return Service()

    def test_sync_twice_is_idempotent(self):
        store,manager=self.components()
        for _ in range(2):manager(self.provider(),store).run(days=3,end_date='2026-10-28',full=True)
        rows=store.load('2026-10-26','2026-10-28')
        self.assertEqual(len(rows['activities']),1)
        self.assertIsNotNone(store.last_complete())

    def test_partial_failure_never_advances_complete_watermark(self):
        store,manager=self.components()
        r=manager(self.provider(failure=True),store).run(days=3,end_date='2026-10-28',full=True)
        self.assertEqual(r['status'],'partial')
        self.assertIsNone(store.last_complete())
        self.assertTrue(store.load('2026-10-26','2026-10-28')['daily_summaries'])

    def test_bad_date_does_not_start_network(self):
        store,manager=self.components()
        with self.assertRaises(ValueError):manager(self.provider(),store).run(days=0,end_date='2026-10-28')

    def test_body_battery_date_field_is_normalized_and_persisted(self):
        store,manager=self.components()
        from garmin_assistant.sync import unpack
        rows=unpack('body_battery',[{'date':'2026-10-28','charged':30}])
        store.put('body_battery',rows,'2026-10-28T12:00:00+00:00')
        result=store.load('2026-10-28','2026-10-28')['body_battery']
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['calendarDate'],'2026-10-28')

    def test_malformed_envelope_fails_instead_of_returning_empty(self):
        self.components()
        from garmin_assistant.sync import unpack
        with self.assertRaises(ValueError):unpack('daily_summaries',{'unexpected':[]})

    def test_successful_empty_refresh_removes_obsolete_activity(self):
        store,manager=self.components()
        store.put('activities',[{'activityId':999,'startTimeLocal':'2026-10-27 18:00:00'}],'old')
        manager(self.provider(),store).run(days=3,end_date='2026-10-28',full=True)
        self.assertEqual([r['activityId'] for r in store.load('2026-10-26','2026-10-28')['activities']],[1])

    def test_malformed_date_preserves_previous_chunk(self):
        store,manager=self.components()
        store.put('daily_summaries',[{'calendarDate':'2026-10-27','known':'old'}],'old')
        delegate=self.provider()
        class Bad:
            def query(self,kind,**kwargs):
                if kind=='daily_summaries':return {'status':'ok','data':{'data':[{'calendarDate':'invalid'}]},'fetched_at':'now'}
                return delegate.query(kind,**kwargs)
        r=manager(Bad(),store).run(days=3,end_date='2026-10-28',full=True)
        self.assertEqual(r['status'],'partial')
        self.assertEqual(store.load('2026-10-26','2026-10-28')['daily_summaries'][0]['known'],'old')

    def test_successful_activity_pages_survive_later_page_failure(self):
        store,manager=self.components();delegate=self.provider()
        class Pages:
            def query(self,kind,**kwargs):
                if kind!='activities':return delegate.query(kind,**kwargs)
                if kwargs['start']>0:return {'status':'error','error':'offline','data':None}
                return {'status':'ok','data':[{'activityId':i+1,'startTimeLocal':'2026-10-27 18:00:00'} for i in range(100)],'fetched_at':'now'}
        r=manager(Pages(),store).run(days=3,end_date='2026-10-28',full=True)
        self.assertEqual(r['status'],'partial')
        self.assertEqual(len(store.load('2026-10-26','2026-10-28')['activities']),100)


if __name__=='__main__':unittest.main()
