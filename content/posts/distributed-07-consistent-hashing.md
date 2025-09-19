---
title: "分布式系统基础：一致性哈希算法深度解析与实现"
date: 2024-09-19T16:00:00+08:00
draft: false
tags: ["分布式系统", "一致性哈希", "负载均衡", "数据分片", "哈希环"]
categories: ["分布式系统"]
author: "lesshash"
description: "深入理解一致性哈希算法：分布式系统中数据分片和负载均衡的核心技术，从基本原理到工程实现的完整指南"
---

## 引言

一致性哈希(Consistent Hashing)是分布式系统中解决数据分片和负载均衡问题的重要算法。由David Karger等人在1997年提出，该算法能够在节点动态加入或离开时，最小化数据的重新分布，广泛应用于分布式缓存、分布式存储和CDN等系统中。

## 问题背景

### 传统哈希的局限性

在分布式系统中，我们需要将数据分布到多个节点上：

```
传统哈希分片：
┌─────────────────────────────────────┐
│ hash(key) % N = 节点索引            │
│                                     │
│ 问题：                              │
│ • 节点数量变化时，几乎所有数据需要重新分布 │
│ • 扩容/缩容成本极高                 │
│ • 数据迁移量巨大                   │
└─────────────────────────────────────┘

示例：
3个节点时：hash("key1") % 3 = 1
4个节点时：hash("key1") % 4 = 2  # 节点变了！
```

### 一致性哈希解决方案

#### 流程图表


**关系流向：**
```
A[一致性哈希优势] → B[最小化数据迁移]
A → C[良好的负载均衡]
A → D[高可扩展性]
A → E[容错能力]
B → F[节点变化时只影响相邻数据]
```

## 一致性哈希算法原理

### 哈希环概念

```
一致性哈希环：
        0
        ┌─┐
   359° │ │ 1°
      ┌─┘ └─┐
  358°│     │2°
     │       │
  357°│   ●   │3°    ● = 数据
     │ Node1 │       ○ = 节点
  356°│       │4°
      └─┐ ┌─┘
   355° │○│ 5°
        └─┘
       Node2

特点：
• 0-359度的环形空间 (实际为 0 - 2^32-1)
• 节点和数据都映射到环上
• 数据存储在顺时针方向第一个节点
```

## 基础实现

### 核心数据结构

