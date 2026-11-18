package com.sirin.hk3gtl.client.wonder;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

final class Hk3W13Puppetry{
    private static final float[][] GAZE={{0,0},{.9f,.3f},{-.55f,-.55f},{-1,.45f},{.35f,.85f},{1,-.4f},{0,0}};
    private final Hk3W13FxModel model;
    private final Matrix4f[] transforms;
    private final Vector3f[][] joints=new Vector3f[9][17];
    private final Matrix4f[][] cables=new Matrix4f[9][16];
    private final Matrix4f eye=new Matrix4f();
    Hk3W13Puppetry(Hk3W13FxModel model){
        this.model=model;transforms=new Matrix4f[model.parts().length];
        for(int i=0;i<transforms.length;i++)transforms[i]=new Matrix4f().set(model.parts()[i].metadata().rest_matrix());
        for(int c=0;c<9;c++){for(int i=0;i<17;i++)joints[c][i]=new Vector3f();for(int i=0;i<16;i++)cables[c][i]=new Matrix4f();}
    }
    Matrix4f[] frame(double seconds){
        double step=seconds/3,phase=step-Math.floor(step),blend=Math.max(0,(phase-.4)/.6),ease=blend*blend*(3-2*blend);
        int index=(int)Math.floor(step)%GAZE.length;float[] from=GAZE[index],to=GAZE[(index+1)%GAZE.length];
        float x=(float)(from[0]+(to[0]-from[0])*ease)*16,y=(float)(from[1]+(to[1]-from[1])*ease)*3;
        eye.translation(.5f+x,525.5f+y,254.5f).rotateXYZ(-y*.02f,x*.005625f,(float)Math.sin(seconds*.7)*.012f);
        float gain=(float)(1-Math.exp(-seconds*2));
        for(int c=0;c<9;c++){
            var rig=model.data().rig()[c];var points=joints[c];double p=seconds*(.65+c*.047)+c*1.71;
            points[0].set(rig.rest()[0]);
            if(c==2)for(int j=1;j<17;j++){
                points[j].set(rig.rest()[j]);
                if(j>1&&j<15){float envelope=(float)Math.sin(Math.PI*(j-1)/14)*gain;
                    points[j].add(1.8f*envelope*(float)Math.sin(p-j*.36),0,2.4f*envelope*(float)Math.cos(p*.83-j*.31));}
            }
            for(int i=0;i<16;i++){
                var base=new Quaternionf(rig.quaternions()[i][0],rig.quaternions()[i][1],rig.quaternions()[i][2],rig.quaternions()[i][3]);
                Quaternionf rotation;
                if(c==2){
                    var direction=new Vector3f(points[i+1]).sub(points[i]).normalize();
                    rotation=new Quaternionf().rotationTo(new Vector3f(rig.units()[i]),direction).mul(base);
                }else{
                    float amplitude=rig.budget()*(i==0?0:(float)Math.pow(i/15.,1.25))*gain;
                    rotation=new Quaternionf().rotationXYZ(.6f*amplitude*(float)Math.sin(p-i*.36),0,.4f*amplitude*(float)Math.cos(p*.83-i*.29)).mul(base);
                    points[i+1].set(0,1,0).rotate(rotation).mul(rig.lengths()[i]).add(points[i]);
                }
                cables[c][i].translation(points[i]).rotate(rotation);
            }
        }
        for(int i=0;i<transforms.length;i++){
            var m=model.parts()[i].metadata();
            if(m.mode()==3)transforms[i].set(eye);
            if(m.mode()==4)transforms[i].set(cables[m.cable()][m.segment()]);
        }
        return transforms;
    }
}
