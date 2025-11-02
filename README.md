# 坦克大战 · Flask + Canvas 前端

一个采用 Flask 提供后端接口、原生 JavaScript/Canvas 渲染前端的复古坦克大战项目。新版界面使用霓虹 HUD，全屏画布，并内置多张难度递增的关卡与 AI 波次。

> **亮点速览**
> - 4 个逐级升级的关卡版图（训练场 / 城区 / 迷宫 / 要塞）
> - 统一的 API 服务 (`/api`) 驱动地图、敌人波次、难度数据
> - 霓虹主题 UI，主菜单、关卡列表、游戏内 HUD 完全响应式
> - 可通过 URL 参数或关卡列表直接跳转指定关卡 (`/game?level=3`)

---

## 目录

1. [功能特性](#功能特性)  
2. [项目结构](#项目结构)  
3. [环境准备](#环境准备)  
4. [快速启动](#快速启动)  
5. [关卡与难度](#关卡与难度)  
6. [操作方式](#操作方式)  
7. [API 概览](#api-概览)  
8. [自定义指南](#自定义指南)  
9. [常见问题](#常见问题)

---

## 功能特性

- **全屏游戏画面**：Canvas 画布自适应窗口（带安全边距），HUD 悬浮在画布上方显示生命、波次、FPS 等信息。
- **多关卡设计**：后端以 `LevelConfig` 数据类集中管理关卡，布局函数会生成不同的砖墙 / 草地 / 水域 / 钢板组合。
- **难度递进**：每关拥有不同的敌人波次、最大同时出现数量和地图限制，适合逐步挑战。
- **UI 升级**：主菜单、首页、关卡列表等采用霓虹紫配色的玻璃拟态风格，适配桌面与移动浏览器。
- **API 驱动**：所有前端渲染依赖 `/api/level/<id>` 返回的地图与波次数据，方便后续迭代或与其他客户端整合。

---

## 项目结构

```
tankedazhan-main/
├── requirements.txt        # 后端依赖
├── web/
│   ├── app.py              # Flask 主应用及路由
│   ├── api.py              # 关卡、敌人相关 API
│   ├── static/styles.css   # 全局样式与霓虹 HUD 主题
│   └── templates/
│       ├── index.html      # 启动控制台
│       ├── main_menu.html  # 主菜单大厅
│       ├── levels.html     # 关卡列表
│       ├── game.html       # 游戏页面（Canvas）
│       └── ...             # 其他辅助页面（设置 / 帮助 / 关于等）
└── ...
```

---

## 环境准备

1. **Python**：3.9+（项目在 Windows Anaconda 环境下验证）。  
2. **pip**：已包含在大部分 Python 发行版中。  
3. **浏览器**：推荐 Chrome / Edge / Firefox 最新版本。

可选：建议创建虚拟环境隔离依赖。

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
source .venv/bin/activate     # macOS / Linux
```

---

## 快速启动

```bash
pip install -r requirements.txt
python -m web.app
```

默认监听 `http://127.0.0.1:5000/`，主要入口：

- `http://127.0.0.1:5000/`          – 启动控制台  
- `http://127.0.0.1:5000/main_menu` – 主菜单  
- `http://127.0.0.1:5000/levels`    – 关卡列表  
- `http://127.0.0.1:5000/game`      – 默认加载第 1 关  
- `http://127.0.0.1:5000/game?level=3` – 指定关卡  
- `http://127.0.0.1:5000/api/levels` – API 关卡索引  
- `http://127.0.0.1:5000/api/level/2` – 关卡 2 详细数据

若需生产部署，可使用 `waitress` 或其他 WSGI 服务器（配置在 `requirements.txt` 中）。

---

## 关卡与难度

`web/api.py` 中定义了四个关卡，概览如下：

| 关卡 | 难度 | 地图特点 | 敌人总数 | 最大同屏 | 波次 | 描述 |
|------|------|----------|----------|----------|------|------|
| 1 | Easy    | 十字形砖墙，左上草地、右下水塘 | 9  | 3 | 2 | 新手训练，熟悉操作与掩体 |
| 2 | Normal  | “USRCOR” 字样城区，水渠＋草地区隔 | 13 | 4 | 3 | 城区巷战，多兵种混编 |
| 3 | Hard    | 迷宫砖墙，中部水池、草地隐蔽点 | 20 | 5 | 4 | 需要精准走位与火力管理 |
| 4 | Extreme | 护城河要塞，钢板堡垒＋草地缓冲 | 26 | 6 | 5 | 多轮重装 / 特殊坦克，总决战 |

每关布局由独立函数生成，方便进一步自定义或新增关卡。

---

## 操作方式

- **移动**：`W A S D` 或 方向键
- **射击**：`J` 或 空格键
- **暂停**：`Esc`
- **重启**：`R`

HUD 顶部展示生命、分数、关卡编号、敌人剩余、波次、FPS；底部提示当前按键状态與常用快捷键。

---

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/levels` | 返回全部关卡摘要（名称、难度、波次、敌人数等） |
| `GET` | `/api/level/<id>` | 返回指定关卡的地图网格、出生点、敌人波次配置 |
| `GET` | `/api/enemy_types` | 敌人类型参数（速度、生命、射速、尺寸、颜色） |
| `POST` | `/api/progress` | 占位接口，未来可用于存档 |

`/api/level/<id>` 返回格式示例（局部）：

```json
{
  "id": 2,
  "name": "城区行动",
  "difficulty": "normal",
  "size": [45, 39],
  "tile_size": 16,
  "tiles": [["steel", "steel", ...], ...],
  "player_spawn": [4, 34],
  "base": [22, 37],
  "enemy_spawns": [[2, 2], [22, 2], [42, 2]],
  "enemy_waves": [
    {"type": "normal", "count": 6, "interval": 2.0},
    {"type": "fast", "count": 4, "interval": 1.6},
    {"type": "heavy", "count": 3, "interval": 2.8}
  ],
  "max_enemies_on_screen": 4,
  "total_enemies": 13
}
```

---

## 自定义指南

1. **新增关卡**  
   - 在 `web/api.py` 中实现新的布局函数或编辑现有函数。  
   - 将新关卡添加到 `LEVELS` 字典，指定 `layout_builder`、波次、出生点等。

2. **修改敌人类型**  
   - 更新 `/api/enemy_types` 中的参数（速度、生命、射速、颜色等）。  
   - 游戏前端会自动使用这些数据驱动敌人 AI。

3. **调整 HUD 或主题**  
   - 编辑 `web/static/styles.css`，更改颜色变量、阴影、玻璃拟态效果。  
   - Canvas 中的坦克绘制在 `game.html` 脚本内。

4. **接入其他客户端**  
   - 直接调用 `/api/level/<id>` 获取地图和波次数据，方便移植到 Unity、移动端或其他图形前端。

---

## 常见问题

1. **运行时报 `ModuleNotFoundError: flask_cors`**  
   - 说明依赖未安装，执行 `pip install -r requirements.txt`。

2. **所有关卡画面看起来一样**  
   - 请从 `http://127.0.0.1:5000/levels` 进入，再跳转到 `/game?level=<ID>`。  
   - 如果从主菜单“开始游戏”进入，会默认打开第 1 关。

3. **如何调整画布大小/窗口自适应？**  
   - `game.html` 中的 `resizeViewport` 会依据关卡地图尺寸 + 浏览器窗口计算画布大小，可修改 `VIEWPORT_PADDING` 或逻辑以实现不同策略。

4. **如何调试关卡布局？**  
   - 可使用 Flask 的 `app.test_client()` 调用 `/api/level/<id>`，检查 `tiles` 阵列。  
   - 或在前端 Canvas 中添加可视化辅助（例如渲染网格、坐标等）。

---

欢迎继续扩展音效、道具系统、多人模式或存档功能。如果在使用过程中遇到问题或需要新特性，随时提出 Issue 或 PR！