```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentSkipListMap;

/**
 * 一致性哈希实现
 */
public class ConsistentHash<T> {

    /**
     * 哈希环节点
     */
    public static class HashNode<T> {
        private final String nodeId;
        private final T node;
        private final long hash;
        private final boolean isVirtual;
        private final String realNodeId;

        public HashNode(String nodeId, T node, long hash, boolean isVirtual, String realNodeId) {
            this.nodeId = nodeId;
            this.node = node;
            this.hash = hash;
            this.isVirtual = isVirtual;
            this.realNodeId = realNodeId;
        }

        public String getNodeId() { return nodeId; }
        public T getNode() { return node; }
        public long getHash() { return hash; }
        public boolean isVirtual() { return isVirtual; }
        public String getRealNodeId() { return realNodeId; }

        @Override
        public String toString() {
            return String.format("HashNode{id='%s', hash=%d, virtual=%s}",
                               nodeId, hash, isVirtual);
        }
    }

    // 哈希环 - 使用TreeMap保持有序
    private final ConcurrentSkipListMap<Long, HashNode<T>> ring;

    // 真实节点映射
    private final ConcurrentHashMap<String, T> realNodes;

    // 虚拟节点数量
    private final int virtualNodeCount;

    // 哈希函数
    private final MessageDigest md5;

    public ConsistentHash(int virtualNodeCount) {
        this.virtualNodeCount = virtualNodeCount;
        this.ring = new ConcurrentSkipListMap<>();
        this.realNodes = new ConcurrentHashMap<>();

        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5算法不可用", e);
        }
    }

    /**
     * 添加节点
     */
    public void addNode(String nodeId, T node) {
        if (realNodes.containsKey(nodeId)) {
            throw new IllegalArgumentException("节点已存在: " + nodeId);
        }

        realNodes.put(nodeId, node);

        // 添加真实节点
        long realHash = hash(nodeId);
        HashNode<T> realNode = new HashNode<>(nodeId, node, realHash, false, nodeId);
        ring.put(realHash, realNode);

        // 添加虚拟节点
        for (int i = 0; i < virtualNodeCount; i++) {
            String virtualNodeId = nodeId + "#" + i;
            long virtualHash = hash(virtualNodeId);
            HashNode<T> virtualNode = new HashNode<>(virtualNodeId, node, virtualHash, true, nodeId);
            ring.put(virtualHash, virtualNode);
        }

        System.out.printf("添加节点 %s: 1个真实节点 + %d个虚拟节点%n", nodeId, virtualNodeCount);
    }

    /**
     * 移除节点
     */
    public void removeNode(String nodeId) {
        T removedNode = realNodes.remove(nodeId);
        if (removedNode == null) {
            throw new IllegalArgumentException("节点不存在: " + nodeId);
        }

        // 移除所有相关的节点（真实+虚拟）
        Iterator<Map.Entry<Long, HashNode<T>>> iterator = ring.entrySet().iterator();
        int removedCount = 0;

        while (iterator.hasNext()) {
            Map.Entry<Long, HashNode<T>> entry = iterator.next();
            HashNode<T> hashNode = entry.getValue();

            if (nodeId.equals(hashNode.getRealNodeId())) {
                iterator.remove();
                removedCount++;
            }
        }

        System.out.printf("移除节点 %s: 共移除 %d 个节点位置%n", nodeId, removedCount);
    }

    /**
     * 获取负责处理指定key的节点
     */
    public T getNode(String key) {
        if (ring.isEmpty()) {
            return null;
        }

        long keyHash = hash(key);

        // 查找顺时针方向第一个节点
        Map.Entry<Long, HashNode<T>> entry = ring.ceilingEntry(keyHash);

        // 如果没找到，说明需要回到环的开始
        if (entry == null) {
            entry = ring.firstEntry();
        }

        return entry.getValue().getNode();
    }

    /**
     * 获取负责处理指定key的节点ID
     */
    public String getNodeId(String key) {
        if (ring.isEmpty()) {
            return null;
        }

        long keyHash = hash(key);
        Map.Entry<Long, HashNode<T>> entry = ring.ceilingEntry(keyHash);

        if (entry == null) {
            entry = ring.firstEntry();
        }

        return entry.getValue().getRealNodeId();
    }

    /**
     * 获取多个副本节点
     */
    public List<T> getNodes(String key, int replicaCount) {
        if (ring.isEmpty()) {
            return Collections.emptyList();
        }

        long keyHash = hash(key);
        List<T> nodes = new ArrayList<>();
        Set<String> addedRealNodes = new HashSet<>();

        Map.Entry<Long, HashNode<T>> entry = ring.ceilingEntry(keyHash);
        if (entry == null) {
            entry = ring.firstEntry();
        }

        // 遍历环，直到找到足够的不同真实节点
        Iterator<Map.Entry<Long, HashNode<T>>> iterator =
            ring.tailMap(entry.getKey()).entrySet().iterator();

        while (nodes.size() < replicaCount && iterator.hasNext()) {
            HashNode<T> node = iterator.next().getValue();
            String realNodeId = node.getRealNodeId();

            if (!addedRealNodes.contains(realNodeId)) {
                nodes.add(node.getNode());
                addedRealNodes.add(realNodeId);
            }
        }

        // 如果还没有足够的节点，从环的开始继续
        if (nodes.size() < replicaCount) {
            iterator = ring.entrySet().iterator();
            while (nodes.size() < replicaCount && iterator.hasNext()) {
                HashNode<T> node = iterator.next().getValue();
                String realNodeId = node.getRealNodeId();

                if (!addedRealNodes.contains(realNodeId)) {
                    nodes.add(node.getNode());
                    addedRealNodes.add(realNodeId);
                }
            }
        }

        return nodes;
    }

    /**
     * 哈希函数
     */
    private long hash(String input) {
        synchronized (md5) {
            md5.reset();
            md5.update(input.getBytes());
            byte[] digest = md5.digest();

            // 取前4个字节作为hash值
            long hash = 0;
            for (int i = 0; i < 4; i++) {
                hash = (hash << 8) | (digest[i] & 0xFF);
            }

            return hash & 0xFFFFFFFFL; // 确保为正数
        }
    }

    /**
     * 获取节点分布统计
     */
    public Map<String, Integer> getDistributionStats(List<String> keys) {
        Map<String, Integer> stats = new HashMap<>();

        for (String key : keys) {
            String nodeId = getNodeId(key);
            if (nodeId != null) {
                stats.put(nodeId, stats.getOrDefault(nodeId, 0) + 1);
            }
        }

        return stats;
    }

    /**
     * 计算负载均衡度
     */
    public double calculateLoadBalance(List<String> keys) {
        if (realNodes.isEmpty() || keys.isEmpty()) {
            return 0.0;
        }

        Map<String, Integer> stats = getDistributionStats(keys);
        double average = (double) keys.size() / realNodes.size();

        double variance = 0.0;
        for (String nodeId : realNodes.keySet()) {
            int count = stats.getOrDefault(nodeId, 0);
            variance += Math.pow(count - average, 2);
        }

        double standardDeviation = Math.sqrt(variance / realNodes.size());
        return 1.0 - (standardDeviation / average); // 越接近1越均衡
    }

    /**
     * 获取环状态信息
     */
    public String getRingStatus() {
        StringBuilder sb = new StringBuilder();
        sb.append("=== 一致性哈希环状态 ===\n");
        sb.append(String.format("真实节点数: %d\n", realNodes.size()));
        sb.append(String.format("环上总节点数: %d\n", ring.size()));
        sb.append(String.format("虚拟节点数/真实节点: %d\n", virtualNodeCount));

        sb.append("\n环上节点分布:\n");
        for (Map.Entry<Long, HashNode<T>> entry : ring.entrySet()) {
            HashNode<T> node = entry.getValue();
            sb.append(String.format("  位置 %10d: %s%s\n",
                     entry.getKey(),
                     node.getNodeId(),
                     node.isVirtual() ? " (虚拟)" : " (真实)"));
        }

        return sb.toString();
    }

    // Getter方法
    public Set<String> getNodeIds() {
        return new HashSet<>(realNodes.keySet());
    }

    public int getNodeCount() {
        return realNodes.size();
    }

    public int getVirtualNodeCount() {
        return virtualNodeCount;
    }
}

/**
 * 服务器节点示例
 */
class ServerNode {
    private final String serverId;
    private final String host;
    private final int port;
    private final Map<String, String> data;

    public ServerNode(String serverId, String host, int port) {
        this.serverId = serverId;
        this.host = host;
        this.port = port;
        this.data = new ConcurrentHashMap<>();
    }

    public void put(String key, String value) {
        data.put(key, value);
        System.out.printf("服务器 %s 存储: %s = %s%n", serverId, key, value);
    }

    public String get(String key) {
        String value = data.get(key);
        System.out.printf("服务器 %s 读取: %s = %s%n", serverId, key, value);
        return value;
    }

    public int getDataCount() {
        return data.size();
    }

    public Set<String> getKeys() {
        return new HashSet<>(data.keySet());
    }

    // Getter方法
    public String getServerId() { return serverId; }
    public String getHost() { return host; }
    public int getPort() { return port; }

    @Override
    public String toString() {
        return String.format("ServerNode{id='%s', host='%s', port=%d, data=%d}",
                           serverId, host, port, data.size());
    }
}

/**
 * 一致性哈希演示
 */
class ConsistentHashDemo {
    public static void main(String[] args) {
        System.out.println("=== 一致性哈希算法演示 ===");

        // 创建一致性哈希，每个节点150个虚拟节点
        ConsistentHash<ServerNode> consistentHash = new ConsistentHash<>(150);

        // 添加初始节点
        consistentHash.addNode("Server1", new ServerNode("Server1", "192.168.1.1", 8001));
        consistentHash.addNode("Server2", new ServerNode("Server2", "192.168.1.2", 8002));
        consistentHash.addNode("Server3", new ServerNode("Server3", "192.168.1.3", 8003));

        // 生成测试数据
        List<String> testKeys = new ArrayList<>();
        for (int i = 1; i <= 1000; i++) {
            testKeys.add("key" + i);
        }

        // 测试初始分布
        System.out.println("\n--- 初始数据分布 ---");
        testDataDistribution(consistentHash, testKeys);

        // 添加新节点
        System.out.println("\n--- 添加新节点 Server4 ---");
        consistentHash.addNode("Server4", new ServerNode("Server4", "192.168.1.4", 8004));
        testDataDistribution(consistentHash, testKeys);

        // 移除节点
        System.out.println("\n--- 移除节点 Server2 ---");
        consistentHash.removeNode("Server2");
        testDataDistribution(consistentHash, testKeys);

        // 测试副本
        System.out.println("\n--- 副本分布测试 ---");
        testReplicaDistribution(consistentHash, Arrays.asList("key1", "key500", "key1000"));
    }

    private static void testDataDistribution(ConsistentHash<ServerNode> hash, List<String> keys) {
        Map<String, Integer> distribution = hash.getDistributionStats(keys);
        double balance = hash.calculateLoadBalance(keys);

        System.out.println("数据分布:");
        distribution.forEach((nodeId, count) -> {
            double percentage = (double) count / keys.size() * 100;
            System.out.printf("  %s: %d 个key (%.1f%%)%n", nodeId, count, percentage);
        });
        System.out.printf("负载均衡度: %.3f%n", balance);
    }

    private static void testReplicaDistribution(ConsistentHash<ServerNode> hash, List<String> keys) {
        for (String key : keys) {
            List<ServerNode> replicas = hash.getNodes(key, 2);
            System.out.printf("Key '%s' 的副本节点: %s%n", key,
                             replicas.stream()
                                   .map(ServerNode::getServerId)
                                   .reduce((a, b) -> a + ", " + b)
                                   .orElse("无"));
        }
    }
}
```

