# quick_start.py
from nonone import ok, err, Result, Ok, Err

# 1. 基本构造
result = ok(42)           # Ok(42)
error = err("出错了")     # Err("出错了")

# 2. 链式调用
def parse_number(s: str) -> Result[float, str]:
    try:
        return ok(float(s))
    except ValueError:
        return err(f"'{s}' 不是有效数字")

def validate_positive(num: float) -> Result[float, str]:
    if num <= 0:
        return err("数字必须大于0")
    return ok(num)

def calculate(num: float) -> Result[float, str]:
    return ok(num * 2)

# 组合多个操作
def process_input(input_str: str) -> Result[float, str]:
    return (
        parse_number(input_str)      # 解析字符串
        .and_then(validate_positive) # 验证正数
        .and_then(calculate)         # 计算
    )

# 3. 模式匹配处理结果
result = process_input("10")
match result:
    case Ok(value):
        print(f"✅ 结果: {value}")
    case Err(error):
        print(f"❌ 错误: {error}")
