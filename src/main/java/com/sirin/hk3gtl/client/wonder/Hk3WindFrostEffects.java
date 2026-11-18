package com.sirin.hk3gtl.client.wonder;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.GameRenderer;
import org.joml.Matrix4f;
import org.joml.Vector3f;

final class Hk3WindFrostEffects {
    private static final BufferBuilder BUILDER=new BufferBuilder(2*1024*1024);
    private static final Vector3f RIGHT=new Vector3f(),UP=new Vector3f();
    private static final Gson GSON=new Gson();
    private static VertexBuffer particles;
    private static Wind wind;
    private static Frost frost;
    private Hk3WindFrostEffects(){}

    private record Tower(float[] center,float bottom,float top,float radius){}
    private record Accent(float[] center,float radius,String color){}
    private record Crown(float[] pivot,float[] motion_axis,float idle_speed,float running_speed,Accent[] accents){}
    private record Wind(float[][][] stream_paths,float[] stream_phase_offsets,float flow_speed,int flow_beads_per_path,
                        float[] flow_bead_radii,int flow_color,int flow_tube_color,Tower[] towers,float tower_speed,
                        float tower_running_multiplier,int tower_strands,float tower_turns,float[][] lightning_origins,
                        float[] lightning_target,int lightning_branches,int lightning_samples,int lightning_color,
                        float pulse_speed,float pulse_phase_multiplier,float pulse_visible_threshold,
                        float[] tail_ring_z,float[] tail_ring_radii,float tail_ring_radius,int tail_color,
                        float[] tail_helix_start_z,float tail_helix_length,float[] crown_center,float[] crown_y_range,
                        float[] crown_radius_range,int crown_strands,float crown_twist,Crown[] crowns,
                        float tornado_speed,float[] tornado_y_range,float tornado_radius,float tornado_turns,
                        int tornado_strands,float[] refraction_speeds){}
    private record Frost(float[] center,int snow_count,float snow_width,float snow_depth,float snow_height,
                         float[] snow_speed_range,float snow_preview_step,float snow_wind_frequency,
                         float snow_wind_particle_phase,float snow_wind_step,int snow_color,float snow_size,float snow_opacity,
                         int star_count,float[] star_y_range,int star_color,float star_size,float[] star_opacity,float star_frequency,
                         int aurora_count,float aurora_width,int aurora_steps,float aurora_y,float aurora_y_step,
                         float aurora_y_amplitude,float aurora_z_offset,float aurora_z_step,float aurora_z_amplitude,
                         float[] aurora_y_extent,int aurora_color,float[] aurora_opacity,float aurora_frequency,
                         float beam_height,float[] beam_radii,int[] beam_colors,float[] beam_opacity,
                         float[] beam_opacity_amplitudes,float[] beam_frequencies,float[] beam_phases,
                         float[] end_ring_y,float end_ring_radius,float end_ring_thickness,int end_ring_color,
                         float end_ring_scale_amplitude,float end_ring_frequency){}

