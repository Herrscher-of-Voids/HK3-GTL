"""修订90 · 2026-09-27 04:27:05：验证静态审计确实能拦截典型回退。
删除：无。新增：内存中的错误夹具；修改：不写生产源码；用途：审计规则失效时返回非零。
"""
import json
from unittest.mock import patch
import audit_industrial_consistency as audit

def main():
    original_read=audit.read;results=[]
    scenarios=[
        ('跨级标签','src/main/resources/data/forge/tags/items/circuits/hbv.json',
         lambda s:s.replace('hk3gtl:hbv_processor','hk3gtl:hcv_assembly'),'voltage_tag'),
        ('Java等级偏移','src/main/java/com/sirin/hk3gtl/common/item/Hk3CircuitCatalog.java',
         lambda s:s.replace('"hbv_processor", 15','"hbv_processor", 16'),'catalog_java_resource'),
        ('错误上一形态','src/main/java/com/sirin/hk3gtl/common/recipe/Hk3CircuitManufacturing.java',
         lambda s:s.replace('e.form() == form - 1','e.form() == form - 2'),'exact_previous_form'),
        ('具体系列代替通用电路','src/main/java/com/sirin/hk3gtl/common/recipe/machine/AdvancedControllerRecipes.java',
         lambda s:s.replace('com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(circuitTier), 64',
                            'new ItemStack(FinalityCircuitItems.CIRCUIT_CEV.get(), 64)'),'ordinary_controllers'),
        ('电子部件纹理失联','src/main/resources/assets/hk3gtl/models/item/honkai_lattice_ram_chip.json',
         lambda s:json.dumps({**json.loads(s),'textures':{'layer0':'hk3gtl:item/missing_fixture_texture'}}),'item_resource'),
        ('错误物料注册键','src/main/java/com/sirin/hk3gtl/common/recipe/Hk3ElectronicRecipes.java',
         lambda s:s.replace('item("circuit_encapsulation_part",','item("missing_fixture_item",'),'registered_item_references')
    ]
    for title,target,mutate,code in scenarios:
        edited=[]
        def changed_read(path):
            text=original_read(path)
            if path.relative_to(audit.ROOT).as_posix()==target:
                replacement=mutate(text)
                if replacement==text: raise AssertionError('夹具未生效：'+title)
                edited.append(target);return replacement
            return text
        with patch.object(audit,'read',changed_read): result=audit.audit(audit.ROOT)
        detected=any(x['code']==code for x in result['errors'])
        if not edited or not detected:raise AssertionError('审计漏检：'+title)
        results.append({'scenario':title,'detected':code,'production_files_written':0})
    print(json.dumps({'passed':len(results),'results':results},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
