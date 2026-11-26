# SPDX-License-Identifier: GPL-3.0-only
import os
import hashlib
import tempfile
import subprocess
import unittest
from unittest.mock import patch
from gpg_backend import execute

class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); os.chmod(self.temp.name, 0o700)
        self.env = patch.dict(os.environ, {'GNUPGHOME': self.temp.name}); self.env.start()
    def tearDown(self):
        self.env.stop(); self.temp.cleanup()
    def test_symmetric_round_trip_and_wrong_password(self):
        encrypted = execute({'action':'encrypt','mode':'symmetric','text':'Hola, clase: ñ', 'password':'secreto-prueba'})
        self.assertTrue(encrypted['ok'], encrypted['detail']); self.assertIn('BEGIN PGP MESSAGE', encrypted['output']); self.assertNotIn('secreto-prueba', encrypted['command'])
        self.assertIn('--symmetric', encrypted['teaching']); self.assertIn('> mensaje-cifrado.asc', encrypted['teaching'])
        decrypted = execute({'action':'decrypt','text':encrypted['output'],'password':'secreto-prueba'})
        self.assertTrue(decrypted['ok'], decrypted['detail']); self.assertEqual(decrypted['output'], 'Hola, clase: ñ')
    def test_default_generation_returns_fingerprint(self):
        result = execute({'action':'generate', 'name':'Prueba defecto', 'password':'clave-prueba'})
        self.assertTrue(result['ok'], result['detail'])
        self.assertRegex(result['fingerprint'], r'^[0-9A-F]{40}$')

    def test_binary_encrypted_message(self):
        encrypted = subprocess.run(['gpg', '--batch', '--yes', '--pinentry-mode', 'loopback',
                                    '--passphrase', 'prueba', '--symmetric'],
                                   input='Mensaje binario: ñ'.encode(), capture_output=True, check=True)
        result = execute({'action':'decrypt', 'encrypted_bytes':encrypted.stdout, 'password':'prueba'})
        self.assertTrue(result['ok'], result['detail'])
        self.assertEqual(result['output'], 'Mensaje binario: ñ')

    def test_binary_file_round_trip(self):
        original = b'\x00\xff\x80 datos binarios\n'
        encrypted = execute({'action':'encrypt', 'mode':'symmetric', 'content_bytes':original,
                             'format':'gpg', 'password':'prueba'})
        self.assertTrue(encrypted['ok'], encrypted['detail'])
        self.assertTrue(encrypted['output_bytes'])
        self.assertIn('mensaje-cifrado.gpg', encrypted['teaching'])
        decrypted = execute({'action':'decrypt', 'encrypted_bytes':encrypted['output_bytes'], 'password':'prueba'})
        self.assertTrue(decrypted['ok'], decrypted['detail'])
        self.assertEqual(decrypted['output_bytes'], original)

    def test_generate_export_import_encrypt_sign_decrypt(self):
        generated = execute({'action':'generate','name':'Prueba Alumno','email':'alumno@example.org','password':'clave-prueba','algorithm':'rsa2048','expiry':'1y'})
        self.assertTrue(generated['ok'], generated['detail'])
        self.assertRegex(generated['fingerprint'], r'^[0-9A-F]{40}$')
        self.assertIn('rsa2048', generated['command']); self.assertIn('1y', generated['command'])
        self.assertIn('--quick-generate-key', generated['teaching']); self.assertIn('--quick-add-key', generated['teaching']); self.assertNotIn('--status-fd', generated['teaching'])
        keys=execute({'action':'keys'}); self.assertEqual(len(keys['keys']),1); key=keys['keys'][0]['fingerprint']
        self.assertIn('--list-keys', keys['teaching']); self.assertNotIn('--with-colons', keys['teaching'])
        self.assertIn('--list-secret-keys', execute({'action':'keys','secret':True})['teaching'])
        exported=execute({'action':'export','key':key}); self.assertTrue(exported['ok'], exported['detail']); self.assertIn('BEGIN PGP PUBLIC KEY',exported['output'])
        self.assertIn('--export',exported['teaching']); self.assertIn('> clave-publica.asc',exported['teaching'])
        imported=execute({'action':'import','text':exported['output']}); self.assertTrue(imported['ok'],imported['detail'])
        self.assertEqual(imported['teaching'], 'gpg --import < clave.asc'); self.assertIn('--batch', imported['command'])
        enc=execute({'action':'encrypt','mode':'asymmetric','text':'Mensaje firmado', 'recipient':key,'signer':key,'password':'clave-prueba','cipher':'AES256'})
        self.assertTrue(enc['ok'],enc['detail'])
        self.assertIn('--cipher-algo AES256',enc['command'])
        self.assertIn('--encrypt',enc['teaching']); self.assertIn('< mensaje.txt',enc['teaching']); self.assertNotIn('--batch',enc['teaching']); self.assertNotIn('clave-prueba',enc['teaching'])
        dec=execute({'action':'decrypt','text':enc['output'],'password':'clave-prueba'})
        self.assertTrue(dec['ok'],dec['detail']); self.assertEqual(dec['output'],'Mensaje firmado'); self.assertIn('signature',dec['detail'].lower())
        self.assertEqual(dec['teaching'], 'gpg --decrypt < mensaje-cifrado.asc > mensaje-descifrado.txt')
        info = execute({'action':'key_info','key':key}); self.assertTrue(info['ok'], info['detail']); self.assertIn('Prueba Alumno', info['output'])
        self.assertIn('--fingerprint --list-keys', info['teaching'])
        with tempfile.TemporaryDirectory() as other:
            os.chmod(other, 0o700)
            with patch.dict(os.environ, {'GNUPGHOME': other}):
                self.assertTrue(execute({'action':'import','text':exported['output']})['ok'])
                data = {'action':'encrypt', 'mode':'asymmetric', 'text':'Mensaje importado', 'recipient':key}
                rejected = execute(data)
                self.assertFalse(rejected['ok'], rejected['detail'])
                encrypted = execute({**data, 'confirmed_recipient':True})
                self.assertTrue(encrypted['ok'], encrypted['detail'])
                self.assertIn('--trust-model always', encrypted['teaching'])
                deleted = execute({'action':'delete_key','key':key,'has_secret':False})
                self.assertIn('--list-secret-keys', deleted['teaching']); self.assertIn('--delete-key', deleted['teaching'])
                self.assertTrue(deleted['ok'],deleted['detail']); self.assertEqual(execute({'action':'keys'})['keys'],[])
        decrypted = execute({'action':'decrypt', 'text':encrypted['output'], 'password':'clave-prueba'})
        self.assertTrue(decrypted['ok'], decrypted['detail']); self.assertEqual(decrypted['output'], 'Mensaje importado')
        with self.assertRaises(ValueError): execute({'action':'delete_key','key':key,'has_secret':False})
        deleted = execute({'action':'delete_key','key':key,'has_secret':True})
        self.assertIn('--delete-secret-and-public-key', deleted['teaching'])
        self.assertTrue(deleted['ok'],deleted['detail']); self.assertEqual(execute({'action':'keys'})['keys'],[]); self.assertEqual(execute({'action':'keys','secret':True})['keys'],[])
    def test_missing_data(self):
        with self.assertRaises(ValueError): execute({'action':'encrypt','mode':'symmetric','text':'hola'})
        with self.assertRaises(ValueError): execute({'action':'import','text':''})
        with self.assertRaises(ValueError): execute({'action':'hash','filename':'archivo','expected':'incorrecto'})
    def test_hash_file_and_comparison(self):
        filename = os.path.join(self.temp.name, 'archivo: prueba.bin')
        data = b'\x00\xff\x80 contenido binario\n'
        with open(filename, 'wb') as f: f.write(data)
        expected = hashlib.sha256(data).hexdigest()
        result = execute({'action':'hash','filename':filename,'algorithm':'SHA256','expected':expected})
        self.assertTrue(result['ok'], result['detail']); self.assertEqual(result['output'].lower(), expected)
        self.assertIn('--print-md SHA256',result['teaching']); self.assertNotIn('--with-colons',result['teaching'])
        self.assertEqual(result['detail'], 'El hash coincide.')
        result = execute({'action':'hash','filename':filename,'algorithm':'SHA256','expected':'0'*64})
        self.assertEqual(result['detail'], 'El hash NO coincide.')

if __name__ == '__main__': unittest.main()
