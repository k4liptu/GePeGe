# Instrucciones para trabajar en GePeGe

- GePeGe es una aplicación de escritorio educativa para alumnado de ciclos formativos. No convertirla en una aplicación web.
- Mantener la interfaz y la documentación en castellano claro. Mostrar los comandos GPG y los errores útiles sin mostrar contraseñas ni datos secretos.
- Ejecutar GPG con argumentos separados, sin shell. No guardar contraseñas, claves privadas ni mensajes de ejemplo sensibles en el repositorio.
- Respetar el llavero del usuario. Las pruebas deben usar siempre un `GNUPGHOME` temporal aislado.
- Mantener compatibilidad con Linux moderno y el flujo de empaquetado AppImage. Documentar las dependencias externas y las limitaciones reales.
- Después de modificar operaciones criptográficas, ejecutar las pruebas de integración y comprobar la interfaz en modo sin pantalla cuando sea posible.
