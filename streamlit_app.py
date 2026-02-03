import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. 디자인 설정 (모바일 최적화 + 강제 화이트)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="철근 전문가", page_icon="🏗️", layout="centered")

hide_st_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            
            .block-container {
                padding-top: 1rem;
                padding-bottom: 5rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            /* 모든 글씨 강제 백색 */
            html, body, [class*="css"], div, span, p, label, h1, h2, h3, h4, h5, h6 {
                font-family: 'Noto Sans KR', sans-serif;
                color: #ffffff !important;
            }
            
            .stApp { background-color: #1a1a1a; }
            
            /* 입력창 스타일 */
            .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
                background-color: #333333 !important;
                color: #ffffff !important;
                font-weight: bold;
                border: 1px solid #555555;
            }
            
            /* 탭 스타일 */
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #333333;
                border-radius: 4px;
                padding: 10px 20px;
                color: #cccccc;
            }
            .stTabs [aria-selected="true"] {
                background-color: #0085ff !important;
                color: #ffffff !important;
            }

            /* 버튼 스타일 */
            div.stButton > button {
                background-color: #0085ff;
                color: white !important;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                padding: 15px 0;
                margin-top: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }
            
            /* 결과 박스 */
            .result-box {
                background-color: #262626;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #444;
                border-left: 6px solid #0085ff;
                margin-top: 20px;
            }
            
            #MainMenu, footer, header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 데이터 (단위중량표 - KS D 3504)
# -----------------------------------------------------------------------------
unit_weights = {
    "D10": 0.560, "D13": 0.995, "D16": 1.560, "D19": 2.250, 
    "D22": 3.040, "D25": 3.980, "D29": 5.040, "D32": 6.230
}

# -----------------------------------------------------------------------------
# 3. 타이틀
# -----------------------------------------------------------------------------
st.markdown("<h3 style='text-align: center;'>🏗️ 철근 마스터</h3>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 탭 구성 (기능 분리)
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["⚖️ 중량 산출", "📏 이음/정착"])

# =============================================================================
# TAB 1: 중량 산출기 (적산 기능 포함)
# =============================================================================
with tab1:
    if 'rebar_list' not in st.session_state:
        st.session_state.rebar_list = []

    c1, c2 = st.columns([1, 1.5])
    with c1:
        rebar_dia = st.selectbox("철근 규격", list(unit_weights.keys()))
    with c2:
        unit_w_val = unit_weights[rebar_dia]
        st.markdown(f"<div style='padding-top:35px; color:#cccccc !important; font-size:14px;'>단위중량: {unit_w_val} kg/m</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        rb_len = st.number_input("길이 (m)", value=8.0, step=0.5)
    with c4:
        rb_qty = st.number_input("수량 (가닥)", value=10, step=10)

    # 추가 버튼
    if st.button("➕ 리스트 추가"):
        w_kg = rb_len * rb_qty * unit_w_val
        st.session_state.rebar_list.append({
            "규격": rebar_dia,
            "길이": rb_len,
            "수량": rb_qty,
            "중량(kg)": round(w_kg, 1)
        })
        st.toast("추가 완료!")

    # 리스트 출력
    st.write("---")
    if len(st.session_state.rebar_list) > 0:
        df = pd.DataFrame(st.session_state.rebar_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        total_kg = df["중량(kg)"].sum()
        total_ton = total_kg / 1000
        
        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 16px;">총 중량 합계</div>
            <div style="font-size: 32px; font-weight:bold; color:#0085ff !important; margin: 5px 0;">
                {total_ton:.3f} Ton
            </div>
            <div style="font-size: 14px; color:#cccccc !important;">({total_kg:,.1f} kg)</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ 초기화", type="secondary"):
            st.session_state.rebar_list = []
            st.rerun()
    else:
        st.info("규격과 수량을 입력하고 추가해주세요.")


# =============================================================================
# TAB 2: 이음/정착 길이 계산기 (간이 계산)
# =============================================================================
with tab2:
    st.markdown("##### 📐 인장 이음/정착 길이 (일반)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        fck = st.selectbox("콘크리트 (fck)", [21, 24, 27, 30, 35, 40], index=1) # 24MPa 기본
    with col_b:
        fy = st.selectbox("철근 강도 (fy)", ["SD400", "SD500", "SD600"], index=0) # SD400 기본
        
    target_dia = st.selectbox("철근 규격 선택", list(unit_weights.keys()))
    
    # 계산 로직 (KDS 14 20 간이식 - 일반적인 보정계수 1.0 가정)
    # 기본정착길이 Ld = (0.6 * fy / sqrt(fck)) * db
    fy_val = int(fy.replace("SD", ""))
    db_map = {"D10":9.53, "D13":12.7, "D16":15.9, "D19":19.1, "D22":22.2, "D25":25.4, "D29":28.6, "D32":31.8}
    db = db_map[target_dia]
    
    # 인장정착길이 (Ld) 계산
    raw_Ld = (0.6 * fy_val * db) / (fck ** 0.5)
    
    # 최소 기준 적용 (300mm 이상)
    Ld = max(300, raw_Ld)
    
    # B급 이음 (1.3 Ld) - 현장에서 가장 많이 씀
    splice_B = Ld * 1.3
    
    # 10mm 단위 올림 처리 (현장 관례)
    Ld_final = (int(Ld) // 10 + 1) * 10
    splice_final = (int(splice_B) // 10 + 1) * 10

    st.markdown(f"""
    <div class="result-box">
        <div style="margin-bottom: 10px; font-size: 18px; font-weight:bold;">
            {fy} / {fck}MPa / {target_dia}
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>기본 정착 (Ld)</span>
            <span style="color:#0085ff !important; font-weight:bold; font-size:20px;">{Ld_final:,} mm</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span>B급 이음 (1.3 Ld)</span>
            <span style="color:#ff4b4b !important; font-weight:bold; font-size:20px;">{splice_final:,} mm</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.info("💡 위 계산은 '일반 보정계수(1.0)'를 적용한 약산식입니다. 정확한 구조검토용 값은 도면의 일반주기사항(General Notes)을 최우선으로 따르세요.")
