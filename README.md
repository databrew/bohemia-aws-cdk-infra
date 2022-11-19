
# DataBrew ECS Data Workflow
![example workflow](https://github.com/arytontediarjo/ecs-data-workflow/actions/workflows/deploy_to_prod.yml/badge.svg)  ![issues](https://img.shields.io/github/issues/arytontediarjo/ecs-data-workflow)

Author: Aryton Tediarjo (atediarjo@gmail.com)

Reviewer: Joe Brew (joe@databrew.cc)

## About:
This repository is used for orchestrating Databrew data pipeline using AWS. This workflow utilizes Docker as that runs the each of the data stages from data collection, anomaly detection, data cleaning  and reporting to our business stakeholders. 

This workflow is made to remediate the current process of having one big AWS EC2 machine and change it to  a cheaper & scalabale alternative. 

Our team is using AWS CDK to spin up alll the required component using code (Infrastructure as Code)
## Documentation:
![My Image](images/ecs_wf_v0.jpeg)
Check out our [terminology list](https://github.com/arytontediarjo/ecs-data-workflow/tree/main/docs/terminology.md) for more information

## Contributing Guidelines:
### Prerequisites
1. [Installing Python](https://www.python.org/downloads/)
2. [Getting started with AWS CDK for Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)

Before using this workflow, make sure that you have authenticated to AWS.

 (TODO: add documentation link on how to be authenticated to AWS)

### Clone Repository
```bash
git clone https://github.com/arytontediarjo/ecs-data-workflow.git
```
### Create new branch for your local development
```bash
git checkout -b [name_of_your_new_branch]
git push origin [name_of_your_new_branch]
```

### Change Management
 

1. [Adding Microservices](https://github.com/arytontediarjo/ecs-data-workflow/tree/main/docs/add_microservice.md)

### Provision to AWS Test Account / Pre-Deployment
1. After you push your changes to the new branch, create a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) towards the [dev_uat branch](https://github.com/arytontediarjo/ecs-data-workflow/tree/dev-uat). 
2. We will do code-review process before merging to dev_uat. 
3. Once code is reviewed, merge all the changes to dev_uat
4. Github Action will pick up the recent push and automatically run all the required CDK commands (synth, deploy) to provision all the resources to Test Account (Insert Account Number)
5. Team will be able review and to QA on the deployment in the Test Account

### Provision to AWS Prod Account / Deployment
Once deployment is tested in (Insert Account Number), create a PR to the [main branch](https://github.com/arytontediarjo/ecs-data-workflow/tree/main). We will do all final sanity checks before merging all the changes to the main branch (production branch)

## Feature Request
Feature request will be done through team's Trello board

## Future Implementations
- How to add container dependencies (order of execution of each container)
- Streamline new image using config files
- Create test cases










