param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("mysql", "postgresql", "mongodb", "couchdb", "neo4j", "memgraph")]
    [string]$Engine,

    [Parameter(Mandatory = $true)]
    [ValidateSet("up", "down", "clean", "status", "smoke")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Compose = Join-Path $Root "docker\compose.yaml"
$EnvFile = Join-Path $Root ".env"

if (-not (Test-Path $EnvFile)) {
    throw "Falta archivo .env en $Root. Copie .env.example a .env y configure las contraseñas."
}

$ExpectedContainer = "biolink-bench-$Engine"

switch ($Action) {
    "up" {
        $running = docker ps --filter "name=biolink-bench-" --format "{{.Names}}"
        $others = @($running | Where-Object { $_ -and $_ -ne $ExpectedContainer })
        if ($others.Count -gt 0) {
            throw "Hay otro motor activo ($($others -join ', ')). Deténgalo primero para respetar la ejecución secuencial."
        }
        docker compose --env-file $EnvFile -f $Compose --profile $Engine up -d --wait
    }
    "down" {
        docker compose --env-file $EnvFile -f $Compose --profile $Engine down
    }
    "clean" {
        Write-Warning "Se eliminarán el contenedor y el volumen de datos de '$Engine'."
        docker compose --env-file $EnvFile -f $Compose --profile $Engine down -v
    }
    "status" {
        docker ps -a --filter "name=$ExpectedContainer"
    }
    "smoke" {
        $Py = Join-Path $Root ".venv\Scripts\python.exe"
        if (-not (Test-Path $Py)) { $Py = "python" }
        & $Py -m biolink_bench smoke --engine $Engine
    }
}
