#!/usr/bin/env python3

from nonone import Result, ok, err, Ok, Err

"""
痛点 1：错误处理的缺失与运行时崩溃
"""

# ❌ 传统写法 - 无显式错误处理
def divide(a: float, b: float) -> float:
    return a / b
    # ✅ 极简，零开销
    # ❌ 除零时程序崩溃
    # 🎯 适用：确信 b!=0、快速原型、脚本

result = divide(10, 0)  # 💥 程序直接崩溃, 抛出 ZeroDivisionError
print(f"结果: {result}")

# ❌ 传统写法 - 出错提前返回 None
def divide_with_none(a: float, b: float) -> float | None:
    if b == 0:
        return None
    return a / b

result = divide_with_none(10, 0)
print(result * 2)  # 💥 如果 result 是 None，这里会抛出 TypeError！


# ✅ NoNone 写法 - 类型安全
def divide_safe(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return err("除数不能为零")
    return ok(a / b)

result = divide_safe(10, 0)

# Python 解释器和 IDE 会强制你处理两种情况，无法忽略错误
match result:
    case Ok(value):
        print(f"结果: {value * 2}")  # ✅ 安全，value 一定存在
    case Err(msg):
        print(f"错误: {msg}")
