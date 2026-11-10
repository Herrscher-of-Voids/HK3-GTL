$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$javaRoot = Join-Path $root "src/main/java/com/sirin/hk3gtl"
$recipeRoot = Join-Path $javaRoot "common/recipe"
$machineRoot = Join-Path $javaRoot "common/machine"
$eventRoot = Join-Path $javaRoot "common/event"
$regTabFile = Join-Path $javaRoot "common/registration/Hk3CreativeTabsImpl.java"

function Get-Text([string]$path) {
    return [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
}

function Normalize-RecipeTypeRef([string]$typeRef) {
    if ($typeRef.StartsWith("Hk3RecipeTypesImpl.")) {
        return "Hk3RecipeTypes." + $typeRef.Substring("Hk3RecipeTypesImpl.".Length)
    }
    return $typeRef
}

function Parse-Controllers {
    $text = Get-Text $regTabFile
    $arrayMatch = [regex]::Match($text, "MULTIBLOCK_CONTROLLER_PATHS\s*=\s*\{(?<body>.*?)\};", [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if (-not $arrayMatch.Success) {
        throw "无法定位 MULTIBLOCK_CONTROLLER_PATHS"
    }
    $strMatches = [regex]::Matches($arrayMatch.Groups["body"].Value, '"([^"]+)"')
    return @($strMatches | ForEach-Object { $_.Groups[1].Value })
}

function Parse-RecipeTypes {
    $map = @{}
    Get-ChildItem $recipeRoot -Filter "Hk3RecipeTypes*.java" | ForEach-Object {
        $cls = $_.BaseName
        $text = Get-Text $_.FullName
        $matches = [regex]::Matches(
            $text,
            "public\s+static\s+final\s+GTRecipeType\s+([A-Z0-9_]+)\s*=\s*GTRecipeTypes\.register\(\s*""([^""]+)""",
            [System.Text.RegularExpressions.RegexOptions]::Singleline
        )
        foreach ($m in $matches) {
            $key = Normalize-RecipeTypeRef("$cls.$($m.Groups[1].Value)")
            $map[$key] = $m.Groups[2].Value
        }
    }
    return $map
}

function Parse-RecipeBuilderUsage {
    $usage = @{}
    Get-ChildItem $recipeRoot -Recurse -Filter "*.java" | ForEach-Object {
        $text = Get-Text $_.FullName
        $matches = [regex]::Matches($text, "([A-Za-z0-9_\.]+)\s*\.recipeBuilder\(""([^""]+)""\)")
        foreach ($m in $matches) {
            $type = Normalize-RecipeTypeRef($m.Groups[1].Value)
            $id = $m.Groups[2].Value
            if (-not $usage.ContainsKey($type)) {
                $usage[$type] = New-Object System.Collections.Generic.List[string]
            }
            $usage[$type].Add($id)
        }

        # 兼容 helper 封装：build(provider, "hk3gtl_xxx", ...) / buildAbyssController(...)
        $helperMatches = [regex]::Matches($text, '(?:build|buildAbyssController)\(\s*provider\s*,\s*"([^"]+)"')
        foreach ($m in $helperMatches) {
            $id = $m.Groups[1].Value
            if (-not $usage.ContainsKey("GTRecipeTypes.ASSEMBLER_RECIPES")) {
                $usage["GTRecipeTypes.ASSEMBLER_RECIPES"] = New-Object System.Collections.Generic.List[string]
            }
            $usage["GTRecipeTypes.ASSEMBLER_RECIPES"].Add($id)
        }
    }
    return $usage
}

function Parse-MachineRecipeTypes {
    $result = @{}
    Get-ChildItem $machineRoot -Filter "Hk3Machines*.java" | ForEach-Object {
        $lines = Get-Content $_.FullName
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $m = [regex]::Match($line, 'multiblock\("([^"]+)"')
            if (-not $m.Success) { continue }
            $machinePath = $m.Groups[1].Value
            $maxJ = [Math]::Min($i + 40, $lines.Count - 1)
            for ($j = $i; $j -le $maxJ; $j++) {
                $r = [regex]::Match($lines[$j], '\.recipeType\(([A-Za-z0-9_\.]+)\)')
                if ($r.Success) {
                    $result[$machinePath] = Normalize-RecipeTypeRef($r.Groups[1].Value)
                    break
                }
            }
        }
    }
    return $result
}

function Parse-EventMachineRefs {
    $refs = @{}
    Get-ChildItem $eventRoot -Filter "*.java" | ForEach-Object {
        $text = Get-Text $_.FullName
        $matches = [regex]::Matches($text, 'case\s+"([^"]+)"')
        if ($matches.Count -eq 0) { return }
        $set = New-Object System.Collections.Generic.HashSet[string]
        foreach ($m in $matches) {
            $candidate = $m.Groups[1].Value
            if ($candidate -match "^[a-z0-9_]+$") {
                [void]$set.Add($candidate)
            }
        }
        $refs[$_.Name] = @($set)
    }
    return $refs
}

$controllers = Parse-Controllers
$controllerSet = New-Object System.Collections.Generic.HashSet[string]
$controllers | ForEach-Object { [void]$controllerSet.Add($_) }

$recipeTypes = Parse-RecipeTypes
$recipeUsage = Parse-RecipeBuilderUsage
$machineRecipeTypes = Parse-MachineRecipeTypes
$eventRefs = Parse-EventMachineRefs

$assemblerIds = @()
if ($recipeUsage.ContainsKey("GTRecipeTypes.ASSEMBLER_RECIPES")) {
    $assemblerIds = @($recipeUsage["GTRecipeTypes.ASSEMBLER_RECIPES"])
}
$assemblerSet = New-Object System.Collections.Generic.HashSet[string]
$assemblerIds | ForEach-Object { [void]$assemblerSet.Add($_) }

$missingControllerAssembler = @(
    $controllers | Where-Object { -not $assemblerSet.Contains("hk3gtl_$($_)") } | Sort-Object
)

$boundRecipeTypes = New-Object System.Collections.Generic.HashSet[string]
$machineRecipeTypes.Values | ForEach-Object { [void]$boundRecipeTypes.Add($_) }

$recipeTypeUsage = @{}
foreach ($entry in $recipeUsage.GetEnumerator()) {
    if ($entry.Key.StartsWith("Hk3RecipeTypes")) {
        $recipeTypeUsage[$entry.Key] = @($entry.Value)
    }
}

$declaredRecipeTypes = @($recipeTypes.Keys | Sort-Object)
$unusedRecipeTypes = @($declaredRecipeTypes | Where-Object { -not $recipeTypeUsage.ContainsKey($_) })
$orphanRecipeTypes = @(
    $recipeTypeUsage.Keys |
        Where-Object { $recipeTypeUsage[$_].Count -gt 0 -and -not $boundRecipeTypes.Contains($_) } |
        Sort-Object
)

$machineRecipeTypeWithoutRecipes = @(
    $machineRecipeTypes.GetEnumerator() |
        Where-Object { $_.Value.StartsWith("Hk3RecipeTypes") -and -not $recipeTypeUsage.ContainsKey($_.Value) } |
        ForEach-Object { $_.Key } |
        Sort-Object
)

$staleEventRefs = @{}
foreach ($entry in $eventRefs.GetEnumerator()) {
    $stale = @($entry.Value | Where-Object { -not $controllerSet.Contains($_) } | Sort-Object)
    if ($stale.Count -gt 0) {
        $staleEventRefs[$entry.Key] = $stale
    }
}

$report = [ordered]@{
    controllerCount = $controllers.Count
    recipeTypeCount = $declaredRecipeTypes.Count
    machineWithRecipeTypeCount = $machineRecipeTypes.Count
    missingControllerAssemblerRecipes = $missingControllerAssembler
    orphanRecipeTypesWithoutMachine = $orphanRecipeTypes
    recipeTypesDeclaredButNeverUsed = $unusedRecipeTypes
    machineRecipeTypesWithoutRecipes = $machineRecipeTypeWithoutRecipes
    staleEventMachineRefs = $staleEventRefs
}

$jsonPath = Join-Path $root "tools/audit_recipes_report.json"
$txtPath = Join-Path $root "tools/audit_recipes_report.txt"

$json = $report | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($jsonPath, $json, [System.Text.Encoding]::UTF8)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("HK3GTL Recipe Audit Report")
$lines.Add(("=" * 64))
$lines.Add("Controllers: $($report.controllerCount)")
$lines.Add("RecipeTypes: $($report.recipeTypeCount)")
$lines.Add("MachinesWithRecipeType: $($report.machineWithRecipeTypeCount)")
$lines.Add("")

function Append-Section([string]$title, $value) {
    $lines.Add("[$title]")
    if ($value -is [hashtable]) {
        if ($value.Count -eq 0) {
            $lines.Add("- None")
        } else {
            foreach ($k in ($value.Keys | Sort-Object)) {
                $lines.Add("- ${k}: $([string]::Join(', ', $value[$k]))")
            }
        }
    } else {
        if ($null -eq $value -or $value.Count -eq 0) {
            $lines.Add("- None")
        } else {
            foreach ($item in $value) {
                $lines.Add("- $item")
            }
        }
    }
    $lines.Add("")
}

Append-Section "Missing Controller Assembler Recipes" $report.missingControllerAssemblerRecipes
Append-Section "Orphan RecipeTypes Without Machine" $report.orphanRecipeTypesWithoutMachine
Append-Section "RecipeTypes Declared But Never Used" $report.recipeTypesDeclaredButNeverUsed
Append-Section "Machine RecipeTypes Without Recipes" $report.machineRecipeTypesWithoutRecipes
Append-Section "Stale Event Machine References" $report.staleEventMachineRefs

[System.IO.File]::WriteAllLines($txtPath, $lines, [System.Text.Encoding]::UTF8)

Write-Output "Audit completed:"
Write-Output $jsonPath
Write-Output $txtPath
