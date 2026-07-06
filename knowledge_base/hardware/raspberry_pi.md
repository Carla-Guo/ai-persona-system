# Raspberry Pi 重装系统标准流程

## 1. 文件转移

### 方案A：GitHub（推荐，代码）

适用于：

```text
源码
Markdown
文档
PCB工程
配置文件
```

不适用于：

```text
视频
镜像
压缩包
大模型
```

### 检查大文件

进入仓库：

```bash
cd ~/Documents/OSHW-XIAO-Series
```

检查超过 25MB 的文件：

```bash
find . -type f -size +25M
```

如果有结果：

```text
./video/demo.mp4
./firmware.bin
```

加入 `.gitignore`：

```gitignore
*.mp4
*.zip
*.tar.gz
*.img
*.bin
```

重新提交：

```bash
git add .
git commit -m "backup before reinstall"
git push
```

---

### 方案B：U盘（推荐，资料）

查看U盘：

```bash
lsblk
```

例如：

```text
sda
└─sda1
```

挂载：

```bash
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
```

复制：

```bash
cp -r ~/Documents /mnt/usb/
```

或者：

```bash
tar czvf backup.tar.gz ~/Documents
sudo cp backup.tar.gz /mnt/usb/
```

同步：

```bash
sync
```

卸载：

```bash
sudo umount /mnt/usb
```

---

### 方案C：Windows拉取

树莓派查IP：

```bash
hostname -I
```

Windows PowerShell：

```powershell
scp -r willowpi@192.168.x.x:/home/willowpi/Documents .
```

---

# 2. SD卡格式化恢复容量

## 情况

64GB SD卡刷完树莓派镜像后：

```text
Windows只显示512MB
```

原因：

```text
boot分区 512MB
rootfs分区 60GB+
```

Windows只能看到boot分区。

---

## 推荐方案

安装：

[SD Card Formatter](https://www.sdcard.org/downloads/formatter/?utm_source=chatgpt.com)

直接：

```text
Format
```

即可恢复全部容量。

---

## Windows DiskPart

管理员PowerShell：

```powershell
diskpart
```

查看磁盘：

```text
list disk
```

选择SD卡：

```text
select disk X
```

⚠️ 确认是SD卡

清除全部分区：

```text
clean
create partition primary
format fs=exfat quick
assign
exit
```

恢复完整64GB。

---

# 3. VSCode Remote SSH 远程记录刷新

## 删除 known_hosts

打开：

```text
C:\Users\<用户名>\.ssh\known_hosts
```

删除：

```text
openclawpi
```

对应行。

---

```text
1. GitHub推代码
2. U盘备份Documents
3. 刷机
4. ssh-keygen -R 主机名
5. 删除 ~/.vscode-server
6. 重新连接
```


