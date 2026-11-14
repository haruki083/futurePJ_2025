# models.py
# eポートフォリオ（カルテ）システムのデータモデル（Flask-SQLAlchemy / ORM）
from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 日本時間（Windows でも tzdata 不要な固定オフセット）
JST = timezone(timedelta(hours=9))


def now_jst():
    """DB保存用の現在時刻（JST・タイムゾーン情報なし）"""
    return datetime.now(JST).replace(tzinfo=None)


# ---------- 定数 ----------
ROLE_STUDENT = "student"
ROLE_TEACHER = "teacher"

# 記録の種類（カルテに書く日々の情報）
CATEGORIES = [
    ("attendance", "出席"),
    ("slack", "授業チャンネルへの書き込み"),
    ("pj", "未来創造PJ"),
    ("activity", "活動の様子"),
    ("other", "その他"),
]
CATEGORY_LABELS = dict(CATEGORIES)

ATTENDANCE_STATUSES = [
    ("present", "出席"),
    ("late", "遅刻"),
    ("absent", "欠席"),
    ("excused", "公欠"),
]
ATTENDANCE_LABELS = dict(ATTENDANCE_STATUSES)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)  # ログインID
    display_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(16), nullable=False, default=ROLE_STUDENT)

    # 学生プロフィール
    student_no = db.Column(db.String(32))
    grade = db.Column(db.String(16))
    pj_assignment = db.Column(db.String(100))  # 未来創造PJの配属
    bio = db.Column(db.Text)

    # ログイン試行回数の制限（ブルートフォース対策）
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, nullable=False, default=now_jst)

    records = db.relationship("Record", back_populates="student",
                              cascade="all, delete-orphan",
                              foreign_keys="Record.student_id")
    works = db.relationship("Work", back_populates="student",
                            cascade="all, delete-orphan",
                            foreign_keys="Work.student_id")

    @property
    def is_teacher(self):
        return self.role == ROLE_TEACHER

    @property
    def is_student(self):
        return self.role == ROLE_STUDENT

    def __repr__(self):
        return f"<User {self.id}:{self.username}>"


class Record(db.Model):
    """カルテの1件の記録（出席・Slack書き込み・PJ・活動の様子など）"""
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    category = db.Column(db.String(16), nullable=False, index=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    course = db.Column(db.String(100))        # 授業名・チャンネル名・PJ名など
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    attendance_status = db.Column(db.String(16))  # category=attendance のときのみ
    link_url = db.Column(db.String(500))      # Slack のメッセージリンクなど
    created_at = db.Column(db.DateTime, nullable=False, default=now_jst)
    updated_at = db.Column(db.DateTime, nullable=False, default=now_jst, onupdate=now_jst)

    student = db.relationship("User", back_populates="records", foreign_keys=[student_id])
    messages = db.relationship("Message", back_populates="record",
                               cascade="all, delete-orphan")

    @property
    def category_label(self):
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def attendance_label(self):
        return ATTENDANCE_LABELS.get(self.attendance_status, "")

    def __repr__(self):
        return f"<Record {self.id}:{self.category}>"


class Work(db.Model):
    """学生の作品（ファイル）または外部リンク"""
    __tablename__ = "works"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    external_url = db.Column(db.String(500))
    file_name = db.Column(db.String(100))      # 保存名（UUID）
    original_name = db.Column(db.String(255))  # 表示用の元ファイル名
    file_type = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, nullable=False, default=now_jst)
    updated_at = db.Column(db.DateTime, nullable=False, default=now_jst, onupdate=now_jst)

    student = db.relationship("User", back_populates="works", foreign_keys=[student_id])
    messages = db.relationship("Message", back_populates="work",
                               cascade="all, delete-orphan")

    @property
    def is_image(self):
        return self.file_type in {"png", "jpg", "jpeg", "gif", "webp"}

    def __repr__(self):
        return f"<Work {self.id}:{self.title}>"


class Message(db.Model):
    """学生と教員の対話（カルテ全体、または特定の記録・作品へのコメント）"""
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                           nullable=False, index=True)  # どの学生のカルテか
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey("records.id", ondelete="CASCADE"))
    work_id = db.Column(db.Integer, db.ForeignKey("works.id", ondelete="CASCADE"))
    body = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime)  # 相手側（学生 or 教員）が読んだ時刻
    created_at = db.Column(db.DateTime, nullable=False, default=now_jst)

    author = db.relationship("User", foreign_keys=[author_id])
    student = db.relationship("User", foreign_keys=[student_id])
    record = db.relationship("Record", back_populates="messages")
    work = db.relationship("Work", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id}>"
