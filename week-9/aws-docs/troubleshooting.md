# AWS Troubleshooting Guide

## Purpose

Quick reference for resolving common AWS credential issues when using boto3 in Jupyter notebooks.

## Target Audience

Developers using AWS CLI with `aws login` or `aws configure` and boto3 in Jupyter notebooks.

---

## Problem: NoCredentialsError in Jupyter Notebook

### Symptoms

```
NoCredentialsError: Unable to locate credentials
```

Occurs when invoking AWS services via boto3 in a notebook, even after successfully running `aws login` in the terminal.

### Root Cause

Jupyter notebook kernels run in separate Python processes that don't automatically access credentials cached by `aws login`. Credentials are stored in `~/.aws/login/cache/` but boto3 doesn't read this location by default.

### Solution

#### Step 1: Load Credentials Function

Add this function to your notebook:

```python
import boto3
import json
import os
from pathlib import Path


def load_aws_login_credentials():
    """
    Loads credentials from aws login cache.
    
    Returns:
        dict: Credentials with keys: aws_access_key_id, aws_secret_access_key, 
              aws_session_token. Returns None if not found.
    """
    login_cache_dir = Path.home() / '.aws' / 'login' / 'cache'
    credential_files = list(login_cache_dir.glob('*.json'))
    
    if not credential_files:
        return None
    
    try:
        with open(credential_files[0]) as f:
            creds_data = json.load(f)
            access_token = creds_data.get('accessToken', {})
            return {
                'aws_access_key_id': access_token.get('accessKeyId'),
                'aws_secret_access_key': access_token.get('secretAccessKey'),
                'aws_session_token': access_token.get('sessionToken')
            }
    except Exception:
        return None
```

#### Step 2: Initialize Credentials

Load credentials at the start of your notebook:

```python
_aws_creds = load_aws_login_credentials()
if _aws_creds:
    os.environ.update(_aws_creds)
    print("✓ AWS credentials loaded")
else:
    print("⚠ No credentials found. Run 'aws login' first.")
```

#### Step 3: Use Credentials in boto3

Pass credentials directly to `boto3.Session()`:

```python
def invoke_lambda_function(function_name, payload, region_name='us-west-2'):
    """
    Invokes an AWS Lambda function.
    
    Args:
        function_name (str): Lambda function name.
        payload (dict): Request payload.
        region_name (str): AWS region. Defaults to 'us-west-2'.
    
    Returns:
        dict: Lambda function response.
    
    Raises:
        NoCredentialsError: If credentials are missing and not in cache.
    """
    if _aws_creds:
        session = boto3.Session(
            aws_access_key_id=_aws_creds['aws_access_key_id'],
            aws_secret_access_key=_aws_creds['aws_secret_access_key'],
            aws_session_token=_aws_creds['aws_session_token'],
            region_name=region_name
        )
    else:
        session = boto3.Session(region_name=region_name)
    
    lambda_client = session.client('lambda', region_name=region_name)
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    return json.loads(response['Payload'].read())
```

### Verification

After running the credential loading code, you should see:

- `✓ AWS credentials loaded` message
- Successful boto3 API calls without credential errors

### Edge Cases

**No credentials in cache:**

- Ensure `aws login` completed successfully
- Check `~/.aws/login/cache/` contains JSON files
- Credentials expire after the session timeout; re-run `aws login` if needed

**Multiple credential files:**

- Function uses the first JSON file found
- For multiple accounts, modify the function to select a specific file

**Credential expiration:**

- `aws login` credentials have expiration times
- Re-run `aws login` when credentials expire
- Check expiration in the credential file's `expiresAt` field

### Alternative Solutions

#### Option 1: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
```

Then restart the notebook kernel.

#### Option 2: AWS Configure

Use `aws configure` for persistent credentials that work automatically with boto3.

**Step 1: Get AWS Access Keys**

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to: **IAM** → **Users** → **Your Username** → **Security Credentials**
3. Click **Create Access Key**
4. Select **Command Line Interface (CLI)**
5. Download or copy the **Access Key ID** and **Secret Access Key**
6. ⚠️ **Important**: Save these securely - you won't be able to see the secret key again

**Step 2: Configure AWS CLI**

Run the interactive configuration:

```bash
aws configure
```

Enter the following when prompted:

```
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-west-2
Default output format [None]: json
```

**Step 3: Verify Configuration**

```bash
aws sts get-caller-identity
aws configure list
```

**Step 4: Use in Notebook**

With `aws configure`, boto3 automatically reads credentials from `~/.aws/credentials`. No special code needed:

```python
import boto3
import json

def invoke_lambda_function(function_name, payload, region_name='us-west-2'):
    """
    Invokes an AWS Lambda function.
    
    Args:
        function_name (str): Lambda function name.
        payload (dict): Request payload.
        region_name (str): AWS region. Defaults to 'us-west-2'.
    
    Returns:
        dict: Lambda function response.
    """
    lambda_client = boto3.client('lambda', region_name=region_name)
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    return json.loads(response['Payload'].read())
```

**Advantages:**
- No credential loading code needed
- Works immediately with standard boto3
- No kernel restart required
- Credentials persist across sessions

**Security Notes:**
- Access keys are permanent until rotated
- Never commit credentials to version control
- Rotate keys regularly
- Use IAM policies to limit permissions

---

## Related Documentation

- [AWS Setup Guide](../AWS_SETUP.md) - Initial AWS CLI configuration
- [AWS CLI v2 Login Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
