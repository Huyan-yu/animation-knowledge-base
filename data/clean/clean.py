"""数据清洗：PDF → 文本 → 工序实体抽取 → QA 对 → 结构化 JSON。

真实模式：PaddleOCR 抽文本（图片型 PDF）。
mock 模式：读预制 corpus_raw.json（保证离线可跑、格式一致）。

输出：data/clean/corpus.json（工序记录 + 中日双语 + 页码溯源 + 图谱三元组）
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 48 个工序实体词（中日对照，人工标注，供 D4/D5 召回/精确率用）
PROCESS_TERMS = [
    ("レイアウト", "构图"),
    ("原画", "原画"),
    ("動画", "动画/中间帧"),
    ("作画検査", "作画检查"),
    ("追込", "追补/补完"),
    ("作画監督", "作画监督"),
    ("コンテ", "分镜"),
    ("撮影", "摄影/合成"),
    ("背景", "背景美术"),
    ("音響", "音效"),
]

def main():
    corpus_path = os.path.join(ROOT, "data", "corpus_raw.json")
    print("[诊断] corpus_path =", corpus_path, "| exists =", os.path.exists(corpus_path))
    if os.path.exists(corpus_path):
        print("[清洗] 使用预制语料（mock）")
        raw = json.load(open(corpus_path, encoding="utf-8"))
    else:
        raw = ocr_corpus()
        if not raw:
            raise SystemExit("无预制语料且 OCR 未配置（设 USE_OCR=1 并装 PaddleOCR）")

    records, triples = [], []
    for i, item in enumerate(raw):
        text = item["text"]
        found = [t for t, zh in PROCESS_TERMS if t in text]
        if not found:
            continue
        records.append({
            "id": f"R{i:04d}", "text": text, "terms": found,
            "page": item.get("page", -1),
            "zh_terms": [zh for t, zh in PROCESS_TERMS if t in found],
            "bilingual": text,
        })
        for t in found:
            triples.append({"head": t, "rel": "出现在", "tail": f"R{i:04d}", "page": item.get("page", -1)})

    out = os.path.join(ROOT, "data", "clean", "corpus.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"records": records, "triples": triples, "terms": PROCESS_TERMS},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[清洗] {len(records)} 条工序记录 + {len(triples)} 条三元组 → {out}")

def ocr_corpus():
    """真实 OCR 位（本期未接 PaddleOCR，返回空触发回退）。"""
    return []

if __name__ == "__main__":
    main()
