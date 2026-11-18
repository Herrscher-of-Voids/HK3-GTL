package com.sirin.hk3gtl.client.communication;

 

 






 





 





public final class Hk3LetterScreen {
    private Hk3LetterScreen(){}
    public static void open(int document,String state,net.minecraft.nbt.CompoundTag context){
        com.sirin.hk3gtl.client.phone.Hk3PhoneScreen.openLetter(document,state,context);
    }
}
