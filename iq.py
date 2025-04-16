import time
import random
import math
import re
import ast
import sympy as sp
from difflib import SequenceMatcher

# Настройки теста
TIME_PENALTY_PER_CHAR = 0.1
TIME_PENALTY_PER_SEC = 0.5
BASE_IQ = 100
IQ_SCALE_FACTOR = 1.2

word_categories = {
    'easy': [
        ('электровоз', 3), ('фотография', 4), ('радиоэлектроника', 6),
        ('металлоконструкция', 6), ('автопогрузчик', 5), ('теплоэлектростанция', 7),
        ('книгоиздательство', 6), ('сельскохозяйственный', 6), ('железнодорожный', 5),
        ('высоковольтный', 5), ('крупногабаритный', 5), ('судостроительный', 6),
        ('лесопромышленный', 6), ('кинотеатр', 4), ('фотоаппарат', 5),
        ('телескоп', 4), ('микроволновка', 5), ('гидроэлектростанция', 8),
        ('аэропорт', 3), ('электрогитара', 6)
    ],
    'medium': [
        ('антидисэстэблишментаризм', 8), ('трансцендентальность', 6),
        ('квазиаксиоматичность', 7), ('ультрамикроскопический', 8),
        ('экзистенциальность', 6), ('интеллектуализация', 7),
        ('контрреформация', 6), ('гиперчувствительность', 7),
        ('псевдонаучность', 6), ('транснациональный', 6),
        ('инфраструктурный', 6), ('квазикристаллический', 7),
        ('метафизический', 6), ('парапсихология', 6),
        ('ультразвуковой', 6), ('антикоррозийный', 6),
        ('криптографический', 6), ('нейрофизиология', 7),
        ('радиоактивность', 7), ('трансмутация', 5)
    ],
    'hard': [
        ('псевдопаралингвистический', 9), ('ультрамикроскопически-спектрографический', 12),
        ('экзистенциально-феноменологический', 11), ('антиконституционно-государственный', 10),
        ('квазикристаллическо-аморфный', 9), ('трансцендентально-имманентный', 8),
        ('нейробиологически-физиологический', 10), ('радиоэлектронно-оптический', 9),
        ('квадрокоптерно-стабилизированный', 9), ('гидрометеорологический', 8),
        ('электрокардиографический', 8), ('фотоэлектрифицированный', 8),
        ('радиоиммунохимический', 7), ('криоэлектронный', 6),
        ('ультразвуково-диагностический', 9), ('макроэкономико-статистический', 9),
        ('антибактериально-резистентный', 9), ('квантово-механический', 7),
        ('нейропсихолингвистический', 8), ('гидроакустико-локационный', 9)
    ]
}

math_operations = {
    'easy': [
        ('15 + 7 − 3', 19), ('24 ÷ 3 × 2', 16), ('5² + 10', 35),
        ('√144 + 5', 17), ('20% от 50', 10), ('3³ − 10', 17),
        ('7 × 8 − 6', 50), ('45 ÷ 9 + 12', 17), ('100 − 34', 66),
        ('15 × 3 ÷ 5', 9), ('2⁴ + 10', 26), ('13 + 27 − 8', 32),
        ('56 ÷ 7 × 2', 16), ('√81 + 7²', 58), ('30% от 200', 60),
        ('4³ ÷ 8', 8), ('25 × 4 − 30', 70), ('99 − 45 + 12', 66),
        ('72 ÷ 9 × 5', 40), ('1.5 × 20 + 5', 35)
    ],
    'medium': [
        ('(18 + 7) × 3', 75), ('√225 + 4³', 79), ('35% от 140', 49),
        ('5! ÷ 10', 12), ('log₂(64) × 5', 30), ('sin(π/2) × 25', 25),
        ('3⁴ − 100', 11), ('(45 + 15) ÷ 4', 15), ('7² × √16', 196),
        ('2.5 × 16 + 10', 50), ('ln(e³)', 3), ('∫(2x dx) от 0 до 3', 9),
        ('15 × (4 + 3)', 105), ('40% от 250', 100), ('∛512 + 10²', 108),
        ('cos(0) × 50', 50), ('(12² − 44) ÷ 5', 20), ('Гипотенуза 5-12-?', 13),
        ('Сумма углов 7-угольника', 900), ('Среднее 15,20,25', 20)
    ],
    'hard': [
        ('∫(3x² dx) от 1 до 2', 7), ('lim(x→∞) (1+1/x)ˣ', math.e),
        ('det([[3,7],[2,5]])', 1), ('d/dx(eˣ + x³)', "eˣ + 3x²"),
        ('Матрица 2×2: [[1,2],[3,4]]ⁿ при n=2', [[7,10],[15,22]]),
        ('Комплексное число: (3+2i)(1-i)', "5 - i"),
        ('Вероятность 3 орла из 5 бросков', 0.3125),
        ('Факториал 7 ÷ 5!', 42), ('Ряд Фибоначчи 15-й член', 610),
        ('cos(π/3) × 100', 50), ('Объем сферы r=3', 113.097),
        ('Площадь эллипса a=5,b=3', 47.124), ('Производная ln(x²)', "2/x"),
        ('Ряд Тейлора eˣ при x=0', "1 + x + x²/2! + ..."),
        ('Диффур y = y', "y=Ceˣ"), ('Матожидание кубика', 3.5),
        ('Бином Ньютона (a+b)³', "a³+3a²b+3ab²+b³"),
        ('Предел (x²-4)/(x-2) при x→2', 4),
        ('Градиент f(x,y)=x²+y', "(2x, 1)"),
        ('Ранг матрицы [[1,2],[2,4]]', 1)
    ]
}

