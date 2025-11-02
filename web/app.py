from __future__ import annotations

import os
from flask import Flask, render_template
from .api import api
from flask_cors import CORS

# 🎮 游戏链接（复制到浏览器打开）：
# 首页: http://127.0.0.1:5000/
# 游戏: http://127.0.0.1:5000/game
# 关卡: http://127.0.0.1:5000/levels  
# 健康: http://127.0.0.1:5000/health


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    # 让 jsonify 直接输出中文而不是 \uXXXX
    try:
        app.json.ensure_ascii = False  # Flask 3.x
    except Exception:
        app.config["JSON_AS_ASCII"] = False  # 兼容旧版本
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(api)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/game")
    def game():
        return render_template("game.html")

    @app.route("/levels")
    def levels():
        return render_template("levels.html")

    @app.route("/main_menu")
    def main_menu():
        return render_template("main_menu.html")

    @app.route("/settings")
    def settings():
        return render_template("settings.html")

    @app.route("/help")
    def help():
        return render_template("help.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    # 支持从环境变量切换 host/port 与调试模式
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app = create_app()
    app.run(host=host, port=port, debug=debug)


