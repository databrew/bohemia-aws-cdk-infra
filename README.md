
# DataBrew ECS Data Workflow
![example workflow](https://github.com/arytontediarjo/ecs-data-workflow/actions/workflows/deploy_to_prod.yml/badge.svg)  ![issues](https://img.shields.io/github/issues/arytontediarjo/ecs-data-workflow)

- Author: Aryton Tediarjo (atediarjo@gmail.com)
- Reviewer: Joe Brew (joe@databrew.cc)

## About
This repository is used for orchestrating Databrew data pipeline using AWS. This workflow utilizes Docker as that runs the each of the data stages from data collection, anomaly detection, data cleaning  and reporting to our business stakeholders. 

This workflow is made to remediate the current process of having one big AWS EC2 machine and change it to  a cheaper & scalabale alternative. 

Our team is using AWS CDK to spin up alll the required component using code (Infrastructure as Code)
## Documentation & Guidelines
1. [Access to DataBrew AWS Accounts](/docs/authentication.md)
2. [AWS Workflow Infrastructure](/docs/workflow_aws.md)
3. [Workflow CI/CD Process](/docs/workflow_cicd.md)
4. [Contributing Guidelines](/docs/contb.md)
5. [List of Key Terminology](/docs/terminology.md)

## Feature Request
Feature request will be done through team's Trello board

## Future Implementations
- How to add container dependencies (order of execution of each container)
- Streamline new image using config files
- Create test cases










