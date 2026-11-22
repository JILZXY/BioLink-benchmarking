param(
    [switch]$RequireEnv
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    $Py = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $Py)) {
        $Py = "python"
    }
    if ($RequireEnv) {
        & $Py -m biolink_bench check-config --require-env
    } else {
        & $Py -m biolink_bench check-config
    }
    & $Py -m biolink_bench verify-fixture
} finally {
    Pop-Location
}
