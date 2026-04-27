# examples/01_file_io.py

import json
from pathlib import Path
from nonone import catch, Ok, Err

@catch
def read_json_config(path: str | Path) -> dict[str, object]:
    """读取并解析 JSON 配置文件。"""
    file_path = Path(path) if isinstance(path, str) else path
    content = file_path.read_text(encoding="utf-8")
    return json.loads(content)

def main() -> None:
    # Deleted:rprint("[bold cyan]尝试读取不存在的文件：[/bold cyan]")
    print("尝试读取不存在的文件：")
    bad_result = read_json_config("missing.json")
    
    match bad_result:
        case Ok(data):
            # Deleted:rprint(data)
            print(data)
        case Err(e):
            # Deleted:rprint(f"[red]读取失败: {type(e).__name__} - {e}[/red]")
            print(f"读取失败: {type(e).__name__} - {e}")
            
    # 使用 unwrap_or 提供默认回退值
    safe_config = bad_result.unwrap_or({"theme": "dark", "version": 1.0})
    # Deleted:rprint("\n[bold green]最终使用的配置：[/bold green]")
    print("\n最终使用的配置：")
    # Deleted:rprint(safe_config)
    print(safe_config)

if __name__ == "__main__":
    main()