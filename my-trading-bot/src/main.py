import os
from dotenv import load_dotenv
from moomoo import *

# .envファイルを読み込む
load_dotenv()

def test_connection():
    # OpenD（ゲートウェイ）への接続設定
    # 自分のPCでOpenDを動かしている場合は 127.0.0.1
    host = os.getenv('MOOMOO_OPEND_IP', '127.0.0.1')
    port = int(os.getenv('MOOMOO_OPEND_PORT', 11111))

    # 1. 接続開始
    quote_ctx = OpenQuoteContext(host=host, port=port)
    
    # 2. 接続確認（マーケットの状態を取得してみる）
    ret, data = quote_ctx.get_global_state()
    
    if ret == RET_OK:
        print("✅ moomoo OpenD 接続成功！")
        print(data)
    else:
        print(f"❌ 接続失敗: {data}")
    
    # 3. 終了
    quote_ctx.close()

if __name__ == "__main__":
    test_connection()
    