# Script completo para iniciar el servidor
# Guarda este archivo como: iniciar_servidor.ps1

param(
    [switch]$Build,     # Si se pasa -Build, reconstruye la imagen
    [switch]$Logs       # Si se pasa -Logs, muestra los logs
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   INICIANDO SERVIDOR - CARNETIZACIÓN SENA " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que Docker Desktop está corriendo
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker Desktop no está corriendo" -ForegroundColor Red
    Write-Host "   Inicia Docker Desktop y vuelve a ejecutar este script" -ForegroundColor Yellow
    exit
}

Write-Host "✅ Docker Desktop está corriendo" -ForegroundColor Green

# 2. Si se especifica -Build, reconstruir la imagen
if ($Build) {
    Write-Host ""
    Write-Host "🔨 Reconstruyendo la imagen..." -ForegroundColor Yellow
    docker-compose build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
        exit
    }
    Write-Host "✅ Imagen construida correctamente" -ForegroundColor Green
}

# 3. Iniciar el contenedor
Write-Host ""
Write-Host "🚀 Iniciando contenedor..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar el contenedor" -ForegroundColor Red
    exit
}

# 4. Esperar 5 segundos para que inicie
Write-Host "⏳ Esperando a que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 5. Verificar que está corriendo
$containerStatus = docker ps --filter "name=carnetizacion_sena" --format "{{.Status}}"

if ($containerStatus -match "Up") {
    Write-Host "✅ Contenedor iniciado correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ El contenedor no pudo iniciar" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Logs del contenedor:" -ForegroundColor Yellow
    docker logs carnetizacion_sena
    exit
}

# 6. Mostrar IPs disponibles
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SERVIDOR LISTO - URLs DE ACCESO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Detectar IPs
$WiFiIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi* -ErrorAction SilentlyContinue).IPAddress
$EthernetIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Ethernet* -ErrorAction SilentlyContinue).IPAddress

Write-Host "💻 Desde este PC:" -ForegroundColor White
Write-Host "   http://localhost:5000" -ForegroundColor Green
Write-Host ""

if ($WiFiIP) {
    Write-Host "📱 Desde celular/tablet (Wi-Fi):" -ForegroundColor White
    Write-Host "   http://$WiFiIP:5000" -ForegroundColor Green
    Write-Host ""
}

if ($EthernetIP) {
    Write-Host "🔌 Desde red cableada:" -ForegroundColor White
    Write-Host "   http://$EthernetIP:5000" -ForegroundColor Green
    Write-Host ""
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 7. Abrir el navegador
Write-Host "🌐 Abriendo navegador..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:5000"

# 8. Mostrar logs si se especifica -Logs
if ($Logs) {
    Write-Host ""
    Write-Host "📋 Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Yellow
    Write-Host ""
    docker-compose logs -f
} else {
    Write-Host ""
    Write-Host "💡 Para ver los logs, ejecuta:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs -f" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🛑 Para detener el servidor, ejecuta:" -ForegroundColor Yellow
    Write-Host "   docker-compose down" -ForegroundColor Cyan
    Write-Host ""
}