param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'GarminAssistantAPI-App'),
    [string]$PythonExecutable = '',
    [switch]$SkipSetup
)
$ErrorActionPreference = 'Stop'

function Find-Python {
    $candidates = @()
    if ($PythonExecutable) { $candidates += @{Exe=$PythonExecutable; Prefix=@()} }
    $candidates += @{Exe='py'; Prefix=@('-3.13')}
    $candidates += @{Exe='py'; Prefix=@('-3.12')}
    $candidates += @{Exe=(Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'); Prefix=@()}
    $candidates += @{Exe=(Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'); Prefix=@()}
    $candidates += @{Exe='python'; Prefix=@()}
    foreach ($candidate in $candidates) {
        try {
            $exe = $candidate.Exe
            $prefixArgs = $candidate.Prefix
            $resolved = & $exe @prefixArgs -c "import sys, tkinter, venv; assert (3,12) <= sys.version_info[:2] <= (3,13); print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $resolved -and (Test-Path -LiteralPath ([string]$resolved))) { return [string]$resolved }
        } catch { }
    }
    return $null
}

try {
    Write-Host 'Garmin Assistant installer / Garmin Assistant API local setup'
    Write-Host 'Internet is required. Your API key will be entered in a separate local window.'
    $version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION') -Raw).Trim()
    if ($version -notmatch '^\d+\.\d+\.\d+$') { throw 'Invalid installer version.' }
    $wheels = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'garmin_assistant_api-*.whl')
    if ($wheels.Count -ne 1) { throw 'Extract the entire ZIP first. One application wheel must be beside Install.cmd.' }
    $expected = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'WHEEL-SHA256.txt') -Raw).Trim()
    $actual = (Get-FileHash -LiteralPath $wheels[0].FullName -Algorithm SHA256).Hash
    if ($expected -ne $actual) { throw 'Application checksum failed. Download the release again.' }
    if ($wheels[0].Name -ne "garmin_assistant_api-$version-py3-none-any.whl") { throw 'Installer and application version mismatch.' }
    $pythonPath = Find-Python
    if (-not $pythonPath) {
        if ($SkipSetup) { throw 'Python 3.12 or 3.13 with Tk is required. Install from python.org, then retry.' }
        Add-Type -AssemblyName System.Windows.Forms
        $choice = [System.Windows.Forms.MessageBox]::Show(
            "Python 3.12/3.13 with Tk is required. Install Python 3.12 for this user using WinGet? This downloads Python and accepts its package/source agreements. No admin install is requested.`n`n需要 Python 3.12/3.13。是否通过 WinGet 为当前用户安装 Python 3.12？将下载软件并接受软件包和来源协议，不请求管理员安装。",
            'Garmin Assistant / 佳明助手', 'YesNo', 'Question')
        if ($choice -ne 'Yes') { throw 'Python installation cancelled. Install Python 3.12/3.13 from python.org (including Tcl/Tk), then retry.' }
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'WinGet unavailable. Install Python 3.12/3.13 with Tcl/Tk from https://www.python.org/downloads/windows/ and retry.' }
        & winget install --id Python.Python.3.12 --exact --source winget --scope user --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { throw 'Python installation failed. Install Python 3.12/3.13 with Tcl/Tk from python.org and retry.' }
        $pythonPath = Find-Python
        if (-not $pythonPath) { throw 'Python was not found after installation. Restart the installer or install Python with Tcl/Tk from python.org.' }
    }
    $versionDir = Join-Path $InstallRoot $version
    $venvDir = Join-Path $versionDir 'venv'
    $venvPython = Join-Path $venvDir 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        New-Item -ItemType Directory -Path $versionDir -Force | Out-Null
        & $pythonPath -m venv $venvDir
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the private Python environment.' }
    }
    & $venvPython -m pip install --disable-pip-version-check $wheels[0].FullName
    if ($LASTEXITCODE -ne 0) { throw 'Package installation failed. Check internet/proxy settings and retry. Existing user data has been preserved.' }
    & $venvPython -c "import tkinter; from garmin_assistant import __version__; assert __version__ == '$version'"
    if ($LASTEXITCODE -ne 0) { throw 'Installed runtime check failed.' }
    Write-Host "Installed: $venvPython"
    if (-not $SkipSetup) {
        $pythonw = Join-Path $venvDir 'Scripts\pythonw.exe'
        $shellObject = New-Object -ComObject WScript.Shell
        $shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'Garmin Assistant Setup.lnk'
        $shortcut = $shellObject.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $pythonw
        $shortcut.Arguments = '-m garmin_assistant setup'
        $shortcut.WorkingDirectory = $versionDir
        $shortcut.Save()
        $chatShortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'Garmin Assistant DeepSeek.lnk'
        $chatShortcut = $shellObject.CreateShortcut($chatShortcutPath)
        $chatShortcut.TargetPath = $venvPython
        $chatShortcut.Arguments = '-m garmin_assistant deepseek'
        $chatShortcut.WorkingDirectory = $versionDir
        $chatShortcut.Save()
        # This is an interactive setup window explicitly opened by the user.
        & $venvPython -m garmin_assistant setup
        if ($LASTEXITCODE -ne 0) { throw 'Setup window could not start. Check Tcl/Tk and the installation guide.' }
    }
    exit 0
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host '安装未完成。请查看上方原因，解压完整安装包后重试；缺少 Python 时请从 python.org 安装 3.12/3.13 并包含 Tcl/Tk。'
    Write-Host 'Guide / 使用说明: https://github.com/1838337544m-droid/Garmin-Assistant/blob/main/docs/EASY_INSTALL.md'
    exit 1
}
