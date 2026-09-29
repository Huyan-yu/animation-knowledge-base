# 部署到 Cloudflare Pages（公网 URL）

前端 `frontend/` 是纯静态，直接部署。

```bash
# 1. 部署
npx wrangler pages deploy frontend/ --project-name animation-kb

# 2. 公网 URL
# https://animation-kb.<subdomain>.pages.dev
```

后端（真实 LLM 评估）可部署到任意 Python 托管（Cloudflare Workers Python / Render / Vercel），
前端把 API base 指向它。mock 模式下前端内置回退，无需后端。
