import importlib.util
import tempfile
import unittest
from pathlib import Path


class WorkflowTests(unittest.TestCase):
    def test_offline_analysis_is_explicit_and_creates_readable_report(self):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.training'),'Workflow not implemented')
        from garmin_assistant.training import TrainingWorkflow
        class NoNetwork:
            def query(self,*a,**k):raise AssertionError('Offline analysis attempted network access')
        with tempfile.TemporaryDirectory() as tmp:
            result=TrainingWorkflow(NoNetwork(),Path(tmp)).tomorrow(as_of='2026-10-28',sync_first=False,research_refresh=False)
            self.assertEqual(result['decision'],'insufficient_data')
            self.assertFalse(result['sync']['fresh'])
            self.assertIn('fresh_complete_sync',result['missing'])
            self.assertTrue(Path(result['report_markdown']).is_file())
            text=Path(result['report_markdown']).read_text(encoding='utf-8')
            self.assertIn('2026-10-29',text)
            self.assertIn('https://',text)


if __name__=='__main__':unittest.main()
