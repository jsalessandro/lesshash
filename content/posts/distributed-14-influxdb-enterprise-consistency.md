---
title: "分布式系统实战剖析：InfluxDB企业版一致性实现原理与Java模拟"
date: 2024-12-19T16:00:00+08:00
draft: false
tags: ["分布式系统", "InfluxDB", "一致性", "时序数据库", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入剖析InfluxDB企业版的分布式一致性实现原理、Anti-Entropy机制以及在时序数据库中的应用实践，包含完整的Java模拟实现"
---

## 1. InfluxDB企业版概述

InfluxDB是一个专为时序数据设计的开源数据库，企业版在开源版基础上增加了集群功能、高可用性和强一致性保证。InfluxDB企业版采用了独特的一致性模型来处理时序数据的特殊需求。

### 1.1 架构特点

#### 流程图表


**关系流向：**
```
A[Client] → B[Load Balancer]
B → C[Meta Node 1]
B → D[Meta Node 2]
B → E[Meta Node 3]
C → F[Data Node 1]
```

### 1.2 核心组件

- **Meta Nodes**：管理集群元数据，使用Raft协议保证一致性
- **Data Nodes**：存储实际的时序数据
- **Shards**：数据分片，按时间窗口分割
- **Anti-Entropy**：反熵机制，用于数据修复

## 2. InfluxDB一致性模型

### 2.1 最终一致性

InfluxDB企业版采用最终一致性模型，主要考虑因素：

1. **时序数据特性**：数据通常按时间顺序写入，很少修改
2. **高写入性能**：优先保证写入吞吐量
3. **可用性优先**：在网络分区时优先保证可用性

### 2.2 一致性层次

```
强一致性层：Meta数据（使用Raft）
├── 集群配置
├── 用户权限
├── 数据库schema
└── 分片分布

最终一致性层：时序数据
├── 写入优先
├── 异步复制
├── Anti-Entropy修复
└── 冲突解决
```

## 3. Meta数据一致性实现

### 3.1 Meta节点Raft实现

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * InfluxDB Meta节点，使用Raft协议
 */
public class InfluxDBMetaNode {
    private final String nodeId;
    private final Set<String> clusterNodes;
    private final Map<String, String> nodeAddresses = new ConcurrentHashMap<>();

    // Meta数据存储
    private final Map<String, Database> databases = new ConcurrentHashMap<>();
    private final Map<String, User> users = new ConcurrentHashMap<>();
    private final Map<String, ShardInfo> shards = new ConcurrentHashMap<>();
    private final AtomicLong metaIndex = new AtomicLong(0);

    // Raft状态
    private volatile RaftRole role = RaftRole.FOLLOWER;
    private volatile String leaderId;
    private volatile long currentTerm = 0;
    private volatile String votedFor;

    // 选举相关
    private final Random random = new Random();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    private ScheduledFuture<?> electionTimer;
    private ScheduledFuture<?> heartbeatTimer;

    // 配置参数
    private final long electionTimeoutMin = 150; // 毫秒
    private final long electionTimeoutMax = 300; // 毫秒
    private final long heartbeatInterval = 50;   // 毫秒

    public InfluxDBMetaNode(String nodeId, Set<String> clusterNodes) {
        this.nodeId = nodeId;
        this.clusterNodes = new HashSet<>(clusterNodes);
        initializeDefaultData();
        startElectionTimer();
    }

    /**
     * 初始化默认数据
     */
    private void initializeDefaultData() {
        // 创建默认数据库
        Database defaultDB = new Database("_internal", RetentionPolicy.defaultPolicy());
        databases.put("_internal", defaultDB);

        // 创建管理员用户
        User adminUser = new User("admin", "admin", Arrays.asList("admin"));
        users.put("admin", adminUser);
    }

    /**
     * 创建数据库
     */
    public CompletableFuture<Boolean> createDatabase(String dbName, RetentionPolicy policy) {
        if (role != RaftRole.LEADER) {
            return CompletableFuture.completedFuture(false);
        }

        MetaCommand command = new MetaCommand(
            MetaCommandType.CREATE_DATABASE,
            metaIndex.incrementAndGet(),
            Map.of("name", dbName, "policy", policy)
        );

        return replicateCommand(command);
    }

    /**
     * 创建分片
     */
    public CompletableFuture<Boolean> createShard(String dbName, long startTime, long endTime,
                                                 List<String> owners) {
        if (role != RaftRole.LEADER) {
            return CompletableFuture.completedFuture(false);
        }

        String shardId = generateShardId(dbName, startTime, endTime);
        ShardInfo shard = new ShardInfo(shardId, dbName, startTime, endTime, owners);

        MetaCommand command = new MetaCommand(
            MetaCommandType.CREATE_SHARD,
            metaIndex.incrementAndGet(),
            Map.of("shard", shard)
        );

        return replicateCommand(command);
    }

    /**
     * 复制命令到其他节点
     */
    private CompletableFuture<Boolean> replicateCommand(MetaCommand command) {
        List<CompletableFuture<Boolean>> futures = new ArrayList<>();

        for (String node : clusterNodes) {
            if (!node.equals(nodeId)) {
                CompletableFuture<Boolean> future = sendCommandToNode(node, command);
                futures.add(future);
            }
        }

        // 等待大多数节点确认
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> {
                    long successCount = futures.stream()
                            .mapToLong(f -> f.join() ? 1 : 0)
                            .sum() + 1; // +1 for leader

                    boolean majority = successCount > clusterNodes.size() / 2;
                    if (majority) {
                        applyCommand(command);
                    }
                    return majority;
                });
    }

    /**
     * 应用命令到本地状态
     */
    private void applyCommand(MetaCommand command) {
        switch (command.getType()) {
            case CREATE_DATABASE:
                String dbName = (String) command.getData().get("name");
                RetentionPolicy policy = (RetentionPolicy) command.getData().get("policy");
                Database db = new Database(dbName, policy);
                databases.put(dbName, db);
                System.out.println("应用命令：创建数据库 " + dbName);
                break;

            case CREATE_SHARD:
                ShardInfo shard = (ShardInfo) command.getData().get("shard");
                shards.put(shard.getId(), shard);
                System.out.println("应用命令：创建分片 " + shard.getId());
                break;

            case CREATE_USER:
                // 实现用户创建逻辑
                break;
        }

        metaIndex.set(command.getIndex());
    }

    /**
     * 发送命令到指定节点
     */
    private CompletableFuture<Boolean> sendCommandToNode(String nodeId, MetaCommand command) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // 模拟网络通信
                Thread.sleep(10);
                return random.nextDouble() > 0.1; // 90%成功率
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        });
    }

    /**
     * 开始选举定时器
     */
    private void startElectionTimer() {
        long timeout = electionTimeoutMin + random.nextInt((int)(electionTimeoutMax - electionTimeoutMin));

        electionTimer = scheduler.schedule(() -> {
            if (role != RaftRole.LEADER) {
                startElection();
            }
        }, timeout, TimeUnit.MILLISECONDS);
    }

    /**
     * 开始选举
     */
    private void startElection() {
        role = RaftRole.CANDIDATE;
        currentTerm++;
        votedFor = nodeId;

        System.out.println("节点 " + nodeId + " 开始选举，任期 " + currentTerm);

        AtomicInteger voteCount = new AtomicInteger(1); // 投票给自己

        for (String node : clusterNodes) {
            if (!node.equals(nodeId)) {
                requestVote(node, voteCount);
            }
        }

        // 重新设置选举定时器
        startElectionTimer();
    }

    /**
     * 请求投票
     */
    private void requestVote(String nodeId, AtomicInteger voteCount) {
        CompletableFuture.supplyAsync(() -> {
            // 模拟投票请求
            return random.nextDouble() > 0.3; // 70%概率获得选票
        }).thenAccept(granted -> {
            if (granted && role == RaftRole.CANDIDATE) {
                int votes = voteCount.incrementAndGet();
                if (votes > clusterNodes.size() / 2) {
                    becomeLeader();
                }
            }
        });
    }

    /**
     * 成为Leader
     */
    private void becomeLeader() {
        if (role != RaftRole.CANDIDATE) {
            return;
        }

        role = RaftRole.LEADER;
        leaderId = nodeId;

        System.out.println("节点 " + nodeId + " 成为Leader，任期 " + currentTerm);

        // 取消选举定时器
        if (electionTimer != null) {
            electionTimer.cancel(false);
        }

        // 开始发送心跳
        startHeartbeat();
    }

    /**
     * 开始心跳
     */
    private void startHeartbeat() {
        heartbeatTimer = scheduler.scheduleAtFixedRate(() -> {
            if (role == RaftRole.LEADER) {
                for (String node : clusterNodes) {
                    if (!node.equals(nodeId)) {
                        sendHeartbeat(node);
                    }
                }
            }
        }, 0, heartbeatInterval, TimeUnit.MILLISECONDS);
    }

    /**
     * 发送心跳
     */
    private void sendHeartbeat(String nodeId) {
        // 模拟心跳发送
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(5);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }

    /**
     * 生成分片ID
     */
    private String generateShardId(String dbName, long startTime, long endTime) {
        return dbName + "_" + startTime + "_" + endTime + "_" + System.nanoTime();
    }

    /**
     * 获取分片信息
     */
    public List<ShardInfo> getShardsForTimeRange(String dbName, long startTime, long endTime) {
        return shards.values().stream()
                .filter(shard -> shard.getDatabase().equals(dbName))
                .filter(shard -> shard.overlaps(startTime, endTime))
                .collect(Collectors.toList());
    }

    /**
     * 获取集群状态
     */
    public ClusterStatus getClusterStatus() {
        return new ClusterStatus(
            nodeId,
            role,
            leaderId,
            currentTerm,
            databases.size(),
            shards.size(),
            users.size()
        );
    }

    /**
     * 关闭节点
     */
    public void shutdown() {
        if (electionTimer != null) {
            electionTimer.cancel(false);
        }
        if (heartbeatTimer != null) {
            heartbeatTimer.cancel(false);
        }
        scheduler.shutdown();
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public RaftRole getRole() { return role; }
    public String getLeaderId() { return leaderId; }
    public Map<String, Database> getDatabases() { return new HashMap<>(databases); }
    public Map<String, ShardInfo> getShards() { return new HashMap<>(shards); }
}

