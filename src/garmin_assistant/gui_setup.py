"""Optional Tk setup UI. Network/client processes run outside the Tk event loop."""
import json
import queue
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .config import load_settings
from .menu import MenuStore
from .onboarding import localize_result
from .research import atomic_json
from .setup import client_entry, configure, connect_claude, connect_codex, default_claude_path


class SetupWindow:
    def __init__(self,root):
        self.root=root;self.settings=load_settings();self.events=queue.Queue();self.busy=False
        root.title(f'Garmin Assistant | 佳明助手 {__version__}');root.geometry('780x720');root.minsize(680,650)
        self.frame=ttk.Frame(root,padding=20);self.frame.pack(fill='both',expand=True)
        ttk.Label(self.frame,text='Welcome to Garmin Assistant!\n欢迎首次使用佳明助手！',font=('',17),justify='center').pack(pady=30)
        ttk.Label(self.frame,text='Please choose your language / 请选择语言').pack(pady=15)
        ttk.Button(self.frame,text='English',command=lambda:self.form('en')).pack(pady=8)
        ttk.Button(self.frame,text='中文',command=lambda:self.form('zh')).pack(pady=8)
        root.after(100,self.poll)

    def text(self,en,zh):return zh if self.language=='zh' else en

    def form(self,language):
        self.language=language
        for child in self.frame.winfo_children():child.destroy()
        ttk.Label(self.frame,text=self.text('Local setup','本机设置'),font=('',18)).pack(anchor='w')
        ttk.Label(self.frame,text=self.text('Your key stays on this computer. Never paste it into AI chat.','密钥保存在本机，请不要发送到 AI 聊天里。')).pack(anchor='w',pady=8)
        self.values={}
        fields=[('key','Garmin Personal API key (leave blank to keep existing)','Garmin API 密钥（已保存可留空）',''),
                ('timezone','IANA timezone, e.g. Asia/Dubai or America/New_York','IANA 时区，例如 Asia/Shanghai 或 Asia/Dubai',self.settings.timezone),
                ('distance','Running goal: distance in km','跑步目标：距离（公里）',str(self.settings.goal_distance_km)),
                ('minutes','Running goal: finish time in minutes','跑步目标：完成时间（分钟）',str(self.settings.goal_minutes))]
        for name,en,zh,value in fields:
            ttk.Label(self.frame,text=self.text(en,zh)).pack(anchor='w',pady=(7,0))
            var=tk.StringVar(value=value);self.values[name]=var
            ttk.Entry(self.frame,textvariable=var,show='*' if name=='key' else '').pack(fill='x')
        ttk.Button(self.frame,text=self.text('Open Garmin key page','打开 Garmin 密钥页面'),command=lambda:webbrowser.open('https://connect.garmin.com/app/settings/personalApiToken')).pack(anchor='w',pady=5)
        ttk.Label(self.frame,text=self.text('AI client','AI 客户端')).pack(anchor='w')
        self.client=tk.StringVar(value='Claude Desktop')
        ttk.Combobox(self.frame,textvariable=self.client,state='readonly',values=['Claude Desktop','Codex CLI','Export only / 仅导出（豆包等）']).pack(fill='x')
        ttk.Label(self.frame,text=self.text('Claude config file (use the file opened by Edit Config)','Claude 配置文件（以客户端“编辑配置”打开的文件为准）')).pack(anchor='w',pady=(7,0))
        row=ttk.Frame(self.frame);row.pack(fill='x');self.path=tk.StringVar(value=str(default_claude_path()))
        ttk.Entry(row,textvariable=self.path).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text=self.text('Browse','浏览'),command=self.browse).pack(side='right')
        self.replace=tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame,text=self.text('Replace an existing Garmin entry (a backup is made first)','替换已有佳明连接条目（会先备份，不影响其他服务）'),variable=self.replace).pack(anchor='w',pady=7)
        buttons=ttk.Frame(self.frame);buttons.pack(fill='x',pady=7)
        self.save_button=ttk.Button(buttons,text=self.text('Save and connect','保存并接入'),command=self.save);self.save_button.pack(side='left')
        self.check_button=ttk.Button(buttons,text=self.text('Check Garmin connection','检查 Garmin 连接'),command=self.check);self.check_button.pack(side='left',padx=8)
        self.output=tk.Text(self.frame,height=8,wrap='word');self.output.pack(fill='both',expand=True)
        self.show(self.text('Select your client, then Save and connect. Export only does not connect a chat platform automatically.','选择客户端，再点“保存并接入”。“仅导出”不会自动连接聊天平台。'))

    def browse(self):
        path=filedialog.asksaveasfilename(initialfile='claude_desktop_config.json',filetypes=[('JSON','*.json')],confirmoverwrite=False)
        if path:self.path.set(path)

    def show(self,text):
        self.output.configure(state='normal');self.output.delete('1.0','end');self.output.insert('end',text);self.output.configure(state='disabled')

    def work(self,operation):
        if self.busy:return
        self.busy=True;self.save_button.configure(state='disabled');self.check_button.configure(state='disabled')
        self.show(self.text('Working…','处理中……'))
        def run():
            try:self.events.put((True,operation()))
            except Exception:self.events.put((False,self.text('Setup failed. Check the key, timezone, file permissions, selected config file, existing-entry checkbox and client installation. Existing configuration backups are retained.','设置失败。请检查密钥、时区、文件权限、配置路径、是否勾选替换已有条目及客户端是否安装。已有配置备份会保留。')))
        threading.Thread(target=run,daemon=True).start()

    def poll(self):
        try:
            ok,result=self.events.get_nowait();self.busy=False
            self.save_button.configure(state='normal');self.check_button.configure(state='normal');self.show(result)
            if not ok:messagebox.showerror(self.text('Action failed','操作失败'),result)
        except queue.Empty:pass
        self.root.after(100,self.poll)

    def save(self):
        values={k:v.get() for k,v in self.values.items()};client=self.client.get();path=self.path.get();replace=self.replace.get()
        def operation():
            settings=configure(self.settings,self.language,values['timezone'],values['distance'],values['minutes'],values['key'])
            self.settings=settings
            if client=='Claude Desktop':backup=connect_claude(path,settings,replace)
            elif client=='Codex CLI':backup=connect_codex(settings,replace)
            else:
                target=settings.data_dir/'client-config.json';atomic_json(target,{'mcpServers':{'garmin-assistant':client_entry(settings)}})
                return self.text('Settings saved. Configuration exported to: ','设置已保存。配置导出至：')+str(target)+'\n'+self.text('Import only if your client supports local stdio MCP. This does not connect ordinary web/mobile chats.','仅适用于支持本地 stdio MCP 的客户端，普通网页／手机聊天不能直接连接。')
            menu=localize_result(MenuStore(settings.data_dir/'menu-preferences.json').view(),self.language)
            return self.text('Client configuration saved. Garmin connection has not yet been checked. Click Check Garmin connection, then restart the AI client and say “Start Garmin Assistant”.','客户端配置已保存，尚未验证 Garmin 连接。请点“检查 Garmin 连接”，然后重启 AI 客户端并说“启动佳明助手”。')+'\n'+(self.text('Backup: ','备份：')+str(backup)+'\n' if backup else '')+json.dumps(menu,ensure_ascii=False,indent=2)
        self.work(operation)
        # Tk variables are only accessed on the UI thread; do not retain the pasted key in the form.
        self.values['key'].set('')

    def check(self):
        def operation():
            result=subprocess.run([sys.executable,'-m','garmin_assistant','doctor','--live'],capture_output=True,timeout=90)
            try:data=json.loads(result.stdout.decode('utf-8'))
            except (ValueError,UnicodeError):raise ValueError('Invalid diagnostic response') from None
            status=data.get('garmin_status','not_checked')
            if result.returncode or status in ('error','stale','not_checked'):
                return self.text('Garmin connection is not verified. Save settings first; check the key and network. Status: ','Garmin 连接未验证。请先保存设置，并检查密钥和网络。状态：')+status
            return self.text('Garmin check completed. Status: ','Garmin 检查完成。状态：')+status+'\n'+self.text('Restart your AI client and say “Show original function menu”.','重启 AI 客户端后，输入“显示原有功能菜单”。')
        self.work(operation)


def run():
    root=tk.Tk();SetupWindow(root);root.mainloop()


if __name__=='__main__':run()
