# AWS Troubleshooting Guide

## Purpose

Quick reference for resolving common AWS credential and permission issues when using boto3 in Jupyter notebooks.

## Target Audience

Developers using AWS CLI with `aws login` or `aws configure` and boto3 in Jupyter notebooks.

---

## Problem: NoCredentialsError in Jupyter Notebook

### Symptoms

```text
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

#### Option 2: AWS Configure (Recommended)

Use `aws configure` for persistent credentials that work automatically with boto3. See [AWS Setup Guide](AWS_SETUP.md) for detailed instructions.

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
An error occurred (AccessDeniedException) when calling the CreateRepository operation:
User: arn:aws:iam::ACCOUNT_ID:user/USERNAME is not authorized to perform:
ecr:CreateRepository on resource: arn:aws:ecr:REGION:ACCOUNT_ID:repository/REPO_NAME
because no identity-based policy allows the ecr:CreateRepository action
```

Occurs when attempting AWS operations (e.g., creating ECR repositories, Lambda functions) via CLI or boto3.

### IAM Permission Error Root Cause

Your IAM user lacks the necessary permissions to perform the requested AWS operation. IAM permissions must be granted by an AWS administrator.

### IAM Permission Error Solution

**You cannot request permissions via CLI.** Permissions must be granted by an AWS administrator.

#### Step 1: Identify Required Permissions

Determine which permissions you need based on the error message. Common examples:

- `ecr:CreateRepository` - Create ECR repositories
- `ecr:DescribeRepositories` - List repositories
- `ecr:GetAuthorizationToken` - Authenticate Docker pushes
- `ecr:PutImage` - Push Docker images
- `lambda:CreateFunction` - Create Lambda functions
- `iam:CreateRole` - Create IAM roles

#### Step 2: Request Permissions from Administrator

Contact your AWS administrator and request one of the following:

#### Option A: Managed Policy (Recommended)

Request attachment of the appropriate managed AWS policy to your IAM user:

- `AmazonEC2ContainerRegistryFullAccess` - For ECR operations
- `AWSLambda_FullAccess` - For Lambda operations

#### Option B: Custom Policy

Provide your administrator with a custom policy document:

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

**Creating ECR Repository via Console:**

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

- You may have some permissions but not others
- Check which specific action failed in the error message
- Request only the missing permissions

**Region-Specific Permissions:**

- Some policies may be region-specific
- Ensure permissions are granted for your target region

**Temporary Credentials:**

- If using `aws login`, ensure your session has sufficient permissions
- Re-authenticate if credentials expired

**Existing Resources:**

- If a role or resource already exists, use it instead of creating a new one
- Check existing resources before requesting creation permissions

### What You Cannot Do

- ❌ Request permissions via CLI
- ❌ Grant yourself permissions
- ❌ Modify IAM policies without `iam:*` permissions

### What You Can Do

- ✅ Check your current permissions (if you have `iam:ListAttachedUserPolicies`)
- ✅ Use AWS Console if you have console access
- ✅ Contact your AWS administrator
- ✅ Use existing resources created by others

---

## Problem: ModuleNotFoundError for TensorFlow After Installation

### TensorFlow Import Error Symptoms

```text
ModuleNotFoundError: No module named 'tensorflow'
```

Occurs in Jupyter notebook even after running `%pip install tensorflow` and restarting the kernel.

### TensorFlow Import Error Root Cause

Jupyter notebook kernels may use a different Python environment (virtual environment) than the system Python where TensorFlow was installed. The kernel's Python interpreter doesn't have access to packages installed in other environments.

### TensorFlow Import Error Solution

#### Step 1: Identify the Kernel's Python Environment

Check which Python your notebook kernel is using:

```python
import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path[0])
```

#### Step 2: Install TensorFlow in the Correct Environment

Install TensorFlow directly in the kernel's Python environment:

#### Option A: Using %pip in Notebook (Recommended)

```python
# This installs in the kernel's environment
%pip install tensorflow
```

#### Option B: Install via Command Line

If `%pip install` doesn't work, install using the kernel's Python directly:

