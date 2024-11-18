# 法诉信息截图工具

## 项目简介

这是一个基于Python和Selenium的自动化工具，用于自动获取和处理法诉相关信息的截图。该工具提供了图形用户界面(GUI)，可以方便地进行订单信息的批量截图和处理。

## 功能特点

- 自动登录系统
- 批量处理订单信息
- 自动截取订单详情页面
- 自动合并身份证正反面图片
- 自动生成PDF文档
- 支持多订单并发处理
- 自动更新ChromeDriver
- 支持无头模式运行

## 系统要求

- Windows操作系统
- Python 3.7+
- Google Chrome浏览器(最新版本)
- 稳定的网络连接

## 安装步骤

1. 克隆或下载项目到本地
2. 安装依赖包：pip install -r requirements.txt


## 文件结构说明

```tree
project/
├── main.py                    # 主程序入口
├── driver/                    # ChromeDriver目录
│   └── windows/              # Windows驱动
├── case/                      # 测试用例目录
│   ├── web_demo/             # Web测试用例
│   │   └── test_zzy_business.py  # 业务测试类
│   └── pageobj/              # 页面对象
│       └── adminBusiness.py  # 管理页面类
├── database/                  # 数据配置目录
│   ├── caseYAML/             # 测试用例YAML配置
│   │   └── test_zzy_business.yaml  # 测试数据配置
│   └── locatorYAML/          # 页面元素定位配置
│       └── test_zzy_business.yaml  # 元素定位配置
├── config/                    # 配置文件目录
│   └── setting.yaml          # 系统配置文件
├── logs/                      # 日志目录
│   └── app.log               # 应用日志文件
└── LegalFile/                # 输出文件目录
    └── {订单号}{用户名}信息资料/  # 订单相关文件
```

### 目录说明

1. **main.py**: 程序主入口文件
2. **driver/**: 存放ChromeDriver驱动文件
   - **windows/**: Windows系统驱动文件
3. **case/**: 测试相关代码
   - **web_demo/**: Web端测试用例
     - **test_zzy_business.py**: 业务测试类
   - **pageobj/**: 页面对象模型
     - **adminBusiness.py**: 管理页面类
4. **database/**: 配置数据
   - **caseYAML/**: 测试用例数据配置
     - **test_zzy_business.yaml**: 测试数据配置
   - **locatorYAML/**: 页面元素定位配置
     - **test_zzy_business.yaml**: 元素定位配置
5. **config/**: 系统配置文件
6. **logs/**: 日志文件目录
7. **LegalFile/**: 输出文件存储目录



## 输出文件说明

1. 截图文件位置：
   - 路径：`LegalFile/{订单号}{用户名}信息资料/`
   - 包含文件：
     - 身份证正面.jpg
     - 身份证反面.jpg
     - {用户名}身份证_{订单号}.png (合并后的身份证图片)
     - 租金支付流水_{订单号}.csv (账务明细)

2. 日志文件：
   - 路径：`logs/app.log`
   - 记录程序运行的详细日志

## 重要提示

1. 账务明细文件要求：
   - 文件名：必须为"账务明细.csv"
   - 位置：必须在桌面 (`C:\Users\Administrator\Desktop\账务明细.csv`)
   - 格式：CSV格式，包含订单相关信息

2. 运行环境：
   - 确保Chrome浏览器已更新至最新版本
   - 程序会自动检测并更新匹配的ChromeDriver
   - 建议使用管理员权限运行程序

3. 性能说明：
   - 支持批量处理多个订单
   - 处理时间与订单数量成正比
   - 无头模式可提高处理速度

## 常见问题解决

1. 截图异常：
   - 更新Chrome浏览器至最新版本
   - 检查网络连接是否稳定
   - 查看日志文件排查具体错误

2. 文件未找到：
   - 检查账务明细.csv是否存在于正确位置
   - 确保文件名称正确
   - 检查文件格式是否正确

3. 程序无响应：
   - 检查网络连接
   - 确认目标网站可访问
   - 查看日志文件了解详细错误信息
   - 重启程序


## 使用说明

如需测试自己项目，请修改case/web_demo/test_zzy_business.py 是测试类，和adminBusiness.py 中的代码对应
case/pageobj/adminBusiness.py 中的代码 pageobj中的代码是操作页面元素的代码，

以及database/caseYAML/ 中的yaml文件caseyaml是测试数据，
以及database/locatorYAML/ 中的yaml文件locatoryaml是定位操作信息 和pageobj中的代码对应

setting.yaml是配置文件 修改url

1. 项目代码内运行截图工具程序：python main.py

2. 程序启动后的操作步骤：

   a. 点击"加载YAML"按钮加载配置
   
   b. 在文本框中修改订单号(orderNo)和数量(num)  orderNo和num保持一致
   
   c. 点击"保存YAML"保存修改
   
   d. 再次点击"加载YAML"确认修改
   
   e. 点击"运行截图工具"开始执行

3. YAML配置示例:
testdata:
user: "admin" # 用户名=后台登录的账号
code: "123456" # 验证码
num: "1015103728969591" # 订单号
orderNo: "1015103728969591" # 订单号(与num保持一致)

url在setting.yaml中
url: "http://dev.admin.zuzuya.cn" # 系统登录地址

## 技术支持

如遇到问题，请按以下步骤排查：

1. 检查日志文件：`logs/app.log`
2. 确认所有依赖包已正确安装
3. 验证Chrome浏览器版本
4. 测试网络连接
5. 确保账务明细文件存在且格式正确

## 更新日志

v1.0.0 (2024-03-20)
- 初始版本发布
- 支持批量处理订单
- 添加无头模式选项
- 优化文件处理逻辑
- 增加自动更新ChromeDriver功能
- 完善错误处理机制
- 增加详细日志记录

## 许可证

本项目遵循 MIT 许可证