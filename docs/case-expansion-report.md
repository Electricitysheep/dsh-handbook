# DSH 复杂案例扩展报告

> 执行时间：2026-08-13
> 执行模型：deepseek-v4-flash（via opencode-go 网关）
> 执行方式：`npx -y @deepseek-ai/dsh --profile headless`
> 数据声明：全部使用合成数据/自造代码，未触碰任何真实业务数据、密钥或敏感信息。

---

## 案例 C：HTML 页面构建与解析（Web 前端领域）

### 任务描述
基于一个包含表格+表单+图表的合成 HTML 页面（`page.html`，8 行产品库存数据），要求 dsh 编写一个零第三方依赖的 Python 解析脚本，提取指定表格并以 CSV 格式输出到 stdout，最后运行验证。

### 输入产物
- `page.html`：合成电子产品库存看板，含 `<table id="product-table">`（8 行数据 × 7 列）、补货表单、CSS 图表

### dsh 执行过程
- **启动**：2026-08-13T12:17:54-04:00
- **结束**：2026-08-13T12:21:12-04:00
- **耗时**：约 3 分 18 秒

### 工具链路径（从输出推断）
1. 读取 `page.html`（文件系统工具）
2. 分析 HTML 结构（语义理解）
3. 编写 `parser.py`（代码生成工具）
4. 运行 `python parser.py`（shell 执行工具）
5. 比对输出与原始表格（验证工具）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case3/page.html` | 输入 HTML（合成数据） |
| `case3/parser.py` | dsh 生成的解析脚本（标准库 `html.parser`，78 行） |
| `case3/case3-output.txt` | 运行记录与验证结果 |

### 验证结果
- **文件存在**：parser.py ✓、case3-output.txt ✓
- **内容检查**：parser.py 使用 `HTMLParser` 子类，含表格深度计数、安全退出机制
- **运行验证**：输出 9 行 × 7 列 CSV，与 page.html 中表格逐字段核对一致
- **编码**：UTF-8，无 BOM，零第三方依赖

### 输出亮点
- **零依赖策略**：dsh 主动选择标准库 `html.parser` 而非 BeautifulSoup，体现了对"最小依赖"的权衡
- **健壮性设计**：实现了 `table_depth` 嵌套计数，防止页面中嵌套表格导致解析越界
- **路径无关性**：使用 `os.path.dirname(os.path.abspath(__file__))` 定位 HTML 文件，不依赖运行目录

---

## 案例 D：代码重构（软件工程领域）

### 任务描述
给定一段约 200 行的过程式 Python 订单处理脚本（含重复代码 `calc_order_total` / `calc_order_total_v2`），要求 dsh 重构为面向对象 + 职责分离风格，保持行为一致，并用测试验证。

### 输入产物
- `legacy_orders.py`：过程式风格，全局状态 + 函数集合，含重复金额计算逻辑

### dsh 执行过程
- **启动**：2026-08-13T12:22:00-04:00
- **结束**：2026-08-13T12:26:37-04:00（测试追加时间）
- **耗时**：约 4 分 37 秒

### 工具链路径（从输出推断）
1. 读取并分析 `legacy_orders.py`（代码分析工具）
2. 识别重复代码与职责边界（语义理解）
3. 编写 `orders_refactored.py`（代码生成工具）
4. 编写 `test_refactor.py`（测试生成工具）
5. 运行测试并对比输出（shell 执行 + 验证工具）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case4/legacy_orders.py` | 输入代码（过程式，约 200 行） |
| `case4/orders_refactored.py` | 重构后代码（OOP，312 行，dataclass + 职责分离） |
| `case4/test_refactor.py` | 行为一致性测试脚本（186 行，17 项检查） |
| `case4/case4-output.txt` | 运行记录与测试结果 |

### 验证结果
- **文件存在**：orders_refactored.py ✓、test_refactor.py ✓、case4-output.txt ✓
- **测试覆盖**：17/17 项全部 PASS，退出码 0
  - format_report() 输出完全一致（固定时间戳后）
  - export_json() 文本 + 解析后数据一致
  - 全部查询函数（get_customer_orders ×4、get_product_sales ×5、get_region_summary、get_pending_orders）一致
  - calc_order_total(未知ID) 均返回 0.0
  - 脚本整体运行产物（report.txt、orders.json）一致
