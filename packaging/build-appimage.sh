#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v appimagetool >/dev/null; then
  echo 'Falta appimagetool en PATH. Consulta README.md.' >&2
  exit 1
fi
if [[ ! -x .venv/bin/pyinstaller ]]; then
  echo 'Instala primero las dependencias de compilación: .venv/bin/pip install -r requirements-build.txt' >&2
  exit 1
fi
.venv/bin/pyinstaller --noconfirm --clean --windowed --name GePeGe --icon packaging/GePeGe.svg --add-data 'packaging/GePeGe.svg:packaging' app.py
mkdir -p AppDir/usr/bin
cp -a dist/GePeGe/. AppDir/usr/bin/
cp packaging/GePeGe.desktop AppDir/
cp packaging/GePeGe.svg AppDir/
cat > AppDir/AppRun <<'RUN'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/GePeGe" "$@"
RUN
chmod +x AppDir/AppRun
runtime_args=()
if [[ -n "${APPIMAGE_RUNTIME_FILE:-}" ]]; then
  runtime_args=(--runtime-file "$APPIMAGE_RUNTIME_FILE")
fi
output="GePeGe-$(uname -m).AppImage"
temporary=".${output}.$$.tmp"
trap 'rm -f -- "$temporary"' EXIT
ARCH="$(uname -m)" appimagetool "${runtime_args[@]}" AppDir "$temporary"
mv -f -- "$temporary" "$output"
