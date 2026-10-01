import streamlit as st
import pandas as pd
from datetime import date
from streamlit_calendar import calendar

# ページ基本設定
st.set_page_config(
    page_title="作業依頼書管理システム",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 擬似データベース ---
if "requests_df" not in st.session_state:
    st.session_state.requests_df = pd.DataFrame([
        {
            "id": 1,
            "依頼日": "2026-09-20",
            "工程番号": "A-101",
            "客先名": "◯◯工業株式会社",
            "作業予定日": "2026-09-28",
            "件名": "定期メンテナンス作業",
            "作成者": "山田太郎",
            "機器名称・型式": "ポンプ A-200",
            "製造番号": "SN-98765",
            "客先担当": "佐藤様",
            "作業者名": "鈴木一郎",
            "作業内容": "ベアリングの交換および動作確認作業を実施する。\n・分解清掃\n・グリスアップ\n・試運転確認",
            "備考": "安全具（ヘルメット・安全靴）着用必須",
            "連絡先": "090-1234-5678"
        }
    ])

if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

# 画面切り替え状態 ("MAIN", "PRINT")
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "MAIN"

# --- 削除確認ダイアログ ---
@st.dialog("作業依頼書の削除")
def delete_confirm_dialog(target_id):
    st.write(f"ID: **{target_id}** の作業依頼書を削除してもよろしいですか？")
    st.caption("※この操作は取り消せません。")

    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("キャンセル", use_container_width=True):
            st.rerun()
    with col_confirm:
        if st.button("削除する", type="primary", use_container_width=True):
            st.session_state.requests_df = st.session_state.requests_df[
                st.session_state.requests_df["id"] != target_id
            ].reset_index(drop=True)
            st.session_state.selected_id = None
            st.success("削除しました。")
            st.rerun()

# --- サイドバー：設定・モード切り替え ---
st.sidebar.title("設定・ログイン")
user_mode = st.sidebar.radio("モード選択", ["閲覧用", "編集用"])

is_edit_mode = False
if user_mode == "編集用":
    password = st.sidebar.text_input("編集用パスワード", type="password")
    if password == "admin123":
        is_edit_mode = True
        st.sidebar.success("編集モードでログイン中")
    else:
        st.sidebar.warning("パスワードを入力してください")

# ==========================================
# 画面3: 印刷専用ページ（完全切り離し）
# ==========================================
if st.session_state.view_mode == "PRINT":
    sel_id = st.session_state.selected_id
    df = st.session_state.requests_df
    matched = df[df['id'] == sel_id]
    target_data = matched.iloc[0].to_dict() if not matched.empty else {}

    # 印刷用CSS
    st.markdown("""
        <style>
        .print-container {
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
        }

        .sheet {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .sheet th, .sheet td {
            border: 1px solid #000;
            padding: 8px 10px;
            font-size: 11pt;
            vertical-align: middle;
        }
        .sheet th {
            background-color: #f2f2f2 !important;
            -webkit-print-color-adjust: exact;
            width: 18%;
            font-weight: bold;
            text-align: center;
        }
        .sheet td {
            width: 32%;
        }
        .sheet-title {
            text-align: center;
            font-size: 20pt;
            font-weight: bold;
            letter-spacing: 4px;
            margin-bottom: 20px;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
        }
        .multiline {
            white-space: pre-wrap;
            height: 160px;
            vertical-align: top !important;
        }

        div[data-testid="stCheckbox"] {
            display: none !important;
        }

        @media print {
            header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], iframe, div[data-testid="stCustomComponentV1"] {
                display: none !important;
            }
            .block-container {
                padding: 0 !important;
            }
            @page {
                size: A4 portrait;
                margin: 10mm;
            }
            .print-container {
                max-width: 100% !important;
                padding: 0 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    is_back_clicked = st.checkbox("back_trigger_key", key="back_trigger_key")
    if is_back_clicked:
        st.session_state.view_mode = "MAIN"
        st.rerun()

    st.components.v1.html(
        """
        <script>
        function goBack() {
            const doc = window.parent.document;
            const checkboxes = doc.querySelectorAll('input[type="checkbox"]');
            if (checkboxes.length > 0) {
                checkboxes[0].click();
            }
        }
        </script>
        <div style="max-width: 800px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; font-family: sans-serif;">
            <button onclick="goBack()" style="
                padding: 8px 16px;
                background-color: #f0f2f6;
                color: #31333F;
                border: 1px solid #d6d6d6;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                cursor: pointer;">
                ⬅️ 詳細画面に戻る
            </button>
            <button onclick="window.parent.print()" style="
                padding: 8px 20px;
                background-color: #ff4b4b;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                cursor: pointer;">
                🖨️ 今すぐ印刷する（PDF保存）
            </button>
        </div>
        """,
        height=50
    )

    st.markdown(f"""
        <div class="print-container">
            <div class="sheet-title">作 業 依 頼 書</div>
            <table class="sheet">
                <tr>
                    <th>工程番号</th>
                    <td>{target_data.get('工程番号', '')}</td>
                    <th>依頼日</th>
                    <td>{target_data.get('依頼日', '')}</td>
                </tr>
                <tr>
                    <th>客先名</th>
                    <td>{target_data.get('客先名', '')}</td>
                    <th>作成者</th>
                    <td>{target_data.get('作成者', '')}</td>
                </tr>
                <tr>
                    <th>作業予定日</th>
                    <td>{target_data.get('作業予定日', '')}</td>
                    <th>機器名称・型式</th>
                    <td>{target_data.get('機器名称・型式', '')}</td>
                </tr>
                <tr>
                    <th>件名</th>
                    <td>{target_data.get('件名', '')}</td>
                    <th>製造番号</th>
                    <td>{target_data.get('製造番号', '')}</td>
                </tr>
                <tr>
                    <th>客先担当</th>
                    <td>{target_data.get('客先担当', '')}</td>
                    <th>作業者名</th>
                    <td>{target_data.get('作業者名', '')}</td>
                </tr>
                <tr>
                    <th>連絡先</th>
                    <td colspan="3">{target_data.get('連絡先', '')}</td>
                </tr>
                <tr>
                    <th>作業内容</th>
                    <td colspan="3" class="multiline">{target_data.get('作業内容', '')}</td>
                </tr>
                <tr>
                    <th>備考</th>
                    <td colspan="3" class="multiline">{target_data.get('備考', '')}</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 画面1: 一覧画面（カレンダー／リスト）
# ==========================================
elif st.session_state.selected_id is None:
    st.title("📋 作業依頼書一覧")

    col_header1, col_header2 = st.columns([2, 1])
    with col_header1:
        view_type = st.radio("表示形式", ["📅 カレンダー表示", "📄 リスト表示"], horizontal=True, label_visibility="collapsed")
    with col_header2:
        if is_edit_mode:
            if st.button("➕ 新規作業依頼書を作成", use_container_width=True):
                st.session_state.selected_id = "NEW"
                st.rerun()

    st.divider()
    df = st.session_state.requests_df

    if view_type == "📅 カレンダー表示":
        events = []
        for _, row in df.iterrows():
            events.append({
                "id": str(row["id"]),
                "title": f"【{row['工程番号']}】{row['件名']}",
                "start": row["作業予定日"],
                "end": row["作業予定日"],
            })

        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "initialView": "dayGridMonth",
            "locale": "ja",
            "selectable": True,
        }

        cal_res = calendar(events=events, options=calendar_options, key="work_calendar")

        if cal_res.get("eventClick"):
            clicked_id = int(cal_res["eventClick"]["event"]["id"])
            st.session_state.selected_id = clicked_id
            st.rerun()

    else:
        if not df.empty:
            for idx, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"【{row['工程番号']}】{row['件名']}")
                    st.caption(f"客先名: {row['客先名']} | 作業予定日: {row['作業予定日']} | 作成者: {row['作成者']}")
                with col2:
                    if st.button("詳細を表示", key=f"btn_{row['id']}", use_container_width=True):
                        st.session_state.selected_id = row['id']
                        st.rerun()
                st.divider()

