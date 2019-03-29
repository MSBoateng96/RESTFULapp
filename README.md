# RESTFULapp

A Cloud Application with a REST-based interface, used to retrieve and present data from an API for Police Crime Data. The data I focused on was statistics about **stop-and-search** in the UK.

## Installation

Configure the settings

```bash
gcloud config set project oceanic-column-229409
gcloud config set compute/zone europe-west6-c
export PROJECT_ID="$(gcloud config get-value project -q)"
gcloud auth configure-docker
```

## Create Clusters

```bash
gcloud container clusters create restful-cluster --num-nodes=3
gcloud container clusters create cassandra --num-nodes=3 --machine-type "n1-standard-2"
```

## Download and Create Cassandra files

```bash
wget -O cassandra-peer-service.yml http://tinyurl.com/yyxnephy
wget -O cassandra-service.yml http://tinyurl.com/y65czz8e
wget -O cassandra-replication-controller.yml http://tinyurl.com/y2crfsl8
kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml
kubectl scale rc cassandra --replicas=3
```

## Build and Push App using Docker

```bash
docker build -t gcr.io/${PROJECT_ID}/restful-app:v1 .
docker push gcr.io/${PROJECT_ID}/restful-app:v1
```

## Run using kubectl for scaling and load-balancing

```bash
kubectl run restful-web --image=gcr.io/${PROJECT_ID}/restful-app:v1
kubectl expose deployment restful-web --type=LoadBalancer --port 80 --target-port 8080
kubectl scale deployment restful-web --replicas=1
kubectl get pods
kubectl get services
```

## Copying Data from CSV file to Cassandra

```bash
kubectl get pods -l name=cassandra
kubectl exec -it cassandra-b5x5r -- nodetool status
kubectl cp stopsdata.csv cassandra-b5x5r:/stopsdata.csv
kubectl exec -it cassandra-b5x5r cqlsh
```

```sql
CREATE KEYSPACE searches WITH REPLICATION =
{'class' : 'SimpleStrategy', 'replication_factor' : 1};

CREATE TABLE searches.stats (ID int PRIMARY KEY,
outcome text, self_defined_ethnicity text, object_of_search text);

COPY searches.stats(ID,outcome,self_defined_ethnicity,object_of_search)
FROM 'stopsdata.csv'
WITH DELIMITER=',' AND HEADER=TRUE;

select * from searches.stats;
```


