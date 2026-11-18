package com.sirin.hk3gtl.common.phone.cipher;

import java.util.List;
import java.util.Locale;

public final class Hk3CipherPuzzles {
    public record Puzzle(String id, String title, String body, String hint, String answer) {}

    private static final List<Puzzle> PUZZLES = List.of(
            new Puzzle("fold", "折痕", """
                    纸舟的封面写着：
                    「归航的信，要从归航的方向读。」

                    字条：A E S D E E S

                    字条右端画着起点，箭头朝左。
                    从最右边开始，向左依次抄下七个字母。
                    不用翻译，也不用把字母画成镜像。

                    只输入抄出的字母，大小写和空格不影响。
                    这就是这片海的名字。
                    """, "整串从右往左读：先抄最右边的 S，再抄它左边的 E，一直读到最左边。", "SEEDSEA"),
            new Puzzle("drift", "移走的名字", """
                    「名字没有消失，只是走远了一格。」

                    密文：T J S J O

                    字母表：ABCDEFGHIJKLMNOPQRSTUVWXYZ

                    把密文中的每个字母，换成字母表里
                    紧挨着它前面的字母，例如 B → A、D → C。
                    五个字母都退一格，再按原顺序连起来。

                    这一页不需要上一页的答案作钥匙。
                    输入还原的五个字母，不用翻译名字。
                    """, "从第一个字母开始：T 的前一个是 S；其余四个字母也各退一格。", "SIRIN"),
            new Puzzle("book", "四页无页码的书", """
                    书没有页码，但四张页签还在：

                    A：FOUR SMALL BOATS
                    B：A GIFT WAITS
                    C：SEEDS IN STACKS
                    D：KEEP THE NAME

                    书签只留下两个坐标：A1、C3。

                    字母选页，数字选这一页的第几个单词。
                    单词由空格分开，从 1 开始数。
                    先取 A 页第一个词，再取 C 页第三个词。
                    把这两个词连起来输入，不用翻译。
                    """, "A1 取的是 FOUR。C 页的三个词依次为 SEEDS、IN、STACKS，取第三个接在后面。", "FOURSTACKS"),
            new Puzzle("columns", "错位的礼单", """
                    「礼单被风吹散，幸好每一片都标了号。」

                    ③ ZHE
                    ① ZI
                    ⑤ XI
                    ② JI
                    ⑥ GUA
                    ④ ZHONG

                    按编号 1 → 6 重新排列六张纸片，
                    每片里面的字母顺序保持原样。
                    最后只把字母连起来输入，不抄编号。

                    纸片已经写好拼音，不必自己猜称呼。
                    """, "先放 ① ZI，再放 ② JI，接着找 ③、④、⑤、⑥；每一片都用一次。", "ZIJIZHEZHONGXIGUA"),
            new Puzzle("recipient", "收件人", """
                    「你建造过许多世界。
                    这一次，换我们为你留下一个。」

                    信封上的玩家名被写成了八个数字：
                    24、9、7、21、1、13、1、15

                    字母表：ABCDEFGHIJKLMNOPQRSTUVWXYZ
                    A = 1，B = 2，C = 3，依次到 Z = 26。

                    数字表示字母在表中的位置，从 1 开始数。
                    例如 3 就换成 C。
                    依次把八个数字换成字母，再连起来输入。

                    不需要上一页的拼音作钥匙，也不用输入数字。
                    """, "第一个数字 24 对应 X，第二个数字 9 对应 I；照这样把剩下六个数字也换成字母。", "XIGUAMAO")
    );

    private Hk3CipherPuzzles() {}

    public static List<Puzzle> all() {
        return PUZZLES;
    }

    public static boolean accepts(int stage, String input) {
        return PUZZLES.get(stage).answer().equals(input.replaceAll("[\\s_-]+", "").toUpperCase(Locale.ROOT));
    }
}
