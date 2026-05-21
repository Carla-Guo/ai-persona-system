# 📌 知识库：嵌入式串口命令解析与容错设计

## 一、 核心认知与三大硬坑

### 1. 触发时机坑（长度触发 vs 结束符触发）

* **错误做法：** 只要检测到关键词长度（如 `MIN=` 满 4 字节）就立刻触发解析。因为串口是按字节逐个接收的，这会导致等号后面的数字还没传完，程序就急忙去解析空字符串，从而把数值误判为 `0.0`。
* **正确做法：** 必须使用换行符（`\n` 或 `\r`）作为一帧数据的“结束标志”。只有收到结束符，才代表整行指令发送完毕，此时触发解析最安全。

### 2. 串口助手的“手打 \r”误区

* 在串口调试助手输入框里手打的 `\r` 或 `\n` 会被当成**普通文本字符**（`\` 和 `r`，占 2 字节）发送。
* 代码中的 `'\n'` 和 `'\r'` 指的是**不可见的控制字符（ASCII 码 10 和 13）**。必须通过调整串口调试助手的“结束符/Line Ending”设置（选 LF 或 CRLF），让软件在发送时自动在末尾追加控制字符。

### 3. `static` 变量的妙用

* 接收缓冲区 `static String command = "";` 必须声明为 `static`（静态）。这样即使函数反复退出和进入，已经接收到的半截字符串也不会丢失，能像滚雪球一样往后拼接。

---

## 二、 标准串口命令解析模板（Arduino C++）

这是一套具备**自动过滤多余换行、大小写容错、防空指令、自动切除首尾空格**的高健壮性标准模板。

```cpp
// 全局变量定义（示例）
float minTemp = 18.0;
float maxTemp = 30.0;

/**
 * @brief 串口命令接收器（在 loop 中持续调用）
 * 核心逻辑：利用静态变量拼装字符，直到遇见换行符才触发解析，并完美过滤双换行符（\r\n）。
 */
void handleSerialCommand() {
  static String command = ""; // 静态变量，函数退出后内容不销毁

  while (Serial.available()) {
    char c = Serial.read();

    // 检测到换行符（回车或换行），说明一帧指令发送完毕
    if (c == '\n' || c == '\r') {
      if (command.length() > 0) { // 确保不是连续换行造成的空行
        parseCommand(command);    // 移交解析器
        command = "";             // 解析完后立刻清空，准备接收下一条
      }
      return; // 退出函数，防止单次循环处理过多导致阻塞
    }

    // 还没收到结束符，持续将当前字符拼接到命令末尾
    command += c;
  }
}

/**
 * @brief 串口命令解析执行器
 * 核心逻辑：容错清洗 -> 前缀匹配 -> 字符串切片 -> 类型转换
 */
void parseCommand(String cmd) {
  cmd.trim();        // 切除字符串首尾的不可见杂质（如空格）
  cmd.toUpperCase(); // 强制转换为全大写，实现大小写不敏感（如 min=25 -> MIN=25）

  // 1. 匹配 MIN 命令
  if (cmd.startsWith("MIN=")) {
    // 从索引 4（即 '=' 后面）开始截取到最后
    String numStr = cmd.substring(4); 
    float val = numStr.toFloat();     // 转换为浮点数（空字符串或纯字母默认转为 0.0）
    
    minTemp = val;
    Serial.print("Set MIN to: ");
    Serial.println(minTemp);
  } 
  // 2. 匹配 MAX 命令
  else if (cmd.startsWith("MAX=")) {
    float val = cmd.substring(4).toFloat();
    maxTemp = val;
    Serial.print("Set MAX to: ");
    Serial.println(maxTemp);
  } 
  // 3. 未知命令未知处理
  else {
    Serial.println("Unknown command. Use: MIN=value or MAX=value");
  }
}

```

---

## 三、 标准模板下的调试行为速查表

在开启串口助手结束符（LF 或 CRLF）的前提下，各类输入的预期运行结果如下：

| 串口输入文本 | 实际解析字符串 | 转换为 `float` 的机制与结果 | 串口最终打印 | 评估与结论 |
| --- | --- | --- | --- | --- |
| `MIN=-1` | `"MIN=-1"` | 正确识别负号，转为 `-1.0` | `Set MIN to: -1.00` | **正常**。负数设置成功。 |
| `MIN=100` | `"MIN=100"` | 正确识别多位数，转为 `100.0` | `Set MIN to: 100.00` | **正常**。百位数设置成功。 |
| `min=2.5` | `"MIN=2.5"` | 大小写自动修复，转为 `2.5` | `Set MIN to: 2.50` | **正常**。支持大小写混敲与浮点数。 |
| `MIN=` | `"MIN="` | 后面无内容，`.toFloat()` 默认返回 `0.0` | `Set MIN to: 0.00` | **容错成功**。不会死机，默认赋零。 |
| `MIN= 25 ` | `"MIN=25"` | `trim()` 和 `toFloat()` 会自动过滤前后的空格 | `Set MIN to: 25.00` | **容错成功**。误触空格不影响结果。 |
| `MIN=25MAX=30` | `"MIN=25MAX=30"` | `.toFloat()` 读到非数字字符 `M` 时停止，只抓取到 `25` | `Set MIN to: 25.00` | **部分容错**。前部分指令生效，后半截被丢弃。 |
| `MIN = 25` | `"MIN = 25"` | 中间带空格导致 `startsWith("MIN=")` 匹配失败 | `Unknown command...` | **拦截**。指令格式不合规，拒绝执行。 |
