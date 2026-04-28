# nonone

> 拒绝隐式 `None`，拥抱现代 Python 的 Rust 风格 `Result` 类型。

**nonone** 是一个轻量、纯粹且类型安全的 Python 库。它引入了 Rust 语言中著名的 `Result`（`Ok` / `Err`）模式，并专为 **Python 3.10+** 的 `match-case`（结构化模式匹配）语法量身定制。

---

### 为什么选择 nonone？告别 None 和嵌套判断的痛苦

在传统的 Python 开发中，我们经常面临以下痛点：

#### 痛点 1：隐式 `None` 导致的运行时错误

**❌ 传统写法 - 危险！**
```python
def find_user(user_id: int) -> User | None:
    # ... 数据库查询逻辑
    return None if not found else user

user = find_user(123)
print(user.name)  # 💥 如果 user 是 None，这里会抛出 AttributeError！
```

**✅ nonone 写法 - 类型安全**
```python
from nonone import Result, ok, err

def find_user_safe(user_id: int) -> Result[User, str]:
    # 必须返回 ok(user) 或 err("错误信息")
    pass

result = find_user_safe(123)
# 编译器和 IDE 会强制你处理两种情况，无法忽略错误
match result:
    case Ok(user):
        print(user.name)  # ✅ 安全，user 一定存在
    case Err(msg):
        print(f"错误: {msg}")
```

---

#### 痛点 2：繁琐的嵌套 None 判断

**❌ 传统写法 - 嵌套地狱**
```python
user = find_user(123)
if user is not None:
    profile = get_profile(user.id)
    if profile is not None:
        address = get_address(profile.address_id)
        if address is not None:
            print(f"用户地址: {address.street}")
        else:
            print("地址不存在")
    else:
        print("用户资料不存在")
else:
    print("用户不存在")
```

**✅ nonone 写法 - 扁平化链式调用**
```python
from nonone import ok, err, Result

# 定义安全的函数
def find_user_safe(user_id: int) -> Result[User, str]:
    pass

def get_profile_safe(user_id: int) -> Result[Profile, str]:
    pass

def get_address_safe(address_id: int) -> Result[Address, str]:
    pass

# 使用链式调用，完全避免嵌套
result = (
    find_user_safe(123)                    # 第1步: 查找用户 → Result[User, str]
    .and_then(get_profile_safe)            # 第2步: 获取资料 → Result[Profile, str]
    .and_then(get_address_safe)            # 第3步: 获取地址 → Result[Address, str]
    .map(lambda address: f"用户地址: {address.street}")  # 第4步: 格式化输出 → Result[str, str]
)

match result:
    case Ok(message):
        print(message)                     # 如果所有步骤都成功，打印格式化后的消息
    case Err(msg):
        print(f"处理失败: {msg}")          # 任何一步出错都会到这里
```

💡 **理解链式调用中的关键方法**：

- **`.and_then(func)`** - 当前一步成功时，执行下一个返回 `Result` 的操作
  - 如果前一步是 `Err`，则跳过后续所有步骤
  - 用于串联多个可能失败的操作

- **`.map(func)`** - 对成功的值进行转换（不改变 Result 结构）
  - 只在 `Ok` 时执行，将 `Ok(value)` 转换为 `Ok(func(value))`
  - 用于最后的格式化、计算等纯函数操作

**对比理解**：
```python
# 假设 get_address_safe 返回 Ok(Address(street="长安街"))

# 使用 .map() 转换结果
result = get_address_safe(123).map(lambda addr: addr.street)
# 结果: Ok("长安街")  ← 仍然是 Ok，但内部值从 Address 变成了 str

# 如果不使用 .map()
result = get_address_safe(123)
# 结果: Ok(Address(street="长安街"))  ← 内部还是 Address 对象
```



---

#### 痛点 3：异常处理的复杂性与遗漏风险

**❌ 传统写法 - try-except 容易遗漏**
```python
try:
    user = find_user(123)
    profile = get_profile(user.id)  # 如果 user 是 None，这里也会出错！
    address = get_address(profile.address_id)
    print(f"用户地址: {address.street}")
except (AttributeError, ValueError, DatabaseError) as e:
    print(f"处理失败: {e}")
# ⚠️ 问题：可能忘记捕获某些异常，或者异常类型不匹配
```

**✅ nonone 写法 - 统一错误处理**
```python
from nonone import catch, try_catch

# 方式 A: 使用装饰器 - 一键转换现有函数
@catch
def dangerous_divide(a: float, b: float) -> float:
    return a / b  # 可能抛出 ZeroDivisionError

result = dangerous_divide(10, 0)
# 自动包装为: Err(ZeroDivisionError(...))

# 方式 B: 临时调用 - 无需修改原函数定义
import requests

def fetch_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 直接包装调用，立即获得 Result
result = try_catch(fetch_data, "https://api.example.com/data")

match result:
    case Ok(data):
        print(f"获取成功: {data}")
    case Err(e):
        print(f"请求失败: {type(e).__name__}: {e}")
# ✅ 所有异常都被统一捕获并转换为 Err，不会遗漏
```

---

### nonone 的核心优势

