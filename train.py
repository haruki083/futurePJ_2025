def calculate_commute():
    print("=== 通学コスト・シミュレーター ===")
    
    # ユーザーからの入力
    try:
        fare = int(input("片道の運賃（円）を入力してください: "))
        teiki_price = int(input("1ヶ月の定期代（円）を入力してください: "))
        days_per_week = int(input("週に何日学校に行きますか？: "))
    except ValueError:
        print("エラー: 数字を入力してください。")
        return

    # 計算（1ヶ月を4週間として計算）
    monthly_days = days_per_week * 4
    total_normal_fare = fare * 2 * monthly_days
    diff = abs(total_normal_fare - teiki_price)

    # 結果の表示
    print("-" * 30)
    print(f"【計算結果】")
    print(f"1ヶ月の通学日数（目安）: {monthly_days}日")
    print(f"都度払いの合計額: {total_normal_fare}円")
    print(f"1ヶ月の定期代: {teiki_price}円")
    print("-" * 30)

    if total_normal_fare > teiki_price:
        print(f"★ 定期の方が 【{diff}円】 お得です！")
        print("迷わず定期を買いましょう。")
    elif total_normal_fare < teiki_price:
        print(f"★ 普通に行く方が 【{diff}円】 安いです。")
        print(f"定期を買うと損しちゃいますね。")
    else:
        print("★ どちらも同じ金額です！")
        print("買いに行く手間を考えれば定期が楽かも？")

# 実行
if __name__ == "__main__":
    calculate_commute()