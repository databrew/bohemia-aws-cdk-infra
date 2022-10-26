# create bucket
create_s3_bucket <- function(s3obj, bucket_name){
  bucket_list <- s3obj$list_buckets() %>%
    .$Buckets %>%
    purrr::map_dfr(function(b){b})
  if(!bucket_name %in% bucket_list$Name){
    s3obj$create_bucket(Bucket = bucket_name)
    message(glue::glue("LOG:{bucket_name} created"))

    s3obj$put_bucket_versioning(Bucket = bucket_name, VersioningConfiguration = list(Status = 'Enabled'))
    message(glue::glue("LOG:{bucket_name} versioning enabled"))

  }else{
    message(glue::glue("LOG: {bucket_name} is available"))
  }
}




# save object to S3
save_object_to_s3 <- function(s3obj, robject, bucket, bucket_path, fileext = ".csv"){
  # convert to file
  file_path <- tempfile(fileext = fileext)
  save(robject, file = file_path)

  tryCatch({
    # Upload to bucket
    s3obj$put_object(Bucket = bucket, Body = file_path, Key = bucket_path)
  })
  message('Uploaded ', file_path, ' to ', bucket, 'with URI:', bucket_path)
}


#' Credentials check
#'
#' Check on or create credentials. If a credentials_path argument is supplied, this function will set the bohemia_credentials environment variable to that path; if it is not supplied, this function will do the same, but will first prompt a few fields so as to create the credentials file.
#' @param credentials_path Path to a bohemia_credentials.yaml file
#' @return A credentials file will be created and a bohemia_credentials environment variable will be set
#' @export
#' @import yaml

credentials_check <- function(credentials_path = NULL){

  # If a path was given, confirm that it's the path they want
  if(is.null(credentials_path)){
    out <- menu(choices = c('Yes', 'No, stop.'),
                title = 'You did not supply a path to a credentials file. Would you like to make one now?')

    if(out == 1){
      url <- ''
      while(nchar(url) < 1){
        url <- readline(prompt="ODK Central server (include https://): ")
      }

      project_name <- ''
      while(nchar(project_name) < 1){
        project_name <- readline(prompt="ODK Central project_name: ")
      }

      un <- ''
      while(nchar(un) < 1){
        un <- readline(prompt="ODK Central user email: ")
      }

      pw <- ''
      while(nchar(pw) < 1){
        pw <- readline(prompt="ODK Central user password: ")
      }

      backup_pw <- readline(prompt="ODK Central password for backups: ")


      agg_url <- ''
      while(nchar(agg_url) < 1){
        agg_url <- readline(prompt="ODK Aggregate server (include https://): ")
      }

      agg_un <- ''
      while(nchar(agg_un) < 1){
        agg_un <- readline(prompt="ODK Aggregate user name: ")
      }

      agg_pw <- ''
      while(nchar(agg_pw) < 1){
        agg_pw <- readline(prompt="ODK Aggregate user password: ")
      }

      briefcase_directory <- ''
      while(nchar(briefcase_directory) < 1){
        briefcase_directory <- readline(prompt="ODK Aggregate briefcase directory: ")
      }

      aws_access_key_id <- ''
      while(nchar(aws_access_key_id) < 1){
        aws_access_key_id <- readline(prompt="AWS S3 Access key ID: ")
      }

      aws_secret_access_key <- ''
      while(nchar(aws_secret_access_key) < 1){
        aws_secret_access_key <- readline(prompt="AWS S3 Secret access key: ")
      }

      message('Great! You have set up the following credentials.')
      message('---ODK Central server: ', url)
      message('---ODK Central project name: ', project_name)
      message('---ODK Central user: ', un)
      message('---ODK Central pass: ', pw)
      message('---ODK Central backup pass: ', backup_pw)
      message('---ODK Aggregate server : ', agg_url)
      message('---ODK Aggregate user : ', agg_un)
      message('---ODK Aggregate password : ', agg_pw)
      message('---ODK Aggregate briefcase directory: ', briefcase_directory)
      message('---AWS S3 Access key ID: ', aws_access_key_id)
      message('---AWS S3 Secrety access key: ', aws_secret_access_key)

      is_ok <- FALSE
      while(!is_ok){
        write_to <- readline(prompt = 'In which folder would you like to write your bohemia_credentials.yaml file (type the folder path)? ')
        is_ok <- dir.exists(write_to)
      }
      yaml_lines <-
        c(paste0('url: ', url),
          paste0('project_name: ', project_name),
          paste0('un: ', un),
          paste0('pw: ', pw),
          paste0('backup_pw: ', backup_pw),
          paste0('agg_url: ', agg_url),
          paste0('agg_un: ', agg_un),
          paste0('agg_pw: ', agg_pw),
          paste0('briefcase_directory: ', briefcase_directory),
          paste0('aws_access_key_id: ', aws_access_key_id),
          paste0('aws_secret_access_key: ', aws_secret_access_key),
          paste0('aws_default_region_name: "eu-west-3"'),
          c(''))
      out_file <- file.path(write_to, 'bohemia_credentials.yaml')
      conn <- file(out_file)
      writeLines(text = yaml_lines,
                 con = conn)
      close(conn)
      message('Successfully wrote a file to ', out_file)
      credentials_path <- out_file
    } else {
      stop('Okay, stopping.')
    }
  }

  message('Going to set the bohemia_credentials environment variable to ', credentials_path)
  Sys.setenv('bohemia_credentials'=credentials_path)
  message('(done)')
}