/**
 * Raft角色枚举
 */
enum RaftRole {
    FOLLOWER,
    CANDIDATE,
    LEADER
}

/**
 * Meta命令类型
 */
enum MetaCommandType {
    CREATE_DATABASE,
    DROP_DATABASE,
    CREATE_SHARD,
    DELETE_SHARD,
    CREATE_USER,
    DELETE_USER
}

/**
 * Meta命令
 */
class MetaCommand {
    private final MetaCommandType type;
    private final long index;
    private final Map<String, Object> data;
    private final long timestamp;

    public MetaCommand(MetaCommandType type, long index, Map<String, Object> data) {
        this.type = type;
        this.index = index;
        this.data = new HashMap<>(data);
        this.timestamp = System.currentTimeMillis();
    }

    // Getters
    public MetaCommandType getType() { return type; }
    public long getIndex() { return index; }
    public Map<String, Object> getData() { return new HashMap<>(data); }
    public long getTimestamp() { return timestamp; }
}

/**
 * 数据库定义
 */
class Database {
    private final String name;
    private final RetentionPolicy retentionPolicy;
    private final Map<String, Measurement> measurements = new ConcurrentHashMap<>();

    public Database(String name, RetentionPolicy retentionPolicy) {
        this.name = name;
        this.retentionPolicy = retentionPolicy;
    }

    public String getName() { return name; }
    public RetentionPolicy getRetentionPolicy() { return retentionPolicy; }
    public Map<String, Measurement> getMeasurements() { return new HashMap<>(measurements); }
}

/**
 * 保留策略
 */
class RetentionPolicy {
    private final String name;
    private final long duration; // 毫秒
    private final int replication;
    private final boolean isDefault;

    public RetentionPolicy(String name, long duration, int replication, boolean isDefault) {
        this.name = name;
        this.duration = duration;
        this.replication = replication;
        this.isDefault = isDefault;
    }

    public static RetentionPolicy defaultPolicy() {
        return new RetentionPolicy("autogen", 0, 1, true); // 0表示永不过期
    }

    // Getters
    public String getName() { return name; }
    public long getDuration() { return duration; }
    public int getReplication() { return replication; }
    public boolean isDefault() { return isDefault; }
}

/**
 * 分片信息
 */
class ShardInfo {
    private final String id;
    private final String database;
    private final long startTime;
    private final long endTime;
    private final List<String> owners;

    public ShardInfo(String id, String database, long startTime, long endTime, List<String> owners) {
        this.id = id;
        this.database = database;
        this.startTime = startTime;
        this.endTime = endTime;
        this.owners = new ArrayList<>(owners);
    }

    /**
     * 检查时间范围是否重叠
     */
    public boolean overlaps(long start, long end) {
        return !(end <= startTime || start >= endTime);
    }

    // Getters
    public String getId() { return id; }
    public String getDatabase() { return database; }
    public long getStartTime() { return startTime; }
    public long getEndTime() { return endTime; }
    public List<String> getOwners() { return new ArrayList<>(owners); }
}

/**
 * 用户定义
 */
class User {
    private final String username;
    private final String password;
    private final List<String> privileges;

    public User(String username, String password, List<String> privileges) {
        this.username = username;
        this.password = password;
        this.privileges = new ArrayList<>(privileges);
    }

