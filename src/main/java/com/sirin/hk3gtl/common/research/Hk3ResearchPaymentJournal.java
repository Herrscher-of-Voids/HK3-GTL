package com.sirin.hk3gtl.common.research;

import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.UUID;

/**
 * 【文件职责】保存研究账本和付款玩家的事务后像，重放时固定写回相同文件，重复执行不再扣料或发奖。
 * 【变更记录 #1】2026-11-04 01:23:43（第1次备注 · 内测5修订194）
 * - 删除：无。
 * - 新增：压缩NBT预写日志、强制落盘、原子替换与严格结构校验；失败保留日志并向调用者抛错。
 * - 修改：研究支付文件先写日志，再写玩家、账本，最后移除日志；不支持原子移动的文件系统拒绝提交。
 * - 用途：Hk3ResearchPayment调用；恢复JVM强停后的跨文件支付，不承诺操作系统断电或外部能源仓的原子性。
 */
/**
 * 【变更记录 #2】2026-11-04 02:53:59（第2次备注 · 内测5修订194）
 * - 删除：重放文件后立即删除日志的顺序；新增：独立finish完成点。
 * - 修改：recover/replay保留日志，调用方恢复缓存及玩家内存后才能finish，失败仍能重启恢复。
 * - 用途：防止内存恢复或界面同步异常后正常停服以旧缓存覆盖文件，却已失去重放决定。
 */
public final class Hk3ResearchPaymentJournal {
    private Hk3ResearchPaymentJournal() {}
    public static final String LEDGER = "hk3gtl_research_v5";
    public static final String JOURNAL = "hk3gtl_research_payment.wal";

    public static Path journal(Path root) { return root.resolve("data").resolve(JOURNAL); }

    /** 日志是提交点；此前失败不改目标文件，此后必须重放，不能回滚已持久的决定。 */
    public static void prepare(Path root, UUID payer, CompoundTag ledger, CompoundTag player) throws IOException {
        if (!Files.notExists(journal(root))) throw new IOException("支付日志未恢复，拒绝覆盖：" + journal(root));
        CompoundTag record = new CompoundTag();
        record.putInt("Version", 1); record.putUUID("Payer", payer);
        record.put("Ledger", ledger.copy()); record.put("Player", player.copy());
        validate(record);
        write(journal(root), record);
    }

    /** 文件不存在才视为空闲；损坏或读取失败不能创建空账本，也不能移除日志。 */
    public static CompoundTag recover(Path root) throws IOException {
        Path file = journal(root);
        if (Files.notExists(file)) return null;
        CompoundTag record = NbtIo.readCompressed(file.toFile());
        validate(record);
        replay(root, record);
        return record;
    }

    public static void replay(Path root, CompoundTag record) throws IOException {
        validate(record);
        UUID payer = record.getUUID("Payer");
        write(root.resolve("playerdata").resolve(payer + ".dat"), record.getCompound("Player"));
        // 单人服主优先从level.dat读取，必须与playerdata一起重放，不能让旧内嵌库存复活。
        Path levelFile = root.resolve("level.dat");
        if (!Files.notExists(levelFile)) {
            CompoundTag level = NbtIo.readCompressed(levelFile.toFile());
            CompoundTag embedded = level.getCompound("Data").getCompound("Player");
            if (embedded.hasUUID("UUID") && payer.equals(embedded.getUUID("UUID"))) {
                level.getCompound("Data").put("Player", record.getCompound("Player").copy());
                write(levelFile, level);
            }
        }
        CompoundTag envelope = new CompoundTag();
        envelope.put("data", record.getCompound("Ledger").copy());
        envelope.putInt("DataVersion", SharedConstants.getCurrentVersion().getDataVersion().getVersion());
        write(root.resolve("data").resolve(LEDGER + ".dat"), envelope);
    }

    /** 必须在文件与内存都恢复成功后调用，任何先前步骤失败都保留原日志。 */
    public static void finish(Path root) throws IOException { Files.delete(journal(root)); }

    private static void validate(CompoundTag record) throws IOException {
        if (!record.contains("Version", Tag.TAG_INT) || record.getInt("Version") != 1 || !record.hasUUID("Payer")
                || !record.contains("Ledger", Tag.TAG_COMPOUND) || !record.contains("Player", Tag.TAG_COMPOUND))
            throw new IOException("研究支付日志结构损坏");
        CompoundTag player = record.getCompound("Player");
        if (!player.hasUUID("UUID") || !record.getUUID("Payer").equals(player.getUUID("UUID"))
                || !player.contains("Inventory", Tag.TAG_LIST)) throw new IOException("研究支付玩家后像损坏");
        try { Hk3ResearchData.load(record.getCompound("Ledger")); }
        catch (RuntimeException failure) { throw new IOException("研究支付账本后像损坏", failure); }
    }

    /** 临时文件与目标同目录，文件强制写入后原子替换；绝不回退到可能留下半文件的复制。 */
    public static void write(Path target, CompoundTag value) throws IOException {
        Files.createDirectories(target.getParent());
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        NbtIo.writeCompressed(value, bytes);
        Path temporary = Files.createTempFile(target.getParent(), target.getFileName().toString(), ".pending");
        try {
            try (FileChannel channel = FileChannel.open(temporary, StandardOpenOption.WRITE)) {
                ByteBuffer buffer = ByteBuffer.wrap(bytes.toByteArray());
                while (buffer.hasRemaining()) channel.write(buffer);
                channel.force(true);
            }
            Files.move(temporary, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } finally { Files.deleteIfExists(temporary); }
    }
}
