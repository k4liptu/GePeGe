# Primera publicación de GePeGe en GitHub

Git guarda el historial de cambios en tu ordenador. GitHub aloja una copia en Internet. Un **commit** es una versión guardada en Git; **push** envía esos commits a GitHub. El proyecto utiliza la rama `main`: puedes consultar su estado con `git status` y su historial con `git log --oneline`.

## 1. Antes de publicar

Decide si el repositorio será **privado** (acceso limitado) o **público** (cualquiera podrá ver el código). GePeGe utiliza la licencia GPL v3 para su código propio; los componentes externos tienen sus propias condiciones.

El archivo `.gitignore` excluye el entorno virtual, los AppImage y extensiones habituales de claves. Comprueba igualmente los archivos antes de subirlos: no incluyas contraseñas, claves privadas, datos de alumnos ni mensajes reales. El llavero personal está fuera del proyecto y no forma parte del repositorio.

## 2. Revisar los cambios locales

El proyecto ya tiene commits locales. Para consultar si hay cambios pendientes:

```bash
cd ~/Proyectos/GePeGe
git status
```

En VS Code puedes ver los archivos modificados en **Control de código fuente**. Cuando hagas nuevos cambios y quieras guardar una versión, puedes usar esa vista o los comandos siguientes:

En una terminal:

```bash
cd ~/Proyectos/GePeGe
git status
git add .
git diff --cached --stat
git diff --cached
git commit -m "Describe aquí los cambios"
```

Revisa la salida de los dos comandos `git diff` antes del commit; pulsa `q` para salir del visor si aparece. Git puede solicitar un nombre y correo de autor si no están configurados. Estos datos quedan en el historial de los commits y se compartirán si publicas el repositorio.

## 3. Crear o conectar el repositorio en GitHub

Si aún no existe un repositorio para GePeGe, puedes usar **Publicar en GitHub** en la vista Control de código fuente de VS Code y escoger el nombre y la visibilidad. Si ya existe, usa su dirección como remoto. Para crearlo manualmente en GitHub, elige un repositorio vacío, sin añadir allí un README, `.gitignore` ni licencia; el proyecto ya los incluye.

GitHub mostrará la dirección del repositorio. Con esa dirección, desde la carpeta del proyecto:

```bash
git remote add origin DIRECCION_DEL_REPOSITORIO
git push -u origin main
```

Sustituye `DIRECCION_DEL_REPOSITORIO` por la dirección HTTPS o SSH que muestre GitHub. Para enviar cambios tendrás que autenticarte con un método compatible con GitHub. Consulta la [guía oficial para añadir código local](https://docs.github.com/es/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=linux) y la [documentación de autenticación](https://docs.github.com/es/authentication/keeping-your-account-and-data-secure/about-authentication-to-github).

## 4. Cambios posteriores

Después de modificar archivos, revisa `git status` y `git diff`, prepara los cambios con `git add`, crea un nuevo commit y ejecuta `git push`. Un repositorio público permite leer su contenido; cambiarlo requiere permisos.

El AppImage está excluido de Git. Si más adelante quieres ofrecer un ejecutable a los alumnos, puedes crear una versión en GitHub y adjuntarlo como archivo de una [publicación (release)](https://docs.github.com/es/repositories/releasing-projects-on-github/about-releases). Antes de distribuirlo, pruébalo en las distribuciones y arquitecturas que vayan a usar.
