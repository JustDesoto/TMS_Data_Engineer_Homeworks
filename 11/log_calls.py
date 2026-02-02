from functools import wraps
from datetime import datetime

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with open("11/function_log.txt", "a", encoding="utf-8") as file:
            file.write(
                f"Время вызова: {datetime.now()}\n"
                f"Имя функции: {func.__name__}\n"
                f"Аргументы: {args}, {kwargs}\n"
                f"Возвращаемое значение: {result}")
        return result
    return wrapper