    static void clear(){
        if(particles!=null){particles.close();particles=null;}
        wind=null;frost=null;
    }
    static void draw(String role,JsonObject effects,Matrix4f origin,Matrix4f projection,Vector3f right,Vector3f up,
                     double idle,double work,double seconds,double seed,boolean running){
        RIGHT.set(right);UP.set(up);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);
        RenderSystem.setShaderColor(1,1,1,1);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        if(role.equals("W05")){
            if(wind==null)wind=GSON.fromJson(effects,Wind.class);
            drawWind(idle,work,seconds,running);
        }else{
            if(frost==null)frost=GSON.fromJson(effects,Frost.class);
            drawFrost(seconds,seed,running);
        }
        if(particles==null)particles=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        particles.bind();particles.upload(BUILDER.end());particles.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        VertexBuffer.unbind();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }

    private static void drawWind(double idle,double work,double time,boolean running){
        if(running){
            for(int i=0;i<wind.stream_paths.length;i++){
                var path=wind.stream_paths[i];
                for(int j=1;j<path.length;j++)trace(path[j-1],path[j],.7,wind.flow_tube_color,.23);
                for(int j=0;j<wind.flow_beads_per_path;j++){
                    double t=fract(time*wind.flow_speed+j/(double)wind.flow_beads_per_path+wind.stream_phase_offsets[i])*(path.length-1);
                    int index=(int)t;float[] a=path[index],b=path[index+1];double f=t-index;
                    pixel(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f,
                            wind.flow_bead_radii[j%wind.flow_bead_radii.length]*2,wind.flow_color,.7);
                }
            }
            for(int strand=0;strand<wind.tornado_strands;strand++)for(int i=0;i<200;i++){
                double t=i/199.,a=wind.tornado_turns*Math.PI*2*t+strand*Math.PI*2/wind.tornado_strands+time*wind.tornado_speed;
                double r=wind.tornado_radius*(.36+.64*t);
                pixel(Math.cos(a)*r,mix(wind.tornado_y_range,t),Math.sin(a)*r,3.2,wind.tail_color,.28);
            }
            for(int band=0;band<wind.refraction_speeds.length;band++)for(int i=0;i<120;i++){
                double t=i/119.,a=t*Math.PI*5+wind.refraction_speeds[band]*(idle+work*wind.tower_running_multiplier);
                double r=35+band*8+Math.sin(t*Math.PI)*9;
                pixel(Math.cos(a)*r,160+(t-.5)*77,Math.sin(a)*r,4.4,0xc5fff2,.22);
            }
        }
        double towerTurn=wind.tower_speed*(idle+work*wind.tower_running_multiplier);
        for(var tower:wind.towers)for(int strand=0;strand<wind.tower_strands;strand++)for(int i=0;i<180;i++){
            double t=i/179.,a=wind.tower_turns*Math.PI*2*t+strand*Math.PI*2/wind.tower_strands+towerTurn;
            double r=tower.radius*(.36+.64*t);
            pixel(tower.center[0]+Math.cos(a)*r,tower.bottom+(tower.top-tower.bottom)*t,
                    tower.center[2]+Math.sin(a)*r,1.5,wind.tail_color,.28);
        }
        for(float[] source:wind.lightning_origins)for(int branch=0;branch<wind.lightning_branches;branch++){
            if(Math.sin(time*wind.pulse_speed+(branch+Math.signum(source[0]))*wind.pulse_phase_multiplier)<=wind.pulse_visible_threshold)continue;
            for(int i=1;i<wind.lightning_samples;i++){
                var a=lightning(source,branch,i-1);var b=lightning(source,branch,i);
                trace(a,b,1.1,wind.lightning_color,.6);
            }
        }
        for(int i=0;i<wind.tail_ring_z.length;i++){
            if(Math.sin(time*wind.pulse_speed+i*wind.pulse_phase_multiplier)>wind.pulse_visible_threshold)
                ring(0,160,wind.tail_ring_z[i],wind.tail_ring_radii[i],wind.tail_ring_radius*2,wind.tail_color,.28,false);
        }
        for(float start:wind.tail_helix_start_z)for(int j=0;j<120;j++){
            double t=j/119.,a=t*Math.PI*2,r=13+Math.sin(t*Math.PI)*15;
            pixel(Math.cos(a)*r,160+Math.sin(a)*r,start+wind.tail_helix_length*t,1.6,wind.flow_color,.7);
        }
        for(int strand=0;strand<wind.crown_strands;strand++)for(int j=0;j<110;j++){
            double t=j/109.,a=strand/(double)wind.crown_strands*Math.PI*2+t*wind.crown_twist;
            double r=wind.crown_radius_range[0]+(wind.crown_radius_range[1]-wind.crown_radius_range[0])*t*t;
            pixel(wind.crown_center[0]+Math.cos(a)*r,mix(wind.crown_y_range,t),wind.crown_center[2]+Math.sin(a)*r,
                    1.8,wind.flow_tube_color,.23);
        }
        for(int row=0;row<36;row++)for(int column=0;column<wind.crown_strands;column++){
            double t=(row+.5)/36,a=(column+.38)/wind.crown_strands*Math.PI*2+t*wind.crown_twist;
            double r=wind.crown_radius_range[0]+(wind.crown_radius_range[1]-wind.crown_radius_range[0])*t*t;
            pixel(wind.crown_center[0]+Math.cos(a)*r,mix(wind.crown_y_range,t),wind.crown_center[2]+Math.sin(a)*r,
                    4+8*t,0x5eebd0,.035);
        }
        for(var crown:wind.crowns){
            float[] p=crown.pivot,a=crown.motion_axis;
            var transform=new Matrix4f().translate(p[0],p[1],p[2])
                    .rotate((float)(idle*crown.idle_speed+work*crown.running_speed),new Vector3f(a[0],a[1],a[2]).normalize())
                    .translate(-p[0],-p[1],-p[2]);
            for(var accent:crown.accents){
                var point=transform.transformPosition(new Vector3f(accent.center[0],accent.center[1],accent.center[2]));
                pixel(point.x,point.y,point.z,accent.radius*2,Integer.parseInt(accent.color.substring(1),16),.5);
            }
        }
    }

    private static float[] lightning(float[] source,int branch,int index){
        double t=index/(double)(wind.lightning_samples-1),curve=Math.sin(t*Math.PI);
        return new float[]{(float)(source[0]*(1-t)+wind.lightning_target[0]*t+Math.sin(index*2.7+branch)*10*curve),
                (float)(source[1]*(1-t)+wind.lightning_target[1]*t+(branch-1.5)*9*curve),
                (float)(source[2]*(1-t)+wind.lightning_target[2]*t+Math.cos(index*1.9+branch)*11*curve)};
    }

    private static void drawFrost(double time,double seed,boolean running){
        double cx=frost.center[0],cz=frost.center[2],height=frost.snow_height;
        long random=0x6d2b79f5L;
        for(int i=0;i<frost.snow_count;i++){
            random=next(random);double x=cx+(unit(random)-.5)*frost.snow_width;
            random=next(random);double y=unit(random)*height;
            random=next(random);double z=cz+(unit(random)-.5)*frost.snow_depth;
            random=next(random);double speed=mix(frost.snow_speed_range,unit(random))*frost.snow_preview_step*60;
            y=height*fract((y-speed*time)/height);
            double drift=frost.snow_wind_step*60/frost.snow_wind_frequency;
            x+=drift*(Math.cos(i*frost.snow_wind_particle_phase)-Math.cos(time*frost.snow_wind_frequency+i*frost.snow_wind_particle_phase));
            pixel(x,y,z,frost.snow_size,frost.snow_color,frost.snow_opacity);
        }
        for(int i=0;i<frost.star_count;i++){
            random=next(random);double x=cx+(unit(random)-.5)*frost.snow_width;
            random=next(random);double y=mix(frost.star_y_range,unit(random));
            random=next(random);double z=cz+(unit(random)-.5)*frost.snow_depth;
            pixel(x,y,z,frost.star_size,frost.star_color,frost.star_opacity[0]+Math.sin(time*frost.star_frequency)*frost.star_opacity[1]);
        }
        double curtain=frost.aurora_opacity[0]+Math.sin(time*frost.aurora_frequency)*frost.aurora_opacity[1];
        for(int band=0;band<frost.aurora_count;band++)for(int i=0;i<frost.aurora_steps;i++)for(int row=0;row<12;row++){
            double t=(i+.5)/frost.aurora_steps,x=cx+(t-.5)*frost.aurora_width;
            double y=frost.aurora_y+band*frost.aurora_y_step+Math.sin(t*9+band*1.4)*frost.aurora_y_amplitude;
            double z=cz+frost.aurora_z_offset+band*frost.aurora_z_step+Math.sin(t*14+band)*frost.aurora_z_amplitude;
            pixel(x,y+mix(frost.aurora_y_extent,(row+.5)/12),z,frost.aurora_width/frost.aurora_steps*1.02,frost.aurora_color,curtain);
        }
        if(running){
            for(int layer=0;layer<frost.beam_radii.length;layer++){
                double radius=frost.beam_radii[layer],alpha=frost.beam_opacity[layer]
                        +Math.sin(time*frost.beam_frequencies[layer]+frost.beam_phases[layer])*frost.beam_opacity_amplitudes[layer];
                int sides=Math.max(4,(int)Math.ceil(radius*Math.PI));
                for(int i=0;i<=191;i++)for(int j=0;j<sides;j++){
                    double a=j/(double)sides*Math.PI*2;
                    pixel(cx+Math.cos(a)*radius,frost.beam_height*i/191.,cz+Math.sin(a)*radius,2.2,frost.beam_colors[layer],alpha);
                }
            }
            for(int i=0;i<frost.end_ring_y.length;i++){
                double scale=1+Math.sin(time*frost.end_ring_frequency+i)*frost.end_ring_scale_amplitude;
                ring(cx,frost.end_ring_y[i],cz,frost.end_ring_radius*scale,frost.end_ring_thickness*2,frost.end_ring_color,.7,true);
            }
        }
    }

    private static long next(long value){return (value*1664525+1013904223)&0xffffffffL;}
    private static double unit(long value){return value/4294967296.;}
    private static double fract(double value){return value-Math.floor(value);}
    private static double mix(float[] values,double t){return values[0]+(values[1]-values[0])*t;}
    private static void ring(double x,double y,double z,double radius,double size,int color,double alpha,boolean horizontal){
        int count=(int)Math.ceil(radius*Math.PI*2);
        for(int i=0;i<count;i++){
            double a=i/(double)count*Math.PI*2;
            pixel(x+Math.cos(a)*radius,y+(horizontal?0:Math.sin(a)*radius),z+(horizontal?Math.sin(a)*radius:0),size,color,alpha);
        }
    }
    private static void trace(float[] start,float[] end,double size,int color,double alpha){
        double dx=end[0]-start[0],dy=end[1]-start[1],dz=end[2]-start[2];
        int count=(int)Math.ceil(Math.sqrt(dx*dx+dy*dy+dz*dz)/Math.max(.8,size));
        for(int i=0;i<count;i++){
            double t=i/(double)count;
            pixel(start[0]+dx*t,start[1]+dy*t,start[2]+dz*t,size,color,alpha);
        }
    }
    private static void pixel(double x,double y,double z,double size,int color,double opacity){
        float half=(float)(size*.5);int alpha=(int)(255*opacity);
        for(int i=0;i<4;i++){
            float r=i==1||i==2?half:-half,u=i>=2?half:-half;
            BUILDER.vertex(x+RIGHT.x*r+UP.x*u,y+RIGHT.y*r+UP.y*u,z+RIGHT.z*r+UP.z*u)
                    .color(color>>16&255,color>>8&255,color&255,alpha).endVertex();
        }
    }
}
