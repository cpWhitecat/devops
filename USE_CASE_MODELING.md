# 📋 用例模型深度分析

这个文档提供了详细的用例建模、业务规则、活动图和交互模式。

---

## 📊 用例概览 (Actor-Use Case Matrix)

### 角色定义

| 角色 | 描述 | 权限 | 职责 |
|------|------|------|------|
| **开发者** | 编写和提交代码的工程师 | 提交代码、查看报告 | 编写安全代码、修复漏洞 |
| **安全工程师** | 负责安全测试和评估的专家 | 手动触发、自定义参数 | 定义扫描策略、评估风险 |
| **系统管理员** | 维护基础设施的运维人员 | 管理 Runner、维护系统 | 保证系统可用性、性能 |
| **GitHub Actions** | 自动化系统 | 执行工作流、管理任务 | 编排任务执行 |
| **SQLMap** | 扫描工具 | 执行扫描、生成日志 | 检测 SQL 注入漏洞 |

---

## 🎯 主要用例详解

### 用例 UC-001: 自动触发安全扫描

**用例标题**: 开发者提交代码后自动执行安全扫描

**参与者**: 
- 主要: 开发者, GitHub Actions
- 次要: SQLMap, Reporter

**前置条件**:
```
✓ Runner 已在线并就绪
✓ Docker 镜像已构建
✓ 工作流文件已就位 (.github/workflows/security-scan-runner.yml)
✓ 环境变量已配置 (GITHUB_TOKEN, REPO_URL)
✓ 代码仓库已连接到 GitHub
```

**基本流程**:
1. 开发者在本地修改代码
   ```bash
   # 修改 src/app.py 添加新功能
   vim src/app.py
   ```

2. 开发者提交变更
   ```bash
   git add .
   git commit -m "feat: add new API endpoint"
   ```

3. 开发者推送到 GitHub
   ```bash
   git push origin main
   ```

4. GitHub 检测 push 事件
   - 触发 webhook
   - 加载 `.github/workflows/security-scan-runner.yml`
   - 解析工作流配置

5. GitHub Actions 初始化任务
   - 检查触发条件
   - 验证分支是 main
   - 检查修改的文件路径
   - 分配 job ID

6. Actions 查找可用 Runner
   - 检查标签匹配
   - 查找状态为 "Idle" 的 Runner
   - 分配任务到 Runner

7. Runner 接收并准备环境
   ```bash
   # Runner 加载环境变量
   source /opt/github-runner/.env
   
   # 创建工作目录
   mkdir -p ${GITHUB_WORKSPACE}/scans
   
   # 验证必要的二进制文件
   which docker
   which python3
   ```

8. Runner 执行 Docker 容器
   ```bash
   docker run -d \
     -e TARGET="http://target.com" \
     -e LEVEL="1" \
     -e RISK="1" \
     -v ${GITHUB_WORKSPACE}/scans:/scans \
     security-scanner:latest
   ```

9. 容器内 SQLMap 执行扫描
   - 验证目标 URL 可达
   - 探测参数
   - 检测注入点
   - 执行 payload 测试
   - 生成 run.log

10. 报告生成器处理日志
    - 读取 run.log
    - 解析漏洞特征
    - 生成 HTML report.html

11. Runner 上传结果
    ```bash
    # 打包结果
    zip -r artifact.zip ./scans/
    
    # 上传到 GitHub Artifact
    curl -X POST ... artifact.zip
    ```

12. GitHub 存储 Artifact
    - 存储在 GitHub 服务器
    - 可保留 30 天（默认）

13. GitHub Actions UI 显示完成
    - 显示 ✓ 状态
    - 提供下载链接

14. 开发者收到通知（可选）
    - 邮件通知
    - Slack 消息
    - GitHub 通知

**异常流程**:

| 异常 | 触发条件 | 处理方案 |
|------|---------|--------|
| 无可用 Runner | Runner 离线超过 6 小时 | 工作流失败，发送告警 |
| Docker 镜像缺失 | 镜像未预先构建 | 触发构建，然后等待 |
| 目标不可达 | 网络故障或防火墙 | SQLMap 超时，报错输出 |
| 扫描卡顿 | SQL 查询复杂、网络慢 | 设置超时，中断并记录 |
| 报告生成失败 | Python 脚本错误 | 使用默认模板或文本输出 |

**后置条件**:
```
✓ 报告已生成
✓ 结果已上传到 Artifact
✓ 工作流状态已更新
✓ 用户可下载报告
```

