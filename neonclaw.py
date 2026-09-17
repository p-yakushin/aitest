#!/usr/bin/env python3
"""
🐱 NEONCLAW: Хроники Девяти Жизней
Пошаговая TRPG в стиле Langrisser

Управление:
- ЛКМ: выбор юнита/атака/перемещение
- ПКМ: отмена выбора
- Пробел: завершить ход
- ESC: выход
"""

import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# === КОНСТАНТЫ ===
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
HEX_SIZE = 40
GRID_COLS = 12
GRID_ROWS = 12
FPS = 60

# Цвета (неоновая палитра)
COLOR_BG = (10, 10, 30)
COLOR_GRID = (30, 30, 60)
COLOR_HIGHLIGHT = (100, 100, 255, 100)
COLOR_ATTACK_RANGE = (255, 100, 100, 100)
COLOR_NEON_PURPLE = (180, 50, 255)
COLOR_NEON_ORANGE = (255, 150, 50)
COLOR_NEON_BLUE = (50, 200, 255)
COLOR_NEON_GOLD = (255, 220, 50)
COLOR_NEON_RED = (255, 50, 80)
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (20, 20, 40)
COLOR_HP_BAR = (50, 255, 100)
COLOR_HP_LOW = (255, 50, 50)

# === ПЕРЕЧИСЛЕНИЯ ===

class Faction(Enum):
    SILK = "Шёлковые"      # Хакеры
    FLINT = "Кремень"      # Инженеры
    MOON = "Луна"          # Биоманты
    SYNDICATE = "Синдикат" # Наёмники
    MEOW_ZENITH = "МЯУ-ЗЕНИТ"  # Враг

class UnitClass(Enum):
    GUARDIAN = "Страж"
    BLADE = "Клинок"
    NETRUNNER = "Хакер"
    MENDER = "Медик"
    SNIPER = "Снайпер"
    CALLER = "Призыватель"

class GameState(Enum):
    PLAYER_TURN = "Ход игрока"
    ENEMY_TURN = "Ход врага"
    GAME_OVER = "Конец игры"
    VICTORY = "Победа"

# === ТРЕУГОЛЬНИК УРОНА ===
CLASS_ADVANTAGES = {
    UnitClass.BLADE: UnitClass.SNIPER,
    UnitClass.SNIPER: UnitClass.GUARDIAN,
    UnitClass.GUARDIAN: UnitClass.BLADE,
    UnitClass.NETRUNNER: UnitClass.CALLER,
    UnitClass.CALLER: UnitClass.MENDER,
    UnitClass.MENDER: UnitClass.NETRUNNER,
}

# === КЛАССЫ ===

@dataclass
class Stats:
    str_: int = 5  # Сила
    agi: int = 5   # Ловкость
    int_: int = 5  # Интеллект
    wis: int = 5   # Мудрость
    cha: int = 5   # Харизма
    
    def get_attack(self, unit_class: UnitClass) -> int:
        if unit_class in [UnitClass.BLADE, UnitClass.GUARDIAN]:
            return self.str_ * 2 + self.agi
        elif unit_class in [UnitClass.SNIPER]:
            return self.str_ + self.agi * 2
        elif unit_class in [UnitClass.NETRUNNER]:
            return self.int_ * 2 + self.agi
        elif unit_class in [UnitClass.MENDER, UnitClass.CALLER]:
            return self.wis * 2 + self.int_
        return self.str_ + self.agi
    
    def get_defense(self, unit_class: UnitClass) -> int:
        if unit_class == UnitClass.GUARDIAN:
            return self.str_ * 2 + self.agi
        elif unit_class in [UnitClass.BLADE, UnitClass.SNIPER]:
            return self.agi * 2
        else:
            return self.wis + self.int_
    
    def get_hp(self, unit_class: UnitClass) -> int:
        base = 20
        if unit_class == UnitClass.GUARDIAN:
            return base + self.str_ * 3
        elif unit_class == UnitClass.BLADE:
            return base + self.str_ * 2 + self.agi
        elif unit_class == UnitClass.SNIPER:
            return base + self.agi * 2
        else:
            return base + self.wis * 2

