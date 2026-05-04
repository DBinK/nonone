from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable, Generic, NoReturn, ParamSpec, TypeAlias, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")
P = ParamSpec("P")  # 用于保留装饰器参数签名


class UnwrapError(RuntimeError):
    """统一抛出的解包异常。"""


# -------------------- 成功分支 --------------------
@dataclass(frozen=True, slots=True)
class Ok(Generic[T, E]):
    value: T

    # --- 检查结果状态 ---
    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    # --- 提取值（谨慎使用） ---
    def unwrap(self) -> T:
        """提取成功值。"""
        return self.value

    def unwrap_err(self) -> NoReturn:
        """提取错误值，如果是 Ok 则抛出异常。"""
        raise UnwrapError(f"Called unwrap_err() on an Ok: {self.value!r}")

    def unwrap_or(self, default: T) -> T:
        """返回成功值，忽略默认值。"""
        return self.value

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """返回成功值，忽略错误处理函数。"""
        return self.value

    def expect(self, msg: str) -> T:
        """返回成功值，忽略自定义消息。"""
        return self.value

    # --- 链式操作 ---
    def map(self, f: Callable[[T], U]) -> Ok[U, E]:
        """变换成功值：Ok(v) → Ok(f(v))，用于纯函数转换。"""
        return Ok(f(self.value))

    def map_err(self, f: Callable[[E], F]) -> Ok[T, F]:
        """Ok 无操作：直接传递成功值，不调用错误变换函数。"""
        return Ok(self.value)

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """链式调用：用成功值调用返回 Result 的函数，用于串联操作。"""
        return f(self.value)
    
    def try_and_then(self, f: Callable[[T], U]) -> Result[U, Exception]:
        """安全链式：捕获函数异常并转为 Result，用于包装普通函数。"""
        return try_catch(f, self.value)  # 用于处理不是返回 Result 的函数
    
    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Ok 无操作：直接传递成功值，不调用错误恢复函数。"""
        return Ok(self.value)
        
    def inspect(self, func: Callable[[T], Any]) -> Ok[T, E]:
        """副作用执行：对值执行副作用（如打印）后返回自身，用于调试。"""
        func(self.value)
        return self
    


# -------------------- 失败分支 --------------------
@dataclass(frozen=True, slots=True)
class Err(Generic[T, E]):
    error: E

    # --- 检查结果状态 ---
    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    # --- 提取值（谨慎使用） ---
    def unwrap(self) -> T:
        """提取成功值，如果是 Err 则抛出异常。"""
        raise UnwrapError(f"Called unwrap() on an Err: {self.error!r}")

    def unwrap_err(self) -> E:
        """提取错误值。"""
        return self.error

    def unwrap_or(self, default: T) -> T:
        """返回成功值或默认值。"""
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """返回成功值或用错误值调用函数的结果。"""
        return op(self.error)

    def expect(self, msg: str) -> NoReturn:
        """提取成功值，如果是 Err 则抛出自定义消息异常。"""
        raise UnwrapError(f"{msg}: {self.error!r}")

    # --- 链式操作 ---
    def map(self, f: Callable[[T], U]) -> Err[U, E]:
        """Err 无操作：直接传递错误，不调用变换函数。"""
        return Err(self.error)

    def map_err(self, f: Callable[[E], F]) -> Err[T, F]:
        """变换错误值：Err(e) → Err(f(e))，用于错误类型转换。"""
        return Err(f(self.error))

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Err 无操作：直接传递错误，不调用链式函数。"""
        return Err(self.error)
    
    def try_and_then(self, f: Callable[[T], U]) -> Result[U, Exception | E]:
        """Err 无操作：直接传递错误，不调用安全链式函数。"""
        return Err(self.error)
        # return cast(Any, self)  # 强制将当前实例视为目标返回类型

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """错误恢复：用错误值调用函数尝试恢复，用于错误处理。"""
        return f(self.error)
    
    def inspect(self, func: Callable[[E], Any]) -> Err[T, E]:
        """错误副作用：对错误执行副作用（如打印）后返回自身，用于调试。"""
        func(self.error)
        return self


# -------------------- 联合类型别名 --------------------
Result: TypeAlias = Ok[T, E] | Err[T, E]


# -------------------- 辅助构造器 --------------------
def ok(value: T) -> Ok[T, Any]:
    """小写构造器，返回 Ok[T, Any]（错误类型留作 Any）。"""
    return Ok(value)


def err(error: E) -> Err[Any, E]:
    """小写构造器，返回 Err[Any, E]（成功类型留作 Any）。"""
    return Err(error)


# -------------------- 装饰器：将普通函数变为返回 Result 的函数 --------------------
def catch(func: Callable[P, T]) -> Callable[P, Result[T, Exception]]:
    """
    装饰器。自动捕获异常并返回 Result。
    利用 ParamSpec 完美保留了原函数的参数类型提示。
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)
    return wrapper


# -------------------- 函数式调用：立即执行函数并返回 Result --------------------
def try_catch(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
    """手动调用：立即执行函数并返回 Result。"""
    try:
        return Ok(func(*args, **kwargs))
    except Exception as e:
        return Err(e)