**业务规则**:
- BR-1: 只有 main 分支的 push 事件才触发扫描
- BR-2: 必须修改 `security-scanner/` 或应用代码才能触发
- BR-3: 扫描超时时间不超过 工作流 timeout-minutes 设置
- BR-4: 报告必须包含目标 URL、扫描时间、发现的漏洞列表

---

### 用例 UC-002: 手动执行自定义参数扫描

**用例标题**: 安全团队手动触发扫描并指定参数

**参与者**: 
- 主要: 安全工程师
- 次要: GitHub Actions, SQLMap

**前置条件**:
```
✓ 安全工程师有 GitHub 仓库访问权限
✓ 了解 SQLMap 参数含义
✓ 明确扫描目标 URL
✓ Runner 在线
```

**基本流程**:
1. 安全工程师访问 GitHub 仓库
   ```
   https://github.com/cpWhitecat/devops
   ```

2. 导航到 Actions 选项卡
   ```
   Repository → Actions → 查看所有工作流
   ```

3. 选择 "Security Scan with SQLMap" 工作流
   ```
   展示工作流运行历史和最后一次运行结果
   ```

4. 点击 "Run workflow" 按钮
   ```
   出现输入框接收参数
   ```

5. 输入扫描参数
   ```
   Target URL: https://internal-app.company.com/login
   LEVEL: 3 (中等深度)
   RISK: 2 (中等风险)
   ```

6. 点击 "Run" 执行
   ```
   保存参数并提交
   Actions 立即开始处理
   ```

7. 后续流程同 UC-001 的步骤 6-14

**参数选择指南**:

```
LEVEL (扫描深度) :
├─ 1 : 快速扫描，只测试基本技术 (2-3 分钟)
├─ 2 : 标准扫描，增加参数和技术 (3-5 分钟)
├─ 3 : 深度扫描，详细测试 (5-10 分钟) ⭐ 推荐
├─ 4 : 很深的扫描，包括高级技术 (10-20 分钟)
└─ 5 : 极端扫描，包括所有可能的技术 (20-40 分钟)

RISK (风险等级) :
├─ 1 : 低风险，使用安全的 payload
├─ 2 : 中风险，可能导致数据库查询缓慢 ⭐ 平衡
└─ 3 : 高风险，可能导致目标系统锁定或数据修改

选择建议:
├─ 开发环境: LEVEL=3, RISK=2 (平衡)
├─ 生产环境: LEVEL=1, RISK=1 (保守)
└─ 安全审计: LEVEL=5, RISK=3 (激进，仅在有人监控时)
```

**异常处理**:
- 参数验证失败: 返回错误消息并要求重新输入
- 权限不足: 提示 403 Forbidden
- 工作流文件有误: 显示 YAML 语法错误

---

### 用例 UC-003: 查看和分析扫描报告

**用例标题**: 用户下载和分析最终的 HTML 报告

**参与者**: 
- 主要: 开发者、安全工程师
- 次要: GitHub Artifact

**前置条件**:
```
✓ 扫描已完成
✓ 报告已生成并上传
✓ 用户可访问 GitHub Actions
```

**基本流程**:

1. 用户访问 Actions 运行页面
   ```
   GitHub → Actions → 选择具体的工作流运行
   ```

2. 查看工作流执行摘要
   ```
   ✓ 运行状态: 成功/失败
   • 耗时: 3分45秒
   • 触发者: push event / manual trigger
   • 分支: main
   • commit: abc123def
   ```

3. 定位 Artifact 下载区
   ```
   向下滚动到 Artifacts 部分
   看到 "security-scan-results-123" 
   点击下载按钮
   ```

4. 浏览器下载 ZIP 文件
   ```
   security-scan-results-123.zip (约 2-5 MB)
   自动保存到下载文件夹
   ```

5. 解析 ZIP 文件
   ```bash
   cd ~/Downloads
   unzip security-scan-results-123.zip
   cd security-scan-results-123
   ls -la
   # report.html          (HTML 报告，用浏览器打开)
   # run.log              (完整的 SQLMap 日志)
   # [其他 SQLMap 文件]
   ```

6. 用浏览器打开 report.html
   ```bash
   open report.html
   # 或
   firefox report.html
   ```

