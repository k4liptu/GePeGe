#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
# Ejecutar únicamente dentro de un contenedor Ubuntu 22.04; ver README.md.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip patchelf fuse3 libegl1 libgl1 file libdbus-1-3 libxkbcommon0 libglib2.0-0 libxcb-shape0 libxcb-cursor0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-image0 libxcb-render-util0 libx11-xcb1
mkdir /work
cp /src/app.py /src/gepege_ui.py /src/gpg_backend.py /src/requirements-build.txt /src/requirements.txt /src/LICENSE /work/
cp -a /src/packaging /work/
cd /work
python3 -m venv .venv
.venv/bin/pip install -q -r requirements-build.txt
.venv/bin/python -c "from PySide6.QtCore import QLibraryInfo; print(QLibraryInfo.version().toString())"
.venv/bin/pyinstaller --noconfirm --clean --windowed --name GePeGe --icon packaging/GePeGe.svg --add-data 'packaging/GePeGe.svg:packaging' --add-data 'LICENSE:.' app.py
mkdir -p AppDir/usr/bin
cp -a dist/GePeGe/. AppDir/usr/bin/
cp packaging/GePeGe.desktop packaging/GePeGe.svg LICENSE AppDir/
printf '%s\n' '#!/bin/sh' 'HERE="$(dirname "$(readlink -f "$0")")"' 'exec "$HERE/usr/bin/GePeGe" "$@"' > AppDir/AppRun
chmod +x AppDir/AppRun
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 /tools/appimagetool --runtime-file /tools/runtime AppDir /out/GePeGe-x86_64.AppImage
chown --reference=/out /out/GePeGe-x86_64.AppImage
