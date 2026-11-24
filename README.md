# GePeGe

Aplicación de escritorio para aprender a usar GnuPG con una interfaz visual. Está pensada para alumnado de ciclos formativos: muestra el comando usado y el diagnóstico de GPG para relacionar los botones con la terminal.

![Ventana de GePeGe con un ejemplo de cifrado simétrico](assets/GePeGe-cifrar.png)

La consola muestra primero un ejemplo didáctico para la terminal y después el comando real usado por la aplicación. Los nombres `clave.asc`, `mensaje.txt` y los de salida son ejemplos: los archivos de entrada deben existir y las redirecciones de salida pueden sobrescribir archivos; GePeGe pasa el texto por la entrada estándar. El comando real añade opciones de automatización y, cuando es necesario, pasa la contraseña mediante un descriptor privado. La consulta en línea es HTTPS y no ejecuta GPG. La comparación de hashes la realiza GePeGe después de calcularlos con GPG.

## Qué permite hacer

- Cifrar y descifrar mensajes de texto con contraseña o claves públicas/privadas.
- Firmar al cifrar, seleccionando una clave privada; al descifrar, GPG muestra el resultado de la verificación en el diagnóstico.
- Crear pares de claves, consultar el llavero, importar claves y exportar claves públicas en ASCII.
- Consultar información de una clave seleccionada y borrarla tras dos confirmaciones. Si existe su clave privada, se borran tanto la privada como la pública y sus subclaves.
- Consultar por correo o huella completa en keys.openpgp.org directamente desde la aplicación y después importar el resultado.
- Importar mensajes y claves desde archivos de texto, copiar y guardar resultados.
- Elegir el tipo y tamaño de las claves RSA y su caducidad; seleccionar el algoritmo de cifrado del mensaje o dejarlo en automático.
- Calcular y comparar hashes SHA-256, SHA-512 o SHA-1 de cualquier archivo. SHA-1 se incluye únicamente para prácticas con sistemas antiguos.

## Requisitos e instalación en Linux

Se necesita Python 3.10 o superior, GnuPG 2.2 o superior y una sesión gráfica Linux con bibliotecas compatibles con Qt. En Debian/Kali, instala los paquetes de Python, `python3-venv` y `gnupg` con el gestor de paquetes de la distribución. En Arch y derivadas, instala `python` y `gnupg`.

Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

### Ejecutar desde Visual Studio Code

Abre la carpeta `GePeGe` completa en VS Code, instala la extensión de Python de Microsoft y permite que VS Code confíe en la carpeta si aparece esa pregunta. En **Ejecutar y depurar**, elige **GePeGe: abrir aplicación** y pulsa el triángulo verde o `F5`. La configuración usa el Python de `.venv`, que debe estar preparado con los comandos anteriores. Para detener la aplicación, cierra su ventana o utiliza el botón de detener de VS Code.

Ejecutar abre la aplicación desde el código; no genera un AppImage. El empaquetado se explica más abajo.

La ventana utiliza el llavero GPG del usuario actual (`~/.gnupg`, salvo que se defina `GNUPGHOME`). Los comandos se ejecutan localmente; únicamente la consulta de claves necesita conexión a Internet. La contraseña se pasa a GPG mediante un descriptor privado, no en el comando ni en archivos. El comando mostrado representa el descriptor mediante `<descriptor>`; no es directamente copiable tal cual.

## Uso en clase

1. Crea una clave desde **Claves** y comparte únicamente la clave pública exportada.
2. Importa la clave pública de otro alumno y verifica su huella por otro canal.
3. En **Cifrar**, escribe el texto, selecciona cifrado asimétrico y el destinatario. Opcionalmente, selecciona tu clave para firmar.
4. Comparte el resultado. El destinatario lo importa o pega en **Descifrar** y utiliza su contraseña para descifrarlo.
5. Para practicar cifrado simétrico, selecciona esa opción y comparte la contraseña por un canal seguro diferente.

