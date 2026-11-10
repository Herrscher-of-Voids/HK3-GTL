# PowerShell 脚本：批量生成 80 个高阶仓的 blockstate / block model / item model JSON。
# 运行方式：从项目根目录执行 `powershell -ExecutionPolicy Bypass -File tools\gen_high_tier_hatch_assets.ps1`
#
# 为什么用脚本而不是 Forge DataGen：
# - DataGen 需要完整的 provider / gradle 集成，本轮只为这一批资源接入成本过高
# - 80 个方块 × 3 种 JSON = 240 个文件，手写易错；脚本保证模板统一、易维护
# - 生成结果进 git，玩家/打包机无需运行脚本

$tierKeys = @(
    "hbv",    "hcv",    "hrv",    "hdv",
    "qsv","qcv","qev","qav",
    "imv",  "icv",  "irv",  "iwv",
    "wfv", "wsv", "civ", "cev"
)

$types = @{
    "energy_input_hatch"  = "minecraft:block/lapis_block"
    "energy_output_hatch" = "minecraft:block/amethyst_block"
    "laser_source_hatch"  = "minecraft:block/redstone_block"
    "laser_target_hatch"  = "minecraft:block/bone_block"
    "parallel_hatch"      = "minecraft:block/copper_block"
}

$root = Split-Path -Parent $PSCommandPath | Split-Path -Parent
$assets = Join-Path $root "src\main\resources\assets\hk3gtl"
$blockstateDir = Join-Path $assets "blockstates"
$blockModelDir = Join-Path $assets "models\block"
$itemModelDir  = Join-Path $assets "models\item"

foreach ($tier in $tierKeys) {
    foreach ($type in $types.Keys) {
        $id = "${tier}_${type}"
        $texture = $types[$type]

        # blockstate
        $bsPath = Join-Path $blockstateDir "$id.json"
        $bsContent = @{
            variants = @{
                "" = @{ model = "hk3gtl:block/$id" }
            }
        } | ConvertTo-Json -Depth 5 -Compress
        Set-Content -Path $bsPath -Value $bsContent -Encoding UTF8 -NoNewline

        # block model
        $bmPath = Join-Path $blockModelDir "$id.json"
        $bmContent = @{
            parent = "minecraft:block/cube_all"
            textures = @{ all = $texture }
        } | ConvertTo-Json -Depth 5 -Compress
        Set-Content -Path $bmPath -Value $bmContent -Encoding UTF8 -NoNewline

        # item model
        $imPath = Join-Path $itemModelDir "$id.json"
        $imContent = @{ parent = "hk3gtl:block/$id" } | ConvertTo-Json -Compress
        Set-Content -Path $imPath -Value $imContent -Encoding UTF8 -NoNewline
    }
}

Write-Host "Generated $(16 * 5) blockstates / block models / item models under $assets"

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。
