package com.sirin.hk3gtl.common.easter;
 
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
