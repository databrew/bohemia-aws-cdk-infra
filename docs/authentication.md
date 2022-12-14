# Authenticate to AWS

Our team uses 2 AWS Accounts to isolate Development / Production Cycle:
- databrew-dev (Account No: 381386504386)
- databrew-prod (Account No: 354598940118)

## Checklists
1. To have access to the AWS accounts, you will be required to request access through joe@databrew.cc as the owner of the management account. Then we will review your access requirements to our AWS acounts.

2. Once access is given, go to our team's AWS Organizations Landing Page [here](https://databrewllc.awsapps.com/start#/)

3. Type in your login and temporary password, once logged reset your password

4. You will see this Landing Page once logged in

![authentication](/images/aws_org_lp.png)

In the landing page you will be able to `Assume a Role` to AWS, meaning that you will get temporary access (1 hour) for visiting the console or using Access Key and Secret Keys for programmatic access.

## Programmatic Access for RStudio
We would like our data analysts to have programmatic access to access AWS data.

Install AWS-Supported Library for R:
```r
install.packages("paws")
```

There are two options to have access to our resources
### Option 1: Copy Paste Access Key and Secret Access Key to RStudio Session

 `Click Command line or programmatic access` and you will see all the temporary keys in the option tab, copy paste it into your R Environment Variable. 
```r
Sys.setenv(
    AWS_ACCESS_KEY_ID = "your AWS access key",
    AWS_SECRET_ACCESS_KEY = "your AWS secret key",
    AWS_SESSION_TOKEN = "your session token",
    AWS_CREDENTIAL_EXPIRATION = "ISO 8601 expiration time" #don't change the cred expiration
)
```

### Option 2: Using Amazon SSO

To use this option, you will be required to have AWS CLI in your machine. Installation guide [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

AWS SSO (Single Sign-On) enables you to login using specified profile. You will need to specify the SSO settings to use in the AWS config file, log in to SSO using the AWS CLI, then tell Paws to use the profile.

1. Specify the SSO settings to use in the AWS config file in ~/.aws/config, e.g.

```
[profile dbrew-prod]
sso_start_url = https://databrewllc.awsapps.com/start
sso_region = us-east-1
sso_account_id = 354598940118
sso_role_name = PowerUserAccess # or access available to you
region = us-east-1
output = json
```

2. Log in to SSO using the AWS CLI.
```
aws sso login --profile dbrew-prod
```
Tell Paws to use the SSO profile. For alternate ways of specifying your profile, see the set profile section.
```R
Sys.setenv(AWS_PROFILE = "dbrew-prod")
```

## Testing your Access
Once logged in, you will be able to start accessing the AWS resources based on the privileges we granted you.
```r
# list all buckets in S3
library(paws)
s3 <- paws::s3()
s3$list_buckets()
```
If you are authenticated, you will get a retrun message listing all our S3 buckets
