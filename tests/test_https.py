# SPDX-License-Identifier: GPL-3.0-only
import ssl
import unittest
from unittest.mock import Mock, patch

from app import fetch_key, https_context


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


if __name__ == '__main__':
    unittest.main()
