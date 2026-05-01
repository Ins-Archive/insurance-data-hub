import streamlit as st
import os
from pypdf import PdfReader

# 1. 페이지 기본 설정 (탭 이름과 아이콘)
st.set_page_config(page_title="팩트인스 | FactIns", page_icon="🏛️", layout="wide")

# 2. 팩트인스 전용 커스텀 디자인 (CSS)
st.markdown("""
<style>
    /* 메인 타이틀 폰트 및 색상 */
    .main-title {
        color: #002D62; 
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0px;
    }
    /* 서브 타이틀 */
    .sub-title {
        color: #555555;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    /* 검색 결과 카드 디자인 */
    .fact-card {
        background-color: #F8F9FA;
        border-left: 5px solid #007BFF;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 (왼쪽 메뉴) - 신뢰감 부여
with st.sidebar:
    st.markdown("## 🏛️ FactIns")
    st.markdown("**전국 보험설계사를 위한 분쟁 팩트체커**")
    st.divider()
    st.markdown("### 📂 정보 출처")
    st.markdown("✅ 금융감독원 보도자료\n✅ 분쟁조정위원회 판례\n*(2024~2025 최신 데이터)*")
    st.divider()
    st.info("💡 카더라에 속지 마세요. 고객 상담 전, 팩트인스에서 먼저 확인하세요.")

# 4. 헤더 영역 (로고 및 타이틀)
st.markdown('<p class="main-title">🏛️ FactIns (팩트인스)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">"카더라는 가라. 오직 금감원 팩트로만 승부합니다."</p>', unsafe_allow_html=True)
st.divider()

# 5. 메인 검색 엔진 영역
col1, col2 = st.columns([4, 1]) # 검색창을 넓게, 버튼을 좁게 배치
with col1:
    search_query = st.text_input("🔎 어떤 분쟁 사례를 찾으시나요?", placeholder="예: 유암종, 고지의무 위반, 백내장 다초점렌즈 등")
with col2:
    st.write("") # 높이 맞춤용 빈칸
    st.write("")
    search_button = st.button("팩트 검색 🚀", use_container_width=True)

# 6. 검색 결과 출력 영역
if search_button and search_query:
    st.success(f"🔍 '{search_query}'에 대한 금감원 공식 자료를 분석 중입니다...")
    
    # 💡 [여기에 나중에 실제 PDF를 읽고 검색하는 코드가 들어갈 자리입니다]
    
    # 지금은 디자인 확인용 가짜 결과(Mock-up)를 보여줍니다.
    st.markdown(f"""
    <div class="fact-card">
        <h4 style='color:#002D62; margin-top:0;'>📌 [핵심 요약] {search_query} 관련 분쟁 조정 결과</h4>
        <p><b>출처:</b> 금융감독원 분쟁조정국 보도자료</p>
        <p><b>팩트 체크:</b> 고객의 {search_query} 청구 건에 대하여, 금융감독원은 약관상 명시된 사유를 근거로 보상 책임을 인정하는 취지의 조정을 내렸습니다. (관련 판례 번호: 2024-xxx)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 자세히 보기 아코디언 메뉴
    with st.expander("📄 보도자료 원문 자세히 보기 (고객 공유용)"):
        st.write("여기에 PDF에서 추출된 실제 긴 문장들이 표시됩니다. 설계사님이 이 부분을 캡처해서 고객에게 보내주면 신뢰도가 급상승합니다.")

else:
    # 검색하기 전 초기 화면 (대시보드 느낌)
    st.subheader("📊 오늘의 팩트인스 현황")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="누적 검증 자료", value="124건", delta="이번 주 +5건 추가")
    with c2:
        st.metric(label="설계사 최다 검색 키워드", value="백내장 입원")
    with c3:
        st.metric(label="시스템 최종 업데이트", value="2026.05.01")
