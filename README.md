## ${{ values.serviceName }} application

### Files
- main.py: a Flask application
- requirements.txt: dependencies for the application
- Dockerfile

### Testing
build and test locally:
- IMAGE_NAME=${{ values.serviceName }}
- docker build -t $IMAGE_NAME .
- docker run -dp 127.0.0.1:8080:8080 $IMAGE_NAME
- curl 127.0.0.1:8080

cleanup after test:
- docker container rm -f $(docker container ls | grep $IMAGE_NAME | awk '{print $1}')
- docker image rm $IMAGE_NAME

# Connecting to Cloud SQL postgresql

The service account provided, only has access to connect to public schema, you will need to [Grant](https://www.postgresql.org/docs/current/sql-grant.html) it access to the databases and tables it needs access to by obtaining the default user credentials. You can reset the password by following [this document](https://cloud.google.com/sql/docs/postgres/create-manage-users#change-pwd)

## Managing Connections

Please read the [following guidance on how to manage your connections](https://cloud.google.com/sql/docs/postgres/manage-connections#python), please note that mishandling connections will cause degregation in performance.


## Connect to Cloud SQL from on Premesis

From on-prem you will connect to the [public endpoint](https://console.cloud.google.com/sql/instances), so a [firewall rule](https://hcaservicecentral.service-now.com/hca?id=hca_cat_item&sys_id=bc9146dedb79970006c1ef92ca96196e) is required to connect. If you are using the [cloud SQL auth proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy), the outbound port is `3307` instead of `5432`. 


# Cloud CI/CD pipelines

Please refer to the documentation located in your [/docs](/docs) directory to learn more