"""
UI表示やHTMLテーブル生成に関する関数
"""
from utils.time_utils import is_early_time_slot, is_regular_time_slot, is_all_regular_slots_sold_out

def generate_table_html(filtered_members, sorted_time_slots, inventory_data, member_urls, 
                        member_groups_map, sold_out_counts, crowded_time_slots, member_sales_count):
    """
    在庫情報を表示するHTMLテーブルを生成
    
    Args:
        filtered_members (list): フィルタリングされたメンバー情報リスト
        sorted_time_slots (list): ソートされた時間帯のリスト
        inventory_data (dict): メンバー名と在庫情報のマッピング
        member_urls (dict): メンバー名とURLのマップ
        member_groups_map (dict): メンバー名からグループを取得するマップ
        sold_out_counts (dict): 時間帯と完売数のマッピング
        crowded_time_slots (dict): 時間帯と混雑状態のマッピング
        member_sales_count (dict): メンバー名と売上数のマッピング
        
    Returns:
        str: 生成されたHTMLテーブル
    """
    from utils.data_loader import format_member_name
    from utils.time_utils import is_early_time_slot, is_regular_time_slot, is_all_regular_slots_sold_out
    
    # フィルター用のメンバー名リスト
    filtered_member_names = [member["name"] for member in filtered_members]
    
    # カスタムテーブルスタイルを適用したdiv要素
    html = """
    <div class="table-scroll-container">
        <table class="inventory-table">
    """
    
    # ヘッダー行
    html += "<thead><tr>"
    html += '<th class="corner-header">メンバー名</th>'
    
    # 時間帯ヘッダー
    for time_slot in sorted_time_slots:
        time_display = format_time_slot_display(time_slot)
        header_class = "time-header"
        
        if crowded_time_slots[time_slot]:
            header_class += " crowded"
            time_slot_display = f'<span class="crowded-label">{time_display}</span>'
        else:
            time_slot_display = time_display
        
        # 完売数ラベルを追加
        sold_out_count = sold_out_counts[time_slot]
        count_class = "sold-out-count crowded" if crowded_time_slots[time_slot] else "sold-out-count"
        
        html += f'<th class="{header_class}">'
        html += f'{time_slot_display}'
        html += f'<span class="{count_class}">{sold_out_count}</span>'
        html += '</th>'
    
    html += "</tr></thead>"
    
    # データ行
    html += "<tbody>"
    
    for member_name in filtered_member_names:
        member_url = member_urls.get(member_name, "#")
        member_group = member_groups_map.get(member_name, "")
        is_u17_member = (member_group == "U17")
        
        html += "<tr>"
        
        # メンバー名セル - 縦方向中央揃えのためのフレックスボックスコンテナを使用
        formatted_name = format_member_name(member_name)
        sales_count = member_sales_count[member_name]
        
        html += f'<td class="member-cell">'
        html += f'<div class="member-name-container">'
        html += f'<a href="{member_url}" target="_blank" class="member-link">{formatted_name}</a>'
        html += f'<span class="member-sales-count">{sales_count}</span>'
        html += f'</div></td>'
        
        # メンバーの時間帯ごとの状態セル
        member_data = inventory_data.get(member_name, {})
        all_regular_slots_sold = is_all_regular_slots_sold_out(member_data, sorted_time_slots)
        
        for time_slot in sorted_time_slots:
            status = member_data.get(time_slot, "")
            
            if not is_u17_member and is_early_time_slot(time_slot) and status == "×" and not all_regular_slots_sold:
                display_status = "🔒"
                status_class = "locked"
            else:
                display_status = status
                status_class = "sold-out" if status == "×" else "last-one" if status == "⚪︎" else ""
            
            html += f'<td class="status-cell {status_class}">{display_status}</td>'
        
        html += "</tr>"
    
    html += "</tbody></table></div>"
    
    # 固定ヘッダーをサポートするためのインラインCSS
    inline_css = """
    <style>
        .table-scroll-container {
            position: relative;
            width: 100%;
            overflow: auto;
            max-height: 80vh;
        }
        
        .inventory-table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            border: 1px solid #ddd;
        }
        
        .inventory-table th, 
        .inventory-table td {
            border: 1px solid #ddd;
            padding: 8px;
            background-color: white;
        }
        
        /* 時間ヘッダー (上端) */
        .time-header {
            position: sticky;
            top: 0;
            background-color: #f2f2f2 !important;
            z-index: 10;
            min-width: 65px;
            text-align: center;
        }
        
        /* メンバー名セル (左端) */
        .member-cell {
            position: sticky;
            left: 0;
            background-color: #f2f2f2 !important;
            z-index: 1;
            min-width: 120px;
            max-width: 120px;
            padding: 0 8px; /* 内側のパディングを調整 */
            height: 64px; /* 高さを固定 */
        }
        
        /* メンバー名のコンテナ - 縦方向中央揃え */
        .member-name-container {
            display: flex;
            align-items: center; /* 垂直方向中央揃え */
            justify-content: space-between; /* 名前と数字を左右に配置 */
            height: 100%;
            width: 100%;
        }
        
        /* 左上の角のセル */
        .corner-header {
            position: sticky;
            top: 0;
            left: 0;
            background-color: #f2f2f2 !important;
            z-index: 100;
            min-width: 120px;
            max-width: 120px;
            text-align: center;
        }
        
        /* 状態セル */
        .status-cell {
            text-align: center;
            font-size: 20px;
            min-width: 65px;
            vertical-align: middle;
            line-height: 1;
        }
        
        /* ステータスアイコン */
        .sold-out { color: #dc3545; }
        .last-one { color: #198754; }
        .locked { color: #6c757d; font-size: 22px; }
        
        /* ラベル */
        .crowded-label { color: #fd7e14; font-weight: bold; }
        
        .sold-out-count {
            display: block;
            font-size: 11px;
            font-weight: bold;
            background-color: #212529;
            color: white;
            padding: 2px 4px;
            border-radius: 4px;
            margin-top: 4px;
            text-align: center;
        }
        
        .sold-out-count.crowded {
            background-color: #fd7e14;
            color: black;
        }
        
        .member-sales-count {
            display: inline-block;
            font-size: 11px;
            font-weight: bold;
            background-color: #212529;
            color: white;
            padding: 2px 5px;
            border-radius: 4px;
            margin-left: 5px;
        }
        
        .member-link {
            color: #212529;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            max-width: 90px;
            word-wrap: break-word;
        }
        
        .member-link:hover {
            color: #0d6efd;
            text-decoration: underline;
        }
    </style>
    """
    
    return inline_css + html


