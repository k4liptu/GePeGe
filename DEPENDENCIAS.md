# Dependencias y distribución

El código propio de GePeGe se distribuye bajo GPL-3.0-only; consulta [LICENSE](LICENSE). Esa licencia no sustituye a las licencias de las herramientas y bibliotecas utilizadas.

- **PySide6 / Qt** se utiliza para la interfaz y se incluye al generar el AppImage. Qt for Python se ofrece bajo LGPLv3/GPLv3 y licencia comercial, según los componentes y la opción elegida. Antes de distribuir un ejecutable hay que revisar las obligaciones y avisos aplicables a los componentes incluidos. Consulta [Qt for Python](https://doc.qt.io/qtforpython-6/) y [licencias de Qt](https://doc.qt.io/qt-6/licensing.html).
- **GnuPG** realiza las operaciones criptográficas como programa externo; debe estar instalado en el equipo del usuario. Consulta sus [condiciones de licencia](https://www.gnupg.org/copying.html).
- **PyInstaller** se emplea para crear el ejecutable. Su licencia incluye una excepción para los programas empaquetados, que deben respetar las licencias de sus propias dependencias. Consulta la [licencia de PyInstaller](https://www.pyinstaller.org/en/stable/license.html).

Esta descripción orienta la revisión; no certifica que el paquete esté listo para distribuirse ni sustituye la comprobación de las condiciones de las versiones y componentes concretos que incluya cada release.
