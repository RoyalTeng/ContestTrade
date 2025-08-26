prompt_for_research_plan = """
<Task>
{task}
</Task>

<Current_Time>
{current_time}
</Current_Time>

<Background_Information>
{background_information}
</Background_Information>

<Available_Tools>
{tools_info}
</Available_Tools>

Please create a detailed step-by-step plan to complete the following user task based on the background information provided.
Each step should be a clear, actionable instruction. Each step should be a one-line description explaining what needs to be done.
Steps should:
1. Be specific and actionable
2. Use appropriate tools from those provided
3. Be arranged in logical order
4. Consider contextual information
5. Return a list of strings, where each element is a step, without unnecessary words or explanations
6. Focus on information gathering or visualization, no analysis or summary steps needed
7. Not exceed 5 steps
8. Output result in language: {output_language}

Please output the action plan in the following format, do not output any other information:
1. xxx
2. xxx
"""

prompt_for_research_choose_tool = """
<Task>
{task}
</Task>

<Current_Time>
{current_time}
</Current_Time>

<Background_Information>
{background_information}
</Background_Information>

<Your_Plan>
{plan}
</Your_Plan>

<Available_Tools>
{tools_info}
</Available_Tools>

<Current_Task_Context>
{tool_call_context}
</Current_Task_Context>

Analyze the following steps and select tools:
## Available Resources
You currently have access to the following analysis tools:
- **Financial Data Tools**: Get company financials, market data, and historical information
- **News & Information Tools**: Search for recent news, announcements, and market updates
- **Research Tools**: Access analyst reports, industry data, and comparative analysis
- **Web Search Tools**: Get real-time information from various sources

## Development Needs Assessment
If you encounter limitations in your analytical capabilities that prevent you from completing high-quality research, you can propose new tool development. Consider whether you need specialized tools for:
- Advanced technical analysis and charting capabilities
- Real-time sentiment analysis from social media platforms
- Alternative data sources (satellite data, credit card spending, etc.)
- Automated financial model building and scenario analysis
- Industry-specific databases and metrics
- Options flow and derivatives analysis tools
- ESG and sustainability metrics analysis
- Cryptocurrency and digital asset analysis
- Or any other specialized analytical capability you deem essential

## Output Format:
You must and can only return a JSON object in the following format enclosed by <Output> and </Output> like:
<Output>
{{
    "tool_name": string, # tool name
    "properties": dict, # tool execution arguments
}}
</Output>

## Tool Usage Rules:
You must always follow these rules to complete the task:
1. After receiving a user task, you will first create an action plan, then call tools according to the action plan to complete the task.
2. Always provide tool calls, otherwise it will fail.
3. Always use correct tool parameters. Do not use variable names in action parameters, use specific values instead.
    - When using the corp_info tool, pay attention to whether its stock_code parameter is valid. If invalid, you need to convert it to a valid format.
4. Never repeat calls to tools that have already been used with exactly the same parameters
5. Do not return any other text format, do not explain your choices, do not apologize, do not express inability to answer.
6. If a step requires multiple tools, choose the most important one.
7. If you have completed all action plans and obtained sufficient information, please use the tool action named "final_report" to provide the final report to the task. This is the only way to complete the task, otherwise you will fall into a loop.
8. If you need to output string, please output in language: {output_language}

Note: 
- Only propose new tools if you identify critical gaps that cannot be addressed by current available tools.
- Be specific about the capabilities and analytical value of any proposed tools.
- Focus on tools that would significantly enhance your research quality and depth.
"""

prompt_for_research_write_result = """
<Task>
{task}
</Task>

<Current_Time>
{current_time}
</Current_Time>

<Background_Information>
{background_information}
</Background_Information>

<Your_Plan>
{plan}
</Your_Plan>

<Available_Tools>
{tools_info}
</Available_Tools>

<Current_Task_Context>
{tool_call_context}
</Current_Task_Context>

Please generate a complete answer based on the user task, current subtask, and the execution steps and results of the subtask.
Requirements:
1. Do not directly answer the user's original question, as the subtask you executed is only part of the reasoning process. Answering the original question prematurely may mislead the user.
2. Integrate information from all steps, including task objectives and execution results
3. Maintain logical consistency and coherence
4. Highlight key findings and conclusions
5. If you find conflicting or insufficient information, please clearly point it out
6. Reflect the contribution of each step in your answer


You have exhausted all available research steps and are not allowed to perform further searches or create Actions. 
Now please complete the task proposed by the user based on the above research information.
Your output language is {output_language}.
Your output format should be like this, enclosed by <Output> and </Output>:
<Output>
{output_format}
</Output>
"""

format_for_symbol_retrieval = """
<stock>
<market>xxx</market>   # market name, e.g. "CN-Stock", "CN-ETF", "HK-Stock", "US-Stock"
<code>xxx</code>
<name>xxx</name>
<reason>xxx</reason>
</stock>
<stock>
<market>xxx</market>
<code>xxx</code>
<name>xxx</name>
<reason>xxx</reason>
</stock>
...
"""

