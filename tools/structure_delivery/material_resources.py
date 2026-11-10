"""修订71：解析指定实例的跨模组父模型、KubeJS 动态材质与纹理引用。

只证明静态资源与形体；不把模型文件当注册表或生存配方证明。
"""
# 变更记录 #1 2026-09-25 04:49:51（内测5修订72）
# 删除：按名称猜透明及无元数据截帧。新增：PNG透明度、动画元数据与显式透明声明。
# 修改：仅translucent渲染声明视为半透明；用途：solid/cutout不因调用renderType被误判。
from pathlib import Path
import base64
import io
import json
import re
import zipfile
from PIL import Image

INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft'
CLIENT = Path.home() / 'AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
FACES = ('east', 'west', 'up', 'down', 'south', 'north')


class Resources:
    """跨命名空间读取资源；不为未知方块合成默认立方体。"""
    def __init__(self, instance=INSTANCE, client=CLIENT, project_resources=None):
        self.instance = Path(instance)
        self.project_resources = Path(project_resources) if project_resources else None
        self.archives = []
        self.index = {}
        self.sources = {}
        self.cache = {}
        self.declarations = {}
        self.unresolved_scripts = []
        for path in [Path(client), *sorted((self.instance / 'mods').glob('*.jar'))]:
            if not path.is_file():
                continue
            archive = zipfile.ZipFile(path)
            self.archives.append((path, archive))
            for name in archive.namelist():
                if name.startswith('assets/'):
                    self.index[name] = (path, archive)
        self._scripts()

    def close(self):
        for _, archive in self.archives:
            archive.close()

    def read(self, rel):
        if self.project_resources and rel.startswith('assets/hk3gtl/'):
            project = self.project_resources / rel
            if project.is_file():
                self.sources[rel] = str(project)
                return project.read_bytes()
        local = self.instance / 'kubejs' / rel
        if local.is_file():
            self.sources[rel] = str(local)
            return local.read_bytes()
        if rel in self.index:
            path, archive = self.index[rel]
            self.sources[rel] = str(path) + '!/' + rel
            return archive.read(rel)
        raise FileNotFoundError(rel)

    def _scripts(self):
        for path in sorted((self.instance / 'kubejs/startup_scripts').rglob('*.js')):
            text = path.read_text(encoding='utf-8-sig')
            if not re.search(r'StartupEvents\.registry\([\"\']block[\"\']', text):
                continue
            # 明确字符串注册及链式纹理；动态表达式另列，不执行整合包脚本。
            matches = list(re.finditer(r'event\.create\(\s*([\"\'])([^\"\']+)\1\s*(?:,\s*([\"\'])([^\"\']+)\3\s*)?\)', text))
            for match in matches:
                end = text.find('event.create(', match.end())
                body = text[match.end():end if end >= 0 else len(text)]
                key = match[2] if ':' in match[2] else 'kubejs:' + match[2]
                self.declarations[key] = {'kind': match[4] or 'basic', 'body': body, 'source': str(path)}
            # 当前实例的 coils 数组：逐项展开，不能按名称猜 ID。
            array = re.search(r'const\s+coils\s*=\s*(\[[\s\S]*?\])\s*coils\.forEach', text)
            if array and 'event.create(coil[0] + "_coil_block", "gtceu:coil")' in text:
                for row in json.loads(array[1]):
                    key = row[0] + '_coil_block'
                    self.declarations['kubejs:' + key] = {'kind': 'gtceu:coil',
                        'body': '.texture("kubejs:block/' + key + '")', 'source': str(path)}
            for line in text.splitlines():
                if 'event.create(' in line and not re.search(r'event\.create\(\s*[\"\']', line) and 'coil[0]' not in line:
                    self.unresolved_scripts.append({'source': str(path), 'expression': line.strip()})

    def model(self, name, trail=()):
        if name in trail or len(trail) > 32:
            raise ValueError('模型父链循环或过深：' + name)
        if name in self.cache:
            return self.cache[name]
        ns, key = name.split(':', 1) if ':' in name else ('minecraft', name)
        raw = json.loads(self.read(f'assets/{ns}/models/{key}.json'))
        parent = self.model(raw['parent'], (*trail, name)) if raw.get('parent') else {}
        merged = {**parent, **raw, 'textures': {**parent.get('textures', {}), **raw.get('textures', {})}}
        self.cache[name] = merged
        return merged

    def _script_model(self, block):
        decl = self.declarations.get(block)
        if not decl or decl['kind'] not in ('basic', 'gtceu:coil'):
            raise ValueError('无可确认的完整方块声明：' + block)
        body = decl['body']
        if re.search(r'\.(box|model|noCollision|noOcclusion|defaultState|property)\s*\(', body):
            raise ValueError('自定义形体或状态必须单独核验：' + block)
        textures = {face: block.replace(':', ':block/') for face in FACES}
        for match in re.finditer(r'\.(textureAll|texture)\(\s*[\"\']([^\"\']+)[\"\']\s*(?:,\s*[\"\']([^\"\']+)[\"\']\s*)?\)', body):
            if match[3]:
                if match[2] not in FACES:
                    raise ValueError('未知纹理面：' + match[2])
                textures[match[2]] = match[3]
            else:
                textures = {face: match[2] for face in FACES}
        return {'textures': textures, 'elements': [{'from': [0, 0, 0], 'to': [16, 16, 16],
            'faces': {face: {'texture': '#' + face} for face in FACES}}]}, decl['source']

    def material(self, state):
        block = state.split('[')[0]
        ns, key = block.split(':', 1)
        properties = dict(re.findall(r'(\w+)=([^,\]]+)', state))
        try:
            bs = json.loads(self.read(f'assets/{ns}/blockstates/{key}.json'))
        except FileNotFoundError:
            if ns != 'kubejs':
                raise
            model, source = self._script_model(block)
        else:
            if 'multipart' in bs:
                raise ValueError('多部件模型需单独核验：' + state)
            matches = [v for cond, v in bs.get('variants', {}).items()
                if all(properties.get(k) in val.split('|') for k, val in re.findall(r'(\w+)=([^,]+)', cond))]
            if len(matches) != 1:
                raise ValueError('方块状态不唯一，必须明确状态：' + state)
            variant = matches[0]
            if isinstance(variant, list):
                raise ValueError('随机变体需逐一核验：' + state)
            if variant.get('x', 0) or variant.get('y', 0):
                raise ValueError('旋转模型需按状态变换纹理：' + state)
            source = variant['model']
            model = self.model(source)
        elements = model.get('elements', [])
        if (len(elements) != 1 or elements[0].get('from') != [0, 0, 0]
                or elements[0].get('to') != [16, 16, 16] or elements[0].get('rotation')):
            raise ValueError('不是已确认的完整立方体：' + state)
        faces = {}
        animations = {}
        texture_alpha = False
        for face in FACES:
            value = elements[0]['faces'][face]['texture']
            seen = set()
            while value.startswith('#'):
                if value in seen:
                    raise ValueError('纹理引用循环：' + state)
                seen.add(value)
                value = model['textures'][value[1:]]
            tns, path = value.split(':', 1) if ':' in value else ('minecraft', value)
            texture_path = f'assets/{tns}/textures/{path}.png'
            picture = Image.open(io.BytesIO(self.read(texture_path))).convert('RGBA')
            texture_alpha = texture_alpha or picture.getchannel('A').getextrema()[0] < 255
            try:
                animation = json.loads(self.read(texture_path + '.mcmeta')).get('animation')
            except FileNotFoundError:
                animation = None
            if animation is not None:
                width = animation.get('width', picture.width if 'height' in animation else min(picture.size))
                height = animation.get('height', picture.height if 'width' in animation else min(picture.size))
                if width <= 0 or height <= 0 or picture.width % width or picture.height % height:
                    raise ValueError('动画帧尺寸无效：' + texture_path)
                columns = picture.width // width
                frames = animation.get('frames', list(range(columns * (picture.height // height))))
                if not frames:
                    raise ValueError('动画没有帧：' + texture_path)
                first = frames[0].get('index') if isinstance(frames[0], dict) else frames[0]
                if not isinstance(first, int) or not 0 <= first < columns * (picture.height // height):
                    raise ValueError('动画帧索引无效：' + texture_path)
                x, y = first % columns * width, first // columns * height
                animations[face] = {'texture': value, 'metadata': animation, 'preview_frame': first}
                picture = picture.crop((x, y, x + width, y + height))
            stream = io.BytesIO()
            picture.save(stream, format='PNG')
            faces[face] = 'data:image/png;base64,' + base64.b64encode(stream.getvalue()).decode('ascii')
        body = self.declarations.get(block, {}).get('body', '')
        translucent = bool(re.search(r'\.defaultTranslucent\s*\(', body)
                           or re.search(r'''\.renderType\s*\(\s*["']translucent["']''', body))
        return {'state': state, 'faces': faces, 'transparent': texture_alpha or translucent,
            'texture_alpha': texture_alpha, 'animations': animations,
            'model': source, 'complete_cube': True,
            'tinted': any('tintindex' in v for v in elements[0]['faces'].values())}
