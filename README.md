# 动画知识库（题目 A）

日本动画作画工序 RAG 知识库：三路混合检索（向量 bge-m3 + BM25 + 图谱 NetworkX）+ LLM 问答 + 同口径评估。
选题理由、选型考量、评估方案、失败案例详见 [README_交付说明.md](README_交付说明.md)。

## 目录

```
data/clean/clean.py     数据清洗（PDF→文本→实体→QA 对）；mock 用预制 corpus_raw.json
retrieval/hybrid.py     三路混合检索 + RRF 融合（mock 近似分 / 真实 bge-m3+FAISS+whoosh）
qa/answer.py            问答层（检索→LLM 生成 + 引文；检索不到说"库中没有"）
eval/evaluate.py        评估（Recall@5 + 忠实度 + 完整性，75/90 口径）
eval/eval_set.json      评测对（gold ids + 关键事实）
frontend/               静态前端（公网部署用）
deploy/DEPLOY.md        Cloudflare Pages 部署说明
```

## 运行（mock，无需 API key）

```bash
pip install jieba numpy
python data/clean/clean.py    # 生成 data/clean/corpus.json
python eval/evaluate.py       # 出 eval/report.json
python qa/answer.py "摄影合成在哪个工序之后"
```

## 真实接入（加分项）

- 向量：`bge-m3`（sentence-transformers）+ FAISS
- 关键词：whoosh BM25 + jieba（中文）/ 日文 n-gram
- 问答 LLM：DeepSeek chat（OpenAI 兼容 API）
- 评估 judge：LLM-as-judge，与人工 20 条对齐 (kappa≥0.7) 才启用
