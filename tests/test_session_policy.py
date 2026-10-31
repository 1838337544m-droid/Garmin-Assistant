import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from garmin_assistant.history import HistoryStore
from garmin_assistant.sync import SyncManager
from garmin_assistant.research import update_research
from garmin_assistant.training import TrainingWorkflow


class SessionPolicyTests(unittest.TestCase):
    def test_week_boundary_refreshes_research_but_six_days_reuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def fetch(day):calls.append(day);return [{'pmid':'1'}]
            folder=Path(tmp)
            update_research(folder,'2026-10-24',fetch=fetch)
            update_research(folder,'2026-10-30',fetch=fetch)
            update_research(folder,'2026-10-31',fetch=fetch)
            self.assertEqual(calls,['2026-10-24','2026-10-31'])

    def test_classic_models_and_menu_return_in_saved_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=TrainingWorkflow(None,Path(tmp)).tomorrow(as_of='2026-10-28',sync_first=False,research_refresh=False)
            self.assertIn('classic_models',r)
            self.assertTrue(all(m.get('url') and m.get('application') for m in r['classic_models']))
            self.assertIn('function_menu',r)
            text=Path(r['report_markdown']).read_text(encoding='utf-8')
            self.assertIn('经典训练模型',text)
            self.assertIn('功能菜单',text)

    def test_long_absence_backfills_entire_gap_not_just_analysis_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=HistoryStore(Path(tmp)/'history.sqlite3')
            store.finish({'status':'ok','requested_start':'2026-01-01','end_date':'2026-04-01'})
            calls=[]
            class Stop:
                def query(self,kind,**p):
                    calls.append(p)
                    return {'status':'error','data':None,'error':'offline'}
            r=SyncManager(Stop(),store).run(days=93,end_date='2026-10-31')
            self.assertEqual(calls[0]['start_date'],'2026-03-25')
            self.assertEqual(r['interval']['gap_start'],'2026-04-02')
            self.assertEqual(r['interval']['gap_end'],'2026-10-31')
            self.assertIn('function_menu',r)

    def test_year_long_gap_chunks_activity_ranges_within_api_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=HistoryStore(Path(tmp)/'history.sqlite3')
            store.finish({'status':'ok','requested_start':'2024-10-01','end_date':'2025-01-01'})
            ranges=[]
            class Empty:
                def query(self,kind,**p):
                    if kind=='activities':
                        span=(date.fromisoformat(p['end_date'])-date.fromisoformat(p['start_date'])).days+1
                        if span>366:raise ValueError('API range limit')
                        ranges.append((p['start_date'],p['end_date']))
                    data=[]
                    if kind=='daily_summaries':data={'data':[]}
                    if kind=='hrv_summaries':data={'hrvSummaries':[]}
                    return {'status':'ok','data':data,'fetched_at':'now'}
            r=SyncManager(Empty(),store).run(end_date='2026-10-31')
            self.assertEqual(r['status'],'ok')
            self.assertEqual(ranges[0][0],'2024-12-25')
            self.assertEqual(ranges[-1][1],'2026-10-31')
            self.assertGreater(len(ranges),1)


if __name__=='__main__':unittest.main()
