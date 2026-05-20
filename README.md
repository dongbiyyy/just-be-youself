# 集团工商治理监控系统 (Governance Monitor)

针对集团内 ~40 家公司、母子公司关联、董监高/股东/实控人变化的工商治理监控平台。

## 核心能力 (Iteration 1)

- 公司、人员、任职关系、股权关系四大主数据 CRUD
- 母子公司层级（自关联，支持树状视图 API）
- 身份证号脱敏存储（SHA-256 哈希 + 仅保留后 4 位明文用于检索）
- Excel 模板下载 / 批量导入（公司、人员、任职、股权）
- 全文搜索（公司名 / 信用代码 / 人名 / 身份证后 4 位）
- 风险预警引擎（默认规则：监事不得兼任董事/高管；母子公司同任董事）
- 任期到期提醒（30 / 60 / 90 天三档）
- 变更审计日志（每个字段记录前后值）
- JWT 登录 + 角色字段（superadmin / admin / editor / viewer）

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2 + Pydantic v2 |
| 数据库 | PostgreSQL (生产) / SQLite (开发) |
| 认证 | JWT (python-jose) + bcrypt |
| 导入 | openpyxl |
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia + Vite |
| 部署 | Docker Compose |

## 目录结构

```
backend/                FastAPI 后端
  app/
    api/                路由层
    core/               配置、数据库、安全
    models/             SQLAlchemy 模型
    schemas/            Pydantic schema
    services/           Excel 导入、审计、冲突检测
    main.py             入口
    seed.py             示例数据脚本
  tests/                pytest 测试
frontend/               Vue 3 前端
  src/
    api/                axios 封装
    router/             路由
    stores/             Pinia
    views/              Login / Layout / Dashboard / Companies / Persons
docs/                   数据字典、设计文档
docker-compose.yml      一键启动 (db + backend + frontend)
```

## 本地运行 —— 不用 Docker

后端：

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python -m app.seed                       # 可选：写入示例数据
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173
```

浏览器打开 http://localhost:5173 ，使用 `admin / admin123` 登录。

## Docker 一键启动

```bash
docker compose up --build -d
# 写入示例数据
docker compose exec backend python -m app.seed
# 打开 http://localhost
```

## 测试

```bash
cd backend
pytest -q
```

## 后续迭代

下个迭代将补充：

- Iteration 2：任职/股权页 + 公司视角 / 人员视角详情页 + 时间轴
- Iteration 3：股权树（ECharts）+ 人-公司关系图（AntV G6）+ 变更对比
- Iteration 4：报表导出 (PDF/Excel)、审计日志查询界面、按公司/部门数据权限隔离
- 扩展：企查查/天眼查 API 对接、移动端、自然语言查询

详见 [`docs/`](docs/) 中的数据字典与设计说明。