    // Getters
    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public List<String> getPrivileges() { return new ArrayList<>(privileges); }
}

/**
 * 测量指标
 */
class Measurement {
    private final String name;
    private final Map<String, String> tags = new ConcurrentHashMap<>();
    private final Map<String, Class<?>> fields = new ConcurrentHashMap<>();

    public Measurement(String name) {
        this.name = name;
    }

    public String getName() { return name; }
    public Map<String, String> getTags() { return new HashMap<>(tags); }
    public Map<String, Class<?>> getFields() { return new HashMap<>(fields); }
}

/**
 * 集群状态
 */
class ClusterStatus {
    private final String nodeId;
    private final RaftRole role;
    private final String leaderId;
    private final long term;
    private final int databaseCount;
    private final int shardCount;
    private final int userCount;

    public ClusterStatus(String nodeId, RaftRole role, String leaderId, long term,
                        int databaseCount, int shardCount, int userCount) {
        this.nodeId = nodeId;
        this.role = role;
        this.leaderId = leaderId;
        this.term = term;
        this.databaseCount = databaseCount;
        this.shardCount = shardCount;
        this.userCount = userCount;
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public RaftRole getRole() { return role; }
    public String getLeaderId() { return leaderId; }
    public long getTerm() { return term; }
    public int getDatabaseCount() { return databaseCount; }
    public int getShardCount() { return shardCount; }
    public int getUserCount() { return userCount; }

    @Override
    public String toString() {
        return String.format("ClusterStatus{nodeId='%s', role=%s, leader='%s', term=%d, dbs=%d, shards=%d, users=%d}",
                nodeId, role, leaderId, term, databaseCount, shardCount, userCount);
    }
}
```

## 4. 时序数据存储与复制

### 4.1 数据节点实现

```java
/**
 * InfluxDB数据节点
 */
public class InfluxDBDataNode {
    private final String nodeId;
    private final String metaNodeAddress;
    private final Map<String, Shard> localShards = new ConcurrentHashMap<>();

    // 时序数据存储
    private final Map<String, TSMFile> tsmFiles = new ConcurrentHashMap<>();
    private final WAL wal = new WAL();

    // Anti-Entropy相关
    private final ScheduledExecutorService antiEntropyScheduler = Executors.newSingleThreadScheduledExecutor();
    private final Map<String, Long> lastSyncTime = new ConcurrentHashMap<>();

    // 配置参数
    private final long antiEntropyInterval = 300000; // 5分钟
    private final int maxPointsPerWrite = 10000;

    public InfluxDBDataNode(String nodeId, String metaNodeAddress) {
        this.nodeId = nodeId;
        this.metaNodeAddress = metaNodeAddress;

        // 启动Anti-Entropy定时任务
        antiEntropyScheduler.scheduleAtFixedRate(
            this::performAntiEntropy,
            antiEntropyInterval,
            antiEntropyInterval,
            TimeUnit.MILLISECONDS
        );
    }

    /**
     * 写入时序数据点
     */
    public CompletableFuture<WriteResult> writePoints(String database, List<Point> points) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // 按时间分组到不同的分片
                Map<String, List<Point>> pointsByShards = groupPointsByShards(database, points);

                List<WriteResult> results = new ArrayList<>();

                for (Map.Entry<String, List<Point>> entry : pointsByShards.entrySet()) {
                    String shardId = entry.getKey();
                    List<Point> shardPoints = entry.getValue();

                    WriteResult result = writePointsToShard(shardId, shardPoints);
                    results.add(result);
                }

