# SPDX-License-Identifier: GPL-3.0-only
"""Operaciones GPG sin shell; las contraseñas viajan por un descriptor privado."""
import os
import re
import shlex
import subprocess

def teaching_command(args):
    """Una variante interactiva de los argumentos, para practicar en terminal."""
    simplified = []
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg == '--status-fd':
            skip = True
        elif arg != '--with-colons':
            simplified.append(arg)
    command = shlex.join(['gpg', *simplified])
    if '--import' in args:
        command += ' < clave.asc'
    elif '--export' in args:
        command += ' > clave-publica.asc'
    elif '--decrypt' in args:
        command += ' < mensaje-cifrado.asc > mensaje-descifrado.txt'
    elif '--encrypt' in args or '--symmetric' in args:
        command += ' < mensaje.txt > mensaje-cifrado.asc'
    return command

def run_gpg(args, data='', password=None, timeout=120):
    command = ['gpg', '--batch', '--yes', *args]
    display = shlex.join(command)
    read_fd = write_fd = None
    try:
        if password is not None:
            read_fd, write_fd = os.pipe()
            os.write(write_fd, (password + '\n').encode())
            os.close(write_fd)
            write_fd = None
            command[1:1] = ['--pinentry-mode', 'loopback', '--passphrase-fd', str(read_fd)]
            display = 'gpg --pinentry-mode loopback --passphrase-fd <descriptor> ' + shlex.join(command[5:])
        env = os.environ.copy()
        if 'LD_LIBRARY_PATH_ORIG' in env:
            env['LD_LIBRARY_PATH'] = env.pop('LD_LIBRARY_PATH_ORIG')
        elif getattr(__import__('sys'), 'frozen', False):
            env.pop('LD_LIBRARY_PATH', None)
        result = subprocess.run(command, input=data.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                pass_fds=(read_fd,) if read_fd is not None else (), timeout=timeout, env=env)
        return {'ok': result.returncode == 0, 'output': result.stdout.decode('utf-8', 'replace'),
                'detail': result.stderr.decode('utf-8', 'replace'), 'command': display, 'teaching': teaching_command(args)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'output': '', 'detail': str(exc), 'command': display, 'teaching': teaching_command(args)}
    finally:
        if read_fd is not None: os.close(read_fd)
        if write_fd is not None: os.close(write_fd)


def list_keys(secret=False):
    result = run_gpg(['--with-colons', '--fingerprint', '--list-secret-keys' if secret else '--list-keys'])
    keys = []
    for line in result['output'].splitlines():
        fields = line.split(':')
        if fields[0] in ('pub', 'sec'):
            keys.append({'id': fields[4], 'uid': '', 'fingerprint': '', 'validity': fields[1]})
        elif fields[0] == 'fpr' and keys and not keys[-1]['fingerprint']:
            keys[-1]['fingerprint'] = fields[9]
        elif fields[0] == 'uid' and keys and not keys[-1]['uid']:
            keys[-1]['uid'] = fields[9]
    result['keys'] = keys
    result['output'] = ''
    return result


