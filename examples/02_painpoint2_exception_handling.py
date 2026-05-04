#!/usr/bin/env python3
from nonone import catch, try_catch, Ok, Err

"""
痛点 2：异常处理冗长且容易遗漏
"""

# ❌ 传统写法 - 异常处理复杂且容易遗漏
def parse_and_calculate(input_str: str) -> float:
    try:
        num = float(input_str)
        if num <= 0:
            raise ValueError("数字必须大于0")
        return 100 / num
    except ValueError as e:
        # 需要手动处理每种异常类型
        print(f"解析失败: {e}")
        raise  # 或者返回默认值，但会丢失异常信息

def another_operation(data: str) -> float:
    try:
        # 一些复杂操作
        return float(data) * 2
    except ValueError as e:
        print(f"操作失败: {e}")
        raise

# 调用方需要嵌套 try-catch，代码冗长
try:
    result1 = parse_and_calculate("abc")
    result2 = another_operation("xyz")
    print(f"结果1: {result1}, 结果2: {result2}")
except ValueError as e:
    print(f"值错误: {e}")
except ZeroDivisionError as e:
    print(f"除零错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")

# 问题：
# 1. 异常处理代码冗长，需要多层嵌套
# 2. 容易遗漏某些异常类型
# 3. 错误处理逻辑分散，难以统一管理



# ✅ NoNone 写法 - 统一错误处理

# 方式 A: 使用装饰器 - 一键转换现有函数
@catch
def dangerous_divide(a: float, b: float) -> float:
    return a / b  # 可能抛出 ZeroDivisionError

result = dangerous_divide(10, 0)
# 自动包装为: Err(ZeroDivisionError(...))

# 方式 B: 临时调用 - 无需修改原函数定义
def parse_and_calculate_unsafe(input_str: str) -> float:
    num = float(input_str)
    if num <= 0:
        raise ValueError("数字必须大于0")
    return 100 / num

# 直接包装调用，立即获得 Result
result = try_catch(parse_and_calculate_unsafe, "abc")

match result:
    case Ok(value):
        print(f"计算成功: {value}")
    case Err(e):
        print(f"处理失败: {type(e).__name__}: {e}")
# ✅ 所有异常都被统一捕获并转换为 Err，不会遗漏