## 高级特性实现

### 加权一致性哈希

```java
/**
 * 加权一致性哈希
 */
public class WeightedConsistentHash<T> extends ConsistentHash<T> {

    /**
     * 加权节点信息
     */
    public static class WeightedNode<T> {
        private final String nodeId;
        private final T node;
        private final int weight;

        public WeightedNode(String nodeId, T node, int weight) {
            this.nodeId = nodeId;
            this.node = node;
            this.weight = Math.max(1, weight); // 权重至少为1
        }

        public String getNodeId() { return nodeId; }
        public T getNode() { return node; }
        public int getWeight() { return weight; }
    }

    private final Map<String, WeightedNode<T>> weightedNodes;

    public WeightedConsistentHash() {
        super(0); // 基类虚拟节点数设为0，由权重决定
        this.weightedNodes = new ConcurrentHashMap<>();
    }

    /**
     * 添加加权节点
     */
    public void addWeightedNode(String nodeId, T node, int weight) {
        WeightedNode<T> weightedNode = new WeightedNode<>(nodeId, node, weight);
        weightedNodes.put(nodeId, weightedNode);

        // 根据权重添加虚拟节点
        int virtualNodeCount = weight * 40; // 基础虚拟节点数 * 权重

        for (int i = 0; i < virtualNodeCount; i++) {
            String virtualNodeId = nodeId + "#" + i;
            long virtualHash = hash(virtualNodeId);
            HashNode<T> virtualNode = new HashNode<>(virtualNodeId, node, virtualHash, true, nodeId);
            ring.put(virtualHash, virtualNode);
        }

        System.out.printf("添加加权节点 %s (权重=%d): %d个虚拟节点%n",
                         nodeId, weight, virtualNodeCount);
    }

    /**
     * 更新节点权重
     */
    public void updateNodeWeight(String nodeId, int newWeight) {
        WeightedNode<T> existingNode = weightedNodes.get(nodeId);
        if (existingNode == null) {
            throw new IllegalArgumentException("节点不存在: " + nodeId);
        }

        // 移除旧的虚拟节点
        removeNode(nodeId);

        // 添加新的加权节点
        addWeightedNode(nodeId, existingNode.getNode(), newWeight);
    }

    /**
     * 获取节点权重信息
     */
    public Map<String, Integer> getWeightInfo() {
        Map<String, Integer> weights = new HashMap<>();
        weightedNodes.forEach((nodeId, weightedNode) -> {
            weights.put(nodeId, weightedNode.getWeight());
        });
        return weights;
    }

    private long hash(String input) {
        // 重用父类的哈希函数逻辑
        return super.hash(input);
    }
}

/**
 * 加权一致性哈希演示
 */
class WeightedConsistentHashDemo {
    public static void main(String[] args) {
        System.out.println("=== 加权一致性哈希演示 ===");

        WeightedConsistentHash<ServerNode> weightedHash = new WeightedConsistentHash<>();

        // 添加不同权重的节点
        weightedHash.addWeightedNode("HighEnd",
            new ServerNode("HighEnd", "192.168.1.1", 8001), 4);
        weightedHash.addWeightedNode("Medium",
            new ServerNode("Medium", "192.168.1.2", 8002), 2);
        weightedHash.addWeightedNode("LowEnd",
            new ServerNode("LowEnd", "192.168.1.3", 8003), 1);

        // 生成测试数据
        List<String> testKeys = new ArrayList<>();
        for (int i = 1; i <= 1000; i++) {
            testKeys.add("key" + i);
        }

        // 测试加权分布
        System.out.println("\n--- 加权分布测试 ---");
        Map<String, Integer> distribution = weightedHash.getDistributionStats(testKeys);
        Map<String, Integer> weights = weightedHash.getWeightInfo();

        distribution.forEach((nodeId, count) -> {
            int weight = weights.get(nodeId);
            double percentage = (double) count / testKeys.size() * 100;
            double expectedPercentage = (double) weight / weights.values().stream().mapToInt(Integer::intValue).sum() * 100;
            System.out.printf("节点 %s (权重=%d): %d个key (%.1f%%, 期望=%.1f%%)%n",
                             nodeId, weight, count, percentage, expectedPercentage);
        });

        // 动态调整权重
        System.out.println("\n--- 调整权重后 ---");
        weightedHash.updateNodeWeight("LowEnd", 3);

        Map<String, Integer> newDistribution = weightedHash.getDistributionStats(testKeys);
        Map<String, Integer> newWeights = weightedHash.getWeightInfo();

        newDistribution.forEach((nodeId, count) -> {
            int weight = newWeights.get(nodeId);
            double percentage = (double) count / testKeys.size() * 100;
            System.out.printf("节点 %s (权重=%d): %d个key (%.1f%%)%n",
                             nodeId, weight, count, percentage);
        });
    }
}
```

