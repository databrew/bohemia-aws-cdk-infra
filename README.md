
# DataBrew ECS Data Workflow
![example workflow](https://github.com/arytontediarjo/ecs-data-workflow/actions/workflows/deploy_to_prod.yml/badge.svg)  ![issues](https://img.shields.io/github/issues/arytontediarjo/ecs-data-workflow)

Author: Aryton Tediarjo (atediarjo@gmail.com)

Reviewer: Joe Brew (joe@databrew.cc)

## About
This repository is used for creating ECS Data Workflows for DataBrew Projects. 
It consists of two systems requirements:
- [Installing AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html)
- [Installing Docker](https://docs.docker.com/engine/install/)

This Github repository uses AWS CDK as IaC tooling to automatically provision AWS resources using code. The CDK will point towards a Docker Image in Dockerhub to create scheduled tasks for day to day use-cases. 

## Workflow
![My Image](images/ecs_wf_v0.jpeg)

To start, clone this repository
```bash
git clone https://github.com/arytontediarjo/ecs-data-workflow.git
```

Based on two types of users:

**Data Scientists / Analysts Workflows**: 

1. Create a new git branch (don't name it **dev-uat** as it is used for provisioning to dev account)

2. Create a new folder of the analysis or process inside the  **./assets** folder

3. Create R Project based on the newly created folder

4. Create Dockerfiles in each folder to help reproduce your analysis/script environment into the data workflow - more info in [Docker Assets Documentation](https://github.com/arytontediarjo/ecs-data-workflow/blob/main/assets/README.md)

4. Push Docker Image to DataBrew Dockerhub

5. Create PR to **dev-uat** branch and assign to atediarjo@gmail.com and joe@databrew.cc

6. For every Docker Images published in Dockerhub, append this function to [ecs_data_workflow_stack](https://github.com/arytontediarjo/ecs-data-workflow/blob/main/ecs_data_workflow/ecs_data_workflow_stack.py) to add microservice container to the ECS cluster.

```python
odk_extraction_fargate_stack_test = FargateStack(
            self, 
            'dextract2',
            cluster=cluster,  ## name of cluster DON'T CHANGE
            dockerhub_image="aryton/databrew-wf-data-extraction", ## dockerhub image
            ecs_role=ecs_role, ## name of role used for ECS execution
            family="data-extraction-five-days", ## name of the task
            environment={
                "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
                "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')}, ## environment passed to ECS
            cron_expr="rate(5 days)" ## cron job
        )
```

**DevOPS**

1. Review incoming PR from uat-dev from users

2. Merge PR to uat-dev branch for doing testing

3. TODO: create UAT checklist

## Feature Request
Trello?

## Future Implementations
- How to add container dependencies (order of execution of each container)
- Streamline new container indexing
- Create test cases










