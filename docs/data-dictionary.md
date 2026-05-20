# 数据字典

## Company 公司
| 字段 | 类型 | 说明 |
|---|---|---|
| id | int | 主键 |
| name | str (256) | 公司全称（唯一） |
| credit_code | str (32) | 统一社会信用代码（唯一可空） |
| short_name | str (128) | 简称 |
| legal_representative | str (64) | 法定代表人 |
| reg_capital | numeric(18,2) | 注册资本 |
| reg_capital_currency | str (8) | 货币代码，默认 CNY |
| established_date | date | 成立日期 |
| reg_address | str (512) | 注册地址 |
| business_scope | text | 经营范围 |
| company_type | str (64) | 企业类型 |
| status | str | active / dissolved |
| parent_company_id | int FK | 母公司 ID（自关联） |
| remark | text | 备注 |

## Person 自然人
| 字段 | 类型 | 说明 |
|---|---|---|
| id | int | 主键 |
| name | str (64) | 姓名 |
| id_card_hash | str (128) | 身份证号 SHA-256 加盐哈希（唯一） |
| id_card_last4 | str (4) | 身份证后 4 位（用于检索） |
| nationality | str (32) | 国籍，默认 中国 |
| phone / email / gender | | 联系方式 / 性别 |
| remark | text | 备注 |

> **隐私设计**：身份证号原文从不入库。`hash_id_card()` 在 `app.core.security` 中实现，使用 `SECRET_KEY` 加盐避免彩虹表攻击。

## Position 任职关系
| 字段 | 说明 |
|---|---|
| person_id, company_id | 外键 |
| position_type | 枚举：法定代表人 / 董事长 / 董事 / 监事 / 总经理 / 财务负责人 / 实际控制人 / ... |
| start_date, end_date | end_date 为 NULL 表示在任 |
| document_no | 任职文号 |

## Shareholding 持股关系
| 字段 | 说明 |
|---|---|
| company_id | 被持股公司 |
| shareholder_type | "person" 或 "company"（多态） |
| shareholder_id | 指向 persons.id 或 companies.id |
| ratio | 持股比例（0-100） |
| amount | 出资额 |
| currency, contribute_method, contribute_date | 货币、方式、出资日期 |

## ConflictRule 冲突规则
- `rule_type=incompatible_positions`：定义 position_a / position_b 不可同时由同一人担任
- `scope`：`same_company`（仅同一公司） / `parent_subsidiary`（母子公司） / `any`（任意范围）
- `severity`：info / warning / critical

## Alert 预警
- `kind`：conflict / term_expiry / other
- `status`：open / acknowledged / resolved / ignored
- 预警重复抑制：以标题去重，避免重复推送

## ChangeLog 审计日志
- 任意主数据 CRUD 都会写入一条记录
- 修改时按字段拆分多条 `update` 记录，记录 `old_value` / `new_value`

## RBAC 角色
- `superadmin`：全部权限
- `admin`：管理用户、数据
- `editor`：编辑业务数据
- `viewer`：只读

> 数据范围权限（按公司 / 按部门隔离）将在 Iteration 4 落地。