                return aggregateWriteResults(results);

            } catch (Exception e) {
                return new WriteResult(false, 0, e.getMessage());
            }
        });
    }

    /**
     * 按分片分组数据点
     */
    private Map<String, List<Point>> groupPointsByShards(String database, List<Point> points) {
        Map<String, List<Point>> result = new HashMap<>();

        for (Point point : points) {
            String shardId = findShardForPoint(database, point);
            result.computeIfAbsent(shardId, k -> new ArrayList<>()).add(point);
        }

        return result;
    }

    /**
     * 查找数据点对应的分片
     */
    private String findShardForPoint(String database, Point point) {
        long timestamp = point.getTimestamp();

        // 简化实现：基于时间戳找到对应的分片
        for (Shard shard : localShards.values()) {
            if (shard.getDatabase().equals(database) && shard.containsTime(timestamp)) {
                return shard.getId();
            }
        }

        // 如果没有找到分片，创建新的分片
        return createShardForTime(database, timestamp);
    }

    /**
     * 为指定时间创建分片
     */
    private String createShardForTime(String database, long timestamp) {
        // 计算分片时间窗口（例如：每小时一个分片）
        long shardDuration = 3600000; // 1小时
        long startTime = (timestamp / shardDuration) * shardDuration;
        long endTime = startTime + shardDuration;

        String shardId = database + "_" + startTime + "_" + endTime;
        Shard shard = new Shard(shardId, database, startTime, endTime, Arrays.asList(nodeId));
        localShards.put(shardId, shard);

        return shardId;
    }

    /**
     * 写入数据点到分片
     */
    private WriteResult writePointsToShard(String shardId, List<Point> points) {
        try {
            Shard shard = localShards.get(shardId);
            if (shard == null) {
                return new WriteResult(false, 0, "分片不存在: " + shardId);
            }

            // 首先写入WAL
            for (Point point : points) {
                wal.writePoint(shardId, point);
            }

            // 写入内存中的分片
            int writtenCount = 0;
            for (Point point : points) {
                if (shard.addPoint(point)) {
                    writtenCount++;
                }
            }

            // 检查是否需要刷新到TSM文件
            if (shard.shouldFlush()) {
                flushShardToTSM(shard);
            }

            // 异步复制到其他副本
            replicateToOtherNodes(shardId, points);

            return new WriteResult(true, writtenCount, "写入成功");

        } catch (Exception e) {
            return new WriteResult(false, 0, "写入失败: " + e.getMessage());
        }
    }

    /**
     * 刷新分片到TSM文件
     */
    private void flushShardToTSM(Shard shard) {
        try {
            String fileName = shard.getId() + "_" + System.currentTimeMillis() + ".tsm";
            TSMFile tsmFile = new TSMFile(fileName);

            // 将分片中的数据写入TSM文件
            for (Series series : shard.getAllSeries()) {
                tsmFile.writeSeries(series);
            }

            tsmFile.flush();
            tsmFiles.put(fileName, tsmFile);

            // 清空分片内存数据
            shard.clearMemoryData();

            System.out.println("分片 " + shard.getId() + " 刷新到TSM文件: " + fileName);

        } catch (Exception e) {
            System.err.println("刷新分片到TSM文件失败: " + e.getMessage());
        }
    }

    /**
     * 复制到其他节点
     */
    private void replicateToOtherNodes(String shardId, List<Point> points) {
        Shard shard = localShards.get(shardId);
        if (shard == null) {
            return;
        }

        // 获取分片的其他副本节点
        List<String> otherNodes = shard.getOwners().stream()
                .filter(owner -> !owner.equals(nodeId))
                .collect(Collectors.toList());

        if (otherNodes.isEmpty()) {
            return;
        }

        // 异步复制到其他节点
        CompletableFuture.runAsync(() -> {
            for (String nodeId : otherNodes) {
                try {
                    sendPointsToNode(nodeId, shardId, points);
                } catch (Exception e) {
                    System.err.println("复制到节点 " + nodeId + " 失败: " + e.getMessage());
                }
            }
        });
    }

    /**
     * 发送数据点到指定节点
     */
    private void sendPointsToNode(String targetNodeId, String shardId, List<Point> points) {
        // 模拟网络发送
        try {
            Thread.sleep(10); // 模拟网络延迟
            System.out.println("复制 " + points.size() + " 个数据点到节点 " + targetNodeId);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * 查询时序数据
     */
    public CompletableFuture<QueryResult> queryPoints(String database, String measurement,
                                                     long startTime, long endTime,
                                                     Map<String, String> tags) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                List<Point> result = new ArrayList<>();

                // 查找相关分片
                List<Shard> relevantShards = findShardsForTimeRange(database, startTime, endTime);

                for (Shard shard : relevantShards) {
                    List<Point> shardPoints = queryPointsFromShard(shard, measurement, startTime, endTime, tags);
                    result.addAll(shardPoints);
                }

                // 按时间排序
                result.sort(Comparator.comparing(Point::getTimestamp));

                return new QueryResult(true, result, "查询成功");

            } catch (Exception e) {
                return new QueryResult(false, Collections.emptyList(), "查询失败: " + e.getMessage());
            }
        });
    }

    /**
     * 查找时间范围内的分片
     */
    private List<Shard> findShardsForTimeRange(String database, long startTime, long endTime) {
        return localShards.values().stream()
                .filter(shard -> shard.getDatabase().equals(database))
                .filter(shard -> shard.overlapsTimeRange(startTime, endTime))
                .collect(Collectors.toList());
    }

    /**
     * 从分片查询数据点
     */
    private List<Point> queryPointsFromShard(Shard shard, String measurement,
                                           long startTime, long endTime,
                                           Map<String, String> tags) {
        List<Point> result = new ArrayList<>();

        // 从内存数据查询
        List<Point> memoryPoints = shard.queryPoints(measurement, startTime, endTime, tags);
        result.addAll(memoryPoints);

        // 从TSM文件查询
        for (TSMFile tsmFile : tsmFiles.values()) {
            if (tsmFile.getShardId().equals(shard.getId())) {
                List<Point> tsmPoints = tsmFile.queryPoints(measurement, startTime, endTime, tags);
                result.addAll(tsmPoints);
            }
        }

        return result;
    }

    /**
     * 执行Anti-Entropy
     */
    private void performAntiEntropy() {
        System.out.println("节点 " + nodeId + " 开始执行Anti-Entropy");

        for (Shard shard : localShards.values()) {
            try {
                performShardAntiEntropy(shard);
            } catch (Exception e) {
                System.err.println("分片 " + shard.getId() + " Anti-Entropy失败: " + e.getMessage());
            }
        }
    }

    /**
     * 对单个分片执行Anti-Entropy
     */
    private void performShardAntiEntropy(Shard shard) {
        List<String> otherNodes = shard.getOwners().stream()
                .filter(owner -> !owner.equals(nodeId))
                .collect(Collectors.toList());

        if (otherNodes.isEmpty()) {
            return;
        }

        for (String otherNode : otherNodes) {
            try {
                // 获取其他节点的分片校验和
                String otherChecksum = getShardChecksumFromNode(otherNode, shard.getId());
                String localChecksum = calculateShardChecksum(shard);

                if (!localChecksum.equals(otherChecksum)) {
                    System.out.println("检测到分片 " + shard.getId() + " 与节点 " + otherNode + " 不一致");
                    repairShardWithNode(shard, otherNode);
                }

            } catch (Exception e) {
                System.err.println("与节点 " + otherNode + " 进行Anti-Entropy失败: " + e.getMessage());
            }
        }
    }

    /**
     * 获取其他节点的分片校验和
     */
    private String getShardChecksumFromNode(String nodeId, String shardId) {
        // 模拟网络请求
        return "checksum_" + nodeId + "_" + shardId + "_" + System.currentTimeMillis();
    }

    /**
     * 计算分片校验和
     */
    private String calculateShardChecksum(Shard shard) {
        // 简化的校验和计算
        long pointCount = shard.getPointCount();
        long lastModified = shard.getLastModified();
        return "checksum_" + shard.getId() + "_" + pointCount + "_" + lastModified;
    }

    /**
     * 修复分片与其他节点的差异
     */
    private void repairShardWithNode(Shard shard, String otherNode) {
        System.out.println("开始修复分片 " + shard.getId() + " 与节点 " + otherNode + " 的差异");

        // 获取差异数据
        List<Point> missingPoints = getMissingPointsFromNode(otherNode, shard.getId());

        // 应用差异数据
        for (Point point : missingPoints) {
            shard.addPoint(point);
        }

        System.out.println("修复完成，添加了 " + missingPoints.size() + " 个数据点");
    }

    /**
     * 从其他节点获取缺失的数据点
     */
    private List<Point> getMissingPointsFromNode(String nodeId, String shardId) {
        // 模拟从其他节点获取数据
        List<Point> points = new ArrayList<>();

        // 生成一些模拟数据
        for (int i = 0; i < 5; i++) {
            Point point = new Point(
                "temperature",
                Map.of("location", "room" + i),
                Map.of("value", 20.0 + i),
                System.currentTimeMillis() + i * 1000
            );
            points.add(point);
        }

        return points;
    }

    /**
     * 聚合写入结果
     */
    private WriteResult aggregateWriteResults(List<WriteResult> results) {
        boolean allSuccess = results.stream().allMatch(WriteResult::isSuccess);
        int totalWritten = results.stream().mapToInt(WriteResult::getPointsWritten).sum();

        if (allSuccess) {
            return new WriteResult(true, totalWritten, "所有写入成功");
        } else {
            String errorMsg = results.stream()
                    .filter(r -> !r.isSuccess())
                    .map(WriteResult::getMessage)
                    .collect(Collectors.joining("; "));
            return new WriteResult(false, totalWritten, "部分写入失败: " + errorMsg);
        }
    }

    /**
     * 获取节点状态
     */
    public DataNodeStatus getStatus() {
        long totalPoints = localShards.values().stream()
                .mapToLong(Shard::getPointCount)
                .sum();

        return new DataNodeStatus(
            nodeId,
            localShards.size(),
            totalPoints,
            tsmFiles.size(),
            wal.getSize()
        );
    }

    /**
     * 关闭数据节点
     */
    public void shutdown() {
        antiEntropyScheduler.shutdown();

        // 刷新所有分片
        for (Shard shard : localShards.values()) {
            if (shard.hasMemoryData()) {
                flushShardToTSM(shard);
            }
        }

        // 关闭WAL
        wal.close();

        // 关闭TSM文件
        for (TSMFile tsmFile : tsmFiles.values()) {
            tsmFile.close();
        }
    }
}

