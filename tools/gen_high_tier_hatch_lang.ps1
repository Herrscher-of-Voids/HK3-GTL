# 生成 80 个高阶仓的中英文语言键，输出两份补丁文件（stdout 形式），
# 便于人工粘贴到 zh_cn.json / en_us.json 对应位置。
# 之所以不直接 in-place 改 JSON：JSON 是结构化的，用 PS 增量 merge 容易破坏其它顺序；
# 改为输出补丁让 Cursor 用 StrReplace 插入最干净。

$tierNamesZh = @(
    "海渊I","海渊II","海渊III","海渊IV",
    "虚数I","虚数II","虚数III","虚数IV",
    "量子I","量子II","量子III","量子IV",
    "终焉I","终焉II","终焉III","终焉IV"
)
$tierNamesEn = @(
    "Abyss I","Abyss II","Abyss III","Abyss IV",
    "Imaginary I","Imaginary II","Imaginary III","Imaginary IV",
    "Quantum I","Quantum II","Quantum III","Quantum IV",
    "Finality I","Finality II","Finality III","Finality IV"
)
$tierKeys = @(
    "hbv","hcv","hrv","hdv",
    "qsv","qcv","qev","qav",
    "imv","icv","irv","iwv",
    "wfv","wsv","civ","cev"
)

$typesZh = [ordered]@{
    "energy_input_hatch"  = "能源输入仓"
    "energy_output_hatch" = "能源输出仓"
    "laser_source_hatch"  = "激光源仓"
    "laser_target_hatch"  = "激光靶仓"
    "parallel_hatch"      = "并行处理仓"
}
$typesEn = [ordered]@{
    "energy_input_hatch"  = "Energy Input Hatch"
    "energy_output_hatch" = "Energy Output Hatch"
    "laser_source_hatch"  = "Laser Source Hatch"
    "laser_target_hatch"  = "Laser Target Hatch"
    "parallel_hatch"      = "Parallel Hatch"
}

function Emit($tierNames, $typesMap) {
    $lines = @()
    for ($i = 0; $i -lt 16; $i++) {
        $tk = $tierKeys[$i]
        $tn = $tierNames[$i]
        foreach ($t in $typesMap.Keys) {
            $name = "$tn $($typesMap[$t])"
            $lines += "  `"block.hk3gtl.${tk}_${t}`": `"$name`","
        }
    }
    return $lines
}

$root = Split-Path -Parent $PSCommandPath | Split-Path -Parent
$outZh = Join-Path $root "tools\high_tier_hatch_lang_zh.txt"
$outEn = Join-Path $root "tools\high_tier_hatch_lang_en.txt"
(Emit $tierNamesZh $typesZh) | Set-Content -Path $outZh -Encoding UTF8
(Emit $tierNamesEn $typesEn) | Set-Content -Path $outEn -Encoding UTF8
Write-Host "ZH lines written to $outZh"
Write-Host "EN lines written to $outEn"

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。
