# 以鲜国际 · 项目记忆

## 展会板块（exhibitions.html）

- DEFAULT_EXPO 当前最新 ID 范围：d1 ~ d13（截至 2026-06-29）
- 新增展会需检查现有条目避免重复，d5 中食展、d10 青岛渔博会、d11 FHC上海、d8 Anuga、d9 Gulfood 已被占用
- 展会描述中如有单引号需转义为 \'
- ID 命名规则：默认 d 开头（d1, d2, ...），用户手动新增为 u 开头（u1, u2, ...）
- 部署流程：使用 GIT_INDEX_FILE=/tmp/efsupply_index 临时索引提交，必须加 dangerouslyDisableSandbox: true
