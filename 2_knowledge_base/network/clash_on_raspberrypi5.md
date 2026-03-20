# 树莓派 5 (WillowPi) 网络全自动化部署实战全记录

## 一、 环境准备与内核安装
**目标：** 下载并安装适配树莓派 5 (ARM64) 的 Mihomo 内核。

1. **进入工作目录：**
   ```bash
   mkdir ~/clash && cd ~/clash
   ```
2. **下载内核 (v1.19.21)：**
   ```bash
   wget https://github.com/MetaCubeX/mihomo/releases/download/v1.19.21/mihomo-linux-arm64-v1.19.21.gz
   ```
3. **解压文件：**
   *注意：`gunzip` 会在解压后自动删除原 `.gz` 文件。*
   ```bash
   gunzip mihomo-linux-arm64-v1.19.21.gz
   ```
4. **重命名并赋予执行权限：**
   ```bash
   mv mihomo-linux-arm64-v1.19.21 mihomo
   chmod +x mihomo
   ```
5. **版本校验：**
   ```bash
   ./mihomo -v
   ```

---

## 二、 配置文件与初步测试
**目标：** 获取订阅并解决权限/路径报错。

1. **下载订阅配置文件：**
   ```bash
   curl -L -o config.yaml "your url"
   ```
2. **第一次手动测试 (前台运行)：**
   ```bash
   ./mihomo -d .
   ```
   * *现象：* 报错 `bind: permission denied`，原因是无法监听 53 端口。
3. **赋予底层网络权限 (关键加固)：**
   ```bash
   sudo setcap 'cap_net_bind_service=+ep' /home/willowpi/clash/mihomo
   ```

---

## 三、 系统服务化 (Systemd 自动化)
**目标：** 实现开机自启，脱离 SSH 窗口运行。

1. **创建服务配置文件：**
   ```bash
   sudo nano /etc/systemd/system/mihomo.service
   ```
2. **写入配置内容：**
   ```ini
   [Unit]
   Description=Mihomo Meta Proxy for WillowPi
   After=network.target

   [Service]
   User=willowpi
   WorkingDirectory=/home/willowpi/clash
   ExecStart=/home/willowpi/clash/mihomo -d /home/willowpi/clash
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
3. **激活服务流程：**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable mihomo
   sudo systemctl start mihomo
   ```
4. **检查运行状态：**
   ```bash
   sudo systemctl status mihomo
   ```

---

## 四、 环境变量与图形界面适配
**目标：** 让系统所有工具及物理屏幕上的浏览器感知代理。

1. **注入全局代理变量：**
   ```bash
   echo 'export http_proxy="http://127.0.0.1:7890"' >> ~/.bashrc
   echo 'export https_proxy="http://127.0.0.1:7890"' >> ~/.bashrc
   echo 'export no_proxy="localhost,127.0.0.1,localaddress,.local,feishu.cn,qq.com"' >> ~/.bashrc
   source ~/.bashrc
   ```
2. **终端连通性终极测试：**
   ```bash
   curl -x http://127.0.0.1:7890 -I https://www.google.com
   ```
3. **物理屏幕启动浏览器 (解决 $DISPLAY 报错)：**
   ```bash
   export DISPLAY=:0
   chromium --proxy-server="http://127.0.0.1:7890" &
   ```

---

## 五、 经验总结 (Carla's Notes)
* **路径陷阱：** 在 `systemd` 配置中必须使用 `/home/willowpi/clash` 绝对路径，不可使用 `~/`。
* **GUI 报错：** 在 SSH 远程操作图形程序时，必须先 `export DISPLAY=:0` 否则会触发 `Missing X server` 报错。
* **分流策略：** `no_proxy` 必须包含常用内网域名（如 feishu），否则会导致办公软件连接异常。



既然你的新加坡节点已经全线打通，VS Code 内置面板也配置完成了，这绝对是值得记录的一个里程碑。

为了方便你更新 GitHub 的知识库（Knowledge Base），我按照 **“功能模块化”** 的逻辑为你整理了这份 Markdown 文档。你可以直接复制到你的 `README.md` 或 `docs/` 目录下。

---

## 🛠️ 树莓派 Mihomo (Clash Meta) 进阶配置指南

### 1. 目录结构规范
为了确保服务运行稳定，建议统一使用以下路径管理配置文件：
* **程序与主配置目录**: `/home/willowpi/clash`
* **Web UI 静态文件**: `/home/willowpi/clash/ui`
* **Systemd 服务脚本**: `/etc/systemd/system/mihomo.service`

### 2. 外部控制面板 (External UI) 配置
通过在树莓派本地部署 `MetacubexD` 面板，实现 VS Code 内部的一体化管理。

#### A. 面板文件部署
```bash
cd /home/willowpi/clash
mkdir -p ui && cd ui
# 下载并解压 MetacubexD (注意文件夹名称大小写)
wget https://github.com/MetaCubeX/MetacubexD/archive/gh-pages.zip
unzip gh-pages.zip
mv metacubexd-gh-pages/* .
rm -rf metacubexd-gh-pages gh-pages.zip
```

#### B. config.yaml 核心参数
在 `/home/willowpi/clash/config.yaml` 中添加以下内容：
```yaml
# 外部控制 API 端口
external-controller: 0.0.0.0:9090
# 面板访问密钥 (登录时使用)
secret: '123456'
# 静态资源路径 (相对于 -d 指定的工作目录)
external-ui: ui
```

### 3. VS Code 集成方案
无需切换浏览器，利用 VS Code 内置功能实时监控流量：
1. **端口转发**: 在 VS Code 的 "PORTS" 标签页中确保 `9090` 端口已转发。
2. **启动浏览器**: `Ctrl + Shift + P` -> `Simple Browser: Show`。
3. **访问地址**: `http://127.0.0.1:9090/ui/`（注意末尾必须带 `/`）。

### 4. 终端代理与验证

#### 链路状态验证
通过查询出口 IP 验证节点切换是否生效：
```bash
# 预期输出应包含 "country_name": "Singapore" 或目标节点所在地
curl -I https://ipapi.co/json
```

---

### 📝 维护笔记 (2026-03-20)
* **故障排除**: 如果访问面板出现 404，优先检查 `systemctl status mihomo` 确认工作目录 `-d` 的指向是否与 `ui` 文件夹物理路径一致。
* **权限说明**: 确保 `ui` 文件夹具有 `755` 权限，否则 Mihomo 无法读取静态资源。

