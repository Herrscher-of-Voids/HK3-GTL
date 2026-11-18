# -*- coding: utf-8 -*-
"""在扩展坐标域重放旧生成器，保留越界几何；不修改历史源文件。"""
import ast
import hashlib
import importlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/wonder-clipping-audit-20261108'
PAD=64


class LogicalGrid:
    """蓝图坐标包含负数；所有显式写入必须在扩展域内，禁止截断。"""
    def __init__(self,shape,pad):
        self.pad=pad
        self.array=np.zeros(tuple(n+2*pad for n in shape),np.uint8)

    def key(self,key):
        if isinstance(key,np.ndarray) and key.dtype==bool:return key
        key=key if isinstance(key,tuple) else (key,)
        result=[]
        for axis,value in enumerate(key):
            if isinstance(value,slice):
                start=None if value.start is None else value.start+self.pad
                stop=None if value.stop is None else value.stop+self.pad
                assert start is None or 0<=start<=self.array.shape[axis],key
                assert stop is None or 0<=stop<=self.array.shape[axis],key
                result.append(slice(start,stop,value.step))
            else:
                translated=np.asarray(value)+self.pad
                assert np.all(translated>=0) and np.all(translated<self.array.shape[axis]),key
                result.append(translated if translated.ndim else int(translated))
        return tuple(result)

    def __getitem__(self,key):return self.array[self.key(key)]
    def __setitem__(self,key,value):self.array[self.key(key)]=value
    def __ne__(self,value):return self.array!=value


class ExpandBuild(ast.NodeTransformer):
    def __init__(self):self.inside=False;self.explicit_drops=0;self.box_clamps=0

    def visit_FunctionDef(self,node):
        if node.name=='build':
            self.inside=True;node=self.generic_visit(node);self.inside=False
            return node
        return self.generic_visit(node) if self.inside else node

    def visit_Assert(self,node):
        return None if self.inside else node

    def visit_Assign(self,node):
        if self.inside and any(isinstance(t,ast.Name) and t.id=='c' for t in node.targets):
            node.value=ast.parse('LogicalGrid((H,D,W),PAD)',mode='eval').body
            return node
        if self.inside and any(isinstance(t,ast.Name) and t.id=='p' for t in node.targets):
            if ast.unparse(node.value)=='p[valid]':
                self.explicit_drops+=1
                return None
            if ast.unparse(node.value).startswith('np.minimum(np.maximum(p, extent + 1)'):
                self.explicit_drops+=1
                return None
        if self.inside and any(isinstance(t,ast.Name) and t.id=='taper' for t in node.targets):
            if 'W - 1 - p[0]' in ast.unparse(node.value):
                node.value=ast.parse('min(1,(1-t)*20+.01)',mode='eval').body
        return self.generic_visit(node)

    def visit_Subscript(self,node):
        node=self.generic_visit(node)
        if not self.inside:return node
        text=ast.unparse(node)
        if text in ('np.ogrid[:D, :W]','np.ogrid[:H, :D]'):
            a,b=('D','W') if ':W' in text else ('H','D')
            return ast.parse(f'np.ogrid[-PAD:{a}+PAD,-PAD:{b}+PAD]',mode='eval').body
        if isinstance(node.value,ast.Name) and node.value.id=='c' and isinstance(node.slice,ast.Tuple):
            for i,e in enumerate(node.slice.elts):
                if i in (1,2) and isinstance(e,ast.Name) and e.id in ('zs','xs'):
                    node.slice.elts[i]=ast.BinOp(e,ast.Sub(),ast.Name('PAD',ast.Load()))
        return node

    def visit_Call(self,node):
        node=self.generic_visit(node)
        if self.inside and ast.unparse(node.func) in ('np.broadcast_to','np.zeros'):
            for i,arg in enumerate(node.args):
                if ast.unparse(arg) in ('(D, W)','(H, D)'):
                    node.args[i]=ast.Tuple([ast.BinOp(e,ast.Add(),ast.Constant(2*PAD)) for e in arg.elts],ast.Load())
        if self.inside and isinstance(node.func,ast.Name) and node.func.id=='box':
            for i,arg in enumerate(node.args[:2]):
                if isinstance(arg,ast.Call) and ast.unparse(arg.func) in ('np.minimum','np.maximum'):
                    node.args[i]=arg.args[0];self.box_clamps+=1
        return node


def expanded(module_name):
    module=importlib.import_module(module_name)
    source=Path(module.__file__).read_text(encoding='utf8')
    tree=ast.parse(source);patch=ExpandBuild();tree=ast.fix_missing_locations(patch.visit(tree))
    env=dict(module.__dict__,__name__='expanded_geometry',LogicalGrid=LogicalGrid,PAD=PAD)
    exec(compile(tree,str(module.__file__)+' (扩展域核验)','exec'),env)
    grid,data=env['build']();cube=grid.array
    occupied=cube!=0;lo=[];hi=[]
    for axis in range(3):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)))
        lo.append(int(p[0]));hi.append(int(p[-1])+1)
    assert all(a>0 and b<cube.shape[i] for i,(a,b) in enumerate(zip(lo,hi))),'扩展域仍不足，禁止生成截断候选'
    crop=cube[tuple(slice(a,b) for a,b in zip(lo,hi))].copy()
    h,d,w=module.H,module.D,module.W
    nominal=cube[PAD:PAD+h,PAD:PAD+d,PAD:PAD+w].copy()
    original,_=module.build()
    inside_difference=int(np.count_nonzero(nominal!=original))
    outside=int(np.count_nonzero(cube)-np.count_nonzero(nominal))
    bounds=dict(min=[lo[2]-PAD,lo[0]-PAD,lo[1]-PAD],max=[hi[2]-PAD-1,hi[0]-PAD-1,hi[1]-PAD-1])
    result=dict(source=str(Path(module.__file__).relative_to(ROOT)),source_sha256=hashlib.sha256(source.encode('utf8')).hexdigest(),
        nominal_xyz=[w,h,d],expanded_actual_bounds_xyz=bounds,actual_xyz=[crop.shape[2],crop.shape[0],crop.shape[1]],
        recovered_outside_blocks=outside,inside_changed_blocks=inside_difference,explicit_point_filter_sites=patch.explicit_drops,
        explicit_box_clamp_arguments=patch.box_clamps,padding_domain_complete=True,
        interpretation='外部方块数是按同一旧公式扩展重放后的唯一体素，不代表原作者完整图纸；显式限定的循环终点仍按旧源代码保留。')
    return crop,data,result


def main():
    LOG.mkdir(parents=True,exist_ok=True)
    results=[]
    names=['w02_matrix_geometry_v2_20261107','w03_crown_geometry_v2_20261107','w03_celestial_geometry_v3_20261107','w03_celestial_geometry_v4_20261107','w03_crown_geometry_v5_20261108']
    for name in names:
        cube,data,result=expanded(name);results.append(result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
        del cube
        (LOG/'boundary-replay.json').write_text(json.dumps(dict(passed=len(results)==len(names),results=results),ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()
