# DSH 复杂案例扩展报告 · 第三批（日志分析 / 数据迁移 / 单测生成）

> 执行时间：2026-08-13
> 执行模型：deepseek-v4-flash（via opencode-go 网关）
> 执行方式：`npx -y @deepseek-ai/dsh --profile headless`
> 数据声明：全部使用合成数据/自造代码，未触碰任何真实业务数据、密钥或敏感信息。

---

## 案例 F：日志分析与异常检测（运维可观测性领域）

### 任务描述
给定一份 200 行合成应用日志（`app.log`，2026-08-13 上午 09:00–11:59，格式 `时间戳,毫秒 [级别] [模块] 消息`，含 ERROR/WARN 与刻意注入的错误爆发窗口），要求 dsh 编写一个零第三方依赖的 Python 分析脚本，统计错误率、TOP 错误类型、小时级趋势并识别异常模式，最后生成 Markdown 分析报告并运行验证。

### 输入产物
- `app.log`：合成日志 200 行。ground truth：INFO 130 / DEBUG 20 / WARN 20 / ERROR 30（错误率 15%）；错误类型 DatabaseError 10 / ConnectionTimeout 8 / RateLimitExceeded 7 / ValidationError 3 / AuthFailure 2；其中 23 条错误集中在 10:00–10:59 爆发窗口

### dsh 执行过程
- **启动**：2026-08-13T13:11:08-04:00
- **结束**：2026-08-13T13:17:03-04:00
- **耗时**：约 5 分 55 秒

### 工具链路径（从输出推断）
1. 读取 `app.log`（文件系统工具）
2. 分析日志格式与错误模式（语义理解）
3. 编写 `log_analyzer.py`（代码生成工具，392 行）
4. 运行 `python log_analyzer.py`（shell 执行工具）
5. 校验统计结果并生成 `log-report.md`（验证 + 文档生成工具）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case6/app.log` | 输入日志（200 行，合成数据） |
| `case6/log_analyzer.py` | dsh 生成的分析脚本（392 行，纯标准库） |
| `case6/log-report.md` | 生成的分析报告（83 行，含趋势图与结论） |
| `case6/case6-output.txt` | 运行记录与验证结果 |

### 验证结果（14 项指标 100% 一致）
- **文件存在**：log_analyzer.py ✓、log-report.md ✓、case6-output.txt ✓
- **独立核对**：grep 直接统计 app.log，与脚本输出逐项对比
  - 总行数 200 ✓；DEBUG 20 / INFO 130 / WARN 20 / ERROR 30 ✓；错误率 15.0% ✓
  - 错误类型：DatabaseError 10 / ConnectionTimeout 8 / RateLimitExceeded 7 / ValidationError 3 / AuthFailure 2 ✓
  - 小时趋势 09:00=5 / 10:00=23 / 11:00=2 ✓（10:00 爆发窗口识别正确）
- **报告结构**：概览表、级别分布、TOP 错误、小时趋势（ASCII 柱状图）、3 个爆发窗口明细、结论建议、复现附录全部齐全

### 输出亮点
- **零第三方依赖**：仅用标准库 `argparse`/`bisect`/`collections`/`datetime`/`math`/`re`/`pathlib`，开箱即用
- **解析容错**：正则精确匹配日志格式的同时统计"解析失败/跳过行数"，脏数据不静默吞掉
- **滑动窗口爆发检测**：10 分钟窗口 + 阈值 `max(3, 2×期望值)`，重叠窗口智能去重，精准识别出 3 个错误爆发时段
- **ASCII 可视化**：小时级趋势用 `#` 比例柱状图呈现（10:00 = 26.7% 错误率），无需任何图表库
- **完全可复现**：窗口时长/阈值/期望倍数全部命令行可调，报告附录给出复现命令与解析规则

---

## 案例 G：CSV → SQLite 数据迁移（数据工程领域）

### 任务描述
给定一份 50 行合成员工数据 CSV（`data.csv`，8 列），要求 dsh 编写迁移脚本，处理类型转换（千分位逗号工资、yes/no/true/false 多态布尔、混合日期格式、空值、重复 id）并应用表约束（PRIMARY KEY / NOT NULL / CHECK），迁移完成后编写独立验证脚本核对行数、唯一性、约束与抽样数据。