### 数据迁移管理

```java
/**
 * 数据迁移管理器
 */
public class DataMigrationManager<T> {

    /**
     * 迁移任务
     */
    public static class MigrationTask {
        private final String key;
        private final String fromNodeId;
        private final String toNodeId;
        private final long timestamp;

        public MigrationTask(String key, String fromNodeId, String toNodeId) {
            this.key = key;
            this.fromNodeId = fromNodeId;
            this.toNodeId = toNodeId;
            this.timestamp = System.currentTimeMillis();
        }

        public String getKey() { return key; }
        public String getFromNodeId() { return fromNodeId; }
        public String getToNodeId() { return toNodeId; }
        public long getTimestamp() { return timestamp; }

        @Override
        public String toString() {
            return String.format("MigrationTask{key='%s', %s -> %s}", key, fromNodeId, toNodeId);
        }
    }

    /**
     * 迁移结果
     */
    public static class MigrationResult {
        private final int totalKeys;
        private final int migratedKeys;
        private final long duration;
        private final List<MigrationTask> tasks;

        public MigrationResult(int totalKeys, int migratedKeys, long duration,
                             List<MigrationTask> tasks) {
            this.totalKeys = totalKeys;
            this.migratedKeys = migratedKeys;
            this.duration = duration;
            this.tasks = new ArrayList<>(tasks);
        }

        public int getTotalKeys() { return totalKeys; }
        public int getMigratedKeys() { return migratedKeys; }
        public long getDuration() { return duration; }
        public List<MigrationTask> getTasks() { return tasks; }
        public double getMigrationRatio() { return (double) migratedKeys / totalKeys; }
    }

    private final ConsistentHash<T> consistentHash;

    public DataMigrationManager(ConsistentHash<T> consistentHash) {
        this.consistentHash = consistentHash;
    }

    /**
     * 计算添加节点后的数据迁移
     */
    public MigrationResult calculateAddNodeMigration(String newNodeId, T newNode,
                                                   List<String> existingKeys) {
        long startTime = System.currentTimeMillis();

        // 记录原始分布
        Map<String, String> originalMapping = new HashMap<>();
        for (String key : existingKeys) {
            originalMapping.put(key, consistentHash.getNodeId(key));
        }

        // 添加新节点
        consistentHash.addNode(newNodeId, newNode);

        // 计算新分布和迁移任务
        List<MigrationTask> migrationTasks = new ArrayList<>();
        for (String key : existingKeys) {
            String newNodeForKey = consistentHash.getNodeId(key);
            String originalNode = originalMapping.get(key);

            if (!newNodeForKey.equals(originalNode)) {
                migrationTasks.add(new MigrationTask(key, originalNode, newNodeForKey));
            }
        }

        long endTime = System.currentTimeMillis();

        return new MigrationResult(
            existingKeys.size(),
            migrationTasks.size(),
            endTime - startTime,
            migrationTasks
        );
    }

    /**
     * 计算移除节点后的数据迁移
     */
    public MigrationResult calculateRemoveNodeMigration(String nodeIdToRemove,
                                                      List<String> existingKeys) {
        long startTime = System.currentTimeMillis();

        // 找出需要迁移的key
        List<String> keysToMigrate = new ArrayList<>();
        for (String key : existingKeys) {
            if (nodeIdToRemove.equals(consistentHash.getNodeId(key))) {
                keysToMigrate.add(key);
            }
        }

        // 移除节点
        consistentHash.removeNode(nodeIdToRemove);

        // 计算迁移任务
        List<MigrationTask> migrationTasks = new ArrayList<>();
        for (String key : keysToMigrate) {
            String newNodeForKey = consistentHash.getNodeId(key);
            if (newNodeForKey != null) {
                migrationTasks.add(new MigrationTask(key, nodeIdToRemove, newNodeForKey));
            }
        }

        long endTime = System.currentTimeMillis();

        return new MigrationResult(
            existingKeys.size(),
            migrationTasks.size(),
            endTime - startTime,
            migrationTasks
        );
    }

    /**
     * 执行数据迁移
     */
    public void executeMigration(MigrationResult migrationResult,
                               Map<String, ServerNode> nodeMap) {
        System.out.printf("开始执行数据迁移: %d个任务%n", migrationResult.getTasks().size());

        int completedTasks = 0;
        for (MigrationTask task : migrationResult.getTasks()) {
            try {
                ServerNode fromNode = nodeMap.get(task.getFromNodeId());
                ServerNode toNode = nodeMap.get(task.getToNodeId());

                if (fromNode != null && toNode != null) {
                    // 模拟数据迁移
                    String value = fromNode.get(task.getKey());
                    if (value != null) {
                        toNode.put(task.getKey(), value);
                        // 注意：实际应用中可能需要从源节点删除数据
                    }
                    completedTasks++;
                } else {
                    System.err.printf("迁移任务失败: 找不到节点 %s%n", task);
                }
            } catch (Exception e) {
                System.err.printf("迁移任务异常: %s, 错误: %s%n", task, e.getMessage());
            }
        }

        System.out.printf("数据迁移完成: %d/%d 任务成功%n",
                         completedTasks, migrationResult.getTasks().size());
    }

    /**
     * 分析迁移影响
     */
    public void analyzeMigrationImpact(MigrationResult result) {
        System.out.println("\n=== 迁移影响分析 ===");
        System.out.printf("总数据量: %d%n", result.getTotalKeys());
        System.out.printf("需要迁移: %d (%.2f%%)%n",
                         result.getMigratedKeys(),
                         result.getMigrationRatio() * 100);
        System.out.printf("计算耗时: %d ms%n", result.getDuration());

        // 按目标节点分组统计
        Map<String, Long> targetNodeStats = result.getTasks().stream()
            .collect(Collectors.groupingBy(
                MigrationTask::getToNodeId,
                Collectors.counting()
            ));

        System.out.println("目标节点分布:");
        targetNodeStats.forEach((nodeId, count) -> {
            System.out.printf("  %s: %d个key%n", nodeId, count);
        });
    }
}

/**
 * 数据迁移演示
 */
class DataMigrationDemo {
    public static void main(String[] args) {
        System.out.println("=== 数据迁移管理演示 ===");

        ConsistentHash<ServerNode> hash = new ConsistentHash<>(100);
        DataMigrationManager<ServerNode> migrationManager = new DataMigrationManager<>(hash);

        // 创建节点映射
        Map<String, ServerNode> nodeMap = new HashMap<>();

        // 初始化集群
        ServerNode server1 = new ServerNode("Server1", "192.168.1.1", 8001);
        ServerNode server2 = new ServerNode("Server2", "192.168.1.2", 8002);
        ServerNode server3 = new ServerNode("Server3", "192.168.1.3", 8003);

        hash.addNode("Server1", server1);
        hash.addNode("Server2", server2);
        hash.addNode("Server3", server3);

        nodeMap.put("Server1", server1);
        nodeMap.put("Server2", server2);
        nodeMap.put("Server3", server3);

        // 生成测试数据
        List<String> testKeys = new ArrayList<>();
        for (int i = 1; i <= 100; i++) {
            testKeys.add("key" + i);
        }

        // 模拟数据已存储在对应节点
        for (String key : testKeys) {
            String nodeId = hash.getNodeId(key);
            ServerNode node = nodeMap.get(nodeId);
            if (node != null) {
                node.put(key, "value_" + key);
            }
        }

        // 测试添加节点的迁移
        System.out.println("--- 添加节点迁移测试 ---");
        ServerNode server4 = new ServerNode("Server4", "192.168.1.4", 8004);
        nodeMap.put("Server4", server4);

        MigrationResult addResult = migrationManager.calculateAddNodeMigration(
            "Server4", server4, testKeys);
        migrationManager.analyzeMigrationImpact(addResult);
        migrationManager.executeMigration(addResult, nodeMap);

        // 测试移除节点的迁移
        System.out.println("\n--- 移除节点迁移测试 ---");
        MigrationResult removeResult = migrationManager.calculateRemoveNodeMigration(
            "Server2", testKeys);
        migrationManager.analyzeMigrationImpact(removeResult);
        migrationManager.executeMigration(removeResult, nodeMap);
    }
}
```

