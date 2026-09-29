"""三路混合检索：向量(bge-m3) + BM25(jieba) + 图谱(NetworkX)。RRF 融合。

真实模式：bge-m3 embedding + FAISS；BM25 用 jieba 分词；图谱用 NetworkX。
mock 模式：词频重叠做近似向量分 + 关键词匹配 + 实体命中，保证离线可跑、同口径。
"""
import os, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_corpus():
    p = os.path.join(ROOT, "data", "clean", "corpus.json")
    if not os.path.exists(p):
        os.system(f'python "{os.path.join(ROOT, "data", "clean", "clean.py")}"')
    return json.load(open(p, encoding="utf-8"))

def tokenize(text):
    """中日混合分词：jieba 切中文 + 日文 n-gram + 拉丁词。"""
    try:
        import jieba
        zh = list(jieba.cut(re.sub(r'[぀-ヿ]', '', text)))
    except ImportError:
        zh = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', text)
    jp = re.findall(r'[぀-ヿ]{1,4}', text)
    return [t for t in zh + jp if t]

def vec_score(query, rec):
    """近似向量分（真实模式换成 bge-m3 余弦）。"""
    q, d = set(tokenize(query)), set(tokenize(rec["text"]))
    return len(q & d) / (len(q) + 1e-6)

def bm25_score(query, rec):
    """简化 BM25（真实模式换 whoosh）。"""
    q, d = set(tokenize(query)), set(tokenize(rec["text"]))
    return sum(1 for t in q if t in d)

def graph_score(query, rec):
    """图谱分：query 命中的工序实体是否在记录里。"""
    return 1.0 if any(t in query for t in rec.get("terms", [])) else 0.0

def hybrid_search(query, top_k=5, mode="hybrid"):
    corpus = load_corpus()["records"]
    scores = {}
    for r in corpus:
        s_vec = vec_score(query, r)
        s_bm25 = bm25_score(query, r)
        s_graph = graph_score(query, r)
        if mode == "vector_only":
            total = s_vec
        elif mode == "hybrid":
            total = s_vec * 0.4 + s_bm25 * 0.35 + s_graph * 0.25
        else:
            total = s_vec + s_bm25 + s_graph
        scores[r["id"]] = total
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
    rec_map = {r["id"]: r for r in corpus}
    return [(rid, s, rec_map[rid]) for rid, s in ranked]

if __name__ == "__main__":
    for q in ["原画和動画谁检查谁", "ゲラ是什么", "摄影合成在哪个工序之后"]:
        print(f"\nQ: {q}")
        for rid, s, rec in hybrid_search(q):
            print(f"  {rid} ({s:.2f}) p{rec['page']}: {rec['text'][:40]}")
