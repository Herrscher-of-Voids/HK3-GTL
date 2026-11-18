package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】保留最大流扣料分配，并返回逐需求分配以区分耗材与不消耗工装。
 */

import java.util.Arrays;

public final class Hk3MaterialAllocation {
    private Hk3MaterialAllocation() {}

    /** 数量单位为物品个数，全部非负；溢出拒绝，输入数组不修改。 / Counts are whole items; reject overflow and never mutate caller arrays. */
    public static long[] allocate(long[] stock, long[] cost, boolean[][] matches) {
        var plan=allocateDetailed(stock,cost,matches); return plan==null?null:plan.used();
    }
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
