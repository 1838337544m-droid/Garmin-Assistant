"""Reviewed evidence plus dated PubMed discovery; new articles are never executable rules."""
import json
import time
import uuid
import re
import html
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone

REVIEWED = [
    {'id':'readiness2026','year':2026,'title':'Conceptual Frameworks and Assessment of Readiness to Train in Endurance Exercise: A Systematic Review',
     'url':'https://pubmed.ncbi.nlm.nih.gov/42926133/','type':'systematic review',
     'application':'综合主观疲劳、睡眠、压力、疼痛及客观指标，结合个人基线解释，不用单一分数放行训练。'},
    {'id':'hrv2026','year':2026,'title':'Heart rate variability–guided endurance training: evaluating strengths, weaknesses, opportunities, and threats for load prescription and adjustment',
     'url':'https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2026.1858271/full','type':'critical analysis',
     'application':'HRV 采用多日趋势及个人参照；最佳阈值和基线策略尚无统一共识，不能将单晚下降直接解释为需要停跑。'},
    {'id':'sleep2026','year':2026,'title':'Physical activity, athletic performance, and recovery: The role of sleep',
     'url':'https://pubmed.ncbi.nlm.nih.gov/41963169/','type':'narrative review',
     'application':'关注睡眠时长与个人平常水平，安排足够睡眠和恢复；不能用今天的数据预知今晚睡眠。'},
    {'id':'distance2025','year':2025,'title':'How much running is too much? Identifying high-risk running sessions in a 5200-person cohort study',
     'url':'https://pubmed.ncbi.nlm.nih.gov/40623829/','type':'observational cohort',
     'application':'检查计划单次距离与近 30 天最长跑的变化。观察性关联不等于因果，也不能把 10% 当成人人适用的安全保证。'},
    {'id':'rehab2024','year':2024,'title':'Criteria and Guidelines for Returning to Running Following a Tibial Bone Stress Injury: A Scoping Review',
     'url':'https://link.springer.com/article/10.1007/s40279-024-02051-y','type':'scoping review; predominantly low-level evidence',
     'application':'胫骨骨应力伤后回跑需考虑无痛步行、局部症状与专业评估；先逐步恢复距离再恢复速度。不是对所有伤病的通用康复处方。'},
    {'id':'intensity2025','year':2025,'title':'Which Training Intensity Distribution Intervention will Produce the Greatest Improvements in Maximal Oxygen Uptake and Time-Trial Performance in Endurance Athletes?',
     'url':'https://pubmed.ncbi.nlm.nih.gov/39888556/','type':'individual-participant network meta-analysis',
     'application':'训练强度分配需适配运动水平；不能宣称极化训练普遍优于金字塔分配，更不能保证最快达标。'},
]

CLASSIC_MODELS = [
    {'id':'fitness_fatigue','name':'Banister / Morton 适能—疲劳模型','year':1990,
     'title':'Modeling human performance in running','url':'https://pubmed.ncbi.nlm.nih.gov/2246166/',
     'application':'训练刺激同时积累适能与疲劳；结合近期负荷和恢复指标决定是否增加刺激。这里只作解释框架，未拟合个人模型参数，不产生预测成绩。'},
    {'id':'intensity_distribution','name':'Seiler 低强度主导的耐力强度分配','year':2010,
     'title':'What is best practice for training intensity and duration distribution in endurance athletes?',
     'url':'https://pubmed.ncbi.nlm.nih.gov/20861519/',
     'application':'以可恢复的低强度训练为主体，质量课按能力和恢复安排；结合近期研究比较极化/金字塔分配，不机械规定每个人都必须 80/20。'},
    {'id':'daniels','name':'Daniels 跑步训练强度分类','year':2021,
     'title':"Daniels’ Running Formula, 4th edition",'url':'https://us.humankinetics.com/products/daniels-running-formula-4th-edition',
     'application':'区分轻松、马拉松配速、阈值、间歇与重复跑；训练配速应基于当前能力，不能直接用目标成绩反推当前 VDOT 或强度课配速。'},
]