/**
 * 数据点
 */
class Point {
    private final String measurement;
    private final Map<String, String> tags;
    private final Map<String, Object> fields;
    private final long timestamp;

    public Point(String measurement, Map<String, String> tags, Map<String, Object> fields, long timestamp) {
        this.measurement = measurement;
        this.tags = new HashMap<>(tags);
        this.fields = new HashMap<>(fields);
        this.timestamp = timestamp;
    }

    // Getters
    public String getMeasurement() { return measurement; }
    public Map<String, String> getTags() { return new HashMap<>(tags); }
    public Map<String, Object> getFields() { return new HashMap<>(fields); }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("Point{measurement='%s', tags=%s, fields=%s, timestamp=%d}",
                measurement, tags, fields, timestamp);
    }
}

/**
 * 分片实现
 */
class Shard {
    private final String id;
    private final String database;
    private final long startTime;
    private final long endTime;
    private final List<String> owners;

    private final Map<String, Series> series = new ConcurrentHashMap<>();
    private final AtomicLong pointCount = new AtomicLong(0);
    private volatile long lastModified = System.currentTimeMillis();

    public Shard(String id, String database, long startTime, long endTime, List<String> owners) {
        this.id = id;
        this.database = database;
        this.startTime = startTime;
        this.endTime = endTime;
        this.owners = new ArrayList<>(owners);
    }

    /**
     * 添加数据点
     */
    public boolean addPoint(Point point) {
        if (!containsTime(point.getTimestamp())) {
            return false;
        }

        String seriesKey = generateSeriesKey(point.getMeasurement(), point.getTags());
        Series targetSeries = series.computeIfAbsent(seriesKey,
            k -> new Series(point.getMeasurement(), point.getTags()));

        targetSeries.addPoint(point);
        pointCount.incrementAndGet();
        lastModified = System.currentTimeMillis();

        return true;
    }

    /**
     * 检查时间是否在分片范围内
     */
    public boolean containsTime(long timestamp) {
        return timestamp >= startTime && timestamp < endTime;
    }

    /**
     * 检查时间范围是否重叠
     */
    public boolean overlapsTimeRange(long start, long end) {
        return !(end <= startTime || start >= endTime);
    }

    /**
     * 查询数据点
     */
    public List<Point> queryPoints(String measurement, long startTime, long endTime, Map<String, String> tags) {
        List<Point> result = new ArrayList<>();

        for (Series s : series.values()) {
            if (s.matches(measurement, tags)) {
                List<Point> seriesPoints = s.getPointsInRange(startTime, endTime);
                result.addAll(seriesPoints);
            }
        }

        return result;
    }

    /**
     * 检查是否需要刷新
     */
    public boolean shouldFlush() {
        return pointCount.get() > 100000 || // 超过10万个点
               System.currentTimeMillis() - lastModified > 300000; // 超过5分钟
    }

    /**
     * 清空内存数据
     */
    public void clearMemoryData() {
        series.clear();
        pointCount.set(0);
    }

    /**
     * 检查是否有内存数据
     */
    public boolean hasMemoryData() {
        return !series.isEmpty();
    }

    /**
     * 生成系列键
     */
    private String generateSeriesKey(String measurement, Map<String, String> tags) {
        StringBuilder sb = new StringBuilder(measurement);
        tags.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> sb.append(",").append(entry.getKey()).append("=").append(entry.getValue()));
        return sb.toString();
    }

    // Getters
    public String getId() { return id; }
    public String getDatabase() { return database; }
    public long getStartTime() { return startTime; }
    public long getEndTime() { return endTime; }
    public List<String> getOwners() { return new ArrayList<>(owners); }
    public long getPointCount() { return pointCount.get(); }
    public long getLastModified() { return lastModified; }
    public Collection<Series> getAllSeries() { return new ArrayList<>(series.values()); }
}

/**
 * 时序数据系列
 */
class Series {
    private final String measurement;
    private final Map<String, String> tags;
    private final List<Point> points = new ArrayList<>();

    public Series(String measurement, Map<String, String> tags) {
        this.measurement = measurement;
        this.tags = new HashMap<>(tags);
    }

    /**
     * 添加数据点
     */
    public synchronized void addPoint(Point point) {
        points.add(point);
        // 保持按时间排序
        points.sort(Comparator.comparing(Point::getTimestamp));
    }

    /**
     * 检查是否匹配查询条件
     */
    public boolean matches(String measurement, Map<String, String> queryTags) {
        if (!this.measurement.equals(measurement)) {
            return false;
        }

        for (Map.Entry<String, String> entry : queryTags.entrySet()) {
            String tagValue = tags.get(entry.getKey());
            if (!entry.getValue().equals(tagValue)) {
                return false;
            }
        }

        return true;
    }

    /**
     * 获取时间范围内的数据点
     */
    public List<Point> getPointsInRange(long startTime, long endTime) {
        return points.stream()
                .filter(point -> point.getTimestamp() >= startTime && point.getTimestamp() < endTime)
                .collect(Collectors.toList());
    }

    // Getters
    public String getMeasurement() { return measurement; }
    public Map<String, String> getTags() { return new HashMap<>(tags); }
    public List<Point> getPoints() { return new ArrayList<>(points); }
}

/**
 * WAL (Write-Ahead Log)
 */
class WAL {
    private final Map<String, List<Point>> walData = new ConcurrentHashMap<>();

    public void writePoint(String shardId, Point point) {
        walData.computeIfAbsent(shardId, k -> new ArrayList<>()).add(point);
    }

    public long getSize() {
        return walData.values().stream().mapToLong(List::size).sum();
    }

    public void close() {
        walData.clear();
    }
}

/**
 * TSM文件
 */
class TSMFile {
    private final String fileName;
    private final String shardId;
    private final Map<String, Series> storedSeries = new HashMap<>();

    public TSMFile(String fileName) {
        this.fileName = fileName;
        this.shardId = extractShardIdFromFileName(fileName);
    }

    public void writeSeries(Series series) {
        storedSeries.put(generateSeriesKey(series), series);
    }

    public void flush() {
        // 模拟写入磁盘
        System.out.println("TSM文件 " + fileName + " 写入磁盘，包含 " + storedSeries.size() + " 个系列");
    }