GPG puede rechazar claves públicas importadas si aún no confía en ellas. Verifica siempre la huella y configura la confianza de acuerdo con la práctica y la política del aula. Una firma válida acredita su relación con una clave, pero no verifica por sí sola la identidad de su propietario.

## Limitaciones de esta primera versión

Se admiten mensajes UTF-8 y claves ASCII, no archivos binarios arbitrarios. El cifrado asimétrico usa el modelo de confianza de GPG; no fuerza la aceptación de claves. Al cifrar simétricamente y firmar a la vez se utiliza la misma contraseña para ambas operaciones. Los mensajes y las contraseñas se mantienen temporalmente en memoria durante la operación; no se guardan deliberadamente en archivos de la aplicación. Se exportan claves públicas, no privadas. La búsqueda depende de la disponibilidad y las políticas de publicación del servidor.

## Pruebas

```bash
.venv/bin/python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen .venv/bin/python -c 'from PySide6.QtWidgets import QApplication; from app import Window; a=QApplication([]); w=Window(); w.show(); a.processEvents(); print("Ventana creada")'
```

Las pruebas de GPG crean un llavero temporal y no modifican el llavero personal.

## Organización del proyecto

- `app.py`: ventana, pestañas y acciones de la interfaz.
- `gepege_ui.py`: estilos, iconos y componentes visuales compartidos.
- `gpg_backend.py`: ejecución de GPG y preparación de los comandos didácticos.
- `tests/`: pruebas de las operaciones con llaveros temporales.
- `packaging/`: icono, entrada de escritorio y guion para crear el AppImage.
- `requirements*.txt`: dependencias de ejecución y de compilación.
- `DEPENDENCIAS.md`: referencias para revisar las licencias de componentes externos antes de distribuirlos.
- `AGENTS.md`: indicaciones para asistentes que trabajen en el proyecto.
- `.github/workflows/`: comprobaciones automáticas que GitHub ejecutará cuando se suban cambios o se abra una propuesta.
- `.vscode/`: configuración para abrir la aplicación y ejecutar pruebas desde Visual Studio Code.

La carpeta `.venv` y los archivos generados, incluidos los AppImage, no se incorporan a Git. Consulta [GUIA_GITHUB.md](GUIA_GITHUB.md) para preparar la primera publicación.

## Preparar un AppImage

El guion `packaging/build-appimage.sh` prepara un AppDir con PyInstaller y lo convierte con `appimagetool`, que debe instalarse por separado y estar en `PATH`. La aplicación empaquetada sigue necesitando `gpg` en el sistema. Para compatibilidad amplia, compila en una distribución base suficientemente antigua para los sistemas de destino y prueba el resultado en Kali y otras distribuciones; la compatibilidad no está garantizada por el formato por sí solo.

```bash
.venv/bin/pip install -r requirements-build.txt
./packaging/build-appimage.sh
```

Este repositorio no incluye `appimagetool` ni un AppImage precompilado. Comprueba también los requisitos de FUSE de la distribución donde lo vayas a ejecutar.

Para la versión de prueba se utilizó Ubuntu 22.04 en un contenedor con `packaging/build-ubuntu22-container.sh`. El guion espera el código en `/src` (solo lectura), la carpeta de salida en `/out`, y los archivos oficiales `appimagetool` y el runtime de AppImage en `/tools/appimagetool` y `/tools/runtime`. Instala las dependencias dentro del contenedor; no debe ejecutarse directamente en el sistema anfitrión.

## Estado

Primera versión funcional en desarrollo, 0.1b. La versión AppImage para x86_64 se ha compilado en Ubuntu 22.04; se han ejecutado las pruebas GPG en un contenedor Kali Rolling y comprobado que la ventana arranca allí con una pantalla virtual. Aún falta probar el uso interactivo en una instalación completa de Kali y otras distribuciones.

## Licencia

El código propio de GePeGe se distribuye bajo la [GNU General Public License, versión 3](LICENSE) (GPL-3.0-only). Las dependencias tienen sus propias licencias; consulta [DEPENDENCIAS.md](DEPENDENCIAS.md) antes de distribuir el AppImage.
