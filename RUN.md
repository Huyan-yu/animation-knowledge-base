# 运行管线（Mock 模式，无需 API key）

## 环境

```bash
pip install jieba numpy
# ffmpeg 可选（有则合成 .mp4，无则输出成片帧序列）
```

## 全流程

```bash
python data/clean/clean.py     # 数据清洗 → corpus.json
python eval/evaluate.py        # 评估（Recall@5 + 忠实度 + 完整性）
python qa/answer.py "问题"      # 单条问答 demo
```

## 输出

- `data/clean/corpus.json` — 工序记录 + 图谱三元组
- `eval/report.json` — 评测对逐条得分 + 达标率
- `frontend/` — 公网部署的静态前端

## 真实接入（加分项）

- 设 `USE_OCR=1` + 装 PaddleOCR → 阶段 1 真实抽 PDF 文本
- 装 `bge-m3` + FAISS + whoosh → 检索走真实向量/BM25
- 配 `DEEPSEEK_API_KEY` → 问答 + 评估 judge 走真实 LLM
- 部署：`deploy/DEPLOY.md`（Cloudflare Pages）
