# AO3 文章批量下载器
ao3下载器第二版.几乎是重构了所有代码.原项目是自己一年前写的代码,越看越嫌弃

除python默认库外额外需求bs4和pyOpenssl库,前者为加载项,即BeautifulSoup所处库, 后者如果不装会导致无法连接(不知是否与VPN有关,我对通信不是非常熟)
如果提示少了xxxx库就pip install xxxxx

已废弃老项目: https://github.com/610yilingliu/Get-Ao3-Article

目前使用工作邮箱：liuyiling.windy610@bytedance.com.github绑的这个很少看了

## 运行环境

### Python版本

Python 3.7

### 操作系统

Windows 10

在mac和linux下可能导致txt文件名中含有非法字符而发生错误(我只对Windows做了适配), 如果需要在这两个系统下使用请修改`__main__.py`中`win_invalid_chars`变量,使其等于mac/linux的非法字符集

## 运行方法
将VPN调整至全局模式,确定当前python环境中有pyopenssl这个库

将命令行定位至本文件夹下, 使用指令`python -m pkg`即可.如果电脑有多个python版本,请使用`python3 -m pkg`
如果想用VSCode开debug模式运行, 把`__main__.py`中(其实比较推荐使用debug运行)

```Python
from pkg.router import *
from pkg.fetcher import *
```

改成

```python
from router import *
from fetcher import *
```

就可以了

## 说明

**相对于第一版的改进**

1. 代码更为简洁
   
2. 使用proceed中所带链接而非直接拼凑的url,适配性更强
   
3. 对于大批量下载更为友好, ao3在高频访问下会触发保护机制, 请求返回空值或返回错误代码429, 所以这个下载器移除了多进程下载功能, 使用单一进程下载并在方问过快导致返回错误时采取了等待后重新尝试连接, 对于因网络波动造成的断线也做了同样处理(一般设置为三次, 30秒至两分钟不等)
   
4. 可选择是否仅下载中文页面


**其他**

屏幕打印信息全部是用英文写的(初中水平应该就能看懂), 这是因为中文在部分系统中会因为编码原因显示乱码

输入大小写随意,注意使用半角符号输入.全角符号是无法识别的

## 代码说明

### fetcher.py

下载文章

### router.py

通过目录页面源码识别出其所包含的文章

### __main__.py

工具人

### __init__.py

空的Python包标识文件

各个function懒得写了, 源码里注释的应该算比较清楚

如果碰到什么奇怪的bug请带出问题的链接和问题描述(有截图最好)发邮件到 yilingliu1994@gmail.com 或 22214014@student.uwa.edu.au


## 测试说明:

部分已通过的test case:

https://archiveofourown.org/works/26447329

https://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=zh&commit=%E6%8E%92%E5%BA%8F%E5%92%8C%E8%BF%87%E6%BB%A4&tag_id=Hatake+Kakashi\*s\*Uchiha+Obito
(全页面, 5-6页)

https://archiveofourown.org/users/HelloHappy/pseuds/HelloHappy

https://archiveofourown.org/users/huaishang233/pseuds/huaishang233/works
