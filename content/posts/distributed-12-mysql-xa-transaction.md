---
title: "分布式系统核心技术详解：MySQL XA分布式事务原理与Java实现"
date: 2024-12-19T14:00:00+08:00
draft: false
tags: ["分布式系统", "MySQL", "XA事务", "分布式事务", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入解析MySQL XA分布式事务的工作原理、两阶段提交协议以及在分布式系统中的应用实践，包含完整的Java实现代码"
---

## 1. MySQL XA事务概述

XA（eXtended Architecture）是由X/Open组织提出的分布式事务处理标准，MySQL从5.0版本开始支持XA事务。XA事务允许多个数据库参与同一个全局事务，确保分布式环境下的数据一致性。

### 1.1 核心概念

- **全局事务（Global Transaction）**：跨多个资源管理器的事务
- **事务管理器（Transaction Manager, TM）**：协调全局事务的组件
- **资源管理器（Resource Manager, RM）**：管理实际资源的组件（如MySQL数据库）
- **两阶段提交（2PC）**：XA事务的核心协议

### 1.2 XA事务模型

#### 流程图表


**关系流向：**
```
A[应用程序] → B[事务管理器 TM]
B → C[资源管理器 RM1]
B → D[资源管理器 RM2]
B → E[资源管理器 RM3]
C → F[MySQL数据库1]
```

## 2. XA事务的两阶段提交协议

### 2.1 协议流程

#### 序列图

| 步骤 | 参与者 | 动作 | 目标 | 说明 |
|------|--------|------|------|------|
| 1 | App | 发送 | TM | 开始全局事务 |
| 2 | TM | 发送 | RM1 | XA START |
| 3 | TM | 发送 | RM2 | XA START |
| 4 | App | 发送 | RM1 | 执行SQL操作 |
| 5 | App | 发送 | RM2 | 执行SQL操作 |
| 6 | App | 发送 | TM | 提交全局事务 |
| 7 | TM | 发送 | RM1 | XA PREPARE |
| 8 | RM1 | 发送 | TM | OK/ABORT |
| 9 | TM | 发送 | RM2 | XA PREPARE |
| 10 | RM2 | 发送 | TM | OK/ABORT |
| 11 | TM | 发送 | RM1 | XA COMMIT |
| 12 | TM | 发送 | RM2 | XA COMMIT |


### 2.2 XA事务状态

- **ACTIVE**：事务活跃状态，可以执行SQL操作
- **IDLE**：事务空闲状态，等待下一个操作
- **PREPARED**：事务已准备好提交
- **COMMITTED**：事务已提交
- **ROLLBACK**：事务已回滚

## 3. MySQL XA事务基础实现

### 3.1 XA事务标识和状态管理

```java
import java.nio.ByteBuffer;
import java.util.*;
import java.util.concurrent.*;

/**
 * XA事务标识符
 */
public class XATransactionId {
    private final String globalTransactionId;  // 全局事务ID
    private final String branchQualifier;      // 分支限定符
    private final int formatId;                // 格式ID

    public XATransactionId(String globalTransactionId, String branchQualifier, int formatId) {
        this.globalTransactionId = globalTransactionId;
        this.branchQualifier = branchQualifier;
        this.formatId = formatId;
    }

    public XATransactionId(String globalTransactionId, String branchQualifier) {
        this(globalTransactionId, branchQualifier, 1);
    }

    /**
     * 生成唯一的XA事务ID
     */
    public static XATransactionId generate(String nodeId) {
        String gtrid = nodeId + "-" + System.currentTimeMillis() + "-" +
                      Thread.currentThread().getId();
        String bqual = "branch-" + UUID.randomUUID().toString().substring(0, 8);
        return new XATransactionId(gtrid, bqual);
    }

    /**
     * 转换为MySQL XA格式
     */
    public String toMySQLFormat() {
        return String.format("'%s','%s',%d", globalTransactionId, branchQualifier, formatId);
    }

    @Override
    public String toString() {
        return String.format("XID{gtrid='%s', bqual='%s', formatId=%d}",
                globalTransactionId, branchQualifier, formatId);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        XATransactionId that = (XATransactionId) obj;
        return formatId == that.formatId &&
               Objects.equals(globalTransactionId, that.globalTransactionId) &&
               Objects.equals(branchQualifier, that.branchQualifier);
    }

    @Override
    public int hashCode() {
        return Objects.hash(globalTransactionId, branchQualifier, formatId);
    }

    // Getters
    public String getGlobalTransactionId() { return globalTransactionId; }
    public String getBranchQualifier() { return branchQualifier; }
    public int getFormatId() { return formatId; }
}

/**
 * XA事务状态枚举
 */
public enum XATransactionState {
    ACTIVE,     // 活跃状态
    IDLE,       // 空闲状态
    PREPARED,   // 已准备
    COMMITTED,  // 已提交
    ABORTED,    // 已中止
    UNKNOWN     // 未知状态
}

/**
 * XA事务信息
 */
public class XATransactionInfo {
    private final XATransactionId xid;
    private volatile XATransactionState state;
    private final long createTime;
    private volatile long lastActiveTime;
    private final Map<String, Object> attributes = new ConcurrentHashMap<>();

    public XATransactionInfo(XATransactionId xid) {
        this.xid = xid;
        this.state = XATransactionState.ACTIVE;
        this.createTime = System.currentTimeMillis();
        this.lastActiveTime = createTime;
    }

    /**
     * 更新活跃时间
     */
    public void touch() {
        this.lastActiveTime = System.currentTimeMillis();
    }

    /**
     * 获取事务存活时间
     */
    public long getAgeInMillis() {
        return System.currentTimeMillis() - createTime;
    }

    /**
     * 获取空闲时间
     */
    public long getIdleTimeInMillis() {
        return System.currentTimeMillis() - lastActiveTime;
    }

    /**
     * 设置属性
     */
    public void setAttribute(String key, Object value) {
        attributes.put(key, value);
    }

    /**
     * 获取属性
     */
    public <T> T getAttribute(String key, Class<T> type) {
        Object value = attributes.get(key);
        return type.isInstance(value) ? type.cast(value) : null;
    }

    // Getters and Setters
    public XATransactionId getXid() { return xid; }
    public XATransactionState getState() { return state; }
    public void setState(XATransactionState state) {
        this.state = state;
        touch();
    }
    public long getCreateTime() { return createTime; }
    public long getLastActiveTime() { return lastActiveTime; }
    public Map<String, Object> getAttributes() { return new HashMap<>(attributes); }

    @Override
    public String toString() {
        return String.format("XATransactionInfo{xid=%s, state=%s, age=%dms, idle=%dms}",
                xid, state, getAgeInMillis(), getIdleTimeInMillis());
    }
}
```

### 3.2 XA资源管理器实现

```java
import java.sql.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * MySQL XA资源管理器
 */
public class MySQLXAResourceManager {
    private final String resourceId;
    private final String jdbcUrl;
    private final String username;
    private final String password;
    private final Map<XATransactionId, XATransactionInfo> activeTransactions = new ConcurrentHashMap<>();

    // 连接池（简化实现）
    private final BlockingQueue<Connection> connectionPool = new LinkedBlockingQueue<>();
    private final AtomicBoolean initialized = new AtomicBoolean(false);
    private final int maxConnections = 10;

    public MySQLXAResourceManager(String resourceId, String jdbcUrl, String username, String password) {
        this.resourceId = resourceId;
        this.jdbcUrl = jdbcUrl;
        this.username = username;
        this.password = password;
    }

    /**
     * 初始化资源管理器
     */
    public void initialize() throws SQLException {
        if (initialized.compareAndSet(false, true)) {
            // 预创建连接池
            for (int i = 0; i < maxConnections; i++) {
                Connection conn = DriverManager.getConnection(jdbcUrl, username, password);
                connectionPool.offer(conn);
            }
            System.out.println("MySQL XA资源管理器初始化完成: " + resourceId);
        }
    }

    /**
     * 获取连接
     */
    private Connection getConnection() throws SQLException {
        try {
            Connection conn = connectionPool.poll(5, TimeUnit.SECONDS);
            if (conn == null) {
                throw new SQLException("获取数据库连接超时");
            }
            if (conn.isClosed()) {
                conn = DriverManager.getConnection(jdbcUrl, username, password);
            }
            return conn;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new SQLException("获取连接被中断", e);
        }
    }

    /**
     * 归还连接
     */
    private void returnConnection(Connection conn) {
        if (conn != null) {
            try {
                if (!conn.isClosed() && connectionPool.remainingCapacity() > 0) {
                    connectionPool.offer(conn);
                } else {
                    conn.close();
                }
            } catch (SQLException e) {
                System.err.println("归还连接失败: " + e.getMessage());
            }
        }
    }

    /**
     * 开始XA事务
     */
    public void xaStart(XATransactionId xid) throws SQLException {
        Connection conn = getConnection();
        try {
            executeXACommand(conn, "XA START " + xid.toMySQLFormat());

            XATransactionInfo txInfo = new XATransactionInfo(xid);
            txInfo.setAttribute("connection", conn);
            activeTransactions.put(xid, txInfo);

            System.out.println("XA START: " + xid + " on " + resourceId);
        } catch (SQLException e) {
            returnConnection(conn);
            throw e;
        }
    }

    /**
     * 结束XA事务
     */
    public void xaEnd(XATransactionId xid) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try {
            executeXACommand(conn, "XA END " + xid.toMySQLFormat());
            txInfo.setState(XATransactionState.IDLE);

            System.out.println("XA END: " + xid + " on " + resourceId);
        } catch (SQLException e) {
            System.err.println("XA END失败: " + xid + ", " + e.getMessage());
            throw e;
        }
    }

    /**
     * 准备XA事务
     */
    public XAPrepareResult xaPrepare(XATransactionId xid) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        if (txInfo.getState() != XATransactionState.IDLE) {
            throw new SQLException("XA事务状态错误: " + txInfo.getState());
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try {
            executeXACommand(conn, "XA PREPARE " + xid.toMySQLFormat());
            txInfo.setState(XATransactionState.PREPARED);

            System.out.println("XA PREPARE: " + xid + " on " + resourceId + " - OK");
            return XAPrepareResult.OK;

        } catch (SQLException e) {
            System.err.println("XA PREPARE失败: " + xid + ", " + e.getMessage());

            // 根据错误码判断结果
            if (e.getErrorCode() == 1399) { // XA_RBROLLBACK
                txInfo.setState(XATransactionState.ABORTED);
                return XAPrepareResult.ROLLBACK;
            } else {
                throw e;
            }
        }
    }

    /**
     * 提交XA事务
     */
    public void xaCommit(XATransactionId xid, boolean onePhase) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try {
            String command = onePhase ?
                "XA COMMIT " + xid.toMySQLFormat() + " ONE PHASE" :
                "XA COMMIT " + xid.toMySQLFormat();

            executeXACommand(conn, command);
            txInfo.setState(XATransactionState.COMMITTED);

            System.out.println("XA COMMIT: " + xid + " on " + resourceId +
                              (onePhase ? " (ONE PHASE)" : ""));

        } catch (SQLException e) {
            System.err.println("XA COMMIT失败: " + xid + ", " + e.getMessage());
            throw e;
        } finally {
            // 清理事务信息
            activeTransactions.remove(xid);
            returnConnection(conn);
        }
    }

    /**
     * 回滚XA事务
     */
    public void xaRollback(XATransactionId xid) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try {
            executeXACommand(conn, "XA ROLLBACK " + xid.toMySQLFormat());
            txInfo.setState(XATransactionState.ABORTED);

            System.out.println("XA ROLLBACK: " + xid + " on " + resourceId);

        } catch (SQLException e) {
            System.err.println("XA ROLLBACK失败: " + xid + ", " + e.getMessage());
            throw e;
        } finally {
            // 清理事务信息
            activeTransactions.remove(xid);
            returnConnection(conn);
        }
    }

    /**
     * 恢复XA事务
     */
    public List<XATransactionId> xaRecover() throws SQLException {
        Connection conn = getConnection();
        try {
            List<XATransactionId> xids = new ArrayList<>();

            try (Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("XA RECOVER")) {

                while (rs.next()) {
                    int formatId = rs.getInt("formatID");
                    String gtridLength = rs.getString("gtrid_length");
                    String bqualLength = rs.getString("bqual_length");
                    String data = rs.getString("data");

                    // 解析XID（简化实现）
                    XATransactionId xid = parseRecoveredXID(formatId, data);
                    if (xid != null) {
                        xids.add(xid);
                    }
                }
            }

            System.out.println("XA RECOVER: 找到 " + xids.size() + " 个待恢复事务");
            return xids;

        } catch (SQLException e) {
            System.err.println("XA RECOVER失败: " + e.getMessage());
            throw e;
        } finally {
            returnConnection(conn);
        }
    }

    /**
     * 执行SQL语句
     */
    public int executeUpdate(XATransactionId xid, String sql, Object... params) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        if (txInfo.getState() != XATransactionState.ACTIVE) {
            throw new SQLException("XA事务状态错误: " + txInfo.getState());
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // 设置参数
            for (int i = 0; i < params.length; i++) {
                pstmt.setObject(i + 1, params[i]);
            }

            int result = pstmt.executeUpdate();
            txInfo.touch();

            System.out.println("执行SQL: " + sql + " 在事务 " + xid + "，影响行数: " + result);
            return result;

        } catch (SQLException e) {
            System.err.println("执行SQL失败: " + sql + ", " + e.getMessage());
            throw e;
        }
    }

    /**
     * 执行查询
     */
    public <T> T executeQuery(XATransactionId xid, String sql, ResultSetExtractor<T> extractor,
                             Object... params) throws SQLException {
        XATransactionInfo txInfo = activeTransactions.get(xid);
        if (txInfo == null) {
            throw new SQLException("XA事务不存在: " + xid);
        }

        Connection conn = txInfo.getAttribute("connection", Connection.class);
        if (conn == null) {
            throw new SQLException("XA事务连接丢失: " + xid);
        }

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // 设置参数
            for (int i = 0; i < params.length; i++) {
                pstmt.setObject(i + 1, params[i]);
            }

            try (ResultSet rs = pstmt.executeQuery()) {
                T result = extractor.extract(rs);
                txInfo.touch();
                return result;
            }

        } catch (SQLException e) {
            System.err.println("执行查询失败: " + sql + ", " + e.getMessage());
            throw e;
        }
    }

    /**
     * 执行XA命令
     */
    private void executeXACommand(Connection conn, String command) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute(command);
        }
    }

    /**
     * 解析恢复的XID
     */
    private XATransactionId parseRecoveredXID(int formatId, String data) {
        try {
            // 简化的XID解析逻辑
            String[] parts = data.split(",");
            if (parts.length >= 2) {
                return new XATransactionId(parts[0], parts[1], formatId);
            }
        } catch (Exception e) {
            System.err.println("解析XID失败: " + data + ", " + e.getMessage());
        }
        return null;
    }

    /**
     * 获取活跃事务信息
     */
    public List<XATransactionInfo> getActiveTransactions() {
        return new ArrayList<>(activeTransactions.values());
    }

    /**
     * 关闭资源管理器
     */
    public void shutdown() {
        // 回滚所有活跃事务
        for (XATransactionId xid : new ArrayList<>(activeTransactions.keySet())) {
            try {
                xaRollback(xid);
            } catch (SQLException e) {
                System.err.println("关闭时回滚事务失败: " + xid + ", " + e.getMessage());
            }
        }

        // 关闭连接池
        Connection conn;
        while ((conn = connectionPool.poll()) != null) {
            try {
                conn.close();
            } catch (SQLException e) {
                System.err.println("关闭连接失败: " + e.getMessage());
            }
        }

        System.out.println("MySQL XA资源管理器已关闭: " + resourceId);
    }

    public String getResourceId() {
        return resourceId;
    }
}

/**
 * XA准备结果
 */
enum XAPrepareResult {
    OK,         // 准备成功
    ROLLBACK,   // 需要回滚
    READONLY    // 只读事务
}

/**
 * 结果集提取器
 */
@FunctionalInterface
interface ResultSetExtractor<T> {
    T extract(ResultSet rs) throws SQLException;
}
```

## 4. XA事务管理器实现

### 4.1 分布式事务管理器

```java
import java.util.concurrent.atomic.AtomicLong;

/**
 * XA分布式事务管理器
 */
public class XATransactionManager {
    private final String nodeId;
    private final AtomicLong transactionCounter = new AtomicLong(0);
    private final Map<XATransactionId, GlobalTransaction> globalTransactions = new ConcurrentHashMap<>();
    private final Map<String, MySQLXAResourceManager> resourceManagers = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // 配置参数
    private final long transactionTimeout = 300000; // 5分钟
    private final long recoveryInterval = 60000;    // 1分钟

    public XATransactionManager(String nodeId) {
        this.nodeId = nodeId;

        // 启动定时任务
        scheduler.scheduleAtFixedRate(this::timeoutCheck, 30, 30, TimeUnit.SECONDS);
        scheduler.scheduleAtFixedRate(this::recoveryCheck, recoveryInterval, recoveryInterval, TimeUnit.MILLISECONDS);
    }

    /**
     * 注册资源管理器
     */
    public void registerResourceManager(MySQLXAResourceManager rm) throws SQLException {
        rm.initialize();
        resourceManagers.put(rm.getResourceId(), rm);
        System.out.println("注册资源管理器: " + rm.getResourceId());
    }

    /**
     * 开始全局事务
     */
    public XATransactionId beginGlobalTransaction() {
        XATransactionId xid = XATransactionId.generate(nodeId);
        GlobalTransaction globalTx = new GlobalTransaction(xid, resourceManagers.keySet());
        globalTransactions.put(xid, globalTx);

        System.out.println("开始全局事务: " + xid);
        return xid;
    }

    /**
     * 在指定资源上开始分支事务
     */
    public void startBranch(XATransactionId xid, String resourceId) throws SQLException {
        GlobalTransaction globalTx = globalTransactions.get(xid);
        if (globalTx == null) {
            throw new SQLException("全局事务不存在: " + xid);
        }

        MySQLXAResourceManager rm = resourceManagers.get(resourceId);
        if (rm == null) {
            throw new SQLException("资源管理器不存在: " + resourceId);
        }

        // 创建分支事务ID
        XATransactionId branchXid = new XATransactionId(
            xid.getGlobalTransactionId(),
            resourceId + "-" + System.nanoTime(),
            xid.getFormatId()
        );

        rm.xaStart(branchXid);
        globalTx.addBranch(resourceId, branchXid);

        System.out.println("开始分支事务: " + branchXid + " on " + resourceId);
    }

    /**
     * 在指定资源上执行SQL
     */
    public int executeUpdate(XATransactionId globalXid, String resourceId, String sql, Object... params)
            throws SQLException {
        GlobalTransaction globalTx = globalTransactions.get(globalXid);
        if (globalTx == null) {
            throw new SQLException("全局事务不存在: " + globalXid);
        }

        XATransactionId branchXid = globalTx.getBranchXid(resourceId);
        if (branchXid == null) {
            throw new SQLException("分支事务不存在: " + resourceId);
        }

        MySQLXAResourceManager rm = resourceManagers.get(resourceId);
        if (rm == null) {
            throw new SQLException("资源管理器不存在: " + resourceId);
        }

        return rm.executeUpdate(branchXid, sql, params);
    }

    /**
     * 在指定资源上执行查询
     */
    public <T> T executeQuery(XATransactionId globalXid, String resourceId, String sql,
                             ResultSetExtractor<T> extractor, Object... params) throws SQLException {
        GlobalTransaction globalTx = globalTransactions.get(globalXid);
        if (globalTx == null) {
            throw new SQLException("全局事务不存在: " + globalXid);
        }

        XATransactionId branchXid = globalTx.getBranchXid(resourceId);
        if (branchXid == null) {
            throw new SQLException("分支事务不存在: " + resourceId);
        }

        MySQLXAResourceManager rm = resourceManagers.get(resourceId);
        if (rm == null) {
            throw new SQLException("资源管理器不存在: " + resourceId);
        }

        return rm.executeQuery(branchXid, sql, extractor, params);
    }

    /**
     * 提交全局事务
     */
    public void commitGlobalTransaction(XATransactionId xid) throws SQLException {
        GlobalTransaction globalTx = globalTransactions.get(xid);
        if (globalTx == null) {
            throw new SQLException("全局事务不存在: " + xid);
        }

        try {
            globalTx.setState(GlobalTransactionState.COMMITTING);

            // 如果只有一个分支，使用一阶段提交
            if (globalTx.getBranches().size() == 1) {
                commitOnePhase(globalTx);
            } else {
                commitTwoPhase(globalTx);
            }

            globalTx.setState(GlobalTransactionState.COMMITTED);
            System.out.println("全局事务提交成功: " + xid);

        } catch (SQLException e) {
            globalTx.setState(GlobalTransactionState.FAILED);
            System.err.println("全局事务提交失败: " + xid + ", " + e.getMessage());
            throw e;
        } finally {
            globalTransactions.remove(xid);
        }
    }

    /**
     * 回滚全局事务
     */
    public void rollbackGlobalTransaction(XATransactionId xid) throws SQLException {
        GlobalTransaction globalTx = globalTransactions.get(xid);
        if (globalTx == null) {
            throw new SQLException("全局事务不存在: " + xid);
        }

        try {
            globalTx.setState(GlobalTransactionState.ROLLING_BACK);

            List<SQLException> exceptions = new ArrayList<>();

            // 并行回滚所有分支
            List<CompletableFuture<Void>> futures = new ArrayList<>();

            for (Map.Entry<String, XATransactionId> entry : globalTx.getBranches().entrySet()) {
                String resourceId = entry.getKey();
                XATransactionId branchXid = entry.getValue();

                CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                    try {
                        MySQLXAResourceManager rm = resourceManagers.get(resourceId);
                        if (rm != null) {
                            rm.xaEnd(branchXid);
                            rm.xaRollback(branchXid);
                        }
                    } catch (SQLException e) {
                        synchronized (exceptions) {
                            exceptions.add(e);
                        }
                    }
                }, executor);

                futures.add(future);
            }

            // 等待所有回滚完成
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                    .get(30, TimeUnit.SECONDS);

            if (!exceptions.isEmpty()) {
                SQLException combined = new SQLException("部分分支回滚失败");
                for (SQLException e : exceptions) {
                    combined.addSuppressed(e);
                }
                throw combined;
            }

            globalTx.setState(GlobalTransactionState.ABORTED);
            System.out.println("全局事务回滚成功: " + xid);

        } catch (Exception e) {
            globalTx.setState(GlobalTransactionState.FAILED);
            System.err.println("全局事务回滚失败: " + xid + ", " + e.getMessage());
            if (e instanceof SQLException) {
                throw (SQLException) e;
            } else {
                throw new SQLException("回滚失败", e);
            }
        } finally {
            globalTransactions.remove(xid);
        }
    }

    /**
     * 一阶段提交
     */
    private void commitOnePhase(GlobalTransaction globalTx) throws SQLException {
        Map.Entry<String, XATransactionId> entry = globalTx.getBranches().entrySet().iterator().next();
        String resourceId = entry.getKey();
        XATransactionId branchXid = entry.getValue();

        MySQLXAResourceManager rm = resourceManagers.get(resourceId);
        if (rm == null) {
            throw new SQLException("资源管理器不存在: " + resourceId);
        }

        rm.xaEnd(branchXid);
        rm.xaCommit(branchXid, true); // 一阶段提交

        System.out.println("一阶段提交完成: " + globalTx.getXid());
    }

    /**
     * 两阶段提交
     */
    private void commitTwoPhase(GlobalTransaction globalTx) throws SQLException {
        // 第一阶段：准备
        List<SQLException> prepareExceptions = new ArrayList<>();
        List<CompletableFuture<XAPrepareResult>> prepareFutures = new ArrayList<>();

        for (Map.Entry<String, XATransactionId> entry : globalTx.getBranches().entrySet()) {
            String resourceId = entry.getKey();
            XATransactionId branchXid = entry.getValue();

            CompletableFuture<XAPrepareResult> future = CompletableFuture.supplyAsync(() -> {
                try {
                    MySQLXAResourceManager rm = resourceManagers.get(resourceId);
                    if (rm == null) {
                        throw new SQLException("资源管理器不存在: " + resourceId);
                    }

                    rm.xaEnd(branchXid);
                    return rm.xaPrepare(branchXid);

                } catch (SQLException e) {
                    synchronized (prepareExceptions) {
                        prepareExceptions.add(e);
                    }
                    return XAPrepareResult.ROLLBACK;
                }
            }, executor);

            prepareFutures.add(future);
        }

        // 等待所有准备完成
        try {
            List<XAPrepareResult> results = prepareFutures.stream()
                    .map(future -> {
                        try {
                            return future.get(30, TimeUnit.SECONDS);
                        } catch (Exception e) {
                            return XAPrepareResult.ROLLBACK;
                        }
                    })
                    .collect(Collectors.toList());

            // 检查准备结果
            boolean allOk = results.stream().allMatch(result -> result == XAPrepareResult.OK);

            if (!prepareExceptions.isEmpty() || !allOk) {
                // 准备阶段失败，回滚所有分支
                rollbackPreparedBranches(globalTx);

                SQLException combined = new SQLException("准备阶段失败");
                for (SQLException e : prepareExceptions) {
                    combined.addSuppressed(e);
                }
                throw combined;
            }

        } catch (Exception e) {
            rollbackPreparedBranches(globalTx);
            throw new SQLException("准备阶段异常", e);
        }

        // 第二阶段：提交
        List<SQLException> commitExceptions = new ArrayList<>();
        List<CompletableFuture<Void>> commitFutures = new ArrayList<>();

        for (Map.Entry<String, XATransactionId> entry : globalTx.getBranches().entrySet()) {
            String resourceId = entry.getKey();
            XATransactionId branchXid = entry.getValue();

            CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                try {
                    MySQLXAResourceManager rm = resourceManagers.get(resourceId);
                    if (rm != null) {
                        rm.xaCommit(branchXid, false);
                    }
                } catch (SQLException e) {
                    synchronized (commitExceptions) {
                        commitExceptions.add(e);
                    }
                }
            }, executor);

            commitFutures.add(future);
        }

        // 等待所有提交完成
        try {
            CompletableFuture.allOf(commitFutures.toArray(new CompletableFuture[0]))
                    .get(60, TimeUnit.SECONDS);
        } catch (Exception e) {
            System.err.println("等待提交完成异常: " + e.getMessage());
        }

        if (!commitExceptions.isEmpty()) {
            SQLException combined = new SQLException("部分分支提交失败");
            for (SQLException e : commitExceptions) {
                combined.addSuppressed(e);
            }
            throw combined;
        }

        System.out.println("两阶段提交完成: " + globalTx.getXid());
    }

    /**
     * 回滚已准备的分支
     */
    private void rollbackPreparedBranches(GlobalTransaction globalTx) {
        for (Map.Entry<String, XATransactionId> entry : globalTx.getBranches().entrySet()) {
            String resourceId = entry.getKey();
            XATransactionId branchXid = entry.getValue();

            try {
                MySQLXAResourceManager rm = resourceManagers.get(resourceId);
                if (rm != null) {
                    rm.xaRollback(branchXid);
                }
            } catch (SQLException e) {
                System.err.println("回滚已准备分支失败: " + branchXid + ", " + e.getMessage());
            }
        }
    }

    /**
     * 超时检查
     */
    private void timeoutCheck() {
        long currentTime = System.currentTimeMillis();
        List<XATransactionId> timeoutTransactions = new ArrayList<>();

        for (GlobalTransaction globalTx : globalTransactions.values()) {
            if (currentTime - globalTx.getCreateTime() > transactionTimeout) {
                timeoutTransactions.add(globalTx.getXid());
            }
        }

        for (XATransactionId xid : timeoutTransactions) {
            try {
                System.out.println("事务超时，自动回滚: " + xid);
                rollbackGlobalTransaction(xid);
            } catch (SQLException e) {
                System.err.println("超时回滚失败: " + xid + ", " + e.getMessage());
            }
        }
    }

    /**
     * 恢复检查
     */
    private void recoveryCheck() {
        for (MySQLXAResourceManager rm : resourceManagers.values()) {
            try {
                List<XATransactionId> recoveredXids = rm.xaRecover();
                for (XATransactionId xid : recoveredXids) {
                    // 简化的恢复逻辑：回滚所有恢复的事务
                    try {
                        rm.xaRollback(xid);
                        System.out.println("恢复时回滚事务: " + xid);
                    } catch (SQLException e) {
                        System.err.println("恢复回滚失败: " + xid + ", " + e.getMessage());
                    }
                }
            } catch (SQLException e) {
                System.err.println("恢复检查失败: " + rm.getResourceId() + ", " + e.getMessage());
            }
        }
    }

    /**
     * 获取全局事务统计信息
     */
    public XATransactionManagerStats getStats() {
        int activeCount = globalTransactions.size();
        Map<GlobalTransactionState, Long> stateCount = globalTransactions.values().stream()
                .collect(Collectors.groupingBy(GlobalTransaction::getState, Collectors.counting()));

        return new XATransactionManagerStats(
            nodeId,
            transactionCounter.get(),
            activeCount,
            resourceManagers.size(),
            stateCount
        );
    }

    /**
     * 关闭事务管理器
     */
    public void shutdown() {
        // 回滚所有活跃事务
        for (XATransactionId xid : new ArrayList<>(globalTransactions.keySet())) {
            try {
                rollbackGlobalTransaction(xid);
            } catch (SQLException e) {
                System.err.println("关闭时回滚事务失败: " + xid + ", " + e.getMessage());
            }
        }

        // 关闭资源管理器
        for (MySQLXAResourceManager rm : resourceManagers.values()) {
            rm.shutdown();
        }

        // 关闭线程池
        scheduler.shutdown();
        executor.shutdown();

        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }

        System.out.println("XA事务管理器已关闭: " + nodeId);
    }
}

/**
 * 全局事务状态
 */
enum GlobalTransactionState {
    ACTIVE,         // 活跃
    COMMITTING,     // 提交中
    COMMITTED,      // 已提交
    ROLLING_BACK,   // 回滚中
    ABORTED,        // 已中止
    FAILED          // 失败
}

/**
 * 全局事务
 */
class GlobalTransaction {
    private final XATransactionId xid;
    private volatile GlobalTransactionState state;
    private final long createTime;
    private final Map<String, XATransactionId> branches = new ConcurrentHashMap<>();

    public GlobalTransaction(XATransactionId xid, Set<String> resourceIds) {
        this.xid = xid;
        this.state = GlobalTransactionState.ACTIVE;
        this.createTime = System.currentTimeMillis();
    }

    public void addBranch(String resourceId, XATransactionId branchXid) {
        branches.put(resourceId, branchXid);
    }

    public XATransactionId getBranchXid(String resourceId) {
        return branches.get(resourceId);
    }

    public Map<String, XATransactionId> getBranches() {
        return new HashMap<>(branches);
    }

    // Getters and Setters
    public XATransactionId getXid() { return xid; }
    public GlobalTransactionState getState() { return state; }
    public void setState(GlobalTransactionState state) { this.state = state; }
    public long getCreateTime() { return createTime; }
}

/**
 * 事务管理器统计信息
 */
class XATransactionManagerStats {
    private final String nodeId;
    private final long totalTransactions;
    private final int activeTransactions;
    private final int resourceManagers;
    private final Map<GlobalTransactionState, Long> stateDistribution;

    public XATransactionManagerStats(String nodeId, long totalTransactions, int activeTransactions,
                                   int resourceManagers, Map<GlobalTransactionState, Long> stateDistribution) {
        this.nodeId = nodeId;
        this.totalTransactions = totalTransactions;
        this.activeTransactions = activeTransactions;
        this.resourceManagers = resourceManagers;
        this.stateDistribution = new HashMap<>(stateDistribution);
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public long getTotalTransactions() { return totalTransactions; }
    public int getActiveTransactions() { return activeTransactions; }
    public int getResourceManagers() { return resourceManagers; }
    public Map<GlobalTransactionState, Long> getStateDistribution() { return new HashMap<>(stateDistribution); }

    @Override
    public String toString() {
        return String.format("XATransactionManagerStats{nodeId='%s', total=%d, active=%d, resources=%d, states=%s}",
                nodeId, totalTransactions, activeTransactions, resourceManagers, stateDistribution);
    }
}
```

## 5. XA事务应用层封装

### 5.1 注解驱动的事务管理

```java
import java.lang.annotation.*;

/**
 * XA事务注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface XATransactional {
    /**
     * 事务超时时间（毫秒）
     */
    long timeout() default 300000;

    /**
     * 发生异常时是否回滚
     */
    Class<? extends Throwable>[] rollbackFor() default {Exception.class};

    /**
     * 不回滚的异常
     */
    Class<? extends Throwable>[] noRollbackFor() default {};

    /**
     * 事务传播行为
     */
    XAPropagation propagation() default XAPropagation.REQUIRED;
}

/**
 * XA事务传播行为
 */
enum XAPropagation {
    REQUIRED,       // 需要事务，如果当前没有事务则创建新事务
    REQUIRES_NEW,   // 总是创建新事务
    SUPPORTS,       // 支持事务，如果当前有事务则加入
    NOT_SUPPORTED,  // 不支持事务
    NEVER,          // 从不使用事务
    MANDATORY       // 强制要求事务，如果当前没有事务则抛出异常
}

/**
 * XA事务上下文
 */
public class XATransactionContext {
    private static final ThreadLocal<XATransactionId> CURRENT_TRANSACTION = new ThreadLocal<>();
    private static final ThreadLocal<XATransactionManager> CURRENT_MANAGER = new ThreadLocal<>();

    public static void setCurrentTransaction(XATransactionId xid, XATransactionManager manager) {
        CURRENT_TRANSACTION.set(xid);
        CURRENT_MANAGER.set(manager);
    }

    public static XATransactionId getCurrentTransaction() {
        return CURRENT_TRANSACTION.get();
    }

    public static XATransactionManager getCurrentManager() {
        return CURRENT_MANAGER.get();
    }

    public static boolean hasActiveTransaction() {
        return CURRENT_TRANSACTION.get() != null;
    }

    public static void clear() {
        CURRENT_TRANSACTION.remove();
        CURRENT_MANAGER.remove();
    }
}

/**
 * XA事务拦截器
 */
public class XATransactionInterceptor {
    private final XATransactionManager transactionManager;

    public XATransactionInterceptor(XATransactionManager transactionManager) {
        this.transactionManager = transactionManager;
    }

    /**
     * 拦截带有@XATransactional注解的方法
     */
    public Object intercept(Method method, Object[] args, Callable<?> proceed) throws Exception {
        XATransactional annotation = method.getAnnotation(XATransactional.class);
        if (annotation == null) {
            return proceed.call();
        }

        XAPropagation propagation = annotation.propagation();
        XATransactionId currentXid = XATransactionContext.getCurrentTransaction();

        switch (propagation) {
            case REQUIRED:
                if (currentXid != null) {
                    // 加入当前事务
                    return proceed.call();
                } else {
                    // 创建新事务
                    return executeInNewTransaction(annotation, proceed);
                }

            case REQUIRES_NEW:
                // 总是创建新事务
                return executeInNewTransaction(annotation, proceed);

            case SUPPORTS:
                // 支持当前事务
                return proceed.call();

            case NOT_SUPPORTED:
                // 暂停当前事务
                return executeWithoutTransaction(proceed);

            case NEVER:
                if (currentXid != null) {
                    throw new IllegalStateException("当前存在事务，但方法配置为NEVER");
                }
                return proceed.call();

            case MANDATORY:
                if (currentXid == null) {
                    throw new IllegalStateException("当前没有事务，但方法配置为MANDATORY");
                }
                return proceed.call();

            default:
                return proceed.call();
        }
    }

    /**
     * 在新事务中执行
     */
    private Object executeInNewTransaction(XATransactional annotation, Callable<?> proceed) throws Exception {
        XATransactionId xid = transactionManager.beginGlobalTransaction();
        XATransactionContext.setCurrentTransaction(xid, transactionManager);

        try {
            Object result = proceed.call();
            transactionManager.commitGlobalTransaction(xid);
            return result;

        } catch (Exception e) {
            if (shouldRollback(e, annotation)) {
                transactionManager.rollbackGlobalTransaction(xid);
            } else {
                transactionManager.commitGlobalTransaction(xid);
            }
            throw e;

        } finally {
            XATransactionContext.clear();
        }
    }

    /**
     * 不使用事务执行
     */
    private Object executeWithoutTransaction(Callable<?> proceed) throws Exception {
        XATransactionId suspendedXid = XATransactionContext.getCurrentTransaction();
        XATransactionManager suspendedManager = XATransactionContext.getCurrentManager();

        try {
            XATransactionContext.clear();
            return proceed.call();
        } finally {
            if (suspendedXid != null) {
                XATransactionContext.setCurrentTransaction(suspendedXid, suspendedManager);
            }
        }
    }

    /**
     * 判断是否应该回滚
     */
    private boolean shouldRollback(Exception e, XATransactional annotation) {
        Class<? extends Throwable>[] rollbackFor = annotation.rollbackFor();
        Class<? extends Throwable>[] noRollbackFor = annotation.noRollbackFor();

        // 检查不回滚的异常
        for (Class<? extends Throwable> clazz : noRollbackFor) {
            if (clazz.isAssignableFrom(e.getClass())) {
                return false;
            }
        }

        // 检查回滚的异常
        for (Class<? extends Throwable> clazz : rollbackFor) {
            if (clazz.isAssignableFrom(e.getClass())) {
                return true;
            }
        }

        return false;
    }
}
```

### 5.2 XA数据访问对象

```java
/**
 * XA数据访问对象基类
 */
public abstract class XABaseDAO {
    protected final XATransactionManager transactionManager;
    protected final String resourceId;

    public XABaseDAO(XATransactionManager transactionManager, String resourceId) {
        this.transactionManager = transactionManager;
        this.resourceId = resourceId;
    }

    /**
     * 执行更新操作
     */
    protected int executeUpdate(String sql, Object... params) throws SQLException {
        XATransactionId xid = XATransactionContext.getCurrentTransaction();
        if (xid == null) {
            throw new SQLException("当前没有活跃的XA事务");
        }

        return transactionManager.executeUpdate(xid, resourceId, sql, params);
    }

    /**
     * 执行查询操作
     */
    protected <T> T executeQuery(String sql, ResultSetExtractor<T> extractor, Object... params) throws SQLException {
        XATransactionId xid = XATransactionContext.getCurrentTransaction();
        if (xid == null) {
            throw new SQLException("当前没有活跃的XA事务");
        }

        return transactionManager.executeQuery(xid, resourceId, sql, extractor, params);
    }

    /**
     * 查询单个对象
     */
    protected <T> T queryForObject(String sql, RowMapper<T> rowMapper, Object... params) throws SQLException {
        return executeQuery(sql, rs -> {
            if (rs.next()) {
                return rowMapper.mapRow(rs, 1);
            }
            return null;
        }, params);
    }

    /**
     * 查询对象列表
     */
    protected <T> List<T> queryForList(String sql, RowMapper<T> rowMapper, Object... params) throws SQLException {
        return executeQuery(sql, rs -> {
            List<T> list = new ArrayList<>();
            int rowNum = 1;
            while (rs.next()) {
                list.add(rowMapper.mapRow(rs, rowNum++));
            }
            return list;
        }, params);
    }

    /**
     * 查询计数
     */
    protected long queryForCount(String sql, Object... params) throws SQLException {
        return executeQuery(sql, rs -> {
            if (rs.next()) {
                return rs.getLong(1);
            }
            return 0L;
        }, params);
    }

    /**
     * 确保分支事务已启动
     */
    protected void ensureBranchStarted() throws SQLException {
        XATransactionId xid = XATransactionContext.getCurrentTransaction();
        if (xid != null) {
            transactionManager.startBranch(xid, resourceId);
        }
    }
}

/**
 * 行映射器接口
 */
@FunctionalInterface
interface RowMapper<T> {
    T mapRow(ResultSet rs, int rowNum) throws SQLException;
}

/**
 * 用户DAO示例
 */
public class UserXADAO extends XABaseDAO {
    public UserXADAO(XATransactionManager transactionManager, String resourceId) {
        super(transactionManager, resourceId);
    }

    public void createUser(User user) throws SQLException {
        ensureBranchStarted();

        String sql = "INSERT INTO users (id, username, email, created_at) VALUES (?, ?, ?, ?)";
        executeUpdate(sql, user.getId(), user.getUsername(), user.getEmail(), user.getCreatedAt());
    }

    public User findById(Long id) throws SQLException {
        String sql = "SELECT id, username, email, created_at FROM users WHERE id = ?";
        return queryForObject(sql, this::mapUser, id);
    }

    public List<User> findByUsername(String username) throws SQLException {
        String sql = "SELECT id, username, email, created_at FROM users WHERE username LIKE ?";
        return queryForList(sql, this::mapUser, "%" + username + "%");
    }

    public void updateUser(User user) throws SQLException {
        ensureBranchStarted();

        String sql = "UPDATE users SET username = ?, email = ? WHERE id = ?";
        executeUpdate(sql, user.getUsername(), user.getEmail(), user.getId());
    }

    public void deleteUser(Long id) throws SQLException {
        ensureBranchStarted();

        String sql = "DELETE FROM users WHERE id = ?";
        executeUpdate(sql, id);
    }

    public long countUsers() throws SQLException {
        String sql = "SELECT COUNT(*) FROM users";
        return queryForCount(sql);
    }

    private User mapUser(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(rs.getLong("id"));
        user.setUsername(rs.getString("username"));
        user.setEmail(rs.getString("email"));
        user.setCreatedAt(rs.getTimestamp("created_at"));
        return user;
    }
}

/**
 * 订单DAO示例
 */
public class OrderXADAO extends XABaseDAO {
    public OrderXADAO(XATransactionManager transactionManager, String resourceId) {
        super(transactionManager, resourceId);
    }

    public void createOrder(Order order) throws SQLException {
        ensureBranchStarted();

        String sql = "INSERT INTO orders (id, user_id, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?)";
        executeUpdate(sql, order.getId(), order.getUserId(), order.getTotalAmount(),
                     order.getStatus(), order.getCreatedAt());
    }

    public Order findById(Long id) throws SQLException {
        String sql = "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = ?";
        return queryForObject(sql, this::mapOrder, id);
    }

    public List<Order> findByUserId(Long userId) throws SQLException {
        String sql = "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE user_id = ?";
        return queryForList(sql, this::mapOrder, userId);
    }

    public void updateOrderStatus(Long id, String status) throws SQLException {
        ensureBranchStarted();

        String sql = "UPDATE orders SET status = ? WHERE id = ?";
        executeUpdate(sql, status, id);
    }

    private Order mapOrder(ResultSet rs, int rowNum) throws SQLException {
        Order order = new Order();
        order.setId(rs.getLong("id"));
        order.setUserId(rs.getLong("user_id"));
        order.setTotalAmount(rs.getBigDecimal("total_amount"));
        order.setStatus(rs.getString("status"));
        order.setCreatedAt(rs.getTimestamp("created_at"));
        return order;
    }
}

/**
 * 用户实体
 */
class User {
    private Long id;
    private String username;
    private String email;
    private Timestamp createdAt;

    // Constructors, getters and setters
    public User() {}

    public User(Long id, String username, String email) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.createdAt = new Timestamp(System.currentTimeMillis());
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return String.format("User{id=%d, username='%s', email='%s'}", id, username, email);
    }
}

/**
 * 订单实体
 */
class Order {
    private Long id;
    private Long userId;
    private BigDecimal totalAmount;
    private String status;
    private Timestamp createdAt;

    // Constructors, getters and setters
    public Order() {}

    public Order(Long id, Long userId, BigDecimal totalAmount, String status) {
        this.id = id;
        this.userId = userId;
        this.totalAmount = totalAmount;
        this.status = status;
        this.createdAt = new Timestamp(System.currentTimeMillis());
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return String.format("Order{id=%d, userId=%d, amount=%s, status='%s'}",
                           id, userId, totalAmount, status);
    }
}
```

## 6. 完整测试示例

### 6.1 XA事务测试

```java
import java.math.BigDecimal;

/**
 * MySQL XA事务综合测试
 */
public class MySQLXATransactionTest {

    public static void main(String[] args) throws Exception {
        testXATransaction();
    }

    /**
     * 测试XA事务
     */
    private static void testXATransaction() throws Exception {
        System.out.println("=== MySQL XA事务测试开始 ===\n");

        // 创建事务管理器
        XATransactionManager txManager = new XATransactionManager("test-node");

        try {
            // 注册资源管理器
            setupResourceManagers(txManager);

            // 创建DAO
            UserXADAO userDAO1 = new UserXADAO(txManager, "db1");
            UserXADAO userDAO2 = new UserXADAO(txManager, "db2");
            OrderXADAO orderDAO1 = new OrderXADAO(txManager, "db1");
            OrderXADAO orderDAO2 = new OrderXADAO(txManager, "db2");

            // 测试成功的分布式事务
            testSuccessfulTransaction(txManager, userDAO1, userDAO2, orderDAO1, orderDAO2);

            // 测试失败的分布式事务（回滚）
            testFailedTransaction(txManager, userDAO1, userDAO2, orderDAO1, orderDAO2);

            // 测试并发事务
            testConcurrentTransactions(txManager, userDAO1, orderDAO1);

            // 性能测试
            performanceTest(txManager, userDAO1, orderDAO1);

        } finally {
            txManager.shutdown();
        }

        System.out.println("\n=== MySQL XA事务测试完成 ===");
    }

    /**
     * 设置资源管理器
     */
    private static void setupResourceManagers(XATransactionManager txManager) throws SQLException {
        // 数据库连接配置
        String db1Url = "jdbc:mysql://localhost:3306/test_db1?useSSL=false&allowPublicKeyRetrieval=true";
        String db2Url = "jdbc:mysql://localhost:3306/test_db2?useSSL=false&allowPublicKeyRetrieval=true";
        String username = "test_user";
        String password = "test_password";

        // 创建资源管理器
        MySQLXAResourceManager rm1 = new MySQLXAResourceManager("db1", db1Url, username, password);
        MySQLXAResourceManager rm2 = new MySQLXAResourceManager("db2", db2Url, username, password);

        // 注册资源管理器
        txManager.registerResourceManager(rm1);
        txManager.registerResourceManager(rm2);

        System.out.println("资源管理器注册完成\n");
    }

    /**
     * 测试成功的分布式事务
     */
    private static void testSuccessfulTransaction(XATransactionManager txManager,
                                                UserXADAO userDAO1, UserXADAO userDAO2,
                                                OrderXADAO orderDAO1, OrderXADAO orderDAO2) throws Exception {
        System.out.println("=== 测试成功的分布式事务 ===");

        XATransactionId xid = txManager.beginGlobalTransaction();
        XATransactionContext.setCurrentTransaction(xid, txManager);

        try {
            // 在两个数据库中创建用户
            User user1 = new User(1L, "alice", "alice@example.com");
            User user2 = new User(2L, "bob", "bob@example.com");

            userDAO1.createUser(user1);
            userDAO2.createUser(user2);

            // 在两个数据库中创建订单
            Order order1 = new Order(1L, 1L, new BigDecimal("100.00"), "PENDING");
            Order order2 = new Order(2L, 2L, new BigDecimal("200.00"), "PENDING");

            orderDAO1.createOrder(order1);
            orderDAO2.createOrder(order2);

            // 提交事务
            txManager.commitGlobalTransaction(xid);
            System.out.println("分布式事务提交成功");

            // 验证数据
            verifyData(userDAO1, userDAO2, orderDAO1, orderDAO2);

        } catch (Exception e) {
            txManager.rollbackGlobalTransaction(xid);
            throw e;
        } finally {
            XATransactionContext.clear();
        }

        System.out.println("=== 成功事务测试完成 ===\n");
    }

    /**
     * 测试失败的分布式事务
     */
    private static void testFailedTransaction(XATransactionManager txManager,
                                            UserXADAO userDAO1, UserXADAO userDAO2,
                                            OrderXADAO orderDAO1, OrderXADAO orderDAO2) throws Exception {
        System.out.println("=== 测试失败的分布式事务 ===");

        XATransactionId xid = txManager.beginGlobalTransaction();
        XATransactionContext.setCurrentTransaction(xid, txManager);

        try {
            // 在两个数据库中创建用户
            User user3 = new User(3L, "charlie", "charlie@example.com");
            User user4 = new User(4L, "david", "david@example.com");

            userDAO1.createUser(user3);
            userDAO2.createUser(user4);

            // 故意创建一个会失败的操作（重复ID）
            User duplicateUser = new User(3L, "duplicate", "duplicate@example.com");
            userDAO1.createUser(duplicateUser); // 这应该失败

            txManager.commitGlobalTransaction(xid);

        } catch (Exception e) {
            System.out.println("检测到异常，回滚事务: " + e.getMessage());
            txManager.rollbackGlobalTransaction(xid);

            // 验证数据未被提交
            User user3Check = userDAO1.findById(3L);
            User user4Check = userDAO2.findById(4L);

            if (user3Check == null && user4Check == null) {
                System.out.println("回滚验证成功：数据未被提交");
            } else {
                System.err.println("回滚验证失败：数据已被提交");
            }

        } finally {
            XATransactionContext.clear();
        }

        System.out.println("=== 失败事务测试完成 ===\n");
    }

    /**
     * 测试并发事务
     */
    private static void testConcurrentTransactions(XATransactionManager txManager,
                                                 UserXADAO userDAO, OrderXADAO orderDAO) throws Exception {
        System.out.println("=== 测试并发事务 ===");

        int concurrentCount = 5;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentCount);
        CountDownLatch latch = new CountDownLatch(concurrentCount);
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failureCount = new AtomicInteger(0);

        for (int i = 0; i < concurrentCount; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    XATransactionId xid = txManager.beginGlobalTransaction();
                    XATransactionContext.setCurrentTransaction(xid, txManager);

                    try {
                        // 创建用户和订单
                        User user = new User((long) (100 + threadId),
                                           "user" + threadId,
                                           "user" + threadId + "@example.com");
                        Order order = new Order((long) (100 + threadId),
                                              user.getId(),
                                              new BigDecimal("50.00"),
                                              "PENDING");

                        userDAO.createUser(user);
                        orderDAO.createOrder(order);

                        // 模拟一些处理时间
                        Thread.sleep(100);

                        txManager.commitGlobalTransaction(xid);
                        successCount.incrementAndGet();

                        System.out.println("并发事务 " + threadId + " 成功");

                    } catch (Exception e) {
                        txManager.rollbackGlobalTransaction(xid);
                        failureCount.incrementAndGet();
                        System.err.println("并发事务 " + threadId + " 失败: " + e.getMessage());
                    } finally {
                        XATransactionContext.clear();
                    }

                } catch (Exception e) {
                    failureCount.incrementAndGet();
                    System.err.println("并发事务 " + threadId + " 异常: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();

        System.out.println("并发事务结果 - 成功: " + successCount.get() + ", 失败: " + failureCount.get());
        System.out.println("=== 并发事务测试完成 ===\n");
    }

    /**
     * 性能测试
     */
    private static void performanceTest(XATransactionManager txManager,
                                      UserXADAO userDAO, OrderXADAO orderDAO) throws Exception {
        System.out.println("=== 性能测试 ===");

        int testCount = 100;
        long startTime = System.currentTimeMillis();

        for (int i = 0; i < testCount; i++) {
            XATransactionId xid = txManager.beginGlobalTransaction();
            XATransactionContext.setCurrentTransaction(xid, txManager);

            try {
                User user = new User((long) (200 + i),
                                   "perfuser" + i,
                                   "perfuser" + i + "@example.com");
                Order order = new Order((long) (200 + i),
                                      user.getId(),
                                      new BigDecimal("25.00"),
                                      "COMPLETED");

                userDAO.createUser(user);
                orderDAO.createOrder(order);

                txManager.commitGlobalTransaction(xid);

            } catch (Exception e) {
                txManager.rollbackGlobalTransaction(xid);
                throw e;
            } finally {
                XATransactionContext.clear();
            }
        }

        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;

        System.out.println("性能测试结果:");
        System.out.println("事务数量: " + testCount);
        System.out.println("总耗时: " + duration + "ms");
        System.out.println("平均耗时: " + (duration / (double) testCount) + "ms/事务");
        System.out.println("吞吐量: " + (testCount * 1000.0 / duration) + " 事务/秒");

        System.out.println("=== 性能测试完成 ===\n");
    }

    /**
     * 验证数据
     */
    private static void verifyData(UserXADAO userDAO1, UserXADAO userDAO2,
                                 OrderXADAO orderDAO1, OrderXADAO orderDAO2) throws SQLException {
        System.out.println("验证提交的数据:");

        User user1 = userDAO1.findById(1L);
        User user2 = userDAO2.findById(2L);
        Order order1 = orderDAO1.findById(1L);
        Order order2 = orderDAO2.findById(2L);

        System.out.println("DB1 - " + user1);
        System.out.println("DB2 - " + user2);
        System.out.println("DB1 - " + order1);
        System.out.println("DB2 - " + order2);
    }

    /**
     * 注解驱动事务测试
     */
    @XATransactional
    public void annotationDrivenTransactionTest(XATransactionManager txManager) throws SQLException {
        UserXADAO userDAO1 = new UserXADAO(txManager, "db1");
        UserXADAO userDAO2 = new UserXADAO(txManager, "db2");

        // 这个方法会自动被XA事务包装
        User user = new User(999L, "annotation_user", "annotation@example.com");
        userDAO1.createUser(user);
        userDAO2.createUser(user);

        // 如果发生异常，事务会自动回滚
        if (user.getUsername().contains("test")) {
            throw new RuntimeException("测试异常回滚");
        }
    }
}
```

## 7. 总结

MySQL XA分布式事务是实现跨多个数据库ACID特性的重要技术，具有以下特点：

### 7.1 核心优势
- **强一致性**：保证分布式环境下的ACID特性
- **标准化**：基于X/Open XA标准，具有良好的兼容性
- **可靠性**：通过两阶段提交协议确保事务原子性
- **透明性**：对应用层相对透明，易于集成

### 7.2 关键机制
- **两阶段提交**：准备阶段和提交阶段确保原子性
- **XID管理**：全局事务标识符管理分支事务
- **资源管理器**：封装数据库操作和XA协议
- **事务管理器**：协调全局事务的生命周期

### 7.3 应用场景
- **分布式订单系统**：跨多个数据库的订单处理
- **金融转账**：确保账户间转账的原子性
- **库存管理**：跨多个仓库的库存扣减
- **数据同步**：多数据源间的数据一致性

### 7.4 性能考虑
- **网络开销**：两阶段提交增加网络通信
- **锁时间延长**：事务持续时间较长，影响并发
- **单点故障**：事务管理器的可用性影响全局
- **恢复复杂性**：故障恢复机制相对复杂

### 7.5 最佳实践
- **事务范围最小化**：减少分布式事务的使用范围
- **超时设置**：合理设置事务超时时间
- **监控告警**：监控事务状态和性能指标
- **故障恢复**：完善的故障检测和恢复机制

### 7.6 替代方案
- **Saga模式**：长时间运行的业务流程
- **最终一致性**：通过消息队列实现异步一致性
- **分布式锁**：通过锁机制保证操作原子性
- **事件驱动**：基于事件的最终一致性

通过本文的详细实现，你可以深入理解MySQL XA分布式事务的工作原理和实现细节，为构建高可靠的分布式系统提供坚实的技术基础。