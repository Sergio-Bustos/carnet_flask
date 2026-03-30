# Script para obtener la IP actual del PC
# Guarda este archivo como: obtener_ip.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SISTEMA DE CARNETIZACIÓN SENA - DOCKER  " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Detectar IP del adaptador Wi-Fi
$WiFiIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi* -ErrorAction SilentlyContinue).IPAddress

# Detectar IP del adaptador Ethernet
$EthernetIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Ethernet* -ErrorAction SilentlyContinue).IPAddress

# Detectar IP de hotspot móvil
$HotspotIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Local* -ErrorAction SilentlyContinue).IPAddress

Write-Host "🔍 Direcciones IP detectadas:" -ForegroundColor Yellow
Write-Host ""

if ($WiFiIP) {
    Write-Host "  📶 Wi-Fi:     " -NoNewline -ForegroundColor White
    Write-Host "http://$WiFiIP:5000" -ForegroundColor Green
}

if ($EthernetIP) {
    Write-Host "  🔌 Ethernet:  " -NoNewline -ForegroundColor White
    Write-Host "http://$EthernetIP:5000" -ForegroundColor Green
}

if ($HotspotIP) {
    Write-Host "  📱 Hotspot:   " -NoNewline -ForegroundColor White
    Write-Host "http://$HotspotIP:5000" -ForegroundColor Green
}

Write-Host ""
Write-Host "  💻 Localhost: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Copia la URL que corresponde a tu red activa" -ForegroundColor Yellow
Write-Host ""

# Verificar si Docker está corriendo
$dockerStatus = docker ps -a --filter "name=carnetizacion_sena" --format "{{.Status}}"

if ($dockerStatus -match "Up") {
    Write-Host "✅ El contenedor está corriendo" -ForegroundColor Green
} else {
    Write-Host "⚠️  El contenedor NO está corriendo" -ForegroundColor Red
    Write-Host "   Ejecuta: docker-compose up -d" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")