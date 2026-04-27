"""
单元测试：result.py
运行方式：pytest test_result.py -v
"""
import pytest
from nonone import (
    Ok, Err, Result,
    ok, err,
    catch, try_catch,
    UnwrapError
)


# =============================================================================
# Ok 分支测试
# =============================================================================

class TestOk:
    @pytest.fixture
    def ok_val(self):
        return Ok[int, str](42)

    def test_is_ok(self, ok_val):
        assert ok_val.is_ok() is True

    def test_is_err(self, ok_val):
        assert ok_val.is_err() is False

    def test_unwrap(self, ok_val):
        assert ok_val.unwrap() == 42

    def test_unwrap_err_raises(self, ok_val):
        with pytest.raises(UnwrapError, match="Called unwrap_err\\(\\) on an Ok"):
            ok_val.unwrap_err()

    def test_unwrap_or(self, ok_val):
        assert ok_val.unwrap_or(0) == 42

    def test_unwrap_or_else(self, ok_val):
        called = False
        def f(e):
            nonlocal called
            called = True
            return 0
        assert ok_val.unwrap_or_else(f) == 42
        assert called is False   # 不应被调用

    def test_expect(self, ok_val):
        assert ok_val.expect("should not fail") == 42

    def test_map(self, ok_val):
        res = ok_val.map(lambda x: x * 2)
        assert isinstance(res, Ok)
        assert res.unwrap() == 84

    def test_map_err_does_nothing(self, ok_val):
        # map_err on Ok 应该返回 Ok，且错误处理函数不会被调用
        called = False
        def f(e):
            nonlocal called
            called = True
            return "new error"
        res = ok_val.map_err(f)
        assert called is False
        assert isinstance(res, Ok)
        assert res.unwrap() == 42

    def test_and_then_ok(self, ok_val):
        res = ok_val.and_then(lambda x: Ok[str, str]("success"))
        assert isinstance(res, Ok)
        assert res.unwrap() == "success"

    def test_and_then_err(self, ok_val):
        res = ok_val.and_then(lambda x: Err[str, str]("failed"))
        assert isinstance(res, Err)
        assert res.unwrap_err() == "failed"

    def test_or_else_on_ok(self, ok_val):
        # Ok 上的 or_else 应忽略函数，返回自身
        called = False
        def f(e):
            nonlocal called
            called = True
            return Err[int, str]("recovered")
        res = ok_val.or_else(f)
        assert called is False
        assert isinstance(res, Ok)
        assert res.unwrap() == 42

    def test_repr(self, ok_val):
        assert repr(ok_val) == "Ok(value=42)"

    def test_dataclass_immutable(self, ok_val):
        with pytest.raises(Exception):
            ok_val.value = 99

    def test_match_pattern(self, ok_val):
        # 验证 __match_args__ 生效（只测试匹配行为，不依赖 Python 版本）
        match ok_val:
            case Ok(value):
                assert value == 42
            case _:
                pytest.fail("Should have matched Ok")


# =============================================================================
# Err 分支测试
# =============================================================================

class TestErr:
    @pytest.fixture
    def err_val(self):
        return Err[int, str]("something went wrong")

    def test_is_ok(self, err_val):
        assert err_val.is_ok() is False

    def test_is_err(self, err_val):
        assert err_val.is_err() is True

    def test_unwrap_raises(self, err_val):
        with pytest.raises(UnwrapError, match="Called unwrap\\(\\) on an Err"):
            err_val.unwrap()

    def test_unwrap_err(self, err_val):
        assert err_val.unwrap_err() == "something went wrong"

    def test_unwrap_or(self, err_val):
        assert err_val.unwrap_or(100) == 100

    def test_unwrap_or_else(self, err_val):
        def f(e):
            return f"handled: {e}"
        assert err_val.unwrap_or_else(f) == "handled: something went wrong"

    def test_expect_raises(self, err_val):
        with pytest.raises(UnwrapError, match=r"boom: 'something went wrong'"):
            err_val.expect("boom")


    def test_map(self, err_val):
        res = err_val.map(lambda x: x + 1)
        assert isinstance(res, Err)
        assert res.unwrap_err() == "something went wrong"

    def test_map_err(self, err_val):
        res = err_val.map_err(lambda e: e.upper())
        assert isinstance(res, Err)
        assert res.unwrap_err() == "SOMETHING WENT WRONG"

    def test_and_then_short_circuits(self, err_val):
        called = False
        def f(x):
            nonlocal called
            called = True
            return Ok("should not happen")
        res = err_val.and_then(f)
        assert called is False
        assert isinstance(res, Err)
        assert res.unwrap_err() == "something went wrong"

    def test_or_else_recovery(self, err_val):
        res = err_val.or_else(lambda e: Ok[str, str](f"recovered from {e}"))
        assert isinstance(res, Ok)
        assert res.unwrap() == "recovered from something went wrong"

    def test_repr(self, err_val):
        assert repr(err_val) == "Err(error='something went wrong')"

    def test_dataclass_immutable(self, err_val):
        with pytest.raises(Exception):
            err_val.error = "new"

    def test_match_pattern(self, err_val):
        match err_val:
            case Err(error):
                assert error == "something went wrong"
            case _:
                pytest.fail("Should have matched Err")


