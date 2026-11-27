# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Offline HTML report. All dynamic text is escaped; no remote assets or telemetry."""
from html import escape
from urllib.parse import urlsplit

SPORTS={'running':'跑步','cycling':'骑车','swimming':'游泳','climbing':'攀岩','other':'其他'}


def render_dashboard(r,show_controls=True):
    def e(value):
        return escape(str(value if value is not None else '未提供'),quote=True)
    p=r.get('prescription',{})
    primary=r.get('primary_sport','running')
    sport=r.get('session_sport','running')
    action=p.get('session_action',r.get('recommendation','信息不足，请复评'))
    comparison=r.get('distance_comparison',{}).get('display_zh','')
    comparison_html='<p>'+e(comparison)+'</p>' if comparison else ''
    guidance=r.get('goal_guidance',{})
    guidance_html=''
    for index,section in enumerate(guidance.get('priorities',[])):
        guidance_html+='<section class="card" style="margin-top:18px"><h3>'+e(section['title'])+'</h3>'
        if index==0 and guidance.get('load_status')=='overload_warning':
            guidance_html+='<p style="padding:12px;background:#fff0df;color:#823700"><strong>超负荷警示：原计划需复核；下方提供下调后的训练安排。</strong></p>'
        guidance_html+='<dl>'+''.join('<dt style="font-weight:600;margin-top:16px">'+e(label)+'</dt><dd style="margin:4px 0">'+e(value)+'</dd>' for label,value in section['items'])+'</dl>'
        if index==0 and guidance.get('week_plan'):
            guidance_html+='<h3 style="margin-top:24px">7日条件性训练安排</h3><p class="muted">'+e(guidance['method'])+'</p><div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;text-align:left"><thead><tr><th style="padding:12px">日期</th><th style="padding:12px">安排与执行条件</th></tr></thead><tbody>'+''.join('<tr><td style="padding:12px;border-top:1px solid #dfe5df;white-space:nowrap;vertical-align:top">'+e(row['date'])+'</td><td style="padding:12px;border-top:1px solid #dfe5df">'+e(row['action'])+'</td></tr>' for row in guidance['week_plan'])+'</tbody></table></div>'
        guidance_html+='</section>'
    if guidance:
        guidance_html+='<details class="card"><summary>指导依据：经典理论、近期研究与局限</summary><p>'+e(guidance['evidence_scope'])+'</p><ul>'
        for source in guidance.get('sources',[]):
            if urlsplit(source.get('url','')).scheme in {'http','https'}:
                guidance_html+='<li><a rel="noreferrer" href="'+e(source['url'])+'">'+e(source['title'])+'</a> · '+e(source['date'])+' · 核对 '+e(source['checked_on'])+'<p>'+e(source['quality'])+' '+e(source['application'])+'</p></li>'
        guidance_html+='</ul></details>'
    targets_html=''
    if p.get('session_targets'):
        targets_html='<section class="card" style="margin-top:18px"><h3>专项执行指标 · '+e(SPORTS.get(sport,sport))+'</h3><dl>'+''.join('<dt style="font-weight:600;margin-top:16px">'+e(label)+'</dt><dd style="margin:4px 0">'+e(value)+'</dd>' for label,value in p['session_targets'])+'</dl><small>个人保存的轻松训练区间与算术换算，不是生理阈值测定。到达时长即停止，不为凑距离加速；任何不适优先停止。未设置的指标可在“专项数值设置”补充一次。</small></section>'
    metrics=r.get('metrics',{})
    cards=''.join(f'<div class="metric"><span>{label}</span><strong>{e(metrics.get(key))}</strong><small>{unit}</small></div>' for key,label,unit in
        [('latest_sleep_hours','最新睡眠','小时'),('hrv_recent_mean','近期 HRV','Garmin 原始单位'),('last_complete_day_resting_hr','上一完整日静息心率','次 / 分')])
    flags=''.join('<li>'+e(f['reason'])+'</li>' for f in r.get('flags',[])) or '<li>未发现已设定的恢复不足线索；仍需结合缺项与症状复评。</li>'
    missing='、'.join(r.get('missing',[])) or '无已知缺项'
    sources=''
    for s in r.get('research',{}).get('reviewed_sources',[]):
        url=s.get('url','')
        if urlsplit(url).scheme in {'https','http'}:
            sources+=f'<li><a href="{e(url)}" rel="noreferrer">{e(s.get("title"))}</a> · {e(s.get("year"))}</li>'
    options=lambda selected: ''.join(f'<option value="{k}" {"selected" if k==selected else ""}>{v}</option>' for k,v in SPORTS.items())
    if r.get('race_context'):
        targets_html+='<section class="card" style="margin-top:18px"><h3>比赛计划与综合分析</h3><dl>'+''.join('<dt style="font-weight:600;margin-top:14px">'+e(label)+'</dt><dd style="margin:4px 0">'+e(value)+'</dd>' for label,value in r['race_context'])+'</dl><p>恢复结论：'+e(action)+' 安全筛查优先，比赛目标不能覆盖疼痛或恢复不足的判断。</p></section>'
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>训练与能力日报</title>
<style>
:root{color-scheme:light;--ink:#18221e;--muted:#68776f;--line:#dfe5df}*{box-sizing:border-box}body{margin:0;background:#f1f3ef;color:var(--ink);font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1120px;margin:32px auto;padding:0 28px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:26px}.brand{font-size:12px;letter-spacing:.18em;font-weight:750}h1{font-size:30px;margin:7px 0;font-weight:600;letter-spacing:-.04em}.muted,small{color:var(--muted)}.meta{font-size:12px;text-align:right}.hero{background:#172b23;color:#f7faf6;padding:32px;border-radius:16px}h2{font-size:27px;line-height:1.5;font-weight:500;margin:14px 0}.label{font-size:11px;letter-spacing:.12em;text-transform:uppercase}.hero .label{color:#c3db9c}.hero p{color:#d0ddd2}.grid{display:grid;grid-template-columns:1.4fr 1fr;gap:18px;margin:18px 0}.card{background:white;border:1px solid var(--line);border-radius:14px;padding:25px}h3{font-size:17px;margin:0 0 12px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);margin:18px 0;gap:12px}.metric{background:white;border:1px solid var(--line);padding:20px;border-radius:12px}.metric span,.metric small{display:block;font-size:12px}.metric strong{display:block;font-size:29px;font-weight:500;line-height:1.5}.boundary{background:#faf5eb}ul{padding-left:20px;font-size:13px}a{color:#386150}select,input,button{font:inherit;border:1px solid #cbd4cc;background:white;border-radius:7px;padding:9px;max-width:100%}label{display:block;font-size:12px;margin:10px 0}select{width:100%}button{cursor:pointer;background:#1a3327;color:white}textarea{width:100%;height:100px;font:13px/1.5 system-ui;border:1px solid var(--line);padding:10px;border-radius:7px}details{margin-top:18px}footer{font-size:12px;color:var(--muted);padding:18px 0 36px}@media(max-width:700px){main{padding:0 16px;margin:20px auto}.grid{grid-template-columns:1fr}.metrics{grid-template-columns:1fr}.hero{padding:22px}header{display:block}.meta{text-align:left}}
</style><main><header><div><div class="brand">PACE / DAILY BRIEF</div><h1>训练与能力日报</h1></div><div class="meta">'''+e(r.get('target_date'))+''' · 明日预建议<br>Asia / Dubai · 数据来源 Garmin</div></header>
<section class="hero"><div class="label">'''+e(SPORTS.get(primary,primary))+' / '+e(SPORTS.get(sport,sport))+'''</div><h2>'''+e(action)+'''</h2><p>'''+e(p.get('dose','以原报告建议为准，明早复评。'))+'''</p>'''+comparison_html+'''</section>'''+guidance_html+'''<div class="metrics">'''+cards+'''</div>
'''+targets_html+'''<div class="grid"><section class="card"><h3>能力处方总结</h3><p>'''+e(p.get('capacity_summary','以当前恢复线索决定是否降级训练。'))+'''</p><p>'''+e(p.get('capacity_focus','维持可恢复的训练节奏。'))+'''</p><div class="muted">长期目标：'''+e(r.get('goal'))+'''</div><hr style="border:0;border-top:1px solid #e5e9e4;margin:22px 0"><h3>本次依据</h3><ul>'''+flags+'''</ul></section>
<aside class="card"><h3>下一次训练选择</h3><p class="muted">选择后生成请求，复制给 MCP 重新分析。此页保留本次评估结果。</p><label>长期主项<select id="primary">'''+options(primary)+'''</select></label><label>本次项目<select id="sport">'''+options(sport)+'''</select></label><label>长期目标<input id="goal" style="width:100%" value="'''+e(r.get('goal',''))+'''"></label><button onclick="request()">生成分析请求</button><textarea id="request" aria-label="复制到 MCP 的分析请求" readonly></textarea></aside></div>
<section class="card boundary"><h3>未知项与调整条件</h3><p>缺项：'''+e(missing)+'''</p><p>'''+e(p.get('evidence_boundary','当前结果不等于医疗放行。'))+'''</p><p>'''+e(p.get('downgrade_rule','有不适应停止并复评。'))+'''</p><strong>明早同步并确认身体状态后再执行。</strong></section>
<details class="card"><summary>研究来源与检索范围</summary><p>检索状态：'''+e(r.get('research',{}).get('status'))+'''；上次成功检索：'''+e(r.get('research',{}).get('checked_on'))+'''</p><p>现有资料主要覆盖跑步与恢复；其他项目仅提供保守方向。新检索候选未自动成为训练规则。</p><ul>'''+sources+'''</ul></details><footer>生成时间：'''+e(r.get('generated_at'))+''' · 本地离线报告 · 缺失数据不显示为零</footer></main>
<script>function request(){const a=document.getElementById('primary'),b=document.getElementById('sport'),g=document.getElementById('goal');document.getElementById('request').value='请将长期主项设置为 '+a.value+'，长期目标为 '+g.value+'；使用 garmin_assess_session 评估明天的 '+b.value+'。请先询问尚未确认的症状和专项安全信息。';}</script></html>'''


    return html if show_controls else html.replace('<aside class="card">','<aside class="card" hidden>').replace('grid-template-columns:1.4fr 1fr','grid-template-columns:1fr')
