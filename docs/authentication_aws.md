# Authenticate to AWS

Our team uses 2 AWS Accounts to isolate Development / Production Cycle:
- databrew-dev (Account No: 381386504386)
- databrew-prod (Account No: 354598940118)

## Checklists
1. To have access to the AWS accounts, you will be required to request access through joe@databrew.cc as the owner of the management account. Then we will review your access requirements to our AWS acounts.

2. Once access is given, go to our team's AWS Organizations Landing Page [here](https://databrewllc.awsapps.com/start#/)

3. Type in your login and temporary password, once logged reset your password

4. You will see this Landing Page once logged in

![authentication](images/aws_org_lp.png)

In the landing page you will be able to `Assume a Role` to AWS, meaning that you will get temporary access (1 hour) for visiting the console or using Access Key and Secret Keys for programmatic access.

## Programmatic Access for RStudio
As we grow as a team, we would like our engineers and analyst to be able to have programmatic access to build dashboards or data reports. There are two ways you can be authenticated to our resources:

### Option 1: Copy Paste Access Key to RStudio

 `Click Command line or programmatic access` and you will see all the temporary keys in the option tab, copy paste it into your R Environment Variable. 
```r
Sys.setenv(
    AWS_ACCESS_KEY_ID = "your AWS access key",
    AWS_SECRET_ACCESS_KEY = "your AWS secret key",
    AWS_SESSION_TOKEN = "your session token",
    AWS_CREDENTIAL_EXPIRATION = "ISO 8601 expiration time" #don't change the cred expiration
)
```

### Option 2: Amazon SSO (Recommended)

Copy pasted from [R paws documentation](https://github.com/paws-r/paws/blob/main/docs/credentials.md)

To use AWS SSO to provide credentials for accessing AWS, you will need to specify the SSO settings to use in the AWS config file, log in to SSO using the AWS CLI, then tell Paws to use the profile.

1. Specify the SSO settings to use in the AWS config file in ~/.aws/config, e.g.

```
[profile my-dev-profile]
sso_start_url = https://my-sso-portal.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789011
sso_role_name = readOnly
region = us-west-2
output = json
```

2. Log in to SSO using the AWS CLI.
```
aws sso login --profile my-dev-profile
```
Tell Paws to use the SSO profile. For alternate ways of specifying your profile, see the set profile section.
```R
Sys.setenv(AWS_PROFILE = "my-dev-profile")
```
Once logged in, you will be able to start accessing the AWS resources based on the privileges we granted you.
```r
# list all buckets in S3
library(paws)
svc <- paws::s3()
s3$list_buckets()
```
It is highly recommended to use the R [`paws`](https://github.com/paws-r/paws) Library as it is actively supported by the AWS team with syntax similar to the AWS SDK