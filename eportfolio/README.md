# eポートフォリオシステム（カルテシステム）

学生一人ひとりの日々の情報を「カルテ」として蓄積し、教員が閲覧・対話できる Web アプリケーションです。
授業「Webアプリケーション開発」で学んだ構成（Flask / Flask-WTF / Flask-SQLAlchemy / SQLite / Bootstrap）で作っています。

| ツール | 種類 | 役割 |
|---|---|---|
| Slack | フロー型 | その場のやり取り。情報は流れていく |
| eポートフォリオ | ストック型 | 記録・作品・対話を個人ごとに蓄積し、あとから振り返る |

## 機能

### 学生
- **カルテ（個人ノート）への記録**：種類は次の5つ
  - 出席（出席・遅刻・欠席・公欠）
  - 授業チャンネルへの書き込み（Slack のメッセージリンクも保存できる）
  - 未来創造PJ
  - 活動の様子
  - その他
- 記録の一覧表示、種類別の件数・出欠の集計、種類とキーワードでの絞り込み、ページ送り
- プロフィール（学籍番号・学年・**未来創造PJの配属**・自己紹介）
- **作品の登録**：ファイル（画像・PDF）と外部リンク（GitHub・YouTube など）のどちらでも可
- 教員との**対話**（カルテ全体へのメッセージ、記録や作品へのコメント）

### 教員
- 学生一覧：記録数、最終記録日、作品数、**未読メッセージ数**を表示。氏名・学籍番号・PJで検索できる
- 学生のカルテ・作品を**閲覧**する（教員は編集できない）
- 学生との**対話**（メッセージ・コメント）。既読の管理もする

## セキュリティ対策

| 脅威 | 対策 | 授業の回 |
|---|---|---|
| パスワード漏えい | `generate_password_hash`（scrypt）で保存する。8文字以上で英字と数字を両方含むことを必須にする | 5 |
| 総当たり攻撃 | 5回続けて失敗したら10分ロックする。エラーメッセージではIDとパスワードのどちらが違うかを教えない | ― |
| CSRF | すべてのPOSTを Flask-WTF の CSRF トークンで守る。ログアウトや削除もPOSTのみ | 3 |
| XSS | Jinja2 の自動エスケープを使い、`\|safe` は使わない。URLは http/https だけを許可する（`javascript:` を拒否）。CSP でインラインスクリプトを禁止する | 3 |
| SQLインジェクション | ORM（SQLAlchemy）のパラメータバインドを使う | 4, 9 |
| セッションハイジャック | `HttpOnly`、`SameSite=Lax`、`Secure`（本番）を設定する。ログイン時に `session.clear()` する（固定化対策）。30分操作がなければ自動でログアウトする | 5, 6 |
| 権限の確認漏れ（IDOR） | 他の学生のカルテ・記録・作品・ファイルは404にする。編集・削除は本人だけ。教員ページは教員だけ | ― |
| 不正なファイルのアップロード | 拡張子をホワイトリストで制限し、先頭バイトで中身も確認する。保存名はUUID、上限は10MB。ファイルは公開フォルダに置かず、権限を確認してから返す | 7 |
| 二重送信 | PRGパターンと、JavaScript でのボタン無効化 | 2, 3 |
| クリックジャッキングなど | `X-Frame-Options: DENY`、`X-Content-Type-Options: nosniff`、`Referrer-Policy` を付ける。ログイン後のページは `Cache-Control: no-store` | ― |
| 秘密鍵 | `SECRET_KEY` は環境変数から読む。未設定なら `instance/secret_key` にランダムな値を作って保存する（Git には含めない） | 6 |

## セットアップ

```bash
cd eportfolio
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### データベースの作成とアカウント

```bash
flask --app app init-db                     # テーブル作成
flask --app app create-user                 # 教員アカウントを作成（対話形式）
```

試しに動かすだけなら、サンプルデータを入れると便利です（パスワードはすべて `password123`）。

```bash
flask --app app seed-demo                   # teacher / s2522001 / s2522002
```

### 起動

```bash
python app.py                               # http://127.0.0.1:8080
```

開発中にデバッグモードを使うときは `FLASK_DEBUG=1 python app.py`（**本番では使わない**）。

### 環境変数

| 変数 | 説明 | 既定値 |
|---|---|---|
| `SECRET_KEY` | セッションの署名鍵 | `instance/secret_key` を自動生成 |
| `SIGNUP_CODE` | 設定すると、学生登録に登録コードが必要になる | 空（コード不要） |
| `SESSION_COOKIE_SECURE` | HTTPSで運用するときは `1` | `0` |
| `SESSION_IDLE_TIMEOUT` | 何秒操作がなければ自動ログアウトするか | `1800` |
| `DATABASE_URL` | DBの接続先 | `instance/eportfolio.db` |
| `UPLOAD_FOLDER` | 作品ファイルの保存先 | `instance/uploads` |

## テスト

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

認証、権限、対話と既読、ファイルアップロードの検証、XSS・CSRF対策、セッションのタイムアウトなどを確認する18件のテストです。

## ファイル構成

```
eportfolio/
├── app.py             ルーティング・設定・管理コマンド
├── models.py          User / Record / Work / Message（ORM）
├── forms.py           Flask-WTF のフォームと入力チェック
├── security.py        権限チェックのデコレータ、アップロード検証、セキュリティヘッダ
├── templates/         Jinja2 テンプレート（base.html を継承）
├── static/            style.css / script.js
├── tests/             pytest
└── instance/          DB・アップロードファイル・秘密鍵（Git に含めない）
```
