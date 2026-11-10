package com.sirin.hk3gtl.common.farview;

import it.unimi.dsi.fastutil.ints.Int2IntOpenHashMap;
import it.unimi.dsi.fastutil.ints.IntArrayList;

/** 精确保存16³个实际方块；局部调色板索引每格两字节，不将薄壁扩大为实心采样块。 */
public final class Hk3FarSection {
    public record Snapshot(int[] palette,short[] cells) {
        public Snapshot {
            if(palette.length<1||palette.length>Hk3FarMesh.COUNT+1||palette[0]!=0||cells.length!=Hk3FarMesh.COUNT)
                throw new IllegalArgumentException("远景分区尺寸或调色板错误");
            for(int state:palette)if(state<0)throw new IllegalArgumentException("远景状态越界");
            for(short cell:cells)if(Short.toUnsignedInt(cell)>=palette.length)throw new IllegalArgumentException("远景调色板索引越界");
        }
        public int state(int index){return palette[Short.toUnsignedInt(cells[index])];}
    }
    private final short[] cells=new short[Hk3FarMesh.COUNT];
    private final IntArrayList palette=new IntArrayList();
    private final Int2IntOpenHashMap ids=new Int2IntOpenHashMap();
    public Hk3FarSection(){palette.add(0);}
    public int state(int index){return palette.getInt(Short.toUnsignedInt(cells[index]));}
    public boolean set(int index,int state) {
        if(state<0)throw new IllegalArgumentException("远景状态越界");
        if(state(index)==state)return false;
        int id=ids.get(state);
        if(state!=0&&id==0) {
            if(palette.size()>Hk3FarMesh.COUNT){cells[index]=0;compact();}
            id=palette.size();palette.add(state);ids.put(state,id);
        }
        cells[index]=(short)id;return true;
    }
    private void compact() {
        int[] previous=palette.toIntArray();palette.clear();palette.add(0);ids.clear();
        for(int i=0;i<cells.length;i++) {
            int state=previous[Short.toUnsignedInt(cells[i])];
            int id=ids.get(state);
            if(state!=0&&id==0){id=palette.size();palette.add(state);ids.put(state,id);}
            cells[i]=(short)id;
        }
    }
    public Snapshot snapshot(){return new Snapshot(palette.toIntArray(),cells.clone());}
}
