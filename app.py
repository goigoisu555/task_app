from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from markupsafe import Markup


app = Flask(__name__)
app.secret_key = "secret"   # flash を使うために必要（改善点1）

# -----------------------------
# DB 設定
# -----------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -----------------------------
# 共通関数（改善点2）
# -----------------------------
def parse_deadline(deadline_str):
    """YYYY-MM-DD を datetime に変換する共通関数"""
    return datetime.strptime(deadline_str, "%Y-%m-%d") if deadline_str else None

def highlight_keyword(text, keyword):
    """タイトル内の keyword を <span> で囲んで返す"""
    if not keyword:
        return text

    highlighted = text.replace(
        keyword,
        f'<span class="highlight">{keyword}</span>'
    )

    return Markup(highlighted)  # safe と同じ効果
# -----------------------------
# モデル
# -----------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=False, default=2)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 期限切れ判定
    def is_overdue(self):
        if self.deadline is None:
            return False
        return (not self.is_done) and (self.deadline < datetime.utcnow())

    # 完了トグル（改善点5）
    def toggle(self):
        self.is_done = not self.is_done

    # デバッグ用（改善点9）
    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"


# -----------------------------
# 一覧
# -----------------------------
@app.route("/")
def index():
    tasks = Task.query.order_by(
        Task.is_done.asc(),
        Task.deadline.asc().nulls_last(),
        Task.priority.asc()
    ).all()

    for task in tasks:
        task.highlighted_title = highlight_keyword(task.title, None)

    return render_template("index.html", tasks=tasks)



# -----------------------------
# 作成（改善点1,2）
# -----------------------------
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        deadline_str = request.form["deadline"]
        priority = int(request.form["priority"])

        # バリデーション（改善点1）
        if not title or len(title) > 100:
            flash("タイトルは必須で100文字以内です")
            return redirect(url_for("create"))

        deadline = parse_deadline(deadline_str)  # 改善点2

        new_task = Task(
            title=title,
            deadline=deadline,
            priority=priority
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("create.html")


# -----------------------------
# 編集（改善点1,2）
# -----------------------------
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        title = request.form["title"]
        deadline_str = request.form["deadline"]
        priority = int(request.form["priority"])

        # バリデーション（改善点1）
        if not title or len(title) > 100:
            flash("タイトルは必須で100文字以内です")
            return redirect(url_for("edit", task_id=task_id))

        task.title = title
        task.priority = priority
        task.deadline = parse_deadline(deadline_str)  # 改善点2

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit.html", task=task)

# -----------------------------
# 削除確認（POST）
# -----------------------------
@app.route("/delete_confirm/<int:task_id>")
def delete_confirm(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("delete.html", task=task)

# -----------------------------
# 削除（POST）
# -----------------------------
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


# -----------------------------
# 完了トグル（POST）改善点5
# -----------------------------
@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    task = Task.query.get_or_404(task_id)
    task.toggle()  # モデル側のメソッドを呼ぶ
    db.session.commit()
    return redirect(url_for("index"))


# -----------------------------
# 検索（改善点3）
# -----------------------------
@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return redirect(url_for("index"))

    tasks = Task.query.filter(
        Task.title.ilike(f"%{keyword}%")
    ).order_by(
        Task.is_done.asc(),
        Task.deadline.asc().nulls_last(),
        Task.priority.asc()
    ).all()

    # 🔥 ここでハイライトを適用
    for task in tasks:
        task.highlighted_title = highlight_keyword(task.title, keyword)

    return render_template("index.html", tasks=tasks, keyword=keyword)

# -----------------------------
# メイン
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
