package com.sirin.hk3gtl.common.easter;
/** 【变更记录 #1】2026-10-01 04:19:02（修订128）：删除无；新增连续正文片段校验；修改无；用途：打开不是读完，跳末页/重传/旧会话不算全读，不绑定字体或GUI缩放。 */
public final class Hk3EggReadingCursor {
    private final String body;private int offset,pages;
    public Hk3EggReadingCursor(String body){this.body=normalize(body);if(this.body.length()>131072)throw new IllegalArgumentException("正文过长");}
    public static String normalize(String text){var b=new StringBuilder();text.codePoints().filter(c->!Character.isWhitespace(c)).forEach(b::appendCodePoint);return b.toString();}
    public boolean accept(int start,String piece){
        String value=normalize(piece);
        if(start!=offset||value.isEmpty()||value.length()>4096||offset+value.length()>body.length()||!body.startsWith(value,offset))return false;
        offset+=value.length();pages++;return true;
    }
    public boolean done(){return !body.isEmpty()&&offset==body.length();}
    public int pages(){return pages;}
}
