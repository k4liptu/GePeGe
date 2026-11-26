# SPDX-License-Identifier: GPL-3.0-only
import ssl
import json
import unittest
from unittest.mock import Mock, patch

from app import fetch_key, https_context, publish_key


class CertificateContext(unittest.TestCase):
    @patch('app.Path.is_file', return_value=True)
    @patch('app.ssl.create_default_context')
    def test_loads_system_bundle_when_packaged_defaults_are_empty(self, create, exists):
        context = create.return_value
        context.get_ca_certs.return_value = []
        self.assertIs(https_context(), context)
        context.load_verify_locations.assert_called_once_with(cafile='/etc/ssl/certs/ca-certificates.crt')

    @patch('app.Path.is_file')
    @patch('app.ssl.create_default_context')
    def test_preserves_working_default_context(self, create, exists):
        context = create.return_value
        context.get_ca_certs.return_value = [Mock()]
        self.assertIs(https_context(), context)
        context.load_verify_locations.assert_not_called()
        exists.assert_not_called()

    @patch('app.urllib.request.urlopen', side_effect=ssl.SSLCertVerificationError('certificado inválido'))
    def test_certificate_failure_is_reported_without_disabling_verification(self, request):
        result = fetch_key('prueba@example.org')
        self.assertFalse(result['ok'])
        self.assertIn('certificado inválido', result['detail'])
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.kwargs['context'].verify_mode, ssl.CERT_REQUIRED)


class PublishKey(unittest.TestCase):
    @patch('app.https_context')
    @patch('app.urllib.request.urlopen')
    @patch('app.execute')
    def test_public_upload_and_email_verification(self, execute, urlopen, context):
        fingerprint = 'A' * 40
        execute.return_value = {'ok': True, 'output': '-----BEGIN PGP PUBLIC KEY BLOCK-----\npublic', 'command': 'gpg --export'}
        replies = [
            {'key_fpr': fingerprint, 'token': 'secret-token', 'status': {'a@example.org': 'unpublished'}},
            {'key_fpr': fingerprint, 'status': {'a@example.org': 'pending'}},
        ]
        from unittest.mock import MagicMock
        urlopen.side_effect = [MagicMock(**{'__enter__.return_value.read.return_value': json.dumps(reply).encode()}) for reply in replies]
        result = publish_key(fingerprint, 'a@example.org')
        self.assertTrue(result['ok'], result['detail'])
        self.assertIn('Revisa el correo', result['detail'])
        execute.assert_called_once_with({'action': 'export', 'key': fingerprint})
        first = urlopen.call_args_list[0].args[0]
        second = urlopen.call_args_list[1].args[0]
        self.assertEqual(json.loads(first.data)['keytext'], execute.return_value['output'])
        self.assertEqual(json.loads(second.data)['addresses'], ['a@example.org'])
        self.assertNotIn('secret-token', str(result))

    @patch('app.execute', return_value={'ok': True, 'output': '-----BEGIN PGP PRIVATE KEY BLOCK-----', 'command': 'gpg'})
    @patch('app.urllib.request.urlopen')
    def test_never_uploads_private_material(self, urlopen, execute):
        self.assertFalse(publish_key('A' * 40, '')['ok'])
        urlopen.assert_not_called()

    @patch('app.execute', return_value={'ok': True, 'output': '-----BEGIN PGP PUBLIC KEY BLOCK-----', 'command': 'gpg'})
    @patch('app.urllib.request.urlopen', side_effect=OSError('sin conexión'))
    def test_network_failure(self, urlopen, execute):
        result = publish_key('A' * 40, '')
        self.assertFalse(result['ok'])
        self.assertIn('sin conexión', result['detail'])


if __name__ == '__main__':
    unittest.main()
