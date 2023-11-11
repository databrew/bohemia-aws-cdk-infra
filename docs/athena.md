# Interactive Queries via Athena

1. To query data via Athena, log in to the console
2. Authenticate using role `cloudbrewr-aws-role`
3. In the console, search for Athena
4. Once in Athena, go to `Query Editor` on the left sidebar

Note: If being prompted to select for S3 bucket output, please set to bucket `bohemia-athena-query-results`


## Understanding the UI

On the left side, you will be able to see several dropdowns.

**Database (schema):**
- `clean_form`: This is the form coming from the data pipeline, it is refreshed every 15 minutes and reflect the data being used for our data-operations
- `metadata`: This is the metadata generated from Joe
- `ext_data`: This is manual ext files coming from Slack conversation that can come in handy 

**Tables** 
These are tables that is under a certain schema, you will be able to see all columns under each table

**Views**
These are preset queries that you can built on top on of tables for reproducing frequent queries

## Testing your first Queries

**Getting number of user in a household**

```sql
select hhid, count(distinct extid)
from clean_form.safety s
inner join clean_form.safety_repeat_individual sr
on s.key = sr.parent_key
group by 1
```
**Getting status of an extid in metadata**
You can also make joins cross databases:
```sql
select sr.extid, 
       ms.starting_safety_status
from clean_form.safety_repeat_individual sr
inner join metadata.safety ms
on sr.extid = ms.extid
```

**Querying Historical Table**
Athena can also query historical daily snapshots of tables. For instance:
```sql
select extid, 
        most_recent_visit
        starting_safety_status 
from metadata.icf_hist
where run_date in ('2023-11-05', '2023-11-06')
```

**Note**: This is currently only set on metadata, will require further scoping for `clean_form`



