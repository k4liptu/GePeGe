# Decisiones y comprobaciones de GePeGe

## Versión 0.2

- La generación de pares y el almacén de claves tienen pestañas separadas. Las confirmaciones de generación e importación indican dónde consultar el almacén. La exportación de claves públicas se hace desde cada fila y utiliza un diálogo para elegir archivo.
- Una clave importada puede ser válida para cifrar aunque GPG aún no confíe en su identidad. Si no hay confianza plena, se pide comprobar la huella y confirmar su uso para ese mensaje; `--trust-model always` solo se aplica a esa operación y no modifica la confianza del llavero. GPG debe seguir rechazando claves caducadas, revocadas o no aptas.
- El algoritmo del mensaje se muestra en cifrado simétrico y asimétrico porque este último también cifra el contenido mediante una clave de sesión simétrica. La contraseña solo aparece para cifrado simétrico o firma.
- El AppImage compilado en Ubuntu puede buscar certificados en una ruta ausente en otras distribuciones. Si el contexto TLS predeterminado no carga autoridades, se utiliza el almacén de certificados del sistema. Nunca desactivar la verificación del servidor HTTPS. Mantener las pruebas de este comportamiento.
- La opción de actualizaciones abre la página de versiones: no instala ni sustituye el AppImage automáticamente.

## Antes de publicar

- Ejecutar las pruebas de integración con llaveros temporales y comprobar la interfaz sin pantalla. Probar la búsqueda real, la importación y la exportación con datos públicos y un `GNUPGHOME` aislado.
- Compilar el AppImage en Ubuntu 22.04 con el guion documentado. Comprobar el arranque y las operaciones GPG en contenedores Debian, Kali y Arch cuando estén disponibles; esto no sustituye las pruebas interactivas en instalaciones completas.
- Calcular y verificar la suma SHA-256, comprobar que los archivos subidos coinciden y que la etiqueta de la release apunta al código utilizado. Si se sustituye una versión existente por petición expresa, comunicar que quienes ya la descargaron deben volver a hacerlo.
- Los cambios locales no modifican un AppImage ya compilado. No anunciar una release actualizada hasta comprobar el código, el paquete y los archivos publicados.
