"""Target only the explicitly identified development Minecraft window for smoke testing.

Change #1 2026-09-22: screenshot and normalized client-area clicks/keys, rejecting other processes.
Change #2 2026-09-22 21:04:00: add targeted right-click for native machine UI inspection; hold mouse for polling.
Never targets Prism, sends chat to other people, or opens an existing save automatically.
"""
import argparse, ctypes, time
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab

p=argparse.ArgumentParser(); p.add_argument('--pid',type=int,required=True)
p.add_argument('--click',nargs=2,type=float); p.add_argument('--key'); p.add_argument('--text')
p.add_argument('--right-click',action='store_true')
args=p.parse_args()
u=ctypes.windll.user32; u.SetProcessDPIAware(); u.GetForegroundWindow.restype=wintypes.HWND
found=[]
CALLBACK=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
@CALLBACK
def visit(hwnd,_):
    pid=wintypes.DWORD(); u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    title=ctypes.create_unicode_buffer(512); u.GetWindowTextW(hwnd,title,512)
    if pid.value==args.pid and u.IsWindowVisible(hwnd) and any(t in title.value for t in ('Minecraft', 'GregTech Leisure')):
        found.append(hwnd)
    return True
u.EnumWindows(visit,0)
assert len(found)==1,found
hwnd=found[0]; u.SetForegroundWindow(hwnd); time.sleep(.4)
assert u.GetForegroundWindow()==hwnd,'Focus changed'
r=wintypes.RECT(); u.GetClientRect(hwnd,ctypes.byref(r)); pt=wintypes.POINT(); u.ClientToScreen(hwnd,ctypes.byref(pt))
if args.click:
    x,y=args.click; assert 0<=x<=1 and 0<=y<=1
    u.SetCursorPos(pt.x+int(r.right*x),pt.y+int(r.bottom*y)); u.mouse_event(2,0,0,0,0); time.sleep(.12); u.mouse_event(4,0,0,0,0)
if args.right_click:
    u.mouse_event(8,0,0,0,0); time.sleep(.12); u.mouse_event(16,0,0,0,0)
if args.key:
    keys={'ESC':27,'ENTER':13,'E':69,'F3':114,'T':84,'TAB':9,'SLASH':191,'SELECT_ALL':65}
    if args.key=='SELECT_ALL': u.keybd_event(17,0,0,0)
    k=keys[args.key]; scan=u.MapVirtualKeyW(k,0)
    u.keybd_event(k,scan,0,0); time.sleep(.12); u.keybd_event(k,scan,2,0)
    if args.key=='SELECT_ALL': u.keybd_event(17,0,2,0)
if args.text:
    # WM_CHAR only enters text into the already reviewed Minecraft screen.
    for c in args.text: u.PostMessageW(hwnd,0x102,ord(c),0)
time.sleep(.7)
assert u.GetForegroundWindow()==hwnd,'Focus changed before capture'
dest=Path(__file__).resolve().parents[1]/'build/industrial-game-smoke.png'
ImageGrab.grab(bbox=(pt.x,pt.y,pt.x+r.right,pt.y+r.bottom),all_screens=True).save(dest)
print(dict(pid=args.pid,hwnd=hwnd,width=r.right,height=r.bottom,screenshot=str(dest)))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