def replace_local_file(staged, destination):
    try:
        staged.replace(destination)
    except OSError as error:
        if getattr(error, 'winerror', None) != 17:
            raise
        # Store Python may redirect files to a different volume even when the
        # parent directory resolves to its logical path. Resolve the actual files.
        physical_source = staged.resolve(strict=True)
        try:
            physical_target = destination.resolve(strict=True)
        except FileNotFoundError:
            physical_target = physical_source.with_name(destination.name)
        if physical_target != physical_source.with_name(destination.name):
            raise
        physical_source.replace(physical_target)


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Store Python may virtualize LOCALAPPDATA onto another drive. Resolve the
    # existing parent before constructing *both* sides of an atomic rename.
    path = path.parent.resolve() / path.name
    tmp = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        replace_local_file(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def parse_pubmed(xml, as_of):
    records=[]
    for article in ET.fromstring(xml).findall('PubmedArticle'):
        citation=article.find('MedlineCitation');body=article.find('MedlineCitation/Article')
        if citation is None or body is None:continue
        pmid=citation.findtext('PMID')
        title=''.join(body.find('ArticleTitle').itertext()) if body.find('ArticleTitle') is not None else ''
        pub=body.find('ArticleDate')
        if pub is None:pub=body.find('Journal/JournalIssue/PubDate')
        published=None
        if pub is not None:
            year=pub.findtext('Year');month=pub.findtext('Month','01');day=pub.findtext('Day','01')
            if year:
                if not month.isdigit():
                    months={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
                    month=str(months.get(month[:3],1))
                try:published=date(int(year),int(month),int(day)).isoformat()
                except ValueError:continue
        if not pmid or not title or not published or published>as_of:continue
        abstract=' '.join(''.join(part.itertext()) for part in body.findall('Abstract/AbstractText'))
        records.append({'pmid':pmid,'title':title,'publication_date':published,
                        'journal':body.findtext('Journal/Title'), 'abstract':abstract,
                        'publication_types':[p.text for p in body.findall('PublicationTypeList/PublicationType')],
                        'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'})
    return records


def discover_pubmed(as_of):
    import requests
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    topics=[
        '(running[Title/Abstract] OR endurance[Title/Abstract]) AND (training intensity[Title/Abstract] OR training distribution[Title/Abstract])',
        '(athlete[Title/Abstract] OR endurance[Title/Abstract]) AND (heart rate variability[Title/Abstract] OR readiness[Title/Abstract] OR sleep recovery[Title/Abstract])',
        'running[Title/Abstract] AND (return to running[Title/Abstract] OR injury rehabilitation[Title/Abstract] OR bone stress[Title/Abstract])',
    ]
    ids=[]
    with requests.Session() as session:
        session.headers['User-Agent']='GarminLocalMCP/1.0 personal research discovery'
        for topic in topics:
            response=session.get(url+'esearch.fcgi',params={'db':'pubmed','retmode':'json','retmax':3,'sort':'pub_date',
                'term':topic,'datetype':'pdat','mindate':'2024/01/01','maxdate':as_of.replace('-','/'),'tool':'GarminLocalMCP'},timeout=15)
            response.raise_for_status()
            ids.extend(response.json()['esearchresult']['idlist'])
            time.sleep(.4)
        if not ids:raise ValueError('No research records returned')
        response=session.get(url+'efetch.fcgi',params={'db':'pubmed','id':','.join(dict.fromkeys(ids)),
                'retmode':'xml','tool':'GarminLocalMCP'},timeout=20)
        response.raise_for_status()
        records=parse_pubmed(response.text,as_of)
        if not records:raise ValueError('No usable research records returned')
        return records


def discover_europepmc(as_of):
    import requests
    topics=[
        'TITLE_ABS:("endurance training") AND TITLE_ABS:(polarized OR pyramidal OR "intensity distribution")',
        'TITLE_ABS:(athlete OR endurance) AND TITLE_ABS:("heart rate variability" OR "readiness to train" OR "sleep recovery")',
        'TITLE_ABS:(running) AND TITLE_ABS:("return to running" OR rehabilitation OR "bone stress")',
    ]
    records={}
    with requests.Session() as session:
        for topic in topics:
            response=session.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',params={
                'query':f'({topic}) AND FIRST_PDATE:[2024-01-01 TO {as_of}] AND SRC:MED sort_date:y',
                'format':'json','pageSize':3,'resultType':'core'},timeout=15)
            response.raise_for_status()
            for paper in response.json()['resultList']['result']:
                pmid=paper.get('pmid');published=paper.get('firstPublicationDate')
                if not pmid or not published or published>as_of:continue
                records[pmid]={'pmid':pmid,'title':paper.get('title'),'publication_date':published,
                    'journal':paper.get('journalInfo',{}).get('journal',{}).get('title'),
                    'abstract':html.unescape(re.sub('<[^>]+>',' ',paper.get('abstractText',''))),
                    'publication_types':paper.get('pubTypeList',{}).get('pubType',[]),
                    'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/','retrieved_via':'Europe PMC (EMBL-EBI)'}
    if not records:raise ValueError('No usable Europe PMC records')
    return list(records.values())


def discover(as_of):
    try:
        return [{**r,'retrieved_via':'PubMed E-utilities'} for r in discover_pubmed(as_of)]
    except Exception:
        return discover_europepmc(as_of)


def update_research(folder, as_of, force=False, fetch=None):
    path=folder/'research.json'
    try:previous=json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError,json.JSONDecodeError):previous={}
    checked=previous.get('checked_on')
    age=(date.fromisoformat(as_of)-date.fromisoformat(checked)).days if checked else 999
    metadata={'reviewed_sources':REVIEWED,'rules_reviewed_on':'2026-10-28',
              'classic_models':CLASSIC_MODELS,'refresh_interval_days':7,
              'interpretation_policy':'Before using a newly retrieved article, assess its study design, running-specific applicability and limitations; cite title/year/link and distinguish its findings from the implemented heuristics. If no applicable higher-quality evidence changes the classic framework, say so. Do not equate newest with strongest evidence.',
              'scope':'Selected PubMed-indexed papers since 2024, retrieved via NCBI or Europe PMC; not an exhaustive systematic search. Retrieved abstracts require appraisal before changing advice.',
              'health_data_shared':False}
    if not force and 0<=age<7:
        return {**previous,**metadata,'status':'stale' if previous.get('error') else 'cached'}
    attempt=datetime.now(timezone.utc).isoformat()
    try:
        candidates=(fetch or discover)(as_of)
        candidates=[{**r,'review_status':'not_appraised'} for r in candidates]
        result={**metadata,'status':'updated','checked_on':as_of,'retrieved_at':datetime.now(timezone.utc).isoformat(),
                'last_attempt_at':attempt,'candidates':candidates,'error':None}
        atomic_json(path,result)
        return result
    except Exception:
        result={**previous,**metadata,'status':'stale' if previous.get('checked_on') else 'reviewed_only',
                'checked_on':checked,'candidates':previous.get('candidates',[]),
                'last_attempt_at':attempt,'error':'research_refresh_failed; retained reviewed sources and any previous candidates'}
        atomic_json(path,result)
        return result
