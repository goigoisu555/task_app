# Flask Task Management App

## 概要

Flask と SQLAlchemy を用いて作成したシンプルなタスク管理アプリです。
CRUD操作に加え、期限・優先度・完了状態を管理できます。

---

## 機能

* タスクの作成 / 編集 / 削除
* 完了・未完了の切り替え（トグル）
* 優先度（高・中・低）の設定
* 期限の設定
* 期限切れタスクの判定・表示
* タスクの並び替え（未完了 → 期限順 → 優先度）

---

## 使用技術

* Python
* Flask
* SQLAlchemy
* SQLite

---

## ディレクトリ構成

```
task_app/
├── app.py
├── templates/
├── static/
├── instance/        # DB（Git管理外）
├── venv/            # 仮想環境（Git管理外）
├── .gitignore
├── requirements.txt
└── README.md
```

---

## セットアップ方法

```bash
git clone <リポジトリURL>
cd task_app

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## データベース作成

```bash
python
```

```python
from app import app, db
with app.app_context():
    db.create_all()
```

---

## 起動方法

```bash
python app.py
```

ブラウザで以下にアクセス：

```
http://127.0.0.1:5001/
```

---

## 工夫した点

* `updated_at` を `onupdate` で自動更新する設計
* モデルにロジック（期限切れ判定など）を持たせた
* NULLを考慮した期限処理
* 表示ロジックとデータロジックの分離を意識

---

## 今後の改善案

* 検索機能（タイトルの部分一致）
* フィルタ機能（未完了 / 完了）
* ユーザー認証機能（ログイン）
* UI改善

---

## 注意事項

* `venv/` や `instance/` は `.gitignore` によりGit管理対象外です
* 初回起動時は必ずデータベースを作成してください

```
```
