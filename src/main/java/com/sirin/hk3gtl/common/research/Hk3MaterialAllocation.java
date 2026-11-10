package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】保留最大流扣料分配，并返回逐需求分配以区分耗材与不消耗工装。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：保留最大流扣料分配，并返回逐需求分配以区分耗材与不消耗工装。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import java.util.Arrays;

/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
public final class Hk3MaterialAllocation {
    private Hk3MaterialAllocation() {}

    /** 数量单位为物品个数，全部非负；溢出拒绝，输入数组不修改。 / Counts are whole items; reject overflow and never mutate caller arrays. */
    public static long[] allocate(long[] stock, long[] cost, boolean[][] matches) {
        var plan=allocateDetailed(stock,cost,matches); return plan==null?null:plan.used();
    }
    /** 修订100：保留每种需求的分配，准确区分消耗品和需退回的带NBT工装。 */
    public record Plan(long[] used,long[][] assigned) {}
    public static Plan allocateDetailed(long[] stock, long[] cost, boolean[][] matches) {
        int s = stock.length, c = cost.length, sink = s+c+1, n = sink+1;
        if (s > 128 || c < 1 || c > 128 || matches.length != s) throw new IllegalArgumentException("Invalid allocation size");
        long[][] residual = new long[n][n]; long required = 0;
        for (int j=0;j<c;j++) {
            if (cost[j] < 1) throw new IllegalArgumentException("Invalid cost");
            required = Math.addExact(required, cost[j]); residual[1+s+j][sink] = cost[j];
        }
        for (int i=0;i<s;i++) {
            if (stock[i] < 0 || matches[i].length != c) throw new IllegalArgumentException("Invalid stock/matches");
            residual[0][1+i] = stock[i];
            for (int j=0;j<c;j++) if (matches[i][j]) residual[1+i][1+s+j] = Math.min(stock[i], cost[j]);
        }
        long flow = 0;
        while (flow < required) {
            int[] parents = new int[n], queue = new int[n]; Arrays.fill(parents, -1);
            int head=0, tail=0; queue[tail++]=0; parents[0]=0;
            while (head < tail && parents[sink] == -1) {
                int u=queue[head++];
                for (int v=1;v<n;v++) if (parents[v] == -1 && residual[u][v] > 0) { parents[v]=u; queue[tail++]=v; }
            }
            if (parents[sink] == -1) return null;
            long amount = required-flow;
            for (int v=sink;v!=0;v=parents[v]) amount = Math.min(amount, residual[parents[v]][v]);
            for (int v=sink;v!=0;v=parents[v]) { residual[parents[v]][v]-=amount; residual[v][parents[v]]+=amount; }
            flow+=amount;
        }
        long[] used = new long[s];
        long[][] assigned=new long[s][c];
        for (int i=0;i<s;i++) used[i]=stock[i]-residual[0][i+1];
        for(int i=0;i<s;i++)for(int j=0;j<c;j++)assigned[i][j]=residual[1+s+j][1+i];
        return new Plan(used,assigned);
    }
}
