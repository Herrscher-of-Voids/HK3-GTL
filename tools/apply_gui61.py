"""Change #1 2026-09-23 12:07:00 revision61.
Archive exact originals, migrate HK3 screens and terminal to viewport fitting.
归档原文件后迁移坐标，不修改研究/配方/玩家存档；仅运行一次。
"""
from pathlib import Path
from datetime import datetime
import shutil, re

root = Path(__file__).resolve().parents[1]
stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
archive = root / 'archive' / ('gui61-' + stamp.replace(':', '-').replace(' ', '_'))
base = 'src/main/java/com/sirin/hk3gtl/'

def update(rel, transform):
    p = root / rel
    text = p.read_text(encoding='utf-8')
    target = archive / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, target)
    result = transform(text)
    numbers = [int(n) for n in re.findall(r'变更记录 #(\d+)', text)]
    note = f'''/**
 * 【变更记录 #{max(numbers, default=0)+1}】{stamp}（内测5修订61）
 * 删除：无，旧布局完整归档。新增：视窗自适应与统一鼠标坐标变换。
 * 修改：仅在可用视窗不足时等比缩小，裁剪区域与实际绘制同步。
 * 用途：小窗口保持完整可操作界面；不修改服务端研究费用、凭据或权限。
 * Fit small viewports with consistent rendering, clipping and input. Preserve server-side progression rules.
 */
'''
    result = re.sub(r'(?m)^public (?:final )?class ', lambda m: note+m[0], result, count=1)
    p.write_text(result, encoding='utf-8')

def terminal(s):
    s = s.replace('g.pose().translate(getPositionX(),getPositionY(),0);',
        'var fit=fit(); g.pose().translate(fit.left(),fit.top(),0);\n        g.pose().scale((float)fit.scale(),(float)fit.scale(),1);')
    s = s.replace('g.enableScissor(getPositionX()+168,getPositionY()+58,getPositionX()+506,getPositionY()+157);',
        'g.enableScissor((int)Math.floor(fit.screenX(168)),(int)Math.floor(fit.screenY(58)),\n                (int)Math.ceil(fit.screenX(506)),(int)Math.ceil(fit.screenY(157)));')
    s = s.replace('int x=mx-getPositionX(),y=my-getPositionY();',
        'int x=(int)Math.floor(fit().x(mx)),y=(int)Math.floor(fit().y(my));')
    s = s.replace('int x=(int)mx-getPositionX(),y=(int)my-getPositionY()',
        'int x=(int)Math.floor(fit().x(mx)),y=(int)Math.floor(fit().y(my))')
    s = s.replace('dragScroll(y-getPositionY())', 'dragScroll(fit().y(y))')
    marker = '    private void send(String value)'
    addition = '''    /** 每次读取当前视窗以支持打开时调整窗口；不影响服务端控件ID和状态同步。
     * Read the current GUI viewport on demand; resizing never alters server widget IDs or synchronization.
     */
    @OnlyIn(Dist.CLIENT) private Hk3GuiFit fit() {
        var window=Minecraft.getInstance().getWindow();
        return Hk3GuiFit.centered(Math.max(1,window.getGuiScaledWidth()),Math.max(1,window.getGuiScaledHeight()),WIDTH,HEIGHT,8);
    }
    /** 点击区域与缩放后面板一致；面板外不得提交操作。 / Only the fitted visible panel accepts pointer actions. */
    @Override @OnlyIn(Dist.CLIENT) public boolean isMouseOverElement(double x,double y) {
        return fit().contains(x,y,WIDTH,HEIGHT);
    }
'''
    return s.replace(marker, addition+marker)

update(base+'common/gui/Hk3ResearchTerminalWidget.java', terminal)

screens = {
    'bootstrap/Hk3ModWelcomeScreen.java': (444,304),
    'narrative/Hk3NarrativeCodexScreen.java': (444,344),
    'communication/Hk3LetterScreen.java': (380,240),
    'dialogue/Hk3DialogueScreen.java': (640,320),
    'research/Hk3ResearchMatrixScreen.java': (620,360),
}
names = {'init':'initFitted','render':'renderFitted','mouseClicked':'clickFitted',
         'mouseReleased':'releaseFitted','mouseDragged':'dragFitted','mouseScrolled':'scrollFitted'}
for path, (w,h) in screens.items():
    def convert(s, w=w, h=h, path=path):
        s = s.replace('extends Screen', 'extends com.sirin.hk3gtl.client.gui.Hk3FittedScreen')
        # Each existing screen constructor passes only its title to Screen.
        s = re.sub(r'(?m)^(\s*)super\((Component\.[^\n]+)\);', rf'\1super(\2, {w}, {h});', s)
        for old,new in names.items():
            s = re.sub(r'\b(void|boolean) '+old+r'\(', rf'\1 {new}(', s)
            s = s.replace('super.'+old+'(', 'super.'+new+'(')
        s = s.replace('gui.enableScissor(', 'fittedScissor(gui, ')
        if path.startswith('research/'):
            # Screen.init clears children on resize; reuse the button but reattach it.
            s = s.replace('submitButton.setX(submitX);', 'this.addRenderableWidget(submitButton);\n            submitButton.setX(submitX);')
        if path.startswith('dialogue/'):
            # Resizing should retain the current line, animation and choices.
            s = s.replace('        loadSegment(currentSegmentId);\n    }', '''        if (currentLines.isEmpty()) loadSegment(currentSegmentId);
        else if (showingChoices && lineIndex < currentLines.size()) showChoices(currentLines.get(lineIndex).choices());
    }''',1)
        return s
    update(base+'client/'+path, convert)
print(archive)
