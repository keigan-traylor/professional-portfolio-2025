# provision_account.py - AWS provisioning simulation (dry-run supported)
import argparse, json, os, zipfile, tempfile
from pathlib import Path
import boto3, botocore, yaml, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATE_ROLE = {...}  # see README for full template

def load_config(path): return json.loads(Path(path).read_text())

def package_lambda(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(source_dir):
            for f in files:
                zf.write(os.path.join(root,f), arcname=os.path.relpath(os.path.join(root,f), source_dir))
    return output_zip

def dry_run_create_role(role_name):
    logger.info(f"[DRY-RUN] Would create role: {role_name}")
    return {"RoleName": role_name}

def main():
    parser = argparse.ArgumentParser(description='Provision AWS account components (dry-run supported)')
    parser.add_argument('--config', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    cfg = load_config(args.config)
    # package simple lambda source (sample)
    sample_src = Path('lambda_src'); sample_src.mkdir(exist_ok=True)
    (sample_src/'app.py').write_text("""def lambda_handler(event, context):\n    return {'status': 'ok'}\n""")
    tmp_zip = Path(tempfile.gettempdir())/'lambda_package.zip'
    package_lambda(sample_src, tmp_zip)
    for fn in cfg.get('functions', []):
        func_name = fn['name']
        role_name = fn.get('role', func_name + '-role')
        if args.dry_run:
            dry_run_create_role(role_name)
        else:
            logger.info('Real mode not shown in sample README; requires AWS creds and permissions')
if __name__=='__main__': main()
