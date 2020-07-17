# Compile dependencies

| External dependencies  | Version           | Description              |
| ---------------------- | ----------------- | :----------------------- |
| openresty              | 1.17.8.1rc1       | Generate bin file        |
| nginx                  | openresty version |                          |
| redis                  | 6.0.3             |                          |

# Compile

- Download and install openresty  [download](https://openresty.org/download/openresty-1.17.8.1rc1.tar.gz)
- Compilation parameters http_v2_module (./configure --with-http_v2_module)
- gmake && gmake install
- Move the bin file 

# Attention

- fl_proxy_online/config/fl_proxy.conf
  - set $redis_url --Fill in the specific redis ip
  - grpc_pass --Fill in the specific ip and port
- config/nginx.conf
  - lua_package_path --Local openresty installation path
- redis
  - Need to support external access