```bash
# Find the kernel's Python path from Step 1, then:
/path/to/kernel/python -m pip install tensorflow
```

#### Option C: Install pip First (If Missing)

If the virtual environment doesn't have pip:

```bash
/path/to/kernel/python -m ensurepip --upgrade
/path/to/kernel/python -m pip install tensorflow
```

#### Step 3: Restart Kernel

After installation, restart the Jupyter kernel:

1. Go to **Kernel** → **Restart Kernel**
2. Re-run the installation cell
3. Re-run the import cell

### TensorFlow Import Verification

After restarting the kernel:

```python
try:
    import tensorflow as tf
    print(f"✓ TensorFlow version: {tf.__version__}")
    print(f"✓ TensorFlow location: {tf.__file__}")
except ImportError as e:
    print(f"✗ TensorFlow not found: {e}")
```

### TensorFlow Import Edge Cases

**Virtual Environment Without pip:**

- Some virtual environments are created without pip
- Use `python -m ensurepip --upgrade` to install pip first
- Then install TensorFlow

**Multiple Python Environments:**

- System Python may have TensorFlow, but kernel uses a different environment
- Always install in the kernel's environment, not system Python
- Check `sys.executable` to confirm the correct path

**Kernel Using Symlinked Python:**

- Virtual environment may symlink to system Python but have separate site-packages
- Install directly in the virtual environment's site-packages directory

### TensorFlow Import Alternative Solutions

#### Option 1: Use Pre-converted Models

Skip TensorFlow installation entirely by downloading pre-converted ONNX models instead of converting Keras models locally.

#### Option 2: Use Docker for Conversion

Run TensorFlow model conversion in a Docker container to avoid environment conflicts.

---

## Problem: AccessDenied When Attaching Policy to Existing IAM Role

### IAM Role Policy Attachment Error Symptoms

```text
An error occurred (AccessDenied) when calling the AttachRolePolicy operation:
User: arn:aws:iam::ACCOUNT_ID:user/USERNAME is not authorized to perform:
iam:AttachRolePolicy on resource: role ROLE_NAME
because no identity-based policy allows the iam:AttachRolePolicy action
```

Occurs when trying to attach policies to an IAM role that already exists, even though you can read the role.

### IAM Role Policy Attachment Root Cause

You have read permissions for the IAM role (`iam:GetRole`) but lack write permissions (`iam:AttachRolePolicy`, `iam:DetachRolePolicy`). The role may already have the required policies attached, making modification unnecessary.

### IAM Role Policy Attachment Solution

#### Step 1: Check if Role Already Has Required Policies

List the policies attached to the role:

```bash
aws iam list-attached-role-policies --role-name ROLE_NAME
aws iam list-role-policies --role-name ROLE_NAME
```

Check if the role already has the policy you're trying to attach (e.g., `AWSLambdaBasicExecutionRole`).

#### Step 2: Use the Existing Role

If the role already exists with the necessary policies, **skip the creation/attachment steps** and use the existing role:

```bash
# Get the role ARN (only requires read permission)
ROLE_ARN=$(aws iam get-role --role-name ROLE_NAME --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"

# Use this ARN when creating Lambda function
aws lambda create-function \
  --function-name your-function \
  --role "${ROLE_ARN}" \
  ...
```

#### Step 3: Request Permissions (If Modification Needed)

If you need to modify the role and don't have permissions:

1. **Check what's missing:** Verify which policies the role needs
2. **Contact administrator:** Request `iam:AttachRolePolicy` and `iam:DetachRolePolicy` permissions
3. **Use console:** If you have console access, modify the role through the AWS Console

### IAM Role Policy Attachment Verification

Verify the role has the required policies:

```bash
# List attached managed policies
aws iam list-attached-role-policies --role-name ROLE_NAME

# Check for specific policy
aws iam get-role-policy \
  --role-name ROLE_NAME \
  --policy-name POLICY_NAME
```

### IAM Role Policy Attachment Edge Cases

**Role Exists But Missing Policies:**

- Role may exist but lack required policies
- You need `iam:AttachRolePolicy` permission to add policies
- Contact administrator or use AWS Console if available

**Read-Only Access:**

