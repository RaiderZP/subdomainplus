# subdomainplus
该脚本为集成工具，集成了chaos线上平台、ksubdomain、subfinder3款子域名工具，将3个项目收集的结果进行集合并使用httpx进行存活验证，并进行状态码分类，最后将新增的子域名发送到企业微信群中进行通知。

# 如何使用？
1.将wx_url、wx_upload_url中的token改为自己的企业微信token。

2.在/root/subdoamin/下创建域名文件夹，如想收集百度的域名，则创建baidu文件夹，并在baidu文件下创建Domain文件，导入baidu的域名资产，如baidu.com,badu.cn等等

3.将项目文件写入计划任务循环执行即可达成域名监管作用。

# 自定义小功能
  1.禁用标题，当某个标题多次出现且为无用域名时，可尝试禁用该标题，这样该域名就不会出现在新增列表中，需在当前目录下创建ban_title文件并写入关键字即可。
  
  2.禁用某个跳转的url，需在当前目录下创建ban_title文件并写入关键字即可。