7. 浏览报告内容
   ```
   ┌────────────────────────────────┐
   │         扫描摘要                │
   ├────────────────────────────────┤
   │ 目标 URL: https://target.com   │
   │ 扫描时间: 2026-03-26 14:30:45 │
   │ 耗时: 120 秒                   │
   │ 数据库: MySQL 5.7             │
   │ 风险等级: [RED] 高              │
   └────────────────────────────────┘
   
   ┌────────────────────────────────┐
   │      发现的漏洞                │
   ├────────────────────────────────┤
   │ [1] SQL 注入 - login_id 参数  │
   │     位置: POST /api/login      │
   │     严重性: 严重                │
   │     Payload: ...               │
   │ [2] SQL 注入 - search 参数    │
   │     位置: GET /search          │
   │     严重性: 中等                │
   └────────────────────────────────┘
   
   ┌────────────────────────────────┐
   │      详细日志 (可选)            │
   ├────────────────────────────────┤
   │ [*] Starting scan...           │
   │ [+] Parameter 'id' is vulnerable│
   │ [>] 100 payloads tested        │
   │ ... (完整日志)                  │
   └────────────────────────────────┘
   ```

8. 分析报告并标记行动项
   ```
   分析步骤:
   1. 识别严重漏洞 (需立即修复)
   2. 评估受影响的功能
   3. 估算修复工作量
   4. 优先级排序
   5. 分配给开发团队
   ```

9. 创建修复计划
   ```
   优先级 1 (立即修复):
   └─ SQL 注入 - login_id 参数
      └─ 预计 2 天
      └─ 分配给: 张三
   
   优先级 2 (本周修复):
   └─ SQL 注入 - search 参数
      └─ 预计 1 天
      └─ 分配给: 李四
   
   优先级 3 (下周修复):
   └─ ... (其他发现)
   ```

10. 反馈给开发者
    ```
    提交 GitHub Issue 或评论:
    
    提问: 发现了以下安全问题:
    
    ## 严重问题 🔴
    - login 接口存在 SQL 注入漏洞
      参考: #123-sql-injection-login
      
    ## 中等问题 🟠
    - search 接口参数未过滤
      参考: #124-sql-injection-search
      
    请在 7 天内修复这些问题
    ```

**报告字段解释**:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           HTML 报告字段说明               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                          ┃
┃ [目标 URL]                               ┃
┃  • 被扫描的 Web 应用地址                 ┃
┃  • 例: https://api.example.com/users    ┃
┃                                          ┃
┃ [数据库类型]                             ┃
┃  • 检测到的后端数据库                    ┃
┃  • 例: MySQL 5.7, PostgreSQL 10         ┃
┃  • 对修复方案有指导意义                  ┃
┃                                          ┃
┃ [漏洞列表]                               ┃
┃  • 检测到的每个 SQL 注入点              ┃
┃  • 包括参数名、请求位置（GET/POST）     ┃
┃  • payload 示例                          ┃
┃                                          ┃
┃ [严重性等级]                             ┃
┃  • 红色 (严重): 立即修复                 ┃
┃  • 橙色 (高): 本周修复                   ┃
┃  • 黄色 (中): 本月修复                   ┃
┃  • 蓝色 (低): 持续改进                  ┃
┃                                          ┃
┃ [完整日志]                               ┃
┃  • SQLMap 的原始输出                     ┃
┃  • 用于技术深入分析                      ┃
┃  • Payload 和响应示例                    ┃
┃                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

### 用例 UC-004: 系统维护和监控

**用例标题**: 系统管理员维护 Runner 和扫描系统

**参与者**:
- 主要: 系统管理员
- 次要: Docker, GitHub, 监控系统

**任务流程**:

#### 任务 T1: 日常健康检查 (每天 09:00)

```
1. 检查 Runner 在线状态
   $ docker ps | grep github-runner
   # 输出: github-runner 正常运行
   
2. 查看 Runner 日志
   $ docker logs github-runner --tail 20
   # 检查是否有错误症状
   
3. 检查网络连接
   $ docker exec github-runner ping github.com
   # 验证网络正常
   
4. 查看 GitHub Actions 成功率
   访问: https://github.com/cpWhitecat/devops/actions
   目标: 最近 24 小时成功率 > 95%
   
5. 若有异常，进行排查并记录
```

#### 任务 T2: 周期性维护 (每周一 14:00)

```
1. 清理 Docker 缓存
   $ docker system prune -a --volumes
   # 释放磁盘空间
   
2. 更新 SQLMap 工具
   $ docker pull security-scanner:latest
   $ docker tag security-scanner:latest security-scanner:prev
   
3. 检查日志文件大小
   $ du -sh /var/log/docker-*
   # 若超过 1GB，进行归档
   
4. 备份 Runner 配置
   $ tar -czf runner-backup-$(date +%Y%m%d).tar.gz /opt/github-runner/
   
5. 更新文档和 Readme
```

#### 任务 T3: 容量规划 (每月一日)

