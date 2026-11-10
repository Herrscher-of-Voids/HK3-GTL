"""Compile and draw the production GLSL in a hidden Windows OpenGL context."""
import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
user=c.WinDLL('user32',use_last_error=True);gdi=c.WinDLL('gdi32');gl=c.WinDLL('opengl32')
user.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,w.HMENU,w.HINSTANCE,c.c_void_p]
user.CreateWindowExW.restype=w.HWND;user.GetDC.argtypes=[w.HWND];user.GetDC.restype=w.HDC
gl.wglCreateContext.argtypes=[w.HDC];gl.wglCreateContext.restype=c.c_void_p
gl.wglMakeCurrent.argtypes=[w.HDC,c.c_void_p];gl.wglGetProcAddress.argtypes=[c.c_char_p];gl.wglGetProcAddress.restype=c.c_void_p
gl.wglDeleteContext.argtypes=[c.c_void_p]
user.ReleaseDC.argtypes=[w.HWND,w.HDC];user.DestroyWindow.argtypes=[w.HWND]

class PixelFormat(c.Structure):
    _fields_=[('nSize',w.WORD),('nVersion',w.WORD),('dwFlags',w.DWORD),('iPixelType',c.c_ubyte),
        ('cColorBits',c.c_ubyte),('cRedBits',c.c_ubyte),('cRedShift',c.c_ubyte),('cGreenBits',c.c_ubyte),
        ('cGreenShift',c.c_ubyte),('cBlueBits',c.c_ubyte),('cBlueShift',c.c_ubyte),('cAlphaBits',c.c_ubyte),
        ('cAlphaShift',c.c_ubyte),('cAccumBits',c.c_ubyte),('cAccumRedBits',c.c_ubyte),('cAccumGreenBits',c.c_ubyte),
        ('cAccumBlueBits',c.c_ubyte),('cAccumAlphaBits',c.c_ubyte),('cDepthBits',c.c_ubyte),('cStencilBits',c.c_ubyte),
        ('cAuxBuffers',c.c_ubyte),('iLayerType',c.c_ubyte),('bReserved',c.c_ubyte),('dwLayerMask',w.DWORD),
        ('dwVisibleMask',w.DWORD),('dwDamageMask',w.DWORD)]

def api(name,restype,*args):
    ptr=gl.wglGetProcAddress(name.encode())
    if ptr and ptr not in (1,2,3,c.c_void_p(-1).value):return c.WINFUNCTYPE(restype,*args)(ptr)
    f=getattr(gl,name);f.restype=restype;f.argtypes=args;return f

