import streamlit as st
import math

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료 (기존 유지)
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
# 2. [로직] 매입등록비 (기존 유지)
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
# 3. 메인 앱 (V31: 교통비 추가 및 만원 단위 단축 입력 적용)
# -----------------------------------------------------------
def smart_purchase_calculator_final_v31():
    st.set_page_config(page_title="매입견적서 by 김희주", layout="wide")
    
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

    # [초기화] 세션 상태값 초기화
    if 'p_type' not in st.session_state: st.session_state['p_type'] = "개인"
    if 'p_route' not in st.session_state: st.session_state['p_route'] = "셀프"
    if 't_cost' not in st.session_state: st.session_state['t_cost'] = 30000
    if 'check_cost' not in st.session_state: st.session_state['check_cost'] = 66000
    
    # [추가] 상품화 비용 입력을 위한 세션 초기화 (자동 변환을 위해 필요)
    if 'cost_dent' not in st.session_state: st.session_state['cost_dent'] = 0
    if 'cost_wheel' not in st.session_state: st.session_state['cost_wheel'] = 0
    if 'cost_etc' not in st.session_state: st.session_state['cost_etc'] = 0

    # [기능] 입력값 자동 변환 콜백 함수 (17 -> 170,000)
    def smart_unit_converter(key):
        val = st.session_state[key]
        # 0보다 크고 1000 이하인 경우 만원 단위로 간주하여 곱하기 10000
        if 0 < val <= 1000:
            st.session_state[key] = val * 10000

    st.title("매입견적서 by 김희주")

    # =========================================================
    # Step 1. 상단 기본 정보
    # =========================================================
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        # 판매 예정가 (만원 단위 입력)
        sales_input = st.number_input("판매 예정가 (단위: 만원)", value=3500, step=10, format="%d")
        sales_price = sales_input * 10000
        st.markdown(f"<div class='input-check'>확인: {sales_price:,} 원</div>", unsafe_allow_html=True)
        
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"], key='p_type')
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"], key='p_route')

    st.markdown("---")

    # =========================================================
    # Step 2. 메인 화면 분할
    # =========================================================
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("<div class='section-header'>상품화 비용 입력</div>", unsafe_allow_html=True)
        
        cost_perf = st.radio("성능점검비", [44000, 66000], key='check_cost', horizontal=True)
        
        # [수정] 교통비 옵션 추가 (5만원, 60만원) 및 정렬
        transport_options = [30000, 50000, 80000, 130000, 170000, 200000, 600000]
        cost_transport = st.selectbox("교통비", transport_options, key='t_cost')
        
        # [수정] 만원 단위 숏컷 입력 적용 (on_change 사용)
        st.caption("※ 비용 입력 팁: 17 입력시 → 170,000원으로 자동 변환")
        
        cost_dent = st.number_input(
            "판금/도색", step=10000, format="%d", 
            key='cost_dent', on_change=smart_unit_converter, args=('cost_dent',)
        )
        
        cost_wheel = st.number_input(
            "휠/타이어", step=10000, format="%d", 
            key='cost_wheel', on_change=smart_unit_converter, args=('cost_wheel',)
        )
        
        cost_etc = st.number_input(
            "기타비용", step=10000, format="%d", 
            key='cost_etc', on_change=smart_unit_converter, args=('cost_etc',)
        )

        HIDDEN_AD = 275000
        HIDDEN_POLISH = 120000
        HIDDEN_DEPOSIT = 60000
        
        st.caption(f"※ 광고({HIDDEN_AD//10000}만), 광택({HIDDEN_POLISH//10000}만), 입금({HIDDEN_DEPOSIT//10000}만) 자동 포함")
        
        cost_repair_total = cost_dent + cost_wheel + cost_etc

    # --- 가이드 산출 ---
    fixed_costs = (cost_perf + HIDDEN_AD + cost_transport + 
                   cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT)
    
    budget_after_55 = int(sales_price * 0.945)
    
    guide_bid = 0
    start_point = budget_after_55 - fixed_costs
    
    for bid in range(start_point, start_point - 5000000, -10000):
        fee = get_auction_fee(bid, p_route)
        reg = get_reg_cost(bid, p_type)
        if (bid + fixed_costs + fee + reg) <= budget_after_55:
            guide_bid = bid
            break
            
    # 천원 단위 올림 처리
    if guide_bid > 0:
        guide_bid = math.ceil(guide_bid / 10000) * 10000

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        
        st.markdown("**적정 매입가 (Guide)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("")
        
        st.markdown("**▼ 실제 입찰금액 입력**")
        my_bid = st.number_input("입찰가 입력", value=guide_bid, step=10000, format="%d", label_visibility="collapsed")
        
        bid_ratio = (my_bid / sales_price) * 100 if sales_price > 0 else 0
        st.markdown(f"<div class='input-check' style='text-align:right;'>확인: ({bid_ratio:.1f}%) {my_bid:,} 원</div>", unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================
    # Step 3. 최종 결과
    # =========================================================
    real_fee = get_auction_fee(my_bid, p_route)
    real_reg = get_reg_cost(my_bid, p_type)
    real_interest = int(my_bid * 0.01)
    
    sum_vat_costs = cost_perf + HIDDEN_AD + real_fee
    sum_non_vat_costs = cost_transport + cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT
    
    gross_margin = sales_price - my_bid - sum_vat_costs
    dealer_income = int(gross_margin / 1.1)
    
    tax_base = dealer_income - real_reg
    tax_33 = int(tax_base * 0.033) if tax_base > 0 else 0
    
    real_income = dealer_income - (sum_non_vat_costs + real_reg + real_interest + tax_33)
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
    smart_purchase_calculator_final_v31()
