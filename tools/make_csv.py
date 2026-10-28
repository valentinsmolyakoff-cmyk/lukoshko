#!/usr/bin/env python3
"""Собирает уровни.csv прямо из index.html (источник правды — игра).

Запуск:  python3 tools/make_csv.py
"""
import csv, json, re, subprocess, tempfile, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'уровни.csv')

src = open(HTML, encoding='utf-8').read()
block = src[src.index("const LEVELS = ["): src.index("\n];\n", src.index("const LEVELS = [")) + 3]

js = ("const c=(q,good,bad,need,o={})=>Object.assign({k:'catch',q,good:good||[],bad:bad||[],need},o);\n"
      + block.replace("const LEVELS", "var LEVELS") +
      "\nrequire('fs').writeFileSync(process.argv[2], JSON.stringify(LEVELS));")
with tempfile.TemporaryDirectory() as d:
    jf = os.path.join(d, 'l.js'); of = os.path.join(d, 'l.json')
    open(jf, 'w', encoding='utf-8').write(js)
    subprocess.run(['node', jf, of], check=True)
    levels = json.load(open(of, encoding='utf-8'))

WORLDS = ["Яблоневый сад","Цветочная поляна","Букворечка","Счётная горка","Лесная школа",
          "Морской порт","Космос","Город профессий","Музыкальный замок","Звёздная башня",
          "Долина динозавров","Зоопарк","Времена года","Башня магии","Пиратские острова",
          "Ферма","Уютный дом","Безопасный город","Подводный мир","Радужный фестиваль"]
NAME = {'catch':'Ловля','sort':'Сортировка','mem':'Память','seq':'Узор','odd':'Лишнее',
        'diff':'Отличия','dots':'Точки','maze':'Лабиринт','rhythm':'Ритм','word':'Слово',
        'choice':'Вопрос'}

def est(l):
    t = 0.0
    for r in l['r']:
        k, rate = r['k'], r.get('rate', 900)
        if k == 'catch':  t += r.get('need', 6) * rate / 1000 + 2.5
        elif k == 'rhythm': t += r['need'] * (r.get('period', 1300) / 1000) + 2.5
        elif k == 'word': t += len(r['w']) * rate / 1000 + 2.5
        elif k == 'sort': t += r['need'] * 1.4
        elif k == 'mem':  t += len(r['set']) * 2.2
        elif k == 'dots': t += r['count'] * 1.4
        elif k == 'maze': t += r['size'] ** 2 * 0.30
        elif k == 'diff': t += 7
        elif k == 'odd':  t += 5
        else: t += 6
    return round(t, 1)

with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';', lineterminator='\r\n')
    w.writerow(['№', 'Мир', 'Название', 'Типы заданий', 'Задания', 'Раундов', '≈Секунд'])
    for l in levels:
        w.writerow([l['n'], WORLDS[l['w']], l['t'],
                    ', '.join(NAME[r['k']] for r in l['r']),
                    ' | '.join(r['q'] for r in l['r']),
                    len(l['r']), est(l)])
print("уровни.csv:", len(levels), "строк")
