# 🎨 可视化流程图与交互图

这个文档包含了完整的 Mermaid 可视化图表，可在 VS Code、GitHub 等支持 Mermaid 的环境中直接查看。

---

## 1️⃣ 系统架构图

```mermaid
graph TB
    subgraph "开发环境"
        A["🧑‍💻 开发者<br/>本地开发"]
    end

    subgraph "代码管理"
        B["📦 Git Repository<br/>GitHub"]
    end

    subgraph "CI/CD 编排"
        C["⚡ GitHub Actions<br/>工作流引擎"]
    end

    subgraph "任务执行"
        D["🏃 Self-Hosted Runner<br/>CentOS Server"]
    end

    subgraph "容器层"
        E["🐳 Docker Container<br/>security-scanner:latest"]
    end

    subgraph "扫描工具"
        F["🔍 SQLMap<br/>SQL 注入检测"]
        G["🐍 Python<br/>报告生成"]
    end

    subgraph "结果存储"
        H["💾 GitHub Artifact<br/>report.html + run.log"]
    end

    subgraph "结果查看"
        I["📊 开发者下载<br/>浏览器查看"]
    end

    A -->|git push| B
    B -->|webhook| C
    C -->|分配任务| D
    D -->|启动容器| E
    E -->|执行| F
    F -->|日志| G
    G -->|生成报告| H
    H -->|下载| I
    I -->|分析| A

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#fff9c4
    style G fill:#e0f2f1
    style H fill:#f1f8e9
    style I fill:#ede7f6
```

---

## 2️⃣ 完整工作流执行流程

```mermaid
sequenceDiagram
    participant DEV as 开发者
    participant GIT as GitHub
    participant ACT as Actions
    participant RUN as Runner
    participant DOC as Docker
    participant SQL as SQLMap
    participant RPT as Reporter
    participant ART as Artifact
    participant USER as 用户

    DEV->>GIT: 1. Push Code
    GIT->>ACT: 2. Webhook Event
    ACT->>RUN: 3. Trigger Job
    RUN->>RUN: 4. Init Environment
    
    par Build and Scan
        RUN->>DOC: 5a. Pull Image
        RUN->>DOC: 5b. Start Container
    and Check Status
        RUN->>RUN: 5c. Verify State
    end

    DOC->>SQL: 6. Execute Scan
    SQL->>SQL: 7. Test Injection Points
    SQL->>RUN: 8. Generate run.log

    RUN->>RPT: 9. Call Reporter
    RPT->>RPT: 10. Parse Log
    RPT->>RPT: 11. Render HTML
    RPT->>RUN: 12. Return report.html

    RUN->>ART: 13. Upload Artifact
    ART->>GIT: 14. Store Result

    USER->>GIT: 15. Access Action
    GIT->>ART: 16. Retrieve Artifact
    ART->>USER: 17. Download Files

    USER->>USER: 18. View Report
```

---

## 3️⃣ 分支决策流程图

```mermaid
flowchart TD
    A["🚀 触发事件<br/>Push/Manual/Schedule"]
    
    B{"事件类型?"}
    C{"代码变更<br/>检查"}
    D{"Runner<br/>在线?"}
    E{"环境变量<br/>完整?"}
    F{"Docker<br/>镜像存在?"}
    G{"构建镜像"}
    H{"启动容器"}
    I{"执行扫描"}
    J{"生成报告"}
    K{"上传结果"}
    L{"通知完成"}
    M["❌ 失败流程"]
    N["✅ 成功完成"]

    A --> B
    B -->|Push| C
    B -->|Manual| E
    B -->|Schedule| E
    
    C -->|无变更| M
    C -->|有变更| D
    
    D -->|离线| M
    D -->|在线| E
    
    E -->|缺失| M
    E -->|完整| F
    
    F -->|存在| H
    F -->|不存在| G
    G -->|成功| H
    G -->|失败| M
    
    H -->|成功| I
    H -->|失败| M
    
    I -->|成功| J
    I -->|超时| M
    I -->|目标不可达| M
    
    J -->|成功| K
    J -->|失败| M
    
    K -->|成功| L
    K -->|失败| M
    
    L --> N

    style A fill:#fff9c4
    style N fill:#c8e6c9
    style M fill:#ffcdd2
```

---

## 4️⃣ Docker 容器内部流程

