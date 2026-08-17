# Tool Architecture

`agent-architecture-analysis` 的域专用参考之一。当用户选择分析 **Tool** 时，按本文件的维度和问题分析当前项目中的 Tool 相关实现。

## 重点关注

- Tool Definition
- Tool Schema
- Tool Registry
- Tool Discovery
- Tool Selection
- Tool Execution
- Parameter Validation
- Permission
- Timeout
- Retry
- Error Handling
- Tool Result

## 重点回答

- Tool 如何定义？
- Tool 如何注册？
- Agent / LLM 如何发现 Tool？
- 谁决定调用哪个 Tool？
- Tool 如何执行？
- 参数如何校验？
- 如何处理执行失败？
- 如何处理 Timeout / Retry？
- Tool Result 如何返回？
- Tool Result 如何进入 Context？

## 守卫

以上列表只是分析维度，不代表当前项目一定存在这些组件。如果无法从代码确认某个机制，不要将其作为事实描述；可以标记为“未发现”或“无法确认”。
