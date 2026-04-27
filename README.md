# nonone

> 拒绝隐式 `None`，拥抱现代 Python 的 Rust 风格 `Result` 类型。

**nonone** 是一个轻量、纯粹且类型安全的 Python 库。它引入了 Rust 语言中著名的 `Result`（`Ok` / `Err`）模式，并专为 **Python 3.10+** 的 `match-case`（结构化模式匹配）语法量身定制。

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