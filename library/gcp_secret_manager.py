#!/usr/bin/env python3
# coding: utf-8

from __future__ import (absolute_import, division, print_function)
from datetime import datetime
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from google.cloud import secretmanager
from google.oauth2 import service_account
import google_crc32c

def run_module():
    module_args = dict(
        credentials=dict(type='str', required=True),
        project_id=dict(type='str', required=True),
        secret_name=dict(type='str', required=True),
        version=dict(type='str', required=False, default="latest"),
        get_info=dict(type='bool', required=False, default=False)
    )

    result = dict(
        value="",
        labels=dict,
        create_time=datetime,
        replication='',
        etag="",
        message=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    creds = service_account.Credentials.from_service_account_file(
         str(module.params['credentials'])
    )

    project_id = module.params['project_id']
    secret_id = module.params['secret_name']
    version_id = module.params['version']
    get_info = module.params['get_info']
    labels = {}
    create_time = datetime(1900,1,1,0,0,0,0)
    etag, replication = "", ""

    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    if get_info:
        name = client.secret_path(project_id, secret_id)
        response = client.get_secret(request={"name": name})
        labels = dict(response.labels)
        create_time = datetime.fromtimestamp(response.create_time.timestamp())
        etag = response.etag
        if "automatic" in response.replication:
            replication = "AUTOMATIC"
        elif "user_managed" in response.replication:
            replication = "MANAGED"
        else:
            replication = str(response.replication)

    # Access the secret version.
    name_data = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response_data = client.access_secret_version(request={"name": name_data})
    crc32c = google_crc32c.Checksum()
    crc32c.update(response_data.payload.data)
    if response_data.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        module.fail_json(msg='Data corruption detected', **result)

    payload = response_data.payload.data.decode("UTF-8")
    result['value'] = payload
    result['labels'] = labels
    result['message'] = "All good"
    result['create_time'] = create_time
    result['replication'] = replication
    result['etag'] = etag
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