- **结论**：重构前后行为完全一致

### 输出亮点
- **精准识别重复**：dsh 准确识别出 `calc_order_total` 与 `calc_order_total_v2` 是同一逻辑的两份实现，合并为 `Order.total()` 单一入口
- **职责分离设计**：Product/Customer/Order（领域模型）+ OrderProcessor（数据仓库与查询）+ ReportGenerator（报告与导出），符合 SOLID 原则
- **向后兼容**：保留模块级函数接口（`load_data()`、`calc_order_total()` 等），可直接替换调用
- **测试深度**：不仅对比函数返回值，还对比了脚本级整体运行产物（report.txt / orders.json），并处理了时间戳差异
- **沙箱感知**：dsh 注意到 `tempfile.mkdtemp` 的 0700 ACL 在沙箱下不可写，主动改为 `os.makedirs` 方案

---

## 案例 E：API 文档生成（文档领域）

### 任务描述
给定一个含 8 个函数的 Python 模块（`user_module.py`，含类型注解、docstring、示例），要求 dsh 生成完整 Markdown API 文档，含参数表、返回值、异常、示例、边界说明。

### 输入产物
- `user_module.py`：8 个函数（create_user, get_user, update_user, delete_user, list_users, validate_user_email, batch_create_users, get_user_statistics），均有 docstring 和类型注解

### dsh 执行过程
- **启动**：2026-08-13T12:28:56-04:00
- **结束**：2026-08-13T12:30:00-04:00
- **耗时**：约 1 分 4 秒

### 工具链路径（从输出推断）
1. 读取 `user_module.py`（文件系统工具）
2. 解析函数签名、docstring、类型注解（代码分析工具）
3. 分析文档契约与实际实现的差异（语义理解）
4. 生成 `API.md`（文档生成工具）
5. 验证文档完整性（验证工具）

### 产出清单
| 文件 | 说明 |
| --- | --- |
| `case5/user_module.py` | 输入 Python 模块（合成数据） |
| `case5/API.md` | 生成的 Markdown API 文档（423 行，ReadTheDocs 风格） |
| `case5/case5-output.txt` | 运行记录（含完整 API.md 内容） |

### 验证结果
- **文件存在**：API.md ✓、case5-output.txt ✓
- **内容检查**：
  - 目录完整：模块概述、快速开始、8 个函数参考、通用约定与边界情况
  - 每个函数含：完整签名、参数表（名称/类型/必填/说明）、返回值说明、异常表、使用示例（含 doctest 风格）、边界情况说明
  - 通用约定章节：user_db 可变性、时间戳格式、校验范围说明、异常 vs 返回值行为对照表、线程安全、依赖说明
- **结构验证**：通过 grep 确认全部 8 个函数章节及目录、通用约定章节均完整存在

### 输出亮点
- **契约差异识别**：dsh 不仅复制 docstring，还主动对比了"文档声明"与"实际代码实现"的差异（如 `user_id` 字符集、`name` 长度、`role` 枚举在代码中未强制校验），并如实写入"边界情况"章节
- **防御式文档**：为每个函数提供了边界情况说明，提示调用方注意潜在陷阱（如 `list_users` 的负数 `limit`、空 `updates` 字典行为）
- **风格一致性**：采用 ReadTheDocs 风格，参数表、异常表、返回值表格式统一，示例含 doctest 风格输入输出
- **完整性**：423 行文档覆盖了模块的全部公共接口，无遗漏函数

---

## 综合统计

| 案例 | 功能领域 | 耗时 | 验证结果 | 核心亮点 |
| --- | --- | --- | --- | --- |
| C | Web 前端（HTML 解析） | ~3m18s | 通过 | 零依赖、嵌套深度安全、路径无关 |
| D | 软件工程（代码重构） | ~4m37s | 17/17 PASS | 精准消除重复、SOLID 职责分离、向后兼容、沙箱感知 |
| E | 文档（API 文档生成） | ~1m04s | 通过 | 契约差异识别、防御式边界说明、ReadTheDocs 风格 |

**总耗时**：约 9 分钟（三个案例串行执行）
**全部使用合成数据**：✓ 无真实业务数据、密钥或敏感信息

---

*报告生成时间：2026-08-13*
