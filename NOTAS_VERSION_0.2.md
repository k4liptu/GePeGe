# GePeGe 0.2

Esta revisión organiza la gestión de claves y mejora el cifrado con claves públicas importadas.

- El almacén reúne la consulta, búsqueda, importación y exportación de claves; la generación tiene su propia pestaña.
- Al cifrar con una clave cuya identidad GPG no considera plenamente confiable, se muestra la huella y se solicita confirmación para ese mensaje. Comprueba la huella con su propietario por un canal independiente. La confianza del llavero no se modifica.
- La exportación de claves públicas permite elegir el archivo y su ubicación.
- El campo de contraseña aparece cuando se necesita para cifrado simétrico o firma.
- El menú Ayuda permite consultar las versiones publicadas. La actualización es manual.

GePeGe necesita GnuPG instalado y utiliza el llavero del usuario. Cifra mensajes de texto UTF-8, no archivos binarios arbitrarios. Consulta el README y DEPENDENCIAS.md para conocer los requisitos y limitaciones.

Para ejecutar el AppImage en Linux x86_64, dale permiso de ejecución con `chmod +x GePeGe-0.2-x86_64.AppImage` y ábrelo. Comprueba la descarga con `sha256sum -c GePeGe-0.2-x86_64.AppImage.sha256` desde la carpeta donde estén ambos archivos.