def execute(payload):
    action = payload.get('action', '')
    value = lambda name: str(payload.get(name, '')).strip()
    text = str(payload.get('text', ''))
    password = str(payload.get('password', ''))
    if '\n' in password or '\r' in password or len(password.encode()) > 1024:
        raise ValueError('La contraseña no puede contener saltos de línea ni superar 1024 bytes.')
    if action == 'keys': return list_keys(bool(payload.get('secret')))
    if action in ('key_info', 'delete_key'):
        fingerprint = value('key').upper()
        if not re.fullmatch(r'(?:[0-9A-F]{40}|[0-9A-F]{64})', fingerprint):
            raise ValueError('Selecciona una clave con huella completa válida.')
        if action == 'key_info':
            return run_gpg(['--fingerprint', '--list-keys', fingerprint])
        secret_keys = list_keys(True)
        if not secret_keys['ok']: return secret_keys
        has_secret = any(key['fingerprint'].upper() == fingerprint for key in secret_keys['keys'])
        if has_secret != bool(payload.get('has_secret')):
            raise ValueError('La disponibilidad de la clave privada ha cambiado. Actualiza el llavero y vuelve a intentarlo.')
        command = '--delete-secret-and-public-key' if has_secret else '--delete-key'
        result = run_gpg([command, fingerprint])
        result['command'] = secret_keys['command'] + '\n' + result['command']
        result['teaching'] = secret_keys['teaching'] + '\n' + result['teaching']
        return result
    if action == 'encrypt':
        if not text: raise ValueError('Escribe o importa un mensaje.')
        mode = value('mode')
        cipher = value('cipher') or 'default'
        if cipher not in ('default', 'AES128', 'AES256'): raise ValueError('Algoritmo de cifrado no válido.')
        args = ['--armor']
        if cipher != 'default': args += ['--cipher-algo', cipher]
        if mode == 'symmetric':
            if not password: raise ValueError('Introduce una contraseña para cifrar.')
            args += ['--symmetric']
        elif mode == 'asymmetric':
            if not value('recipient'): raise ValueError('Selecciona una clave pública destinataria.')
            args += ['--recipient', value('recipient'), '--encrypt']
        else: raise ValueError('Selecciona un modo de cifrado válido.')
        if value('signer'):
            args += ['--local-user', value('signer'), '--sign']
        return run_gpg(args, text, password if mode == 'symmetric' or value('signer') else None)
    if action == 'decrypt':
        if not text: raise ValueError('Pega o importa el mensaje cifrado.')
        return run_gpg(['--decrypt'], text, password)
    if action == 'generate':
        name, email = value('name'), value('email')
        if not name or any(c in name + email for c in '\r\n<>'): raise ValueError('Introduce un nombre válido y un correo sin caracteres especiales.')
        if email and ('@' not in email or ' ' in email): raise ValueError('Introduce un correo válido.')
        if not password: raise ValueError('Protege la clave nueva con una contraseña.')
        algorithm = value('algorithm') or 'default'
        expiry = value('expiry') or '2y'
        if algorithm not in ('default', 'rsa2048', 'rsa3072', 'rsa4096'): raise ValueError('Algoritmo de clave no válido.')
        if expiry not in ('0', '1y', '2y', '5y'): raise ValueError('Caducidad no válida.')
        uid = f'{name} <{email}>' if email else name
        if algorithm == 'default':
            return run_gpg(['--quick-generate-key', uid, algorithm, 'default', expiry], password=password)
        primary = run_gpg(['--status-fd', '2', '--quick-generate-key', uid, algorithm, 'cert,sign', expiry], password=password)
        if not primary['ok']: return primary
        match = re.search(r'^\[GNUPG:\] KEY_CREATED [A-Z] ([0-9A-F]+)$', primary['detail'], re.MULTILINE)
        if not match:
            primary.update(ok=False, detail=primary['detail'] + '\nLa clave se creó, pero no se pudo identificar para añadir la subclave de cifrado.')
            return primary
        subkey = run_gpg(['--quick-add-key', match.group(1), algorithm, 'encrypt', expiry], password=password)
        subkey['command'] = primary['command'] + '\n' + subkey['command']
        subkey['teaching'] = primary['teaching'] + '\n' + subkey['teaching']
        subkey['detail'] = primary['detail'] + '\n' + subkey['detail']
        if not subkey['ok']: subkey['detail'] += '\nLa clave principal se creó, pero no se pudo añadir la subclave de cifrado.'
        return subkey
    if action == 'hash':
        algorithm, filename = value('algorithm') or 'SHA256', str(payload.get('filename', ''))
        if algorithm not in ('SHA256', 'SHA512', 'SHA1'): raise ValueError('Algoritmo de hash no válido.')
        if not filename: raise ValueError('Selecciona un archivo.')
        expected = ''.join(value('expected').split()).upper()
        lengths = {'SHA256': 64, 'SHA512': 128, 'SHA1': 40}
        if expected and (len(expected) != lengths[algorithm] or any(c not in '0123456789ABCDEF' for c in expected)):
            raise ValueError(f'El hash esperado debe tener {lengths[algorithm]} caracteres hexadecimales para {algorithm}.')
        result = run_gpg(['--with-colons', '--print-md', algorithm, os.path.abspath(filename)], timeout=None)
        if result['ok']:
            parts = result['output'].rstrip().rsplit(':', 2)
            digest = parts[-2].upper() if len(parts) >= 3 else ''
            if len(digest) != lengths[algorithm] or any(c not in '0123456789ABCDEF' for c in digest):
                result.update(ok=False, output='', detail='No se pudo interpretar el hash calculado por GPG.')
            else:
                result['output'] = digest
                result['detail'] = ('El hash coincide.' if digest == expected else 'El hash NO coincide.') if expected else 'Hash calculado. Puedes compararlo con un valor conocido.'
        return result
    if action == 'import':
        if not text: raise ValueError('Pega o importa una clave.')
        return run_gpg(['--import'], text)
    if action == 'export':
        if not value('key'): raise ValueError('Selecciona una clave pública.')
        return run_gpg(['--armor', '--export', value('key')])
    raise ValueError('Operación desconocida.')

