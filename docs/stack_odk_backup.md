## ODK Central Backup

### Creating Backup Snapshot via Python

Code for snapshotting state of ODK can be found in this [Lambda Function](../lambda/odk_backup/lambda_function.py). This lambda function utilizes ODK Backup API to capture the state of databrew.org every **12.00 AM EAT (East African Time)**. Each Backup will be in a `.zip` file format. 

Backup will be stored [here](https://s3.console.aws.amazon.com/s3/buckets/odkbackupstack-odkbackups3bucket7f7e1fd0-1qv24iydo6y6?region=us-east-1&tab=objects) in a version-enabled S3 bucket

### Steps to Restore Backup

#### Step 1: Fully Replicate databrew.org configuration

1. Start an EC2 instance in `databrew-prod`
2. Route HTTPS Request to EC2 Via Route 53 [here](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-ec2-instance.html)
3. Go through the ODK Installation provided in the official documentation [here](https://docs.getodk.org/central-install-digital-ocean/#getting-and-setting-up-central)
4. Before doing `docker compose` revert to Central 1.5.3 submodule to use the same ODK Central Version as databrew.org

```bash
git clone https://github.com/getodk/central;
cd central;
git checkout v1.5.3;
git submodule update --init;
```

5. **IMPORTANT**: The Dockerfile provided by Central does not have valid postgresql distribution. Update the [service dockerfile](https://github.com/getodk/central/blob/v1.5.3/service.dockerfile) to use the right debian distribution for specific installation on `postgresql-client-9.6`

```dockerfile
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list; \
  wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -; \
  apt-get update; \
  apt-get install -y cron gettext postgresql-client-9.6
```

If `focal-pgdg` binary is not available, please check the other [distros](http://apt.postgresql.org/pub/repos/apt/dists/) here

6. Proceed to do `docker compose up -d` on all the services after changing these parameters

Final Checks:
- Make sure you check that new ODK server is v1.5.3
- Make sure that you have `postgres-9.6` and `postgres-client-9.6` to enable `pg_dump` between two databases


#### Step 2: Restoring Backup Files to New Server

1. Get Access to S3 via Roles / Access Keys

2. Fetch backup file from S3 [here](https://s3.console.aws.amazon.com/s3/buckets/odkbackupstack-odkbackups3bucket7f7e1fd0-1qv24iydo6y6?region=us-east-1&tab=objects)

```bash
aws s3 cp s3://odkbackupstack-odkbackups3bucket7f7e1fd0-1qv24iydo6y6/databrew-odk-central-backup.zip /data/transfer/databrew-odk-central-backup.zip
```

3. Restore via Docker Service in Central Repo
```bash
cd
cd central
docker compose exec service node /usr/odk/lib/bin/restore.js /data/transfer/databrew-odk-central-backup.zip
```

### FAQs

1. How long to do daily backup snapshots? 
- Lambda will take appx 2-3 mins

2. How long to restore backup to new server? 
- 3-4 hours for server setup
- 5-10 mins to restore the zip backup 
- 2-3 hours to repoint to new server

3. Incident Response? 
- Repoint data pull to the new server with new credentials etc
- Dump data into a new bucket to not overwrite data that has been stored in the old bucket
- Join data coming from old bucket and new bucket by ID to minimize data loss

4. What is retained?
**Everything in ODK Central** is retained up until the backup snapshot