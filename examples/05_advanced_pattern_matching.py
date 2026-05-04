

from dataclasses import dataclass
from nonone import ok, err, Ok, Err, Result

# === 基础模式匹配 ===
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

# === 高级模式匹配 - 解构内部对象 ===
@dataclass
class CalculationResult:
    value: float
    operation: str
    success: bool

def divide_with_info(a: float, b: float) -> Result[CalculationResult, str]:
    if b == 0:
        return err("除数不能为零")
    return ok(CalculationResult(
        value=a / b,
        operation="division",
        success=True
    ))

match divide_with_info(10, 2):
    # 直接解构内部对象的特定属性
    case Ok(CalculationResult(operation="division", value=result_value)):
        print(f"结果: {result_value}")           # ✅ 输出: 除法结果: 5.0
    case Ok(CalculationResult(value=result_value)):
        print(f"其他运算结果: {result_value}")
    case Err(error):
        print(f"计算失败: {error}")
