<#
.SYNOPSIS
    ReytingOLAP (SRAP-2026) ni Railway.com platformasiga deploy qiladi.

.DESCRIPTION
    Loyihaning uchchala servisini (backend, frontend, bot) ketma-ket
    deploy qiladi. Avval railway CLI mavjudligini, autentifikatsiyani
    va loyiha bog'lanishini tekshiradi.

.PARAMETER Project
    Railway loyiha ID si. Default: a4e35fe2-62f0-4bd4-af50-2ac696da98f6

.PARAMETER Skip
    Deploy qilinmaydigan servislar (comma-separated). Masalan: 'bot' yoki 'frontend,bot'

.EXAMPLE
    .\scripts\deploy_railway.ps1
    Hammasini deploy qiladi.

.EXAMPLE
    .\scripts\deploy_railway.ps1 -Skip frontend
    Faqat backend va botni deploy qiladi.
#>

param(
    [string]$Project = "a4e35fe2-62f0-4bd4-af50-2ac696da98f6",
    [string]$Skip = ""
)

$ErrorActionPreference = "Stop"
$skipList = $Skip.Split(',') | ForEach-Object { $_.Trim().ToLower() }

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Write-Ok($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  [ERR] $msg" -ForegroundColor Red }

# 1. CLI tekshiruvi
Write-Step "Railway CLI tekshiruvi"
$cli = Get-Command railway -ErrorAction SilentlyContinue
if (-not $cli) {
    Write-Err "railway CLI topilmadi. O'rnatish: npm i -g @railway/cli"
    exit 1
}
$version = & railway --version 2>&1
Write-Ok "CLI: $version"

# 2. Autentifikatsiya
Write-Step "Autentifikatsiya"
$who = & railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Tizimga kirilmagan. railway login ishga tushiring."
    & railway login
    if ($LASTEXITCODE -ne 0) { exit 1 }
    $who = & railway whoami 2>&1
}
Write-Ok "Login: $who"

# 3. Loyiha bog'lash
Write-Step "Loyiha bog'lash"
$status = & railway status 2>&1
if ($status -notmatch $Project) {
    Write-Warn "Loyiha bog'lanmagan. railway link $Project"
    & railway link $Project
    if ($LASTEXITCODE -ne 0) { exit 1 }
}
Write-Ok "Loyiha: $Project"

# 4. Servislarni deploy qilish
$services = @(
    @{ name = "backend";  path = "backend" },
    @{ name = "frontend"; path = "frontend" },
    @{ name = "bot";      path = "apps/bot" }
)

foreach ($svc in $services) {
    if ($skipList -contains $svc.name) {
        Write-Step "$($svc.name) — o'tkazib yuborildi (--skip)"
        continue
    }
    Write-Step "Deploy: $($svc.name) (`./$($svc.path)`)"
    Push-Location $svc.path
    try {
        & railway up --service $svc.name --detach
        if ($LASTEXITCODE -ne 0) {
            Write-Err "$($svc.name) deploy muvaffaqiyatsiz"
            Pop-Location
            exit $LASTEXITCODE
        }
        Write-Ok "$($svc.name) deploy yuborildi"
    }
    finally {
        Pop-Location
    }
}

# 5. Yakuniy holat
Write-Step "Yakuniy status"
& railway status

Write-Host ""
Write-Host "Deploy yakunlandi. Loglarni kuzatish:" -ForegroundColor Green
Write-Host "  railway logs --service backend" -ForegroundColor Gray
Write-Host "  railway logs --service frontend" -ForegroundColor Gray
Write-Host "  railway logs --service bot" -ForegroundColor Gray
Write-Host ""
Write-Host "Dashboard: https://railway.com/project/$Project" -ForegroundColor Cyan
