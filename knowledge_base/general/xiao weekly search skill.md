---
name: xiao-weekly-search
description: XIAO 系列硬件热门项目多源搜索与去重（含黑名单机制）。执行 GitHub + YouTube + Instructables 多源搜索，并基于 projects.yaml + blacklist.md 去重后输出最终结果。
---

# xiao-weekly-search

从 GitHub、YouTube、Instructables 三个渠道搜索 XIAO 系列硬件项目，完成去重、信息补全、细筛，并输出可写入候选池。

---

# 🧠 全局执行原则（必须严格遵守）

## ⚠️ STRICT EXECUTION MODE

**This skill runs under ~.openclaw/workspace/EXECUTION_KERNEL.md rules.**

**Every task execution MUST run ~.openclaw/workspace/EXECUTION_SCORE_SYSTEM.md.**

<!-- FORBIDDEN DURING EXECUTION:
- tool substitution
- workflow changes
- step skipping
- external search outside defined scripts
- re-running phases
- Skill defines workflow steps. Skill does NOT grant automatic write permission. Any file modification still requires Carla approval.
- Output only what is explicitly requested. Do not enhance, optimize, summarize, or decorate outputs.
- 如果发现问题或疑问，停下来提出，不要自行决定更改流程
- 所有搜索（GitHub / YouTube / Instructables）**只执行一次**
- 所有 YAML（white + black）**只读取一次**
- 每次回复都严格自检且评分 -->

---

## 📂 数据源

### 白名单（已收录项目）

```bash
~/Documents/OSHW-XIAO-Series/projects.yaml
```

### projects.yaml 格式
```yaml
 ========== 添加新项目模板 / Template for New Projects ==========

   - name:
       en: "Project Name"
       zh: "项目名称"
     description:
       en: "Brief description of the project"
       zh: "项目简介"
     board: "XIAO Model"
     category:
       en: "Category"
       zh: "分类"
     year: 
     author:
       en: "Author Name"
       zh: "作者名称"
     author_type: "Community" or "Official"
     link: "Project URL"
     image: "Image URL"
 ========== Board Options / 型号选项 ==========
 XIAO ESP32-S3, XIAO ESP32-S3 Sense, XIAO ESP32-C3, XIAO ESP32-C6, XIAO ESP32-C5
 XIAO nRF52840, XIAO nRF52840 Sense, XIAO nRF54L15 Sense
 XIAO RP2040, XIAO RP2350, XIAO SAMD21, XIAO RA4M1
 XIAO MG24, XIAO MG24 Sense
 ========== Category Options / 分类选项 ==========
 en: Wearables, Robotics, Smart Home, Healthcare, Power Management
     AI Gadget, Tools & Accessories, Telecommunication, Mechanical Keyboard, LED Lighting
 zh: 可穿戴, 机器人, 智能家居, 健康护理, 电源管理, AI Gadget, 工具配件, 通信, 机械键盘, LED 灯光
```

### 黑名单（噪声项目库）

```bash
~/Documents/blacklist.md
```

---

### blacklist.md 格式

```yaml
- link: "Project URL"
  reason: "Why filtered"
```

---

## PRE-FLIGHT CHECK (MANDATORY)

Before execution starts:

The assistant MUST output:

1. Execution plan (all phases)
2. Tools to be used (explicit list)
3. Data sources (files/scripts/APIs)
4. WAIT FOR USER CONFIRMATION ("CONFIRM")

❗ Execution cannot start without confirmation

# 🚀 Phase 1 — 多源一次性搜索（禁止回查）

<!-- ## ⚠️ OUTPUT CONTRACT (STRICT):

Phase 1 is a RAW DATA EXTRACTION STAGE ONLY.

FORBIDDEN:
- No analysis of relevance
- No commentary on quality
- No summarization of results
- No interpretation of "XIAO relevance"
- No evaluation of dataset quality
- No suggestions for next steps

Any analytical sentence (including "results are good/bad/low relevance") is INVALID. -->


## 1a. GitHub 搜索（Top 60）

执行以下 3 个请求（一次性执行完）：