```mermaid
flowchart LR
    A["📥 Container Start<br/>环境变量注入"]
    
    B["✓ 验证 TARGET<br/>URL 必须指定"]
    C["✓ 验证 LEVEL<br/>1-5 范围检查"]
    D["✓ 验证 RISK<br/>1-3 范围检查"]
    E["✓ 创建输出目录<br/>/scans"]
    
    F["🔧 构建 SQLMap 命令"]
    G["sqlmap -u TARGET<br/>--batch<br/>--level=L<br/>--risk=R"]
    
    H["⏳ 执行扫描<br/>1-5 分钟"]
    I["📝 生成 run.log<br/>原始扫描输出"]
    
    J["🐍 调用 generate_report.py"]
    K["1️⃣ find_runlog<br/>查找日志文件"]
    L["2️⃣ analyze<br/>提取漏洞特征"]
    M["3️⃣ render_html<br/>生成美化报告"]
    N["📄 report.html<br/>最终报告"]
    
    O["📦 输出结果<br/>/scans/"]
    P["✅ Container Exit<br/>结果挂载到主机"]

    A --> B --> C --> D --> E
    E --> F --> G
    G --> H --> I
    I --> J --> K --> L --> M --> N
    N --> O --> P

    style A fill:#b3e5fc
    style H fill:#ffe082
    style I fill:#b3e5fc
    style J fill:#c8e6c9
    style N fill:#f8bbd0
    style P fill:#c8e6c9
```

---

## 5️⃣ 错误处理与恢复流程

```mermaid
flowchart TD
    A["⚠️ 错误发生"]
    
    B{"错误类型"}
    
    C["Runner 离线"]
    D["等待 Runner 恢复<br/>最多 6 小时超时"]
    E1{"已恢复?"}
    E2["重新执行任务"]
    E3["标记超时失败"]
    
    F["Docker 问题"]
    F1["检查 Docker Daemon"]
    F2["重启 Docker"]
    F3["重试拉取镜像"]
    
    G["SQLMap 错误"]
    G1["目标不可达?"]
    G2["网络超时?"]
    G3["减少并发<br/>降低 RISK"]
    G4["增加超时时间"]
    
    H["报告生成失败"]
    H1["检查 log 文件"]
    H2["验证 Python 环境"]
    H3["手动调用脚本"]
    
    I["发送通知"]
    J["记录日志<br/>便于分析"]
    K{"是否重试?"}
    L["重新执行"]
    M["标记失败<br/>等待人工介入"]

    A --> B
    B -->|Runner 离线| C --> D --> E1
    E1 -->|Yes| E2 --> I
    E1 -->|No| E3 --> I
    
    B -->|Docker 错误| F --> F1 --> F2 --> F3 --> I
    
    B -->|SQLMap 错误| G --> G1
    G1 -->|Yes| G4 --> I
    G1 -->|No| G2
    G2 -->|Yes| G4 --> I
    G2 -->|No| G3 --> I
    
    B -->|报告生成失败| H --> H1 --> H2 --> H3 --> I
    
    I --> J --> K
    K -->|Yes| L
    K -->|No| M

    style A fill:#ffcdd2
    style I fill:#fff9c4
    style M fill:#ffcdd2
```

---

## 6️⃣ 用户交互流程图

```mermaid
flowchart TD
    subgraph "开发者工作流"
        D1["👨‍💻 本地开发<br/>编写/修改代码"]
        D2["📝 提交更改<br/>git add & commit"]
        D3["⬆️ 推送到 GitHub<br/>git push origin main"]
        D4["⏳ 等待扫描<br/>GitHub Actions 执行"]
        D5["📥 下载报告<br/>Artifact"]
        D6["📊 查看分析报告<br/>report.html"]
        D7{"是否有漏洞?"}
        D8["🔧 修复代码<br/>回到 D1"]
        D9["✅ 提交修复<br/>回到 D2"]
    end

    subgraph "安全团队工作流"
        S1["🔐 登录 GitHub"]
        S2["🎯 选择工作流<br/>Security Scan"]
        S3["⚙️ 配置参数<br/>TARGET/LEVEL/RISK"]
        S4["▶️ 手动触发"]
        S5["⏱️ 监听执行<br/>查看日志"]
        S6["📥 下载报告"]
        S7["🔍 深度分析<br/>漏洞评估"]
        S8["📋 生成安全报告<br/>分配修复优先级"]
        S9["👥 通知开发者<br/>安排修复"]
    end

    subgraph "运维工作流"
        O1["⚙️ 初始化系统<br/>部署 Runner"]
        O2["🔍 日常监控<br/>检查 Runner 状态"]
        O3["📊 查看指标<br/>执行时间/成功率"]
        O4["🧹 定期维护<br/>清理容器/缓存"]
        O5{"超过阈值?"}
        O6["🚨 发送告警<br/>邮件/Slack"]
        O7["🔧 排查问题<br/>查看日志"]
        O8["🔄 重启服务<br/>恢复正常"]
    end

    D1 --> D2 --> D3 --> D4 --> D5 --> D6 --> D7
    D7 -->|Yes| D8 --> D9 --> D1
    D7 -->|No| D9

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9

    O1 --> O2 --> O3 --> O4 --> O5
    O5 -->|Yes| O6 --> O7 --> O8 --> O2
    O5 -->|No| O4

    style D1 fill:#e3f2fd
    style S1 fill:#f3e5f5
    style O1 fill:#e8f5e9
    style D7 fill:#fff9c4
    style O5 fill:#fff9c4
    style D8 fill:#ffccbc
    style S8 fill:#c8e6c9
```

