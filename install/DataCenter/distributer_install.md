Cluster Deployment Guide:

1. Make Data Center Image

`cd /app/9nfl_opensource/deploy/data_center/images`
`docker build -t  mirror.jd.com/pino/fl:data_center_leader_opensource_v1.0 . -f Data_Center_Dockerfile`

please replace "mirror.jd.com/pino/fl:data_center_leader_opensource_v1.0"  with your data join image name 

when Making follower data center image,need to change mysql config as follower mysql 
 the method of making is follower data center image is the same  as above
