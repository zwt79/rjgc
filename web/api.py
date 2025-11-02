from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__, url_prefix="/api")


@dataclass(frozen=True)
class Wave:
    type: str
    count: int
    interval: float


@dataclass(frozen=True)
class LevelConfig:
    id: int
    name: str
    description: str
    difficulty: str
    grid: Tuple[int, int]
    tile_size: int
    player_spawn: Tuple[int, int]
    base: Tuple[int, int]
    enemy_spawns: List[Tuple[int, int]]
    max_on_screen: int
    waves: List[Wave]
    layout_builder: str  # key for layout function


def safe_assign(tiles: List[List[str]], x: int, y: int, value: str) -> None:
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    if 0 <= y < height and 0 <= x < width:
        tiles[y][x] = value


def build_training_layout(width: int, height: int) -> List[List[str]]:
    tiles = [["ground" for _ in range(width)] for _ in range(height)]
    for x in range(width):
        tiles[0][x] = tiles[height - 1][x] = "steel"
    for y in range(height):
        tiles[y][0] = tiles[y][width - 1] = "steel"

    center_x, center_y = width // 2, height // 2

    # 十字形砖墙，用于教学掩体
    for x in range(3, width - 3):
        if x % 2 == 0:
            tiles[center_y][x] = "brick"
    for y in range(3, height - 6):
        if y % 2 == 0:
            tiles[y][center_x] = "brick"

    # 左上草地区域（安全区）
    for y in range(2, center_y - 2):
        for x in range(2, center_x - 3):
            tiles[y][x] = "grass"

    # 右下水塘，用于教学绕行
    for y in range(center_y + 2, min(height - 2, center_y + 6)):
        for x in range(center_x + 2, min(width - 2, center_x + 6)):
            tiles[y][x] = "water"

    # 底部训练靶场（稀疏砖块）
    for x in range(4, width - 4, 4):
        tiles[height - 6][x] = "brick"

    return tiles


