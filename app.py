import streamlit as st

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료 계산 (V25: 사용자 제공 수식 적용)
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
# 2. [로직] 매입등록비 계산 (V23: 엑셀 수식 적용)
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
# 3. 메인 앱
# -----------------------------------------------------------
def smart_purchase_calculator_final_v27():
    st.set_page_config(page_title="매입견적서 by 김희주", layout="wide")
    
    # [CSS] 스타일링
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 16px; }
        @media (max-width: 600px) { html, body, [class*="css"] { font-size: 14px; } }
        
        h1 { font-size: clamp(1.5rem, 4vw, 2.5rem) !important; font-weight: 800 !important; }
        
        .big-price { font-size: clamp(1.5rem, 3vw, 2.0rem); font-weight: 900; color: #4dabf7; }
        .real-income { font-size: clamp(1.4rem, 2.5vw, 1.8rem); font-weight: bold; }
        .margin-rate { font-size: clamp(2.0rem, 4vw, 2.5rem); font-weight: 900; color: #ff6b6b; }
        
        .input-check {
            font-size: 0.9rem;
            color: #2e7d32;
            font-weight: bold;
            margin-top: -10px;
            margin-bottom: 10px;
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
    # Step 1. 기본 정보
    # =========================================================
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        sales_price = st.number_input("판매 예정가", value=35000000, step=100000, format="%d")
        st.markdown(f"<div class='input-check'>확인: {sales_price:,} 원</div>", unsafe_allow_html=True)
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"], key='p_type')
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"], key='p_route')

    st.markdown("---")

    # =========================================================
    # Step 2. 상품화 내용
    # =========================================================
    st.subheader("상품화 비용 입력")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cost_perf = st.radio("성능점검", [44000, 66000], key='check_cost')
        cost_dent = st.number_input("판금/도색", value=0, step=10000, format="%d")
        if cost_dent > 0: st.caption(f"확인: {cost_dent:,} 원")
    with c2:
        cost_ad = st.number_input("광고비", value=275000, step=1000, format="%d")
        st.caption(f"확인: {cost_ad:,} 원")
        cost_wheel = st.number_input("휠/타이어", value=0, step=10000, format="%d")
        if cost_wheel > 0: st.caption(f"확인: {cost_wheel:,} 원")
    with c3:
        cost_transport = st.selectbox("교통비", [30000, 80000, 130000, 170000, 200000], key='t_cost')
        cost_etc = st.number_input("기타비용", value=0, step=10000, format="%d")
        if cost_etc > 0: st.caption(f"확인: {cost_etc:,} 원")
    with c4:
        st.caption("※ 광택(12만), 입금(6만)은\n자동 포함됩니다.")
    
    cost_repair_total = cost_dent + cost_wheel + cost_etc
    HIDDEN_POLISH = 120000
    HIDDEN_DEPOSIT = 60000

    st.markdown("---")

    # =========================================================
    # Step 3. [핵심] 적정 매입가 가이드 (V4 로직 수정)
    # =========================================================
    # 수식: (판매가 * 0.945) - (고정비 + 수수료 + 등록비)
    # [수정] 가이드 계산 시 '금융이자(1%)' 차감 삭제 (엑셀 수식 일치화)
    
    fixed_costs = (cost_perf + cost_ad + cost_transport + 
                   cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT)
    
    budget_after_55 = int(sales_price * 0.945)
    
    guide_bid = 0
    start_point = budget_after_55 - fixed_costs
    
    for bid in range(start_point, start_point - 5000000, -10000):
        fee = get_auction_fee(bid, p_route)
        reg = get_reg_cost(bid, p_type) 
        
        # [중요] 이자(Interest) 제외하고 계산
        if (bid + fixed_costs + fee + reg) <= budget_after_55:
            guide_bid = bid
            break

    # =========================================================
    # Step 4. 결과 화면
    # =========================================================
    c_res1, c_res2 = st.columns([1, 1])
    with c_res1:
        st.markdown("**적정 매입가 (Guide)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
    with c_res2:
        st.markdown("**▼ 실제 입찰금액 입력**", unsafe_allow_html=True)
        my_bid = st.number_input("입찰가", value=guide_bid, step=10000, format="%d", label_visibility="collapsed")
        
        bid_ratio = (my_bid / sales_price) * 100 if sales_price > 0 else 0
        st.markdown(f"<div style='text-align:right; color:#2e7d32; font-weight:bold; font-size:0.9rem;'>확인: ({bid_ratio:.1f}%) {my_bid:,} 원</div>", unsafe_allow_html=True)

    # --- 실소득액 & 마진율 (실제 결과 계산엔 이자 포함) ---
    real_fee = get_auction_fee(my_bid, p_route)
    real_reg = get_reg_cost(my_bid, p_type)
    real_interest = int(my_bid * 0.01) # 실소득 계산할 땐 이자 1% 반영
    
    sum_vat_costs = cost_perf + cost_ad + real_fee
    sum_non_vat_costs = cost_transport + cost_repair_total + HIDDEN_POLISH + HIDDEN_DEPOSIT
    
    # 1. 딜러 소득 (세전)
    gross_margin = sales_price - my_bid - sum_vat_costs
    dealer_income = int(gross_margin / 1.1)
    
    # 2. 원천세 (3.3%)
    tax_base = dealer_income - real_reg
    tax_33 = int(tax_base * 0.033) if tax_base > 0 else 0
    
    # 3. 실소득액
    real_income = dealer_income - (sum_non_vat_costs + real_reg + real_interest + tax_33)
    
    # 4. 예상 이익률 (매입가 대비)
    real_margin_rate = (real_income / my_bid) * 100 if my_bid > 0 else 0

    st.markdown("---")

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{real_income:,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>예상 이익률 (매입가 대비)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    st.write("")

    # =========================================================
    # Step 5. 상세 내역서
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
    smart_purchase_calculator_final_v27()