```
1. 收集月度指标
   • 工作流执行次数
   • 平均耗时
   • 失败率
   • 扫描目标数量
   
2. 分析趋势
   • 是否需要扩容?
   • 性能是否下降?
   • 是否需要优化?
   
3. 容量规划决策
   └─ 若工作负载 > 150%: 考虑添加 Runner
   └─ 若成功率 < 90%: 进行性能审计
   └─ 若磁盘使用 > 80%: 扩展存储
```

---

## 🔀 活动图

### 活动 A1: 代码扫描工作流

```
开始
 │
 ▼
 ┌─────────────────┐
 │  Push 代码      │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │GitHub 事件触发  │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │Actions 初始化   │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────────────────────┐
 │ 查找可用 Runner                 │
 │ [条件分支]                      │
 └────────┬────────────────────────┘
          │
     ┌────┴─────┐
     │           │
   Runner      无 Runner
   在线        可用
     │           │
     ▼           ▼
   继续     [等待/失败]
     │           │
     ▼           ▼
 ┌──────────┐  ┌──────────┐
 │ 拉取镜像 │  │ 标记失败 │
 └────┬─────┘  └──────────┘
      │
      ▼
  ┌──────────┐
  │ 启动容器 │
  └────┬─────┘
       │
       ▼
  ┌──────────────┐
  │ 执行 SQLMap  │
  └────┬─────────┘
       │
   ┌───┴──────┐
   │           │
  成功       异常
   │           │
   ▼           ▼
┌──────────┐ ┌──────────┐
│生成报告  │ │记录错误  │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            │
┌──────────┐      │
│上传结果  │      │
└────┬─────┘      │
     │            │
     └────┬───────┘
          │
          ▼
     ┌─────────┐
     │  完成   │
     └─────────┘
```

---

## 📋 业务规则 (Business Rules)

### BR-001 : 触发条件
```
IF push to 'main' AND (code changed OR scanner/ changed)
THEN execute security scan workflow
```

### BR-002 : 参数验证
```
IF LEVEL NOT IN [1,5] THEN reject
IF RISK NOT IN [1,3] THEN reject
IF TARGET not valid URL THEN reject
```

### BR-003 : 超时管理
```
IF scan duration > 5 minutes THEN 
    SET status = timeout
    TERMINATE container
    LOG error
```

### BR-004 : 报告质量
```
IF HTML report generation fails THEN
    USE fallback template
    USE raw log output
    NOTIFY admin
```

### BR-005 : 访问控制
```
IF NOT member of devops repo THEN
    DENY manual trigger permission
IF NOT have admin role THEN
    DENY Runner configuration
```

---

## 🎓 学习教案

### 场景 S1: 新员工入职培训

```
时间: 30 分钟
对象: 新入职开发者

步骤:
1. 系统演示 (10 分钟)
   • 展示代码 push → 报告生成全流程
   
2. 操作演练 (15 分钟)
   • 提交测试代码
   • 观察工作流执行
   • 下载并查看报告
   
3. Q&A (5 分钟)
   • 回答疑问
   • 补充说明
```

### 场景 S2: 安全团队参数培训

```
时间: 60 分钟
对象: 安全工程师

内容:
1. SQLMap 工具介绍 (15 分钟)
   • SQL 注入原理
   • 检测方法
   
2. 参数详解 (20 分钟)
   • LEVEL: 扫描深度
   • RISK: 风险等级
   • 其他参数
   
3. 实战演练 (20 分钟)
   • 在测试环境执行
   • 解读报告结果
   
4. 最佳实践 (5 分钟)
   • 选择合适参数
   • 避免误触发
```

---

## ✅ 验收标准

### 功能验收 (FA)

- [ ] FA-001: 代码 push 能自动触发扫描
- [ ] FA-002: 手动触发能接收参数输入
- [ ] FA-003: 扫描完成能生成 HTML 报告
- [ ] FA-004: 报告能正确上传到 Artifact
- [ ] FA-005: 用户能下载并查看报告
- [ ] FA-006: 报告包含所有必要信息

### 非功能验收 (NFA)

- [ ] NFA-001: 端到端耗时 < 10 分钟
- [ ] NFA-002: 报告加载时间 < 3 秒
- [ ] NFA-003: 扫描准确率 > 95%
- [ ] NFA-004: 系统可用性 > 99%
- [ ] NFA-005: 支持并发扫描 (最少 3 个)

### 安全验收 (SA)

- [ ] SA-001: Token 不泄露到日志
- [ ] SA-002: 数据在传输中加密
- [ ] SA-003: 访问控制正确实施
- [ ] SA-004: 审计日志完整记录

---

**最后更新**: 2026-03-26 | **维护者**: cpWhitecat
