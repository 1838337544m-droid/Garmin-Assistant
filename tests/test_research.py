import importlib.util
import tempfile
import unittest
from pathlib import Path


class ResearchTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('garmin_assistant.research'),'Research updater not implemented')
        import garmin_assistant.research as research
        return research

    def test_new_papers_are_candidates_and_do_not_replace_reviewed_rules(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            r=m.update_research(Path(tmp),'2026-10-28',fetch=lambda day:[{'pmid':'123','title':'Example','url':'https://pubmed.ncbi.nlm.nih.gov/123/'}])
            self.assertEqual(r['status'],'updated')
            self.assertEqual(r['candidates'][0]['review_status'],'not_appraised')
            self.assertTrue(r['reviewed_sources'])

    def test_failed_refresh_keeps_previous_candidates_and_marks_stale(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            m.update_research(folder,'2026-10-28',fetch=lambda day:[{'pmid':'123'}])
            def fail(day):raise RuntimeError('SECRET')
            r=m.update_research(folder,'2026-10-28',force=True,fetch=fail)
            self.assertEqual(r['status'],'stale')
            self.assertEqual(r['candidates'][0]['pmid'],'123')
            self.assertNotIn('SECRET',str(r))
            self.assertIsNotNone(r['last_attempt_at'])
            cached=m.update_research(folder,'2026-10-28',fetch=fail)
            self.assertEqual(cached['status'],'stale')
            self.assertIsNotNone(cached['error'])

    def test_pubmed_xml_preserves_dates_and_rejects_future_publications(self):
        m=self.module()
        xml='''<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article><ArticleTitle>Running recovery</ArticleTitle><Journal><Title>Journal</Title><JournalIssue><PubDate><Year>2026</Year><Month>10</Month><Day>24</Day></PubDate></JournalIssue></Journal><Abstract><AbstractText>Example abstract.</AbstractText></Abstract><PublicationTypeList><PublicationType>Review</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle><PubmedArticle><MedlineCitation><PMID>2</PMID><Article><ArticleTitle>Future</ArticleTitle><ArticleDate><Year>2027</Year><Month>01</Month><Day>01</Day></ArticleDate></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'''
        rows=m.parse_pubmed(xml,'2026-10-28')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['pmid'],'1')
        self.assertEqual(rows[0]['publication_date'],'2026-10-24')
        self.assertEqual(rows[0]['abstract'],'Example abstract.')


if __name__=='__main__':unittest.main()
