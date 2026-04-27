# examples/02_data_pipeline.py

from nonone import ok, err, Result

def parse_int(val: str) -> Result[int, str]:
    """尝试将字符串转换为整数。"""
    try:
        return ok(int(val))
    except ValueError:
        return err(f"无法将 '{val}' 转换为整数")

def validate_positive(val: int) -> Result[int, str]:
    """校验整数是否为正数。"""
    if val > 0:
        return ok(val)
    return err(f"数值 {val} 必须大于 0")

def process_input(user_input: str) -> None:
    # Deleted:rprint(f"\n[cyan]处理输入: '{user_input}'[/cyan]")
    print(f"\n处理输入: '{user_input}'")
    
    # 链式调用：解析 -> 校验 -> 翻倍
    # 如果中间任何一步返回 Err，后续流程自动短路
    result = (
        parse_int(user_input)
        .and_then(validate_positive)
        .map(lambda x: x * 2)
    )
    
    if result.is_ok():
        # Deleted:rprint(f"[green]处理成功，最终结果: {result.unwrap()}[/green]")
        print(f"处理成功，最终结果: {result.unwrap()}")
    else:
        # Deleted:rprint(f"[yellow]流程被中断，原因: {result.unwrap_err()}[/yellow]")
        print(f"流程被中断，原因: {result.unwrap_err()}")

def main() -> None:
    process_input("42")      # 成功分支
    process_input("-5")      # 校验失败分支
    process_input("hello")   # 解析失败分支

if __name__ == "__main__":
    main()