## 性能优化策略

### 哈希函数优化

```java
/**
 * 优化的哈希函数实现
 */
public class OptimizedHashFunction {

    /**
     * MurmurHash3实现
     */
    public static class MurmurHash3 {
        private static final int C1 = 0xcc9e2d51;
        private static final int C2 = 0x1b873593;
        private static final int R1 = 15;
        private static final int R2 = 13;
        private static final int M = 5;
        private static final int N = 0xe6546b64;

        public static long hash(String input) {
            return hash(input.getBytes(), 0);
        }

        public static long hash(byte[] data, int seed) {
            int length = data.length;
            int h1 = seed;

            int roundedEnd = (length & 0xfffffffc); // 向下舍入到最近的4的倍数

            for (int i = 0; i < roundedEnd; i += 4) {
                int k1 = (data[i] & 0xff) | ((data[i + 1] & 0xff) << 8) |
                        ((data[i + 2] & 0xff) << 16) | (data[i + 3] << 24);
                k1 *= C1;
                k1 = (k1 << R1) | (k1 >>> (32 - R1));
                k1 *= C2;

                h1 ^= k1;
                h1 = (h1 << R2) | (h1 >>> (32 - R2));
                h1 = h1 * M + N;
            }

            // 处理剩余字节
            int k1 = 0;
            switch (length & 0x03) {
                case 3:
                    k1 = (data[roundedEnd + 2] & 0xff) << 16;
                case 2:
                    k1 |= (data[roundedEnd + 1] & 0xff) << 8;
                case 1:
                    k1 |= (data[roundedEnd] & 0xff);
                    k1 *= C1;
                    k1 = (k1 << R1) | (k1 >>> (32 - R1));
                    k1 *= C2;
                    h1 ^= k1;
            }

            // 最终混合
            h1 ^= length;
            h1 ^= (h1 >>> 16);
            h1 *= 0x85ebca6b;
            h1 ^= (h1 >>> 13);
            h1 *= 0xc2b2ae35;
            h1 ^= (h1 >>> 16);

            return h1 & 0xFFFFFFFFL;
        }
    }

    /**
     * FNV哈希实现
     */
    public static class FNVHash {
        private static final long FNV_OFFSET_BASIS = 2166136261L;
        private static final long FNV_PRIME = 16777619L;

        public static long hash(String input) {
            long hash = FNV_OFFSET_BASIS;
            for (byte b : input.getBytes()) {
                hash ^= (b & 0xff);
                hash *= FNV_PRIME;
            }
            return hash & 0xFFFFFFFFL;
        }
    }

    /**
     * 哈希函数性能测试
     */
    public static void performanceTest() {
        List<String> testData = new ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            testData.add("key_" + i + "_" + System.nanoTime());
        }

        // 测试MD5
        long startTime = System.nanoTime();
        for (String data : testData) {
            try {
                MessageDigest md5 = MessageDigest.getInstance("MD5");
                md5.update(data.getBytes());
                md5.digest();
            } catch (NoSuchAlgorithmException e) {
                // ignore
            }
        }
        long md5Time = System.nanoTime() - startTime;

        // 测试MurmurHash3
        startTime = System.nanoTime();
        for (String data : testData) {
            MurmurHash3.hash(data);
        }
        long murmurTime = System.nanoTime() - startTime;

        // 测试FNV
        startTime = System.nanoTime();
        for (String data : testData) {
            FNVHash.hash(data);
        }
        long fnvTime = System.nanoTime() - startTime;

        System.out.println("=== 哈希函数性能测试结果 ===");
        System.out.printf("MD5:        %d ms%n", md5Time / 1_000_000);
        System.out.printf("MurmurHash3: %d ms%n", murmurTime / 1_000_000);
        System.out.printf("FNV:        %d ms%n", fnvTime / 1_000_000);
    }
}
```