---

## 7️⃣ 数据流向图

```mermaid
graph TB
    subgraph "Input Sources"
        I1["GitHub Push Event"]
        I2["Manual Trigger"]
        I3["Cron Schedule"]
        I4["Environment Variables"]
    end

    subgraph "Processing"
        P1["Workflow Parser"]
        P2["Event Router"]
        P3["Task Scheduler"]
        P4["Container Orchestrator"]
        P5["SQLMap Engine"]
        P6["Report Generator"]
    end

    subgraph "Storage"
        S1["GitHub Artifact"]
        S2["Local Cache"]
        S3["Logs"]
    end

    subgraph "Output"
        O1["HTML Report"]
        O2["JSON Data"]
        O3["Log Files"]
        O4["Notifications"]
    end

    I1 --> P1
    I2 --> P1
    I3 --> P1
    I4 --> P3
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    
    P2 --> S2
    P5 --> S3
    P6 --> S3
    
    P6 --> O1
    P6 --> O2
    S3 --> O3
    P6 --> O4
    
    O1 --> S1
    O2 --> S1
    O3 --> S1

    style I1 fill:#bbdefb
    style I2 fill:#bbdefb
    style I3 fill:#bbdefb
    style I4 fill:#bbdefb
    style P5 fill:#ffe0b2
    style P6 fill:#c8e6c9
    style O1 fill:#f8bbd0
    style S1 fill:#d1c4e9
```

---

## 8️⃣ 状态机图

```mermaid
stateDiagram-v2
    [*] --> Created: Event Triggered
    
    Created --> Queued: Job Assigned
    
    Queued --> Initializing: Runner Available
    Queued --> Failed: Timeout
    
    Initializing --> BuildingImage: Env Ready
    Initializing --> Failed: Env Error
    
    BuildingImage --> Scanning: Image Built
    BuildingImage --> Failed: Build Failed
    
    Scanning --> GeneratingReport: Scan Complete
    Scanning --> Failed: Scan Error\nTimeout\nTarget Unreachable
    
    GeneratingReport --> Uploading: Report Generated
    GeneratingReport --> Failed: Generation Error
    
    Uploading --> Completed: Upload Success
    Uploading --> Failed: Upload Failed
    
    Completed --> [*]
    Failed --> [*]
    
    note right of Created
        初始状态
        工作流已创建
    end note
    
    note right of Queued
        等待状态
        等待 Runner 可用
    end note
    
    note right of Scanning
        扫描中
        执行 SQL 注入检测
        耗时 1-5 分钟
    end note
    
    note right of Completed
        完成状态
        报告已上传
        用户可下载
    end note
    
    note right of Failed
        失败状态
        需要人工介入
    end note
```

---

## 9️⃣ 性能优化路径图

```mermaid
graph LR
    A["当前性能<br/>2-6 分钟"]
    
    B1["优化 1:<br/>镜像缓存<br/>-10s"]
    B2["优化 2:<br/>并行扫描<br/>-30s"]
    B3["优化 3:<br/>预构建镜像<br/>-15s"]
    B4["优化 4:<br/>结果缓存<br/>-20s"]
    
    C["改进后<br/>1-3 分钟<br/>50% 提升"]
    
    A --> B1 --> C
    A --> B2 --> C
    A --> B3 --> C
    A --> B4 --> C

    style A fill:#fff9c4
    style C fill:#c8e6c9
    style B1 fill:#e1f5fe
    style B2 fill:#e1f5fe
    style B3 fill:#e1f5fe
    style B4 fill:#e1f5fe
```

---

## 🔟 可靠性对标图

```mermaid
xychart-beta
    title "系统指标目标 vs 实际"
    x-axis [触发延迟, Runner调度, 镜像拉取, 扫描执行, 报告生成, 上传结果, 总耗时]
    y-axis "秒数" 0 --> 400
    line [1, 10, 30, 300, 10, 20, 600]  title "目标值"
    line [0.5, 8, 20, 240, 5, 15, 360]  title "実际值"
```

---

## 使用建议

### 📌 在线查看
这些 Mermaid 图表可以在以下平台直接查看:
- ✅ GitHub (README.md 中)
- ✅ VS Code (使用 Mermaid 插件)
- ✅ Mermaid Live Editor: https://mermaid.live
- ✅ GitLab, Gitea 等

### 💾 导出为图片
```bash
# 使用 mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# 转换为 PNG
mmdc -i diagram.md -o diagram.png

# 转换为 SVG
mmdc -i diagram.md -o diagram.svg
```

### 🎯 查看完整图表
- 顺序图 (Sequence Diagram): 流程 #2
- 状态机 (State Machine): 流程 #8
- 甘特图、类图等可根据需要扩展

---

**最后更新**: 2026-03-26 | **格式**: Mermaid Diagrams
