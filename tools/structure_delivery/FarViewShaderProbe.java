import java.nio.*;
import java.nio.file.*;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.*;
import org.lwjgl.system.MemoryUtil;

/** 隐藏OpenGL窗口中的生产着色器回归；不读取、操作或替代Minecraft实机验收。 */
public final class FarViewShaderProbe {
    private static int shader(int type,String source) {
        int shader=GL20.glCreateShader(type);GL20.glShaderSource(shader,source);GL20.glCompileShader(shader);
        if(GL20.glGetShaderi(shader,GL20.GL_COMPILE_STATUS)==0)throw new AssertionError(GL20.glGetShaderInfoLog(shader));
        return shader;
    }
    private static int program(String vertex,String fragment) {
        int v=shader(GL20.GL_VERTEX_SHADER,vertex),f=shader(GL20.GL_FRAGMENT_SHADER,fragment),p=GL20.glCreateProgram();
        GL20.glAttachShader(p,v);GL20.glAttachShader(p,f);
        GL20.glBindAttribLocation(p,0,"Position");GL20.glBindAttribLocation(p,1,"Color");GL20.glBindAttribLocation(p,2,"UV0");
        GL20.glLinkProgram(p);GL20.glDeleteShader(v);GL20.glDeleteShader(f);
        if(GL20.glGetProgrami(p,GL20.GL_LINK_STATUS)==0)throw new AssertionError(GL20.glGetProgramInfoLog(p));
        return p;
    }
    private static void matrices(int p) {
        float[] identity={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
        GL20.glUniformMatrix4fv(GL20.glGetUniformLocation(p,"ModelViewMat"),false,identity);
        GL20.glUniformMatrix4fv(GL20.glGetUniformLocation(p,"ProjMat"),false,identity);
    }
    private static int pixel() {
        ByteBuffer data=MemoryUtil.memAlloc(4);
        try{GL11.glReadPixels(32,32,1,1,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,data);return (data.get(0)&255)<<16|(data.get(1)&255)<<8|data.get(2)&255;}
        finally{MemoryUtil.memFree(data);}
    }
    private static void clear(){GL11.glClearColor(.1f,.1f,.1f,1);GL11.glClear(GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT);}
    private static void require(boolean ok,String text){if(!ok)throw new AssertionError(text);}
    public static void main(String[] args) throws Exception {
        require(GLFW.glfwInit(),"GLFW初始化失败");long window=0;
        try{
            GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE,GLFW.GLFW_FALSE);
            GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR,3);GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR,2);
            GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE,GLFW.GLFW_OPENGL_CORE_PROFILE);
            window=GLFW.glfwCreateWindow(64,64,"HK3GTL离屏着色器回归",0,0);require(window!=0,"无法创建隐藏OpenGL上下文");
            GLFW.glfwMakeContextCurrent(window);GL.createCapabilities();
            String vertex=Files.readString(Path.of("src/main/resources/assets/hk3gtl/shaders/core/farview.vsh"));
            int far=program(vertex,Files.readString(Path.of("src/main/resources/assets/hk3gtl/shaders/core/farview.fsh")));
            int near=program(vertex,"#version 150\nout vec4 fragColor;void main(){fragColor=vec4(0,1,0,1);}");
            int vao=GL30.glGenVertexArrays();GL30.glBindVertexArray(vao);
            int vbo=GL15.glGenBuffers();GL15.glBindBuffer(GL15.GL_ARRAY_BUFFER,vbo);
            ByteBuffer vertices=MemoryUtil.memAlloc(6*24);
            try{
                for(float[] point:new float[][]{{-1,-1,0,0},{1,-1,16,0},{1,1,16,16},{-1,-1,0,0},{1,1,16,16},{-1,1,0,16}})
                    vertices.putFloat(point[0]).putFloat(point[1]).putFloat(0).put((byte)0).put((byte)0).put((byte)255).put((byte)255).putFloat(point[2]).putFloat(point[3]);
                vertices.flip();GL15.glBufferData(GL15.GL_ARRAY_BUFFER,vertices,GL15.GL_STATIC_DRAW);
            }finally{MemoryUtil.memFree(vertices);}
            GL20.glVertexAttribPointer(0,3,GL11.GL_FLOAT,false,24,0);GL20.glEnableVertexAttribArray(0);
            GL20.glVertexAttribPointer(1,4,GL11.GL_UNSIGNED_BYTE,true,24,12);GL20.glEnableVertexAttribArray(1);
            GL20.glVertexAttribPointer(2,2,GL11.GL_FLOAT,false,24,16);GL20.glEnableVertexAttribArray(2);
            GL13.glActiveTexture(GL13.GL_TEXTURE0);int atlas=GL11.glGenTextures();GL11.glBindTexture(GL11.GL_TEXTURE_2D,atlas);
            ByteBuffer image=MemoryUtil.memCalloc(1024*1024*4);
            try{
                for(int y=0;y<32;y++)for(int x=0;x<64;x++){int at=(y*1024+x)*4;image.put(at,(byte)(x<32?255:0));image.put(at+2,(byte)(x>=32?255:0));image.put(at+3,(byte)255);}
                GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,1024,1024,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,image);
            }finally{MemoryUtil.memFree(image);}
            GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL12.GL_TEXTURE_MAX_LEVEL,5);GL30.glGenerateMipmap(GL11.GL_TEXTURE_2D);
            GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MIN_FILTER,GL11.GL_LINEAR_MIPMAP_LINEAR);
            GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MAG_FILTER,GL11.GL_LINEAR);
            GL13.glActiveTexture(GL13.GL_TEXTURE1);int mask=GL11.glGenTextures();GL11.glBindTexture(GL11.GL_TEXTURE_2D,mask);
            ByteBuffer pixels=MemoryUtil.memCalloc(128*128*4);
            try{
                GL11.glTexImage2D(GL11.GL_TEXTURE_2D,0,GL11.GL_RGBA8,128,128,0,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,pixels);
                GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MIN_FILTER,GL11.GL_NEAREST);GL11.glTexParameteri(GL11.GL_TEXTURE_2D,GL11.GL_TEXTURE_MAG_FILTER,GL11.GL_NEAREST);
                GL20.glUseProgram(far);matrices(far);
                GL20.glUniform1i(GL20.glGetUniformLocation(far,"Sampler0"),0);GL20.glUniform1i(GL20.glGetUniformLocation(far,"Sampler1"),1);
                GL20.glUniform2f(GL20.glGetUniformLocation(far,"ChunkOrigin"),0,0);
                GL20.glUniform3f(GL20.glGetUniformLocation(far,"TileOrigin"),32,0,32);
                GL20.glUniform3f(GL20.glGetUniformLocation(far,"CameraOrigin"),32,0,34);
                GL20.glUniform1f(GL20.glGetUniformLocation(far,"NearLimit"),10);GL20.glUniform1f(GL20.glGetUniformLocation(far,"FarLimit"),2048);
                GL11.glViewport(0,0,64,64);GL11.glEnable(GL11.GL_DEPTH_TEST);GL11.glDepthFunc(GL11.GL_LESS);clear();
                GL11.glDrawArrays(GL11.GL_TRIANGLES,0,6);int material=pixel();require((material>>16)>240&&(material&255)<10,"远景贴图/LOD图集发生串色");
                clear();GL20.glUseProgram(near);matrices(near);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,6);
                GL20.glUseProgram(far);GL11.glEnable(GL11.GL_POLYGON_OFFSET_FILL);GL11.glPolygonOffset(1,1);GL11.glDrawArrays(GL11.GL_TRIANGLES,0,6);
                require((pixel()&0x00ff00)>0x00f000,"远景不应覆盖同深度真实表面");GL11.glDisable(GL11.GL_POLYGON_OFFSET_FILL);
                for(int i=0;i<pixels.capacity();i++)pixels.put(i,(byte)255);
                GL11.glTexSubImage2D(GL11.GL_TEXTURE_2D,0,0,0,128,128,GL11.GL_RGBA,GL11.GL_UNSIGNED_BYTE,pixels);
                clear();GL11.glDrawArrays(GL11.GL_TRIANGLES,0,6);require((pixel()>>16)<40,"近处遮罩未生效");
                GL20.glUniform3f(GL20.glGetUniformLocation(far,"CameraOrigin"),32,30,34);
                clear();GL11.glDrawArrays(GL11.GL_TRIANGLES,0,6);require((pixel()>>16)>240,"高处远景被二维区块遮罩误删");
                require(GL11.glGetError()==GL11.GL_NO_ERROR,"OpenGL调用发生错误");
                System.out.println("{\"passed\":true,\"production_shader_compiled\":true,\"texture_lod_no_bleed\":true,\"native_surface_wins_depth\":true,\"near_mask\":true,\"vertical_far_survives\":true,\"minecraft_client_test\":false}");
            }finally{MemoryUtil.memFree(pixels);}
        }finally{if(window!=0)GLFW.glfwDestroyWindow(window);GLFW.glfwTerminate();}
    }
}
