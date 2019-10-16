# 接口文档列表

## 开发工具类
* /api/v2.1.0/doc [get]
    * 获取文档

* /log [get]
    * 获取当天日志

## 学生类
* /api/v2.1.0/UploadRecord [post]
    * 作用：上传用户扫码信息，当用户在同一节课重复扫码时，会更新数据库
    * 接收：openid, room, campus, row, col, time: 格式为 时间戳
    * 返回：0 7 8 9 上传成功，返回本次数据库的所有数据；2；3；5；6
        
* /api/v2.1.0/GetStudentHistory [get]
    * 作用：查询用户扫码历史
    * 接收：openid **或** stuid, startTime: 查询开始日期, 格式为yyyy-mm-dd(获取此日至今记录) **或** stamp(获取当前课)
    * 返回：0 上传成功，返回本次的数据列表,包含结果，获取个数；3；2；

* /api/v2.1.0/BindOpenid [post]
    * 作用：绑定openid与id
    * 接收：openid, id, identity_number
    * 返回：0 上传成功，返回被该条数据的_id, openid, id, name, identity；3；4；12

* /api/v2.1.0/GetOpenid [get]
    * 作用：获取openid等信息
    * 接收：js_code, secret, appid
    * 返回：0 上传成功，返回openid, id, name, identity；1；2

* /api/v2.1.0/GetStudentInfo [get]
    * 作用：查询学生详情
    * 接收：openid **或** id
    * 返回：0 已绑定用户详情；2 未绑定用户详情
    * 请注意，二者皆会返回用户详情

* /api/v2.1.0/ChangeStudentRecord [post]
    * 作用：修改学生签到数据
    * 接收：recordid (必填), col(选填), row(选填), exception(选填), late(选填), comment(选填)
    * 返回：0 成功

* /api/v2.1.0/GetStudentCourse [get]
    * 作用：查询学生当前或最近课程
    * 接收：stuid: 学号, time: 格式为yyyy-mm-dd l **或** 时间戳
    * 返回：0 上传成功，返回本次的数据列表；3；10；11

* **/api/v2.1.0/GetStudentCourseByStamp [get] (删除)**
    * 作用：查询学生当前或最近课程
    * 接收：stuid：学号,  time：时间戳
    * 返回：0 上传成功，返回本次的数据列表；3；10；11

## 教师类
* /api/v2.1.0/GetTeacherCourse [get]
    * 作用：查询老师当前或最近课程
    * 接收：teaid: 工号, time: 格式为yyyy-mm-dd l **或** 时间戳
    * 返回：0 上传成功，返回本次的数据；3；10；11

* **/api/v2.1.0/GetTeacherCourseByStamp [get] (删除)**
    * 作用：查询老师当前或最近课程
    * 接收：teaid: 工号,  time：时间戳
    * 返回：0 上传成功，返回本次的数据列表；3；10；11

* /api/v2.1.0/GetTeacherHistory [get]
    * 作用：查询老师授课记录
    * 接收：openid, startTime: 查询开始日期, 格式为yyyy-mm-dd 
    * 返回：0 上传成功，返回本次的数据列表,包含结果，获取个数；3；

* /api/v2.1.0/TeacherScan [post]
    * 作用：记录老师签到
    * 接收：room, time: 时间戳
    * 返回：0 上传成功；3；

* /api/v2.1.0/GetStudentData [get]
    * 作用：获取统计信息
    * 接收：teaid(必填，只可查询教师本人), campus(选填), room(选填), level(选填), late(选填), courseid(选填), stuid(选填), exception(选填), startTime(必填，格式为yyyy-mm-dd 或 时间戳), endTime(必填，格式为yyyy-mm-dd 或 时间戳)
    * 返回：0 上传成功；3；


## 教室类
* /api/v2.1.0/GetRoomHistory [get]
    * 作用：查询教室扫码历史
    * 接收：room: 教室的编号, time: 格式为yyyy-mm-dd l **或** 时间戳
    * 返回：0 上传成功，返回本次的数据列表；3

* **/api/v2.1.0/GetRoomHistoryByStamp [get] (删除)**
    * 作用：查询教室扫码历史
    * 接收：room：教室的编号,  time：时间戳
    * 返回：0 上传成功，返回本次的数据列表；3

* /api/v2.1.0/GetRoomCourse [get]
    * 作用：查询教室课程
    * 接收：room: 教室的编号, time: 格式为yyyy-mm-dd l **或** 时间戳
    * 返回：0 上传成功，返回本次的数据；3；10

* **/api/v2.1.0/GetRoomCourseByStamp [get] (删除)**
    * 作用：查询教室课程
    * 接收：room：教室的编号,  time：时间戳
    * 返回：0 上传成功，返回本次的数据；3；10



## errcode表
0 成功

1 从微信官方获取openid失败

2 openid未绑定，身份未知

3 缺少参数

4 学校账号或身份证错误

5 座位不可用

6 上传失败，无课

7 当前无课，不上传

8 换座成功，记录更新

9 当前无课，且换座（之前已扫码），新记录不保存

10 未查询到数据

11 查询到未来课程

12 再次绑定错误