window=user.CreateWindowExW(0,'STATIC','HK3GTL shader probe',0x80000000,0,0,32,32,None,None,None,None)
assert window
dc=user.GetDC(window);pfd=PixelFormat();pfd.nSize=c.sizeof(pfd);pfd.nVersion=1
pfd.dwFlags=0x04|0x20;pfd.iPixelType=0;pfd.cColorBits=32;pfd.cDepthBits=24
gdi.ChoosePixelFormat.argtypes=[w.HDC,c.POINTER(PixelFormat)];gdi.SetPixelFormat.argtypes=[w.HDC,c.c_int,c.POINTER(PixelFormat)]
fmt=gdi.ChoosePixelFormat(dc,c.byref(pfd));assert fmt and gdi.SetPixelFormat(dc,fmt,c.byref(pfd))
context=gl.wglCreateContext(dc);assert context and gl.wglMakeCurrent(dc,context)
try:
    getString=api('glGetString',c.c_char_p,c.c_uint)
    createShader=api('glCreateShader',c.c_uint,c.c_uint)
    shaderSource=api('glShaderSource',None,c.c_uint,c.c_int,c.POINTER(c.c_char_p),c.POINTER(c.c_int))
    compileShader=api('glCompileShader',None,c.c_uint)
    getShader=api('glGetShaderiv',None,c.c_uint,c.c_uint,c.POINTER(c.c_int))
    shaderLog=api('glGetShaderInfoLog',None,c.c_uint,c.c_int,c.POINTER(c.c_int),c.c_void_p)
    program=api('glCreateProgram',c.c_uint)()
    attach=api('glAttachShader',None,c.c_uint,c.c_uint)
    for suffix,kind in [('vsh',0x8b31),('fsh',0x8b30)]:
        source=(ROOT/f'src/main/resources/assets/hk3gtl/shaders/core/farview.{suffix}').read_bytes()
        shader=createShader(kind);text=c.c_char_p(source);shaderSource(shader,1,c.byref(text),None);compileShader(shader)
        good=c.c_int();getShader(shader,0x8b81,c.byref(good))
        log=c.create_string_buffer(8192);shaderLog(shader,len(log),None,log)
        assert good.value,log.value.decode();attach(program,shader)
    bindAttrib=api('glBindAttribLocation',None,c.c_uint,c.c_uint,c.c_char_p)
    bindAttrib(program,0,b'Position');bindAttrib(program,1,b'Color')
    api('glLinkProgram',None,c.c_uint)(program)
    good=c.c_int();api('glGetProgramiv',None,c.c_uint,c.c_uint,c.POINTER(c.c_int))(program,0x8b82,c.byref(good));assert good.value
    api('glUseProgram',None,c.c_uint)(program)
    uniform=api('glGetUniformLocation',c.c_int,c.c_uint,c.c_char_p)
    matrix=api('glUniformMatrix4fv',None,c.c_int,c.c_int,c.c_ubyte,c.POINTER(c.c_float))
    identity=(c.c_float*16)(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
    projection=(c.c_float*16)(1/32,0,0,0,0,1/32,0,0,0,0,-1,0,-1,-1,0,1)
    matrix(uniform(program,b'ModelViewMat'),1,0,identity);matrix(uniform(program,b'ProjMat'),1,0,projection)
    u3=api('glUniform3f',None,c.c_int,c.c_float,c.c_float,c.c_float)
    u3(uniform(program,b'TileOrigin'),0,0,0);u3(uniform(program,b'CameraOrigin'),0,0,0)
    api('glUniform2f',None,c.c_int,c.c_float,c.c_float)(uniform(program,b'ChunkOrigin'),0,0)
    u1=api('glUniform1f',None,c.c_int,c.c_float);u1(uniform(program,b'FarLimit'),2048)
    api('glUniform1i',None,c.c_int,c.c_int)(uniform(program,b'Sampler0'),0)
    vao=c.c_uint();api('glGenVertexArrays',None,c.c_int,c.POINTER(c.c_uint))(1,c.byref(vao));api('glBindVertexArray',None,c.c_uint)(vao)
    buffer=c.c_uint();api('glGenBuffers',None,c.c_int,c.POINTER(c.c_uint))(1,c.byref(buffer))
    api('glBindBuffer',None,c.c_uint,c.c_uint)(0x8892,buffer)
    raw=b''.join(struct.pack('7f',x,y,0,0.2,0.6,1,1) for x,y in [(0,0),(64,0),(64,64),(0,64)])
    api('glBufferData',None,c.c_uint,c.c_ssize_t,c.c_void_p,c.c_uint)(0x8892,len(raw),c.c_char_p(raw),0x88e4)
    attrib=api('glVertexAttribPointer',None,c.c_uint,c.c_int,c.c_uint,c.c_ubyte,c.c_int,c.c_void_p)
    for n,count,offset in [(0,3,0),(1,4,12)]:
        attrib(n,count,0x1406,0,28,c.c_void_p(offset));api('glEnableVertexAttribArray',None,c.c_uint)(n)
    texture=c.c_uint();api('glGenTextures',None,c.c_int,c.POINTER(c.c_uint))(1,c.byref(texture));api('glBindTexture',None,c.c_uint,c.c_uint)(0x0de1,texture)
    parameter=api('glTexParameteri',None,c.c_uint,c.c_uint,c.c_int)
    for param in [0x2800,0x2801]:parameter(0x0de1,param,0x2600)
    image=api('glTexImage2D',None,c.c_uint,c.c_int,c.c_int,c.c_int,c.c_int,c.c_int,c.c_uint,c.c_uint,c.c_void_p)
    viewport=api('glViewport',None,c.c_int,c.c_int,c.c_int,c.c_int);viewport(0,0,16,16)
    clearColor=api('glClearColor',None,c.c_float,c.c_float,c.c_float,c.c_float);clearColor(0,0,0,1)
    draw=api('glDrawArrays',None,c.c_uint,c.c_int,c.c_int);clear=api('glClear',None,c.c_uint)
    read=api('glReadPixels',None,c.c_int,c.c_int,c.c_int,c.c_int,c.c_uint,c.c_uint,c.c_void_p)
    results=[]
    for label,loaded,limit,visible in [('unloaded_far_surface',False,2048,True),('loaded_chunk_mask',True,2048,False),('distance_limit',False,1,False)]:
        pixels=(b'\xff\xff\xff\xff' if loaded else b'\x00\x00\x00\xff')*(128*128)
        image(0x0de1,0,0x8058,128,128,0,0x1908,0x1401,c.c_char_p(pixels));u1(uniform(program,b'FarLimit'),limit)
        clear(0x4000);draw(0x0006,0,4);pixel=(c.c_ubyte*4)();read(8,8,1,1,0x1908,0x1401,pixel)
        assert (pixel[2]>200)==visible,(label,list(pixel))
        results.append({'case':label,'rgba':list(pixel),'passed':True})
    assert api('glGetError',c.c_uint)()==0
    result={'OpenGL':getString(0x1f02).decode(),'renderer':getString(0x1f01).decode(),
            'production_shaders_compiled_and_linked':True,'checks':results,'hidden_context':True,'game_client_fps_measured':False}
    path=ROOT/'logs/native-distance-package-r219-20261108/shader-probe.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
finally:
    gl.wglMakeCurrent(None,None);gl.wglDeleteContext(context);user.ReleaseDC(window,dc);user.DestroyWindow(window)
