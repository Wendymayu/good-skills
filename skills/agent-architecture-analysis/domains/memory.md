# Memory Architecture

`agent-architecture-analysis` 的域专用参考之一。当用户选择分析 **Memory** 时，按本文件的维度和问题分析当前项目中的 Memory 相关实现。

## 重点关注

- Memory Extraction
- Memory Write
- Memory Store
- Memory Retrieval
- Memory Ranking
- Memory Update
- Memory Merge
- Memory Conflict
- Memory Lifecycle
- Memory → Context

## 重点回答

- 什么信息会成为 Memory？
- Memory 如何产生？
- Memory 如何写入？
- Memory 存在哪里？
- Memory 如何检索？
- Memory 如何排序？
- 如何处理重复？
- 如何处理更新？
- 如何处理 Merge？
- 如何处理 Conflict？
- Memory 如何进入 Context？
- 谁负责 Memory Lifecycle？

## 若项目已有 Memory 实现

如果当前项目已经存在 Memory 实现：

1. 解释 Memory 的产生方式；
2. 解释 Memory 的存储方式；
3. 解释 Memory 的检索方式；
4. 解释 Memory 如何进入 Agent Context；
5. 分析 Memory 的生命周期。

## 守卫

以上列表只是分析维度，不代表当前项目一定存在这些组件。如果无法从代码确认某个机制，不要将其作为事实描述；可以标记为“未发现”或“无法确认”。