def format_time_slot_display(time_slot):
    """
    時間枠の表示形式を「XX:XX-XX:XX」から「XX:XX」（開始時刻のみ）に変換
    
    Args:
        time_slot (str): 元の時間枠文字列（例: "15:00-15:15"）
        
    Returns:
        str: 開始時刻のみの文字列（例: "15:00"）
    """
    if '-' in time_slot:
        return time_slot.split('-')[0].strip()
    return time_slot

def format_time_slot_display(time_slot):
    """
    時間枠の表示形式を「XX:XX-XX:XX」から「XX:XX」（開始時刻のみ）に変換
    
    Args:
        time_slot (str): 元の時間枠文字列（例: "15:00-15:15"）
        
    Returns:
        str: 開始時刻のみの文字列（例: "15:00"）
    """
    if '-' in time_slot:
        return time_slot.split('-')[0].strip()
    return time_slot

def determine_crowded_time_slots(sorted_time_slots, sold_out_counts, members_sold_all_regular_slots):
    """
    混雑時間帯を判定
    
    Args:
        sorted_time_slots (list): ソートされた時間帯のリスト
        sold_out_counts (dict): 時間帯と完売数のマッピング
        members_sold_all_regular_slots (int): 18:00以降の枠をすべて売ったメンバー数
        
    Returns:
        dict: 時間帯と混雑状態のマッピング
    """
    crowded_time_slots = {}
    for time_slot in sorted_time_slots:
        if is_early_time_slot(time_slot):
            # 「15:00-15:15」〜「17:45-18:00」は特殊条件
            crowded_time_slots[time_slot] = (members_sold_all_regular_slots >= 15)
        else:
            # 通常の混雑判定: 15人以上が売り切れの場合は混雑マーク
            crowded_time_slots[time_slot] = (sold_out_counts[time_slot] >= 15)
    
    return crowded_time_slots


def count_members_sold_all_regular_slots(inventory_data, sorted_time_slots, is_all_regular_slots_sold_out):
    """
    18:00以降の枠をすべて売ったメンバー数をカウント
    
    Args:
        inventory_data (dict): メンバー名と在庫情報のマッピング
        sorted_time_slots (list): ソートされた時間帯のリスト
        is_all_regular_slots_sold_out (function): 通常時間帯が全て完売しているかチェックする関数
        
    Returns:
        int: 18:00以降の枠をすべて売ったメンバー数
    """
    members_sold_all_regular_slots = 0
    
    for m_name, m_data in inventory_data.items():
        if is_all_regular_slots_sold_out(m_data, sorted_time_slots):
            members_sold_all_regular_slots += 1
    
    return members_sold_all_regular_slots
