# security.py
# 認証・認可・アップロード検証などセキュリティ関連の共通処理
from functools import wraps

from flask import abort, flash, g, redirect, url_for

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf"}

# ファイル先頭のバイト列（マジックナンバー）で中身を確認する
# 拡張子だけを偽装したファイル（例: HTMLを .png にしたもの）を拒否するため
_SIGNATURES = {
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "gif": [b"GIF87a", b"GIF89a"],
    "pdf": [b"%PDF-"],
}

MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "pdf": "application/pdf",
}


def get_extension(filename):
    """元のファイル名から拡張子を取り出す（日本語ファイル名でも動くよう secure_filename の前に行う）"""
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    return ext if ext in ALLOWED_EXTENSIONS else None


def content_matches_extension(stream, ext):
    """アップロードされたファイルの先頭バイトが拡張子と一致するか"""
    head = stream.read(16)
    stream.seek(0)
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    return any(head.startswith(sig) for sig in _SIGNATURES.get(ext, []))


# ---------- 認可デコレータ ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            flash("ログインしてください。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def teacher_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user.is_teacher:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def student_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user.is_student:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def can_view_student(user, student_id):
    """そのカルテを見てよいか：本人 または 教員"""
    return user is not None and (user.is_teacher or user.id == student_id)


# ---------- HTTPセキュリティヘッダ ----------
CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)


def set_security_headers(response):
    response.headers.setdefault("Content-Security-Policy", CSP)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    # ログイン後のページをブラウザや共有PCにキャッシュさせない
    if g.get("user") is not None:
        response.headers.setdefault("Cache-Control", "no-store")
    return response