```bash
# 1. XIAO SAMD21 / RA4M1 / Seeeduino XIAO
curl -s "https://api.github.com/search/repositories?q=(\"XIAO+SAMD21\"+OR+\"XIAO+RA4M1\"+OR+\"Seeeduino+XIAO\"+OR+\"Seeed+Studio+XIAO\")+in:readme+pushed:>{7天前的日期}+stars:>30&sort=stars&order=desc&per_page=20"

# 2. XIAO nRF / BLE / MG24 / RP2040 / RP2350
curl -s "https://api.github.com/search/repositories?q=(\"XIAO+nRF52850\"+OR+\"XIAO+nRF54L15\"+OR+\"XIAO+BLE\"+OR+\"XIAO+MG24\"+OR+\"XIAO+RP2040\"+OR+\"XIAO+RP2350\")+in:readme+pushed:>{7天前的日期}+stars:>30&sort=stars&order=desc&per_page=20"

# 3. XIAO ESP32 Series
curl -s "https://api.github.com/search/repositories?q=(\"XIAO+ESP32\"+OR+\"XIAO+ESP32S3\"+OR+\"XIAO+ESP32C3\"+OR+\"XIAO+ESP32C6\"+OR+\"XIAO+ESP32C5\")+in:readme+pushed:>{7天前的日期}+stars:>30&sort=stars&order=desc&per_page=20"
```

将3个结果合并输出Markdown preview：

```md
## GitHub Raw Pool (UNFILTERED)
1. ⭐stars | repo full name | description | url 
...
```

---

## 1b. YouTube 搜索

```bash
~/.openclaw/workspace/skills/xiao-weekly-search/scripts/search_youtube.py
python3 scripts/search_youtube.py
```

输出Markdown preview：

```md
## YouTube Raw Pool (UNFILTERED)
1. duration | title | description | url
...
```

---

## 1c. Instructables 搜索

```bash
~/.openclaw/workspace/skills/xiao-weekly-search/scripts/search_instructables.py
python3 scripts/search_instructables.py
```

输出Markdown preview：

```md
## Instructables Raw Pool (UNFILTERED)
1. title | description | url
...
```

---

# 🧊 Phase 2 — 粗筛（仅去重）

<!-- ## ⚠️ INFORMATION ISOLATION RULE:

Phase 2 MUST NOT use any enrichment data.
Only URL-based comparison is allowed.
Any classification or content understanding is forbidden here.
此阶段开始禁止任何网络请求，禁止类型判断，仅做 whitelist / blacklist 去重 -->

---

## 2a. 加载去重库（只读一次）

```text

# 解析 projects.yaml：遍历该文件，提取出所有条目下 link: 对应的值，存入 whitelist_set
whitelist_set ← projects.yaml (link)

# 解析 blacklist.md：同理，提取出 link: 对应的值，存入 blacklist_set
blacklist_set ← blacklist.md (link)

# 求并集 (∪)：将这两个集合合并。由于是“Set（集合）”操作，重复的链接会被自动剔除
dedup_set = whitelist_set ∪ blacklist_set

# 新建粗筛结果缓存空间
rough_candidate_pool = []
```

---

## 2b. 粗筛逻辑（单次执行）

对所有 raw pool 执行：

* ❌ link ∈ whitelist → 已收录
* ❌ link ∈ blacklist → 已过滤历史噪声
* ✅ 其余全部进入 rough_candidate_pool

---

## 2c. 输出粗筛结果

```md
## Rough Dedup Result

- GitHub: X
- YouTube: X
- Instructables: X
- Total: X
```

---

# 🎨 Phase 3 — 批量 enrichment（基于 rough_candidate_pool）

## ⚠️ PRECONDITION:

Only inputs from rough_candidate_pool are allowed.

<!-- ## ⚠️ ENRICHMENT DATA CONTRACT:

All enrichment outputs MUST satisfy two responsibilities:

1. Filtering Support (used in Phase 4)
2. YAML Completion Data Source (used in Phase 5)

Enrichment MUST include all fields required by projects.yaml:
- author
- image
- description
- board inference
- category hints
- year

If any field is missing:
→ explicitly mark as null
→ DO NOT re-fetch or re-run enrichment -->

## Unified Fields

## Unified Output Schema

