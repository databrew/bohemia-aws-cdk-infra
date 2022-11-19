# Contributing Guidelines

## Prerequisites
1. [Installing Python](https://www.python.org/downloads/)
2. [Getting started with AWS CDK for Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)

## How to get started
### Clone Repository
```bash
git clone https://github.com/arytontediarjo/ecs-data-workflow.git
```
### Create new branch for your local development
```bash
git checkout -b [name_of_your_new_branch]
git push origin [name_of_your_new_branch]
```

**Note**: Please do not remove `dev_uat` branch as it is used for user acceptance testing in our dev account

### Making Changes in new feature branch
Most of the workflow is being run under the [ecs_data_workflow folder](/ecs_data_workflow/ecs_data_workflow_stack.py), to make any modifications, you will be able to edit each of the stacks. Stacks are list of AWS resources (called constructs in CDK term) you are planning to provision. 

- To remove a resource, you can remove it from the code.
- To add a resource, refer to this [documentation](https://docs.aws.amazon.com/cdk/api/v1/python/index.html)

### Provision to AWS Test Account / Pre-Deployment
1. After you push your changes to the new branch, create a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) towards the [dev_uat branch](https://github.com/arytontediarjo/ecs-data-workflow/tree/dev-uat). 
2. We will do code-review process before merging to dev_uat. 
3. Once code is reviewed, merge all the changes to dev_uat
4. Github Action will pick up the recent push and automatically run all the required CDK commands (synth, deploy) to provision all the resources to Test Account (Insert Account Number)
5. Team will be able review and to QA on the deployment in the Test Account

### Provision to AWS Prod Account / Deployment
Once deployment is tested in (Insert Account Number), create a PR to the [main branch](https://github.com/arytontediarjo/ecs-data-workflow/tree/main). We will do all final sanity checks before merging all the changes to the main branch (production branch)