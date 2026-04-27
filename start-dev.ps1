# 可爱便签 - 开发模式启动脚本
# 使用方法: .\start-dev.ps1

Write-Host "🍀 可爱便签 - 开发模式" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

# 检查图标文件
$iconsDir = Join-Path $PSScriptRoot "src-tauri\icons"
$icon32 = Join-Path $iconsDir "32x32.png"
$icon128 = Join-Path $iconsDir "128x128.png"

if (-not (Test-Path $icon32)) {
    Write-Host "⚠️  缺少图标文件!" -ForegroundColor Yellow
    Write-Host "📝 请创建以下图标文件:" -ForegroundColor Yellow
    Write-Host "   - $icon32" -ForegroundColor Yellow
    Write-Host "   - $icon128 (可选)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 快速创建图标方法:" -ForegroundColor Cyan
    Write-Host "   方法1: 使用Python创建 (推荐)" -ForegroundColor White
    Write-Host "          运行: python create-icons.py" -ForegroundColor White
    Write-Host ""
    Write-Host "   方法2: 使用画图工具创建32x32 PNG图片" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ 图标文件检查通过" -ForegroundColor Green

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到Python!" -ForegroundColor Red
    exit 1
}

# 检查Rust
try {
    $rustVersion = rustc --version 2>&1
    Write-Host "✅ Rust: $rustVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到Rust!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 即将启动开发模式..." -ForegroundColor Green
Write-Host "📍 前端服务器: http://localhost:1420" -ForegroundColor Cyan
Write-Host "⏳ 首次启动需要下载依赖，请耐心等待..." -ForegroundColor Yellow
Write-Host ""

# 启动Tauri开发模式
Set-Location $PSScriptRoot
cargo tauri dev