- ✅ **编译时类型安全**：静态类型检查器能提前发现潜在错误
- ✅ **强制错误处理**：无法忽略错误情况，必须显式处理
- ✅ **消除 None 隐患**：再也不用担心 `AttributeError: 'NoneType' object has no attribute...`
- ✅ **扁平化代码结构**：通过链式调用将多层嵌套变为线性流程
- ✅ **统一的错误模型**：所有错误都是 `Err`，无需记忆各种异常类型
- ✅ **无缝迁移**：使用 `@catch` 或 `try_catch` 零成本改造现有代码

---

### 核心特性

* **现代语法**：完美支持 Python 3.10+ 的 `match-case` 结构化模式匹配。
* **类型安全**：基于双泛型 `Result[T, E]` 设计，为静态类型检查工具提供极佳的推导支持。
* **极简无包袱**：零第三方依赖，基于 `slots=True` 的数据类构建，极致轻量且高效。
* **优雅链式调用**：提供 `.map()`、`.and_then()` 等函数式操作。
* **无缝接入**：内置 `@catch` 装饰器，一键将传统抛出异常的函数转换为安全函数。

---

### 安装

使用 `uv`（推荐）或 `pip`：

```bash
uv pip install nonone
# 或者
pip install nonone
```

---

### 快速上手

#### 1. 构造结果 (Manual Construction)

你可以手动返回 `ok` 或 `err` 实例。推荐使用小写函数构造器，它们在类型推导上表现更佳：

```python
from nonone import ok, err, Result

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return err("除数不能为零")
    return ok(a / b)
```

#### 2. 使用 match-case 处理结果 (Pattern Matching)

这是处理 `Result` 最优雅、最安全的方式。

```python
from nonone import Ok, Err

result = divide(10, 2)

match result:
    case Ok(value):
        print(f"计算成功: {value}")
    case Err(msg):
        print(f"计算失败: {msg}")
```

---

### 进阶用例：强大的 match-case

由于 `nonone` 基于 `dataclass` 构建，你可以利用 Python 模式匹配的强大特性进行深度解构和过滤。

#### 嵌套对象解构
如果 `Ok` 里面包裹的是字典、列表或另一个 `dataclass`，你可以直接在 `case` 中一步到位拆解它：

```python
from dataclasses import dataclass
from nonone import ok, Ok, Err

@dataclass
class User:
    id: int
    name: str

def get_user() -> Result[User, str]:
    return ok(User(id=1, name="Alice"))

match get_user():
    # 直接解构内部的 User 对象属性
    case Ok(User(id=1, name=name)):
        print(f"管理员已登录: {name}")
    case Ok(User(name=name)):
        print(f"普通用户已登录: {name}")
    case Err(error):
        print(f"登录失败: {error}")
```

#### 使用 Guard (条件过滤)
你可以在匹配时加入 `if` 判断：

```python
res = divide(100, 2)

match res:
    case Ok(val) if val > 10:
        print(f"得到一个较大的正数: {val}")
    case Ok(val):
        print(f"得到一个较小的数: {val}")
```

---

### 函数式链式处理 (Fluent API)

利用 `and_then` 和 `map`，你可以像在 Rust 中一样平铺业务逻辑，避免嵌套的 `if` 判断。

```python
# 模拟：获取输入 -> 转整数 -> 验证 -> 格式化输出
res = (
    ok(" 42 ")
    .map(str.strip)
    .and_then(lambda s: ok(int(s)) if s.isdigit() else err("非法数字"))
    .map(lambda n: n * 2)
)

print(res)  # Ok(84)
```

---


### 工具类：自动捕获异常

使用 `@catch` 装饰器或 `try_catch` 函数，可以轻松将现有的 Python 代码转换为 Result 风格。

#### 装饰器写法
```python
from nonone import catch

@catch
def dangerous_operation(x: int):
    return 10 / x

# 结果将是 Err(ZeroDivisionError(...))
res = dangerous_operation(0)
```

#### 函数式立即执行
如果你不想修改原函数定义，或者只需要临时调用一次，可以使用 `try_catch`：

```python
from nonone import try_catch

# 立即执行函数并捕获可能抛出的异常
res = try_catch(lambda x, y: x + y, 1, "2")

match res:
    case Err(e):
        print(f"执行出错: {e}")  # TypeError: unsupported operand type(s)...
```

---

### 核心 API 概览

| 方法 / 函数 | 描述 |
| :--- | :--- |
| `ok(value)` / `err(error)` | **(推荐)** 快速构造 Ok/Err 实例。 |
| `is_ok()` / `is_err()` | 检查当前状态。 |
| `unwrap()` | 提取值，若为 Err 则抛出 `UnwrapError`。 |
| `unwrap_or(default)` | 提取值，若为 Err 则返回默认值。 |
| `expect(msg)` | 提取值，并在失败时附加自定义错误信息。 |
| `map(f)` / `map_err(f)` | 对成功/错误分支的值进行转换。 |
| `and_then(f)` | 成功时执行下一个返回 Result 的操作 (FlatMap)。 |
| `or_else(f)` | 失败时尝试通过后备函数恢复。 |

---

### 许可协议

本项目基于 MIT License 开源。