### 输入产物
- `data.csv`：50 行（物理），48 个唯一 id（id 7、21 各重复一次）。刻意注入：id5 非法日期 `2024/02/30`；id9 负工资 `-100.00`（违反 CHECK）；id12 日期 `15/03/2024`（DD/MM/YYYY）；id17 空工资；id3 邮箱无 TLD；id22 邮箱含空格；id31 空邮箱；id40 部门 `marketing`（不在 CHECK 枚举）；7 个空 bonus

### dsh 执行过程
- **启动**：2026-08-13T13:11:12-04:00
- **结束**：2026-08-13T13:15:04-04:00
- **耗时**：约 3 分 52 秒

### 工具链路径（从输出推断）
1. 读取并分析 `data.csv` 的列类型与脏数据分布（文件 + 语义分析工具）
2. 设计转换策略：SKIP-AND-WARN / CLEAN-AND-KEEP（语义理解）
3. 编写 `migrate.py`（代码生成工具，292 行）
4. 运行迁移 → 生成 `employees.db`（shell 执行工具）
5. 编写并运行 `verify.py`（测试/验证工具，255 行）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case7/data.csv` | 输入 CSV（50 行，合成数据） |
| `case7/migrate.py` | 迁移脚本（292 行，标准库 csv+sqlite3） |
| `case7/verify.py` | 独立验证脚本（255 行，16 项检查 + 23 项抽样） |
| `case7/employees.db` | 迁移产物（SQLite，46 行） |
| `case7/case7-output.txt` | 运行记录与验证结果 |

### 验证结果（16/16 项检查通过）
- **迁移汇总**：50 行读入 → 46 插入 + 4 跳过（负工资 id9、非法部门 id40、重复 id7/id21）+ 多类清洗保留
- **行数**：DB 实际 46 = migrate.py 报告 46 ✓
- **唯一性**：`COUNT(*)` = `COUNT(DISTINCT id)` = 46 ✓
- **约束零违规**：`salary < 0` → 0 行；department 不在枚举 → 0 行 ✓
- **抽样正确**：id=1 全字段与 CSV 一致（is_active `true`→1、salary 保留 REAL 精度 8350.13）；id9/id40 确认不在 DB ✓

### 输出亮点
- **多态类型统一归一化**：15 行千分位工资 `"14,150.64"` 正确剥离逗号，50 行 is_active 的 yes/no/true/false 全部归一到 0/1，纯标准库实现
- **真实日历校验**：同时支持 ISO / DD-MM-YYYY / YYYY/MM/DD 三种日期格式，对 `2024/02/30` 用 `datetime` 真实日历校验判非法，失败则转 NULL 保留整行而非丢弃
- **显式策略 + 分类计数**：SKIP-AND-WARN（4 行）与 CLEAN-AND-KEEP（多类清洗）全部分类计数并在迁移总结中报告，策略透明可审计
- **验证脚本独立推导**：verify.py 不硬编码期望行数，而是独立读取 CSV、按相同跳过策略重新推导期望 id 集合再比对，防止"迁移与验证共享同一 bug 而互相掩盖"
- **抽样深度**：23 项 spot-check 覆盖正常行、清洗行（逗号/日期/NULL 化）与"必须缺失"行，验证远超简单行数统计

---

## 案例 H：单元测试生成（软件工程质量领域）

### 任务描述
给定一个含 5 个函数的合成模块 `data_utils.py`（parse_duration / chunk_list / fibonacci / is_valid_email / calculate_interest，覆盖字符串解析、列表分块、数值递推、邮箱校验、金融计算，每个函数都有刻意设计的边界与异常语义），要求 dsh 生成完整 pytest 单测（含边界与异常路径）并运行全部通过。

### 输入产物
- `data_utils.py`：5 个函数，95 行。语义要点：parse_duration 组合单位/大小写不敏感/非法→ValueError；chunk_list size≤0→ValueError、非 int（含 bool）→TypeError；fibonacci 0 起始、负数→ValueError；is_valid_email 非字符串→False（不抛异常）、TLD≥2；calculate_interest 支持小数年、负数→ValueError、超大值溢出为 inf

### dsh 执行过程
- **启动**：2026-08-13T13:11:16-04:00
- **结束**：2026-08-13T13:13:58-04:00
- **耗时**：约 2 分 42 秒

### 工具链路径（从输出推断）
1. 读取 `data_utils.py`，解析 5 个函数的签名与异常语义（代码分析工具）
2. 设计用例矩阵：正常 / 边界 / 异常三路覆盖（语义理解）
3. 编写 `test_data_utils.py`（代码生成工具，380 行）
4. 运行 `pytest` 并迭代到全部通过（shell 执行 + 验证工具）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case8/data_utils.py` | 输入模块（5 函数，95 行，未被改动） |
| `case8/test_data_utils.py` | dsh 生成的 pytest 单测（380 行，100 用例） |
| `case8/case8-output.txt` | 运行记录与验证结果 |