@dataclass
class Unit:
    name: str
    unit_class: UnitClass
    faction: Faction
    level: int = 1
    stats: Stats = field(default_factory=Stats)
    hp: int = 20
    max_hp: int = 20
    lives: int = 9  # Девять жизней
    ap: int = 3     # Очки действия
    max_ap: int = 3
    position: Tuple[int, int] = (0, 0)
    is_player: bool = True
    has_moved: bool = False
    has_attacked: bool = False
    murr_charge: int = 0  # Шкала мурчания
    
    def __post_init__(self):
        self.max_hp = self.stats.get_hp(self.unit_class)
        self.hp = self.max_hp
    
    def get_attack_power(self) -> int:
        return self.stats.get_attack(self.unit_class) + self.level * 2
    
    def get_defense_power(self) -> int:
        return self.stats.get_defense(self.unit_class) + self.level
    
    def get_move_range(self) -> int:
        base = 4
        if self.unit_class == UnitClass.BLADE:
            return base + 2
        elif self.unit_class == UnitClass.SNIPER:
            return base - 1
        elif self.unit_class == UnitClass.GUARDIAN:
            return base - 1
        return base
    
    def get_attack_range(self) -> int:
        if self.unit_class == UnitClass.SNIPER:
            return 5
        elif self.unit_class == UnitClass.NETRUNNER:
            return 4
        elif self.unit_class == UnitClass.BLADE:
            return 1
        return 2
    
    def get_advantage_multiplier(self, target: 'Unit') -> float:
        """Проверка преимущества по треугольнику урона"""
        if self.unit_class in CLASS_ADVANTAGES:
            if CLASS_ADVANTAGES[self.unit_class] == target.unit_class:
                return 1.5  # Преимущество +50%
            # Проверка обратного преимущества
            if target.unit_class in CLASS_ADVANTAGES:
                if CLASS_ADVANTAGES[target.unit_class] == self.unit_class:
                    return 0.7  # Недостаток -30%
        return 1.0
    
    def reset_turn(self):
        self.ap = self.max_ap
        self.has_moved = False
        self.has_attacked = False

@dataclass
class Hex:
    col: int
    row: int
    terrain: str = "normal"  # normal, acid, neon_tower, roof
    height: int = 0
    is_walkable: bool = True
    is_highlighted: bool = False
    is_attack_range: bool = False

# === ИГРОВОЙ ДВИЖОК ===

class NeonClawGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🐱 NEONCLAW: Хроники Девяти Жизней")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 18)
        
        self.state = GameState.PLAYER_TURN
        self.selected_unit: Optional[Unit] = None
        self.valid_moves: List[Tuple[int, int]] = []
        self.valid_targets: List[Tuple[int, int]] = []
        self.message_log: List[str] = []
        self.turn_number = 1
        self.murr_meter = 0  # Общая шкала мурчания
        
        #_offset для центрирования сетки
        self.grid_offset_x = (SCREEN_WIDTH - GRID_COLS * HEX_SIZE * 1.5) // 2
        self.grid_offset_y = 100
        
        self.units: List[Unit] = []
        self.hex_grid: List[List[Hex]] = []
        
        self.setup_game()
        self.log("Добро пожаловать в NEONCLAW!")
        self.log("Победите всех врагов МЯУ-ЗЕНИТа!")
    
    def setup_game(self):
        """Инициализация игры"""
        # Создаём сетку
        self.hex_grid = [[Hex(c, r) for c in range(GRID_COLS)] for r in range(GRID_ROWS)]
        
        # Добавляем террейн
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if random.random() < 0.1:
                    self.hex_grid[r][c].terrain = "acid"
                    self.hex_grid[r][c].is_walkable = True  # Можно ходить, но с уроном
                elif random.random() < 0.05:
                    self.hex_grid[r][c].terrain = "neon_tower"
                    self.hex_grid[r][c].height = 2
        
        # Создаём команду игрока
        player_units = [
            Unit("Рэйзор", UnitClass.BLADE, Faction.SILK, position=(2, 5), is_player=True),
            Unit("Бастион", UnitClass.GUARDIAN, Faction.FLINT, position=(1, 6), is_player=True),
            Unit("Нэт", UnitClass.NETRUNNER, Faction.SILK, position=(3, 5), is_player=True),
            Unit("Луна", UnitClass.MENDER, Faction.MOON, position=(2, 6), is_player=True),
        ]
        
        for unit in player_units:
            unit.position = (unit.position[0], unit.position[1])
            self.units.append(unit)
        
        # Создаём врагов
        enemy_units = [
            Unit("Дрон-1", UnitClass.BLADE, Faction.MEOW_ZENITH, position=(8, 3), is_player=False),
            Unit("Дрон-2", UnitClass.SNIPER, Faction.MEOW_ZENITH, position=(9, 4), is_player=False),
            Unit("Дрон-3", UnitClass.GUARDIAN, Faction.MEOW_ZENITH, position=(8, 5), is_player=False),
            Unit("Дрон-4", UnitClass.NETRUNNER, Faction.MEOW_ZENITH, position=(9, 6), is_player=False),
            Unit("Коммандер ЗЕН", UnitClass.BLADE, Faction.MEOW_ZENITH, position=(10, 4), level=3, is_player=False),
        ]
        
        for unit in enemy_units:
            self.units.append(unit)
        
        # Обновляем позиции в сетке
        for unit in self.units:
            col, row = unit.position
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                pass  # Позиция уже установлена
    
    def hex_to_pixel(self, col: int, row: int) -> Tuple[int, int]:
        """Конвертация гекса в пиксели"""
        x = self.grid_offset_x + col * HEX_SIZE * 1.5
        y = self.grid_offset_y + row * HEX_SIZE * math.sqrt(3) / 2
        if col % 2 == 1:
            y += HEX_SIZE * math.sqrt(3) / 4
        return int(x), int(y)
    
    def pixel_to_hex(self, x: int, y: int) -> Tuple[int, int]:
        """Конвертация пикселей в гекс"""
        rel_x = x - self.grid_offset_x
        rel_y = y - self.grid_offset_y
        
        row = int(rel_y / (HEX_SIZE * math.sqrt(3) / 2))
        col = int(rel_x / (HEX_SIZE * 1.5))
        
        # Корректировка для нечётных колонок
        if col % 2 == 1:
            rel_y -= HEX_SIZE * math.sqrt(3) / 4
        
        row = int(rel_y / (HEX_SIZE * math.sqrt(3) / 2))
        
        return max(0, min(GRID_COLS - 1, col)), max(0, min(GRID_ROWS - 1, row))
    
    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Расстояние между гексами (манхэттенское для гексов)"""
        c1, r1 = pos1
        c2, r2 = pos2
        
        # Конвертация в кубические координаты
        x1, z1 = c1, r1 - (c1 - (c1 & 1)) / 2
        x2, z2 = c2, r2 - (c2 - (c2 & 1)) / 2
        
        dx = abs(x1 - x2)
        dz = abs(z1 - z2)
        
        if x1 < x2 and z1 > z2:
            return max(dx, dz)
        elif x1 > x2 and z1 < z2:
            return max(dx, dz)
        else:
            return dx + dz
    
    def get_valid_moves(self, unit: Unit) -> List[Tuple[int, int]]:
        """Получение доступных ходов для юнита"""
        moves = []
        move_range = unit.get_move_range()
        start_col, start_row = unit.position
        
        for dr in range(-move_range, move_range + 1):
            for dc in range(-move_range, move_range + 1):
                new_col = start_col + dc
                new_row = start_row + dr
                
                if 0 <= new_col < GRID_COLS and 0 <= new_row < GRID_ROWS:
                    dist = self.get_distance(unit.position, (new_col, new_row))
                    if 0 < dist <= move_range:
                        hex_cell = self.hex_grid[new_row][new_col]
                        if hex_cell.is_walkable:
                            # Проверка, нет ли там другого юнита
                            occupied = any(u.position == (new_col, new_row) for u in self.units)
                            if not occupied:
                                moves.append((new_col, new_row))
        
        return moves
    
    def get_valid_targets(self, unit: Unit) -> List[Tuple[int, int]]:
        """Получение доступных целей для атаки"""
        targets = []
        attack_range = unit.get_attack_range()
        
        for other in self.units:
            if other.is_player != unit.is_player:  # Только враги/союзники
                dist = self.get_distance(unit.position, other.position)
                if 0 < dist <= attack_range:
                    targets.append(other.position)
        
        return targets
    
    def get_unit_at(self, col: int, row: int) -> Optional[Unit]:
        """Получение юнита на позиции"""
        for unit in self.units:
            if unit.position == (col, row):
                return unit
        return None
    
    def calculate_damage(self, attacker: Unit, defender: Unit) -> int:
        """Расчёт урона"""
        base_attack = attacker.get_attack_power()
        base_defense = defender.get_defense_power()
        
        advantage = attacker.get_advantage_multiplier(defender)
        
        # Бросок d20
        roll = random.randint(1, 20)
        total_attack = roll + base_attack
        
        if total_attack <= base_defense:
            return 0
        
        # Базовый урон d6 + модификатор
        damage_roll = random.randint(1, 6) + (base_attack // 2)
        damage = int(damage_roll * advantage)
        
        # Комбо-атака (если есть союзники рядом)
        allies_nearby = sum(1 for u in self.units 
                          if u.is_player == attacker.is_player 
                          and u != attacker 
                          and self.get_distance(u.position, defender.position) <= 1)
        
        if allies_nearby >= 2:
            damage = int(damage * 1.8)
            self.log(f"Комбо-атака! ×1.8 урона!")
        elif allies_nearby >= 3:
            damage = int(damage * 2.5)
            self.log(f"ПРАЙД-ШТОРМ! ×2.5 урона и оглушение!")
        
        return max(1, damage) if damage > 0 else 0
    
    def attack(self, attacker: Unit, target: Unit):
        """Проведение атаки"""
        damage = self.calculate_damage(attacker, target)
        
        # Эффекты преимущества
        advantage = attacker.get_advantage_multiplier(target)
        if advantage > 1.0:
            self.log(f"Преимущество класса! {attacker.unit_class.value} > {target.unit_class.value}")
        elif advantage < 1.0:
            self.log(f"Недостаток класса! {attacker.unit_class.value} < {target.unit_class.value}")
        
        target.hp -= damage
        self.log(f"{attacker.name} атакует {target.name}: {damage} урона!")
        
        # Заполнение шкалы мурчания
        attacker.murr_charge = min(100, attacker.murr_charge + 20)
        self.murr_meter = min(100, self.murr_meter + 10)
        
        # Проверка смерти
        if target.hp <= 0:
            target.lives -= 1
            if target.lives <= 0:
                self.log(f"☠️ {target.name} погиб навсегда!")
                self.units.remove(target)
            else:
                self.log(f"💀 {target.name} теряет жизнь! Осталось: {target.lives}")
                target.hp = target.max_hp // 2  # Возрождается с половиной HP
        
        attacker.has_attacked = True
        attacker.ap -= 1
    
    def move_unit(self, unit: Unit, new_pos: Tuple[int, int]):
        """Перемещение юнита"""
        old_pos = unit.position
        unit.position = new_pos
        unit.has_moved = True
        unit.ap -= 1
        
        # Урон от кислоты
        hex_cell = self.hex_grid[new_pos[1]][new_pos[0]]
        if hex_cell.terrain == "acid":
            unit.hp -= 2
            self.log(f"☣️ {unit.name} получает 2 урона от кислоты!")
        
        self.log(f"{unit.name} перемещается из ({old_pos[0]},{old_pos[1]}) в ({new_pos[0]},{new_pos[1]})")
    
    def end_turn(self):
        """Завершение хода"""
        if self.state == GameState.PLAYER_TURN:
            for unit in self.units:
                if unit.is_player:
                    unit.reset_turn()
            self.state = GameState.ENEMY_TURN
            self.turn_number += 1
            self.log(f"--- Ход врага {self.turn_number} ---")
            self.process_enemy_turn()
        else:
            for unit in self.units:
                if not unit.is_player:
                    unit.reset_turn()
            self.state = GameState.PLAYER_TURN
            self.log(f"--- Ход игрока {self.turn_number} ---")
    
    def process_enemy_turn(self):
        """Обработка хода врага (простой ИИ)"""
        pygame.time.wait(500)  # Небольшая задержка
        
        enemies = [u for u in self.units if not u.is_player]
        players = [u for u in self.units if u.is_player]
        
        if not players:
            self.state = GameState.GAME_OVER
            return
        
        for enemy in enemies:
            if enemy not in self.units:
                continue
            
            # Найти ближайшего игрока
            nearest_player = min(players, 
                               key=lambda p: self.get_distance(enemy.position, p.position),
                               default=None)
            
            if nearest_player:
                dist = self.get_distance(enemy.position, nearest_player.position)
                attack_range = enemy.get_attack_range()
                
                if dist <= attack_range:
                    # Атаковать
                    self.attack(enemy, nearest_player)
                else:
                    # Двигаться к игроку
                    valid_moves = self.get_valid_moves(enemy)
                    if valid_moves:
                        # Выбрать ход, который приближает к цели
                        best_move = min(valid_moves, 
                                      key=lambda m: self.get_distance(m, nearest_player.position))
                        self.move_unit(enemy, best_move)
                        
                        # Если после хода можно атаковать
                        new_dist = self.get_distance(enemy.position, nearest_player.position)
                        if new_dist <= attack_range:
                            self.attack(enemy, nearest_player)
        
        pygame.time.wait(500)
        self.end_turn()
    
    def log(self, message: str):
        """Добавление сообщения в лог"""
        self.message_log.append(message)
        if len(self.message_log) > 10:
            self.message_log.pop(0)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Обработка клика мыши"""
        col, row = self.pixel_to_hex(pos[0], pos[1])
        
        if not (0 <= col < GRID_COLS and 0 <= row < GRID_ROWS):
            return
        
        clicked_unit = self.get_unit_at(col, row)
        
        if self.state != GameState.PLAYER_TURN:
            return
        
        if self.selected_unit:
            # Если кликнули на допустимое перемещение
            if (col, row) in self.valid_moves and not self.selected_unit.has_moved:
                self.move_unit(self.selected_unit, (col, row))
                self.valid_moves = []
                self.valid_targets = []
                # После движения проверяем цели для атаки
                self.valid_targets = self.get_valid_targets(self.selected_unit)
                return
            
            # Если кликнули на цель для атаки
            if (col, row) in self.valid_targets and not self.selected_unit.has_attacked:
                target_unit = self.get_unit_at(col, row)
                if target_unit and target_unit.is_player != self.selected_unit.is_player:
                    self.attack(self.selected_unit, target_unit)
                    self.valid_targets = []
                    return
            
            # Отмена выбора при клике в пустоту
            if not clicked_unit or clicked_unit == self.selected_unit:
                self.selected_unit = None
                self.valid_moves = []
                self.valid_targets = []
        else:
            # Выбор юнита
            if clicked_unit and clicked_unit.is_player:
                self.selected_unit = clicked_unit
                self.valid_moves = self.get_valid_moves(clicked_unit)
                self.valid_targets = []
                self.log(f"Выбран {clicked_unit.name} ({clicked_unit.unit_class.value}, ур.{clicked_unit.level})")
    
    def draw_hex(self, col: int, row: int, color: Tuple[int, int, int], width: int = 1):
        """Рисование гекса"""
        x, y = self.hex_to_pixel(col, row)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + HEX_SIZE * math.cos(angle)
            py = y + HEX_SIZE * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(self.screen, color, points, width)
        return points
    
    def draw_unit(self, unit: Unit):
        """Рисование юнита"""
        x, y = self.hex_to_pixel(unit.position[0], unit.position[1])
        
        # Цвет фракции
        colors = {
            Faction.SILK: COLOR_NEON_PURPLE,
            Faction.FLINT: COLOR_NEON_ORANGE,
            Faction.MOON: COLOR_NEON_BLUE,
            Faction.SYNDICATE: COLOR_NEON_GOLD,
            Faction.MEOW_ZENITH: COLOR_NEON_RED,
        }
        color = colors.get(unit.faction, COLOR_TEXT)
        
        # Рисуем круг юнита
        pygame.draw.circle(self.screen, color, (x, y), 15)
        
        # Обводка для выбранного юнита
        if unit == self.selected_unit:
            pygame.draw.circle(self.screen, COLOR_TEXT, (x, y), 18, 2)
        
        # Полоска HP
        hp_width = 30
        hp_height = 4
        hp_ratio = unit.hp / unit.max_hp if unit.max_hp > 0 else 0
        hp_color = COLOR_HP_BAR if hp_ratio > 0.5 else COLOR_HP_LOW
        
        pygame.draw.rect(self.screen, (50, 50, 50), (x - hp_width//2, y - 25, hp_width, hp_height))
        pygame.draw.rect(self.screen, hp_color, (x - hp_width//2, y - 25, int(hp_width * hp_ratio), hp_height))
        
        # Иконка класса (упрощённо - первая буква)
        class_letter = unit.unit_class.value[0]
        text = self.font_small.render(class_letter, True, COLOR_BG)
        self.screen.blit(text, (x - 4, y - 4))
    
    def draw_ui(self):
        """Рисование интерфейса"""
        # Панель информации
        ui_bg = pygame.Surface((300, 200), pygame.SRCALPHA)
        ui_bg.fill((20, 20, 40, 200))
        self.screen.blit(ui_bg, (10, 10))
        
        # Информация о выбранном юните
        y_offset = 20
        if self.selected_unit:
            u = self.selected_unit
            info = [
                f"{u.name} (ур.{u.level})",
                f"Класс: {u.unit_class.value}",
                f"Фракция: {u.faction.value}",
                f"HP: {u.hp}/{u.max_hp}",
                f"Жизни: {'❤' * min(5, u.lives)}",
                f"AP: {u.ap}/{u.max_ap}",
                f"АТК: {u.get_attack_power()}",
                f"ЗАЩ: {u.get_defense_power()}",
            ]
            for line in info:
                text = self.font_small.render(line, True, COLOR_TEXT)
                self.screen.blit(text, (20, y_offset))
                y_offset += 18
        else:
            text = self.font.render("Выберите юнита", True, COLOR_TEXT)
            self.screen.blit(text, (20, y_offset))
        
        # Шкала мурчания
        pygame.draw.rect(self.screen, (50, 50, 50), (10, SCREEN_HEIGHT - 40, 200, 20))
        pygame.draw.rect(self.screen, COLOR_NEON_PURPLE, (10, SCREEN_HEIGHT - 40, int(2 * self.murr_meter), 20))
        murr_text = self.font.render(f"Мурчание: {self.murr_meter}%", True, COLOR_TEXT)
        self.screen.blit(murr_text, (220, SCREEN_HEIGHT - 40))
        
        # Лог сообщений
        log_bg = pygame.Surface((400, 200), pygame.SRCALPHA)
        log_bg.fill((20, 20, 40, 200))
        self.screen.blit(log_bg, (SCREEN_WIDTH - 410, SCREEN_HEIGHT - 210))
        
        for i, msg in enumerate(self.message_log[-8:]):
            text = self.font_small.render(msg, True, COLOR_TEXT)
            self.screen.blit(text, (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 200 + i * 22))
        
        # Индикатор хода
        turn_text = self.font_large.render(f"Ход {self.turn_number}: {self.state.value}", True, COLOR_TEXT)
        self.screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 10))
        
        # Подсказки
        hints = [
            "ЛКМ: выбор/атака/ход | ПКМ: отмена | Пробел: конец хода | ESC: выход"
        ]
        for i, hint in enumerate(hints):
            text = self.font_small.render(hint, True, (150, 150, 150))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 20))
    
    def draw_grid(self):
        """Рисование сетки"""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                hex_cell = self.hex_grid[row][col]
                
                # Базовый цвет гекса
                base_color = COLOR_GRID
                
                # Цвет террейна
                if hex_cell.terrain == "acid":
                    base_color = (50, 100, 50)
                elif hex_cell.terrain == "neon_tower":
                    base_color = (80, 50, 100)
                
                # Подсветка
                if hex_cell.is_highlighted:
                    base_color = (min(255, base_color[0] + 50), 
                                 min(255, base_color[1] + 50), 
                                 min(255, base_color[2] + 50))
                
                self.draw_hex(col, row, base_color, 1)
        
        # Подсветка доступных ходов
        for col, row in self.valid_moves:
            x, y = self.hex_to_pixel(col, row)
            pygame.draw.circle(self.screen, (100, 255, 100, 150), (x, y), 10, 2)
        
        # Подсветка целей атаки
        for col, row in self.valid_targets:
            x, y = self.hex_to_pixel(col, row)
            pygame.draw.circle(self.screen, (255, 100, 100, 150), (x, y), 12, 2)
    
    def draw(self):
        """Основной метод рисования"""
        self.screen.fill(COLOR_BG)
        
        self.draw_grid()
        
        # Рисуем юнитов
        for unit in self.units:
            self.draw_unit(unit)
        
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Игровой цикл"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.end_turn()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # ЛКМ
                        self.handle_click(pygame.mouse.get_pos())
                    elif event.button == 3:  # ПКМ
                        self.selected_unit = None
                        self.valid_moves = []
                        self.valid_targets = []
            
            self.draw()
            
            # Проверка условий победы/поражения
            players = [u for u in self.units if u.is_player]
            enemies = [u for u in self.units if not u.is_player]
            
            if not players:
                self.state = GameState.GAME_OVER
                self.log("☠️ ВЫ ПОТЕРПЕЛИ ПОРАЖЕНИЕ!")
            elif not enemies:
                self.state = GameState.VICTORY
                self.log("🎉 ПОБЕДА! Нео-Шанхай-9 спасён!")
        
        pygame.quit()

# === ЗАПУСК ===
if __name__ == "__main__":
    game = NeonClawGame()
    game.run()