# =============================================================================
# 小写构造器测试
# =============================================================================

class TestConstructors:
    def test_ok_constructor(self):
        res = ok(3.14)
        assert isinstance(res, Ok)
        assert res.unwrap() == 3.14

    def test_err_constructor(self):
        res = err("failure")
        assert isinstance(res, Err)
        assert res.unwrap_err() == "failure"

    def test_ok_constructor_with_complex_type(self):
        # 清单类型推导
        res = ok([1, 2, 3])
        assert res.unwrap() == [1, 2, 3]

    def test_err_constructor_with_exception(self):
        ex = ValueError("bad value")
        res = err(ex)
        assert res.unwrap_err() is ex


# =============================================================================
# 装饰器 catch 测试
# =============================================================================

class TestCatchDecorator:
    def test_success(self):
        @catch
        def add(a, b):
            return a + b

        res = add(2, 3)
        assert isinstance(res, Ok)
        assert res.unwrap() == 5

    def test_exception(self):
        @catch
        def fail():
            raise ValueError("oops")

        res = fail()
        assert isinstance(res, Err)
        err_val = res.unwrap_err()
        assert isinstance(err_val, ValueError)
        assert str(err_val) == "oops"

    def test_preserves_function_metadata(self):
        @catch
        def documented():
            """This is a docstring."""
            pass

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "This is a docstring."

    def test_does_not_catch_base_exception(self):
        @catch
        def interrupt():
            raise KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            interrupt()

    def test_function_with_args_and_kwargs(self):
        @catch
        def concat(a, b, *, sep=" "):
            return f"{a}{sep}{b}"

        res = concat("hello", "world", sep=", ")
        assert res.unwrap() == "hello, world"

    def test_chainable_with_methods(self):
        @catch
        def to_int(s: str) -> int:
            return int(s)

        result = to_int("123").map(lambda x: x * 2).unwrap()
        assert result == 246

        result_err = to_int("abc")
        assert result_err.is_err()
        assert isinstance(result_err.unwrap_err(), ValueError)


# =============================================================================
# try_catch 函数测试
# =============================================================================

class TestTryCatch:
    def test_success(self):
        def add(a, b):
            return a + b
        res = try_catch(add, 10, 20)
        assert isinstance(res, Ok)
        assert res.unwrap() == 30

    def test_exception(self):
        def divide(a, b):
            return a / b
        res = try_catch(divide, 1, 0)
        assert isinstance(res, Err)
        assert isinstance(res.unwrap_err(), ZeroDivisionError)

    def test_lambda_success(self):
        res = try_catch(lambda x: x.upper(), "hello")
        assert res.unwrap() == "HELLO"

    def test_args_and_kwargs(self):
        def greet(greeting, name):
            return f"{greeting}, {name}"
        res = try_catch(greet, "Hi", name="Alice")
        assert res.unwrap() == "Hi, Alice"


# =============================================================================
# 类型灵活性与边界情况
# =============================================================================

class TestEdgeCases:
    def test_ok_with_error_type_erased(self):
        # ok() 的 error 类型为 Any，可以赋值给更具体的 Result
        res: Result[int, str] = ok(10)
        assert res.unwrap() == 10

    def test_err_with_value_type_erased(self):
        res: Result[str, int] = err(404)
        assert res.unwrap_err() == 404

    def test_chaining_mixed_operations(self):
        # 模拟真实工作流
        def validate(x: int) -> Result[int, str]:
            return Ok(x) if x > 0 else Err("must be positive")

        def double(x: int) -> Result[int, str]:
            return Ok(x * 2)

        # 链式: Ok -> and_then -> map -> or_else
        r = ok(5).and_then(validate).map(lambda x: x * 10).or_else(lambda e: err("fallback"))
        assert r.unwrap() == 50

        r2 = ok(-1).and_then(validate).map(lambda x: x * 10).or_else(lambda e: Ok(999))
        assert r2.unwrap() == 999

    def test_expect_on_err_with_custom_message(self):
        e = Err[float, str]("timeout")
        with pytest.raises(UnwrapError, match=r"fatal: 'timeout'"):
            e.expect("fatal")
            
    def test_and_then_type_change(self):
        # Ok[int, str] -> and_then 产生 Result[str, str]
        r = Ok[int, str](1).and_then(lambda x: Ok[str, str]("hello"))
        assert r.unwrap() == "hello"

    def test_or_else_type_change(self):
        # Err[int, str] -> or_else 产生 Result[int, list]
        r = Err[int, str]("fail").or_else(lambda e: Err[int, list]([1,2,3]))
        assert r.unwrap_err() == [1,2,3]