#' Retrieve data from central
#'
#' Retrieve data from Central server
#' @param fids Form IDs for which data should be retrieved. If NULL, all
#' @param except_fids Form IDs to exclude from retrieval
#' @param clean_column_names Whether to clean the column names
#' @return A list
#' @export
#' @import ruODK
#' @import yaml
#' @import dplyr

retrieve_data_from_central <- function(fids = NULL,
                                       except_fids = NULL,
                                       clean_column_names = TRUE){

  # Make sure environment variables are sufficient
  environment_variables <- Sys.getenv()
  ok <- 'bohemia_credentials' %in% names(environment_variables)
  if(!ok){
    stop('You need to define a bohemia_credentials environment variable. Do this by runnning credentials_check("path/to/bohemia_credentials.yaml")')
  }
  bohemia_credentials <- Sys.getenv('bohemia_credentials')

  # Actually read in the credentials
  creds <- yaml::yaml.load_file(bohemia_credentials)

  # Set up some parameters
  ruODK::ru_setup(
    fid = NULL,
    # fid = 'ntd',
    url = creds$url,
    un = creds$un,
    pw = creds$pw,
    verbose = TRUE,
    tz = 'UTC'
  )
  project_name <- creds$project_name

  # Redefine project_list since ruODK function broke
  isodt_to_local <- function(datetime_string,
                             orders = c("YmdHMS", "YmdHMSz"),
                             tz = get_default_tz()) {
    datetime_string %>%
      lubridate::parse_date_time(orders = orders) %>%
      lubridate::with_tz(., tzone = tz)
  }
  get_project_list <- function (url = get_default_url(), un = get_default_un(), pw = get_default_pw(),
                                retries = get_retries(), orders = c("YmdHMS", "YmdHMSz",
                                                                    "Ymd HMS", "Ymd HMSz", "Ymd", "ymd"), tz = get_default_tz()) {
    require(ruODK)
    # yell_if_missing(url, un, pw)
    httr::RETRY("GET", httr::modify_url(url, path = glue::glue("v1/projects")),
                httr::add_headers(Accept = "application/xml", `X-Extended-Metadata` = "true"),
                httr::authenticate(un, pw), times = retries) %>%
      # yell_if_error(., url, un, pw) %>%
      httr::content(.) %>% tibble::tibble(.) %>%
      tidyr::unnest_wider(".", names_repair = "universal") %>%
      janitor::clean_names(.) %>% dplyr::mutate_at(dplyr::vars("last_submission",
                                                               "created_at",
                                                               "updated_at"#,
                                                               # "deleted_at" # this is the only change
      ), ~isodt_to_local(.,
                         orders = orders, tz = tz)) %>% {
                           if ("archived" %in% names(.)) {
                             dplyr::mutate(., archived = tidyr::replace_na(archived,
                                                                           FALSE))
                           }
                           else {
                             .
                           }
                         }
  }


  # List projects on the server
  # projects <- ruODK::project_list()
  projects <- get_project_list()

  # Define which project to use
  pid <- projects$id[projects$name == project_name]
  ruODK::ru_setup(pid = pid)

  # # Get a list of forms in the project
  # fl <- get_form_list()
  # fl <- ruODK::form_list() # this function stopped working in newer versions,
  # replacing here
  gfl  <- function(pid = get_default_pid(),
                   url = get_default_url(),
                   un = get_default_un(),
                   pw = get_default_pw(),
                   retries = get_retries(),
                   orders = c(
                     "YmdHMS",
                     "YmdHMSz",
                     "Ymd HMS",
                     "Ymd HMSz",
                     "Ymd",
                     "ymd"
                   ),
                   tz = get_default_tz()) {
    httr::RETRY(
      "GET",
      httr::modify_url(url, path = glue::glue("v1/projects/{pid}/forms")),
      httr::add_headers(
        "Accept" = "application/xml",
        "X-Extended-Metadata" = "true"
      ),
      httr::authenticate(un, pw),
      times = retries
    ) %>%
      httr::content(.) %>%
      tibble::tibble(.) %>%
      tidyr::unnest_wider(".", names_repair = "universal") %>%
      # tidyr::unnest_wider(
      #   "reviewStates",
      #   names_repair = "universal", names_sep = "_"
      # ) %>%
      # tidyr::unnest_wider(
      #   "createdBy",
      #   names_repair = "universal", names_sep = "_"
      # ) %>%
      janitor::clean_names() %>%
      dplyr::mutate_at(
        dplyr::vars(dplyr::contains("_at")), # assume datetimes are named "_at"
        ~ isodt_to_local(., orders = orders, tz = tz)
      ) %>%
      dplyr::mutate(fid = xml_form_id)
  }
  fl <- gfl()


  # Cut down to only the form IDs which are relevant
  if(!is.null(fids)){
    fl <- fl %>% filter(fid %in% fids)
  }
  # Remove the except ones
  if(!is.null(except_fids)){
    message('Not retrieving any data for: ', except_fids)
    fl <- fl %>% filter(!fid %in% except_fids)
  }
  if(nrow(fl) > 0){

    # Loop through each form ID and get the submission
    out_list <- list()
    for(i in 1:nrow(fl)){
      this_fid <- fl$fid[i]
      message('Form ', i, ' of ', nrow(fl), ': ', this_fid)

      # # Get the schema for the form
      # schema <- form_schema_ext(fid = this_fid)
      # schema_df <- schema %>% dplyr::select(ruodk_name, name, type)

      # New zip method
      td <- paste0('/tmp/odk/')
      if(dir.exists(td)){
        unlink(td, recursive = TRUE)
      }
      dir.create(td)
      ruODK::submission_export(
        local_dir = td,
        overwrite = TRUE,
        media = FALSE,
        repeats = TRUE,
        fid = this_fid,
        verbose = TRUE
      )
      # unzip the downloaded files
      ed <- paste0(td, 'unzipped/')
      zip_path <- paste0(td, this_fid, '.zip')
      unzip(zipfile = zip_path, exdir = ed)

      # Read in the downloaded files
      file_names <- dir(ed)
      data_list <- list()
      fid_list <- c()
      for(f in 1:length(file_names)){
        this_file_name <- file_names[f]
        this_sub_form <- gsub('.csv', '', this_file_name)
        # See if this is the main submission form or not
        is_main <- !grepl('-', this_sub_form)
        this_sub_form <- unlist(lapply(strsplit(this_sub_form, split = '-'), function(x){x[length(x)]}))
        if(is_main){
          this_sub_form <- 'Submissions'
        }
        fid_list <- c(fid_list, this_sub_form)
        file_path <- paste0(ed, this_file_name)
        this_data <- readr::read_csv(file_path, guess_max = Inf)
        # Clean the column names
        if(clean_column_names){
          names(this_data) <- unlist(lapply(strsplit(names(this_data), '-'), function(a){a[length(a)]}))
        }
        this_data$id <- this_data$KEY
        this_data <- janitor::clean_names(this_data)
        this_data <- this_data[,!duplicated(names(this_data))]
        data_list[[f]] <- this_data
      }
      names(data_list) <- fid_list
      out_list[[i]] <- data_list
    }
    names(out_list) <- fl$fid

    data_list <- out_list
    message('Returning a list of length ', length(data_list))
    return(data_list)
  } else {
    message('There are no forms with the IDs supplied. Returning an empty list')
    return(list())
  }
}



