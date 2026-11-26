# Instala Gpg4win mediante el gestor de paquetes de Windows.
$ErrorActionPreference = 'Stop'
Write-Host 'GePeGe necesita GnuPG. Se instalará Gpg4win mediante winget.'
Write-Host 'La instalación puede solicitar permisos de administrador.'
$confirmacion = Read-Host '¿Deseas continuar? Escribe SI para confirmar'
if ($confirmacion -ne 'SI') { Write-Host 'Instalación cancelada.'; exit 0 }
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host 'No se encontró winget. Instala Gpg4win desde https://www.gpg4win.org/download.html'
    exit 1
}
winget install --id GnuPG.Gpg4win --exact --interactive --accept-source-agreements
if ($LASTEXITCODE -ne 0) { throw "winget terminó con el código $LASTEXITCODE" }
Write-Host 'Gpg4win instalado. Abre GePeGe de nuevo.'
