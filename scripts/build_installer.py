"""Build the Windows launcher ZIP from a wheel, never from a private workspace."""
import hashlib
import tomllib
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build():
    version=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    wheel=ROOT/'dist'/f'garmin_assistant_api-{version}-py3-none-any.whl'
    if not wheel.is_file():raise FileNotFoundError('Build the matching wheel first')
    target=ROOT/'dist'/f'Garmin-Assistant-{version}-Windows-Installer.zip'
    prefix=f'Garmin-Assistant-{version}'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.write(wheel,f'{prefix}/{wheel.name}')
        archive.writestr(f'{prefix}/VERSION',version+'\n')
        archive.writestr(f'{prefix}/WHEEL-SHA256.txt',hashlib.sha256(wheel.read_bytes()).hexdigest()+'\n')
        for name in ('Install.cmd','Install.ps1'):
            # Windows PowerShell 5.1 requires a BOM for non-ASCII source text.
            data=(ROOT/'installer'/name).read_text(encoding='utf-8')
            archive.writestr(f'{prefix}/{name}',data.encode('utf-8-sig' if name.endswith('.ps1') else 'utf-8'))
        archive.writestr(f'{prefix}/README-FIRST.txt',(
            'Garmin Assistant - Windows installer\n\n'
            '1. Extract ALL files from this ZIP. Do not run inside the ZIP preview.\n'
            '2. Double-click Install.cmd. Internet access is required.\n'
            '3. If Python is missing, choose whether to install it using WinGet.\n'
            '4. In the local window choose English or 中文, enter your own Garmin API key, timezone and client.\n'
            '5. Save and connect, check Garmin connection, then restart your AI client.\n'
            'Never paste API keys into AI chat. Ordinary web chats cannot install a local MCP.\n'
            'This is an unsigned script-based installer, not a signed EXE or official platform plugin.\n'
            'If Windows or your organization blocks it, ask your administrator or use the manual guide; do not disable security controls.\n\n'
            '佳明助手 - Windows 安装包\n\n'
            '1. 先解压全部文件，不要在 ZIP 预览窗口内直接运行。\n'
            '2. 双击 Install.cmd，需要联网下载依赖。\n'
            '3. 缺少 Python 时，可选择是否通过 WinGet 安装。\n'
            '4. 本地窗口中选择中文或 English，填写自己的密钥、时区并选择客户端。\n'
            '5. 保存并接入，检查 Garmin 连接，再重启 AI 客户端。\n'
            '不要把密钥发送到聊天里。普通网页聊天不能自动安装本地 MCP。\n'
            '这是未签名的脚本安装包，不是签名 EXE 或平台官方插件。若系统／组织策略阻止，请联系管理员或使用手动安装说明，不要关闭安全防护。\n\n'
            'https://github.com/1838337544m-droid/Garmin-Assistant/blob/main/docs/EASY_INSTALL.md\n'
        ).encode('utf-8-sig'))
    print(target.name)
    return target


if __name__=='__main__':build()
