# シフト管理アプリ

FlaskとSQLiteを用いたシンプルなシフト管理アプリです。

## 機能一覧

- ログイン（スタッフ／店長）
- シフト提出（スタッフ）
- 自分の提出一覧表示／編集／削除
- 店長による全体シフト確認

## 技術構成

- Python 3.x
- Flask
- SQLite
- HTML（Jinja2テンプレート）

## 起動方法

```bash
git clone https://github.com/ojogiridar/shift-management-app.git
cd shift-management-app
python -m venv venv
venv\Scripts\activate  # Mac/Linuxの方は source venv/bin/activate
pip install flask
python app.py
