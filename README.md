# Starpath Archive（星轨秘典）

Starpath Archive 是一个面向 AstrBot Native Agent 的娱乐互动占卜插件。它将真实天文资料、传统塔罗文化和星空箴言组合为结构化记录；Native Agent 保留最终对话回复与风格控制权。

> 本项目仅提供文化象征与娱乐体验，不预测未来、不作人生决策、不分析用户心理或画像。

## Sprint 2B-2 — v0.3.1-alpha

已完成：

- Tool Experience Contract：`generate_starpath_record` 现在返回完整可验证的
  结构化协议。
- 顶层字段：`record_id`、`generated_at`、`mode`、`spread`、`star`、`tarot`、
  `quote`、`metadata`。
- `experience/` 仅组织机器可读体验元数据；不生成最终聊天文案。
- 增加 AstrBot API-stub 集成模拟和本地真实环境测试说明。

运行集成步骤见 [docs/runtime-test.md](docs/runtime-test.md)。当前仓库未执行
真实 QQ 平台测试。

## Sprint 2B-1 — v0.3.0-alpha

已完成：

- Astral Knowledge System：50 个真实天体的静态知识数据库。
- 支持恒星、星团、星云、星系四类天体。
- 每项数据分离真实天文资料与非预测性的文化象征。
- 天体数据校验覆盖数量、分类、必填字段和唯一 ID。
- 保留 Sprint 1 的 `chinese_name`、`category` JSON 别名，同时提供
  `zh_name`、`type` 标准字段。

数据规模：

- 恒星：27
- 星团：7
- 星云：8
- 星系：8

下一阶段：

1. 为星体数据增加可审核的来源标识与自动化结构校验。
2. 增加 AstrBot 实际运行环境的集成验证。

## Sprint 2A — v0.2.0-alpha

已完成：

- 完整 Rider–Waite–Smith 对应牌组：22 张大阿尔卡那、56 张小阿尔卡那。
- 四花色静态数据：权杖、圣杯、宝剑、星币各 14 张。
- 小阿卡纳独立保存传统正／逆位含义、关键词、元素象征与文学化图像素材。
- 数据校验覆盖总数、花色分布、必填字段及唯一 ID。

已知限制：

- 牌义为精简的文化参考线索，不替代完整的塔罗历史或牌义研究。
- 不包含塔罗图片、历史/收藏、主动推送、定时任务或多消息仪式流程。

下一阶段：

1. 扩充真实天体数据并引入静态数据来源审阅流程。
2. 增加面向 AstrBot 实际运行环境的集成验证。

## Sprint 1 — v0.1.0-alpha

已完成：

- 每日定星：仅根据发送者标识的哈希与 UTC 日期稳定选择天体。
- 单张塔罗抽取：包含正位、逆位和传统牌义。
- 星辰箴言：随机抽取星空主题文本。
- `generate_starpath_record` Native Tool：返回 JSON，不发送消息、不生成最终聊天回复。
- 静态数据：15 个真实天体、22 张大阿尔卡那、30 条箴言。

## 安装

将此目录作为 AstrBot 插件安装目录。插件需要 AstrBot `>=4.27.2`。

## Tool

`generate_starpath_record(mode="daily", spread="single")`

返回：

```json
{
  "record_id": "starpath-...",
  "generated_at": "2026-08-20T09:30:00Z",
  "mode": "daily",
  "spread": "single",
  "star": {},
  "tarot": {},
  "quote": {},
  "metadata": {}
}
```

工具仅接受 `daily` 与 `single`，并返回文化象征内容。Native Agent 负责将该结果转化为面向用户的最终回复。

## 开发与测试

```bash
python -m pytest -q
python -m ruff check .
```

## 数据参考

牌组结构采用 Rider–Waite–Smith 的 78 张牌配置：22 张大阿尔卡那与四个各
14 张的小阿尔卡那花色。[Rider–Waite Tarot 概览](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_Tarot)
与 [Labyrinthos 的花色说明](https://labyrinthos.co/pages/how-to-read-tarot-cards)
用于结构与花色传统的交叉核对；本项目数据保持精简、非预测的文化参考表述。

## 许可证

[MIT](LICENSE)
