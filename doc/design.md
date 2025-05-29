# upboard

upboard（Update-Board）是一个轻量级的CLI工具，用于在开发期间管理和分发应用程序的测试版本。

**upboard** 通过提供一个简单的HTTP服务器（`upboard-server`）和一个文件发布器（`upboard-publish`）来帮助你将软件更新分发到客户端，应用程序可以在运行时使用标准HTTP请求动态检查和下载更新。

## 项目需求梳理

### upboard-server

- 刚需功能：
  - 一个轻量级的HTTP服务器
  - 接收客户端的请求，返回更新文件。
  - 接收推送的发行版，保存到指定目录，有一个可选的秘钥来验证受信任的客户端。
  - 版本存储结构: 产品名/平台/架构/版本?/版本文件。
    - 每个版本是否需要独立文件夹?
      - 可选：存在独立文件夹, 可以灵活管理, 支持自定义版本升级，但相对复杂而不够直观，因此只有在路径中指定了版本才放在独立文件夹。
      - 比如: 0.1.1 版本的更新文件为 0.1.2, 其他版本的更新文件为 0.1.3, 因此 0.1.1 的目录存储的应该是 0.1.2 的版本文件。
- 可选功能：
  - 一键安装系统服务
  - 简易后台管理面板

接口梳理：

```sh
# 启动服务
upboard-server --host 127.0.0.1 --port 5001 --password mysecret --dir release-dir
```

- `--dir release-dir` 版本文件、日志配置文件等存储目录
  - 默认为当前目录，不存在则报错并终止，给定相对路径则相对于当前目录
  - 版本文件将创建目录：`release-dir/RELEASES`

API 接口

```sh
# 请求更新接口
http://localhost:5001/api/v1/updates/<product>/<platform>/<arch>/[version]/<filename>

# 推送发布接口
http://localhost:5001/api/v1/releases<product>/<platform>/<arch>/[version]/<filename>
```

接口行为：

- 更新接口：
  - 如果包含了版本号，则返回指定版本的更新信息，否则返回最新版本的更新信息。
    - 具体为返回文件: `release-dir/RELEASES/<product>/<platform>/<arch>/version/filename`
    - 指定版本不存在: `release-dir/RELEASES/<product>/<platform>/<arch>/filename`
- 发布接口：
  - 与更新接口类似，文件存储与 URL 路径一致。
  - 如果文件存在则覆盖。

### upboard-publish

- 推送指定文件到服务器
- 推送指定目录下的所有文件到服务器

接口梳理：

```sh
upboard-publish --password mysecret 
    http://localhost:5001/api/v1/releases/projec-name/win32/x64/1.2.3-beta/ 
    release-files
```

必要信息:

- 服务定位: `http://localhost:5001/api/v1/releases/`
- 产品结构: `projec-name/win32/x64/1.2.3-beta/`
- 文件列表: `release-files`
- 鉴权密钥: `--password mysecret`
