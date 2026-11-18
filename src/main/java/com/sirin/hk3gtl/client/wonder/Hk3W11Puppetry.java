package com.sirin.hk3gtl.client.wonder;

import com.google.gson.JsonArray;
import java.util.HashMap;
import java.util.Map;
import org.joml.Matrix4f;
import org.joml.Vector3f;

final class Hk3W11Puppetry{
    record Thread(Vector3f top,Vector3f bottom){}
    record Frame(Matrix4f[] transforms,Thread[] threads){}
    private final Hk3W11FxModel model;
    private final Map<String,Integer> bones=new HashMap<>();
    private final Matrix4f[] inverseRest;
    private final float scale;
    Hk3W11Puppetry(Hk3W11FxModel model){
        this.model=model;var rig=model.data().rig();scale=rig.has("voxel_scale")?rig.get("voxel_scale").getAsFloat():1;inverseRest=new Matrix4f[model.parts().length];
        for(int i=0;i<model.parts().length;i++){
            var m=model.parts()[i].metadata();
            if(m.dynamic()){bones.put(m.actor()+"/"+m.bone(),i);inverseRest[i]=new Matrix4f().set(m.rest_matrix()).invert();}
        }
    }
    private record Motion(double phase,float pull,float roll,float sway,float forward,float twist){}
    private static Motion motion(double time,int index){
        double phase=time*.72+index*Math.PI;
        return new Motion(phase,(float)Math.sin(phase),(float)Math.sin(phase+.5),(float)Math.sin(phase*.73+.2),
                (float)Math.sin(phase*.85-.4),(float)Math.sin(phase*.5+.3));
    }
    private static Vector3f point(JsonArray a){return new Vector3f(a.get(0).getAsFloat(),a.get(1).getAsFloat(),a.get(2).getAsFloat());}
    private Vector3f rootPosition(String actor){return point(model.data().rig().getAsJsonObject("actor_root").getAsJsonArray(actor));}
    private Matrix4f root(String actor,double seconds){
        var position=rootPosition(actor);var result=new Matrix4f().translation(position);
        if(actor.equals("dominion"))return result;
        int index=actor.equals("puppet_l")?0:1;var p=motion(seconds-.18,index);
        Vector3f angles=new Vector3f();
        for(var item:model.data().rig().getAsJsonArray("poses")){
            var pose=item.getAsJsonObject();
            if(pose.get("actor").getAsString().equals(actor))angles=point(pose.getAsJsonObject("angles_degrees").getAsJsonArray("root")).mul((float)Math.PI/180);
        }
        result.translate(p.sway*12,p.pull*10,p.forward*14);
        return result.rotateXYZ(angles.x+p.forward*.035f,angles.y+p.twist*.05f,angles.z+p.sway*.03f);
    }
    private Matrix4f bone(int index,double seconds,Map<Integer,Matrix4f> world){
        var known=world.get(index);if(known!=null)return known;
        var m=model.parts()[index].metadata();float[] pivot=m.pivot(),base=m.base_rotation();
        Vector3f position=new Vector3f(pivot),angles=new Vector3f(base[0],base[1],base[2]);
        Matrix4f parent;
        if(m.parent().equals("root"))parent=root(m.actor(),seconds);
        else{
            int parentIndex=bones.get(m.actor()+"/"+m.parent());
            float[] pp=model.parts()[parentIndex].metadata().pivot();position.sub(pp[0],pp[1],pp[2]);
            parent=bone(parentIndex,seconds,world);
        }
        if(m.actor().equals("dominion")){
            int side=m.bone().equals("floating_hand_f03")?0:1;var p=motion(seconds,side);
            position.add(p.sway*8,p.pull*12,p.forward*10);
            angles.add(p.forward*.065f,p.twist*.055f,(side==0?-1:1)*p.roll*.07f);
        }else{
            int side=m.actor().equals("puppet_l")?0:1;var p=motion(seconds-.18,side);String id=m.bone();
            if(id.equals("body"))angles.add(p.forward*.03f,p.twist*.08f,-p.sway*.025f);
            if(id.equals("head"))angles.add(p.pull*.03f,p.twist*.035f,p.roll*(side==0?.05f:.025f));
            if(id.endsWith("_l")||id.endsWith("_r")){
                int direction=id.endsWith("_l")?1:-1;float knee=(float)Math.sin(p.phase+(direction==1?0:Math.PI));
                if(id.startsWith("arm_"))angles.add(p.forward*.04f,0,p.roll*.04f);
                if(id.startsWith("forearm_"))angles.add(p.pull*.035f,0,direction*p.roll*.03f);
                if(id.startsWith("hand_"))angles.add(p.roll*.06f,p.twist*.04f,0);
                if(id.startsWith("thigh_"))angles.add(knee*.06f,0,direction*p.sway*.018f);
                if(id.startsWith("shin_"))angles.x+=knee*.08f;
                if(id.startsWith("foot_"))angles.x-=.04f+knee*.03f;
            }
        }
        var result=new Matrix4f(parent).translate(position).rotateXYZ(angles.x,angles.y,angles.z);world.put(index,result);return result;
    }
    Frame frame(double seconds){
        var world=new HashMap<Integer,Matrix4f>();var transforms=new Matrix4f[model.parts().length];
        for(int i=0;i<transforms.length;i++){
            var m=model.parts()[i].metadata();
            if(m.dynamic()){
                float[] p=m.pivot();transforms[i]=new Matrix4f(bone(i,seconds,world)).translate(-p[0],-p[1],-p[2]).mul(inverseRest[i]);
                var t=transforms[i];t.setTranslation(t.m30()*scale,t.m31()*scale,t.m32()*scale);
            }else transforms[i]=new Matrix4f();
        }
        var threads=new Thread[10];int n=0;
        var rig=model.data().rig();
        for(String actor:new String[]{"puppet_l","puppet_r"}){
            var hand=rig.getAsJsonObject("hands").getAsJsonObject(actor);
            int topIndex=bones.get("dominion/"+hand.get("part").getAsString());
            var tips=new java.util.ArrayList<Vector3f>();for(var v:hand.getAsJsonArray("points"))tips.add(point(v.getAsJsonArray()));
            tips.sort(java.util.Comparator.comparingDouble(v->v.x));
            var targets=new java.util.ArrayList<com.google.gson.JsonObject>();for(var v:rig.getAsJsonArray("puppet_targets"))targets.add(v.getAsJsonObject());
            targets.sort(java.util.Comparator.comparingDouble(v->v.getAsJsonArray("point").get(0).getAsDouble()));
            for(int j=0;j<5;j++){
                var target=targets.get(j);int bottomIndex=bones.get(actor+"/"+target.get("part").getAsString());
                float[] tp=model.parts()[topIndex].metadata().pivot(),bp=model.parts()[bottomIndex].metadata().pivot();
                var top=bone(topIndex,seconds,world).transformPosition(new Vector3f(tips.get(j)).sub(tp[0],tp[1],tp[2]));
                var bottom=bone(bottomIndex,seconds,world).transformPosition(point(target.getAsJsonArray("point")).sub(bp[0],bp[1],bp[2]));
                threads[n++]=new Thread(top.mul(scale),bottom.mul(scale));
            }
        }
        return new Frame(transforms,threads);
    }
}
