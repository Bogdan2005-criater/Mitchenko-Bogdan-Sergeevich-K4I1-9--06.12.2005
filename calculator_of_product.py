import sqlite3
from configs import DATABASE

def calculate_product_output(product_type_id, material_type_id, raw_amount, param1, param2):
    try:
        product_type_id = int(product_type_id)
        material_type_id = int(material_type_id)
        raw_amount = float(raw_amount)
        param1 = float(param1)
        param2 = float(param2)
        
        if raw_amount <= 0 or param1 <= 0 or param2 <= 0:
            raise ValueError("Все числовые параметры должны быть положительными")
            
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            
            product_coeff = conn.execute('''
                SELECT coefficient FROM ProductType WHERE id = ?
            ''', (product_type_id,)).fetchone()
            
            if not product_coeff:
                raise ValueError("Тип продукции с указанным ID не найден")
            
            loss_percent = conn.execute('''
                SELECT loss_percent FROM MaterialType WHERE id = ?
            ''', (material_type_id,)).fetchone()
            
            if not loss_percent:
                raise ValueError("Тип материала с указанным ID не найден")
            
            product_coeff = product_coeff['coefficient']
            loss_percent = loss_percent['loss_percent']
            
            if product_coeff <= 0 or not (0 <= loss_percent < 1):
                raise ValueError("Некорректные коэффициенты в базе данных")
            
            material_per_unit = param1 * param2 * product_coeff
            
            if loss_percent >= 1:
                raise ValueError("Процент потерь должен быть меньше 1")
                
            required_material_per_unit = material_per_unit / (1 - loss_percent)
            
            product_count = raw_amount / required_material_per_unit
            
            return int(product_count)  
        
    except (ValueError, TypeError) as e:
        print(f"Ошибка ввода: {str(e)}")
        return -1
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {str(e)}")
        return -1
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        return -1

if __name__ == "__main__":
    print(calculate_product_output(1, 1, 1000.0, 2.0, 3.0))
    print(calculate_product_output(999, 1, 1000.0, 2.0, 3.0))
    print(calculate_product_output(1, 1, -1000.0, 2.0, 3.0))