#' Retrieve data from central
#'
#' Retrieve data from Central server
#' @param fids Form IDs for which data should be retrieved. If NULL, all
#' @param except_fids Form IDs to exclude from retrieval
#' @param clean_column_names Whether to clean the column names
#' @return A list
#' @export
#' @import ruODK
#' @import yaml
#' @import dplyr

retrieve_data_from_central <- function(fids = NULL,
                                       except_fids = NULL,
                                       clean_column_names = TRUE){

  # Make sure environment variables are sufficient
  environment_variables <- Sys.getenv()
  ok <- 'bohemia_credentials' %in% names(environment_variables)
  if(!ok){
    stop('You need to define a bohemia_credentials environment variable. Do this by runnning credentials_check("path/to/bohemia_credentials.yaml")')
  }
  bohemia_credentials <- Sys.getenv('bohemia_credentials')

  # Actually read in the credentials
  creds <- yaml::yaml.load_file(bohemia_credentials)

  # Set up some parameters
  ruODK::ru_setup(
    fid = NULL,
    # fid = 'ntd',
    url = creds$url,
    un = creds$un,
    pw = creds$pw,
    verbose = TRUE,
    tz = 'UTC'
  )
  project_name <- creds$project_name

  # Redefine project_list since ruODK function broke
  isodt_to_local <- function(datetime_string,
                             orders = c("YmdHMS", "YmdHMSz"),
                             tz = get_default_tz()) {
    datetime_string %>%
      lubridate::parse_date_time(orders = orders) %>%
      lubridate::with_tz(., tzone = tz)
  }
  get_project_list <- function (url = get_default_url(), un = get_default_un(), pw = get_default_pw(),
                                retries = get_retries(), orders = c("YmdHMS", "YmdHMSz",
                                                                    "Ymd HMS", "Ymd HMSz", "Ymd", "ymd"), tz = get_default_tz()) {
    require(ruODK)
    # yell_if_missing(url, un, pw)
    httr::RETRY("GET", httr::modify_url(url, path = glue::glue("v1/projects")),
                httr::add_headers(Accept = "application/xml", `X-Extended-Metadata` = "true"),
                httr::authenticate(un, pw), times = retries) %>%
      # yell_if_error(., url, un, pw) %>%
      httr::content(.) %>% tibble::tibble(.) %>%
      tidyr::unnest_wider(".", names_repair = "universal") %>%
      janitor::clean_names(.) %>% dplyr::mutate_at(dplyr::vars("last_submission",
                                                               "created_at",
                                                               "updated_at"#,
                                                               # "deleted_at" # this is the only change
      ), ~isodt_to_local(.,
                         orders = orders, tz = tz)) %>% {
                           if ("archived" %in% names(.)) {
                             dplyr::mutate(., archived = tidyr::replace_na(archived,
                                                                           FALSE))
                           }
                           else {
                             .
                           }
                         }
  }


  # List projects on the server
  # projects <- ruODK::project_list()
  projects <- get_project_list()

  # Define which project to use
  pid <- projects$id[projects$name == project_name]
  ruODK::ru_setup(pid = pid)

  # # Get a list of forms in the project
  # fl <- get_form_list()
  # fl <- ruODK::form_list() # this function stopped working in newer versions,
  # replacing here
  gfl  <- function(pid = get_default_pid(),
                   url = get_default_url(),
                   un = get_default_un(),
                   pw = get_default_pw(),
                   retries = get_retries(),
                   orders = c(
                     "YmdHMS",
                     "YmdHMSz",
                     "Ymd HMS",
                     "Ymd HMSz",
                     "Ymd",
                     "ymd"
                   ),
                   tz = get_default_tz()) {
    httr::RETRY(
      "GET",
      httr::modify_url(url, path = glue::glue("v1/projects/{pid}/forms")),
      httr::add_headers(
        "Accept" = "application/xml",
        "X-Extended-Metadata" = "true"
      ),
      httr::authenticate(un, pw),
      times = retries
    ) %>%
      httr::content(.) %>%
      tibble::tibble(.) %>%
      tidyr::unnest_wider(".", names_repair = "universal") %>%
      # tidyr::unnest_wider(
      #   "reviewStates",
      #   names_repair = "universal", names_sep = "_"
      # ) %>%
      # tidyr::unnest_wider(
      #   "createdBy",
      #   names_repair = "universal", names_sep = "_"
      # ) %>%
      janitor::clean_names() %>%
      dplyr::mutate_at(
        dplyr::vars(dplyr::contains("_at")), # assume datetimes are named "_at"
        ~ isodt_to_local(., orders = orders, tz = tz)
      ) %>%
      dplyr::mutate(fid = xml_form_id)
  }
  fl <- gfl()


  # Cut down to only the form IDs which are relevant
  if(!is.null(fids)){
    fl <- fl %>% filter(fid %in% fids)
  }
  # Remove the except ones
  if(!is.null(except_fids)){
    message('Not retrieving any data for: ', except_fids)
    fl <- fl %>% filter(!fid %in% except_fids)
  }
  if(nrow(fl) > 0){

    # Loop through each form ID and get the submission
    out_list <- list()
    for(i in 1:nrow(fl)){
      this_fid <- fl$fid[i]
      message('Form ', i, ' of ', nrow(fl), ': ', this_fid)

      # # Get the schema for the form
      # schema <- form_schema_ext(fid = this_fid)
      # schema_df <- schema %>% dplyr::select(ruodk_name, name, type)

      # New zip method
      td <- paste0('/tmp/odk/')
      if(dir.exists(td)){
        unlink(td, recursive = TRUE)
      }
      dir.create(td)
      ruODK::submission_export(
        local_dir = td,
        overwrite = TRUE,
        media = FALSE,
        repeats = TRUE,
        fid = this_fid,
        verbose = TRUE
      )
      # unzip the downloaded files
      ed <- paste0(td, 'unzipped/')
      zip_path <- paste0(td, this_fid, '.zip')
      unzip(zipfile = zip_path, exdir = ed)

      # Read in the downloaded files
      file_names <- dir(ed)
      data_list <- list()
      fid_list <- c()
      for(f in 1:length(file_names)){
        this_file_name <- file_names[f]
        this_sub_form <- gsub('.csv', '', this_file_name)
        # See if this is the main submission form or not
        is_main <- !grepl('-', this_sub_form)
        this_sub_form <- unlist(lapply(strsplit(this_sub_form, split = '-'), function(x){x[length(x)]}))
        if(is_main){
          this_sub_form <- 'Submissions'
        }
        fid_list <- c(fid_list, this_sub_form)
        file_path <- paste0(ed, this_file_name)
        this_data <- readr::read_csv(file_path, guess_max = Inf)
        # Clean the column names
        if(clean_column_names){
          names(this_data) <- unlist(lapply(strsplit(names(this_data), '-'), function(a){a[length(a)]}))
        }
        this_data$id <- this_data$KEY
        this_data <- janitor::clean_names(this_data)
        this_data <- this_data[,!duplicated(names(this_data))]
        data_list[[f]] <- this_data
      }
      names(data_list) <- fid_list
      out_list[[i]] <- data_list
    }
    names(out_list) <- fl$fid

    data_list <- out_list
    message('Returning a list of length ', length(data_list))
    return(data_list)
  } else {
    message('There are no forms with the IDs supplied. Returning an empty list')
    return(list())
  }
}


#' Get form list
#'
#' Retrieve a dataframe of forms on the Central server
#' @return A list
#' @export
#' @import ruODK
#' @import yaml
#' @import dplyr

get_form_list <- function(){

  # Make sure environment variables are sufficient
  environment_variables <- Sys.getenv()
  ok <- 'bohemia_credentials' %in% names(environment_variables)
  if(!ok){
    stop('You need to define a bohemia_credentials environment variable. Do this by runnning credentials_check("path/to/bohemia_credentials.yaml")')
  }
  bohemia_credentials <- Sys.getenv('bohemia_credentials')

  # Actually read in the credentials
  creds <- yaml::yaml.load_file(bohemia_credentials)

  # Set up some parameters
  ruODK::ru_setup(
    fid = NULL,
    # fid = 'ntd',
    url = creds$url,
    un = creds$un,
    pw = creds$pw,
    verbose = TRUE,
    tz = 'UTC'
  )
  project_name <- creds$project_name

  # List projects on the server
  projects <- ruODK::project_list()

  # Define which project to use
  pid <- projects$id[projects$name == project_name]
  ruODK::ru_setup(pid = pid)

  # # Get a list of forms in the project
  fl <- ruODK::form_list()
  return(fl)
}




