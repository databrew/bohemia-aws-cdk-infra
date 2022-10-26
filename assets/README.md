# Data Workflow Assets
@author: Aryton Tediarjo (atediarjo@gmail.com)

This instruction is dedicated to interested Databrew Data Users who would like their workflow automated by our AWS Workflow. Under this asset directory, each folders represents microservices (Docker container) being deployed to the AWS ECS Cluster. One folder represents one container that is part of the ECS Cluster. 



## Getting Started
[Install Docker Desktop on Local Computer](https://docs.docker.com/desktop/)


## Build Docker Image
Use this [Dockerfile Reference](https://docs.docker.com/build/building/packaging/) to get familiar with Dockerfile

Once Dockerfile is built, run this command:
```zsh
docker build -t your_image_name .
```

## Testing Docker Image Locally
Before pushing to Dockerhub, create a local Docker container to test on your local computer.

```zsh
docker run your_image_name
```

On certain cases, if you need to test pass environment variables for AWS authentication you will be able to pass:
```zsh
docker run \
-e AWS_ACCESS_KEY=... \ 
-e AWS_SECRET_ACCESS_KEY=... \
-e AWS_SESSION_TOKEN=... \
-e AWS_REGION= 'us-east-1' \
-e .......
your_image_name
```

## Push to Dockerhub
Log in to DockerHub:
```zsh
docker login
```

Tag your created Image:
```
docker tag your_image_name databrew/your_image_name:latest
```

Push to Dockerhub:
```
docker push databrew/your_image_name:latest
```

## Create a PR to UAT Branch
Two checklist before pushing to UAT branch:

1. **Tested your Docker Image and Container locally**
2. **Pushed your Docker Image to DockerHub**

Once done, create a Git pull request to UAT branch where DevOps will be reviewing/validated your requests and see whether new instances or additional workflow is needed. 

## Docker Index
Refer to this Google Sheets (WILL BE ADDED) for all indexed and reviewed DataBrew Dockerhub Images
