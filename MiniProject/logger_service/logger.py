import logging
import functools

def safe(func):
    """
    Декоратор для обёртывания функций: поддерживает логирование ошибок
    

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Ошибка в {func.__name__}: {e}")
            return None
    return wrapper