    public List<Point> queryPoints(String measurement, long startTime, long endTime, Map<String, String> tags) {
        List<Point> result = new ArrayList<>();

        for (Series series : storedSeries.values()) {
            if (series.matches(measurement, tags)) {
                List<Point> seriesPoints = series.getPointsInRange(startTime, endTime);
                result.addAll(seriesPoints);
            }
        }

        return result;
    }

    public void close() {
        storedSeries.clear();
    }

    private String extractShardIdFromFileName(String fileName) {
        return fileName.substring(0, fileName.lastIndexOf('_'));
    }

    private String generateSeriesKey(Series series) {
        StringBuilder sb = new StringBuilder(series.getMeasurement());
        series.getTags().entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> sb.append(",").append(entry.getKey()).append("=").append(entry.getValue()));
        return sb.toString();
    }

    public String getShardId() { return shardId; }
    public String getFileName() { return fileName; }
}

/**
 * 写入结果
 */
class WriteResult {
    private final boolean success;
    private final int pointsWritten;
    private final String message;

    public WriteResult(boolean success, int pointsWritten, String message) {
        this.success = success;
        this.pointsWritten = pointsWritten;
        this.message = message;
    }

    // Getters
    public boolean isSuccess() { return success; }
    public int getPointsWritten() { return pointsWritten; }
    public String getMessage() { return message; }
}

/**
 * 查询结果
 */
class QueryResult {
    private final boolean success;
    private final List<Point> points;
    private final String message;

    public QueryResult(boolean success, List<Point> points, String message) {
        this.success = success;
        this.points = new ArrayList<>(points);
        this.message = message;
    }

    // Getters
    public boolean isSuccess() { return success; }
    public List<Point> getPoints() { return new ArrayList<>(points); }
    public String getMessage() { return message; }
}

/**
 * 数据节点状态
 */
class DataNodeStatus {
    private final String nodeId;
    private final int shardCount;
    private final long totalPoints;
    private final int tsmFileCount;
    private final long walSize;

    public DataNodeStatus(String nodeId, int shardCount, long totalPoints, int tsmFileCount, long walSize) {
        this.nodeId = nodeId;
        this.shardCount = shardCount;
        this.totalPoints = totalPoints;
        this.tsmFileCount = tsmFileCount;
        this.walSize = walSize;
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public int getShardCount() { return shardCount; }
    public long getTotalPoints() { return totalPoints; }
    public int getTsmFileCount() { return tsmFileCount; }
    public long getWalSize() { return walSize; }

    @Override
    public String toString() {
        return String.format("DataNodeStatus{nodeId='%s', shards=%d, points=%d, tsmFiles=%d, walSize=%d}",
                nodeId, shardCount, totalPoints, tsmFileCount, walSize);
    }
}
```

## 5. InfluxDB集群管理器

### 5.1 集群协调器

```java
/**
 * InfluxDB集群管理器
 */
public class InfluxDBClusterManager {
    private final Map<String, InfluxDBMetaNode> metaNodes = new ConcurrentHashMap<>();
    private final Map<String, InfluxDBDataNode> dataNodes = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

    // 集群配置
    private final int replicationFactor = 2;
    private final long shardDuration = 3600000; // 1小时

    public InfluxDBClusterManager() {
        // 启动集群监控
        scheduler.scheduleAtFixedRate(this::monitorCluster, 30, 30, TimeUnit.SECONDS);
    }

    /**
     * 添加Meta节点
     */
    public void addMetaNode(InfluxDBMetaNode metaNode) {
        metaNodes.put(metaNode.getNodeId(), metaNode);
        System.out.println("添加Meta节点: " + metaNode.getNodeId());
    }

    /**
     * 添加数据节点
     */
    public void addDataNode(InfluxDBDataNode dataNode) {
        dataNodes.put(dataNode.getNodeId(), dataNode);
        System.out.println("添加数据节点: " + dataNode.getNodeId());
    }

    /**
     * 创建数据库
     */
    public CompletableFuture<Boolean> createDatabase(String dbName, RetentionPolicy policy) {
        InfluxDBMetaNode leader = findMetaLeader();
        if (leader == null) {
            return CompletableFuture.completedFuture(false);
        }

        return leader.createDatabase(dbName, policy)
                .thenCompose(success -> {
                    if (success) {
                        return createInitialShards(dbName);
                    }
                    return CompletableFuture.completedFuture(false);
                });
    }

    /**
     * 创建初始分片
     */
    private CompletableFuture<Boolean> createInitialShards(String dbName) {
        long currentTime = System.currentTimeMillis();
        long startTime = (currentTime / shardDuration) * shardDuration;
        long endTime = startTime + shardDuration;

        // 选择数据节点
        List<String> selectedNodes = selectDataNodes(replicationFactor);

        InfluxDBMetaNode leader = findMetaLeader();
        if (leader == null || selectedNodes.size() < replicationFactor) {
            return CompletableFuture.completedFuture(false);
        }

        return leader.createShard(dbName, startTime, endTime, selectedNodes);
    }

    /**
     * 选择数据节点
     */
    private List<String> selectDataNodes(int count) {
        List<String> nodeIds = new ArrayList<>(dataNodes.keySet());
        Collections.shuffle(nodeIds);
        return nodeIds.subList(0, Math.min(count, nodeIds.size()));
    }

    /**
     * 查找Meta Leader
     */
    private InfluxDBMetaNode findMetaLeader() {
        return metaNodes.values().stream()
                .filter(node -> node.getRole() == RaftRole.LEADER)
                .findFirst()
                .orElse(null);
    }

    /**
     * 写入数据
     */
    public CompletableFuture<WriteResult> writePoints(String database, List<Point> points) {
        // 选择一个数据节点进行写入
        InfluxDBDataNode dataNode = selectDataNodeForWrite();
        if (dataNode == null) {
            return CompletableFuture.completedFuture(
                new WriteResult(false, 0, "没有可用的数据节点"));
        }

        return dataNode.writePoints(database, points);
    }

    /**
     * 查询数据
     */
    public CompletableFuture<QueryResult> queryPoints(String database, String measurement,
                                                     long startTime, long endTime,
                                                     Map<String, String> tags) {
        // 从所有相关数据节点查询并聚合结果
        List<CompletableFuture<QueryResult>> futures = new ArrayList<>();

        for (InfluxDBDataNode dataNode : dataNodes.values()) {
            CompletableFuture<QueryResult> future = dataNode.queryPoints(database, measurement, startTime, endTime, tags);
            futures.add(future);
        }

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> {
                    List<Point> allPoints = new ArrayList<>();
                    boolean anySuccess = false;

                    for (CompletableFuture<QueryResult> future : futures) {
                        try {
                            QueryResult result = future.get();
                            if (result.isSuccess()) {
                                allPoints.addAll(result.getPoints());
                                anySuccess = true;
                            }
                        } catch (Exception e) {
                            // 忽略单个节点的失败
                        }
                    }

                    // 去重并排序
                    allPoints = allPoints.stream()
                            .distinct()
                            .sorted(Comparator.comparing(Point::getTimestamp))
                            .collect(Collectors.toList());

                    return new QueryResult(anySuccess, allPoints, "查询完成");
                });
    }