# ==========================================
# 画面2: 詳細・編集画面
# ==========================================
else:
    sel_id = st.session_state.selected_id
    df = st.session_state.requests_df

    # 画面上部操作バー
    col_back, col_del, col_print = st.columns([2, 1, 1.5])
    with col_back:
        if st.button("⬅️ 一覧に戻る", use_container_width=True):
            st.session_state.selected_id = None
            st.rerun()

    with col_del:
        # 既存データの閲覧・編集時かつ編集モード時のみ削除ボタンを表示
        if sel_id != "NEW" and is_edit_mode:
            if st.button("🗑️ 削除", use_container_width=True, type="secondary"):
                delete_confirm_dialog(sel_id)

    with col_print:
        if st.button("🖨️ A4帳票形式で印刷", use_container_width=True, type="primary"):
            st.session_state.view_mode = "PRINT"
            st.rerun()

    st.markdown("---")

    if sel_id == "NEW":
        st.title("📝 新規作業依頼書の作成")
        target_data = {}
    else:
        st.title(f"📄 作業依頼書 (ID: {sel_id})")
        matched = df[df['id'] == sel_id]
        target_data = matched.iloc[0].to_dict() if not matched.empty else {}

    disabled = not is_edit_mode if sel_id != "NEW" else False

    # --------------------------------------------------
    # 画面操作用フォーム
    # --------------------------------------------------
    with st.form("request_form"):
        st.components.v1.html(
            """
            <script>
            const doc = window.parent.document;
            doc.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
                    e.preventDefault();
                    return false;
                }
            }, true);
            </script>
            """,
            height=0,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            process_num = st.text_input("工程番号", value=target_data.get("工程番号", ""), disabled=disabled)
            customer = st.text_input("客先名", value=target_data.get("客先名", ""), disabled=disabled)
            work_date = st.date_input("作業予定日", value=pd.to_datetime(target_data.get("作業予定日", date.today())), disabled=disabled)
            subject = st.text_input("件名", value=target_data.get("件名", ""), disabled=disabled)
            request_date = st.date_input("依頼日", value=pd.to_datetime(target_data.get("依頼日", date.today())), disabled=disabled)
            creator = st.text_input("作成者", value=target_data.get("作成者", ""), disabled=disabled)

        with col_b:
            machine_name = st.text_input("機器名称・型式", value=target_data.get("機器名称・型式", ""), disabled=disabled)
            serial_num = st.text_input("製造番号", value=target_data.get("製造番号", ""), disabled=disabled)
            customer_contact = st.text_input("客先担当", value=target_data.get("客先担当", ""), disabled=disabled)
            worker_name = st.text_input("作業者名", value=target_data.get("作業者名", ""), disabled=disabled)
            contact = st.text_input("連絡先", value=target_data.get("連絡先", ""), disabled=disabled)

        work_content = st.text_area("作業内容", value=target_data.get("作業内容", ""), height=150, disabled=disabled)
        remarks = st.text_area("備考", value=target_data.get("備考", ""), height=100, disabled=disabled)

        btn_label = "保存する" if is_edit_mode else "閉じる（一覧へ戻る）"
        submitted = st.form_submit_button(btn_label, use_container_width=True)

        if submitted:
            if is_edit_mode:
                new_data = {
                    "id": sel_id if sel_id != "NEW" else (df["id"].max() + 1 if not df.empty else 1),
                    "依頼日": str(request_date),
                    "工程番号": process_num,
                    "客先名": customer,
                    "作業予定日": str(work_date),
                    "件名": subject,
                    "作成者": creator,
                    "機器名称・型式": machine_name,
                    "製造番号": serial_num,
                    "客先担当": customer_contact,
                    "作業者名": worker_name,
                    "作業内容": work_content,
                    "備考": remarks,
                    "連絡先": contact
                }

                if sel_id == "NEW":
                    st.session_state.requests_df = pd.concat(
                        [st.session_state.requests_df, pd.DataFrame([new_data])], 
                        ignore_index=True
                    )
                else:
                    idx = st.session_state.requests_df[st.session_state.requests_df["id"] == sel_id].index
                    if not idx.empty:
                        for key, val in new_data.items():
                            st.session_state.requests_df.loc[idx[0], key] = val

                st.success("保存しました！")

            st.session_state.selected_id = None
            st.rerun()