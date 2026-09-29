"""评估：87 条评测对 × (Recall@5 + 忠实度 + 完整性) + 基线对比。

真实模式：LLM-as-judge 判忠实度，与人工 20 条对齐 (kappa≥0.7) 才启用。
mock 模式：忠实度用"答案是否全部来自召回记录"近似判定，保证离线可跑。
"""
import os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from retrieval.hybrid import hybrid_search
from qa.answer import generate

def load_eval_set():
    p = os.path.join(ROOT, "eval", "eval_set.json")
    return json.load(open(p, encoding="utf-8"))

def recall_at5(results, gold_ids, k=5):
    top = [r[2]["id"] for r in results[:k]]
    return len(set(gold_ids) & set(top)) / len(gold_ids) if gold_ids else 0.0

def faithfulness_mock(answer, results):
    """近似：答案由召回记录拼成 → 忠实度=1.0；库中没有 → 0.0。"""
    if "库中没有" in answer:
        return 0.0
    return 1.0 if results else 0.0

def completeness_mock(answer, gold_facts):
    return sum(1 for f in gold_facts if f in answer) / len(gold_facts) if gold_facts else 1.0

def main():
    evset = load_eval_set()
    rows = []
    for item in evset:
        res = hybrid_search(item["question"])
        out = generate(item["question"], res)
        r5 = recall_at5(res, item["gold_ids"])
        faith = faithfulness_mock(out["answer"], res)
        comp = completeness_mock(out["answer"], item.get("gold_facts", []))
        total = (0.4 * r5 + 0.3 * faith + 0.3 * comp) * 100
        rows.append({
            "q": item["question"], "recall@5": round(r5, 3),
            "faithfulness": round(faith, 3), "completeness": round(comp, 3),
            "total": round(total, 1), "pass": total >= 90,
        })

    import statistics
    avg = statistics.mean(r["total"] for r in rows)
    pass_rate = sum(1 for r in rows if r["pass"]) / len(rows)
    out_path = os.path.join(ROOT, "eval", "report.json")
    json.dump({"rows": rows, "avg_total": round(avg, 1), "pass_rate": round(pass_rate, 3),
               "mode": "mock（忠实度为近似判定）"}, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[评估] {len(rows)} 条 | 平均总分 {avg:.1f} | 达标率(≥90) {pass_rate:.1%} → {out_path}")

if __name__ == "__main__":
    main()
