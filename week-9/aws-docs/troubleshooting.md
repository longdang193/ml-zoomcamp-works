# AWS Troubleshooting Guide

## Purpose

Quick reference for resolving common AWS credential and permission issues
when using boto3 in Jupyter notebooks.

## Target Audience

Developers using AWS CLI with `aws login` or `aws configure` and boto3 in
Jupyter notebooks.

---

## Problem: NoCredentialsError in Jupyter Notebook

### Symptoms

```text
NoCredentialsError: Unable to locate credentials
```

Occurs when invoking AWS services via boto3 in a notebook, even after
successfully running `aws login` in the terminal.

### Root Cause

Jupyter notebook kernels run in separate Python processes that don't
automatically access credentials cached by `aws login`. Credentials are stored
in `~/.aws/login/cache/` but boto3 doesn't read this location by default.

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

Use `aws configure` for persistent credentials that work automatically with
boto3.

##### Get AWS Access Keys

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to: **IAM** → **Users** → **Your Username** → **Security
   Credentials**
3. Click **Create Access Key**
4. Select **Command Line Interface (CLI)**
5. Download or copy the **Access Key ID** and **Secret Access Key**
6. ⚠️ **Important**: Save these securely - you won't be able to see the secret
   key again

##### Configure AWS CLI

Run the interactive configuration:

```bash
aws configure
```

Enter the following when prompted:

```text
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-west-2
Default output format [None]: json
```

##### Verify Configuration

```bash
aws sts get-caller-identity
aws configure list
```

##### Use in Notebook

With `aws configure`, boto3 automatically reads credentials from
`~/.aws/credentials`. No special code needed:

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

## Problem: AccessDeniedException - IAM Permission Errors

### IAM Permission Error Symptoms

```text
An error occurred (AccessDeniedException) when calling the
CreateRepository operation: 
User: arn:aws:iam::ACCOUNT_ID:user/USERNAME is not authorized to perform: 
ecr:CreateRepository on resource:
arn:aws:ecr:REGION:ACCOUNT_ID:repository/REPO_NAME 
because no identity-based policy allows the ecr:CreateRepository action
```

Occurs when attempting AWS operations (e.g., creating ECR repositories, Lambda
functions) via CLI or boto3.

### IAM Permission Error Root Cause

Your IAM user lacks the necessary permissions to perform the requested AWS
operation. IAM permissions must be granted by an AWS administrator.

### IAM Permission Error Solution

**You cannot request permissions via CLI.** Permissions must be granted by
an AWS administrator.

#### Step 1: Identify Required Permissions

Determine which permissions you need based on the error message. For example:

- `ecr:CreateRepository` - Create ECR repositories
- `ecr:DescribeRepositories` - List repositories
- `ecr:GetAuthorizationToken` - Authenticate Docker pushes
- `ecr:PutImage` - Push Docker images

#### Step 2: Request Permissions from Administrator

Contact your AWS administrator and request one of the following:

##### Option A: Managed Policy (Recommended)

- Request attachment of the managed AWS policy
  `AmazonEC2ContainerRegistryFullAccess` to your IAM user

##### Option B: Custom Policy

- Provide your administrator with a custom policy document:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CreateRepository",
                "ecr:DescribeRepositories",
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Step 3: Alternative - Use AWS Console

If you have console access but not CLI permissions:

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to the service (e.g., ECR, Lambda)
3. Create resources through the web interface
4. Use the created resources in your code

##### Creating ECR Repository via Console

1. Go to [ECR Console](https://console.aws.amazon.com/ecr/)
2. Select your region
3. Click **Create repository**
4. Enter repository name
5. Click **Create repository**
6. Copy the repository URI for use in your code

### IAM Permission Verification

After permissions are granted:

```bash
# Test the operation that previously failed
aws ecr create-repository --repository-name test-repo --region us-east-1

# Verify your identity
aws sts get-caller-identity
```

### IAM Permission Edge Cases

**Partial Permissions:**

- You may have some ECR permissions but not others
- Check which specific action failed in the error message
- Request only the missing permissions

**Region-Specific Permissions:**

- Some policies may be region-specific
- Ensure permissions are granted for your target region

**Temporary Credentials:**

- If using `aws login`, ensure your session has sufficient permissions
- Re-authenticate if credentials expired

### What You Cannot Do

- ❌ Request permissions via CLI
- ❌ Grant yourself permissions
- ❌ Modify IAM policies without `iam:*` permissions

### What You Can Do

- ✅ Check your current permissions (if you have
  `iam:ListAttachedUserPolicies`)
- ✅ Use AWS Console if you have console access
- ✅ Contact your AWS administrator
- ✅ Use existing resources created by others

---

## Related Documentation

- [AWS Setup Guide](../AWS_SETUP.md) - Initial AWS CLI configuration
- [AWS CLI v2 Login Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/) -
  Understanding IAM permissions
