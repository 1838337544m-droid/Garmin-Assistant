"""Diagnose setup file access failures without exposing raw exception text."""
import errno
import sys
from contextlib import contextmanager


class SetupFileError(OSError):
    def __init__(self, target, path, error):
        super().__init__(error.errno, 'Setup file access failed')
        self.target = target
        self.path = path
        code = getattr(error, 'winerror', None)
        if code in (32, 33):
            self.reason = 'in_use'
        elif isinstance(error, PermissionError) or code in (5, 1314) or error.errno in (errno.EACCES, errno.EPERM, errno.EROFS):
            self.reason = 'access'
        else:
            self.reason = 'other'


@contextmanager
def setup_file_access(target, path):
    try:
        yield
    except OSError as error:
        raise SetupFileError(target, path, error) from None


def windows_integrity_level():
    """Best-effort integrity label for the process that attempted the write."""
    if sys.platform != 'win32':
        return None
    import ctypes as ct
    from ctypes import wintypes as wt

    kernel = ct.WinDLL('kernel32')
    security = ct.WinDLL('advapi32')
    kernel.GetCurrentProcess.restype = wt.HANDLE
    kernel.CloseHandle.argtypes = [wt.HANDLE]
    security.OpenProcessToken.argtypes = [wt.HANDLE, wt.DWORD, ct.POINTER(wt.HANDLE)]
    security.GetTokenInformation.argtypes = [wt.HANDLE, ct.c_int, ct.c_void_p, wt.DWORD, ct.POINTER(wt.DWORD)]
    security.GetSidSubAuthorityCount.argtypes = [ct.c_void_p]
    security.GetSidSubAuthorityCount.restype = ct.POINTER(ct.c_ubyte)
    security.GetSidSubAuthority.argtypes = [ct.c_void_p, wt.DWORD]
    security.GetSidSubAuthority.restype = ct.POINTER(wt.DWORD)

    token = wt.HANDLE()
    if not security.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008, ct.byref(token)):
        return None
    try:
        size = wt.DWORD()
        # TokenIntegrityLevel returns a TOKEN_MANDATORY_LABEL, whose first field is the SID pointer.
        security.GetTokenInformation(token, 25, None, 0, ct.byref(size))
        if not size.value:
            return None
        buffer = ct.create_string_buffer(size.value)
        if not security.GetTokenInformation(token, 25, buffer, size.value, ct.byref(size)):
            return None
        sid = ct.cast(buffer, ct.POINTER(ct.c_void_p))[0]
        if not sid:
            return None
        count = security.GetSidSubAuthorityCount(sid)
        if not count or not count[0]:
            return None
        authority = security.GetSidSubAuthority(sid, count[0] - 1)
        if not authority:
            return None
        level = authority[0]
        return next(label for minimum, label in ((0x4000, 'System'), (0x3000, 'High'),
                    (0x2000, 'Medium'), (0x1000, 'Low'), (0, 'Untrusted')) if level >= minimum)
    finally:
        kernel.CloseHandle(token)


def write_failure_message(error, language, windows):
    zh = language == 'zh'
    if error.target == 'client_read':
        message = '无法读取现有 AI 客户端配置。' if zh else 'Could not read the existing AI client configuration.'
    elif error.target == 'client':
        message = '无法写入 AI 客户端配置。' if zh else 'Could not write the AI client configuration.'
    elif error.target == 'export':
        message = '无法写入导出的客户端配置。' if zh else 'Could not write the exported client configuration.'
    else:
        message = '无法写入佳明助手本机数据。' if zh else 'Could not write Garmin Assistant local data.'
    if error.path:
        message += f'\n{error.path}'
    if error.reason == 'in_use':
        return message + ('\n文件正在被占用。请关闭相关客户端后重试。' if zh
                          else '\nThe file is in use. Close the relevant client and try again.')
    if error.reason == 'access':
        if error.target == 'client_read':
            message += '\n当前进程没有读取权限。' if zh else '\nThe current process lacks read access.'
        else:
            message += '\n当前进程没有写入权限。' if zh else '\nThe current process lacks write access.'
        if windows:
            try:
                level = windows_integrity_level()
            except (OSError, ValueError):
                level = None
            if level:
                message += (f' Windows 进程完整性级别为 {level}。' if zh
                            else f' Windows process integrity level is {level}.')
            message += ('\n请从 Windows 开始菜单打开 Garmin Assistant Setup，或用平常登录的 Windows 账户双击 Install.cmd，再试一次。' if zh
                        else '\nOpen Garmin Assistant Setup from the Windows Start menu, or double-click Install.cmd under your normal Windows user account, then try again.')
        return message
    return message + ('\n请检查该位置是否可用，再重试。' if zh else '\nCheck that the location is available and try again.')
