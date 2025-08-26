# Claude.md - 基于ContestTrade开发量化交易系统指南

## 项目概述

ContestTrade是一个创新的多智能体（Multi-Agent）量化交易框架，采用内部竞赛机制来构建投资决策。该系统通过数据分析和研究两个阶段的智能体协作，自动发现、评估并跟踪具有投资价值的事件型机会。

## 核心架构理解

### 1. 双阶段工作流程

**第一阶段：数据处理阶段**
- 多个数据分析智能体（Data Analysis Agents）并行工作
- 从多个数据源（新闻、资金流、价格数据等）提取结构化因子
- 通过内部竞赛机制评估因子价值，构建最优因子组合

**第二阶段：研究决策阶段**
- 多个研究员智能体（Research Agents）基于独特交易信念分析
- 使用金融工具集进行深度分析，提交交易提案
- 第二轮内部竞赛评估提案，合成最终资产配置策略

### 2. 关键组件分析

#### 数据源模块 (`contest_trade/data_source/`)
- `hot_money_akshare.py` - 资金流数据
- `price_market_akshare.py` - 价格市场数据
- `sina_news_crawl.py` - 新浪新闻爬取
- `thx_news_crawl.py` - 同花顺新闻爬取

#### 智能体模块 (`contest_trade/agents/`)
- `data_analysis_agent.py` - 数据分析智能体
- `research_agent.py` - 研究智能体
- `prompts.py` - 智能体提示词

#### 竞赛机制 (`contest_trade/contest/`)
- `judger_critic.py` - 信号评判器
- `judger_executor.py` - 执行器
- `judger_weight_optimizer.py` - 权重优化器

#### 工具模块 (`contest_trade/tools/`)
- 股票选择、价格信息、公司信息等金融工具

## 开发指南

### 1. 环境搭建

```bash
# 克隆项目
git clone https://github.com/FinStep-AI/ContestTrade.git
cd ContestTrade

# 创建虚拟环境
conda create -n contesttrade python=3.10
conda activate contesttrade

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置系统

编辑 `config.yaml` 文件，配置必要的API密钥：

```yaml
# 必需配置
LLM:
  url: "your_llm_api_url"
  api_key: "your_api_key"
  model: "your_model_name"

# 可选配置
TUSHARE_KEY: "your_tushare_key"
BOCHA_KEY: "your_bocha_key"
SERP_KEY: "your_serp_key"
LLM_THINKING: "your_thinking_llm_config"
VLM: "your_vlm_config"
```

### 3. 自定义交易信念

编辑 `contest_trade/config/belief_list.json`，定义您的交易策略偏好：

```json
[
  "专注于短期事件驱动机会：优先关注公司公告、并购重组、订单暴增、技术突破等催化事件；偏好中小市值、高波动的题材股，适合激进套利策略。",
  "专注于稳健的确定性事件：关注分红、回购、业绩预告确认、重大合同落地和政策利好等；偏好大盘蓝筹、低波动、确定性高的标的，适合稳健配置。"
]
```

### 4. 扩展开发建议

#### 添加新的数据源

1. 在 `contest_trade/data_source/` 目录下创建新的数据源类
2. 继承 `DataSourceBase` 基类
3. 实现必要的数据获取和处理方法
4. 在配置文件中注册新的数据源

```python
# 示例：创建新的数据源
class CustomDataSource(DataSourceBase):
    def __init__(self, config):
        super().__init__(config)
    
    async def fetch_data(self, trigger_time):
        # 实现数据获取逻辑
        pass
    
    def process_data(self, raw_data):
        # 实现数据处理逻辑
        pass
```

#### 添加新的智能体

1. 在 `contest_trade/agents/` 目录下创建新的智能体类
2. 定义智能体的输入输出格式
3. 实现智能体的核心逻辑
4. 在配置文件中注册新的智能体

```python
# 示例：创建新的研究智能体
class CustomResearchAgent:
    def __init__(self, config):
        self.config = config
    
    async def analyze(self, input_data):
        # 实现分析逻辑
        pass
    
    def generate_signals(self, analysis_result):
        # 实现信号生成逻辑
        pass