- You can read roles but not modify them
- This is common in shared AWS accounts
- Use existing roles as-is or request modification permissions

**Role Created by Administrator:**

- Administrator may have created the role with all necessary policies
- Check existing policies before attempting to attach new ones
- Use the role as-is if it meets your requirements

### IAM Role Policy Attachment - What You Cannot Do

- ❌ Attach policies without `iam:AttachRolePolicy` permission
- ❌ Detach policies without `iam:DetachRolePolicy` permission
- ❌ Modify role trust policy without `iam:UpdateAssumeRolePolicy` permission

### IAM Role Policy Attachment - What You Can Do

- ✅ Read role information and ARN (with `iam:GetRole`)
- ✅ List attached policies (with `iam:ListAttachedRolePolicies`)
- ✅ Use existing roles in Lambda functions
- ✅ Request modification permissions from administrator
- ✅ Use AWS Console if you have console access

---

## Problem: ImportError When Converting TensorFlow Model to ONNX

### Protobuf Import Error Symptoms

```text
ImportError: cannot import name 'runtime_version' from 'google.protobuf'
```

Occurs when running `tf2onnx.convert` to convert a TensorFlow SavedModel to ONNX format, even after successfully installing TensorFlow and tf2onnx.

### Protobuf Import Error Root Cause

Version conflict between protobuf, TensorFlow, and tf2onnx:

- TensorFlow 2.20.0 requires `protobuf >= 5.28.0`
- tf2onnx declares `protobuf~=3.20` as a dependency
- Your environment has protobuf 3.20.3, which is too old for TensorFlow

### Protobuf Import Error Solution

#### Step 1: Upgrade Protobuf

Upgrade protobuf to a version compatible with TensorFlow:

```bash
# If using a virtual environment, activate it first
/path/to/venv/bin/python -m pip install --upgrade 'protobuf>=5.28.0'

# Or in Jupyter notebook:
%pip install --upgrade 'protobuf>=5.28.0'
```

#### Step 2: Verify TensorFlow Works

Test that TensorFlow can import successfully:

```python
import tensorflow as tf
print(f"✓ TensorFlow version: {tf.__version__}")
```

#### Step 3: Verify tf2onnx Works

Despite the dependency warning, tf2onnx works with newer protobuf:

```python
import tf2onnx
print("✓ tf2onnx imports successfully")
```

#### Step 4: Restart Kernel

After upgrading protobuf, restart the Jupyter kernel:

1. Go to **Kernel** → **Restart Kernel**
2. Re-run the conversion cell

### Protobuf Import Error Verification

After upgrading protobuf and restarting the kernel, the conversion should work:

```bash
python -m tf2onnx.convert \
    --saved-model lambda-keras/clothing-model-new_savedmodel \
    --opset 13 \
    --output lambda-keras/clothing-model-new.onnx
```

### Protobuf Import Error Edge Cases

**Dependency Warning:**

- You may see: `tf2onnx 1.16.1 requires protobuf~=3.20, but you have protobuf 6.33.2`
- This is a warning, not an error
- tf2onnx works with protobuf 6.33.2 despite the declared dependency
- The dependency declaration is conservative

**Virtual Environment:**

- Ensure you upgrade protobuf in the same environment where TensorFlow and tf2onnx are installed
- Check which Python environment your kernel uses: `import sys; print(sys.executable)`
- Install protobuf in that specific environment

**Multiple Protobuf Versions:**

- Different packages may have conflicting protobuf requirements
- Upgrade to the highest required version (protobuf >= 5.28.0 for TensorFlow 2.20.0)
- Test that all packages work together

### Protobuf Import Error Alternative Solutions

#### Option 1: Use Docker for Conversion

Avoid version conflicts by using Docker for the conversion process. See README.md for Docker-based conversion steps.

#### Option 2: Use Pre-converted Models

Download pre-converted ONNX models instead of converting locally to avoid dependency issues entirely.

---

## Related Documentation

- [AWS Setup Guide](AWS_SETUP.md) - Initial AWS CLI configuration
- [AWS CLI v2 Login Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/) - Understanding IAM permissions
