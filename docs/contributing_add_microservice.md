# Adding Microservices / Container

For every Docker Images published in Dockerhub, append this function to [ecs_data_workflow_stack](https://github.com/arytontediarjo/ecs-data-workflow/blob/main/ecs_data_workflow/ecs_data_workflow_stack.py) to add microservice container to the ECS cluster.

```python

# this is extra environment variables added
# for authentication and namespacing S3 buckets
input_env = {
    "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
    "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')
}
odk_extraction_fargate_stack_test = FargateStack(
            self, 
            'dextract2',
            cluster=cluster,  ## name of cluster DON'T CHANGE
            dockerhub_image=[NAME OF DOCKER IMAGE IN DOCKERHUB], ## dockerhub image
            ecs_role=ecs_role, ## name of role used for ECS execution
            family="data-extraction-five-days", ## name of the task
            environment=input_env, ## environment passed to ECS
            cron_expr="rate(5 days)" ## cron job
        )
```