    /**
     * 选择数据节点进行写入
     */
    private InfluxDBDataNode selectDataNodeForWrite() {
        List<InfluxDBDataNode> nodes = new ArrayList<>(dataNodes.values());
        if (nodes.isEmpty()) {
            return null;
        }

        // 简单的轮询选择
        int index = (int) (System.currentTimeMillis() % nodes.size());
        return nodes.get(index);
    }

    /**
     * 监控集群状态
     */
    private void monitorCluster() {
        System.out.println("\n=== 集群监控 ===");

        // 监控Meta节点
        System.out.println("Meta节点状态:");
        for (InfluxDBMetaNode metaNode : metaNodes.values()) {
            ClusterStatus status = metaNode.getClusterStatus();
            System.out.println("  " + status);
        }

        // 监控数据节点
        System.out.println("数据节点状态:");
        for (InfluxDBDataNode dataNode : dataNodes.values()) {
            DataNodeStatus status = dataNode.getStatus();
            System.out.println("  " + status);
        }

        System.out.println("================\n");
    }

    /**
     * 获取集群统计信息
     */
    public ClusterStatistics getClusterStatistics() {
        int metaNodeCount = metaNodes.size();
        int dataNodeCount = dataNodes.size();

        long totalPoints = dataNodes.values().stream()
                .mapToLong(node -> node.getStatus().getTotalPoints())
                .sum();

        int totalShards = dataNodes.values().stream()
                .mapToInt(node -> node.getStatus().getShardCount())
                .sum();

        InfluxDBMetaNode leader = findMetaLeader();
        int databaseCount = leader != null ? leader.getDatabases().size() : 0;

        return new ClusterStatistics(
            metaNodeCount,
            dataNodeCount,
            databaseCount,
            totalShards,
            totalPoints
        );
    }

