#!/usr/bin/env python3

from nonone import ok, err, Result, Ok, Err

"""
痛点 3：繁琐的嵌套 None 判断
"""

# ❌ 传统写法 - 嵌套地狱
def get_user(user_id: int):
    if user_id == 123:
        return {"name": "张三"}  # 模拟查询数据
    return None

def get_score_record(user):
    if user and user.get("name") == "张三":
        return {"score": 95.5}  # 模拟查询数据
    return None

def extract_score(record):
    if record and record.get("score", 0) > 0:
        return record["score"]  # 模拟提取数据
    return None

def get_user_score_traditional(user_id: int):
    """获取用户分数，需要三层检查"""
    # 第1层: 检查用户是否存在
    user = get_user(user_id)
    if user is None:
        return None
    
    # 第2层: 检查用户是否有分数记录
    score_record = get_score_record(user)
    if score_record is None:
        return None
    
    # 第3层: 检查分数是否有效
    score = extract_score(score_record)
    if score is None:
        return None
    
    return score

# 使用时的嵌套判断
score = get_user_score_traditional(123)
if score is not None:
    print(f"用户分数: {score}")
else:
    print("无法获取用户分数")



# ✅ NoNone 写法 - 扁平化链式调用
def get_user_safe(user_id: int) -> Result[dict, str]:
    if user_id == 123:
        return ok({"name": "张三"})
    return err("用户不存在")

def get_score_record_safe(user: dict) -> Result[dict, str]:
    if user.get("name") == "张三":
        return ok({"score": 95.5})
    return err("没有分数记录")

def extract_score_safe(record: dict) -> Result[float, str]:
    score = record.get("score", 0)
    if score > 0:
        return ok(score)
    return err("分数无效")

def get_user_score_nonone(user_id: int) -> Result[float, str]:
    """使用链式调用获取用户分数"""
    return (
        get_user_safe(user_id)    # 获取用户
        .and_then(get_score_record_safe)  # 获取分数记录
        .and_then(extract_score_safe)     # 提取分数
    )

# 使用时只需要一次 match
match get_user_score_nonone(123):
    case Ok(score):
        print(f"用户分数: {score}")          # ✅ 输出: 用户分数: 95.5
    case Err(msg):
        print(f"获取失败: {msg}")            # 任何一步出错都会到这里
