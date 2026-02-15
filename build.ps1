[CmdletBinding()]
param (
    [Parameter(Mandatory)][string]$OsFolder,
    [Parameter(Mandatory)][string]$BaseImage,
    [Parameter(Mandatory)][string]$DockerHubUser,

    [string]$Platform = "linux/amd64,linux/arm64",

    [switch]$Push,
    [switch]$Load
)

$RepoRoot = Resolve-Path "."
$Dockerfile = Join-Path $RepoRoot "variants\$OsFolder\$BaseImage\Dockerfile"
$ImageName = "${DockerHubUser}/dovecot:${OsFolder}-${BaseImage}"

if (-not (Test-Path $Dockerfile)) {
    Write-Error "Dockerfile not found for variant '$OsFolder\$BaseImage' at $Dockerfile"
    exit 1
}

try {
    Write-Host "Building image: $ImageName" -ForegroundColor Cyan

    # Validate combinations
    if ($Push -and $Load) {
        throw "You cannot use -Push and -Load together."
    }

    if ($Load -and $Platform -like "*,*") {
        throw "-Load only supports single-platform builds. Use -Push for multi-arch."
    }

    # Determine output flag
    $outputFlag = ""
    if ($Push) {
        $outputFlag = "--push"
    }
    elseif ($Load) {
        $outputFlag = "--load"
    }

    $cmd = @(
        "docker buildx build",
        "--platform $Platform",
        $outputFlag,
        "-f $Dockerfile",
        "-t $ImageName",
        "."
    ) -join " "

    Write-Host "Running: $cmd" -ForegroundColor DarkGray
    Invoke-Expression $cmd

    Write-Host "Successfully built $ImageName" -ForegroundColor Green
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}