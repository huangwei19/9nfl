local pcall = pcall
local router = require 'router'
local ok, err = pcall(router.route, router)
if not ok then
    ngx.log(ngx.ERR, "fl route failed: ", err)
end
