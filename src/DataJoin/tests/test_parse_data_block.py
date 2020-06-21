import requests

HEADERS = {
    'Content-Type': 'application/json',
}
action = getattr(requests, 'POST'.lower(), None)

data = {'dfs_data_block_dir': 'hdfs://ns1018/user/ads_9ncloud/wangjianling/partition_0'}

url = "http://192.168.213.79:9380/v1/parse/data/block/meta"

response = action(url=url, json=data, headers=HEADERS)

res = response.json()

print(1111111111111111111, res)
