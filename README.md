# 电子代表证管理系统 (Electronic Delegate Card Management System)

## 目录

1.  [项目简介](#项目简介)
2.  [主要功能](#主要功能)
3.  [技术栈](#技术栈)
4.  [安装与运行](#安装与运行)
    *   [环境要求](#环境要求)
    *   [安装步骤](#安装步骤)
5.  [项目结构](#项目结构)
6.  [使用说明与主要页面](#使用说明与主要页面)
7.  [未来展望](#未来展望)
8.  [贡献](#贡献)
9.  [许可证](#许可证)

## 项目简介

本项目是一个基于 Django框架开发的电子代表证管理系统，旨在为特定会议（如“山西财专信息科技学院分团委第十次团员、学生代表大会”）提供一套完整的代表信息管理、电子代表证生成、查询、扫码签到及数据统计分析的解决方案。系统包括面向代表的信息申报和查询入口，以及面向管理员的后台管理、数据看板和签到操作界面。

## 主要功能

*   **信息自主申报**:
    *   代表在线填写个人信息（姓名、性别、学号、政治面貌、代表团、班级）。
    *   上传个人免冠照片。
    *   系统自动生成唯一的、基于年份的代表证编号。
*   **代表资格审核 (后台)**:
    *   管理员在 Django Admin 后台审核代表提交的信息。
    *   可设置审核状态（待审核、审核通过、审核不通过）并添加审核备注。
    *   审核通过后，固定信息（如发证单位、签发日期、有效期）自动填充。
*   **电子代表证查询与展示**:
    *   代表通过姓名和学号查询自己的申请状态。
    *   若审核通过，则跳转到电子代表证展示页面。
    *   电子代表证页面展示代表详细信息、照片、唯一卡号及会议二维码。
    *   支持卡片翻转效果，展示背面信息。
    *   提供“保存电子版代表证”功能（生成图片）。
    *   提供“会议议程及须知”弹窗。
*   **扫码签到**:
    *   管理员使用专用页面通过摄像头扫描代表证上的二维码进行签到。
    *   实时反馈签到状态（成功、重复签到、未通过审核、未找到代表等）。
    *   支持手动输入卡号进行签到。
    *   签到成功后记录签到时间。
*   **数据仪表盘 (Dashboard)**:
    *   为管理员提供关键绩效指标 (KPI) 可视化，如总申报人数、各审核状态人数、已签到人数、签到率等。
    *   通过 ECharts 图表展示数据分布，如：
        *   审核状况分析（饼图）
        *   各代表团人数对比（柱状图）
        *   政治面貌构成（饼图/柱状图）
        *   性别比例分析（饼图）
        *   各班级人数分布（横向条形图，带滚动条）
    *   数据动态从后端 API 加载。
*   **代表信息概览 (列表页)**:
    *   管理员查看所有代表信息的列表。
    *   支持按姓名、学号、卡号、代表团进行搜索。
    *   支持按审核状态、签到状态、代表团进行筛选。
    *   支持按卡号、提交时间、姓名、代表团等字段排序。
    *   以卡片形式展示每位代表的摘要信息，包括照片、基本信息、审核与签到状态。
    *   提供KPI概览。
    *   可直接跳转查看已批准代表的电子证。
*   **后台管理 (Django Admin)**:
    *   管理员对代表信息进行增删改查。
    *   自定义的 `DelegateAdmin` 界面，优化了字段显示、筛选和操作。
    *   支持批量审核操作（通过、不通过、标记为待审核）。
*   **API 接口**:
    *   使用 Django REST framework 提供代表数据的 API 接口。
    *   支持通过卡号查询已批准的代表信息。
    *   提供签到操作的 API 端点。
*   **导航页面**:
    *   提供一个中心导航页面，方便用户访问系统的不同功能模块。

## 技术栈

*   **后端**:
    *   Python 3.11+
    *   Django 5.2.1
    *   Django REST framework 3.16.0 (用于 API)
    *   SQLite3 (默认数据库，可配置为其他数据库)
*   **前端**:
    *   HTML5
    *   CSS3 (Tailwind CSS 框架)
    *   JavaScript (原生 JS)
    *   ECharts 5.5.0 (用于数据仪表盘图表)
    *   html5-qrcode (用于扫码签到)
    *   qrcode.js (用于生成代表证二维码)
    *   dom-to-image-more (用于生成代表证图片)
*   **字体**:
    *   Noto Serif SC (思源宋体)
    *   方正小标宋简体 (用于标题等特定场合，需自行确保字体文件存在于 `static/fonts/`)
*   **开发工具**:
    *   Visual Studio Code (或任何 Python IDE)
    *   Git

## 安装与运行

### 环境要求

*   Python (3.11 或更高版本推荐)
*   pip (Python 包安装器)
*   Git (可选，用于克隆仓库)

### 安装步骤

1.  **克隆或下载项目**:
    ```bash
    git clone https://github.com/AmaTsumeAkira/electronic-delegate-card-system.git
    cd electronic-delegate-card-system
    ```
    或者直接下载 ZIP 文件并解压。

2.  **创建并激活虚拟环境** (推荐):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **数据库迁移**:
    ```bash
    python manage.py makemigrations delegate_card_app
    python manage.py migrate
    ```

5.  **创建超级用户** (用于访问 Django Admin 后台):
    ```bash
    python manage.py createsuperuser
    ```
    按照提示设置用户名、邮箱和密码。

6.  **收集静态文件** (生产环境需要，开发环境 Django 会自动处理):
    ```bash
    python manage.py collectstatic
    ```
    确保 `settings.py` 中的 `STATIC_ROOT` 配置正确。

7.  **运行开发服务器**:
    *   **HTTP (标准方式)**:
        ```bash
        python manage.py runserver
        ```
        默认情况下，服务将在 `http://127.0.0.1:8000/` 启动。

    *   **HTTPS (使用 `django-extensions` 和 SSL 证书，可选)**:
        如果你需要 HTTPS 支持（例如，摄像头在某些浏览器下需要 HTTPS），并且已经安装了 `django-extensions`，可以像这样启动服务器：
        ```bash
        python manage.py runserver_plus --cert-file fullchain.pem --key-file privkey.pem 0.0.0.0:8000
        ```
        **注意**:
        *   你需要将 `fullchain.pem` 和 `privkey.pem` 替换为你自己的 SSL 证书文件路径。
        *   使用 `0.0.0.0` 会使服务器在你的局域网内可访问（通过你的 IP 地址）。
        *   确保 `django-extensions` 已经通过 `pip install django-extensions` 安装并已添加到 `settings.py` 的 `INSTALLED_APPS` 中。

8.  **访问系统**:
    *   **导航页 (首页)**: `http://127.0.0.1:8000/`
    *   **管理员后台**: `http://127.0.0.1:8000/admin/` (使用创建的超级用户登录)
    *   **信息申报页**: `http://127.0.0.1:8000/submit-info/`
    *   **信息查询页**: `http://127.0.0.1:8000/query/`
    *   **数据仪表盘**: `http://127.0.0.1:8000/dashboard/` (需管理员登录)
    *   **代表信息概览**: `http://127.0.0.1:8000/delegates-list/` (需管理员登录)
    *   **扫码签到页**: `http://127.0.0.1:8000/scan-checkin/` (需管理员登录)

## 项目结构

```
electronic_card_project/
├── delegate_card_app/         # 主要应用目录
│   ├── migrations/            # 数据库迁移文件
│   ├── static/                # 应用特定的静态文件 (CSS, JS, 图像) (如果存在)
│   ├── templates/             # 应用特定的模板 (如果存在)
│   ├── __init__.py
│   ├── admin.py               # Django Admin 配置
│   ├── apps.py                # 应用配置
│   ├── forms.py               # Django 表单
│   ├── models.py              # 数据库模型
│   ├── serializers.py         # DRF 序列化器
│   ├── tests.py               # 测试文件
│   ├── urls.py                # 应用级 URL 配置
│   └── views.py               # 视图逻辑
├── electronic_card_project/   # Django 项目配置目录
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # 项目设置
│   ├── urls.py                # 项目级 URL 配置
│   └── wsgi.py
├── media/                     # 用户上传的文件 (如代表照片)
│   └── delegate_photos/
├── static/                    # 全局静态文件
│   ├── fonts/                 # 字体文件 (如 FZXiaoBiaoSongJianTi.woff2)
│   └── images/                # 静态图片资源
├── templates/                 # 全局 HTML 模板
│   ├── admin/
│   │   └── login.html         # 自定义管理员登录页
│   ├── dashboard.html
│   ├── delegate_list.html
│   ├── index.html             # 电子代表证展示页
│   ├── navigation.html
│   ├── query_delegate.html
│   ├── scan_checkin.html
│   └── submit_delegate_info.html
├── db.sqlite3                 # SQLite 数据库文件 (默认)
├── manage.py                  # Django 管理脚本
├── requirements.txt           # 项目依赖
└── README.md                  # 项目说明文件
```

## 使用说明与主要页面

1.  **代表**:
    *   访问 `系统导航页` (`/`)。
    *   点击 `信息自主申报` (`/submit-info/`) 填写并提交个人信息和照片。
    *   提交后，可通过 `查询代表证` (`/query/`) 输入姓名和学号查询审核状态。
    *   若审核通过，将自动跳转至个人 `电子代表证展示页` (`/card-display/?card_number=XXXX`)。
    *   在电子代表证页面，可以查看详情、翻转卡片、保存电子版、查看会议议程。

2.  **管理员/工作人员**:
    *   访问 `系统导航页` (`/`)。
    *   点击 `管理员登录` (`/admin/login/`) 或直接访问 `/admin/` 进行登录。
    *   登录后，可通过导航页访问以下功能：
        *   `扫码签到操作` (`/scan-checkin/`): 使用摄像头扫描代表证二维码或手动输入卡号进行签到。
        *   `仪表盘` (`/dashboard/`): 查看会议代表数据的统计图表和KPI。
        *   `代表信息概览` (`/delegates-list/`): 查看、搜索、筛选和排序所有代表信息。
        *   `后台管理` (`/admin/`):
            *   进入 "Delegate Card App" -> "代表信息管理"。
            *   审核新的代表申请、修改现有代表信息、查看详情。
            *   可使用列表页的批量操作进行审核。

## 未来展望

*   **批量导入/导出**: 支持通过 Excel 等格式批量导入代表名单或导出已审核代表信息。
*   **通知系统**:
    *   审核结果（通过/不通过）通过短信或邮件通知代表。
    *   会议重要通知推送。
*   **权限细化**: 为不同类型的工作人员设置更细致的访问和操作权限。
*   **打印优化**: 提供更适合物理打印的代表证模板。
*   **多语言支持**: 为系统增加英文等其他语言界面。
*   **日志审计**: 记录关键操作日志，便于追溯。
*   **与其他系统集成**: 如学校教务系统，自动同步部分学生信息。

## 贡献

欢迎对本项目进行贡献！如果您有任何建议或发现任何问题，请随时提交 Issue 或 Pull Request。

## 许可证

本项目采用 [MIT许可证](LICENSE) (如果项目中包含 LICENSE 文件，请指向它，否则可以写明)。
