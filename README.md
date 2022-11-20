
# DataBrew ECS Data Workflow
![example workflow](https://github.com/arytontediarjo/ecs-data-workflow/actions/workflows/deploy_to_prod.yml/badge.svg)  ![issues](https://img.shields.io/github/issues/arytontediarjo/ecs-data-workflow)

- Author: Aryton Tediarjo (atediarjo@gmail.com)
- Reviewer: Joe Brew (joe@databrew.cc)

## About
This repository is used for orchestrating Databrew data pipeline using AWS. This workflow utilizes Docker as that runs the each of the data stages from data collection, anomaly detection, data cleaning  and reporting to our business stakeholders. 

This workflow is made to remediate the current process of having one big AWS EC2 machine and change it to  a cheaper & scalabale alternative. 

Our team is using AWS CDK to spin up all the required infrastructure component using a Python script ([Infrastructure as Code](https://www.redhat.com/en/topics/automation/what-is-infrastructure-as-code-iac#:~:text=Infrastructure%20as%20Code%20(IaC)%20is,to%20edit%20and%20distribute%20configurations.))
## Documentation & Guidelines
1. [Access to DataBrew AWS Accounts](/docs/authentication.md)
2. [AWS Workflow Infrastructure](/docs/workflow_aws.md)
3. [Workflow CI/CD Process](/docs/workflow_cicd.md)
4. [Contributing Guidelines](/docs/contb.md)
5. [List of Key Terminology](/docs/terminology.md)
6. [Indexed Dockerhub Images](/docs/dockerhub_index.md)

## Product Feature Request
Feature request will be done through [DataBrew Trello Board](https://trello.com/b/QS7U1jAJ/databrew)










