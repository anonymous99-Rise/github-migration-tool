# GitHub 迁移计划

## 背景
- 旧账号（anonymous99-Rise）已积累 178 个仓库
- 新账号（待定）接手，避免频繁操作导致再次被封

## 阶段规划

### Phase 0：这周准备（8月5日-8月9日）
**哥哥负责：**
- [ ] 新账号改邮箱、2FA、密码
- [ ] 手动 fork 13 个大仓库（>400MB）
- [ ] 提供新账号 username + token

**大仓库清单（需手动 fork）：**
```
treat_v1.0.2           4.4G
Penetration_Testing_POC 3.0G
dls-monitor             1.8G
douyin-hot-hub          1.5G
Vulnerability-Wiki      779M
DFYXSec-Wiki-Book       645M
NSFW-collector          636M
NCE_learning            618M
web3-monitor            607M
ai-agent-book           550M
aggregator              513M
Poc-Monitor             481M
heartWall               383M
```

### Phase 1：养号（8月10日-8月12日）
**哥哥负责：**
- 新账号正常浏览、star 几个项目
- 避免任何高危操作
- 等待 48-72 小时

### Phase 2：迁移（8月13日起）
**脚本负责：**
- 164 个仓库分批迁移
- 每批 20 个，间隔 5 分钟
- 断点续传

**迁移配置：**
- BATCH_SIZE = 20
- BATCH_DELAY = 300 秒（5分钟）
- SINGLE_DELAY = 3 秒

**预计耗时：**
- 9 批次 × ~5分钟/批次 ≈ 45 分钟（不含实际推送时间）
- 总计约 1.5-2 小时

### Phase 3：Star 恢复（迁移完成后）
- 获取旧账号 star 列表
- 新账号逐个 star（每批 20 个，间隔 5 分钟）
- 避免一次性全部 star

## 风控措施
1. 批次延迟（5分钟）分散 API 请求
2. 单个操作间隔（3秒）避免突发
3. 新账号养号 3 天后再迁移
4. Star 操作延后到迁移完成后单独进行
5. 不在同一天内完成所有操作
