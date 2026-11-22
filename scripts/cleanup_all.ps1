param(
    [switch]$RemoveVolumes,
    [switch]$RemoveResults
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Compose = Join-Path $Root "docker\compose.yaml"
$EnvFile = Join-Path $Root ".env"
$FallbackEnv = Join-Path $Root ".env.example"

$Profiles = @("mysql", "postgresql", "mongodb", "couchdb", "neo4j", "memgraph")

foreach ($p in $Profiles) {
    $argsList = @("compose")
    if (Test-Path $EnvFile) {
        $argsList += @("--env-file", $EnvFile)
    } elseif (Test-Path $FallbackEnv) {
        $argsList += @("--env-file", $FallbackEnv)
    }
    $argsList += @("-f", $Compose, "--profile", $p, "down")
    if ($RemoveVolumes) {
        $argsList += "-v"
    }
    & docker @argsList | Out-Null
}

if ($RemoveResults) {
    Write-Warning "Eliminando archivos generados en results/ y reports/ (conservando .gitkeep y README.md)..."
    foreach ($dir in @("results\raw", "results\logs", "results\summaries", "reports")) {
        $fullDir = Join-Path $Root $dir
        if (Test-Path $fullDir) {
            Get-ChildItem $fullDir -File | Where-Object { $_.Name -notin @(".gitkeep", "README.md") } | Remove-Item -Force
        }
    }
}

Write-Output "Limpieza completada (RemoveVolumes=$RemoveVolumes, RemoveResults=$RemoveResults)."
