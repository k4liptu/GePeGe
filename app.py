#!/usr/bin/env python3
"""GePeGe: laboratorio visual de GnuPG para Linux."""
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPalette
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QScrollArea, QSizePolicy, QSplitter, QTabWidget, QToolButton, QVBoxLayout, QWidget)
from gpg_backend import execute

from gepege_ui import APP_ICON, STYLE, KeyRow, Task, button, label, password, tab_icon, textedit

class Window(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('GePeGe — aprende GPG'); self.setWindowIcon(QIcon(str(APP_ICON))); self.resize(1150, 850)
        self.pool = QThreadPool.globalInstance(); self.tasks = set(); self.public = []; self.secret = []
        root = QWidget(); self.setCentralWidget(root); layout = QVBoxLayout(root)
        title = QLabel('GePeGe   ·   Laboratorio de criptografía'); title.setStyleSheet('font-size: 22px; font-weight: bold; color: #193966;'); layout.addWidget(title)
        layout.addWidget(label('Practica con mensajes y claves. Cada operación muestra el comando de GPG y su diagnóstico.'))
        split = QSplitter(); layout.addWidget(split, 1)
        self.tabs = QTabWidget(); split.addWidget(self.tabs)
        self.tabs.addTab(self.scroll(self.encrypt_page()), 'Cifrar'); self.tabs.addTab(self.scroll(self.decrypt_page()), 'Descifrar')
        self.tabs.addTab(self.scroll(self.keys()), 'Claves'); self.tabs.addTab(self.scroll(self.hash_page()), 'Hash'); self.tabs.addTab(self.scroll(self.help_page()), 'Aprende')
        self.tabs.currentChanged.connect(self.update_tab_icons); self.update_tab_icons()
        split.addWidget(self.results()); split.setSizes([650, 450]); self.create_menus(); self.refresh()
    def update_tab_icons(self, *_):
        for index in range(self.tabs.count()): self.tabs.setTabIcon(index, tab_icon(index, index == self.tabs.currentIndex()))
    def create_menus(self):
        bar = self.menuBar()
        archive = bar.addMenu('&Archivo')
        save = QAction('Guardar resultado…', self); save.setShortcut('Ctrl+S'); save.triggered.connect(self.save); archive.addAction(save)
        archive.addSeparator(); close = QAction('Salir', self); close.setShortcut('Ctrl+Q'); close.triggered.connect(self.close); archive.addAction(close)
        view = bar.addMenu('&Ver')
        for index, name in enumerate(('Cifrar', 'Descifrar', 'Claves', 'Hash', 'Aprende')):
            action = QAction(name, self); action.triggered.connect(lambda checked=False, i=index: self.tabs.setCurrentIndex(i)); view.addAction(action)
        tools = bar.addMenu('&Herramientas')
        refresh = QAction('Actualizar llavero', self); refresh.triggered.connect(lambda: self.refresh()); tools.addAction(refresh)
        help_menu = bar.addMenu('Ay&uda')
        guide = QAction('Guía de aprendizaje', self); guide.triggered.connect(lambda: self.tabs.setCurrentIndex(4)); help_menu.addAction(guide)
        about = QAction('Acerca de GePeGe', self); about.triggered.connect(self.about); help_menu.addAction(about)
    def about(self):
        QMessageBox.about(self, 'Acerca de GePeGe', 'GePeGe · versión 0.1b\nRGP 2026\n\nUna aplicación educativa de escritorio para aprender a utilizar GnuPG.\n\nLas operaciones criptográficas las realiza GPG; consulta la consola para ver los comandos y resultados.')
    def scroll(self, w):
        s = QScrollArea(); s.setWidgetResizable(True); s.setWidget(w); return s
    def encrypt_page(self):
        w=QWidget(); v=QVBoxLayout(w)
        v.addWidget(label('Escribe o importa el texto que quieres proteger y elige el tipo de cifrado.'))
        self.encrypt_message=textedit('Escribe aquí el mensaje que quieres cifrar…', 170); v.addWidget(self.encrypt_message)
        h=QHBoxLayout(); h.addWidget(button('Importar mensaje…', lambda: self.load_file(self.encrypt_message))); h.addWidget(button('Limpiar', self.encrypt_message.clear)); v.addLayout(h)
        self.encrypt_form=QFormLayout(); self.mode=QComboBox(); self.mode.addItem('Asimétrico — clave pública', 'asymmetric'); self.mode.addItem('Simétrico — contraseña', 'symmetric'); self.mode.currentIndexChanged.connect(self.mode_changed)
        self.recipient=QComboBox(); self.signer=QComboBox(); self.encrypt_pass=password(); self.cipher=QComboBox()
        for title, value in [('Automático — recomendado', 'default'), ('AES-128', 'AES128'), ('AES-256', 'AES256')]: self.cipher.addItem(title, value)
        self.encrypt_form.addRow('Tipo de cifrado', self.mode); self.encrypt_form.addRow('Clave del destinatario', self.recipient); self.encrypt_form.addRow('Algoritmo del mensaje', self.cipher); self.encrypt_form.addRow('Firmar con (opcional)', self.signer); self.encrypt_form.addRow('Contraseña', self.encrypt_pass); v.addLayout(self.encrypt_form)
        v.addWidget(label('En el cifrado asimétrico, la clave del destinatario protege una clave de sesión; AES cifra el mensaje. El modo automático elige un algoritmo compatible.'))
        v.addWidget(label('La contraseña protege el mensaje simétrico o desbloquea la clave privada. Para cifrar y firmar en una sola operación se usa la misma contraseña para ambos.'))
        v.addWidget(button('Cifrar mensaje', lambda: self.message_action('encrypt'), True)); v.addStretch(); return w
    def decrypt_page(self):
        w=QWidget(); v=QVBoxLayout(w)
        v.addWidget(label('Pega o importa el mensaje cifrado. GPG detectará cómo se cifró y, si tiene firma, intentará verificarla.'))
        self.decrypt_message=textedit('Pega aquí el mensaje cifrado…', 170); v.addWidget(self.decrypt_message)
        h=QHBoxLayout(); h.addWidget(button('Importar mensaje cifrado…', lambda: self.load_file(self.decrypt_message))); h.addWidget(button('Limpiar', self.decrypt_message.clear)); v.addLayout(h)
        form=QFormLayout(); self.decrypt_pass=password(); form.addRow('Contraseña', self.decrypt_pass); v.addLayout(form)
        v.addWidget(label('Introduce la contraseña del mensaje simétrico o la de tu clave privada. Consulta el diagnóstico para comprobar la firma.'))
        v.addWidget(button('Descifrar mensaje', lambda: self.message_action('decrypt'), True)); v.addStretch(); return w
    def keys(self):
        w=QWidget(); v=QVBoxLayout(w); v.addWidget(label('El llavero pertenece al usuario actual. Comprueba las huellas por un canal independiente.'))
        self.key_list=QListWidget(); self.key_list.setMinimumHeight(120); v.addWidget(self.key_list)
        self.key_list.itemSelectionChanged.connect(self.update_key_rows)
        v.addWidget(button('Actualizar claves', self.refresh))
        g=QGroupBox('Crear un par de claves'); f=QFormLayout(g); self.name=QLineEdit(); self.email=QLineEdit(); self.key_pass=password(); self.key_algorithm=QComboBox(); self.expiry=QComboBox()
        for title, value in [('Predeterminado de GPG — recomendado', 'default'), ('RSA · 2048 bits', 'rsa2048'), ('RSA · 3072 bits', 'rsa3072'), ('RSA · 4096 bits', 'rsa4096')]: self.key_algorithm.addItem(title, value)
        for title, value in [('2 años', '2y'), ('1 año', '1y'), ('5 años', '5y'), ('Sin caducidad', '0')]: self.expiry.addItem(title, value)
        f.addRow('Nombre', self.name); f.addRow('Correo (opcional)', self.email); f.addRow('Contraseña', self.key_pass); f.addRow('Tipo y tamaño de clave', self.key_algorithm); f.addRow('Caducidad', self.expiry)
        f.addRow(label('GPG crea el par y las subclaves que correspondan. La caducidad limita la validez de la clave; puede modificarse después con GPG.')); f.addRow(button('Crear claves', self.generate, True)); v.addWidget(g)
        g=QGroupBox('Consultar keys.openpgp.org'); f=QFormLayout(g); self.lookup=QLineEdit(); self.lookup.setPlaceholderText('Correo electrónico o huella completa'); f.addRow('Buscar', self.lookup); f.addRow(label('Descarga la clave encontrada a la caja de importación. Verifica siempre su huella antes de confiar en ella.')); f.addRow(button('Buscar clave', self.search)); v.addWidget(g)
        g=QGroupBox('Importar y exportar'); a=QVBoxLayout(g); self.key_text=textedit('Pega una clave en formato ASCII…'); a.addWidget(self.key_text); h=QHBoxLayout(); h.addWidget(button('Abrir archivo…', lambda: self.load_file(self.key_text))); h.addWidget(button('Importar clave', self.import_key)); a.addLayout(h); self.export_key=QComboBox(); a.addWidget(self.export_key); a.addWidget(button('Exportar clave pública', self.export)); v.addWidget(g); v.addStretch(); return w
    def hash_page(self):
        w=QWidget(); v=QVBoxLayout(w)
        v.addWidget(label('Calcula la huella digital de cualquier archivo y compárala con un valor conocido. El archivo se lee, pero no se modifica.'))
        form=QFormLayout(); self.hash_file=QLineEdit(); self.hash_file.setReadOnly(True); self.hash_file.setPlaceholderText('Selecciona un archivo…')
        h=QHBoxLayout(); h.addWidget(self.hash_file); h.addWidget(button('Elegir archivo…', self.choose_hash_file)); form.addRow('Archivo', h)
        self.hash_algorithm=QComboBox()
        for title, value in [('SHA-256 — recomendado', 'SHA256'), ('SHA-512', 'SHA512'), ('SHA-1 — solo prácticas antiguas', 'SHA1')]: self.hash_algorithm.addItem(title, value)
        form.addRow('Algoritmo', self.hash_algorithm); self.hash_expected=QLineEdit(); self.hash_expected.setPlaceholderText('Opcional: pega el hash con el que comparar'); form.addRow('Hash esperado', self.hash_expected); v.addLayout(form)
        v.addWidget(label('SHA-1 está obsoleto para comprobar seguridad. Una coincidencia verifica la integridad frente al valor comparado, no la identidad de quien lo publicó.'))
        v.addWidget(button('Calcular y comprobar hash', self.calculate_hash, True)); v.addStretch(); return w
    def choose_hash_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo para calcular su hash')
        if filename: self.hash_file.setText(filename)
    def calculate_hash(self):
        self.call({'action':'hash', 'filename':self.hash_file.text(), 'algorithm':self.hash_algorithm.currentData(), 'expected':self.hash_expected.text()})
    def help_page(self):
        w=QWidget(); v=QVBoxLayout(w)
        v.addWidget(label('Abre cada apartado para conocer los conceptos y seguir una práctica paso a paso.'))
        lessons = [
            ('1. GPG y el llavero', 'GPG es la herramienta que realiza las operaciones. GePeGe prepara sus argumentos y muestra el comando en la consola.\n\nEl llavero guarda las claves del usuario. Una clave pública se puede compartir; la clave privada debe protegerse y mantenerse en secreto.'),
            ('2. Cifrado simétrico', 'Emisor y destinatario utilizan la misma contraseña.\n\nPráctica: en Cifrar elige «Simétrico», escribe un mensaje y una contraseña. Envía el resultado a Descifrar e introduce la misma contraseña. Comparte la contraseña por un canal diferente del mensaje.'),
            ('3. Claves y cifrado asimétrico', 'Cada persona dispone de una clave pública y una privada. Para enviar un mensaje a otra persona se cifra con su clave pública; ella lo descifra con su clave privada.\n\nPráctica: crea una clave en Claves, exporta la parte pública y compártela. Importa la clave pública del destinatario, selecciónala en Cifrar y envíale el resultado. La clave privada nunca debe compartirse.'),
            ('4. Firma y verificación', 'Una firma se crea con la clave privada del firmante. GPG puede verificarla con la clave pública correspondiente y detectar si el mensaje ha cambiado.\n\nEn Cifrar, selecciona una clave en «Firmar con». Al descifrar, consulta el diagnóstico. Una firma válida vincula el mensaje a la clave; para conocer al propietario hay que verificar también su identidad.'),
            ('5. Huella y confianza', 'La huella identifica una clave. Compárala con su propietario por un canal independiente antes de utilizarla.\n\nImportar una clave no garantiza que pertenezca a quien afirma ser. GPG puede rechazar el cifrado si no confía en ella; configura la confianza con GPG siguiendo las indicaciones del aula.'),
            ('6. Hash e integridad de archivos', 'Un hash resume el contenido de un archivo. Calcula SHA-256 en la pestaña Hash y compara el resultado con uno obtenido de una fuente fiable.\n\nUna diferencia indica que los archivos no coinciden. Una coincidencia no demuestra quién publicó el hash. SHA-1 se incluye para prácticas antiguas, no para comprobaciones de seguridad nuevas.'),
            ('7. Errores y límites', 'Lee el diagnóstico y el comando mostrado: pueden indicar una contraseña incorrecta, una clave ausente o un problema de confianza.\n\nGePeGe cifra mensajes de texto UTF-8 y maneja claves ASCII. La pestaña Hash sí admite archivos binarios; esta versión no cifra archivos binarios arbitrarios.')]
        for title, description in lessons:
            header=QToolButton(); header.setObjectName('lessonHeader'); header.setText(title); header.setCheckable(True); header.setArrowType(Qt.ArrowType.RightArrow); header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon); header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            content=label(description); content.setContentsMargins(16, 8, 12, 14); content.hide()
            def toggle(checked, heading=header, body=content):
                heading.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow); body.setVisible(checked)
            header.toggled.connect(toggle); v.addWidget(header); v.addWidget(content)
        v.addStretch(); return w
    def results(self):
        box=QGroupBox('Consola de aprendizaje'); v=QVBoxLayout(box); self.status=label('Preparado.'); v.addWidget(self.status)
        v.addWidget(label('Comandos: ejemplo en terminal y ejecución real')); self.command=textedit('Aquí aparecerán los comandos…', 105); self.command.setReadOnly(True); v.addWidget(self.command)
        v.addWidget(label('Diagnóstico de GPG')); self.detail=textedit('Aquí aparecerán los detalles y posibles errores…', 130); self.detail.setReadOnly(True); v.addWidget(self.detail)
        v.addWidget(label('Resultado')); self.output=textedit('El texto resultante aparecerá aquí…', 170); self.output.setReadOnly(True); v.addWidget(self.output)
        h=QHBoxLayout(); h.addWidget(button('Copiar', lambda: QApplication.clipboard().setText(self.output.toPlainText()))); h.addWidget(button('Guardar resultado…', self.save)); v.addLayout(h)
        h=QHBoxLayout(); h.addWidget(button('Usar en Cifrar', lambda: self.use_result(0))); h.addWidget(button('Usar en Descifrar', lambda: self.use_result(1))); v.addLayout(h); return box
    def use_result(self, tab):
        result = self.output.toPlainText()
        if not result: return
        target = self.encrypt_message if tab == 0 else self.decrypt_message
        target.setPlainText(result); self.tabs.setCurrentIndex(tab)
    def mode_changed(self): self.encrypt_form.setRowVisible(self.recipient, self.mode.currentData() == 'asymmetric')
    def load_file(self, target):
        filename,_=QFileDialog.getOpenFileName(self, 'Abrir archivo de texto')
        if filename:
            try: target.setPlainText(Path(filename).read_text(encoding='utf-8'))
            except (OSError, UnicodeError) as exc: QMessageBox.warning(self, 'No se pudo abrir', f'Selecciona un archivo de texto UTF-8.\n{exc}')
    def save(self):
        if not self.output.toPlainText(): return
        filename,_=QFileDialog.getSaveFileName(self, 'Guardar resultado', 'resultado.asc')
        if filename:
            try: Path(filename).write_text(self.output.toPlainText(), encoding='utf-8')
            except OSError as exc: QMessageBox.warning(self, 'No se pudo guardar', str(exc))
    def start(self, fn, callback=None):
        self.status.setText('Operación en curso…'); task=Task(fn); self.tasks.add(task)
        def done(result):
            self.tasks.discard(task)
            if callback: callback(result)
            else: self.show_result(result)
        task.signals.done.connect(done); self.pool.start(task)
    def show_result(self, result):
        self.status.setText('Operación completada' if result.get('ok') else 'No se pudo completar la operación')
        command = result.get('command', '')
        if result.get('teaching'):
            command = 'EJEMPLO PARA LA TERMINAL\n' + result['teaching'] + '\n\nLos archivos de entrada deben existir; los de salida son ejemplos y pueden sobrescribirse. GPG puede solicitar la contraseña de forma interactiva.\n\nEJECUCIÓN REAL EN GEPEGE\n' + command
        self.command.setPlainText(command)
        self.detail.setPlainText(result.get('detail') or ('Sin mensajes de diagnóstico.' if result.get('ok') else 'Revisa los datos introducidos.'))
        self.output.setPlainText(result.get('output', ''))
    def call(self, data, refresh=False):
        def done(r):
            self.show_result(r)
            if refresh and r.get('ok'): self.refresh(silent=True)
        self.start(lambda: execute(data), done)
    def message_action(self, action):
        if action == 'encrypt':
            data = {'action':action, 'text':self.encrypt_message.toPlainText(), 'mode':self.mode.currentData(), 'recipient':self.recipient.currentData() or '', 'signer':self.signer.currentData() or '', 'cipher':self.cipher.currentData(), 'password':self.encrypt_pass.text()}
            self.encrypt_pass.clear()
        else:
            data = {'action':action, 'text':self.decrypt_message.toPlainText(), 'password':self.decrypt_pass.text()}
            self.decrypt_pass.clear()
        self.call(data)
    def generate(self):
        self.call({'action':'generate', 'name':self.name.text(), 'email':self.email.text(), 'password':self.key_pass.text(), 'algorithm':self.key_algorithm.currentData(), 'expiry':self.expiry.currentData()}, True); self.key_pass.clear()
    def import_key(self): self.call({'action':'import', 'text':self.key_text.toPlainText()}, True)
    def export(self): self.call({'action':'export', 'key':self.export_key.currentData() or ''})
    def selected_key(self):
        item = self.key_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item and item.isSelected() else None
    def update_key_rows(self):
        for index in range(self.key_list.count()):
            item = self.key_list.item(index); row = self.key_list.itemWidget(item)
            if row: row.set_selected(item.isSelected())
    def key_info(self):
        key = self.selected_key()
        if key: self.call({'action':'key_info', 'key':key['fingerprint']})
    def delete_key(self):
        key = self.selected_key()
        if not key: return
        fingerprint = key['fingerprint']
        has_secret = any(k['fingerprint'] == fingerprint for k in self.secret)
        identity = key['uid'] or '(sin identidad)'
        scope = 'la clave pública y la clave privada correspondientes, incluidas sus subclaves' if has_secret else 'la clave pública y sus subclaves'
        detail = f"{identity}\nHuella: {fingerprint}\n\nSe eliminarán {scope} del llavero de este usuario."
        if has_secret: detail += '\n\nSin una copia de seguridad de la clave privada, podrías perder el acceso a mensajes cifrados y la capacidad de firmar.'
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        if QMessageBox.warning(self, 'Borrar clave — primera confirmación', detail + '\n\n¿Quieres continuar?', buttons, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes: return
        if QMessageBox.warning(self, 'Borrar clave — confirmación final', f'Esta acción elimina {scope}.\n\nHuella: {fingerprint}\n\n¿Confirmas definitivamente que quieres borrar esta clave?', buttons, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes: return
        self.call({'action':'delete_key', 'key':fingerprint, 'has_secret':has_secret}, True)
    def refresh(self, silent=False):
        def do(): return (execute({'action':'keys'}), execute({'action':'keys','secret':True}))
        def done(pair):
            if not isinstance(pair, tuple): return self.show_result(pair)
            pub,sec=pair
            if not pub['ok'] or not sec['ok']: return self.show_result(pub if not pub['ok'] else sec)
            self.public=pub['keys']; self.secret=sec['keys']; self.key_list.clear()
            for k in self.public:
                text = f"{k['uid'] or '(sin identidad)'}\nHuella: {k['fingerprint']}  |  validez: {k['validity']}"
                item = QListWidgetItem(); item.setData(Qt.ItemDataRole.UserRole, k); self.key_list.addItem(item)
                row = KeyRow(self, item, text); item.setSizeHint(row.sizeHint()); self.key_list.setItemWidget(item, row)
            for combo, keys, empty in [(self.recipient,self.public,'Selecciona destinatario'), (self.export_key,self.public,'Selecciona clave pública'), (self.signer,self.secret,'Sin firma')]:
                combo.clear(); combo.addItem(empty, '')
                for k in keys: combo.addItem(f"{k['uid'] or 'Sin identidad'} — {k['id']}", k['fingerprint'])
            if not silent:
                combined = dict(pub)
                combined['command'] = pub['command'] + '\n' + sec['command']
                combined['teaching'] = pub['teaching'] + '\n' + sec['teaching']
                self.show_result(combined); self.detail.setPlainText(f"{len(self.public)} claves públicas y {len(self.secret)} claves privadas.\n\n{pub['detail']}{sec['detail']}")
            else: self.status.setText('Operación completada; llavero actualizado.')
        self.start(do, done)
    def search(self):
        query=self.lookup.text().strip()
        if not query: return self.show_result({'ok':False,'detail':'Introduce un correo electrónico o una huella completa.'})
        is_fpr=len(query)==40 and all(c in '0123456789abcdefABCDEF' for c in query)
        if not is_fpr and ('@' not in query or '/' in query): return self.show_result({'ok':False,'detail':'Introduce un correo válido o una huella de 40 caracteres hexadecimales.'})
        url='https://keys.openpgp.org/vks/v1/' + ('by-fingerprint/' if is_fpr else 'by-email/') + urllib.parse.quote(query, safe='')
        def fetch():
            try:
                with urllib.request.urlopen(url, timeout=15) as response: data=response.read(1_000_001)
                if len(data)>1_000_000: raise ValueError('La respuesta supera 1 MB.')
                return {'ok':True, 'output':data.decode('utf-8'), 'detail':'Clave descargada. Comprueba la huella y pulsa «Importar clave».', 'command':'Consulta HTTPS a keys.openpgp.org (no se ejecuta GPG).'}
            except (OSError, UnicodeError, ValueError) as exc: return {'ok':False, 'detail':f'No se pudo obtener la clave: {exc}', 'command':'Consulta HTTPS a keys.openpgp.org (no se ejecuta GPG).'}
        def done(r):
            self.show_result(r)
            if r.get('ok'): self.key_text.setPlainText(r['output'])
        self.start(fetch, done)

def main():
    app=QApplication(sys.argv)
    app.setApplicationName('GePeGe')
    app.setWindowIcon(QIcon(str(APP_ICON)))
    app.setStyle('Fusion')
    palette = app.palette()
    for role, color in ((QPalette.ColorRole.Window, '#edf2f7'), (QPalette.ColorRole.WindowText, '#182536'),
                        (QPalette.ColorRole.Base, '#ffffff'), (QPalette.ColorRole.Text, '#172536'),
                        (QPalette.ColorRole.Button, '#d5e2f1'), (QPalette.ColorRole.ButtonText, '#173457'),
                        (QPalette.ColorRole.Highlight, '#2854a1'), (QPalette.ColorRole.HighlightedText, '#ffffff'),
                        (QPalette.ColorRole.PlaceholderText, '#526274')):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    app.setStyleSheet(STYLE); window=Window(); window.show(); sys.exit(app.exec())

if __name__ == '__main__': main()
