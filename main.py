import re
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
from pypdf import PdfReader
from streamlit_agraph import Config, Edge, Node, agraph


ARCHIVE_DIR = Path("보험_보도자료_아카이브")
MAX_FILES_IN_GRAPH = 25
STOPWORDS = {
    "그리고",
    "또한",
    "대한",
    "관련",
    "통해",
    "위한",
    "대한민국",
    "보험",
    "분쟁",
    "자료",
    "보도자료",
    "공시",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize_kr_en(text: str) -> List[str]:
    raw = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    return [w for w in raw if w not in STOPWORDS]


@st.cache_data(show_spinner=False)
def read_pdf_text(pdf_path: Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return normalize_text(" ".join(pages))
    except Exception:
        return ""


@st.cache_data(show_spinner=True)
def load_archive(folder: str) -> Dict[str, Dict]:
    base = Path(folder)
    data: Dict[str, Dict] = {}
    if not base.exists():
        return data

    for pdf in sorted(base.rglob("*.pdf")):
        content = read_pdf_text(pdf)
        data[str(pdf)] = {
            "name": pdf.name,
            "path": str(pdf),
            "text": content,
            "tokens": tokenize_kr_en(content),
        }
    return data


def score_document(query: str, text: str, tokens: List[str]) -> float:
    q = query.strip().lower()
    if not q or not text:
        return 0.0
    text_l = text.lower()
    exact = text_l.count(q)
    partial = sum(1 for t in tokens if q in t)
    return exact * 3.0 + partial * 0.3


def search_documents(query: str, docs: Dict[str, Dict]) -> List[Tuple[str, Dict, float]]:
    results: List[Tuple[str, Dict, float]] = []
    for key, doc in docs.items():
        score = score_document(query, doc["text"], doc["tokens"])
        if score > 0:
            results.append((key, doc, score))
    results.sort(key=lambda x: x[2], reverse=True)
    return results


def summarize_text(text: str, query: str, max_sentences: int = 3) -> str:
    if not text:
        return "요약할 텍스트를 찾지 못했습니다."

    sentences = re.split(r"(?<=[.!?다])\s+", text)
    q = query.lower().strip()
    ranked = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 20:
            continue
        score = s_clean.lower().count(q) * 5 + len(set(tokenize_kr_en(s_clean)))
        ranked.append((score, s_clean))

    ranked.sort(key=lambda x: x[0], reverse=True)
    picked = [s for _, s in ranked[:max_sentences]]
    if not picked:
        return normalize_text(text[:300]) + "..."
    return " ".join(picked)


def build_relationship_graph(results: List[Tuple[str, Dict, float]], query: str):
    top_results = results[:MAX_FILES_IN_GRAPH]
    nodes: List[Node] = []
    edges: List[Edge] = []

    if not top_results:
        return nodes, edges

    q = query.strip()
    nodes.append(Node(id="query", label=f"검색어: {q}", size=28, color="#2563eb"))

    token_sets: Dict[str, set] = {}
    for key, doc, score in top_results:
        token_set = set(doc["tokens"])
        token_sets[key] = token_set
        nodes.append(Node(id=key, label=doc["name"][:28], size=16, color="#0ea5e9", title=f"점수: {score:.1f}"))
        edges.append(Edge(source="query", target=key, label=f"{score:.1f}", color="#93c5fd"))

    keys = [k for k, _, _ in top_results]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            inter = token_sets[a].intersection(token_sets[b])
            if len(inter) >= 8:
                edges.append(Edge(source=a, target=b, color="#64748b", label=str(len(inter))))

    return nodes, edges


def init_page():
    st.set_page_config(page_title="대한민국 보험 분쟁 데이터 허브", page_icon="🔎", layout="wide")
    st.markdown(
        """
        <style>
        .hero-wrap {text-align:center; padding-top: 6vh; padding-bottom: 1vh;}
        .hero-title {font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px;}
        .hero-sub {font-size: 1rem; color: #64748b; margin-top: 0.4rem;}
        .result-box {border:1px solid #e5e7eb; border-radius: 12px; padding: 12px; margin-bottom: 8px;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-title">대한민국 보험 분쟁 데이터 허브</div>
          <div class="hero-sub">금감원·손보협·생보협 자료를 한 번에 검색합니다</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_page()
    docs = load_archive(str(ARCHIVE_DIR))

    if not ARCHIVE_DIR.exists():
        st.error(f"'{ARCHIVE_DIR}' 폴더가 없습니다. 먼저 PDF 수집을 진행해주세요.")
        return

    if not docs:
        st.warning("읽을 수 있는 PDF가 아직 없습니다.")
        return

    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        query = st.text_input(
            "검색어 입력",
            placeholder="예: 민원, 분쟁조정, 유의사항 사례",
            label_visibility="collapsed",
        )

    if not query.strip():
        st.info("중앙 검색창에 단어를 입력하면 관련 PDF와 관계 그래프를 보여드립니다.")
        return

    results = search_documents(query, docs)
    st.write(f"총 **{len(results)}건**의 관련 PDF를 찾았습니다.")

    left, right = st.columns([1.1, 1.4], gap="large")

    with left:
        st.subheader("검색 결과")
        if not results:
            st.warning("일치하는 문서를 찾지 못했습니다.")
        for idx, (key, doc, score) in enumerate(results[:50], 1):
            st.markdown(f"<div class='result-box'><b>{idx}. {doc['name']}</b><br/>관련도 점수: {score:.1f}</div>", unsafe_allow_html=True)
            if st.button(f"요약 보기 - {doc['name']}", key=f"sum-{key}"):
                summary = summarize_text(doc["text"], query)
                st.markdown(f"**핵심 요약**\n\n{summary}")
                st.caption(f"파일 경로: {doc['path']}")

    with right:
        st.subheader("사례 관계 네트워크 (안티그래비티)")
        nodes, edges = build_relationship_graph(results, query)
        if not nodes:
            st.info("그래프를 그릴 수 있는 데이터가 부족합니다.")
        else:
            config = Config(
                width="100%",
                height=700,
                directed=False,
                physics=True,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#dbeafe",
                collapsible=True,
                link={"highlightColor": "#93c5fd"},
            )
            agraph(nodes=nodes, edges=edges, config=config)


if __name__ == "__main__":
    main()
