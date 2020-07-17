二. Cluster Deployment Guide:

1. Make Base Image

`cd /app/9nfl_opensource/deploy/data_join/images` 

`docker build -t  FROM mirror.jd.com/pino/fl/opensource_tf1.15_base:v0.1 . -f Base_Dockerfile`

please replace "mirror.jd.com/pino/fl/opensource_tf1.15_base:v0.1"  with your base image name 

2. Make  Data Join Image

`cd /app/9nfl_opensource/deploy/data_join/images`

`docker build -t  mirror.jd.com/pino/fl:data_join_leader_opensource_v1.0 . -f Base_Dockerfile`

please replace "mirror.jd.com/pino/fl:data_join_leader_opensource_v1.0"  with your data join image name 

Making leader data join image  and follower data join image is the same  as the second step

3. deploy

`cd /app/9nfl_opensource/deploy/data_join/k8s`

After finished setting Environment variables, and replace the Environment variables of 
the deployment_worker.yaml with real value;

`deployment_worker.yaml | kubectl --namespace=${NAMESPACE} create -f -`
