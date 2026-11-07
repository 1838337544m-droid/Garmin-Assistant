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
from .setup import SetupIssue, client_entry, configure, connect_claude, connect_codex, console_python, default_claude_path
from .setup_access import SetupFileError, setup_file_access, write_failure_message


SETUP_MESSAGES = {
    'existing_entry': ('The selected client already has a different Garmin connection. To switch it to this installation, select “Replace an existing Garmin entry” and save again. The original is backed up.',
                       '所选客户端已有另一个佳明连接。若要切换到当前安装，请勾选“替换已有佳明连接条目”再保存。系统会先备份原配置。'),
    'invalid_client_config': ('The client configuration format is invalid. Check the file in the client’s configuration editor.',
                              '客户端配置文件格式无效。请用客户端的配置编辑器检查文件。'),
    'missing_config_path': ('Choose the Claude configuration file opened by Edit Config.', '请选择 Claude“编辑配置”打开的配置文件。'),
    'missing_codex': ('Codex CLI was not found. Install it or choose another client.', '找不到 Codex CLI。请安装它或选择其他客户端。'),
    'codex_registration_failed': ('Codex rejected the MCP registration. Check the Codex CLI configuration.', 'Codex 拒绝注册 MCP。请检查 Codex CLI 配置。'),
    'invalid_settings': ('Check the IANA timezone and positive running goal values.', '请检查 IANA 时区，并填写大于零的跑步目标。'),
    'invalid_key_format': ('Paste one Garmin API key without internal spaces or line breaks.', '请粘贴一条完整的 Garmin API 密钥，密钥内部不能有空格或换行。'),
    'missing_key': ('No saved Garmin API key was found for this installation. Enter it in the key field.', '当前安装没有找到已保存的 Garmin API 密钥。请在密钥栏填写。'),
}


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
            entry=ttk.Entry(self.frame,textvariable=var,show='*' if name=='key' else '')
            entry.pack(fill='x')
            if name=='key':self.key_entry=entry
        ttk.Button(self.frame,text=self.text('Open Garmin key page','打开 Garmin 密钥页面'),command=lambda:webbrowser.open('https://connect.garmin.com/app/settings/personalApiToken')).pack(anchor='w',pady=5)
        ttk.Label(self.frame,text=self.text('AI client','AI 客户端')).pack(anchor='w')
        self.client=tk.StringVar(value='Claude Desktop')
        ttk.Combobox(self.frame,textvariable=self.client,state='readonly',values=['Claude Desktop','Codex CLI','DeepSeek API','Export only / 仅导出（豆包等）']).pack(fill='x')
        ttk.Label(self.frame,text=self.text('Claude config file (use the file opened by Edit Config)','Claude 配置文件（以客户端“编辑配置”打开的文件为准）')).pack(anchor='w',pady=(7,0))
        row=ttk.Frame(self.frame);row.pack(fill='x');self.path=tk.StringVar(value=str(default_claude_path()))
        ttk.Entry(row,textvariable=self.path).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text=self.text('Browse','浏览'),command=self.browse).pack(side='right')
        self.replace=tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame,text=self.text('Replace an existing Garmin entry (a backup is made first)','替换已有佳明连接条目（会先备份，不影响其他服务）'),variable=self.replace).pack(anchor='w',pady=7)
        buttons=ttk.Frame(self.frame);buttons.pack(fill='x',pady=7)
        self.save_button=ttk.Button(buttons,text=self.text('Save and connect','保存并接入'),command=self.save);self.save_button.pack(side='left')
        self.check_button=ttk.Button(buttons,text=self.text('Save and check Garmin','保存并检查 Garmin'),command=self.check);self.check_button.pack(side='left',padx=8)
        self.output=tk.Text(self.frame,height=8,wrap='word');self.output.pack(fill='both',expand=True)
        self.show(self.text('Save and check Garmin to verify your key independently. Save and connect to configure the selected AI client.','点“保存并检查 Garmin”单独验证密钥。点“保存并接入”配置所选 AI 客户端。'))

    def browse(self):
        path=filedialog.asksaveasfilename(initialfile='claude_desktop_config.json',filetypes=[('JSON','*.json')],confirmoverwrite=False)
        if path:self.path.set(path)

    def show(self,text):
        self.output.configure(state='normal');self.output.delete('1.0','end');self.output.insert('end',text);self.output.configure(state='disabled')

    def work(self,operation):
        if self.busy:return
        values={key:field.get() for key,field in self.values.items()}
        self.busy=True;self.save_button.configure(state='disabled');self.check_button.configure(state='disabled')
        self.key_entry.configure(state='disabled')
        self.show(self.text('Working…','处理中……'))
        def run():
            saved=None
            try:
                saved=configure(self.settings,self.language,values['timezone'],values['distance'],values['minutes'],values['key'])
                self.events.put((saved,True,operation(saved)))
                return
            except SetupIssue as exc:
                detail=self.text(*SETUP_MESSAGES[exc.args[0]])
            except subprocess.TimeoutExpired:
                detail=self.text('The connection or client check timed out. Try again.','连接或客户端检查超时，请重试。')
            except SetupFileError as exc:
                detail=write_failure_message(exc,self.language,sys.platform=='win32')
            except OSError:
                detail=self.text('A local file or program could not be accessed. Check permissions and close the client if it is using the configuration file.','无法访问本机文件或程序。请检查权限；若配置文件正被客户端占用，请先退出客户端。')
            except Exception:
                detail=self.text('The local operation failed. Check the client configuration and try again.','本机操作失败。请检查客户端配置后重试。')
            stage=self.text('Garmin settings saved. ','Garmin 本机设置已保存。') if saved else self.text('Could not save Garmin settings. ','未能保存 Garmin 本机设置。')
            self.events.put((saved,False,stage+detail))
        threading.Thread(target=run,daemon=True).start()

    def poll(self):
        try:
            saved,ok,result=self.events.get_nowait();self.busy=False
            self.key_entry.configure(state='normal')
            if saved:
                self.settings=saved
                self.values['key'].set('')
            self.save_button.configure(state='normal');self.check_button.configure(state='normal');self.show(result)
            if not ok:messagebox.showerror(self.text('Action failed','操作失败'),result)
        except queue.Empty:pass
        self.root.after(100,self.poll)

    def save(self):
        client=self.client.get();path=self.path.get();replace=self.replace.get()
        def operation(settings):
            if client=='Claude Desktop':backup=connect_claude(path,settings,replace)
            elif client=='Codex CLI':backup=connect_codex(settings,replace)
            elif client=='DeepSeek API':
                return self.text('Garmin settings saved. Check the Garmin connection, then open Garmin Assistant DeepSeek from the Windows Start menu, or run garmin-assistant deepseek in your installed environment.',
                                 '佳明设置已保存。检查 Garmin 连接后，从 Windows 开始菜单打开 Garmin Assistant DeepSeek，或在已安装环境中运行 garmin-assistant deepseek。')
            else:
                target=settings.data_dir/'client-config.json'
                with setup_file_access('export', target):
                    atomic_json(target,{'mcpServers':{'garmin-assistant':client_entry(settings)}})
                return self.text('Settings saved. Configuration exported to: ','设置已保存。配置导出至：')+str(target)+'\n'+self.text('Import only if your client supports local stdio MCP. This does not connect ordinary web/mobile chats.','仅适用于支持本地 stdio MCP 的客户端，普通网页／手机聊天不能直接连接。')
            menu=localize_result(MenuStore(settings.data_dir/'menu-preferences.json').view(),self.language)
            return self.text('Garmin settings saved and client configured. Use Save and check Garmin to verify the connection, then restart the AI client.','Garmin 设置已保存，客户端已配置。请点“保存并检查 Garmin”验证连接，再重启 AI 客户端。')+'\n'+(self.text('Backup: ','备份：')+str(backup)+'\n' if backup else '')+json.dumps(menu,ensure_ascii=False,indent=2)
        self.work(operation)

    def check(self):
        def operation(settings):
            result=subprocess.run([console_python(),'-m','garmin_assistant','doctor','--live'],capture_output=True,timeout=90)
            try:data=json.loads(result.stdout.decode('utf-8'))
            except (ValueError,UnicodeError):raise ValueError('Invalid diagnostic response') from None
            status=data.get('garmin_status','not_checked')
            error=data.get('error') or ''
            if error.startswith('authentication_failed'):
                return self.text('Settings saved. Garmin rejected the credential. Check or renew your Garmin Personal API key.', '设置已保存。Garmin 拒绝了凭据，请检查或更新 Garmin Personal API 密钥。')
            if error.startswith('rate_limited'):
                return self.text('Settings saved. Garmin rate limit reached. Try again later.', '设置已保存。Garmin 请求受到限流，请稍后重试。')
            if result.returncode or status not in ('ok','no_data'):
                return self.text('Settings saved. A live Garmin read could not be verified. Check the network and retry.', '设置已保存。未能验证 Garmin 实时读取，请检查网络后重试。')
            if status=='no_data':
                return self.text('Garmin connection verified. Garmin returned no data for today.', 'Garmin 连接验证通过。Garmin 今天没有返回记录。')
            return self.text('Garmin connection verified. Live data read succeeded.', 'Garmin 连接验证通过，已成功实时读取数据。')
        self.work(operation)


def run():
    root=tk.Tk();SetupWindow(root);root.mainloop()


if __name__=='__main__':run()