```

#### 自定义评判标准

1. 修改 `contest_trade/contest/judger_critic.py`
2. 调整信号评分算法
3. 优化权重分配策略

### 5. 测试策略

#### 单元测试
- 为每个数据源编写测试用例
- 验证智能体的输出格式
- 测试竞赛机制的评分逻辑

#### 集成测试
- 测试完整的工作流程
- 验证数据流转的正确性
- 检查最终输出的质量

#### 回测验证
- 使用历史数据验证策略有效性
- 分析不同市场环境下的表现
- 优化参数配置

### 6. 性能优化

#### 并发优化
- 利用异步编程提高数据获取效率
- 优化智能体的并行执行
- 实现智能的缓存机制

#### 内存管理
- 优化大数据集的处理
- 实现数据流式处理
- 合理使用缓存策略

#### 计算优化
- 优化LLM调用频率
- 实现智能的批处理
- 使用向量化计算

### 7. 监控和日志

#### 系统监控
- 监控智能体的执行状态
- 跟踪API调用频率和成本
- 监控系统资源使用情况

#### 日志记录
- 记录关键决策过程
- 保存中间结果用于分析
- 实现错误追踪和调试

### 8. 部署建议

#### 开发环境
- 使用Docker容器化部署
- 配置开发、测试、生产环境
- 实现自动化部署流程

#### 生产环境
- 使用云服务部署
- 配置负载均衡和自动扩缩容
- 实现高可用性设计

## 风险控制

### 1. 技术风险
- 数据源稳定性监控
- API调用限制和错误处理
- 模型输出的质量验证

### 2. 市场风险
- 设置止损和止盈机制
- 实现风险分散策略
- 监控市场异常情况

### 3. 合规风险
- 确保符合当地金融法规
- 实现交易记录和审计
- 建立风险报告机制

## 持续改进

### 1. 模型优化
- 定期评估智能体表现
- 优化提示词和参数
- 引入新的分析维度

### 2. 策略迭代
- 基于回测结果调整策略
- 适应市场环境变化
- 持续学习新的交易模式

### 3. 社区贡献
- 参与开源社区讨论
- 分享经验和改进建议
- 贡献代码和文档

## 使用TDD开发策略

### 1. 测试驱动开发原则
- **先写测试**：在实现功能前先编写测试用例
- **小步迭代**：每次只实现一个小的功能单元
- **持续重构**：保持代码简洁和可维护性

### 2. 测试框架选择
```python
# 推荐使用pytest进行测试
pip install pytest pytest-asyncio pytest-mock

# 测试文件结构
tests/
├── unit/
│   ├── test_data_sources.py
│   ├── test_agents.py
│   └── test_contest.py
├── integration/
│   ├── test_workflow.py
│   └── test_end_to_end.py
└── conftest.py
```

### 3. 测试示例
```python
# 示例：测试数据源
import pytest
from contest_trade.data_source.hot_money_akshare import HotMoneyAkshare

class TestHotMoneyAkshare:
    @pytest.fixture
    def data_source(self):
        return HotMoneyAkshare({"api_key": "test_key"})
    
    @pytest.mark.asyncio
    async def test_fetch_data(self, data_source):
        # 测试数据获取功能
        result = await data_source.fetch_data("2024-01-01")
        assert result is not None
        assert len(result) > 0
    
    def test_process_data(self, data_source):
        # 测试数据处理功能
        raw_data = {"test": "data"}
        result = data_source.process_data(raw_data)
        assert isinstance(result, dict)
```

### 4. 持续集成
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock
      - name: Run tests
        run: pytest tests/ -v
```

## 模块开发检查清单

### 数据源模块
- [ ] 实现数据获取接口
- [ ] 添加数据验证逻辑
- [ ] 实现错误处理机制
- [ ] 编写单元测试
- [ ] 添加性能监控

### 智能体模块
- [ ] 定义输入输出格式
- [ ] 实现核心分析逻辑
- [ ] 添加配置验证
- [ ] 编写集成测试
- [ ] 优化响应时间

### 竞赛机制模块
- [ ] 实现评分算法
- [ ] 添加权重优化
- [ ] 实现结果聚合
- [ ] 编写压力测试
- [ ] 添加异常处理

## 总结

ContestTrade提供了一个强大的多智能体量化交易框架基础。通过深入理解其架构和组件，您可以：

1. **快速上手**：利用现有的框架快速构建自己的交易系统
2. **灵活扩展**：根据需求添加新的数据源、智能体和工具
3. **持续优化**：通过竞赛机制不断改进决策质量
4. **风险控制**：建立完善的监控和风险控制体系

记住，量化交易是一个持续学习和改进的过程。建议您：

- 从小规模开始，逐步扩大系统规模
- 重视风险控制，不要过度依赖单一策略
- 保持对市场的敏感度，及时调整策略
- 建立完善的测试和验证机制
- 遵循TDD开发策略，确保每个模块都能正常运行

祝您在量化交易的道路上取得成功！
