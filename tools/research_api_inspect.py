"""Read GT runtime APIs for targeted research integration, without loading a game."""
from pathlib import Path
import zipfile
z=zipfile.ZipFile(next(Path('.gradle').rglob('*gtceu*sources.jar')))
for name in ['api/machine/trait/RecipeLogic.java','api/pattern/BlockPattern.java','api/capability/IEnergyContainer.java']:
    s=z.read('com/gregtechceu/gtceu/'+name).decode('utf-8')
    if name.endswith('RecipeLogic.java'):
        for key in ['void onRecipeFinish','boolean handleRecipeIO','afterWorking()']:
            i=s.find(key); print(name,key,s[max(0,i-100):i+2200])
    elif 'BlockPattern' in name:
        for line in s.splitlines():
            if any(x in line for x in ['autoBuild','checkPattern','getPreview']): print(line)
    else:
        i=s.find('removeEnergy'); print(s[i-180:i+450])

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
