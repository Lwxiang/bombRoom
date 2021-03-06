# 大厅部分的API接口 (所有接口分为大厅部分/游戏部分)

## 主要逻辑流程

1. 玩家进入,填写昵称 (to 2

2. 请求```/allot/```,获取玩家uid (to 3

3. 1. 若创建房间,填写信息(最大参与人数,房间边长,最大每回合步数) (to 4
   2. 若进入房间,填写要进入的房间号

4. 请求```/host/```,创建并进入一个房间 (to 5

5. 请求```/change/```,根据玩家填写信息修改房间的属性 (to 7

6. 请求```/enter/```,根据房间号进入一个房间 (to 7

7. 不断请求```/room/```来获取当前房间的最新信息(包括游戏是否开始的信息,把原来```/wait/```并入其中) (to 8

8. 1. 若玩游戏,等待游戏开始,查看game部分文档
   2. 若离开房间,请求```/leave/``` (to 1
   
## 主要接口

所有返回数据由```status```和```info```组成

以下所有的返回数据描述均为```info```内的字段

---

#### allot

提交玩家输入的昵称并绑定一个uid

URL:```/allot/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|name|yes|玩家昵称|

返回结果:

|字段|说明|
|---|---|
|uid|玩家标记|
|name|玩家昵称|
|session|session过期时间|

JSON示例:

{"status": "1", "info": {"session": 1209600, "uid": 2, "name": "lwxiang"}}

---

#### host

创建一个房间

URL:```/host/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|无||

返回结果:

|字段|说明|
|---|---|
|无||

JSON示例:

{"status": "1", "info": {}}

---

#### change

创建一个房间

URL:```/change/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|host|yes|房主uid|
|capacity|yes|最大参与人数|
|length|yes|房间边长|
|energy|yes|最大每回合步数|

返回结果:

|字段|说明|
|---|---|
|无||

JSON示例:

{"status": "1", "info": {}}

---

#### change

进入一个房间

URL:```/enter/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|host|yes|房间id,也就是房主的id|

返回结果:

|字段|说明|
|---|---|
|无||

JSON示例:

{"status": "1", "info": {}}

---

#### leave

离开一个房间

URL:```/leave/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|host|yes|房间id,也就是房主的id|

返回结果:

|字段|说明|
|---|---|
|无||

JSON示例:

{"status": "1", "info": {}}

---

#### room

请求一个房间的当前信息

URL:```/room/```

格式:```JSON```

HTTP请求方式:```POST```

请求参数:

|字段|必选|说明|
|---|---|---|
|host|yes|房间id,也就是房主的id|

返回结果:

|字段|说明|
|---|---|
|start|是否已经开始|
|host|房间id,也就是房主的id|
|name|房主的名字|
|capacity|最大参与人数|
|length|房间边长|
|energy|最大每回合步数|
|num|房间当前人数|
|ids|房间当前的玩家uid列表|
|players|房间当前的玩家uid列表(与ids一一对应)|
|colors|房间当前的玩家颜色列表(与ids一一对应)|

JSON示例:

{"status": "1", "info": {"colors": ["#FF0000"], "capacity": 3, "name": "hello", "players": ["hello"], "energy": 3, "length": 3, "ids": ["8"], "start": false, "host": 8, "num": 1}}

---

#### wait(接下来的更新中不建议使用,已经并入room)

请求一个房间的游戏是否开始

URL:```/wait/```

格式:```JSON```

HTTP请求方式:```GET```

请求参数:

|字段|必选|说明|
|---|---|---|
|无||

返回结果:

|字段|说明|
|---|---|
|uid|玩家的uid|

JSON示例:

{"status": "0", "info": {"uid": 2}}

注:status 1 为开始, 0 为未开始

---

#### hall(当前未使用,建议在进入房间的页面提供已存在房间的选择信息)

请求已经存在的房间

URL:```/hall/```

格式:```JSON```

HTTP请求方式:```GET```

请求参数:

|字段|必选|说明|
|---|---|---|
|无||

返回结果:

|字段|说明|
|---|---|
|total|房间总数|
|rooms|房间信息列表|

JSON示例:

{"status": "1", "info": {"total": 1, "rooms": {"1": {"capacity": 5, "name": "\u6d6a\u5473\u9c9c", "energy": 3, "host": 1, "length": 4, "num": 2}}}}
