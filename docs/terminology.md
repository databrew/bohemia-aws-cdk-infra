## Terminology

# Added terminology

1. [**AWS CDK**](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html): Short for AWS Cloud Development Kit. This tool enables user to provision AWS resources in a form of code (Infrastructure as Code, IaC). It takes in scripts that are created by users and synthesizes it into a **CloudFormation Template** (think of it as a recipe for your application)

2. [**CloudFormation Template**](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html): This is a yaml configuration file that is used to deploy all your resources in 1-click

3. [**CI/CD**](https://www.redhat.com/en/topics/devops/what-is-ci-cd): Short for Continuous Integration / Continuous Deployment. This is a process to iteratively test your app before every deployment. In our case, we would like to be able to test our deployment in a development account before deploying to production account

4. [**Github Actions**](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions): Yaml files used to run pre-defined bash commands after you push to certain branch. Github Actions are used to automatically provision to dev/prod AWS accounts based on the branch that we are pushing towards.

5. [**Dockerhub**](https://www.docker.com/products/docker-hub/): This is where all our docker images / microservices is stored. Our scripts will refer to each desired published Docker image and put it to our Cloudformation Template