# GePeGe 0.1b — primera versión de prueba

GePeGe es una aplicación de escritorio para aprender a utilizar GnuPG con una interfaz visual en castellano. Esta primera versión permite cifrar y descifrar mensajes simétricos o asimétricos, firmar mensajes, gestionar claves y calcular hashes de archivos. Incluye explicaciones y muestra ejemplos de comandos y las operaciones realizadas por GPG.

## Descarga y ejecución

El archivo `GePeGe-x86_64.AppImage` está destinado a Linux de 64 bits x86_64. Tras descargarlo, dale permiso de ejecución y ábrelo:

```bash
chmod +x GePeGe-x86_64.AppImage
./GePeGe-x86_64.AppImage
```

Necesitas GnuPG (`gpg`) instalado. El paquete se ha compilado en Ubuntu 22.04. Se han ejecutado las pruebas GPG del código en un contenedor Kali Rolling y comprobado el arranque del AppImage con pantalla virtual; también se ha probado el arranque sin pantalla en Debian 12. No se ha comprobado todavía el uso interactivo en una instalación completa de Kali y podría no funcionar en otros sistemas. El archivo `GePeGe-x86_64.AppImage.sha256` permite comprobar la integridad de la descarga con `sha256sum -c GePeGe-x86_64.AppImage.sha256` en la carpeta que contenga ambos archivos.

## Limitaciones conocidas

- Es una versión de prueba; úsala primero con claves y datos de práctica.
- Utiliza el llavero GPG del usuario actual. Si borras una clave privada, la aplicación pide dos confirmaciones.
- El cifrado trabaja con mensajes de texto UTF-8, no con archivos binarios arbitrarios. La pestaña Hash sí admite archivos binarios.
- Para cifrar y firmar simultáneamente en modo simétrico se usa la misma contraseña para ambas operaciones.
- La búsqueda de claves depende de keys.openpgp.org y necesita Internet. Verifica las huellas por otro canal.
- El código propio está bajo GPL v3; las dependencias tienen sus propias licencias, descritas en `DEPENDENCIAS.md`.
