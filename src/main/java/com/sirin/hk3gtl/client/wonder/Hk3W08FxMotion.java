package com.sirin.hk3gtl.client.wonder;

import org.joml.Quaternionf;

public final class Hk3W08FxMotion {
    private Hk3W08FxMotion(){}
    public static Quaternionf rotation(int ring,double phase){
        float theta=(float)phase;
        return switch(ring){
            case 0->new Quaternionf().rotationZ(.63f*theta).rotateX(theta);
            case 1->new Quaternionf().rotationZ(.47f*theta).rotateY(-.82f*theta);
            default->new Quaternionf().rotationZ(theta);
        };
    }
}
