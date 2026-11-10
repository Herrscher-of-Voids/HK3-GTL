package com.sirin.hk3gtl.common.command;

import java.util.Map;

/**
 * 【变更记录 #1】2026-10-15 02:35:08（香港时间；内测5修订158）
 * 删除：无。新增：夹具清理的GT生命周期与外部同方块替换安全回归。
 * 修改：直接调用生产身份策略，不创建游戏、注册表、服务器或存档。
 * 用途：合法server_tick切换可清理；朝向、其他属性、实体身份和方块改变不得被删。
 */
public final class ApprovedFixtureOwnershipTest {
    private static void check(boolean valid,String message) {
        if (!valid) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        Object block=new Object(),entity=new Object(),serverTick=new Object(),facing=new Object(),active=new Object();
        Map<Object,Object> placed=Map.of(serverTick,false,facing,"north",active,false);
        Map<Object,Object> ticking=Map.of(serverTick,true,facing,"north",active,false);
        check(permits(block,block,entity,entity,placed,placed,serverTick),"同身份同状态保留清理权");
        check(permits(block,block,entity,entity,placed,ticking,serverTick),"GT启动订阅允许server_tick变化");
        check(permits(block,block,entity,entity,ticking,placed,serverTick),"GT取消订阅允许server_tick恢复");
        check(!permits(block,block,entity,new Object(),placed,placed,serverTick),"外部同方块同状态的新实体不得删");
        check(!permits(block,block,entity,new Object(),placed,ticking,serverTick),"外部新实体兼有合法属性变化仍不得删");
        check(!permits(block,new Object(),entity,entity,placed,placed,serverTick),"不同方块不得删");
        check(!permits(block,block,entity,entity,placed,
                Map.of(serverTick,true,facing,"east",active,false),serverTick),"朝向变化不得借server_tick白名单通过");
        check(!permits(block,block,entity,entity,placed,
                Map.of(serverTick,false,facing,"north",active,true),serverTick),"未白名单active属性不得删");
        check(!permits(block,block,null,null,placed,ticking,serverTick),"没有自有实体身份时不得放宽状态");
        check(!permits(block,block,entity,null,placed,placed,serverTick),"原实体消失不得认领当前状态");
        check(!permits(block,block,entity,entity,placed,ticking,new Object()),"同名或替身属性不能冒充官方对象");
        check(!permits(block,block,entity,entity,placed,
                Map.of(serverTick,"true",facing,"north",active,false),serverTick),"生命周期只能为布尔属性");
        check(!permits(block,block,entity,entity,placed,Map.of(serverTick,true,facing,"north"),serverTick),"属性缺失不得删");
        check(permits(block,block,null,null,Map.of(),Map.of(),null),"普通无实体块的精确状态可清理");
        System.out.println("ApprovedFixtureOwnershipTest passed: 14 ownership and lifecycle safety cases");
    }

    private static boolean permits(Object placedBlock,Object currentBlock,Object placedEntity,Object currentEntity,
                                   Map<?,?> placed,Map<?,?> current,Object lifecycle) {
        return Hk3ApprovedStructureRuntimeCheck.FixtureOwnership.permits(
                placedBlock,currentBlock,placedEntity,currentEntity,placed,current,lifecycle);
    }
}
