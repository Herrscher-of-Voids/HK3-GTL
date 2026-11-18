package com.sirin.hk3gtl.common.research;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;

import java.math.BigInteger;
import java.util.UUID;

/** 同一样本的定宽报告发生冲突后，经独立复验区分记录事实与结论。 */
public final class Hk3ContradictionRetest {
    public static final String REPORTS = "industrial_contradictory_source_sampling";
    public static final String RETEST = "industrial_contradiction_sample_retest";
    public static final String REVIEW = "industrial_contradiction_review";
    private static final int STEPS = 4096;

    private Hk3ContradictionRetest() {}

    public static boolean ready(Hk3ResearchData data, UUID team, String plan) {
        return switch (plan) {
            case REPORTS -> data.hasProcessFact(team, "three_domains");
            case RETEST -> data.hasProcessFact(team, "contradictory_source_reports");
            case REVIEW -> data.hasProcessFact(team, "contradiction_sample_retest");
            default -> true;
        };
    }

    public static void settled(Hk3ResearchData data, UUID team, String plan, CompoundTag receipt) {
        switch (plan) {
            case REPORTS -> {
                var domains = data.processFactReceipt(team, "three_domains");
                int seed = (int) (domains.getUUID("Batch").getLeastSignificantBits() & 0xffff);
                int narrow = 0;
                long wide = 0;
                for (int step = 1; step <= STEPS; step++) {
                    int reading = seed + step * step;
                    narrow += reading;
                    wide += reading;
                }
                var sample = new CompoundTag();
                sample.put("Domains", domains);
                sample.putInt("Seed", seed);
                sample.putInt("Steps", STEPS);
                sample.putString("Definition", "第1至4096步，读数=来源批次低16位+步号平方；两通道读取同一组整数。");
                receipt.put("Sample", sample);
                receipt.put("Report32", report(receipt, 32, narrow));
                receipt.put("Report64", report(receipt, 64, wide));
                data.recordProcessFact(team, "contradictory_source_reports", receipt);
            }
            case RETEST -> {
                var reports = data.processFactReceipt(team, "contradictory_source_reports");
                var sample = reports.getCompound("Sample");
                var total = BigInteger.ZERO;
                var seed = BigInteger.valueOf(sample.getInt("Seed"));
                for (int step = sample.getInt("Steps"); step > 0; step--) {
                    var index = BigInteger.valueOf(step);
                    total = total.add(seed).add(index.multiply(index));
                }
                receipt.put("OriginalReports", reports);
                receipt.putString("Method", "任意精度整数、倒序独立累加，保留完整总量，不作定宽截断。");
                receipt.putString("ExactTotal", total.toString());
                receipt.putInt("Steps", sample.getInt("Steps"));
                data.recordProcessFact(team, "contradiction_sample_retest", receipt);
            }
            case REVIEW -> {
                var retest = data.processFactReceipt(team, "contradiction_sample_retest");
                var reports = retest.getCompound("OriginalReports");
                var sample = reports.getCompound("Sample");
                var steps = BigInteger.valueOf(sample.getInt("Steps"));
                var expected = BigInteger.valueOf(sample.getInt("Seed")).multiply(steps)
                        .add(steps.multiply(steps.add(BigInteger.ONE))
                                .multiply(steps.multiply(BigInteger.TWO).add(BigInteger.ONE)).divide(BigInteger.valueOf(6)));
                var narrow = new BigInteger(reports.getCompound("Report32").getString("Value"));
                var wide = new BigInteger(reports.getCompound("Report64").getString("Value"));
                if (!retest.getString("ExactTotal").equals(expected.toString()) || !wide.equals(expected)
                        || narrow.equals(wide) || narrow.intValue() != expected.intValue()) return;
                receipt.put("Retest", retest);
                receipt.putString("Expected", expected.toString());
                receipt.put("Facts", lines("三领域原始批次、同一样本定义及两份原文完整保留。",
                        "32位通道实际输出" + narrow + "，64位通道实际输出" + wide + "。",
                        "独立任意精度复验与闭式复核均得到" + expected + "。"));
                receipt.put("Inferences", lines("两份报告对同一样本完整总量的断言互斥。",
                        "32位报告保留截断后的有符号值，其完整总量断言不成立；64位报告在本次有限扫描内与复验相符。"));
                receipt.put("Undetermined", lines("本次证明只覆盖给定样本的信息处理条件，不能判定三领域的一般物理规律。",
                        "不同样本、不同扫描范围及其他观测装置须另行取样复验。"));
                data.recordProcessFact(team, "contradiction_retest", receipt);
            }
        }
    }

    private static CompoundTag report(CompoundTag receipt, int bits, long value) {
        var report = new CompoundTag();
        report.putUUID("SourceBatch", receipt.getUUID("Batch"));
        report.putString("Source", receipt.getString("Facility") + "/" + bits + "位采样通道");
        report.putString("Recipe", receipt.getString("Recipe"));
        report.putString("Condition", "相同4096步输入；有符号" + bits + "位整数逐步累加，保留通道原始输出。");
        report.putString("Proposition", "同一样本4096步扫描的完整整数总量");
        report.putString("OriginalText", "本报告断言：同一样本4096步扫描的完整整数总量为" + value + "。");
        report.putString("Value", Long.toString(value));
        return report;
    }

    private static ListTag lines(String... lines) {
        var result = new ListTag();
        for (String line : lines) result.add(StringTag.valueOf(line));
        return result;
    }
}
