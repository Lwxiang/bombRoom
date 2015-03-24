(c) 2015 ccloli. 2015 年自强 Hack Day 作品 BOMB ROOM 前端页面

* 由于后端未完全实现跨域，故在跨域访问时由于浏览器限制将无法正常运行。

  这是对于 Chrome 的可行的解决办法，其他浏览器可按照以下说明寻找对应扩展实现需求：

    1. 安装扩展程序 Redirector（https://code.google.com/p/chrome-redirector/，在左侧找到 crx 下载链接，下载后将其解压至任意文件夹，在 Chrome 扩展程序页面载入此文件夹以完成安装）；

    2. 打开扩展程序选项页，在左侧找到规则管理器，点击 + 号添加规则；

    3. 按以下说明添加规则，并点击左侧的复选框启用规则：

        匹配 - 正则表达式 - 内容过滤全选
        .*121\.43\.228\.141\:8000/.*

        被替换式
        Access-Control-Allow-Origin|Access-Control-Allow-Credentials

        替换式
        http://localhost|true
        （localhost 按需替换成服务器对应域名，http 按需替换成服务器对应协议，如 https://www.google.com）

    4. 点击地址栏上灰色的 Redirector 图标，使其变为蓝色以启用规则。