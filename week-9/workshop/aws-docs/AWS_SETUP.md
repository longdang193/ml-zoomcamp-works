# AWS Setup Guide

Quick guide to authenticate with AWS using `aws login` (similar to `az login` for Azure).

## Prerequisites

- AWS account
- AWS CLI v2 installed (check with `aws --version`)

## Setup Steps

1. **Set your default region**:

   ```bash
   aws configure set region us-east-1
   ```

   Common regions: `us-east-1`, `us-west-2`, `eu-west-1`, `ap-southeast-1`

2. **Login**:

   ```bash
   aws login
   ```

   - Browser will open automatically
   - If not, copy the URL from terminal output
   - Sign in with your AWS Console credentials

3. **Verify**:

   ```bash
   aws sts get-caller-identity
   ```

## Advantages

- No access keys needed
- Uses existing console credentials
- Browser-based authentication
- Credentials refresh automatically

## Troubleshooting

**"You must specify a region"**

```bash
aws configure set region us-east-1
```

**Browser doesn't open**

- Copy the URL from terminal output and paste in browser

**Verify configuration**

```bash
aws configure list
```
