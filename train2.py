import requests

def get_fare_from_api(from_st, to_st, api_key):
    """駅すぱあとAPIを使って運賃と定期代を取得する"""
    url = "https://api.ekispert.jp/v1/json/search/course/light"
    params = {
        "key": api_key,
        "from": from_st,
        "to": to_st,
        "type": "train"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # 経路の最初の候補を取得
        course = data['ResultSet']['Course'][0]
        
        # 運賃情報の抽出
        # Priceリストの中から、片道(Oneway)と1ヶ月定期(Teiki1)を探す
        prices = course['Price']
        oneway_fare = 0
        teiki_fare = 0
        
        for p in prices:
            if 'Oneway' in p:
                oneway_fare = int(p['Oneway'])
            if 'Teiki1' in p:
                teiki_fare = int(p['Teiki1'])
                
        return oneway_fare, teiki_fare
    except Exception as e:
        print(f"\n【エラー】データの取得に失敗しました。駅名が正しいか確認してください。")
        print(f"詳細: {e}")
        return None, None

def main():
    # --- 設定エリア ---
    # ここに届いたAPIキーを貼り付けてください
    API_KEY = "ここにAPIキーを貼り付ける" 
    # ----------------

    print("=== 自動運賃取得・通学コスト比較ツール ===")
    
    if API_KEY == "ここにAPIキーを貼り付ける":
        print("\n[!] APIキーが設定されていません。")
        print("コード内の 'API_KEY' の部分を書き換えてください。")
        return

    # 入力セクション
    from_station = input("出発駅を入力してください (例: 新宿): ")
    to_station = input("到着駅を入力してください (例: 渋谷): ")
    
    print(f"\n「{from_station}」から「{to_station}」の運賃を検索中...")
    oneway, teiki = get_fare_from_api(from_station, to_station, API_KEY)

    if oneway and teiki:
        days_per_week = int(input("週に何日学校に行きますか？ (1-7): "))
        
        # 計算（1ヶ月を4週間として計算）
        monthly_days = days_per_week * 4
        total_normal_fare = oneway * 2 * monthly_days
        diff = abs(total_normal_fare - teiki)
        
        # 損益分岐点の計算
        break_even_point = (teiki + (oneway * 2) - 1) // (oneway * 2)

        print("\n" + "="*40)
        print(f"【判定結果: {from_station} ↔ {to_station}】")
        print(f"片道運賃: {oneway}円 / 1ヶ月定期: {teiki}円")
        print(f"あなたの予定（月{monthly_days}日通学）での合計額: {total_normal_fare}円")
        print("-" * 40)

        if total_normal_fare > teiki:
            print(f"結果: 【定期券】の方が {diff}円 お得です！")
        elif total_normal_fare < teiki:
            print(f"結果: 【都度払い】の方が {diff}円 安いです。")
        else:
            print("結果: どちらも同じ金額です。")

        print(f"\n(参考: 月に {break_even_point} 日以上通学するなら、定期の方が安くなります)")
        print("="*40)

if __name__ == "__main__":
    main()