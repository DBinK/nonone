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
from nonone import Result, ok, err, Ok, Err

def find_user_safe(user_id: int) -> Result[dict, str]:
    # 模拟数据库查询
    users = {123: {"id": 123, "name": "Alice"}}
    if user_id in users:
        return ok(users[user_id])
    return err("用户不存在")

result = find_user_safe(123)
# 编译器和 IDE 会强制你处理两种情况，无法忽略错误
match result:
    case Ok(user):
        print(user["name"])  # ✅ 安全，user 一定存在
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

# 定义安全的函数（完整实现见下方"完整示例"）
def find_user_safe(user_id: int) -> Result[dict, str]:
    users = {123: {"id": 123, "name": "Alice"}}
    return ok(users[user_id]) if user_id in users else err("用户不存在")

def get_profile_safe(user: dict) -> Result[dict, str]:
    profiles = {123: {"user_id": 123, "address_id": 456}}
    return ok(profiles[user["id"]]) if user["id"] in profiles else err("资料不存在")

def get_address_safe(profile: dict) -> Result[dict, str]:
    addresses = {456: {"profile_id": 456, "street": "长安街"}}
    return ok(addresses[profile["address_id"]]) if profile["address_id"] in addresses else err("地址不存在")

def format_address(address: dict) -> str:
    return f"用户地址: {address['street']}"

# 使用链式调用，完全避免嵌套
result = (
    find_user_safe(123)                    # 第1步: 查找用户
    .and_then(get_profile_safe)            # 第2步: 获取资料
    .and_then(get_address_safe)            # 第3步: 获取地址
    .map(format_address)                   # 第4步: 格式化输出
)

match result:
    case Ok(message):
        print(message)                     # ✅ 输出: 用户地址: 长安街
    case Err(msg):
        print(f"处理失败: {msg}")          # 任何一步出错都会到这里
```

💡 **核心思想**：`.and_then()` 用于串联可能失败的操作，`.map()` 用于转换成功的值。详细用法见下方"API 使用指南"。

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

- ✅ **编译时类型安全**：基于双泛型 `Result[T, E]` 设计，静态类型检查器能提前发现潜在错误
- ✅ **强制错误处理**：无法忽略错误情况，必须显式处理所有分支
- ✅ **消除 None 隐患**：再也不用担心 `AttributeError: 'NoneType' object has no attribute...`
- ✅ **扁平化代码结构**：通过 `.map()`、`.and_then()` 等链式调用将多层嵌套变为线性流程
- ✅ **统一的错误模型**：所有错误都是 `Err`，无需记忆各种异常类型
- ✅ **无缝迁移**：使用 `@catch` 或 `try_catch` 零成本改造现有代码
- ✅ **现代语法支持**：专为 Python 3.10+ 的 `match-case` 结构化模式匹配量身定制
- ✅ **极简无包袱**：零第三方依赖，基于 `slots=True` 的数据类构建，极致轻量且高效

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

#### 💡 重要提示：大写 vs 小写

nonone 提供了两套 API，用途不同但很简单：

| 场景 | 使用 | 示例 |
|------|------|------|
| **构造实例** | 小写 `ok()` / `err()` | `return ok(42)` |
| **模式匹配** | 大写 `Ok` / `Err` | `case Ok(value):` |
| **类型注解** | 大写 `Result` | `-> Result[int, str]` |

**简单记忆**：🏗️ **建造时用小写的**（函数），🔍 **检查时用大的**（类）

---

### 完整示例：从安装到运行

让我们通过一个完整的例子来体验 nonone：

```python
# example.py - 完整的用户地址查询示例
from nonone import ok, err, Result, Ok, Err

# 1. 定义数据模型（简化版，实际项目中使用 dataclass）
User = dict
Profile = dict
Address = dict

# 2. 定义安全的业务函数
def find_user(user_id: int) -> Result[User, str]:
    """查找用户"""
    users = {123: {"id": 123, "name": "Alice"}}
    return ok(users[user_id]) if user_id in users else err("用户不存在")

