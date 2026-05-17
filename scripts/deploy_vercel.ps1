<#
.SYNOPSIS
    ReytingOLAP frontend'ini Vercel'ga deploy qiladi.

.PARAMETER BackendUrl
    Backend API root URL. Misol: https://backend.up.railway.app
    Bu URL'ga /api/v1 qo'shiladi va VITE_API_BASE_URL'ga yoziladi.

.PARAMETER Production
    True bo'lsa --prod flag bilan deploy (default true).

.EXAMPLE
    .\scripts\deploy_vercel.ps1 -BackendUrl "https://backend.up.railway.app"

.EXAMPLE
    .\scripts\deploy_vercel.ps1 -BackendUrl "https://backend.up.railway.app" -Production:$false
    Preview deploy qiladi.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl,

    [bool]$Production = $true
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}
function Write-Ok($m)   { Write-Host "  [OK] $m"   -ForegroundColor Green }
function Write-Warn($m) { Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Write-Err($m)  { Write-Host "  [ERR] $m"  -ForegroundColor Red }

# URL normalizatsiyasi
$BackendUrl = $BackendUrl.TrimEnd('/')
if ($BackendUrl -notmatch '^https?://') {
    Write-Err "BackendUrl https:// yoki http:// bilan boshlanishi shart"
    exit 1
}
$apiBase = "$BackendUrl/api/v1"

# 1. CLI tekshiruvi
Write-Step "Vercel CLI tekshiruvi"
$cli = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $cli) {
    Write-Warn "vercel CLI topilmadi. Hozir o'rnatamiz..."
    npm i -g vercel
    if ($LASTEXITCODE -ne 0) {
        Write-Err "vercel CLI o'rnatishda xato"
        exit 1
    }
}
$version = vercel --version
Write-Ok "CLI: v$version"

# 2. Frontend papkaga o'tish
$root = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $root "frontend"
if (-not (Test-Path $frontend)) {
    Write-Err "Frontend papkasi topilmadi: $frontend"
    exit 1
}
Push-Location $frontend
try {
    Write-Step "Frontend papka: $frontend"

    # 3. Autentifikatsiya
    $who = vercel whoami 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Tizimga kirilmagan. vercel login ishga tushiring."
        vercel login
        if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }
        $who = vercel whoami
    }
    Write-Ok "Login: $who"

    # 4. Loyiha link
    if (-not (Test-Path ".vercel/project.json")) {
        Write-Step "Loyiha hali bog'lanmagan. vercel link ishga tushiring..."
        vercel link
        if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }
    }
    Write-Ok "Loyiha bog'langan"

    # 5. Env variable o'rnatish (idempotent: avval o'chirib, qayta qo'shish)
    Write-Step "Env: VITE_API_BASE_URL = $apiBase"
    $envScopes = if ($Production) { @("production", "preview") } else { @("preview") }
    foreach ($scope in $envScopes) {
        vercel env rm VITE_API_BASE_URL $scope --yes 2>$null | Out-Null
        $apiBase | vercel env add VITE_API_BASE_URL $scope | Out-Null
        Write-Ok "Env yangilandi ($scope)"
    }

    # 6. Deploy
    Write-Step "Deploy boshlanmoqda..."
    if ($Production) {
        vercel --prod --yes
    } else {
        vercel --yes
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Err "Deploy muvaffaqiyatsiz tugadi"
        Pop-Location
        exit $LASTEXITCODE
    }

    Write-Step "Deploy tugadi!"
    Write-Host ""
    Write-Host "Keyingi qadamlar:" -ForegroundColor Green
    Write-Host "  1. Vercel domeningizni nusxalang (yuqorida chiqdi)" -ForegroundColor Gray
    Write-Host "  2. Railway backend'ga env qo'shing:" -ForegroundColor Gray
    Write-Host "     CORS_ORIGINS=https://<vercel-domain>" -ForegroundColor Gray
    Write-Host "  3. Backend qayta deploy: railway up --service backend" -ForegroundColor Gray
}
finally {
    Pop-Location
}
