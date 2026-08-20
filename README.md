# Starpath Archive（星轨秘典）

Starpath Archive 是一个面向 AstrBot Native Agent 的娱乐互动占卜插件。它将真实天文资料、传统塔罗文化和星空箴言组合为结构化记录；Native Agent 保留最终对话回复与风格控制权。

> 本项目仅提供文化象征与娱乐体验，不预测未来、不作人生决策、不分析用户心理或画像。

## Sprint 1 — v0.1.0-alpha

已完成：

- 每日定星：仅根据发送者标识的哈希与 UTC 日期稳定选择天体。
- 单张塔罗抽取：包含正位、逆位和传统牌义。
- 星辰箴言：随机抽取星空主题文本。
- `generate_starpath_record` Native Tool：返回 JSON，不发送消息、不生成最终聊天回复。
- 静态数据：15 个真实天体、22 张大阿尔卡那、30 条箴言。

已知限制：

- 当前仅包含大阿尔卡那；完整 78 张牌组将在后续 Sprint 补齐。
- 不包含塔罗图片、历史/收藏、主动推送、定时任务或多消息仪式流程。

下一阶段：

1. 添加 56 张小阿尔卡那及完整牌组数据校验。
2. 增加面向 AstrBot 实际运行环境的集成验证。

## 安装

将此目录作为 AstrBot 插件安装目录。插件需要 AstrBot `>=4.27.2`。

## Tool

`generate_starpath_record(mode="daily", spread="single")`

返回：

```json
{
  "record_id": "starpath-...",
  "star": {},
  "tarot": {},
  "quote": {}
}
```

工具仅接受 `daily` 与 `single`，并返回文化象征内容。Native Agent 负责将该结果转化为面向用户的最终回复。

## 开发与测试

```bash
python -m pytest -q
python -m ruff check .
```

## 许可证

[MIT](LICENSE)
