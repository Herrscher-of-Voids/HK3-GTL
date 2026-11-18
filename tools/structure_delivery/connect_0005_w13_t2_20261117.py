from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl'
LOG = ROOT / 'logs/0005-w13-t2-production-20261117'
NAMES = ['common/machine/wonder/Hk3WonderCatalog.java',
    'common/multiblock/pattern/Hk3SparsePreviewData.java',
    'client/preview/Hk3SparsePreviewWidget.java', 'client/preview/Hk3W01PreviewWidget.java',
    'client/farview/Hk3FarViewRenderer.java', 'client/farview/Hk3WorldFarBuild.java',
    'mixin/client/Hk3W03BlockRenderMixin.java', 'mixin/client/Hk3W03EmbeddiumRenderMixin.java']


def replace(path, old, new):
    text = path.read_text('utf8')
    if old not in text:
        raise ValueError(str(path) + ': 缺少目标文本')
    path.write_text(text.replace(old, new), 'utf8')


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    backup = LOG / 'before-client-routing.zip'
    with ZipFile(backup, 'x', ZIP_DEFLATED, compresslevel=6) as archive:
        for name in NAMES:
            archive.write(JAVA / name, name)
    with ZipFile(backup) as archive:
        for name in NAMES:
            if archive.read(name) != (JAVA / name).read_bytes():
                raise ValueError('压缩备份核对失败：' + name)

    replace(JAVA / NAMES[0], '|| role.equals("W12");', '|| role.equals("W12") || role.equals("W13");')
    replace(JAVA / NAMES[1], '        sources.put("hk3gtl:w12_global_energy_constraint_wall",new Source("w12_candidate",Direction.NORTH));',
        '        sources.put("hk3gtl:w12_global_energy_constraint_wall",new Source("w12_candidate",Direction.NORTH));\n'
        '        sources.put("hk3gtl:w13_self_computing_research_mother",new Source("w13_candidate",Direction.SOUTH));')

    path = JAVA / NAMES[2]
    replace(path, 'if(definition.getId().getPath().equals("w11_distributed_industrial_command")){',
        'if(definition.getId().getPath().equals("w11_distributed_industrial_command")\n'
        '                ||definition.getId().getPath().equals("w13_self_computing_research_mother")){')
    replace(path, '            var meta=com.sirin.hk3gtl.client.wonder.Hk3W11FxModel.loadMetadata();\n'
        '            int[] size=meta.sizeXYZ(),control=meta.controller_blueprint(),offset=meta.blueprint_to_export_offset_xyz();',
        '            boolean w13=definition.getId().getPath().equals("w13_self_computing_research_mother");\n'
        '            var w11meta=w13?null:com.sirin.hk3gtl.client.wonder.Hk3W11FxModel.loadMetadata();\n'
        '            var w13meta=w13?com.sirin.hk3gtl.client.wonder.Hk3W13FxModel.loadMetadata():null;\n'
        '            int[] size=w13?w13meta.sizeXYZ():w11meta.sizeXYZ(),\n'
        '                    control=w13?w13meta.controller_blueprint():w11meta.controller_blueprint(),\n'
        '                    offset=w13?w13meta.blueprint_to_export_offset_xyz():w11meta.blueprint_to_export_offset_xyz();\n'
        '            String[] palette=w13?w13meta.palette():w11meta.palette();')
    replace(path, 'java.util.List.of(meta.palette())', 'java.util.List.of(palette)')
    replace(path, 'meta.palette().length-1', 'palette.length-1')

    path = JAVA / NAMES[3]
    replace(path, 'import com.sirin.hk3gtl.client.wonder.Hk3W11FxModel;',
        'import com.sirin.hk3gtl.client.wonder.Hk3W11FxModel;\n'
        'import com.sirin.hk3gtl.client.wonder.Hk3W13FxRenderer;\n'
        'import com.sirin.hk3gtl.client.wonder.Hk3W13FxModel;')
    replace(path, 'isW11()', 'hasSceneModel()')
    replace(path, 'private boolean hasSceneModel(){return definition.getId().getPath().equals("w11_distributed_industrial_command");}',
        'private boolean isW13(){return definition.getId().getPath().equals("w13_self_computing_research_mother");}\n'
        '    private boolean hasSceneModel(){return isW13()||definition.getId().getPath().equals("w11_distributed_industrial_command");}\n'
        '    private long[] sceneMaterialCounts(){return isW13()?Hk3W13FxModel.loadMetadata().material_counts():Hk3W11FxModel.loadMetadata().material_counts();}')
    replace(path, 'java.util.Arrays.stream(Hk3W11FxModel.loadMetadata().material_counts())', 'java.util.Arrays.stream(sceneMaterialCounts())')
    replace(path, 'Math.toIntExact(Hk3W11FxModel.loadMetadata().material_counts()[i])', 'Math.toIntExact(sceneMaterialCounts()[i])')
    replace(path, 'scene!=null&&Hk3W11FxRenderer.ready()', 'scene!=null&&(isW13()?Hk3W13FxRenderer.ready():Hk3W11FxRenderer.ready())')
    replace(path, 'return Hk3W11FxRenderer.vertexBytes();', 'return isW13()?Hk3W13FxRenderer.vertexBytes():Hk3W11FxRenderer.vertexBytes();')
    replace(path, '"w12_global_energy_constraint_wall", "w11_distributed_industrial_command",',
        '"w12_global_energy_constraint_wall", "w11_distributed_industrial_command", "w13_self_computing_research_mother",')
    replace(path, 'if(Hk3W11FxRenderer.preparePreview()&&scene==null){',
        'if((isW13()?Hk3W13FxRenderer.preparePreview():Hk3W11FxRenderer.preparePreview())&&scene==null){')
    replace(path, '                    Hk3W11FxRenderer.drawPreview((System.nanoTime()-animationStart)/1e9,effectsEnabled,layer);return;',
        '                    double seconds=(System.nanoTime()-animationStart)/1e9;\n'
        '                    if(isW13())Hk3W13FxRenderer.drawPreview(seconds,effectsEnabled,layer);\n'
        '                    else Hk3W11FxRenderer.drawPreview(seconds,effectsEnabled,layer);\n'
        '                    return;')

    for name in NAMES[4:6]:
        path = JAVA / name
        replace(path, 'import com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes;',
            'import com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes;\n'
            'import com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes;')
        text = path.read_text('utf8')
        for expression in ['world,state', 'pos,block', 'new BlockPos(x,y,z),Block.stateById(state-1)']:
            old = 'Hk3W11FieldScenes.hidden(' + expression + ')'
            text = text.replace(old, old + '||Hk3W13FieldScenes.hidden(' + expression + ')')
        text = text.replace('Hk3W11FieldScenes.active()', 'Hk3W11FieldScenes.active()||Hk3W13FieldScenes.active()')
        text = text.replace('signature=signature*31+Hk3W11FieldScenes.signature();',
            'signature=signature*31+Hk3W11FieldScenes.signature();\n        signature=signature*31+Hk3W13FieldScenes.signature();')
        text = text.replace('Hk3W11FieldScenes.addColumns(selected);',
            'Hk3W11FieldScenes.addColumns(selected);Hk3W13FieldScenes.addColumns(selected);')
        path.write_text(text, 'utf8')

    for name, expression in [(NAMES[6], 'pos,state'), (NAMES[7], 'block.hk3gtl$pos(),block.hk3gtl$state()')]:
        target = 'com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes.hidden(' + expression + ')'
        replace(JAVA / name, target,
            target + '\n                ||com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes.hidden(' + expression + ')')
    print('W13正式身份、完整预览、近景与远景遮罩路由已接入。')


if __name__ == '__main__':
    main()
