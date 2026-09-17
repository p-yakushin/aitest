#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEONCLAW v3.0: 50 Врагов + Детальные Изображения + Кампания
"""
import pygame, math, random
pygame.init()

SCREEN_W, SCREEN_H = 1280, 720
HEX_SIZE = 40
FPS = 60

# Цвета
BG = (10, 10, 20)
NEON_PURPLE = (180, 50, 255)
NEON_BLUE = (50, 200, 255)
NEON_RED = (255, 50, 50)
NEON_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# 50 УНИКАЛЬНЫХ ВРАГОВ С ДЕТАЛЯМИ
ENEMIES = [
    # Tier 1 (id 0-4)
    {"id":0,"name":"Ржавый Паук","hp":15,"atk":8,"def":10,"spd":4,"col":(100,100,100),"det":["spider","rust"]},
    {"id":1,"name":"Мусорный Бот","hp":25,"atk":6,"def":15,"spd":3,"col":(139,69,19),"det":["robot","trash"]},
    {"id":2,"name":"Крыса-Киборг","hp":18,"atk":12,"def":5,"spd":7,"col":(150,150,150),"det":["rat","cyborg"]},
    {"id":3,"name":"Дрон-Глаз","hp":12,"atk":14,"def":4,"spd":6,"col":(255,0,0),"det":["drone","eye"]},
    {"id":4,"name":"Нано-Жук","hp":10,"atk":8,"def":3,"spd":8,"col":(0,255,0),"det":["bug","nano"]},
    # Tier 2 (id 5-9)
    {"id":5,"name":"Наёмник Мур","hp":30,"atk":15,"def":12,"spd":6,"col":(255,215,0),"det":["cat","merc"]},
    {"id":6,"name":"Телохранитель","hp":45,"atk":10,"def":20,"spd":4,"col":(255,140,0),"det":["cat","guard"]},
    {"id":7,"name":"Снайпер Крыши","hp":25,"atk":20,"def":8,"spd":7,"col":(192,192,192),"det":["cat","sniper"]},
    {"id":8,"name":"Техно-Жрец","hp":28,"atk":8,"def":10,"spd":5,"col":(255,255,255),"det":["cat","priest"]},
    {"id":9,"name":"Хакер Теней","hp":22,"atk":18,"def":6,"spd":8,"col":(148,0,211),"det":["cat","hacker"]},
    # Tier 3 (id 10-14)
    {"id":10,"name":"Шёлковый Убийца","hp":40,"atk":25,"def":15,"spd":9,"col":(180,50,255),"det":["cat","assassin"]},
    {"id":11,"name":"Страж Кремня","hp":60,"atk":18,"def":30,"spd":3,"col":(255,100,0),"det":["cat","tank"]},
    {"id":12,"name":"Лунный Друид","hp":35,"atk":15,"def":12,"spd":6,"col":(50,200,255),"det":["cat","druid"]},
    {"id":13,"name":"Био-Инженер","hp":40,"atk":12,"def":15,"spd":5,"col":(0,255,127),"det":["cat","engineer"]},
    {"id":14,"name":"Дрон-Оса","hp":30,"atk":22,"def":10,"spd":10,"col":(255,255,0),"det":["wasp","mech"]},
    # Tier 4 (id 15-19)
    {"id":15,"name":"Пустой Кот","hp":50,"atk":30,"def":20,"spd":8,"col":(50,50,50),"det":["void","cat"]},
    {"id":16,"name":"Монолит Защиты","hp":80,"atk":20,"def":40,"spd":2,"col":(100,0,0),"det":["golem","shield"]},
    {"id":17,"name":"Вирусный Разум","hp":45,"atk":35,"def":15,"spd":7,"col":(0,100,0),"det":["virus","ai"]},
    {"id":18,"name":"Фантом Сети","hp":40,"atk":25,"def":18,"spd":6,"col":(150,0,255),"det":["ghost","net"]},
    {"id":19,"name":"Лазерный Луч","hp":35,"atk":40,"def":12,"spd":9,"col":(255,0,100),"det":["laser","beam"]},
    # Tier 5 (id 20-24)
    {"id":20,"name":"Танк Коготь","hp":100,"atk":30,"def":50,"spd":2,"col":(70,70,70),"det":["tank","heavy"]},
    {"id":21,"name":"Ховер-Байк","hp":60,"atk":35,"def":20,"spd":12,"col":(0,255,255),"det":["hover","bike"]},
    {"id":22,"name":"Арт-Турель","hp":70,"atk":45,"def":25,"spd":1,"col":(100,100,0),"det":["turret","gun"]},
    {"id":23,"name":"Ремонтный Дрон","hp":50,"atk":10,"def":30,"spd":4,"col":(200,200,200),"det":["repair","bot"]},
    {"id":24,"name":"Генератор Помех","hp":55,"atk":25,"def":20,"spd":5,"col":(150,50,150),"det":["jammer","tech"]},
    # Tier 6 (id 25-29)
    {"id":25,"name":"Гигантский Таракан","hp":90,"atk":25,"def":45,"spd":3,"col":(50,30,10),"det":["roach","mutant"]},
    {"id":26,"name":"Кислотный Слизень","hp":70,"atk":30,"def":15,"spd":4,"col":(0,255,0),"det":["slime","acid"]},
    {"id":27,"name":"Летучая Мышь","hp":60,"atk":35,"def":10,"spd":11,"col":(100,0,100),"det":["bat","wing"]},
    {"id":28,"name":"Пси-Червь","hp":50,"atk":40,"def":10,"spd":6,"col":(255,100,100),"det":["worm","psi"]},
    {"id":29,"name":"Гриб-Разум","hp":65,"atk":20,"def":25,"spd":2,"col":(255,150,200),"det":["mushroom","hive"]},
    # Tier 7 (id 30-35)
    {"id":30,"name":"Палач ЗЕНИТа","hp":80,"atk":50,"def":30,"spd":9,"col":(255,0,0),"det":["executioner","elite"]},
    {"id":31,"name":"Бастион Истины","hp":120,"atk":35,"def":60,"spd":3,"col":(200,0,0),"det":["bastion","truth"]},
    {"id":32,"name":"Оракул Данных","hp":70,"atk":55,"def":25,"spd":8,"col":(150,0,150),"det":["oracle","data"]},
    {"id":33,"name":"Архангел Сети","hp":75,"atk":45,"def":30,"spd":7,"col":(255,255,255),"det":["angel","network"]},
    {"id":34,"name":"Снайпер Судьбы","hp":65,"atk":60,"def":20,"spd":10,"col":(255,100,100),"det":["fate","sniper"]},
    {"id":35,"name":"Целитель Вируса","hp":80,"atk":30,"def":35,"spd":6,"col":(200,255,200),"det":["healer","virus"]},
    # Tier 8 (id 36-40)
    {"id":36,"name":"Прототип Титан","hp":150,"atk":45,"def":70,"spd":2,"col":(50,50,100),"det":["titan","proto"]},
    {"id":37,"name":"Прототип Призрак","hp":90,"atk":60,"def":35,"spd":12,"col":(100,100,255),"det":["ghost","proto"]},
    {"id":38,"name":"Прототип Шторм","hp":80,"atk":70,"def":25,"spd":11,"col":(200,200,255),"det":["storm","proto"]},
    {"id":39,"name":"Прототип Разум","hp":85,"atk":65,"def":30,"spd":9,"col":(150,150,255),"det":["mind","proto"]},
    {"id":40,"name":"Прототип Жизнь","hp":100,"atk":40,"def":40,"spd":5,"col":(200,255,200),"det":["life","proto"]},
    # Tier 9 (id 41-45)
    {"id":41,"name":"Король Мусора","hp":200,"atk":50,"def":80,"spd":3,"col":(139,69,19),"det":["king","trash"]},
    {"id":42,"name":"Тень Прошлого","hp":180,"atk":80,"def":40,"spd":13,"col":(0,0,0),"det":["shadow","past"]},
    {"id":43,"name":"Мать Роя","hp":160,"atk":60,"def":50,"spd":6,"col":(255,0,255),"det":["queen","swarm"]},
    {"id":44,"name":"Архитектор Боли","hp":150,"atk":90,"def":45,"spd":10,"col":(100,0,0),"det":["architect","pain"]},
    {"id":45,"name":"Око Бури","hp":140,"atk":100,"def":35,"spd":12,"col":(0,100,255),"det":["eye","storm"]},
    # Tier 10 (id 46-49)
    {"id":46,"name":"Аватар Война","hp":300,"atk":120,"def":80,"spd":15,"col":(255,0,0),"det":["avatar","war"]},
    {"id":47,"name":"Аватар Защита","hp":400,"atk":80,"def":150,"spd":5,"col":(0,255,0),"det":["avatar","defense"]},
    {"id":48,"name":"Аватар Контроль","hp":250,"atk":150,"def":60,"spd":12,"col":(0,0,255),"det":["avatar","control"]},
    {"id":49,"name":"МЯУ-ЗЕНИТ","hp":500,"atk":200,"def":100,"spd":10,"col":(255,255,255),"det":["final","boss"]},
]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)
bigfont = pygame.font.SysFont("Arial", 32, bold=True)

class Unit:
    def __init__(self, x, y, is_enemy=False, eid=0, lvl=1):
        self.x, self.y = x, y
        self.is_enemy = is_enemy
        self.lvl = lvl
        if is_enemy and eid < len(ENEMIES):
            e = ENEMIES[eid]
            self.name = e["name"]
            self.maxhp = int(e["hp"] * (1 + lvl*0.1))
            self.hp = self.maxhp
            self.atk = int(e["atk"] * (1 + lvl*0.1))
            self.def_ = int(e["def"] * (1 + lvl*0.1))
            self.col = e["col"]
            self.details = e["det"]
        else:
            self.name = "Кот-Герой"
            self.maxhp = 50 + lvl*5
            self.hp = self.maxhp
            self.atk = 15 + lvl*2
            self.def_ = 8 + lvl
            self.col = NEON_BLUE
            self.details = ["hero","cat"]
        self.anim = 0
    
    def draw(self, surf, cx, cy):
        breath = math.sin(self.anim * 5) * 2
        # Тело
        pygame.draw.circle(surf, self.col, (int(cx), int(cy-10+breath)), 12)
        # Голова
        pygame.draw.circle(surf, self.col, (int(cx), int(cy-25+breath)), 10)
        # Уши
        pygame.draw.polygon(surf, self.col, [(cx-8,cy-30+breath),(cx-12,cy-40+breath),(cx-4,cy-35+breath)])
        pygame.draw.polygon(surf, self.col, [(cx+8,cy-30+breath),(cx+12,cy-40+breath),(cx+4,cy-35+breath)])
        # Глаза
        ecol = NEON_RED if self.is_enemy else WHITE
        pygame.draw.circle(surf, ecol, (int(cx-3), int(cy-27+breath)), 2)
        pygame.draw.circle(surf, ecol, (int(cx+3), int(cy-27+breath)), 2)
        # Детали врага (уникальные элементы)
        if self.is_enemy and len(self.details) > 0:
            det = self.details[0]
            if det == "spider":  # Ноги паука
                for i in range(4):
                    pygame.draw.line(surf, self.col, (cx,cy), (cx-15+i*10, cy+5), 2)
            elif det == "eye":  # Большой глаз
                pygame.draw.circle(surf, (255,255,0), (int(cx), int(cy-25+breath)), 4)
            elif det == "wing":  # Крылья
                pygame.draw.polygon(surf, self.col, [(cx-10,cy-20+breath),(cx-20,cy-30+breath),(cx-10,cy-25+breath)])
                pygame.draw.polygon(surf, self.col, [(cx+10,cy-20+breath),(cx+20,cy-30+breath),(cx+10,cy-25+breath)])
            elif det == "horn":  # Рога
                pygame.draw.line(surf, (255,0,0), (cx-5,cy-35+breath), (cx-8,cy-45+breath), 2)
                pygame.draw.line(surf, (255,0,0), (cx+5,cy-35+breath), (cx+8,cy-45+breath), 2)
        # HP bar
        pct = max(0, self.hp / self.maxhp)
        pygame.draw.rect(surf, (50,50,50), (cx-15, cy-45+breath, 30, 4))
        pygame.draw.rect(surf, (0,255,0), (cx-15, cy-45+breath, 30*pct, 4))

class Game:
    def __init__(self):
        self.state = "MENU"
        self.units = []
        self.selected = None
        self.mission = 0
        self.log = ["NEONCLAW v3.0 - 50 Врагов!"]
    
    def start_mission(self, m):
        self.mission = m
        self.units = [Unit(2,2,False,lvl=5), Unit(2,3,False,lvl=5)]
        # Босс миссии
        boss_id = min(m * 3 + random.randint(0,2), 49)
        self.units.append(Unit(GRID_W-2, GRID_H//2, True, boss_id, lvl=5+m))
        # Миньоны
        for _ in range(3+m):
            mid = random.randint(0, 48)
            self.units.append(Unit(random.randint(GRID_W//2,GRID_W-1), random.randint(0,GRID_H-1), True, mid, lvl=3+m))
        self.state = "BATTLE"
        self.selected = self.units[0]
        self.log.append(f"Миссия {m+1}: {ENEMIES[boss_id]['name']}!")
    
    def update(self, dt):
        for u in self.units:
            u.anim += dt
    
    def draw(self):
        screen.fill(BG)
        if self.state == "MENU":
            t = bigfont.render("NEONCLAW: 50 Врагов", True, NEON_GOLD)
            screen.blit(t, (SCREEN_W//2-t.get_width()//2, SCREEN_H//2-50))
            btn = pygame.Rect(SCREEN_W//2-100, SCREEN_H//2, 200, 50)
            pygame.draw.rect(screen, NEON_BLUE, btn)
            screen.blit(font.render("КАМПАНИЯ", True, BG), (btn.x+50, btn.y+15))
            # Список врагов
            y = SCREEN_H//2 + 70
            for i in range(min(10, len(ENEMIES))):
                e = ENEMIES[i]
                c = font.render(f"{i}. {e['name']} ({e['det'][0]})", True, e["col"])
                screen.blit(c, (SCREEN_W//2-150, y))
                y += 20
        elif self.state == "BATTLE":
            # Гексы
            for r in range(GRID_H):
                for c in range(GRID_W):
                    cx = c * HEX_SIZE * 1.5 + 50
                    cy = r * HEX_SIZE * 1.732 + (HEX_SIZE * 0.866) * (c % 2) + 50
                    pts = []
                    for i in range(6):
                        a = math.pi/3 * i
                        pts.append((cx + HEX_SIZE*math.cos(a), cy + HEX_SIZE*math.sin(a)))
                    pygame.draw.polygon(screen, (40,40,60), pts)
                    pygame.draw.polygon(screen, (80,80,100), pts, 1)
            # Юниты
            for u in self.units:
                cx = u.x * HEX_SIZE * 1.5 + 50
                cy = u.y * HEX_SIZE * 1.732 + (HEX_SIZE * 0.866) * (int(u.x) % 2) + 50
                u.draw(screen, cx, cy)
            # UI
            pygame.draw.rect(screen, (20,20,40), (0, SCREEN_H-120, SCREEN_W, 120))
            y = SCREEN_H - 110
            for msg in self.log[-4:]:
                screen.blit(font.render(msg, True, WHITE), (20, y))
                y += 25
            if self.selected:
                info = f"{self.selected.name} HP:{self.selected.hp}/{self.selected.maxhp} ATK:{self.selected.atk}"
                screen.blit(font.render(info, True, NEON_GOLD), (SCREEN_W-400, SCREEN_H-110))
                details = f"Det: {self.selected.details}"
                screen.blit(font.render(details, True, NEON_BLUE), (SCREEN_W-400, SCREEN_H-90))
        pygame.display.flip()
    
    def handle(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.MOUSEBUTTONDOWN and self.state == "MENU":
                mx,my = pygame.mouse.get_pos()
                if SCREEN_W//2-100 < mx < SCREEN_W//2+100 and SCREEN_H//2 < my < SCREEN_H//2+50:
                    self.start_mission(0)
            if ev.type == pygame.MOUSEBUTTONDOWN and self.state == "BATTLE":
                mx,my = pygame.mouse.get_pos()
                # Найти ближайший гекс
                best,bhex = 9999,None
                for r in range(GRID_H):
                    for c in range(GRID_W):
                        cx = c * HEX_SIZE * 1.5 + 50
                        cy = r * HEX_SIZE * 1.732 + (HEX_SIZE * 0.866) * (c % 2) + 50
                        d = math.hypot(mx-cx, my-cy)
                        if d < best: best,bhex = d,(c,r)
                if bhex and best < HEX_SIZE:
                    hx,hy = bhex
                    clicked = None
                    for u in self.units:
                        if u.x == hx and u.y == hy: clicked = u; break
                    if clicked:
                        if not clicked.is_enemy:
                            self.selected = clicked
                            self.log.append(f"Выбран: {clicked.name}")
                        elif self.selected:
                            dmg = max(1, self.selected.atk - clicked.def_//2)
                            clicked.hp -= dmg
                            self.log.append(f"{self.selected.name} бьёт {clicked.name} на {dmg}!")
                            if clicked.hp <= 0:
                                self.log.append(f"{clicked.name} погиб!")
                                self.units.remove(clicked)
                                if all(not u.is_enemy for u in self.units):
                                    self.log.append("ПОБЕДА! След. миссия...")
                                    pygame.time.wait(1500)
                                    self.start_mission(self.mission + 1)
                            self.selected = None
                    elif self.selected:
                        self.selected.x, self.selected.y = hx, hy
                        self.log.append(f"Ход в ({hx},{hy})")
        return True
    
    def run(self):
        running = True
        while running:
            dt = clock.tick(FPS)/1000
            running = self.handle()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
