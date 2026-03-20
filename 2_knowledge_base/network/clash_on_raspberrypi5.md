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