### 验证结果（100/100 通过）
- **pytest**：`python -m pytest test_data_utils.py -v` → **100 passed, 0 failed**（0.19s）
- **边界覆盖核对**：人工抽查 31 项边界 + `python -c` 验证 20+ 关键断言，全部与 data_utils.py 真实语义一致，无矛盾
  - parse_duration：'1h30m'=5400、'90s'=90、'2d'=172800、'1H30M' 大小写、None/''/'abc'/'1h30'→ValueError ✓
  - chunk_list：size>len→单块、空列表→[]、size≤0→ValueError、1.5/True→TypeError ✓
  - fibonacci：0→0、1→1、10→55、负数→ValueError、非 int→TypeError ✓
  - is_valid_email：子域/大写→True；空串/'a@b'/'a b@c.com'/'a@@b.com'/'a@b.c'/非字符串→False ✓
  - calculate_interest：(1000,0.05,1)≈1050（approx）、rate/years=0 退化、负数→ValueError、1e308 溢出→inf ✓

### 输出亮点
- **用例密度极高**：5 个函数产出 100 个用例（平均每函数 20 个），远超"至少 5 个"的底线且无一冗余
- **参数化组织优雅**：同类边界用例全部 `@pytest.mark.parametrize` 并带语义化 `ids`（`combined_h_m`、`trailing_digits`、`bool_true`），失败时可秒级定位
- **bool 子类陷阱精准覆盖**：为 `chunk_list`/`fibonacci` 单独设立 `True`/`False` 的 TypeError 用例，准确对应实现中 `isinstance(x, bool)` 前置检查——这是初学者最容易漏掉的 Python 类型陷阱
- **浮点语义到位**：`calculate_interest` 全部用 `pytest.approx`，并主动覆盖 `1e308` 溢出为 `inf` 的边界行为
- **异常消息精确匹配**：大量 `pytest.raises(..., match="must be ...")` 同时校验异常类型与消息文本，而非仅捕获类型，测试鲁棒性高

---

## 综合统计

| 案例 | 功能领域 | 耗时 | 验证结果 | 核心亮点 |
| --- | --- | --- | --- | --- |
| F | 运维可观测性（日志分析） | ~5m55s | 14/14 指标一致 | 零依赖、滑动窗口爆发检测、ASCII 可视化、可复现 |
| G | 数据工程（CSV→SQLite 迁移） | ~3m52s | 16/16 检查通过 | 多态类型归一化、真实日历校验、独立推导验证、显式策略 |
| H | 软件工程（单元测试生成） | ~2m42s | 100/100 PASS | 参数化+语义化 ids、bool 子类陷阱、浮点边界、异常消息匹配 |

**dsh 侧总耗时**：约 12 分 29 秒（三个案例并行执行，墙钟约 7 分 35 秒）
**全部使用合成数据**：✓ 无真实业务数据、密钥或敏感信息

关键产物（`.py`）已归档至 `docs/assets/`：`case-r3-log_analyzer.py`、`case-r3-migrate.py`、`case-r3-verify.py`、`case-r3-data_utils.py`、`case-r3-test_data_utils.py`

---

*报告生成时间：2026-08-13*