def build_letters_layout(width: int, height: int, word: str) -> List[List[str]]:
    tiles = [["ground" for _ in range(width)] for _ in range(height)]
    for x in range(width):
        tiles[0][x] = tiles[height - 1][x] = "steel"
    for y in range(height):
        tiles[y][0] = tiles[y][width - 1] = "steel"

    letters = {
        "C": [" ###", "#   ", "#   ", "#   ", " ###"],
        "U": ["#  #", "#  #", "#  #", "#  #", " ## "],
        "R": ["### ", "#  #", "### ", "# # ", "#  #"],
        "S": [" ###", "#   ", " ## ", "   #", " ###"],
        "O": [" ## ", "#  #", "#  #", "#  #", " ## "],
        "A": [" ## ", "#  #", "####", "#  #", "#  #"],
        "N": ["#  #", "## #", "# ##", "#  #", "#  #"],
        "X": ["#  #", " ## ", " ## ", " ## ", "#  #"],
        "L": ["#   ", "#   ", "#   ", "#   ", "####"],
        "I": ["####", " ## ", " ## ", " ## ", "####"],
    }
    letter_width = 5
    total_width = len(word) * letter_width - 1
    start_x = max(2, (width - total_width) // 2)
    start_y = max(4, height // 4)
    for i, letter in enumerate(word):
        pattern = letters.get(letter.upper())
        if not pattern:
            continue
        letter_x = start_x + i * letter_width
        for row, line in enumerate(pattern):
            for col, char in enumerate(line):
                if char == "#":
                    x = letter_x + col
                    y = start_y + row
                    if 0 <= x < width and 0 <= y < height:
                        tiles[y][x] = "brick"

    # 城区街道：纵横道路以钢板和草地区区隔
    for x in range(4, width - 4, 8):
        for y in range(2, height - 2):
            tiles[y][x] = "steel"
    for y in range(height // 2, height - 3, 4):
        for x in range(3, width - 3):
            if tiles[y][x] == "ground":
                tiles[y][x] = "grass"

    # 水渠分隔
    canal_start = max(3, start_y - 3)
    for x in range(6, width - 6):
        tiles[canal_start][x] = "water"
        tiles[canal_start + 1][x] = "water"
    for x in range(8, width - 8, 10):
        safe_assign(tiles, x, canal_start, "ground")
        safe_assign(tiles, x, canal_start + 1, "ground")

    return tiles


def build_maze_layout(width: int, height: int) -> List[List[str]]:
    tiles = [["ground" for _ in range(width)] for _ in range(height)]
    for x in range(width):
        tiles[0][x] = tiles[height - 1][x] = "steel"
    for y in range(height):
        tiles[y][0] = tiles[y][width - 1] = "steel"

    # 构建规则迷宫：偶数列/行布满砖墙，仅偶尔保留通路
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            if x % 4 == 0 or y % 4 == 0:
                tiles[y][x] = "brick"

    # 开口入口
    for x in range(2, width - 2, 6):
        tiles[2][x] = "ground"
        tiles[height - 3][x] = "ground"
    for y in range(2, height - 2, 6):
        tiles[y][2] = "ground"
        tiles[y][width - 3] = "ground"

    # 草地隐藏路径 + 水塘区域
    for y in range(5, height - 5, 6):
        for x in range(5, width - 5, 6):
            tiles[y][x] = "grass"
    for y in range(height // 2 - 3, height // 2 + 3):
        for x in range(width // 2 - 6, width // 2 + 6):
            if (x + y) % 2 == 0:
                tiles[y][x] = "water"

    return tiles


def build_fortress_layout(width: int, height: int) -> List[List[str]]:
    tiles = [["ground" for _ in range(width)] for _ in range(height)]
    for x in range(width):
        tiles[0][x] = tiles[height - 1][x] = "steel"
    for y in range(height):
        tiles[y][0] = tiles[y][width - 1] = "steel"

    # 前线钢板墙阵列
    for x in range(4, width - 4, 4):
        for y in range(4, height // 2):
            tiles[y][x] = "steel"

    # 外围砖墙带
    for y in range(height // 2, height - 6):
        for x in range(3, width - 3):
            if (x + y) % 3 == 0:
                tiles[y][x] = "brick"

    # 护城河包围基地
    moat_inner_x1, moat_inner_x2 = 8, width - 8
    moat_inner_y1, moat_inner_y2 = height // 2 + 2, height - 8
    for y in range(moat_inner_y1, moat_inner_y2):
        safe_assign(tiles, moat_inner_x1, y, "water")
        safe_assign(tiles, moat_inner_x2, y, "water")
    for x in range(moat_inner_x1, moat_inner_x2 + 1):
        safe_assign(tiles, x, moat_inner_y1, "water")
        safe_assign(tiles, x, moat_inner_y2, "water")
    for offset in range(-2, 3):
        safe_assign(tiles, (width // 2) + offset, moat_inner_y1, "ground")
        safe_assign(tiles, (width // 2) + offset, moat_inner_y2, "ground")
        safe_assign(tiles, moat_inner_x1 + offset + 2, (height // 2), "ground")
        safe_assign(tiles, moat_inner_x2 - offset - 2, (height // 2), "ground")

    # 护城河内的钢板堡垒
    for y in range(moat_inner_y1 + 2, moat_inner_y2 - 1, 3):
        for x in range(moat_inner_x1 + 2, moat_inner_x2 - 1, 5):
            safe_assign(tiles, x, y, "steel")

    # 草地缓冲区
    for y in range(moat_inner_y1 + 1, moat_inner_y2):
        for x in range(moat_inner_x1 + 1, moat_inner_x2):
            if tiles[y][x] == "ground" and (x + y) % 4 == 0:
                tiles[y][x] = "grass"

    return tiles


LAYOUT_BUILDERS = {
    "training": build_training_layout,
    "letters": lambda w, h: build_letters_layout(w, h, "USRCOR"),
    "maze": build_maze_layout,
    "fortress": build_fortress_layout,
}

LEVELS: Dict[int, LevelConfig] = {
    1: LevelConfig(
        id=1,
        name="训练关",
        description="基础动作演练，开放地形，敌人分批出现。",
        difficulty="easy",
        grid=(32, 26),
        tile_size=16,
        player_spawn=(4, 22),
        base=(16, 24),
        enemy_spawns=[(2, 2), (16, 2), (30, 2)],
        max_on_screen=3,
        waves=[
            Wave("normal", 6, 2.2),
            Wave("fast", 3, 2.0),
        ],
        layout_builder="training",
    ),
    2: LevelConfig(
        id=2,
        name="城区行动",
        description="街道狭窄，砖墙拼成 USRCOR，敌人混编突袭。",
        difficulty="normal",
        grid=(45, 39),
        tile_size=16,
        player_spawn=(4, 34),
        base=(22, 37),
        enemy_spawns=[(2, 2), (22, 2), (42, 2)],
        max_on_screen=4,
        waves=[
            Wave("normal", 6, 2.0),
            Wave("fast", 4, 1.6),
            Wave("heavy", 3, 2.8),
        ],
        layout_builder="letters",
    ),
    3: LevelConfig(
        id=3,
        name="迷宫突围",
        description="迷宫式砖墙，狭窄通道考验走位与火力。",
        difficulty="hard",
        grid=(48, 42),
        tile_size=16,
        player_spawn=(6, 36),
        base=(24, 39),
        enemy_spawns=[(6, 2), (24, 2), (42, 2), (24, 10)],
        max_on_screen=5,
        waves=[
            Wave("fast", 6, 1.4),
            Wave("normal", 8, 1.6),
            Wave("heavy", 4, 2.4),
            Wave("special", 2, 3.0),
        ],
        layout_builder="maze",
    ),
    4: LevelConfig(
        id=4,
        name="要塞决战",
        description="敌军要塞严密防守，钢板墙与水域双重封锁。",
        difficulty="extreme",
        grid=(52, 44),
        tile_size=16,
        player_spawn=(8, 38),
        base=(26, 41),
        enemy_spawns=[(6, 2), (26, 2), (46, 2), (26, 12)],
        max_on_screen=6,
        waves=[
            Wave("fast", 6, 1.2),
            Wave("heavy", 6, 2.0),
            Wave("special", 4, 2.5),
            Wave("heavy", 6, 1.8),
            Wave("special", 4, 2.0),
        ],
        layout_builder="fortress",
    ),
}


@api.get("/levels")
def list_levels():
    data = [
        {
            "id": level.id,
            "name": level.name,
            "description": level.description,
            "waves": len(level.waves),
            "enemies": sum(w.count for w in level.waves),
            "max_on_screen": level.max_on_screen,
            "difficulty": level.difficulty,
        }
        for level in LEVELS.values()
    ]
    return jsonify(data)


@api.post("/progress")
def save_progress():
    body = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "echo": body})


@api.get("/level/<int:level_id>")
def get_level(level_id: int):
    level = LEVELS.get(level_id)
    if not level:
        return jsonify({"error": "level_not_found"}), 404

    width, height = level.grid
    builder = LAYOUT_BUILDERS[level.layout_builder]
    tiles = builder(width, height)

    # 基地防护
    base_x, base_y = level.base
    for dx in (-1, 0, 1):
        x = base_x + dx
        top_y = base_y - 1
        bottom_y = base_y + 1
        if 0 <= x < width and 0 <= top_y < height:
            tiles[top_y][x] = "steel"
        if 0 <= x < width and 0 <= bottom_y < height:
            tiles[bottom_y][x] = "steel"
    for dx in (-2, -1, 1, 2):
        x = base_x + dx
        if 0 <= x < width and 0 <= base_y < height:
            tiles[base_y][x] = "steel"

    enemy_waves = [
        {"type": wave.type, "count": wave.count, "interval": wave.interval}
        for wave in level.waves
    ]

    data = {
        "id": level.id,
        "name": level.name,
        "description": level.description,
        "size": [width, height],
        "tile_size": level.tile_size,
        "difficulty": level.difficulty,
        "tiles": tiles,
        "player_spawn": list(level.player_spawn),
        "enemy_spawns": [list(spawn) for spawn in level.enemy_spawns],
        "base": list(level.base),
        "enemy_waves": enemy_waves,
        "max_enemies_on_screen": level.max_on_screen,
        "total_enemies": sum(w["count"] for w in enemy_waves),
    }
    return jsonify(data)


@api.get("/enemy_types")
def get_enemy_types():
    types = {
        "normal": {
            "name": "普通坦克",
            "speed": 60,
            "health": 1,
            "fire_rate": 1.0,
            "color": "#ef4444",
            "size": 16,
        },
        "fast": {
            "name": "快速坦克",
            "speed": 100,
            "health": 1,
            "fire_rate": 1.5,
            "color": "#f97316",
            "size": 14,
        },
        "heavy": {
            "name": "重装坦克",
            "speed": 40,
            "health": 2,
            "fire_rate": 0.8,
            "color": "#6b7280",
            "size": 20,
        },
        "special": {
            "name": "特殊坦克",
            "speed": 80,
            "health": 1,
            "fire_rate": 2.0,
            "color": "#8b5cf6",
            "size": 18,
        },
    }
    return jsonify(types)