### 跳表优化

```java
/**
 * 使用跳表优化的一致性哈希
 */
public class SkipListConsistentHash<T> {

    /**
     * 跳表节点
     */
    private static class SkipListNode<T> {
        final long hash;
        final ConsistentHash.HashNode<T> hashNode;
        final SkipListNode<T>[] forward;

        @SuppressWarnings("unchecked")
        SkipListNode(long hash, ConsistentHash.HashNode<T> hashNode, int level) {
            this.hash = hash;
            this.hashNode = hashNode;
            this.forward = new SkipListNode[level + 1];
        }
    }

    private final int maxLevel;
    private final double probability;
    private final Random random;
    private final SkipListNode<T> header;
    private int currentLevel;

    public SkipListConsistentHash() {
        this.maxLevel = 16;
        this.probability = 0.5;
        this.random = new Random();
        this.header = new SkipListNode<>(-1, null, maxLevel);
        this.currentLevel = 0;
    }

    /**
     * 随机生成层级
     */
    private int randomLevel() {
        int level = 0;
        while (random.nextDouble() < probability && level < maxLevel) {
            level++;
        }
        return level;
    }

    /**
     * 插入节点
     */
    public void insert(long hash, ConsistentHash.HashNode<T> hashNode) {
        SkipListNode<T>[] update = new SkipListNode[maxLevel + 1];
        SkipListNode<T> current = header;

        // 从最高层开始搜索
        for (int i = currentLevel; i >= 0; i--) {
            while (current.forward[i] != null && current.forward[i].hash < hash) {
                current = current.forward[i];
            }
            update[i] = current;
        }

        // 生成新节点的层级
        int newLevel = randomLevel();
        if (newLevel > currentLevel) {
            for (int i = currentLevel + 1; i <= newLevel; i++) {
                update[i] = header;
            }
            currentLevel = newLevel;
        }

        // 创建新节点并插入
        SkipListNode<T> newNode = new SkipListNode<>(hash, hashNode, newLevel);
        for (int i = 0; i <= newLevel; i++) {
            newNode.forward[i] = update[i].forward[i];
            update[i].forward[i] = newNode;
        }
    }

    /**
     * 删除节点
     */
    public boolean delete(long hash) {
        SkipListNode<T>[] update = new SkipListNode[maxLevel + 1];
        SkipListNode<T> current = header;

        // 搜索要删除的节点
        for (int i = currentLevel; i >= 0; i--) {
            while (current.forward[i] != null && current.forward[i].hash < hash) {
                current = current.forward[i];
            }
            update[i] = current;
        }

        current = current.forward[0];
        if (current != null && current.hash == hash) {
            // 删除节点
            for (int i = 0; i <= currentLevel; i++) {
                if (update[i].forward[i] != current) {
                    break;
                }
                update[i].forward[i] = current.forward[i];
            }

            // 更新最大层级
            while (currentLevel > 0 && header.forward[currentLevel] == null) {
                currentLevel--;
            }
            return true;
        }
        return false;
    }

    /**
     * 查找大于等于指定hash的第一个节点
     */
    public ConsistentHash.HashNode<T> ceiling(long hash) {
        SkipListNode<T> current = header;

        for (int i = currentLevel; i >= 0; i--) {
            while (current.forward[i] != null && current.forward[i].hash < hash) {
                current = current.forward[i];
            }
        }

        current = current.forward[0];
        if (current != null) {
            return current.hashNode;
        }

        // 如果没找到，返回第一个节点（环形特性）
        return header.forward[0] != null ? header.forward[0].hashNode : null;
    }

    /**
     * 性能测试
     */
    public static void performanceComparison() {
        int nodeCount = 100000;
        int queryCount = 100000;

        // 测试跳表
        SkipListConsistentHash<String> skipList = new SkipListConsistentHash<>();
        Random random = new Random();

        long startTime = System.nanoTime();
        for (int i = 0; i < nodeCount; i++) {
            long hash = random.nextLong() & 0x7FFFFFFFL;
            ConsistentHash.HashNode<String> node =
                new ConsistentHash.HashNode<>("node" + i, "data" + i, hash, false, "node" + i);
            skipList.insert(hash, node);
        }
        long insertTime = System.nanoTime() - startTime;

        startTime = System.nanoTime();
        for (int i = 0; i < queryCount; i++) {
            long hash = random.nextLong() & 0x7FFFFFFFL;
            skipList.ceiling(hash);
        }
        long queryTime = System.nanoTime() - startTime;

        System.out.println("=== 跳表性能测试 ===");
        System.out.printf("插入 %d 个节点: %d ms%n", nodeCount, insertTime / 1_000_000);
        System.out.printf("查询 %d 次: %d ms%n", queryCount, queryTime / 1_000_000);
        System.out.printf("平均查询时间: %.2f μs%n", (double) queryTime / queryCount / 1000);
    }
}
```

