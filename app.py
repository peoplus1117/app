import streamlit as st

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료 계산 (V25 유지: 사용자 제공 수식)
# -----------------------------------------------------------
def get_auction_fee(price, route):
    if route == "셀프":
        if price <= 1000000: return 75000
        elif price <= 5000000: return 185000
        elif price <= 10000000: return 245000
        elif price <= 20000000: return 250000
        elif price <= 30000000: return 250000
        else: return 360000
    elif route == "제로":
        if price <= 1000000: return 140000
        elif price <= 5000000: return 300000
        elif price <= 10000000: return 365000
        elif price <= 15000000: return 365000
        elif price <= 30000000: return 395000
        elif price <= 40000000: return 475000
        else: return 505000
    else:
        return 0

# -----------------------------------------------------------
# 2. [로직] 매입등록비 계산 (V23 유지: 엑셀 수식)
# -----------------------------------------------------------
def get_reg_cost(bid_price, p_type):
    threshold = 28500001
    rate = 0.0105
    if p_type == "개인":
        if bid_price >= threshold: return int(bid_price * rate)
        else: return 0
    else:
        supply_price = bid_price / 1.1
        if supply_price >= threshold: return int(supply_price * rate)
        else: return 0

# -----------------------------------------------------------
# 3. 메인 앱 (UI 전면 개편)
# -----------------------------------------------------------
def smart_purchase_calculator_final_v28():
    st.set_page_config(page_title="매입견적서 by 김희주", layout="wide")
    
    # [CSS] 스타일링
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 16px; }
        @media (max-width: 600px) { html, body, [class*="css"] { font-size: 14px; } }
        
        h1 { font-size: clamp(1.5rem, 4vw, 2.5rem) !important; font-weight: 800 !important; }
        
        .big-price { font-size: clamp(1.6rem, 3.5vw, 2.2rem); font-weight: 900; color: #4dabf7; margin-bottom: 0px; }
        .real-income { font-size: clamp(1.4rem, 2.5vw, 1.8rem); font-weight: bold; }
        .margin-rate { font-size: clamp(2.0rem, 4vw, 2.5rem); font-weight: 900; color: #ff6b6b; }
        
        .input-check {
            font-size: 0.9rem;
            color: #2e7d32;
            font-weight: bold;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        
        .section-header {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 10px;
            border-left: 4px solid #4dabf7;
            padding-left: 10px;
        }

        .detail-table-container { width: 100%; max-width: 450px; margin: 0 auto; }
        .detail-table { width: 100%; border-collapse: collapse; font-size: clamp(0.9rem, 2.5vw, 1.1rem); }
        .detail-table td { padding: 6px 10px; border-bottom: 1px solid #555; }
        @media (prefers-color-scheme: light) { .detail-table td { border-bottom: 1px solid #ddd; } }
        .detail-label { font-weight: bold; opacity: 0.9; white-space: nowrap; }
        .detail-value { text-align: right; font-weight: bold; }
        
        .block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'p_type' not in st.session_state: st.session_state['p_type'] = "개인"
    if 'p_route' not in st.session_state: st.session_state['p_route'] = "셀프"
    if 't_cost' not in st.session_state: st.session_state['t_cost'] = 30000
    if 'check_cost' not in st.session_state: st.session_state['check_cost'] = 66000

    st.title("매입견적서 by 김희주")

    # =========================================================
    # Step 1. 상단 기본 정보 (가로 배열 유지)
    # =========================================================
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_price = st.number_input("판매 예정가", value=35000000, step=100000, format="%d")
        st.markdown(f"<div class='input-check'>확인: {sales_price:,} 원</div>", unsafe_allow_html=True)
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"], key='p_type')
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"], key='p_route')

    st.markdown("---")

    # =========================================================
    # Step 2. 메인 화면 분할 (좌: 비용입력 / 우: 가이드 및 입찰)
    # =========================================================
    left_col, right_col = st.columns([1, 1], gap="large")

    # [왼쪽 컬럼] 비용 입력 (세로 정렬)
    with left_col:
        st.markdown("<div class='section-header'>상품화 비용 입력</div>", unsafe_allow_html=True)
        
        # 성능점검비 (선택형 유지, 필요 시 삭제 가능)
        cost_perf = st.radio("성능점검비", [44000, 66000], key='check_cost', horizontal=True)
        
        # 사용자 지정 4대 비용
        cost_transport = st.selectbox("교통비", [30000, 80000, 130000, 170000, 200000], key='t_cost')
        cost_dent = st.number_input("판금/도색", value=0, step=10000, format="%d")
        cost_wheel = st.number_input("휠/타이어", value=0, step=10000, format="%d")
        cost_etc = st.number_input("기타비용", value=0, step=10000, format="%d")

        # 숨겨진 자동 비용 (광고비 추가됨)
        HIDDEN_AD = 275000      # [수정] 자동 포함
        HIDDEN_POLISH = 120000
        HIDDEN_DEPOSIT = 60000
        
        st.caption(f"※ 광고({HIDDEN_AD//10000}만), 광택({HIDDEN_POLISH//10000}만), 입금({HIDDEN_DEPOSIT//10000}만) 자동 포함")
        
        cost_repair_total = cost_dent + cost_wheel + cost_etc

    # --- 계산 로직 (가이드 산출) ---
    fixed_costs = (cost_perf + HIDDEN_AD + cost_transport + 
                   cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT)
    
    budget_after_55 = int(sales_price * 0.945)
    
    guide_bid = 0
    start_point = budget_after_55 - fixed_costs
    
    # 가이드 역산 루프
    for bid in range(start_point, start_point - 5000000, -10000):
        fee = get_auction_fee(bid, p_route)
        reg = get_reg_cost(bid, p_type)
        # 이자 제외하고 계산 (V27 로직)
        if (bid + fixed_costs + fee + reg) <= budget_after_55:
            guide_bid = bid
            break

    # [오른쪽 컬럼] 가이드 및 실제 입찰 (세로 정렬)
    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        
        # 가이드 표시
        st.markdown("**적정 매입가 (Guide)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("") # 간격 띄우기
        
        # 실제 입찰 입력
        st.markdown("**▼ 실제 입찰금액 입력**")
        my_bid = st.number_input("입찰가 입력", value=guide_bid, step=10000, format="%d", label_visibility="collapsed")
        
        # 비율 확인
        bid_ratio = (my_bid / sales_price) * 100 if sales_price > 0 else 0
        st.markdown(f"<div class='input-check' style='text-align:right;'>확인: ({bid_ratio:.1f}%) {my_bid:,} 원</div>", unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================
    # Step 3. 최종 결과 (하단)
    # =========================================================
    
    # --- 실소득액 & 마진율 계산 ---
    real_fee = get_auction_fee(my_bid, p_route)
    real_reg = get_reg_cost(my_bid, p_type)
    real_interest = int(my_bid * 0.01) # 이자 1%
    
    sum_vat_costs = cost_perf + HIDDEN_AD + real_fee
    sum_non_vat_costs = cost_transport + cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT
    
    gross_margin = sales_price - my_bid - sum_vat_costs
    dealer_income = int(gross_margin / 1.1)
    
    tax_base = dealer_income - real_reg
    tax_33 = int(tax_base * 0.033) if tax_base > 0 else 0
    
    real_income = dealer_income - (sum_non_vat_costs + real_reg + real_interest + tax_33)
    # 이익률: 매입가(투자금) 대비
    real_margin_rate = (real_income / my_bid) * 100 if my_bid > 0 else 0

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{real_income:,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>예상 이익률 (매입가 대비)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    st.write("")

    # =========================================================
    # Step 4. 상세 내역서
    # =========================================================
    with st.expander("🧾 상세 견적 내역 확인 (복사전용)", expanded=True):
        st.markdown(f"""
        <div class='detail-table-container'>
            <table class='detail-table'>
                <tr>
                    <td class='detail-label'>판매가</td>
                    <td class='detail-value'>{sales_price:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>매입가</td>
                    <td class='detail-value' style='color:#4dabf7;'>{my_bid:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>예상이익율</td>
                    <td class='detail-value' style='color:#ff6b6b;'>{real_margin_rate:.2f} %</td>
                </tr>
                <tr>
                    <td class='detail-label'>실소득액</td>
                    <td class='detail-value'>{real_income:,} 원</td>
                </tr>
                <tr><td colspan='2' style='height:8px; border-bottom:1px dashed #777;'></td></tr>
                <tr>
                    <td class='detail-label'>교통비</td>
                    <td class='detail-value'>{cost_transport:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>판금/도색</td>
                    <td class='detail-value'>{cost_dent:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>휠/타이어</td>
                    <td class='detail-value'>{cost_wheel:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>기타비용</td>
                    <td class='detail-value'>{cost_etc:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>매입등록비용</td>
                    <td class='detail-value'>{real_reg:,} 원</td>
                </tr>
                <tr>
                    <td class='detail-label'>낙찰수수료</td>
                    <td class='detail-value'>{real_fee:,} 원</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    smart_purchase_calculator_final_v28()