prompt_for_data_analysis_summary_doc = """
Current time is: {trigger_datetime}

Please perform {summary_style} on the following financial documents, extracting key factual information:

{doc_context}

Requirements:
1. {bias_instruction}
2. Extract specific facts, data, and key information
3. While maintaining accuracy, prioritize content related to the goal
4. Organize content by information importance and timeliness
5. Control within {summary_target_tokens} words
6. For each factual description, add corresponding reference tags at the end, such as [1][2]
7. Output result in language: {language}

{summary_style}:
"""

prompt_for_data_analysis_filter_doc = """
Current time is: {trigger_datetime}

Please select the {titles_to_select} most informative documents from the following financial document titles:

{titles_context}

Selection criteria:
1. Contains specific factual information and data
2. Involves important policies, company dynamics, industry changes
3. Information timeliness and importance
4. Avoid repetitive and low-quality content
5. Output result in language: {language}

Please directly output the selected document IDs, separated by commas, such as: 1,5,8,12
"""

prompt_for_community_sentiment_analysis = """
你是专业的社区情绪分析师，擅长从财经社区(雪球、东方财富股吧等)的讨论中提取市场情绪和投资者行为模式。

<数据源信息>
{source_description}
</数据源信息>

<原始数据>
{raw_data}
</原始数据>

<分析任务>
请对以上社区数据进行深度情绪分析，重点关注：

1. **整体市场情绪**
   - 投资者情绪倾向(看多/看空/观望)
   - 情绪强度和波动程度
   - 恐慌指数和贪婪指数

2. **KOL观点追踪**
   - 高影响力用户的核心观点
   - 观点分歧程度
   - 意见领袖态度变化

3. **热门话题识别**
   - 讨论热度最高的股票/板块
   - 新兴话题和催化剂事件
   - 关注度变化趋势

4. **投资者行为模式**
   - 散户情绪特征
   - 资金流向偏好
   - 风险偏好变化

5. **潜在机会和风险**
   - 情绪极端化的标的
   - 可能的反转信号
   - 需要关注的风险点

请输出结构化的分析结果，为后续投资决策提供情绪面参考。
</分析任务>

输出格式要求：
- 使用中文输出
- 条理清晰，重点突出
- 包含具体的数据支撑
- 提供可执行的建议
"""

prompt_for_data_analysis_merge_summary = """
Current time is: {trigger_time}
Analysis Goal: {goal_instruction}

Please merge the following multiple document batch summaries into a unified market information factor:

{combined_summary}

Requirements:
1. Merge duplicate information, retain all important facts
2. Sort by information importance and timeliness
3. {summary_focus}
4. Control within {final_target_tokens} words
5. Form clear market information summary
6. Preserve reference identifiers [numbers] format from original text
7. Output result in language: {language}

Please output {final_description} directly, do not include any other content.
{final_description}:
"""

prompt_for_research_invest_task = """
As a professional researcher with specific belief, you need to find opportunities in the market today. You need to submit up to 5 critical analysis suggestions to the investor.

Your submission should include following parts for EACH opportunity you identify:
1. Does valuable opportunity exist in the market today?
2. Symbol Information of the opportunity
3. Evidence list you find to prove the opportunity is valuable. Judger will use these evidences to judge the opportunity is valuable or not.
4. Based on the evidence_list, you need to give a probability to this opportunity.
5. You need to give a limitation to your suggestion, such as risk, etc. No limitation will be rejected.
6. You should provide between 1 to 5 opportunity suggestions based on what you find in the market. Only submit signals for opportunities you genuinely identify.
7. If accepted, your suggestions will execute when the market opens and hold for one day. So you need to focus on short-term information.
8. Each signal should be independent and focus on different stocks or strategies.
9. If you cannot find 5 valuable opportunities, submit fewer high-quality signals rather than padding with low-quality ones.
"""

prompt_for_research_invest_output_format = """
<signals>
<signal>
<has_opportunity>xxx</has_opportunity>  # yes or no
<action>xxx</action>  # buy or sell
<symbol_code>xxx</symbol_code>     # such as 600519.SH or TSLA
<symbol_name>xxx</symbol_name>  # such as 贵州茅台 or tesla
<evidence_list>        # no more than 20 evidences
<evidence>xxx</evidence>   # a detailed evidence description, including convincing logical inferences which support your suggestion. About 100 words.
<time>xxx</time>           # evidence time
<from_source>xxx</from_source>   # evidence source, from which media name or website name or tools name
...
</evidence_list>
<limitations>
<limitation>xxx</limitation>   # limitations of your suggestion, such as risk, etc.
...
</limitations>
<probability>xxx</probability>  # 0-100
</signal>
<!-- Repeat <signal>...</signal> block for each opportunity you identify, up to 5 signals -->
<!-- Only include signals for genuine opportunities you find in the market -->
</signals>
"""