    /**
     * 关闭集群
     */
    public void shutdown() {
        scheduler.shutdown();

        // 关闭所有节点
        for (InfluxDBMetaNode metaNode : metaNodes.values()) {
            metaNode.shutdown();
        }

        for (InfluxDBDataNode dataNode : dataNodes.values()) {
            dataNode.shutdown();
        }

        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * 集群统计信息
 */
class ClusterStatistics {
    private final int metaNodeCount;
    private final int dataNodeCount;
    private final int databaseCount;
    private final int shardCount;
    private final long totalPoints;

    public ClusterStatistics(int metaNodeCount, int dataNodeCount, int databaseCount,
                           int shardCount, long totalPoints) {
        this.metaNodeCount = metaNodeCount;
        this.dataNodeCount = dataNodeCount;
        this.databaseCount = databaseCount;
        this.shardCount = shardCount;
        this.totalPoints = totalPoints;
    }

    // Getters
    public int getMetaNodeCount() { return metaNodeCount; }
    public int getDataNodeCount() { return dataNodeCount; }
    public int getDatabaseCount() { return databaseCount; }
    public int getShardCount() { return shardCount; }
    public long getTotalPoints() { return totalPoints; }

    @Override
    public String toString() {
        return String.format("ClusterStatistics{metaNodes=%d, dataNodes=%d, databases=%d, shards=%d, points=%d}",
                metaNodeCount, dataNodeCount, databaseCount, shardCount, totalPoints);
    }
}
```

## 6. 完整测试示例

### 6.1 InfluxDB集群测试

```java
/**
 * InfluxDB企业版集群测试
 */
public class InfluxDBClusterTest {

    public static void main(String[] args) throws Exception {
        testInfluxDBCluster();
    }

    /**
     * 测试InfluxDB集群
     */
    private static void testInfluxDBCluster() throws Exception {
        System.out.println("=== InfluxDB企业版集群测试开始 ===\n");

        // 创建集群管理器
        InfluxDBClusterManager clusterManager = new InfluxDBClusterManager();

        try {
            // 创建Meta节点集群
            createMetaCluster(clusterManager);

            // 创建数据节点集群
            createDataCluster(clusterManager);

            // 等待集群稳定
            Thread.sleep(5000);

            // 创建数据库
            testDatabaseCreation(clusterManager);

            // 测试数据写入
            testDataWriting(clusterManager);

            // 测试数据查询
            testDataQuerying(clusterManager);

            // 测试Anti-Entropy
            testAntiEntropy(clusterManager);

            // 性能测试
            performanceTest(clusterManager);

        } finally {
            clusterManager.shutdown();
        }

        System.out.println("\n=== InfluxDB企业版集群测试完成 ===");
    }

    /**
     * 创建Meta节点集群
     */
    private static void createMetaCluster(InfluxDBClusterManager clusterManager) {
        System.out.println("=== 创建Meta节点集群 ===");

        Set<String> metaNodeIds = Set.of("meta-1", "meta-2", "meta-3");

        for (String nodeId : metaNodeIds) {
            InfluxDBMetaNode metaNode = new InfluxDBMetaNode(nodeId, metaNodeIds);
            clusterManager.addMetaNode(metaNode);
        }

        System.out.println("Meta节点集群创建完成\n");
    }

    /**
     * 创建数据节点集群
     */
    private static void createDataCluster(InfluxDBClusterManager clusterManager) {
        System.out.println("=== 创建数据节点集群 ===");

        String[] dataNodeIds = {"data-1", "data-2", "data-3", "data-4"};

        for (String nodeId : dataNodeIds) {
            InfluxDBDataNode dataNode = new InfluxDBDataNode(nodeId, "meta-1:8088");
            clusterManager.addDataNode(dataNode);
        }

        System.out.println("数据节点集群创建完成\n");
    }

    /**
     * 测试数据库创建
     */
    private static void testDatabaseCreation(InfluxDBClusterManager clusterManager) throws Exception {
        System.out.println("=== 测试数据库创建 ===");

        RetentionPolicy policy = new RetentionPolicy("default", 7 * 24 * 3600 * 1000L, 2, true); // 7天保留

        boolean result = clusterManager.createDatabase("sensor_data", policy).get();
        System.out.println("数据库创建结果: " + (result ? "成功" : "失败"));

        result = clusterManager.createDatabase("metrics", policy).get();
        System.out.println("数据库创建结果: " + (result ? "成功" : "失败"));

        System.out.println("数据库创建测试完成\n");
    }

    /**
     * 测试数据写入
     */
    private static void testDataWriting(InfluxDBClusterManager clusterManager) throws Exception {
        System.out.println("=== 测试数据写入 ===");

        List<Point> points = generateTestPoints(100);

        WriteResult result = clusterManager.writePoints("sensor_data", points).get();
        System.out.println("写入结果: " + result.getMessage() + ", 写入点数: " + result.getPointsWritten());

        // 批量写入测试
        for (int i = 0; i < 5; i++) {
            List<Point> batchPoints = generateTestPoints(50);
            WriteResult batchResult = clusterManager.writePoints("sensor_data", batchPoints).get();
            System.out.println("批次 " + (i + 1) + " 写入: " + batchResult.getPointsWritten() + " 个点");
        }

        System.out.println("数据写入测试完成\n");
    }

    /**
     * 测试数据查询
     */
    private static void testDataQuerying(InfluxDBClusterManager clusterManager) throws Exception {
        System.out.println("=== 测试数据查询 ===");

        long endTime = System.currentTimeMillis();
        long startTime = endTime - 3600000; // 1小时前

        Map<String, String> tags = Map.of("location", "room1");

        QueryResult result = clusterManager.queryPoints("sensor_data", "temperature", startTime, endTime, tags).get();

        if (result.isSuccess()) {
            System.out.println("查询成功，返回 " + result.getPoints().size() + " 个数据点");

            // 显示前5个数据点
            result.getPoints().stream()
                    .limit(5)
                    .forEach(point -> System.out.println("  " + point));
        } else {
            System.out.println("查询失败: " + result.getMessage());
        }

        System.out.println("数据查询测试完成\n");
    }

    /**
     * 测试Anti-Entropy
     */
    private static void testAntiEntropy(InfluxDBClusterManager clusterManager) {
        System.out.println("=== 测试Anti-Entropy ===");

        // Anti-Entropy会在后台自动运行
        System.out.println("Anti-Entropy机制在后台运行中...");

        // 模拟数据不一致的场景
        System.out.println("模拟数据修复场景...");

        try {
            Thread.sleep(10000); // 等待Anti-Entropy执行
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("Anti-Entropy测试完成\n");
    }

    /**
     * 性能测试
     */
    private static void performanceTest(InfluxDBClusterManager clusterManager) throws Exception {
        System.out.println("=== 性能测试 ===");

        int pointCount = 1000;
        long startTime = System.currentTimeMillis();

        // 写入性能测试
        List<Point> points = generateTestPoints(pointCount);
        WriteResult writeResult = clusterManager.writePoints("metrics", points).get();

        long writeEndTime = System.currentTimeMillis();
        long writeDuration = writeEndTime - startTime;

        System.out.println("写入性能测试:");
        System.out.println("  数据点数: " + pointCount);
        System.out.println("  写入耗时: " + writeDuration + "ms");
        System.out.println("  写入速率: " + (pointCount * 1000.0 / writeDuration) + " 点/秒");

        // 查询性能测试
        long queryStartTime = System.currentTimeMillis();
        long endTime = System.currentTimeMillis();
        long queryStart = endTime - 3600000;

        QueryResult queryResult = clusterManager.queryPoints("metrics", "cpu_usage", queryStart, endTime, Map.of()).get();

        long queryEndTime = System.currentTimeMillis();
        long queryDuration = queryEndTime - queryStartTime;

        System.out.println("查询性能测试:");
        System.out.println("  查询耗时: " + queryDuration + "ms");
        System.out.println("  返回点数: " + queryResult.getPoints().size());

        // 集群统计
        ClusterStatistics stats = clusterManager.getClusterStatistics();
        System.out.println("集群统计: " + stats);

        System.out.println("性能测试完成\n");
    }

    /**
     * 生成测试数据点
     */
    private static List<Point> generateTestPoints(int count) {
        List<Point> points = new ArrayList<>();
        long baseTime = System.currentTimeMillis();
        Random random = new Random();

        String[] measurements = {"temperature", "humidity", "cpu_usage", "memory_usage"};
        String[] locations = {"room1", "room2", "room3", "server1", "server2"};

        for (int i = 0; i < count; i++) {
            String measurement = measurements[random.nextInt(measurements.length)];
            String location = locations[random.nextInt(locations.length)];

            Map<String, String> tags = Map.of(
                "location", location,
                "sensor_id", "sensor_" + random.nextInt(10)
            );

            Map<String, Object> fields = Map.of(
                "value", 20.0 + random.nextDouble() * 60.0,
                "status", random.nextBoolean() ? "ok" : "warning"
            );

            long timestamp = baseTime + i * 1000 + random.nextInt(1000); // 添加一些随机性

            Point point = new Point(measurement, tags, fields, timestamp);
            points.add(point);
        }

        return points;
    }

    /**
     * 故障恢复测试
     */
    private static void testFailureRecovery() {
        System.out.println("=== 故障恢复测试 ===");

        // 模拟各种故障场景
        // 1. Meta节点故障
        // 2. 数据节点故障
        // 3. 网络分区
        // 4. 数据损坏恢复

        System.out.println("故障恢复测试完成");
    }
}
```

## 7. 总结

InfluxDB企业版通过精心设计的分布式架构实现了时序数据库的高可用性和一致性保证：

### 7.1 核心特性
- **分层一致性**：Meta数据强一致性，时序数据最终一致性
- **Raft共识**：Meta节点使用Raft保证配置一致性
- **Anti-Entropy**：自动数据修复机制
- **分片管理**：基于时间的数据分片策略

### 7.2 架构优势
- **专为时序数据优化**：考虑时序数据的特殊性质
- **高写入性能**：优先保证写入吞吐量
- **水平扩展**：支持动态添加节点
- **故障容错**：多副本和自动恢复机制

### 7.3 一致性保证
- **Meta数据**：使用Raft协议保证强一致性
- **时序数据**：异步复制 + Anti-Entropy修复
- **冲突解决**：基于时间戳的冲突解决策略
- **最终一致性**：保证数据最终达到一致状态

### 7.4 应用场景
- **IoT数据采集**：大规模传感器数据存储
- **系统监控**：服务器和应用性能监控
- **金融数据**：股票价格、交易数据存储
- **日志分析**：时间序列日志数据分析

### 7.5 设计启示
- **业务特性优化**：针对具体业务场景优化一致性模型
- **分层设计**：不同类型数据采用不同一致性策略
- **自动修复**：Anti-Entropy等自动化机制
- **性能权衡**：在一致性和性能间找到平衡

### 7.6 实际应用考虑
- **数据分片策略**：合理的时间窗口分片
- **副本放置**：考虑机架感知的副本分布
- **压缩策略**：时序数据的高效压缩
- **查询优化**：时间范围查询的优化

通过本文的详细分析和实现，你可以深入理解InfluxDB企业版的分布式一致性设计理念，为构建高性能时序数据库系统提供重要参考。