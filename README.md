# gcp_secret_manager_ansible_module
Ansible module for GCP Secret Manager

## How to run

```bash
python3 -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
cat > /tmp/arguments.json << EOF
{
    "ANSIBLE_MODULE_ARGS": {
        "credentials": "<filepath_to_gcp_creds>",
        "project_id": "<project_id>", 
        "secret_name": "<secret_name>",
        "get_info": true
    }
}
EOF
python library/gcp_secret_manager.py /tmp/arguments.json
```
