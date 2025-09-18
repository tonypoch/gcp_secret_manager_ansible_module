import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library import gcp_secret_manager

class TestGcpSecretManager(unittest.TestCase):

    @patch('library.gcp_secret_manager.AnsibleModule')
    @patch('library.gcp_secret_manager.secretmanager.SecretManagerServiceClient')
    @patch('library.gcp_secret_manager.service_account.Credentials')
    def test_get_info_success(self, mock_creds, mock_client, mock_module):
        # 1. Setup Mocks

        # Mock AnsibleModule
        mock_ansible_module = MagicMock()
        mock_ansible_module.params = {
            'credentials': 'path/to/creds.json',
            'project_id': 'test-project',
            'secret_name': 'test-secret',
            'version': 'latest',
            'get_info': True
        }
        mock_module.return_value = mock_ansible_module

        # Mock GCP Secret Manager Client
        mock_sm_client = MagicMock()
        mock_client.return_value = mock_sm_client

        # Mock get_secret response
        mock_secret_response = MagicMock()
        test_time = datetime(2023, 1, 1)
        mock_secret_response.create_time.timestamp.return_value = test_time.timestamp()
        mock_secret_response.labels = {'env': 'test'}
        mock_secret_response.etag = '12345'
        mock_secret_response.replication = {"automatic": {}}
        mock_sm_client.get_secret.return_value = mock_secret_response

        # Mock access_secret_version response
        mock_access_response = MagicMock()
        mock_access_response.payload.data = b'secret-data'
        mock_access_response.payload.data_crc32c = 1123415124
        mock_sm_client.access_secret_version.return_value = mock_access_response

        # 2. Call the function
        gcp_secret_manager.run_module()

        # 3. Assert the results
        call_args, call_kwargs = mock_ansible_module.exit_json.call_args
        result_dict = call_kwargs

        self.assertIsInstance(result_dict['create_time'], str)
        self.assertEqual(result_dict['create_time'], test_time.isoformat())
        self.assertEqual(result_dict['value'], 'secret-data')

    @patch('library.gcp_secret_manager.AnsibleModule')
    @patch('library.gcp_secret_manager.secretmanager.SecretManagerServiceClient')
    @patch('library.gcp_secret_manager.service_account.Credentials')
    def test_get_info_false(self, mock_creds, mock_client, mock_module):
        # 1. Setup Mocks

        # Mock AnsibleModule
        mock_ansible_module = MagicMock()
        mock_ansible_module.params = {
            'credentials': 'path/to/creds.json',
            'project_id': 'test-project',
            'secret_name': 'test-secret',
            'version': 'latest',
            'get_info': False
        }
        mock_module.return_value = mock_ansible_module

        # Mock GCP Secret Manager Client
        mock_sm_client = MagicMock()
        mock_client.return_value = mock_sm_client

        # Mock access_secret_version response
        mock_access_response = MagicMock()
        mock_access_response.payload.data = b'secret-data'
        mock_access_response.payload.data_crc32c = 1123415124
        mock_sm_client.access_secret_version.return_value = mock_access_response

        # 2. Call the function
        gcp_secret_manager.run_module()

        # 3. Assert the results
        call_args, call_kwargs = mock_ansible_module.exit_json.call_args
        result_dict = call_kwargs

        # With get_info=False, create_time should be the isoformat of the default datetime
        self.assertIsInstance(result_dict['create_time'], str)
        self.assertEqual(result_dict['create_time'], datetime(1900,1,1,0,0,0,0).isoformat())
        self.assertEqual(result_dict['value'], 'secret-data')
        self.assertEqual(result_dict['labels'], {})


if __name__ == '__main__':
    unittest.main()
