# Context Engineering

`agent-architecture-analysis` 的域专用参考之一。当用户选择分析 **Context** 时，按本文件的维度和问题分析当前项目中的 Context 来源和组装过程。

## 重点关注

- System Prompt
- Developer Instructions
- Skill Definitions
- Tool Definitions
- Conversation History
- Memory
- Retrieved Information
- Tool Results
- Runtime Information
- Context Assembly
- Context Compression
- Context Pruning
- Context Budget
- Context Lifecycle

## 重点回答

- Context 有哪些来源？
- 这些信息如何进入 Context？
- Context 如何组装？
- 不同信息如何组织？
- Memory 如何进入 Context？
- Tool Result 如何进入 Context？
- Context 太长时如何处理？
- 哪些信息会被压缩？
- 哪些信息会被裁剪？

重点关注实际代码中的 Context 构建过程，而不是只描述理论上的 Context Engineering。

## 守卫

以上列表只是分析维度，不代表当前项目一定存在这些组件。如果无法从代码确认某个机制，不要将其作为事实描述；可以标记为“未发现”或“无法确认”。
