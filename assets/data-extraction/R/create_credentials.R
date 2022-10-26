library(yaml)
library(paws)
library(magrittr)
library(config)
library(aws.s3)


message("Log Message: creating credentials")

# get ODK credentials from secrets manager
svc  <- paws::secretsmanager()
creds <- svc$get_secret_value(Sys.getenv('ODK_CREDENTIALS_SECRETS_NAME')) %>%
  .$SecretString %>%
  jsonlite::parse_json(.)

# write to yaml file as . systems file
out <- list(
  url= config::get("odk_endpoint"),
  project_name= config::get("odk_project_name"),
  un= creds$username,
  pw= creds$password
)

# write to yaml
yaml::write_yaml(out, "~/.bohemia_credentials")
message("Log Message: credentials created")