def calculate_word_accuracy(original, user_input):
    return SequenceMatcher(None, original.lower(), user_input.lower()).ratio()

def check_math_answer(user_input, correct_answer):
    try:
        # Для числовых ответов
        if isinstance(correct_answer, (int, float)):
            user_num = float(re.sub(r'[^0-9.eE-]', '', user_input))
            return abs(user_num - correct_answer) < 0.01
        
        # Для матриц и векторов
        if isinstance(correct_answer, (list, tuple)):
            user_clean = re.sub(r'\s+', '', user_input)
            user_list = ast.literal_eval(user_clean)
            return str(user_list) == str(correct_answer)
        
        # Для символьных выражений
        if isinstance(correct_answer, str):
            x = sp.symbols('x')
            try:
                user_expr = sp.sympify(user_input.replace('^', '**'))
                correct_expr = sp.sympify(correct_answer.replace('^', '**'))
                return sp.simplify(user_expr - correct_expr) == 0
            except:
                return user_input.lower() == correct_answer.lower()
        
    except:
        return False
    return False

def run_test(level):
    word, word_complexity = random.choice(word_categories[level])
    math_task, math_answer = random.choice(math_operations[level])
    
    print(f"\n▮ Уровень {level.capitalize()}")
    print(f"▮ Слово ({word_complexity} слогов): {word}")
    print(f"▮ Математическая задача: {math_task}")
    
    start_time = time.time()
    
    try:
        user_word = input("► Введите слово: ").strip()
        math_input = input("► Ответ на задачу: ")
    except:
        math_input = None
    
    total_time = time.time() - start_time
    
    # Расчет показателей
    word_score = calculate_word_accuracy(word, user_word)
    time_penalty = max(0, total_time - 15) * TIME_PENALTY_PER_SEC
    
    # Оценка математики
    math_score = 1 if check_math_answer(math_input, math_answer) else 0
    
    # Штрафы за ошибки
    error_penalty = (1 - word_score) * len(word) * TIME_PENALTY_PER_CHAR
    
    # Итоговый балл уровня
    level_score = (
        word_score * 40 +
        math_score * 60 -
        time_penalty -
        error_penalty
    )
    
    return {
        'word_score': word_score,
        'math_score': math_score,
        'time_penalty': time_penalty,
        'error_penalty': error_penalty,
        'total_score': max(0, level_score),
        'time': total_time
    }

def main():
    results = {}
    for level in ['easy', 'medium', 'hard']:
        results[level] = run_test(level)

    total = sum(res['total_score'] for res in results.values())
    time_avg = sum(res['time'] for res in results.values()) / 3

    # Нормализация IQ
    iq = BASE_IQ + (total - 150) * IQ_SCALE_FACTOR
    iq = max(70, min(145, round(iq)))

    # Отчет
    print("\n" + "="*55)
    print(f"{'ДЕТАЛИЗИРОВАННЫЙ ОТЧЕТ':^55}")
    print("="*55)
    
    for level in ['easy', 'medium', 'hard']:
        res = results[level]
        print(f"\n▌ {level.upper()} УРОВЕНЬ:")
        print(f"├ Точность воспроизведения: {res['word_score']*100:.1f}%")
        print(f"├ Точность математики: {res['math_score']*100:.1f}%")
        print(f"├ Затраченное время: {res['time']:.1f} сек")
        print(f"├ Штраф за время: -{res['time_penalty']:.1f}")
        print(f"└ Штраф за ошибки: -{res['error_penalty']:.1f}")

    print("\n" + "-"*55)
    print(f"СРЕДНЕЕ ВРЕМЯ РЕШЕНИЯ: {time_avg:.1f} сек")
    print(f"ОБЩИЙ СЫРОЙ БАЛЛ: {total:.1f}")
    print(f"ИНДЕКС ИНТЕЛЛЕКТА (IQ): {iq}")
    print("="*55)
    print("Формула расчета:\nIQ = 100 + (Общий_балл - 150) × 1.2")
    print("*Диапазон IQ ограничен 70-145 согласно тестовым нормам")
    print("="*55)

if __name__ == "__main__":
    main()
