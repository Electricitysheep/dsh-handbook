# user_module API 参考文档

> **合成数据声明**：本模块中的全部数据均为虚构演示数据，不包含任何真实用户信息或敏感信息，仅供 API 文档生成与学习演示使用。

**模块路径**：`user_module`

**版本**：1.0.0（演示版）

---

## 目录

- [模块概述](#模块概述)
- [快速开始](#快速开始)
- [函数参考](#函数参考)
  - [create_user](#create_useruser_id-name-email-role--member---dict)
  - [get_user](#get_useruser_id-user_db---optionaldict)
  - [update_user](#update_useruser_id-updates-user_db---dict)
  - [delete_user](#delete_useruser_id-user_db---bool)
  - [list_users](#list_usersuser_db-role-none-status-none-limit-100-offset-0---tuplelistdict-int)
  - [validate_user_email](#validate_user_emailemail---bool)
  - [batch_create_users](#batch_create_usersusers_data-user_db---tuplelistdict-liststr)
  - [get_user_statistics](#get_user_statisticsuser_db---dict)
- [通用约定与边界情况](#通用约定与边界情况)

---

## 模块概述

`user_module` 是一个基于内存字典（`Dict[str, Dict]`）实现的用户管理模块，提供用户的**增、删、改、查、分页列表、批量创建与统计**等完整操作能力。该模块不依赖任何外部存储，所有数据保存在由调用方传入的字典 `user_db` 中，因此非常适合作为演示、原型或教学场景中的数据层组件。

### 设计要点

- **内存存储**：所有函数均接收 `user_db: Dict[str, Dict]` 作为"数据库"，键为用户 ID，值为用户字典，函数内部直接读写该字典。
- **用户字典结构**：由 `create_user` 创建的用户包含以下字段：

  | 字段 | 类型 | 说明 |
  | --- | --- | --- |
  | `id` | `str` | 用户唯一标识 |
  | `name` | `str` | 用户显示名称 |
  | `email` | `str` | 用户邮箱 |
  | `role` | `str` | 用户角色，取值为 `"admin"` / `"member"` / `"guest"` |
  | `created_at` | `str` | 创建时间（ISO 8601 格式字符串） |
  | `status` | `str` | 用户状态，取值为 `"active"` / `"deleted"` |

  经 `update_user` 更新后会追加 `updated_at` 字段；经 `delete_user` 软删除后会追加 `deleted_at` 字段。

- **异常约定**：非法参数（格式错误、越界、非法字段）抛出 `ValueError`；目标用户不存在时，`update_user` 抛出 `KeyError`，而 `delete_user` 返回 `False`（详见各函数说明）。

### 快速开始

```python
from user_module import create_user, get_user, update_user, delete_user, list_users, get_user_statistics

db = {}

# 1. 创建用户
create_user("U001", "张三", "zhangsan@example.com", "admin")

# 2. 查询用户
user = get_user("U001", db)          # -> {'id': 'U001', 'name': '张三', ...}

# 3. 更新用户
update_user("U001", {"name": "张三三"}, db)

# 4. 分页列出所有管理员
users, total = list_users(db, role="admin")

# 5. 软删除
delete_user("U001", db)              # -> True

# 6. 统计
get_user_statistics(db)              # -> {'total': 1, 'active': 0, 'deleted': 1, ...}
```

---

## 函数参考

### `create_user(user_id: str, name: str, email: str, role: str = "member") -> Dict`

创建一个新用户并返回其完整用户字典。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | `str` | 是 | 用户唯一标识符，长度 4–20 字符，文档约定仅含字母、数字和下划线。 |
| `name` | `str` | 是 | 用户显示名称，长度 1–50 字符。 |
| `email` | `str` | 是 | 用户邮箱地址，需包含 `@`（基本格式校验）。 |
| `role` | `str` | 否 | 用户角色，可选值为 `"admin"`、`"member"`、`"guest"`，默认 `"member"`。 |

#### 返回值

返回 `Dict`，包含字段：`id`、`name`、`email`、`role`、`created_at`（ISO 8601 时间戳）、`status`（固定为 `"active"`）。

#### 异常

| 异常 | 触发条件 |
| --- | --- |
| `ValueError` | `user_id` 为空或长度不在 4–20 字符之间；或 `email` 中不包含 `@`。 |

#### 使用示例

```python
>>> create_user("U001", "张三", "zhangsan@example.com", "member")
{'id': 'U001', 'name': '张三', 'email': 'zhangsan@example.com',
 'role': 'member', 'created_at': '2026-08-13T12:30:00.123456', 'status': 'active'}

>>> create_user("U001", "张三", "zhangsan@example.com")   # role 使用默认值
{'id': 'U001', 'name': '张三', 'email': 'zhangsan@example.com',
 'role': 'member', 'created_at': '...', 'status': 'active'}
```

#### 边界情况

- `user_id` 恰好 4 字符或恰好 20 字符均合法；3 字符、21 字符或空字符串会抛出 `ValueError`。
- 当前实现**仅校验 `user_id` 长度与 `email` 是否含 `@`**，docstring 中"仅含字母数字下划线"及 `name` 长度 1–50 的约定属于文档契约，实际代码未强制校验，传入超长 `name` 或含特殊字符的 `user_id` 不会报错。
- `role` 的值不在此处校验，任意字符串均可传入（非 `admin`/`member`/`guest` 也会被原样保存）。

---

### `get_user(user_id: str, user_db: Dict[str, Dict]) -> Optional[Dict]`

根据用户 ID 查询用户信息。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | `str` | 是 | 要查询的用户 ID。 |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典，键为用户 ID，值为用户字典。 |

#### 返回值

返回该用户对应的字典；若 `user_id` 在数据库中不存在，返回 `None`。

#### 异常

本函数不抛出异常（正常调用路径下）。

#### 使用示例

```python
>>> get_user("U001", {"U001": {"name": "张三"}})
{'name': '张三'}

>>> get_user("NOT_EXIST", db)
None
```

#### 边界情况

- 查询不存在的 ID 返回 `None` 而非抛异常，调用方应使用 `if user is not None` 或 `user or {}` 防御式取值。
- 若 `user_db` 中某键对应的值为 `None`，本函数同样返回 `None`，与"用户不存在"无法区分。

---

### `update_user(user_id: str, updates: Dict, user_db: Dict[str, Dict]) -> Dict`

更新指定用户的一个或多个字段，并自动记录更新时间。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | `str` | 是 | 目标用户 ID。 |
| `updates` | `Dict` | 是 | 要更新的字段字典，仅支持 `name`、`email`、`role`、`status` 四个字段。 |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典。 |

#### 返回值

返回更新后的用户字典（包含新增的 `updated_at` 字段，值为 ISO 8601 时间戳）。

#### 异常

| 异常 | 触发条件 |
| --- | --- |
| `KeyError` | 目标用户 `user_id` 在 `user_db` 中不存在。 |
| `ValueError` | `updates` 中包含除 `name`、`email`、`role`、`status` 之外的字段。 |

#### 使用示例

```python
>>> update_user("U001", {"name": "张三三"}, db)
{'id': 'U001', 'name': '张三三', 'email': 'zhangsan@example.com',
 'role': 'member', 'status': 'active', 'created_at': '...', 'updated_at': '...'}

>>> update_user("U001", {"phone": "13800000000"}, db)   # 非法字段
ValueError: 不允许更新的字段: phone

>>> update_user("NOT_EXIST", {"name": "x"}, db)         # 用户不存在
KeyError: '用户 NOT_EXIST 不存在'
```

#### 边界情况

- `updates` 为空字典 `{}` 时不报错，但会照常追加 `updated_at` 时间戳。
- 字段名校验发生在存在性校验**之后**：若用户不存在且 `updates` 含非法字段，先抛 `KeyError`。
- `updates` 中的值不做类型或枚举校验（如 `status` 可被改为任意字符串）。

---

### `delete_user(user_id: str, user_db: Dict[str, Dict]) -> bool`

软删除用户，即将用户状态置为 `"deleted"`，并记录删除时间。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | `str` | 是 | 要删除的用户 ID。 |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典。 |

#### 返回值

返回 `bool`：删除成功（用户存在）返回 `True`；用户不存在返回 `False`。

#### 异常

本函数不抛出异常（用户不存在时返回 `False` 而非抛错）。

#### 使用示例

```python
>>> delete_user("U001", db)
True

>>> delete_user("NOT_EXIST", db)
False
```

#### 边界情况

- 这是**软删除**：用户记录仍保留在 `user_db` 中，仅 `status` 变为 `"deleted"`，并新增 `deleted_at` 字段。
- 对已是 `"deleted"` 状态的用户再次调用，仍返回 `True`（重复删除是幂等成功的）。
- 删除后用户仍会被 `list_users` 的总数统计计入（除非按 `status="active"` 过滤）。

---

### `list_users(user_db: Dict[str, Dict], role: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]`

分页查询用户列表，支持按角色和状态过滤。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典。 |
| `role` | `Optional[str]` | 否 | 按角色过滤（如 `"admin"`），`None` 表示不过滤。 |
| `status` | `Optional[str]` | 否 | 按状态过滤（如 `"active"`），`None` 表示不过滤。 |
| `limit` | `int` | 否 | 每页最大返回数量，默认 `100`，最大 `1000`。 |
| `offset` | `int` | 否 | 分页偏移量（跳过前 N 条），默认 `0`。 |

#### 返回值

返回元组 `(用户列表, 总数量)`：

- 用户列表：按 `user_db` 迭代顺序，过滤后切片 `results[offset:offset+limit]` 得到的 `List[Dict]`；
- 总数量：**过滤后、分页前**的完整条数（`int`），可用于计算总页数。

#### 异常

| 异常 | 触发条件 |
| --- | --- |
| `ValueError` | `limit` 大于 `1000`；或 `offset` 为负数。 |

#### 使用示例

```python
>>> list_users(db, role="admin", limit=10)
([{'id': 'U001', 'role': 'admin', ...}], 1)

>>> list_users(db, status="active", offset=5, limit=20)
([...], 50)
```

#### 边界情况

- `offset` 超过总条数时返回空列表，但 `total` 仍为真实总数（可用于判断是否越界）。
- `limit` 仅校验上限（>1000）与 `offset` 非负；**未校验负数 `limit`**，负数会使切片行为异常（如 `results[0:-5]`），调用方应避免传入。
- 两个过滤条件为**且**关系：同时传入 `role` 与 `status` 时，返回同时满足两者的用户。
- 过滤匹配使用精确相等比较；用户缺少 `role`/`status` 字段时（如手工构造的字典），`u.get("role")` 返回 `None`，与过滤值不相等，因而不会被匹配到。

---

### `validate_user_email(email: str) -> bool`

验证邮箱格式是否合法（简化检查）。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `email` | `str` | 是 | 待验证的邮箱字符串。 |

#### 返回值

返回 `bool`：格式合法返回 `True`，否则返回 `False`。

#### 异常

本函数不抛出异常。

#### 使用示例

```python
>>> validate_user_email("test@example.com")
True

>>> validate_user_email("invalid-email")
False
```

#### 边界情况

- 校验规则为简化检查：必须包含 `@`，且 `@` 之后的域名部分必须包含 `.`。
- `"a@b"`（域名无点）返回 `False`；`"a@b.c"` 返回 `True`。
- 不校验空字符串、长度、域名合法性（如 `"a@.b"`、`"a@b..c"` 会返回 `True`）。
- 生产环境建议使用更严格的正则（如 `email-validator` 库）替代本函数。

---

### `batch_create_users(users_data: List[Dict], user_db: Dict[str, Dict]) -> Tuple[List[Dict], List[str]]`

批量创建用户：逐条调用 `create_user`，单条失败不影响其余条目，返回成功列表与失败原因列表。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `users_data` | `List[Dict]` | 是 | 用户数据列表，每个元素需包含 `user_id`、`name`、`email` 三个键，`role` 可选。 |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典，创建成功的用户会被写入其中。 |

#### 返回值

返回元组 `(成功创建的用户列表, 错误信息列表)`：

- 成功列表：`List[Dict]`，为 `create_user` 返回的完整用户字典；
- 错误列表：`List[str]`，每条格式为 `"第 {索引} 条: {异常信息}"`（索引从 0 开始），无失败时为空列表。

#### 异常

本函数**不对外抛出异常**：任何单条数据的问题（如缺少键、格式非法）都会被捕获并记入错误列表。

#### 使用示例

```python
>>> batch_create_users(
...     [{"user_id": "U001", "name": "张三", "email": "a@b.com"},
...      {"user_id": "U002", "name": "李四", "email": "bad-email"}],
...     db)
([{'id': 'U001', 'name': '张三', ...}], ['第 1 条: email 格式不正确'])
```

#### 边界情况

- 元素缺少 `user_id` / `name` / `email` 键时会触发 `KeyError`，同样被捕获并记入错误列表（如 `"第 0 条: 'email'"`）。
- 错误索引基于原始列表的下标（0 起），便于调用方定位出问题的数据条目。
- 成功写入是**逐条即时生效**的：即使后续条目失败，前面成功的用户已写入 `user_db`，不会整体回滚（非事务性）。
- 已存在的 `user_id` 会直接覆盖原记录（`create_user` 不检查重复）。

---

### `get_user_statistics(user_db: Dict[str, Dict]) -> Dict`

获取用户数据库的统计信息。

#### 参数

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_db` | `Dict[str, Dict]` | 是 | 用户数据库字典。 |

#### 返回值

返回统计字典 `Dict`，包含以下键：

| 键 | 类型 | 说明 |
| --- | --- | --- |
| `total` | `int` | 用户总数（`user_db` 中全部记录数）。 |
| `active` | `int` | 状态为 `"active"` 的用户数。 |
| `deleted` | `int` | 状态为 `"deleted"` 的用户数。 |
| `role_distribution` | `Dict[str, int]` | 各角色人数分布，键为角色名，值为人数。 |

#### 异常

本函数不抛出异常。

#### 使用示例

```python
>>> get_user_statistics(db)
{'total': 10, 'active': 8, 'deleted': 2, 'role_distribution': {'admin': 1, 'member': 9}}
```

#### 边界情况

- 用户缺少 `role` 字段时，会被归入 `"unknown"` 角色统计；缺少 `status` 字段时不计入 `active` 或 `deleted`，但仍计入 `total`。
- 若存在 `"active"` / `"deleted"` 之外的状态值（如 `"suspended"`），该用户只计入 `total`，不落入 `active` 或 `deleted` 计数。
- 对空数据库调用返回 `{'total': 0, 'active': 0, 'deleted': 0, 'role_distribution': {}}`。

---

## 通用约定与边界情况

1. **`user_db` 可变性**：所有写操作（`create_user` 调用方写入、`update_user`、`delete_user`、`batch_create_users`）都会直接修改传入的 `user_db` 字典，不存在副本。
2. **时间戳格式**：`created_at`、`updated_at`、`deleted_at` 均为 `datetime.now().isoformat()` 生成的 ISO 8601 字符串。
3. **校验范围**：模块整体采用"文档契约"与"实际校验"分离的设计——docstring 中声明了更严格约束（如 `user_id` 字符集、`name` 长度、`role` 枚举），但实际代码仅校验关键项（长度、`@`、字段白名单、分页边界）。依赖严格校验的生产场景应在此基础上补充校验逻辑。
4. **异常 vs 返回值约定**：

   | 场景 | 行为 |
   | --- | --- |
   | 查询不存在的用户（`get_user`） | 返回 `None` |
   | 更新不存在的用户（`update_user`） | 抛出 `KeyError` |
   | 删除不存在的用户（`delete_user`） | 返回 `False` |
   | 批量创建中单条失败 | 记入错误列表，不抛异常 |
5. **线程安全**：模块非线程安全，并发读写同一 `user_db` 需由调用方自行加锁。
6. **依赖**：仅使用标准库（`typing`、`datetime`），无第三方依赖，兼容 Python 3.8+。

---

*本文档由 `user_module.py` 源码自动分析生成，所有示例输出均为合成演示数据。*