```text
name
author
image

summary_blog

board
category
year

programming_language
secondary_languages
framework_tool
runtime_platform

key_tech
hardware_stack
use_case

source_evidence
confidence
```

Missing values must be `null`.

No re-fetch.

---

## 3a. GitHub 信息

使用Github token提取：
- GitHub图片
  1. README 第一张图片（排除 badge）
  2. open_graph_image_url
  3. 空
- repo topics/description
- README summary about XIAO
- author

---

## 4b. YouTube 信息

```bash
curl -s "https://www.youtube.com/oembed?url={video_url}&format=json"
```

提取：

* author_name → author
* thumbnail_url → 替换为 maxresdefault.jpg

---

## 4c. Instructables

抓取页面提取：

* author
* og:image
* summary

---



# 🔍 Phase 4 — 细筛（类型筛选 + 最终候选池）

---

## 4a. 类型筛选（仅基于 enrichment 后数据）

❌ 排除：
1. SDK/Driver：提供被别人调用的接口库，不是独立项目
2. 收集型/课程型：标题含数字规律或"collection"的合集，不是单一项目
3. 虚假引用：README仅在兼容列表/feature list中提到XIAO，无代码/硬件
4. 噪音：搜索命中但无真实 XIAO 使用

✅ 保留（其余全部）：
- 任何有具体XIAO使用示例的，不管项目多通用
- 任何以XIAO为主控的硬件产品/扩展板/PCB设计/集成产品
- 任何基于XIAO的软件应用（网络协议、无线电、嵌入式Linux风格应用）
- 不管项目是嵌入式/软件/游戏/任何形态
- 不管我认为它是否"配得上"叫XIAO项目
- 只要README有XIAO真实引用，就保留

---

## 4b. 输出去重报告

```md
## Dedup Report

### GitHub
- ❌ reason
- ✅ keep reason

### YouTube
- ❌ reason
- ✅ keep reason

### Instructables
- ❌ reason
- ✅ keep reason
```
---

## 4c. 黑名单新增缓存与最终候选池（锁定）

```md
GitHub: X
YouTube: X
Instructables: X
Total: X
```

```text
# 新增黑名单缓存
new_blacklist_buffer ← 本阶段被淘汰项目

# 新增FINAL CANDIDATE POOL (LOCKED)
final_candidate_pool ← 最终候选池项目
```

⚠️ 从此之后：

❌ 禁止重新筛选
❌ 禁止重新 enrichment
❌ 禁止回查数据

---

# 🧾 Phase 5 — 文件写入（需 Carla 批准）

## ⚠️ 未获得 Carla 明确批准前，只输出预览，不得写文件

---
## 5a. blacklist.md（历史噪声库）

输出：

```md
## Blacklist Updates (NEW)
- link | reason
```

执行：

```text
blacklist.md += new_blacklist_buffer
```

---
## 5b. review-notes.md（人工判断记录）

~/Documents/review-notes.md

用途：

* Carla 指出误判项目
* Carla 修正 category / board / author
* Carla 指出某类项目应保留或应淘汰
* Carla 修改筛选标准

输出：

```md
## Review Notes Preview

### YYYY-MM-DD

- Project: xxx
  Link: xxx
  AI Decision: Reject
  Carla Correction: Keep
  Reason: Real XIAO project with valid hardware usage

- Project: xxx
  AI Category: Tools
  Carla Correction: Mechanical Keyboard
```

```text
append manual corrections / Carla decisions
```

---
## 5c. projects.yaml（最终候选池写入预览）


输出（必须使用 projects.yaml 标准格式）,可包含多个条目。：

```yaml
- name:
    en: ""
    zh: ""
  description:
    en: ""
    zh: ""
  board: ""
  category:
    en: ""
    zh: ""
  year:
  author:
    en: ""
    zh: ""
  author_type: "Community"
  link: ""
  image: ""
```

执行：
```text
projects.yaml += final_candidate_pool

# 新增位置在`projects:` 之后
# 加上开头：
  # ========== 2026-04-16 Community Projects ==========
  # Source: xiao-weekly-search(日期)
```

---

## 执行顺序（批准后）

1. 写入 blacklist.yaml
2. 写入 review-notes.md
3. 写入 projects.yaml

---

获得 Carla 明确批准后方可执行写入。