## 应用场景与案例

### 分布式缓存系统

```java
/**
 * 基于一致性哈希的分布式缓存
 */
public class DistributedCache {

    /**
     * 缓存节点
     */
    public static class CacheNode {
        private final String nodeId;
        private final String host;
        private final int port;
        private final Map<String, CacheEntry> cache;
        private final int maxSize;

        public CacheNode(String nodeId, String host, int port, int maxSize) {
            this.nodeId = nodeId;
            this.host = host;
            this.port = port;
            this.maxSize = maxSize;
            this.cache = new ConcurrentHashMap<>();
        }

        public void put(String key, String value, long ttl) {
            if (cache.size() >= maxSize) {
                evictOldestEntry();
            }

            long expireTime = System.currentTimeMillis() + ttl;
            cache.put(key, new CacheEntry(value, expireTime));
            System.out.printf("缓存节点 %s 存储: %s%n", nodeId, key);
        }

        public String get(String key) {
            CacheEntry entry = cache.get(key);
            if (entry != null && !entry.isExpired()) {
                System.out.printf("缓存节点 %s 命中: %s%n", nodeId, key);
                return entry.getValue();
            } else {
                if (entry != null) {
                    cache.remove(key); // 清除过期条目
                }
                System.out.printf("缓存节点 %s 未命中: %s%n", nodeId, key);
                return null;
            }
        }

        public void delete(String key) {
            cache.remove(key);
            System.out.printf("缓存节点 %s 删除: %s%n", nodeId, key);
        }

        private void evictOldestEntry() {
            // 简化的LRU淘汰策略
            String oldestKey = cache.entrySet().stream()
                .min(Map.Entry.comparingByValue((e1, e2) ->
                    Long.compare(e1.getCreateTime(), e2.getCreateTime())))
                .map(Map.Entry::getKey)
                .orElse(null);

            if (oldestKey != null) {
                cache.remove(oldestKey);
            }
        }

        public String getNodeId() { return nodeId; }
        public int getCacheSize() { return cache.size(); }
    }

    /**
     * 缓存条目
     */
    private static class CacheEntry {
        private final String value;
        private final long expireTime;
        private final long createTime;

        public CacheEntry(String value, long expireTime) {
            this.value = value;
            this.expireTime = expireTime;
            this.createTime = System.currentTimeMillis();
        }

        public String getValue() { return value; }
        public boolean isExpired() { return System.currentTimeMillis() > expireTime; }
        public long getCreateTime() { return createTime; }
    }

    private final ConsistentHash<CacheNode> consistentHash;
    private final Map<String, CacheNode> nodeMap;
    private final int replicationFactor;

    public DistributedCache(int virtualNodeCount, int replicationFactor) {
        this.consistentHash = new ConsistentHash<>(virtualNodeCount);
        this.nodeMap = new ConcurrentHashMap<>();
        this.replicationFactor = replicationFactor;
    }

    /**
     * 添加缓存节点
     */
    public void addCacheNode(String nodeId, String host, int port, int maxSize) {
        CacheNode node = new CacheNode(nodeId, host, port, maxSize);
        nodeMap.put(nodeId, node);
        consistentHash.addNode(nodeId, node);
        System.out.printf("添加缓存节点: %s (%s:%d)%n", nodeId, host, port);
    }

    /**
     * 移除缓存节点
     */
    public void removeCacheNode(String nodeId) {
        nodeMap.remove(nodeId);
        consistentHash.removeNode(nodeId);
        System.out.printf("移除缓存节点: %s%n", nodeId);
    }

    /**
     * 存储数据
     */
    public void put(String key, String value, long ttl) {
        List<CacheNode> nodes = consistentHash.getNodes(key, replicationFactor);

        for (CacheNode node : nodes) {
            node.put(key, value, ttl);
        }
    }

    /**
     * 获取数据
     */
    public String get(String key) {
        List<CacheNode> nodes = consistentHash.getNodes(key, replicationFactor);

        // 尝试从各个副本节点获取数据
        for (CacheNode node : nodes) {
            String value = node.get(key);
            if (value != null) {
                return value;
            }
        }

        return null;
    }

    /**
     * 删除数据
     */
    public void delete(String key) {
        List<CacheNode> nodes = consistentHash.getNodes(key, replicationFactor);

        for (CacheNode node : nodes) {
            node.delete(key);
        }
    }

    /**
     * 获取缓存统计信息
     */
    public Map<String, Integer> getCacheStats() {
        Map<String, Integer> stats = new HashMap<>();
        nodeMap.forEach((nodeId, node) -> {
            stats.put(nodeId, node.getCacheSize());
        });
        return stats;
    }
}

/**
 * 分布式缓存演示
 */
class DistributedCacheDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 分布式缓存系统演示 ===");

        DistributedCache cache = new DistributedCache(100, 2);

        // 添加缓存节点
        cache.addCacheNode("cache1", "192.168.1.1", 11211, 1000);
        cache.addCacheNode("cache2", "192.168.1.2", 11211, 1000);
        cache.addCacheNode("cache3", "192.168.1.3", 11211, 1000);

        // 存储数据
        System.out.println("\n--- 存储数据 ---");
        cache.put("user:1001", "Alice", 60000);
        cache.put("user:1002", "Bob", 60000);
        cache.put("user:1003", "Charlie", 60000);
        cache.put("session:abc123", "session_data", 30000);

        // 读取数据
        System.out.println("\n--- 读取数据 ---");
        System.out.println("user:1001 = " + cache.get("user:1001"));
        System.out.println("user:1002 = " + cache.get("user:1002"));
        System.out.println("user:1003 = " + cache.get("user:1003"));
        System.out.println("session:abc123 = " + cache.get("session:abc123"));

        // 显示缓存统计
        System.out.println("\n--- 缓存统计 ---");
        Map<String, Integer> stats = cache.getCacheStats();
        stats.forEach((nodeId, size) -> {
            System.out.printf("节点 %s: %d 个缓存条目%n", nodeId, size);
        });

        // 测试节点故障
        System.out.println("\n--- 节点故障测试 ---");
        cache.removeCacheNode("cache2");

        // 再次读取数据（应该从副本读取）
        System.out.println("故障后读取:");
        System.out.println("user:1001 = " + cache.get("user:1001"));
        System.out.println("user:1002 = " + cache.get("user:1002"));
    }
}
```

