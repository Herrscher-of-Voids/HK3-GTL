import math
from types import SimpleNamespace

import numpy as np
from scipy.spatial import ConvexHull


SHELL, ARMOR, GLASS, IMPELLER, COIL, CORE, FRAME = range(1, 8)


class Part:
    def __init__(self, name, label, **metadata):
        self.name, self.label, self.metadata = name, label, metadata
        self.chunks, self.values = [], []

    def points(self, points, state):
        points = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(points)
        self.values.append(np.full(len(points), state, np.uint8))

    def box(self, low, high, state):
        low, high = np.minimum(low, high).astype(int), np.maximum(low, high).astype(int)
        z, x = np.mgrid[low[2]:high[2]+1, low[0]:high[0]+1]
        for y in range(low[1], high[1]+1):
            self.points(np.c_[x.ravel(), np.full(x.size, y), z.ravel()], state)

    def beam(self, start, end, radius, state, inner=0):
        a, b = np.asarray(start, float), np.asarray(end, float)
        v = b-a
        lo, hi = np.floor(np.minimum(a,b)-radius).astype(int), np.ceil(np.maximum(a,b)+radius).astype(int)
        z,x = np.mgrid[lo[2]:hi[2]+1, lo[0]:hi[0]+1]
        for y in range(lo[1],hi[1]+1):
            q = np.c_[x.ravel(),np.full(x.size,y),z.ravel()]
            t = np.clip((q-a)@v/(v@v),0,1)
            distance = np.linalg.norm(q-a-t[:,None]*v,axis=1)
            self.points(q[(distance<=radius)&(distance>=inner)],state)

    def sphere(self, center, radius, state, inner=0):
        c = np.asarray(center,float)
        lo,hi = np.floor(c-radius).astype(int),np.ceil(c+radius).astype(int)
        z,x = np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
        for y in range(lo[1],hi[1]+1):
            q=np.c_[x.ravel(),np.full(x.size,y),z.ravel()]
            r=np.linalg.norm(q-c,axis=1)
            self.points(q[(r<=radius)&(r>=inner)],state)

    def ring(self, center, radius, thickness, state, normal=(0,1,0), depth=3):
        c,n=np.asarray(center,float),np.asarray(normal,float)
        n=n/np.linalg.norm(n)
        extent=np.sqrt(1-n*n)*radius+abs(n)*depth/2
        lo,hi=np.floor(c-extent).astype(int),np.ceil(c+extent).astype(int)
        z,x=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
        for y in range(lo[1],hi[1]+1):
            q=np.c_[x.ravel(),np.full(x.size,y),z.ravel()]
            d=q-c
            axial=d@n
            r=np.linalg.norm(d-axial[:,None]*n,axis=1)
            self.points(q[(abs(axial)<=depth/2)&(r<=radius)&(r>=radius-thickness)],state)

    def hull(self, vertices, state):
        v=np.asarray(vertices,float)
        equations=ConvexHull(v).equations
        lo,hi=np.floor(v.min(0)).astype(int),np.ceil(v.max(0)).astype(int)
        z,x=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
        for y in range(lo[1],hi[1]+1):
            q=np.c_[x.ravel(),np.full(x.size,y),z.ravel()]
            self.points(q[np.all(q@equations[:,:3].T+equations[:,3]<=1e-5,axis=1)],state)

    def finish(self):
        points,values=np.concatenate(self.chunks),np.concatenate(self.values)
        low=points.min(0)
        size=points.max(0)-low+1
        local=points-low
        keys=(local[:,1]*size[2]+local[:,2])*size[0]+local[:,0]
        _,index=np.unique(keys[::-1],return_index=True)
        index=len(keys)-index-1
        return SimpleNamespace(name=self.name,label=self.label,p=points[index],states=values[index],metadata=self.metadata)


def trace(part, points, radius, state, inner=0):
    for a,b in zip(points[:-1],points[1:]):
        part.beam(a,b,radius,state,inner)


def bezier(points, t):
    a,b,c,d=np.asarray(points,float)
    return (1-t)**3*a+3*t*(1-t)**2*b+3*t*t*(1-t)*c+t**3*d
