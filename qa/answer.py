"""问答层：检索 → LLM 生成（附引文）；检索不到时明确说"库中没有"。

真实模式：DeepSeek chat（OpenAI 兼容 API），注入 top-k 上下文 + 强制引用块号。
mock 模式：用命中记录直接拼接"答案"，保证离线可跑、格式一致。
"""
import os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from retrieval.hybrid import hybrid_search

def generate(query, top_results, llm=None):
    """真实：llm 是可调用（prompt, context）→ answer。mock：拼接。"""
    if not top_results:
        return {"answer": "库中没有相关记录。", "citations": []}
    if llm is not None:
        ctx = "\n".join(f"[{r['id']} p{r['page']}] {r['text']}" for _, _, r in top_results)
        prompt = f"问题：{query}\n\n依据以下记录回答，必须引用块号 [Rxxxx]，库中没有就说不知道：\n{ctx}"
        return {"answer": llm(prompt, ctx), "citations": [r["id"] for _, _, r in top_results]}
    answer = "；".join(r["text"] for _, _, r in top_results[:3])
    return {"answer": answer, "citations": [r["id"] for _, _, r in top_results]}

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "原画和動画谁检查谁"
    res = hybrid_search(q)
    out = generate(q, res)
    print("Q:", q)
    print("A:", out["answer"])
    print("引用:", out["citations"])