## 总结

一致性哈希算法为分布式系统提供了优雅的数据分片解决方案：

### 核心优势

1. **最小化数据迁移**：节点变化时只影响相邻数据
2. **负载均衡**：通过虚拟节点技术实现均匀分布
3. **高可扩展性**：支持动态添加和删除节点
4. **容错能力**：单点故障不影响整个系统

### 应用场景

```
一致性哈希应用：
├─ 分布式缓存 (Redis Cluster, Memcached)
├─ 分布式存储 (Cassandra, DynamoDB)
├─ 负载均衡 (Nginx, HAProxy)
├─ CDN系统 (Akamai, CloudFlare)
└─ 分布式数据库 (MongoDB分片)
```

### 性能对比

```
┌──────────────────┬──────────────┬──────────────┬──────────────┐
│ 方案             │ 数据迁移量    │ 负载均衡     │ 实现复杂度    │
├──────────────────┼──────────────┼──────────────┼──────────────┤
│ 传统哈希         │ ~100%        │ 完美         │ 简单         │
│ 基础一致性哈希   │ ~1/N         │ 较差         │ 中等         │
│ 虚拟节点优化     │ ~1/N         │ 良好         │ 中等         │
│ 加权一致性哈希   │ ~1/N         │ 可控         │ 复杂         │
└──────────────────┴──────────────┴──────────────┴──────────────┘
```

### 最佳实践

1. **虚拟节点数量**：通常设置为100-200个获得良好均衡
2. **哈希函数选择**：MD5适合通用场景，MurmurHash性能更好
3. **数据迁移策略**：分批迁移，避免影响在线服务
4. **监控告警**：跟踪负载分布和迁移进度

一致性哈希算法是构建可扩展分布式系统的重要基础，正确理解和实现对系统架构设计至关重要。

## 参考资料

1. Karger, D., et al. (1997). Consistent hashing and random trees
2. Stoica, I., et al. (2001). Chord: A scalable peer-to-peer lookup service
3. DeCandia, G., et al. (2007). Dynamo: Amazon's highly available key-value store