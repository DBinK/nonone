# examples/03_logging_and_expect.py

from nonone import try_catch, Result

def fetch_data_from_db(query_id: int) -> dict[str, object]:
    """模拟一个可能抛出异常的数据库查询。"""
    if query_id < 0:
        raise ConnectionError("数据库连接已断开")
    return {"id": query_id, "data": "dummy payload"}

def main() -> None:
    query_id = -1
    print(f"开始执行数据库查询, ID: {query_id}")
    
    # 使用 try_catch 快速包装普通函数调用
    result: Result[dict[str, object], Exception] = try_catch(fetch_data_from_db, query_id)
    
    if result.is_err():
        # 记录真实错误栈，然后用 map_err 转换错误类型或直接抛出
        err_obj = result.unwrap_err()
        print(f"底层服务异常: {err_obj}")
        
        # 使用 expect 进行强硬的断言，这会抛出 UnwrapError 终止程序
        result.expect("启动时必须成功加载基础数据")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序已崩溃 {e}")
        import traceback
        traceback.print_exc()