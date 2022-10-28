# Description: 
# - This script is used for extracting data from ODK Postgres and save it to 
# DataBrew S3 bucket
#
# Author: Aryton Tediarjo (atediarjo@gmail.com)

library(ruODK)
library(dplyr)
library(lubridate)
library(magrittr)
library(aws.s3)
library(paws)
library(config)
source("R/utils.R")

# configuration
conf <- config::get()

# add in credentials
credentials_path <- "~/.bohemia_credentials"
credentials_check(credentials_path)
creds <- yaml::yaml.load_file(Sys.getenv('bohemia_credentials'))

# get s3 object
s3obj <- paws::s3()

# name of the bucket in S3
bucket_name <- glue::glue(Sys.getenv('BUCKET_PREFIX'), conf$bucket_name)
create_s3_bucket(s3obj, bucket_name)

# Establish a prefix (folder on AWS for saving everything)
prefix <- paste0(gsub(
  'https://', '',
  creds$url,
  fixed = TRUE), '/',
  creds$project_name, '/')

folder <- conf$bucket_folder

# Get the time
st <- lubridate::now() %>%
  as.Date() %>%
  as.character()

# get form metadata list
fid_list <- get_form_list() %>%
  .$fid

# parse through data list
# retrieve data one by one to not overload RAM usage in Fargate
purrr::map(fid_list, function(fid){
  bucket_path <- glue::glue('{prefix}{folder}/{fid}/{fid}.csv')
  data <- retrieve_data_from_central(fids = fid)
  data %>%
    save_object_to_s3(
      s3obj = s3obj,
      robject = .,
      bucket = bucket_name,
      bucket_path = bucket_path)
  })


