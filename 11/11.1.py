from log_calls import log_calls

@log_calls
def safe_calculator(a, b, operation):
    try:
        a = float(a)
        b = float(b)

        if operation == "+":
            return a + b
        elif operation == "-":
            return a - b
        elif operation == "*":
            return a * b
        elif operation == "/":
            return a / b
        else:
            return "Неподдерживаемая операция"
        
    except ZeroDivisionError:
        return "Деление на ноль"
    except ValueError:
        return "Неверный тип данных"
    

# Для тестирования

a = input("Введите a: ")
b = input("Введите b: ")
operation = input("Введите тип операции (+, -, *, /): ")
print(safe_calculator(a,b,operation))
    