def get_profile(user: User) -> Result[Profile, str]:
    """获取用户资料"""
    profiles = {123: {"user_id": 123, "address_id": 456}}
    return ok(profiles[user["id"]]) if user["id"] in profiles else err("资料不存在")

def get_address(profile: Profile) -> Result[Address, str]:
    """获取地址信息"""
    addresses = {456: {"profile_id": 456, "street": "长安街"}}
    return ok(addresses[profile["address_id"]]) if profile["address_id"] in addresses else err("地址不存在")

# 3. 使用链式调用组合业务逻辑
def get_user_address(user_id: int) -> Result[str, str]:
    return (
        find_user(user_id)
        .and_then(get_profile)
        .and_then(get_address)
        .map(lambda addr: f"用户 {user_id} 的地址是: {addr['street']}")
    )

# 4. 处理结果
if __name__ == "__main__":
    result = get_user_address(123)
    
    match result:
        case Ok(message):
            print(f"✅ {message}")
        case Err(error):
            print(f"❌ {error}")
```

运行结果：
```bash
$ python example.py
✅ 用户 123 的地址是: 长安街
```

---

### 进阶用法：强大的 match-case

`nonone` 基于 `dataclass` 构建，可以充分利用 Python 模式匹配的强大功能。

#### 🎯 使用 Guard（条件过滤）

在 `case` 中添加 `if` 条件，实现更精细的控制：

```python
from nonone import ok, Ok, Err

def divide(a: float, b: float):
    if b == 0:
        return err("除数不能为零")
    return ok(a / b)

result = divide(100, 2)

match result:
    case Ok(val) if val > 10:
        print(f"得到一个较大的数: {val}")     # ✅ 输出: 得到一个较大的数: 50.0
    case Ok(val):
        print(f"得到一个较小的数: {val}")
    case Err(msg):
        print(f"计算失败: {msg}")
```

#### 📦 嵌套对象解构

如果 `Ok` 里面包裹的是 `dataclass`，可以直接在 `case` 中解构其属性：

```python
from dataclasses import dataclass
from nonone import ok, Ok, Err

@dataclass
class User:
    id: int
    name: str
    role: str

def get_user() -> Result[User, str]:
    return ok(User(id=1, name="Alice", role="admin"))

match get_user():
    # 直接解构内部对象的特定属性
    case Ok(User(role="admin", name=name)):
        print(f"管理员登录: {name}")           # ✅ 输出: 管理员登录: Alice
    case Ok(User(name=name)):
        print(f"普通用户登录: {name}")
    case Err(error):
        print(f"登录失败: {error}")
```

这种深度解构让你可以在一行代码中完成**类型检查 + 属性提取 + 条件判断**，非常优雅！

---

### API 使用指南

根据你的需求选择合适的 API：

#### 🏗️ 构造 Result
```python
from nonone import ok, err

ok(42)           # 成功结果
err("出错了")     # 失败结果
```

#### 🔍 检查结果状态
```python
result.is_ok()   # True/False
result.is_err()  # True/False
```

#### 📦 提取值（谨慎使用）
```python
result.unwrap()          # 成功返回值，失败抛出 UnwrapError
result.unwrap_or(0)      # 成功返回值，失败返回默认值 0
result.expect("错误提示") # 成功返回值，失败抛出带自定义消息的异常
```

#### ⛓️ 链式操作（推荐）
```python
# map: 转换成功的值
ok(5).map(lambda x: x * 2)        # Ok(10)

# and_then: 串联多个可能失败的操作
ok(5).and_then(lambda x: ok(x * 2))  # Ok(10)

# or_else: 失败时尝试恢复
err("错").or_else(lambda e: ok(0))   # Ok(0)
```

#### 🎯 模式匹配（最安全）
```python
from nonone import Ok, Err

match result:
    case Ok(value):
        print(f"成功: {value}")
    case Err(error):
        print(f"失败: {error}")
```

#### 🛡️ 捕获异常
```python
from nonone import catch, try_catch

# 装饰器方式
@catch
def risky_func():
    return 1 / 0

# 函数方式
result = try_catch(risky_func)
```

---

### 许可协议

本项目基于 MIT License 开源。