# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Loopback-only interactive dashboard with per-launch authorization."""
import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from athlete_profile import load_profile, save_profile, PRIMARY_SPORTS
from report_ui import render_dashboard
from prescription import SESSION_SPORTS
from dashboard_defaults import load_defaults, save_defaults
from dashboard_history import load_latest, save_latest, coverage
from session_targets import validate_targets, validate_race
from goal_guidance import validate_benchmark


PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>训练日报</title>
<style>*{box-sizing:border-box}body{background:#f1f3ef;color:#182b22;font:15px/1.6 system-ui;margin:0}main{max-width:1060px;margin:30px auto;padding:24px}.tag{letter-spacing:.17em;font-size:11px}h1{font-size:32px;font-weight:550}.panel{padding:25px;background:white;border:1px solid #dce2db;border-radius:15px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}label{display:block;margin:12px 0;font-size:13px}select,input{width:100%;padding:11px;border:1px solid #c5d0c7;border-radius:7px;background:#fff;font:inherit}button{border:0;border-radius:8px;background:#19382a;color:white;padding:13px 23px;font:inherit;cursor:pointer}button:disabled{opacity:.5}#state{white-space:pre-wrap}iframe{width:100%;height:1100px;border:0;margin-top:24px;background:#f1f3ef}small{color:#68776f}fieldset{border:1px solid #dce2db;border-radius:8px;margin:18px 0} @media(max-width:650px){.grid{grid-template-columns:1fr}main{padding:15px}}</style>
<main><div class="tag">PACE / TRAINING JOURNAL</div><h1>训练工作台</h1><p>长期主项决定目标方向，本次项目决定执行方式。</p><section class="panel" id="first_use" style="margin-bottom:18px"><strong>第一次使用？按这三步来</strong><ol><li>选择长期主项、明天的运动和目标；只有跑步需要可选的计划距离。</li><li>填写身体感受；不确定的项目保留“未确认”，不要为了生成建议随意填“否”。</li><li>点击“生成第一份分析”或“更新分析”，保持页面打开，完成后结果自动显示在下方。</li></ol><small>打开本页尚未同步数据。若没有配置密钥，先回设置窗口完成“保存并检查 Garmin”。</small></section><section class="panel" style="margin-bottom:18px"><h2 style="margin:0">最近一次分析</h2><p id="last_summary">正在读取上次结果，不会自动同步 Garmin…</p><button type="button" id="update" disabled>更新分析</button><div id="state" role="status" aria-live="polite"></div><div id="coverage_box"></div></section><iframe id="result" sandbox="allow-popups allow-popups-to-escape-sandbox" title="训练分析结果" hidden></iframe><form class="panel" id="form"><p id="saved_summary">首次设置后会自动记住，之后可以直接生成分析。</p><details id="preferences" open><summary>修改运动与目标</summary><div class="grid"><label>长期主项<select id="primary"><option value="running">跑步</option><option value="cycling">骑车</option><option value="swimming">游泳</option><option value="climbing">攀岩</option></select></label><label>明天的运动<select id="sport"><option value="running">跑步</option><option value="cycling">骑车</option><option value="swimming">游泳</option><option value="climbing">攀岩</option><option value="other">其他</option></select></label></div><label>长期目标<input id="goal" required maxlength="500" placeholder="例如：建立稳定跑步频率，完成 10 公里"></label>
<label>计划跑步距离（公里，可留空；仅跑步生效）<input id="planned" type="number" min="0.1" max="100" step="0.1"></label></details><details id="body_settings" open><summary>查看或修改身体状态</summary><p id="state_saved">尚无身体状态记录。</p><button type="button" id="confirm_state">状态未变，更新记录时间</button><fieldset><legend>当前身体感受（未选择表示未知）</legend><div class="grid"><label>疼痛 0–10<input id="pain_0_10" type="number" min="0" max="10" step="0.5"></label><label>疲劳 0–10<input id="fatigue_0_10" type="number" min="0" max="10" step="0.5"></label></div><div id="checks" class="grid"></div></fieldset>
<fieldset id="swim" hidden><legend>游泳前确认</legend><div id="swimchecks" class="grid"></div></fieldset>
</details><small>设置会自动保存，下次无需重复填写。身体状态超过24小时后仅保留显示，分析按未知处理；修改或点击“状态未变”可更新记录时间。提交后保存运动偏好，并同步 Garmin 数据与文献。分析可能需要几分钟；密钥仍使用已安装版本的本机设置。</small><p><button id="submit">更新分析</button></p></form></main>
<p style="max-width:1012px;margin:20px auto;padding:0 24px"><button id="close">关闭本次日报服务</button></p><script>
const key=new URLSearchParams(location.search).get('key');
let settingsReady=false;
const hiddenStyle=document.createElement('style');hiddenStyle.textContent='[hidden]{display:none!important}';document.head.append(hiddenStyle);
const fields={illness:'是否生病',pain_with_walking:'是否步行痛',focal_bone_pain:'是否局部骨痛',chest_pain:'是否胸痛',fainting:'是否晕厥'};
function choice(id,label,parent){let wrap=document.createElement('label');wrap.textContent=label;let s=document.createElement('select');s.id=id;for(const [v,t] of [['','未确认'],['false','否'],['true','是']])s.add(new Option(t,v));wrap.append(s);document.getElementById(parent).append(wrap);}
Object.entries(fields).forEach(([k,v])=>choice(k,v,'checks'));choice('shoulder_pain','是否肩痛','swimchecks');choice('swimming_alone','是否独自下水','swimchecks');
document.getElementById('sport').onchange=()=>{document.getElementById('swim').hidden=document.getElementById('sport').value!=='swimming'};
let stateConfirmed=false;document.getElementById("confirm_state").onclick=()=>{stateConfirmed=true;document.getElementById("state_saved").textContent="将在本次提交时更新状态记录时间。";};
const headers={'X-Dashboard-Key':key,'Content-Type':'application/json'};
const phaseLabels={preparing:'正在保存设置…',syncing:'正在同步 Garmin 数据…',research:'正在核对研究资料…',analyzing:'正在分析训练与恢复…',saving:'正在保存日报…',complete:'分析完成',failed:'更新失败，请重试。'};
function showCoverage(c){
 const box=document.getElementById('coverage_box');box.replaceChildren();
 const p=document.createElement('p');p.textContent=(c.sync_complete?'本次同步完成':'本次同步不完整或未确认')+' · '+(c.missing.length?'仍有 '+c.missing.length+' 项信息未确认':'无已知缺项');box.append(p);
 if(c.missing.length){const ul=document.createElement('ul');c.missing.forEach(item=>{let li=document.createElement('li');li.textContent=item;ul.append(li);});box.append(ul);}
 document.getElementById('last_summary').textContent='分析日期：'+(c.as_of||'未知')+' · 建议日期：'+(c.target_date||'未知')+' · 生成时间：'+(c.generated_at?new Date(c.generated_at).toLocaleString():'未知')+(c.is_current?'':'。这是以往结果，请更新分析后再用于当前训练。');
}
async function loadLatest(){
 try{const r=await fetch('/latest',{headers});if(!r.ok)throw Error();const d=await r.json();if(d.has_result){const frame=document.getElementById('result');frame.srcdoc=d.html;frame.hidden=false;showCoverage(d.coverage);}else{document.getElementById('last_summary').textContent=d.message;document.getElementById('update').textContent='生成第一份分析';}}
 catch(e){document.getElementById('last_summary').textContent='无法读取上次报告；可点击更新分析重试。';}
}
document.getElementById('update').onclick=()=>document.getElementById('form').requestSubmit();
document.getElementById('goal').addEventListener('invalid',()=>{document.getElementById('preferences').open=true;document.getElementById('form').scrollIntoView();});

document.getElementById('close').onclick=async()=>{await fetch('/close',{method:'POST',headers});document.getElementById('state').textContent='本次日报服务已关闭，可关闭页面。';document.getElementById('submit').disabled=true;document.getElementById('update').disabled=true;};
fetch('/profile',{headers}).then(r=>r.json()).then(p=>{if(p.profile){document.getElementById('primary').value=p.profile.primary_sport;document.getElementById('sport').value=p.profile.primary_sport;document.getElementById('goal').value=p.profile.goal;document.getElementById('sport').onchange();document.getElementById('preferences').open=false;document.getElementById('first_use').hidden=true;document.getElementById('saved_summary').textContent='已记住目标：'+p.profile.goal+'。没有变化可直接生成分析。';}const d=p.defaults||{};populateTargets(d);populateBenchmark(d);settingsReady=true;if(d.session_sport)document.getElementById('sport').value=d.session_sport;if(d.planned_km!=null)document.getElementById('planned').value=d.planned_km;for(const [k,v] of Object.entries({...d.subjective,...d.swimming_safety})){const el=document.getElementById(k);if(el)el.value=String(v);}if(d.state_recorded_at){document.getElementById('body_settings').open=false;document.getElementById('state_saved').textContent='上次记录：'+new Date(d.state_recorded_at).toLocaleString()+'。超过24小时的记录不会作为当前状态。';}document.getElementById('sport').onchange();showTargets();}).catch(()=>{document.getElementById('state').textContent='无法读取运动偏好，请重新打开训练日报。'});
document.getElementById('form').onsubmit=async ev=>{ev.preventDefault();let btn=document.getElementById('submit'),state=document.getElementById('state'),frame=document.getElementById('result');btn.disabled=true;document.getElementById('update').disabled=true;state.textContent='正在准备更新；下方保留上次结果。';let polling=true;const timer=setInterval(async()=>{try{let r=await fetch('/progress',{headers});let d=await r.json();if(polling)state.textContent=phaseLabels[d.phase]||'正在更新…';}catch(e){}},1000);let subjective={};for(const k of ['pain_0_10','fatigue_0_10',...Object.keys(fields)]){let v=document.getElementById(k).value;if(v!=='')subjective[k]=k.endsWith('_0_10')?Number(v):v==='true';}let swim={};for(const k of ['shoulder_pain','swimming_alone']){let v=document.getElementById(k).value;if(v!=='')swim[k]=v==='true';}try{let r=await fetch('/analyze',{method:'POST',headers,body:JSON.stringify({sport_targets:collectTargets(),running_benchmark:collectBenchmark(),race_plan:collectRace(),state_confirmed:stateConfirmed,primary_sport:document.getElementById('primary').value,goal:document.getElementById('goal').value,session_sport:document.getElementById('sport').value,subjective,swimming_safety:swim,planned_km:document.getElementById('sport').value==='running'&&document.getElementById('planned').value!==''?Number(document.getElementById('planned').value):null})});let data=await r.json();if(!r.ok)throw Error(data.error||'分析失败');stateConfirmed=false;frame.srcdoc=data.html;frame.hidden=false;showCoverage(data.coverage);document.getElementById('update').textContent='更新分析';state.textContent=data.coverage.data_state==='complete'?'分析完成。':'分析已生成，但仍有缺项或同步不完整，请查看上方说明。';frame.scrollIntoView({behavior:'smooth'});}catch(e){state.textContent=e.message+' 上次结果仍保留；修正后点击“更新分析”重试。';}finally{polling=false;clearInterval(timer);btn.disabled=false;document.getElementById('update').disabled=false;}};
const targetFields={running:[['minutes','轻松跑时长（分钟）'],['hr_low','个人轻松跑心率下限（bpm）'],['hr_high','个人轻松跑心率上限（bpm）'],['pace_fast','轻松跑最快配速（秒/公里，例如360=6:00）'],['pace_slow','轻松跑最慢配速（秒/公里）']],cycling:[['minutes','轻松骑时长（分钟）'],['hr_low','骑行心率下限（bpm）'],['hr_high','骑行心率上限（bpm）'],['watts_low','轻松骑功率下限（W）'],['watts_high','轻松骑功率上限（W）'],['speed_low','熟悉平路速度下限（km/h）'],['speed_high','熟悉平路速度上限（km/h）']],swimming:[['distance','轻松游总距离（米）'],['reps','分组数量（整数）'],['rest','组间休息（秒）'],['pace_fast','轻松游最快配速（秒/100米）'],['pace_slow','轻松游最慢配速（秒/100米）']],climbing:[['minutes','技术攀爬时长（分钟）'],['grade','熟悉的轻松路线等级（如YDS 5.8或法式5a）'],['reps','轻松路线条数（整数）'],['rest','路线间休息（秒）']]};
const targetBox=document.createElement('details');targetBox.innerHTML='<summary>专项数值设置（填写一次，按运动分别保存）</summary><p>填写你已确认可耐受的轻松训练区间，可参考既有测试或教练设定。不是比赛目标；不确定就留空，不会从目标心率推算训练区间。</p>';
for(const [sport,fields] of Object.entries(targetFields)){const box=document.createElement('div');box.dataset.targetSport=sport;box.className='grid';for(const [name,label] of fields){const wrap=document.createElement('label');wrap.textContent=label;const input=document.createElement('input');input.id='target_'+sport+'_'+name;input.type=name==='grade'?'text':'number';if(name==='grade')input.maxLength=80;else{input.min=name==='rest'?'0':'1';input.step=name==='reps'?'1':'any';}wrap.append(input);box.append(wrap);}targetBox.append(box);}
document.getElementById('preferences').after(targetBox);
function collectTargets(){const result={};for(const [sport,fields] of Object.entries(targetFields)){result[sport]={};for(const [name] of fields){const v=document.getElementById('target_'+sport+'_'+name).value;if(v!=='')result[sport][name]=name==='grade'?v:Number(v);}}return result;}
function showTargets(){for(const el of targetBox.querySelectorAll('[data-target-sport]'))el.hidden=el.dataset.targetSport!==document.getElementById('sport').value;}
document.getElementById('sport').addEventListener('change',showTargets);showTargets();
const raceBox=document.createElement('details');raceBox.innerHTML='<summary>近期比赛计划（可选，保存后持续参与分析）</summary><label>是否有比赛计划<select id="race_enabled"><option value="false">暂无比赛计划</option><option value="true">有比赛计划</option></select></label><div id="race_fields" hidden class="grid"><label>赛事名称<input id="race_name" maxlength="100"></label><label>比赛日期<input id="race_date" type="date"></label><label>比赛项目<select id="race_sport"><option value="running">跑步</option><option value="cycling">骑车</option><option value="swimming">游泳</option><option value="climbing">攀岩</option></select></label><label>优先级<select id="race_priority"><option value="A">A 主要目标赛</option><option value="B">B 次要比赛</option><option value="C">C 体验或练习赛</option></select></label><label>比赛距离（公里；游泳1500米填1.5）<input id="race_distance_km" type="number" min="0.001" max="2000" step="any"></label><label>累计爬升（米，可选）<input id="race_elevation_m" type="number" min="0" max="30000" step="any"></label><label>目标完赛时间（总分钟，可选）<input id="race_goal_minutes" type="number" min="0.001" max="100000" step="any"></label><label>赛事信息与需求（赛道、地形、补给等）<input id="race_notes" maxlength="500"></label></div><small>比赛信息用于结合训练与恢复进行解释，不自动生成比赛强度或完整减量周期。暂无比赛计划时保留原有训练分析。</small>';
targetBox.after(raceBox);
function showRace(){const enabled=document.getElementById('race_enabled').value==='true';document.getElementById('race_fields').hidden=!enabled;document.getElementById('race_date').required=enabled;for(const el of document.getElementById('race_fields').querySelectorAll('input,select'))el.disabled=!enabled;}
document.getElementById('race_enabled').onchange=showRace;showRace();
function collectRace(){if(document.getElementById('race_enabled').value!=='true')return {enabled:false};const p={enabled:true};for(const k of ['name','date','sport','priority','notes','distance_km','elevation_m','goal_minutes']){let v=document.getElementById('race_'+k).value;if(v!=='')p[k]=['distance_km','elevation_m','goal_minutes'].includes(k)?Number(v):v;}return p;}
function populateTargets(d){for(const [sport,values] of Object.entries(d.sport_targets||{}))for(const [name,v] of Object.entries(values)){const el=document.getElementById('target_'+sport+'_'+name);if(el)el.value=v;}for(const [name,v] of Object.entries(d.race_plan||{})){const el=document.getElementById('race_'+name);if(el)el.value=String(v);}showTargets();showRace();}
document.getElementById('race_date').addEventListener('invalid',()=>{raceBox.open=true;});
const benchmarkBox=document.createElement('details');benchmarkBox.innerHTML='<summary>近期跑步比赛／测试成绩（用于分析目标差距，保存后无需重复填）</summary><label>是否提供有效成绩<select id="benchmark_enabled"><option value="false">暂不提供；按能力待评估处理</option><option value="true">提供比赛或计时测试成绩</option></select></label><div id="benchmark_fields" class="grid" hidden><label>成绩日期<input id="benchmark_date" type="date"></label><label>类型<select id="benchmark_kind"><option value="race">正式比赛</option><option value="time_trial">计时测试</option></select></label><label>距离（公里）<input id="benchmark_distance_km" type="number" min="0.001" max="200" step="any"></label><label>完成时间（总分钟；55分30秒填55.5）<input id="benchmark_time_minutes" type="number" min="0.001" max="10000" step="any"></label></div><small>只填写明确的比赛／测试，不把日常慢跑当能力测试。超过42天会标为待更新；这是产品参考窗口，不能保证成绩仍可重复。</small>';
raceBox.after(benchmarkBox);
function showBenchmark(){const enabled=document.getElementById('benchmark_enabled').value==='true';document.getElementById('benchmark_fields').hidden=!enabled;for(const el of document.getElementById('benchmark_fields').querySelectorAll('input,select')){el.disabled=!enabled;el.required=enabled;}}
document.getElementById('benchmark_enabled').onchange=showBenchmark;showBenchmark();
function collectBenchmark(){if(document.getElementById('benchmark_enabled').value!=='true')return null;const p={};for(const k of ['date','kind','distance_km','time_minutes']){const v=document.getElementById('benchmark_'+k).value;p[k]=['distance_km','time_minutes'].includes(k)?Number(v):v;}return p;}
function populateBenchmark(d){if(d.running_benchmark){document.getElementById('benchmark_enabled').value='true';for(const [k,v] of Object.entries(d.running_benchmark)){const el=document.getElementById('benchmark_'+k);if(el)el.value=v;}}showBenchmark();}
benchmarkBox.addEventListener('invalid',()=>{benchmarkBox.open=true;},true);
const guidanceSettings=document.createElement('button');guidanceSettings.type='button';guidanceSettings.textContent='完善成绩与比赛资料';guidanceSettings.style.marginLeft='12px';document.getElementById('update').after(guidanceSettings);
guidanceSettings.onclick=()=>{raceBox.open=true;benchmarkBox.open=true;raceBox.scrollIntoView({behavior:'smooth'});};
const submitHandler=document.getElementById('form').onsubmit;
document.getElementById('form').onsubmit=ev=>{if(!settingsReady){ev.preventDefault();document.getElementById('state').textContent='设置尚未加载完成，请稍后重试；加载失败请重新打开日报。';return;}const invalid=[...targetBox.querySelectorAll('input')].find(el=>!el.checkValidity());if(invalid){ev.preventDefault();targetBox.open=true;document.getElementById('sport').value=invalid.id.split('_')[1];showTargets();invalid.reportValidity();return;}return submitHandler(ev);};
loadLatest().finally(()=>{document.getElementById('update').disabled=false;});
</script></html>'''


def make_server(workflow, folder):
    token=secrets.token_urlsafe(32)
    lock=threading.Lock()
    progress={'phase':'idle','message':''}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass  # URLs and results may contain private data.

        def respond(self,status,data,html=False):
            payload=data.encode('utf-8') if html else json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self,page=False):
            expected=f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=expected:
                return False
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+expected:
                return False
            supplied=(parse_qs(urlsplit(self.path).query).get('key',[''])[0] if page else self.headers.get('X-Dashboard-Key',''))
            return secrets.compare_digest(supplied,token)

        def do_GET(self):
            route=urlsplit(self.path).path
            if not self.authorized(route=='/'):
                return self.respond(403,{'error':'请使用启动时打开的页面。'})
            if route=='/':
                return self.respond(200,PAGE,True)
            if route=='/progress':
                return self.respond(200,dict(progress))
            if route=='/latest':
                result=load_latest(folder,getattr(workflow,'report_folder',None))
                if result:
                    try:
                        return self.respond(200,{'has_result':True,'html':render_dashboard(result,show_controls=False),'coverage':coverage(result)})
                    except (ValueError,TypeError,KeyError):
                        return self.respond(200,{'has_result':False,'message':'上次报告无法显示，请更新分析。'})
                return self.respond(200,{'has_result':False,'message':'还没有分析记录。设置目标后点击“生成第一份分析”。'})
            if route=='/profile':
                try:
                    return self.respond(200,{'profile':load_profile(folder),'defaults':load_defaults(folder)})
                except ValueError:
                    return self.respond(200,{'profile':None})
            self.respond(404,{'error':'页面不存在'})

        def do_POST(self):
            if not self.authorized():
                return self.respond(403,{'error':'页面授权已失效，请重新打开日报。'})
            if urlsplit(self.path).path=='/close':
                self.respond(200,{'closed':True})
                threading.Thread(target=self.server.shutdown,daemon=True).start()
                return
            if urlsplit(self.path).path!='/analyze':
                return self.respond(404,{'error':'页面不存在'})
            if not lock.acquire(blocking=False):
                return self.respond(409,{'error':'已有分析进行中，请等待完成。'})
            try:
                progress.update(phase='preparing',message='正在保存设置')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=8192:
                    raise ValueError()
                body=json.loads(self.rfile.read(size))
                if body.get('primary_sport') not in PRIMARY_SPORTS or body.get('session_sport') not in SESSION_SPORTS:
                    raise ValueError()
                if not isinstance(body.get('goal'),str) or not 0<len(body['goal'].strip())<=500:
                    raise ValueError()
                subjective=body.get('subjective',{})
                allowed={'pain_0_10','fatigue_0_10','illness','pain_with_walking','focal_bone_pain','chest_pain','fainting'}
                if not isinstance(subjective,dict) or set(subjective)-allowed:
                    raise ValueError()
                for k,v in subjective.items():
                    if k.endswith('_0_10'):
                        if type(v) not in (int,float) or not 0<=v<=10: raise ValueError()
                    elif type(v) is not bool: raise ValueError()
                swim=body.get('swimming_safety',{})
                planned=body.get('planned_km')
                if planned is not None and (type(planned) not in (int,float) or not 0<planned<=100):
                    raise ValueError()
                if not isinstance(swim,dict) or set(swim)-{'shoulder_pain','swimming_alone'} or any(type(v) is not bool for v in swim.values()):
                    raise ValueError()
                profile=load_profile(folder)
                validate_targets(body.get('sport_targets',{}))
                validate_race(body.get('race_plan'))
                validate_benchmark(body.get('running_benchmark'))
                if not profile or profile['primary_sport']!=body['primary_sport'] or profile['goal']!=body['goal'].strip():
                    save_profile(folder,body['primary_sport'],body['goal'])
                saved,subjective,swim=save_defaults(folder,body)
                def update_phase(phase):
                    progress.update(phase=phase)
                result=workflow.assess_session(body['session_sport'],subjective=subjective,swimming_safety=swim,
                    planned_km=planned if body['session_sport']=='running' else None, progress=update_phase)
                progress.update(phase='saving')
                html=render_dashboard(result,show_controls=False)
                save_latest(folder,result)
                progress.update(phase='complete')
                self.respond(200,{'html':html,'coverage':coverage(result)})
            except (ValueError,TypeError,KeyError):
                progress.update(phase='failed',message='请检查运动、目标与身体感受，然后重试。')
                self.respond(400,{'error':'输入无效，请检查运动、目标与身体感受。'})
            except Exception:
                progress.update(phase='failed',message='更新未完成；请检查网络与设置中的 Garmin 连接，然后重试。上次结果仍保留。')
                self.respond(500,{'error':'分析未完成。请确认已在设置中配置 Garmin 密钥、网络可用，然后重试。'})
            finally:
                lock.release()

    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    server.daemon_threads=True
    return server,f'http://127.0.0.1:{server.server_port}/?key={token}'


def run(workflow,folder):
    server,url=make_server(workflow,folder)
    webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()
