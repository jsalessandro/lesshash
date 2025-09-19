---
title: "分布式系统核心模式详解：TCC原子性执行原理与Java实现"
date: 2024-12-19T15:00:00+08:00
draft: false
tags: ["分布式系统", "TCC模式", "分布式事务", "最终一致性", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入解析TCC分布式事务模式的原理、三阶段协议以及在微服务架构中的应用实践，包含完整的Java实现代码"
---

## 1. TCC模式概述

TCC（Try-Confirm-Cancel）是一种分布式事务处理模式，通过业务层面的补偿机制来实现分布式事务的一致性。TCC模式将事务分为三个阶段：Try（尝试）、Confirm（确认）、Cancel（取消），每个参与方都需要实现这三个操作。

### 1.1 核心思想

```
TCC三阶段：
Try阶段    - 预留资源，检查业务规则
Confirm阶段 - 确认执行，完成业务操作
Cancel阶段  - 取消预留，释放资源
```

### 1.2 与XA事务的区别

```
XA事务特点：
- 基于数据库层面的两阶段提交
- 长时间持有数据库锁
- 强一致性但性能较差

TCC模式特点：
- 基于业务层面的补偿操作
- 无长时间锁定，提高并发性
- 最终一致性，性能更好
```

## 2. TCC模式原理

### 2.1 三阶段协议流程

#### 序列图

| 步骤 | 参与者 | 动作 | 目标 | 说明 |
|------|--------|------|------|------|
| 1 | TM | 发送 | PA | Try |
| 2 | PA | 发送 | TM | Try成功 |
| 3 | TM | 发送 | PB | Try |
| 4 | PB | 发送 | TM | Try成功 |
| 5 | TM | 发送 | PC | Try |
| 6 | PC | 发送 | TM | Try成功 |
| 7 | TM | 发送 | PA | Confirm |
| 8 | PA | 发送 | TM | Confirm成功 |
| 9 | TM | 发送 | PB | Confirm |
| 10 | PB | 发送 | TM | Confirm成功 |
| 11 | TM | 发送 | PC | Confirm |
| 12 | PC | 发送 | TM | Confirm成功 |


### 2.2 异常情况处理

#### 序列图

| 步骤 | 参与者 | 动作 | 目标 | 说明 |
|------|--------|------|------|------|
| 1 | TM | 发送 | PA | Try |
| 2 | PA | 发送 | TM | Try成功 |
| 3 | TM | 发送 | PB | Try |
| 4 | PB | 发送 | TM | Try成功 |
| 5 | TM | 发送 | PC | Try |
| 6 | PC | 发送 | TM | Try失败 |
| 7 | TM | 发送 | PA | Cancel |
| 8 | PA | 发送 | TM | Cancel成功 |
| 9 | TM | 发送 | PB | Cancel |
| 10 | PB | 发送 | TM | Cancel成功 |


## 3. TCC框架核心实现

### 3.1 TCC事务上下文

```java
import java.util.*;
import java.util.concurrent.*;

/**
 * TCC事务上下文
 */
public class TCCTransactionContext {
    private final String transactionId;
    private final String rootTransactionId;
    private final long createTime;
    private final long timeout;
    private final Map<String, Object> attributes = new ConcurrentHashMap<>();

    public TCCTransactionContext(String transactionId, long timeout) {
        this.transactionId = transactionId;
        this.rootTransactionId = transactionId;
        this.createTime = System.currentTimeMillis();
        this.timeout = timeout;
    }

    public TCCTransactionContext(String transactionId, String rootTransactionId, long timeout) {
        this.transactionId = transactionId;
        this.rootTransactionId = rootTransactionId;
        this.createTime = System.currentTimeMillis();
        this.timeout = timeout;
    }

    /**
     * 创建分支事务上下文
     */
    public TCCTransactionContext createBranch() {
        String branchId = transactionId + "-" + UUID.randomUUID().toString().substring(0, 8);
        return new TCCTransactionContext(branchId, rootTransactionId, timeout);
    }

    /**
     * 检查是否超时
     */
    public boolean isTimeout() {
        return System.currentTimeMillis() - createTime > timeout;
    }

    /**
     * 获取剩余时间
     */
    public long getRemainingTime() {
        long elapsed = System.currentTimeMillis() - createTime;
        return Math.max(0, timeout - elapsed);
    }

    // Getters and Setters
    public String getTransactionId() { return transactionId; }
    public String getRootTransactionId() { return rootTransactionId; }
    public long getCreateTime() { return createTime; }
    public long getTimeout() { return timeout; }

    public void setAttribute(String key, Object value) {
        attributes.put(key, value);
    }

    public <T> T getAttribute(String key, Class<T> type) {
        Object value = attributes.get(key);
        return type.isInstance(value) ? type.cast(value) : null;
    }

    @Override
    public String toString() {
        return String.format("TCCTransactionContext{id='%s', root='%s', age=%dms, timeout=%dms}",
                transactionId, rootTransactionId,
                System.currentTimeMillis() - createTime, timeout);
    }
}

/**
 * TCC事务上下文持有者
 */
public class TCCTransactionContextHolder {
    private static final ThreadLocal<TCCTransactionContext> CONTEXT_HOLDER = new ThreadLocal<>();

    public static void setContext(TCCTransactionContext context) {
        CONTEXT_HOLDER.set(context);
    }

    public static TCCTransactionContext getContext() {
        return CONTEXT_HOLDER.get();
    }

    public static boolean hasContext() {
        return CONTEXT_HOLDER.get() != null;
    }

    public static void clear() {
        CONTEXT_HOLDER.remove();
    }

    public static String getCurrentTransactionId() {
        TCCTransactionContext context = getContext();
        return context != null ? context.getTransactionId() : null;
    }
}
```

### 3.2 TCC参与者接口

```java
/**
 * TCC参与者接口
 */
public interface TCCParticipant {

    /**
     * Try阶段：预留资源，执行业务检查
     *
     * @param context TCC事务上下文
     * @param businessData 业务数据
     * @return Try执行结果
     */
    TCCResult tryExecute(TCCTransactionContext context, Object businessData);

    /**
     * Confirm阶段：确认执行，完成业务操作
     *
     * @param context TCC事务上下文
     * @return Confirm执行结果
     */
    TCCResult confirmExecute(TCCTransactionContext context);

    /**
     * Cancel阶段：取消预留，释放资源
     *
     * @param context TCC事务上下文
     * @return Cancel执行结果
     */
    TCCResult cancelExecute(TCCTransactionContext context);

    /**
     * 获取参与者标识
     */
    String getParticipantId();
}

/**
 * TCC执行结果
 */
public class TCCResult {
    private final boolean success;
    private final String message;
    private final String errorCode;
    private final Object data;

    public TCCResult(boolean success, String message) {
        this(success, message, null, null);
    }

    public TCCResult(boolean success, String message, String errorCode, Object data) {
        this.success = success;
        this.message = message;
        this.errorCode = errorCode;
        this.data = data;
    }

    public static TCCResult success() {
        return new TCCResult(true, "Success");
    }

    public static TCCResult success(String message) {
        return new TCCResult(true, message);
    }

    public static TCCResult success(String message, Object data) {
        return new TCCResult(true, message, null, data);
    }

    public static TCCResult failure(String message) {
        return new TCCResult(false, message);
    }

    public static TCCResult failure(String message, String errorCode) {
        return new TCCResult(false, message, errorCode, null);
    }

    // Getters
    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public String getErrorCode() { return errorCode; }
    public Object getData() { return data; }

    @Override
    public String toString() {
        return String.format("TCCResult{success=%s, message='%s', errorCode='%s'}",
                success, message, errorCode);
    }
}

/**
 * TCC事务阶段枚举
 */
public enum TCCPhase {
    TRY,        // 尝试阶段
    CONFIRM,    // 确认阶段
    CANCEL      // 取消阶段
}

/**
 * TCC事务状态枚举
 */
public enum TCCTransactionStatus {
    TRYING,     // 尝试中
    CONFIRMING, // 确认中
    CONFIRMED,  // 已确认
    CANCELLING, // 取消中
    CANCELLED,  // 已取消
    FAILED      // 失败
}
```

### 3.3 TCC事务管理器

```java
import java.util.concurrent.atomic.AtomicInteger;

/**
 * TCC事务管理器
 */
public class TCCTransactionManager {
    private final String nodeId;
    private final AtomicInteger transactionCounter = new AtomicInteger(0);
    private final Map<String, TCCTransaction> activeTransactions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(3);
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // 配置参数
    private final long defaultTimeout = 30000; // 30秒
    private final int maxRetryAttempts = 3;
    private final long retryInterval = 5000; // 5秒

    public TCCTransactionManager(String nodeId) {
        this.nodeId = nodeId;

        // 启动定时任务
        scheduler.scheduleAtFixedRate(this::timeoutCheck, 10, 10, TimeUnit.SECONDS);
        scheduler.scheduleAtFixedRate(this::retryCheck, 30, 30, TimeUnit.SECONDS);
    }

    /**
     * 开始TCC事务
     */
    public TCCTransactionContext beginTransaction() {
        return beginTransaction(defaultTimeout);
    }

    /**
     * 开始TCC事务（指定超时时间）
     */
    public TCCTransactionContext beginTransaction(long timeout) {
        String transactionId = generateTransactionId();
        TCCTransactionContext context = new TCCTransactionContext(transactionId, timeout);

        TCCTransaction transaction = new TCCTransaction(context);
        activeTransactions.put(transactionId, transaction);

        TCCTransactionContextHolder.setContext(context);

        System.out.println("开始TCC事务: " + transactionId);
        return context;
    }

    /**
     * 注册TCC参与者
     */
    public void registerParticipant(TCCParticipant participant, Object businessData) {
        TCCTransactionContext context = TCCTransactionContextHolder.getContext();
        if (context == null) {
            throw new IllegalStateException("当前没有活跃的TCC事务");
        }

        TCCTransaction transaction = activeTransactions.get(context.getTransactionId());
        if (transaction == null) {
            throw new IllegalStateException("TCC事务不存在: " + context.getTransactionId());
        }

        transaction.addParticipant(participant, businessData);
        System.out.println("注册TCC参与者: " + participant.getParticipantId());
    }

    /**
     * 提交TCC事务
     */
    public boolean commit() {
        TCCTransactionContext context = TCCTransactionContextHolder.getContext();
        if (context == null) {
            throw new IllegalStateException("当前没有活跃的TCC事务");
        }

        return commit(context.getTransactionId());
    }

    /**
     * 提交指定的TCC事务
     */
    public boolean commit(String transactionId) {
        TCCTransaction transaction = activeTransactions.get(transactionId);
        if (transaction == null) {
            System.err.println("TCC事务不存在: " + transactionId);
            return false;
        }

        try {
            transaction.setStatus(TCCTransactionStatus.CONFIRMING);

            // 执行Try阶段
            boolean trySuccess = executeTryPhase(transaction);
            if (!trySuccess) {
                // Try阶段失败，执行Cancel
                executeCancel(transactionId);
                return false;
            }

            // 执行Confirm阶段
            boolean confirmSuccess = executeConfirmPhase(transaction);
            if (confirmSuccess) {
                transaction.setStatus(TCCTransactionStatus.CONFIRMED);
                activeTransactions.remove(transactionId);
                System.out.println("TCC事务提交成功: " + transactionId);
                return true;
            } else {
                transaction.setStatus(TCCTransactionStatus.FAILED);
                System.err.println("TCC事务Confirm阶段失败: " + transactionId);
                return false;
            }

        } catch (Exception e) {
            transaction.setStatus(TCCTransactionStatus.FAILED);
            System.err.println("TCC事务提交异常: " + transactionId + ", " + e.getMessage());
            return false;
        } finally {
            TCCTransactionContextHolder.clear();
        }
    }

    /**
     * 回滚TCC事务
     */
    public boolean rollback() {
        TCCTransactionContext context = TCCTransactionContextHolder.getContext();
        if (context == null) {
            throw new IllegalStateException("当前没有活跃的TCC事务");
        }

        return rollback(context.getTransactionId());
    }

    /**
     * 回滚指定的TCC事务
     */
    public boolean rollback(String transactionId) {
        return executeCancel(transactionId);
    }

    /**
     * 执行Cancel操作
     */
    private boolean executeCancel(String transactionId) {
        TCCTransaction transaction = activeTransactions.get(transactionId);
        if (transaction == null) {
            System.err.println("TCC事务不存在: " + transactionId);
            return false;
        }

        try {
            transaction.setStatus(TCCTransactionStatus.CANCELLING);

            boolean cancelSuccess = executeCancelPhase(transaction);
            if (cancelSuccess) {
                transaction.setStatus(TCCTransactionStatus.CANCELLED);
                activeTransactions.remove(transactionId);
                System.out.println("TCC事务回滚成功: " + transactionId);
                return true;
            } else {
                transaction.setStatus(TCCTransactionStatus.FAILED);
                System.err.println("TCC事务Cancel阶段失败: " + transactionId);
                return false;
            }

        } catch (Exception e) {
            transaction.setStatus(TCCTransactionStatus.FAILED);
            System.err.println("TCC事务回滚异常: " + transactionId + ", " + e.getMessage());
            return false;
        } finally {
            TCCTransactionContextHolder.clear();
        }
    }

    /**
     * 执行Try阶段
     */
    private boolean executeTryPhase(TCCTransaction transaction) {
        System.out.println("执行Try阶段: " + transaction.getContext().getTransactionId());

        List<CompletableFuture<TCCResult>> futures = new ArrayList<>();

        for (TCCParticipantInfo participantInfo : transaction.getParticipants()) {
            CompletableFuture<TCCResult> future = CompletableFuture.supplyAsync(() -> {
                try {
                    return participantInfo.getParticipant().tryExecute(
                            transaction.getContext(),
                            participantInfo.getBusinessData()
                    );
                } catch (Exception e) {
                    System.err.println("Try阶段异常: " + participantInfo.getParticipant().getParticipantId() +
                                     ", " + e.getMessage());
                    return TCCResult.failure("Try阶段执行异常: " + e.getMessage());
                }
            }, executor);

            futures.add(future);
        }

        // 等待所有Try完成
        try {
            List<TCCResult> results = futures.stream()
                    .map(future -> {
                        try {
                            return future.get(10, TimeUnit.SECONDS);
                        } catch (Exception e) {
                            return TCCResult.failure("Try阶段超时");
                        }
                    })
                    .collect(Collectors.toList());

            // 检查是否所有Try都成功
            boolean allSuccess = results.stream().allMatch(TCCResult::isSuccess);

            if (!allSuccess) {
                System.err.println("Try阶段存在失败:");
                for (int i = 0; i < results.size(); i++) {
                    TCCResult result = results.get(i);
                    if (!result.isSuccess()) {
                        TCCParticipantInfo participantInfo = transaction.getParticipants().get(i);
                        System.err.println("- " + participantInfo.getParticipant().getParticipantId() +
                                         ": " + result.getMessage());
                    }
                }
            }

            return allSuccess;

        } catch (Exception e) {
            System.err.println("Try阶段执行异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * 执行Confirm阶段
     */
    private boolean executeConfirmPhase(TCCTransaction transaction) {
        System.out.println("执行Confirm阶段: " + transaction.getContext().getTransactionId());

        List<CompletableFuture<TCCResult>> futures = new ArrayList<>();

        for (TCCParticipantInfo participantInfo : transaction.getParticipants()) {
            CompletableFuture<TCCResult> future = CompletableFuture.supplyAsync(() -> {
                try {
                    return participantInfo.getParticipant().confirmExecute(transaction.getContext());
                } catch (Exception e) {
                    System.err.println("Confirm阶段异常: " + participantInfo.getParticipant().getParticipantId() +
                                     ", " + e.getMessage());
                    return TCCResult.failure("Confirm阶段执行异常: " + e.getMessage());
                }
            }, executor);

            futures.add(future);
        }

        // 等待所有Confirm完成
        try {
            List<TCCResult> results = futures.stream()
                    .map(future -> {
                        try {
                            return future.get(10, TimeUnit.SECONDS);
                        } catch (Exception e) {
                            return TCCResult.failure("Confirm阶段超时");
                        }
                    })
                    .collect(Collectors.toList());

            // 检查是否所有Confirm都成功
            boolean allSuccess = results.stream().allMatch(TCCResult::isSuccess);

            if (!allSuccess) {
                System.err.println("Confirm阶段存在失败:");
                for (int i = 0; i < results.size(); i++) {
                    TCCResult result = results.get(i);
                    if (!result.isSuccess()) {
                        TCCParticipantInfo participantInfo = transaction.getParticipants().get(i);
                        System.err.println("- " + participantInfo.getParticipant().getParticipantId() +
                                         ": " + result.getMessage());
                    }
                }
            }

            return allSuccess;

        } catch (Exception e) {
            System.err.println("Confirm阶段执行异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * 执行Cancel阶段
     */
    private boolean executeCancelPhase(TCCTransaction transaction) {
        System.out.println("执行Cancel阶段: " + transaction.getContext().getTransactionId());

        List<CompletableFuture<TCCResult>> futures = new ArrayList<>();

        for (TCCParticipantInfo participantInfo : transaction.getParticipants()) {
            CompletableFuture<TCCResult> future = CompletableFuture.supplyAsync(() -> {
                try {
                    return participantInfo.getParticipant().cancelExecute(transaction.getContext());
                } catch (Exception e) {
                    System.err.println("Cancel阶段异常: " + participantInfo.getParticipant().getParticipantId() +
                                     ", " + e.getMessage());
                    return TCCResult.failure("Cancel阶段执行异常: " + e.getMessage());
                }
            }, executor);

            futures.add(future);
        }

        // 等待所有Cancel完成
        try {
            List<TCCResult> results = futures.stream()
                    .map(future -> {
                        try {
                            return future.get(10, TimeUnit.SECONDS);
                        } catch (Exception e) {
                            return TCCResult.failure("Cancel阶段超时");
                        }
                    })
                    .collect(Collectors.toList());

            // Cancel阶段要求最大努力，即使部分失败也认为成功
            long successCount = results.stream().mapToLong(result -> result.isSuccess() ? 1 : 0).sum();
            System.out.println("Cancel阶段完成: " + successCount + "/" + results.size() + " 成功");

            return true;

        } catch (Exception e) {
            System.err.println("Cancel阶段执行异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * 超时检查
     */
    private void timeoutCheck() {
        List<String> timeoutTransactions = new ArrayList<>();

        for (TCCTransaction transaction : activeTransactions.values()) {
            if (transaction.getContext().isTimeout()) {
                timeoutTransactions.add(transaction.getContext().getTransactionId());
            }
        }

        for (String transactionId : timeoutTransactions) {
            System.out.println("TCC事务超时，自动回滚: " + transactionId);
            executeCancel(transactionId);
        }
    }

    /**
     * 重试检查
     */
    private void retryCheck() {
        for (TCCTransaction transaction : activeTransactions.values()) {
            if (transaction.getStatus() == TCCTransactionStatus.FAILED &&
                transaction.getRetryCount() < maxRetryAttempts &&
                System.currentTimeMillis() - transaction.getLastRetryTime() > retryInterval) {

                System.out.println("重试TCC事务: " + transaction.getContext().getTransactionId());
                transaction.incrementRetryCount();
                transaction.setLastRetryTime(System.currentTimeMillis());

                // 重新尝试提交
                executor.submit(() -> commit(transaction.getContext().getTransactionId()));
            }
        }
    }

    /**
     * 生成事务ID
     */
    private String generateTransactionId() {
        return nodeId + "-" + System.currentTimeMillis() + "-" + transactionCounter.incrementAndGet();
    }

    /**
     * 获取活跃事务统计
     */
    public TCCTransactionManagerStats getStats() {
        Map<TCCTransactionStatus, Long> statusCount = activeTransactions.values().stream()
                .collect(Collectors.groupingBy(TCCTransaction::getStatus, Collectors.counting()));

        return new TCCTransactionManagerStats(
                nodeId,
                transactionCounter.get(),
                activeTransactions.size(),
                statusCount
        );
    }

    /**
     * 关闭事务管理器
     */
    public void shutdown() {
        // 回滚所有活跃事务
        for (String transactionId : new ArrayList<>(activeTransactions.keySet())) {
            executeCancel(transactionId);
        }

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

        System.out.println("TCC事务管理器已关闭: " + nodeId);
    }
}

/**
 * TCC事务
 */
class TCCTransaction {
    private final TCCTransactionContext context;
    private volatile TCCTransactionStatus status;
    private final List<TCCParticipantInfo> participants = new ArrayList<>();
    private volatile int retryCount = 0;
    private volatile long lastRetryTime = 0;

    public TCCTransaction(TCCTransactionContext context) {
        this.context = context;
        this.status = TCCTransactionStatus.TRYING;
    }

    public void addParticipant(TCCParticipant participant, Object businessData) {
        participants.add(new TCCParticipantInfo(participant, businessData));
    }

    public void incrementRetryCount() {
        this.retryCount++;
    }

    // Getters and Setters
    public TCCTransactionContext getContext() { return context; }
    public TCCTransactionStatus getStatus() { return status; }
    public void setStatus(TCCTransactionStatus status) { this.status = status; }
    public List<TCCParticipantInfo> getParticipants() { return new ArrayList<>(participants); }
    public int getRetryCount() { return retryCount; }
    public long getLastRetryTime() { return lastRetryTime; }
    public void setLastRetryTime(long lastRetryTime) { this.lastRetryTime = lastRetryTime; }
}

/**
 * TCC参与者信息
 */
class TCCParticipantInfo {
    private final TCCParticipant participant;
    private final Object businessData;

    public TCCParticipantInfo(TCCParticipant participant, Object businessData) {
        this.participant = participant;
        this.businessData = businessData;
    }

    public TCCParticipant getParticipant() { return participant; }
    public Object getBusinessData() { return businessData; }
}

/**
 * TCC事务管理器统计信息
 */
class TCCTransactionManagerStats {
    private final String nodeId;
    private final long totalTransactions;
    private final int activeTransactions;
    private final Map<TCCTransactionStatus, Long> statusDistribution;

    public TCCTransactionManagerStats(String nodeId, long totalTransactions, int activeTransactions,
                                    Map<TCCTransactionStatus, Long> statusDistribution) {
        this.nodeId = nodeId;
        this.totalTransactions = totalTransactions;
        this.activeTransactions = activeTransactions;
        this.statusDistribution = new HashMap<>(statusDistribution);
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public long getTotalTransactions() { return totalTransactions; }
    public int getActiveTransactions() { return activeTransactions; }
    public Map<TCCTransactionStatus, Long> getStatusDistribution() { return new HashMap<>(statusDistribution); }

    @Override
    public String toString() {
        return String.format("TCCTransactionManagerStats{nodeId='%s', total=%d, active=%d, status=%s}",
                nodeId, totalTransactions, activeTransactions, statusDistribution);
    }
}
```

## 4. TCC参与者具体实现

### 4.1 账户服务TCC参与者

```java
import java.math.BigDecimal;
import java.sql.*;

/**
 * 账户服务TCC参与者
 */
public class AccountServiceTCCParticipant implements TCCParticipant {
    private final String participantId;
    private final String jdbcUrl;
    private final String username;
    private final String password;

    public AccountServiceTCCParticipant(String participantId, String jdbcUrl, String username, String password) {
        this.participantId = participantId;
        this.jdbcUrl = jdbcUrl;
        this.username = username;
        this.password = password;
    }

    @Override
    public TCCResult tryExecute(TCCTransactionContext context, Object businessData) {
        if (!(businessData instanceof AccountTransferRequest)) {
            return TCCResult.failure("业务数据类型错误");
        }

        AccountTransferRequest request = (AccountTransferRequest) businessData;

        try (Connection conn = getConnection()) {
            // 检查账户余额是否足够
            BigDecimal balance = getAccountBalance(conn, request.getFromAccount());
            if (balance.compareTo(request.getAmount()) < 0) {
                return TCCResult.failure("账户余额不足");
            }

            // 冻结转账金额
            boolean freezeSuccess = freezeAmount(conn, request.getFromAccount(), request.getAmount(),
                                               context.getTransactionId());
            if (!freezeSuccess) {
                return TCCResult.failure("冻结金额失败");
            }

            System.out.println("Try阶段成功 - 账户: " + request.getFromAccount() +
                              ", 冻结金额: " + request.getAmount());
            return TCCResult.success("Try阶段成功");

        } catch (SQLException e) {
            System.err.println("Try阶段异常: " + e.getMessage());
            return TCCResult.failure("Try阶段执行异常: " + e.getMessage());
        }
    }

    @Override
    public TCCResult confirmExecute(TCCTransactionContext context) {
        try (Connection conn = getConnection()) {
            // 从事务上下文获取业务数据
            AccountTransferRequest request = getBusinessDataFromContext(context);
            if (request == null) {
                return TCCResult.failure("无法获取业务数据");
            }

            // 执行实际转账：从冻结金额中扣除
            boolean deductSuccess = deductFrozenAmount(conn, request.getFromAccount(),
                                                     request.getAmount(), context.getTransactionId());
            if (!deductSuccess) {
                return TCCResult.failure("扣除冻结金额失败");
            }

            // 向目标账户增加金额
            boolean addSuccess = addAmount(conn, request.getToAccount(), request.getAmount());
            if (!addSuccess) {
                return TCCResult.failure("增加目标账户金额失败");
            }

            System.out.println("Confirm阶段成功 - 从账户: " + request.getFromAccount() +
                              " 向账户: " + request.getToAccount() +
                              " 转账: " + request.getAmount());
            return TCCResult.success("Confirm阶段成功");

        } catch (SQLException e) {
            System.err.println("Confirm阶段异常: " + e.getMessage());
            return TCCResult.failure("Confirm阶段执行异常: " + e.getMessage());
        }
    }

    @Override
    public TCCResult cancelExecute(TCCTransactionContext context) {
        try (Connection conn = getConnection()) {
            // 释放冻结的金额
            boolean unfreezeSuccess = unfreezeAmount(conn, context.getTransactionId());
            if (unfreezeSuccess) {
                System.out.println("Cancel阶段成功 - 释放冻结金额: " + context.getTransactionId());
                return TCCResult.success("Cancel阶段成功");
            } else {
                System.err.println("Cancel阶段失败 - 释放冻结金额失败: " + context.getTransactionId());
                return TCCResult.failure("释放冻结金额失败");
            }

        } catch (SQLException e) {
            System.err.println("Cancel阶段异常: " + e.getMessage());
            return TCCResult.failure("Cancel阶段执行异常: " + e.getMessage());
        }
    }

    /**
     * 获取数据库连接
     */
    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(jdbcUrl, username, password);
    }

    /**
     * 获取账户余额
     */
    private BigDecimal getAccountBalance(Connection conn, String accountId) throws SQLException {
        String sql = "SELECT balance FROM accounts WHERE account_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, accountId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getBigDecimal("balance");
                } else {
                    throw new SQLException("账户不存在: " + accountId);
                }
            }
        }
    }

    /**
     * 冻结金额
     */
    private boolean freezeAmount(Connection conn, String accountId, BigDecimal amount, String transactionId)
            throws SQLException {
        // 插入冻结记录
        String insertSql = "INSERT INTO account_freeze (account_id, amount, transaction_id, create_time) VALUES (?, ?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(insertSql)) {
            pstmt.setString(1, accountId);
            pstmt.setBigDecimal(2, amount);
            pstmt.setString(3, transactionId);
            pstmt.setTimestamp(4, new Timestamp(System.currentTimeMillis()));

            int result = pstmt.executeUpdate();
            return result > 0;
        }
    }

    /**
     * 扣除冻结金额
     */
    private boolean deductFrozenAmount(Connection conn, String accountId, BigDecimal amount, String transactionId)
            throws SQLException {
        conn.setAutoCommit(false);
        try {
            // 从账户余额中扣除
            String updateBalanceSql = "UPDATE accounts SET balance = balance - ? WHERE account_id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(updateBalanceSql)) {
                pstmt.setBigDecimal(1, amount);
                pstmt.setString(2, accountId);
                pstmt.executeUpdate();
            }

            // 删除冻结记录
            String deleteFreezeS
= "DELETE FROM account_freeze WHERE account_id = ? AND transaction_id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(deleteFreezeSql)) {
                pstmt.setString(1, accountId);
                pstmt.setString(2, transactionId);
                pstmt.executeUpdate();
            }

            conn.commit();
            return true;

        } catch (SQLException e) {
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
        }
    }

    /**
     * 向账户增加金额
     */
    private boolean addAmount(Connection conn, String accountId, BigDecimal amount) throws SQLException {
        String sql = "UPDATE accounts SET balance = balance + ? WHERE account_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setBigDecimal(1, amount);
            pstmt.setString(2, accountId);

            int result = pstmt.executeUpdate();
            return result > 0;
        }
    }

    /**
     * 释放冻结金额
     */
    private boolean unfreezeAmount(Connection conn, String transactionId) throws SQLException {
        String sql = "DELETE FROM account_freeze WHERE transaction_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, transactionId);

            int result = pstmt.executeUpdate();
            return result >= 0; // 删除0行也算成功（可能已经被处理过）
        }
    }

    /**
     * 从上下文获取业务数据
     */
    private AccountTransferRequest getBusinessDataFromContext(TCCTransactionContext context) {
        // 在实际实现中，应该从持久化存储中获取业务数据
        // 这里简化处理，从上下文属性中获取
        return context.getAttribute("businessData", AccountTransferRequest.class);
    }

    @Override
    public String getParticipantId() {
        return participantId;
    }
}

/**
 * 账户转账请求
 */
class AccountTransferRequest {
    private final String fromAccount;
    private final String toAccount;
    private final BigDecimal amount;
    private final String description;

    public AccountTransferRequest(String fromAccount, String toAccount, BigDecimal amount, String description) {
        this.fromAccount = fromAccount;
        this.toAccount = toAccount;
        this.amount = amount;
        this.description = description;
    }

    // Getters
    public String getFromAccount() { return fromAccount; }
    public String getToAccount() { return toAccount; }
    public BigDecimal getAmount() { return amount; }
    public String getDescription() { return description; }

    @Override
    public String toString() {
        return String.format("AccountTransferRequest{from='%s', to='%s', amount=%s, desc='%s'}",
                fromAccount, toAccount, amount, description);
    }
}
```

### 4.2 库存服务TCC参与者

```java
/**
 * 库存服务TCC参与者
 */
public class InventoryServiceTCCParticipant implements TCCParticipant {
    private final String participantId;
    private final String jdbcUrl;
    private final String username;
    private final String password;

    public InventoryServiceTCCParticipant(String participantId, String jdbcUrl, String username, String password) {
        this.participantId = participantId;
        this.jdbcUrl = jdbcUrl;
        this.username = username;
        this.password = password;
    }

    @Override
    public TCCResult tryExecute(TCCTransactionContext context, Object businessData) {
        if (!(businessData instanceof InventoryReservationRequest)) {
            return TCCResult.failure("业务数据类型错误");
        }

        InventoryReservationRequest request = (InventoryReservationRequest) businessData;

        try (Connection conn = getConnection()) {
            // 检查库存是否足够
            int availableQuantity = getAvailableQuantity(conn, request.getProductId());
            if (availableQuantity < request.getQuantity()) {
                return TCCResult.failure("库存不足");
            }

            // 预留库存
            boolean reserveSuccess = reserveInventory(conn, request.getProductId(), request.getQuantity(),
                                                    context.getTransactionId());
            if (!reserveSuccess) {
                return TCCResult.failure("预留库存失败");
            }

            System.out.println("Try阶段成功 - 产品: " + request.getProductId() +
                              ", 预留数量: " + request.getQuantity());
            return TCCResult.success("Try阶段成功");

        } catch (SQLException e) {
            System.err.println("Try阶段异常: " + e.getMessage());
            return TCCResult.failure("Try阶段执行异常: " + e.getMessage());
        }
    }

    @Override
    public TCCResult confirmExecute(TCCTransactionContext context) {
        try (Connection conn = getConnection()) {
            // 确认扣减库存：将预留的库存转为实际扣减
            boolean confirmSuccess = confirmInventoryDeduction(conn, context.getTransactionId());
            if (confirmSuccess) {
                System.out.println("Confirm阶段成功 - 确认库存扣减: " + context.getTransactionId());
                return TCCResult.success("Confirm阶段成功");
            } else {
                return TCCResult.failure("确认库存扣减失败");
            }

        } catch (SQLException e) {
            System.err.println("Confirm阶段异常: " + e.getMessage());
            return TCCResult.failure("Confirm阶段执行异常: " + e.getMessage());
        }
    }

    @Override
    public TCCResult cancelExecute(TCCTransactionContext context) {
        try (Connection conn = getConnection()) {
            // 释放预留的库存
            boolean releaseSuccess = releaseReservedInventory(conn, context.getTransactionId());
            if (releaseSuccess) {
                System.out.println("Cancel阶段成功 - 释放预留库存: " + context.getTransactionId());
                return TCCResult.success("Cancel阶段成功");
            } else {
                System.err.println("Cancel阶段失败 - 释放预留库存失败: " + context.getTransactionId());
                return TCCResult.failure("释放预留库存失败");
            }

        } catch (SQLException e) {
            System.err.println("Cancel阶段异常: " + e.getMessage());
            return TCCResult.failure("Cancel阶段执行异常: " + e.getMessage());
        }
    }

    /**
     * 获取数据库连接
     */
    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(jdbcUrl, username, password);
    }

    /**
     * 获取可用库存数量
     */
    private int getAvailableQuantity(Connection conn, String productId) throws SQLException {
        String sql = "SELECT quantity FROM inventory WHERE product_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, productId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("quantity");
                } else {
                    throw new SQLException("产品不存在: " + productId);
                }
            }
        }
    }

    /**
     * 预留库存
     */
    private boolean reserveInventory(Connection conn, String productId, int quantity, String transactionId)
            throws SQLException {
        // 插入预留记录
        String insertSql = "INSERT INTO inventory_reservation (product_id, quantity, transaction_id, create_time) VALUES (?, ?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(insertSql)) {
            pstmt.setString(1, productId);
            pstmt.setInt(2, quantity);
            pstmt.setString(3, transactionId);
            pstmt.setTimestamp(4, new Timestamp(System.currentTimeMillis()));

            int result = pstmt.executeUpdate();
            return result > 0;
        }
    }

    /**
     * 确认库存扣减
     */
    private boolean confirmInventoryDeduction(Connection conn, String transactionId) throws SQLException {
        conn.setAutoCommit(false);
        try {
            // 获取预留信息
            String selectSql = "SELECT product_id, quantity FROM inventory_reservation WHERE transaction_id = ?";
            String productId = null;
            int quantity = 0;

            try (PreparedStatement pstmt = conn.prepareStatement(selectSql)) {
                pstmt.setString(1, transactionId);
                try (ResultSet rs = pstmt.executeQuery()) {
                    if (rs.next()) {
                        productId = rs.getString("product_id");
                        quantity = rs.getInt("quantity");
                    } else {
                        throw new SQLException("预留记录不存在: " + transactionId);
                    }
                }
            }

            // 扣减实际库存
            String updateSql = "UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(updateSql)) {
                pstmt.setInt(1, quantity);
                pstmt.setString(2, productId);
                pstmt.executeUpdate();
            }

            // 删除预留记录
            String deleteSql = "DELETE FROM inventory_reservation WHERE transaction_id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(deleteSql)) {
                pstmt.setString(1, transactionId);
                pstmt.executeUpdate();
            }

            // 插入库存变动记录
            String insertLogSql = "INSERT INTO inventory_log (product_id, quantity_change, transaction_id, operation_type, create_time) VALUES (?, ?, ?, ?, ?)";
            try (PreparedStatement pstmt = conn.prepareStatement(insertLogSql)) {
                pstmt.setString(1, productId);
                pstmt.setInt(2, -quantity);
                pstmt.setString(3, transactionId);
                pstmt.setString(4, "DEDUCTION");
                pstmt.setTimestamp(5, new Timestamp(System.currentTimeMillis()));
                pstmt.executeUpdate();
            }

            conn.commit();
            return true;

        } catch (SQLException e) {
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
        }
    }

    /**
     * 释放预留库存
     */
    private boolean releaseReservedInventory(Connection conn, String transactionId) throws SQLException {
        String sql = "DELETE FROM inventory_reservation WHERE transaction_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, transactionId);

            int result = pstmt.executeUpdate();
            return result >= 0; // 删除0行也算成功
        }
    }

    @Override
    public String getParticipantId() {
        return participantId;
    }
}

/**
 * 库存预留请求
 */
class InventoryReservationRequest {
    private final String productId;
    private final int quantity;
    private final String orderId;

    public InventoryReservationRequest(String productId, int quantity, String orderId) {
        this.productId = productId;
        this.quantity = quantity;
        this.orderId = orderId;
    }

    // Getters
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public String getOrderId() { return orderId; }

    @Override
    public String toString() {
        return String.format("InventoryReservationRequest{productId='%s', quantity=%d, orderId='%s'}",
                productId, quantity, orderId);
    }
}
```

## 5. TCC注解和AOP支持

### 5.1 TCC注解定义

```java
import java.lang.annotation.*;

/**
 * TCC事务注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface TCC {
    /**
     * 事务超时时间（毫秒）
     */
    long timeout() default 30000;

    /**
     * 确认方法名
     */
    String confirmMethod() default "";

    /**
     * 取消方法名
     */
    String cancelMethod() default "";

    /**
     * 是否自动提交
     */
    boolean autoCommit() default true;
}

/**
 * TCC Try方法注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface TCCTry {
    /**
     * 确认方法名
     */
    String confirmMethod();

    /**
     * 取消方法名
     */
    String cancelMethod();
}

/**
 * TCC Confirm方法注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface TCCConfirm {
}

/**
 * TCC Cancel方法注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface TCCCancel {
}
```

### 5.2 TCC切面处理器

```java
import java.lang.reflect.Method;

/**
 * TCC切面处理器
 */
public class TCCAspectHandler {
    private final TCCTransactionManager transactionManager;

    public TCCAspectHandler(TCCTransactionManager transactionManager) {
        this.transactionManager = transactionManager;
    }

    /**
     * 处理TCC事务方法
     */
    public Object handleTCCTransaction(Method method, Object[] args, Callable<?> proceed) throws Exception {
        TCC tccAnnotation = method.getAnnotation(TCC.class);
        if (tccAnnotation == null) {
            return proceed.call();
        }

        // 检查是否已经在TCC事务中
        boolean isRootTransaction = !TCCTransactionContextHolder.hasContext();

        TCCTransactionContext context = null;
        if (isRootTransaction) {
            // 开始新的TCC事务
            context = transactionManager.beginTransaction(tccAnnotation.timeout());
        }

        try {
            Object result = proceed.call();

            if (isRootTransaction && tccAnnotation.autoCommit()) {
                // 自动提交事务
                boolean success = transactionManager.commit();
                if (!success) {
                    throw new RuntimeException("TCC事务提交失败");
                }
            }

            return result;

        } catch (Exception e) {
            if (isRootTransaction) {
                // 回滚事务
                transactionManager.rollback();
            }
            throw e;
        }
    }

    /**
     * 处理TCC Try方法
     */
    public Object handleTCCTry(Method method, Object target, Object[] args, Callable<?> proceed) throws Exception {
        TCCTry tryAnnotation = method.getAnnotation(TCCTry.class);
        if (tryAnnotation == null) {
            return proceed.call();
        }

        // 创建动态TCC参与者
        DynamicTCCParticipant participant = new DynamicTCCParticipant(
                target.getClass().getName() + "." + method.getName(),
                target,
                method,
                tryAnnotation.confirmMethod(),
                tryAnnotation.cancelMethod()
        );

        // 注册参与者
        transactionManager.registerParticipant(participant, args);

        // 执行Try方法（实际业务逻辑在参与者中执行）
        return proceed.call();
    }
}

/**
 * 动态TCC参与者
 */
class DynamicTCCParticipant implements TCCParticipant {
    private final String participantId;
    private final Object target;
    private final Method tryMethod;
    private final Method confirmMethod;
    private final Method cancelMethod;

    public DynamicTCCParticipant(String participantId, Object target, Method tryMethod,
                               String confirmMethodName, String cancelMethodName) {
        this.participantId = participantId;
        this.target = target;
        this.tryMethod = tryMethod;

        try {
            this.confirmMethod = target.getClass().getMethod(confirmMethodName, tryMethod.getParameterTypes());
            this.cancelMethod = target.getClass().getMethod(cancelMethodName, tryMethod.getParameterTypes());
        } catch (NoSuchMethodException e) {
            throw new RuntimeException("TCC方法不存在", e);
        }
    }

    @Override
    public TCCResult tryExecute(TCCTransactionContext context, Object businessData) {
        try {
            Object[] args = (Object[]) businessData;
            Object result = tryMethod.invoke(target, args);

            // 将结果保存到上下文
            context.setAttribute("tryResult", result);
            context.setAttribute("businessData", businessData);

            return TCCResult.success("Try阶段成功", result);

        } catch (Exception e) {
            return TCCResult.failure("Try阶段失败: " + e.getMessage());
        }
    }

    @Override
    public TCCResult confirmExecute(TCCTransactionContext context) {
        try {
            Object[] args = context.getAttribute("businessData", Object[].class);
            confirmMethod.invoke(target, args);

            return TCCResult.success("Confirm阶段成功");

        } catch (Exception e) {
            return TCCResult.failure("Confirm阶段失败: " + e.getMessage());
        }
    }

    @Override
    public TCCResult cancelExecute(TCCTransactionContext context) {
        try {
            Object[] args = context.getAttribute("businessData", Object[].class);
            cancelMethod.invoke(target, args);

            return TCCResult.success("Cancel阶段成功");

        } catch (Exception e) {
            return TCCResult.failure("Cancel阶段失败: " + e.getMessage());
        }
    }

    @Override
    public String getParticipantId() {
        return participantId;
    }
}
```

## 6. 完整应用示例

### 6.1 电商订单服务

```java
/**
 * 电商订单服务（使用TCC模式）
 */
public class ECommerceOrderService {
    private final TCCTransactionManager transactionManager;
    private final AccountServiceTCCParticipant accountService;
    private final InventoryServiceTCCParticipant inventoryService;

    public ECommerceOrderService(TCCTransactionManager transactionManager,
                               AccountServiceTCCParticipant accountService,
                               InventoryServiceTCCParticipant inventoryService) {
        this.transactionManager = transactionManager;
        this.accountService = accountService;
        this.inventoryService = inventoryService;
    }

    /**
     * 创建订单（TCC事务）
     */
    @TCC(timeout = 60000)
    public OrderResult createOrder(CreateOrderRequest request) {
        try {
            System.out.println("开始创建订单: " + request);

            // 1. 验证订单数据
            validateOrderRequest(request);

            // 2. 注册账户服务参与者（扣款）
            AccountTransferRequest accountRequest = new AccountTransferRequest(
                    request.getCustomerAccount(),
                    "MERCHANT_ACCOUNT",
                    request.getTotalAmount(),
                    "订单支付: " + request.getOrderId()
            );
            transactionManager.registerParticipant(accountService, accountRequest);

            // 3. 注册库存服务参与者（扣减库存）
            for (OrderItem item : request.getItems()) {
                InventoryReservationRequest inventoryRequest = new InventoryReservationRequest(
                        item.getProductId(),
                        item.getQuantity(),
                        request.getOrderId()
                );
                transactionManager.registerParticipant(inventoryService, inventoryRequest);
            }

            // 4. 创建订单记录
            String orderId = createOrderRecord(request);

            System.out.println("订单创建成功: " + orderId);
            return new OrderResult(true, "订单创建成功", orderId);

        } catch (Exception e) {
            System.err.println("创建订单失败: " + e.getMessage());
            return new OrderResult(false, "订单创建失败: " + e.getMessage(), null);
        }
    }

    /**
     * 手动提交订单事务
     */
    public boolean commitOrder() {
        return transactionManager.commit();
    }

    /**
     * 手动回滚订单事务
     */
    public boolean rollbackOrder() {
        return transactionManager.rollback();
    }

    /**
     * 验证订单请求
     */
    private void validateOrderRequest(CreateOrderRequest request) {
        if (request.getOrderId() == null || request.getOrderId().trim().isEmpty()) {
            throw new IllegalArgumentException("订单ID不能为空");
        }

        if (request.getCustomerAccount() == null || request.getCustomerAccount().trim().isEmpty()) {
            throw new IllegalArgumentException("客户账户不能为空");
        }

        if (request.getItems() == null || request.getItems().isEmpty()) {
            throw new IllegalArgumentException("订单项不能为空");
        }

        if (request.getTotalAmount() == null || request.getTotalAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("订单金额必须大于0");
        }
    }

    /**
     * 创建订单记录
     */
    private String createOrderRecord(CreateOrderRequest request) {
        // 这里应该将订单信息保存到数据库
        // 简化实现中返回订单ID
        System.out.println("保存订单记录: " + request.getOrderId());
        return request.getOrderId();
    }
}

/**
 * 创建订单请求
 */
class CreateOrderRequest {
    private final String orderId;
    private final String customerAccount;
    private final List<OrderItem> items;
    private final BigDecimal totalAmount;

    public CreateOrderRequest(String orderId, String customerAccount, List<OrderItem> items, BigDecimal totalAmount) {
        this.orderId = orderId;
        this.customerAccount = customerAccount;
        this.items = new ArrayList<>(items);
        this.totalAmount = totalAmount;
    }

    // Getters
    public String getOrderId() { return orderId; }
    public String getCustomerAccount() { return customerAccount; }
    public List<OrderItem> getItems() { return new ArrayList<>(items); }
    public BigDecimal getTotalAmount() { return totalAmount; }

    @Override
    public String toString() {
        return String.format("CreateOrderRequest{orderId='%s', account='%s', items=%d, amount=%s}",
                orderId, customerAccount, items.size(), totalAmount);
    }
}

/**
 * 订单项
 */
class OrderItem {
    private final String productId;
    private final int quantity;
    private final BigDecimal price;

    public OrderItem(String productId, int quantity, BigDecimal price) {
        this.productId = productId;
        this.quantity = quantity;
        this.price = price;
    }

    // Getters
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public BigDecimal getPrice() { return price; }

    @Override
    public String toString() {
        return String.format("OrderItem{productId='%s', quantity=%d, price=%s}",
                productId, quantity, price);
    }
}

/**
 * 订单结果
 */
class OrderResult {
    private final boolean success;
    private final String message;
    private final String orderId;

    public OrderResult(boolean success, String message, String orderId) {
        this.success = success;
        this.message = message;
        this.orderId = orderId;
    }

    // Getters
    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public String getOrderId() { return orderId; }

    @Override
    public String toString() {
        return String.format("OrderResult{success=%s, message='%s', orderId='%s'}",
                success, message, orderId);
    }
}
```

## 7. 完整测试示例

### 7.1 TCC模式综合测试

```java
/**
 * TCC模式综合测试
 */
public class TCCPatternTest {

    public static void main(String[] args) throws Exception {
        testTCCPattern();
    }

    /**
     * 测试TCC模式
     */
    private static void testTCCPattern() throws Exception {
        System.out.println("=== TCC模式测试开始 ===\n");

        // 创建TCC事务管理器
        TCCTransactionManager txManager = new TCCTransactionManager("test-node");

        try {
            // 创建参与者
            AccountServiceTCCParticipant accountService = createAccountService();
            InventoryServiceTCCParticipant inventoryService = createInventoryService();

            // 创建订单服务
            ECommerceOrderService orderService = new ECommerceOrderService(
                    txManager, accountService, inventoryService);

            // 测试成功的订单创建
            testSuccessfulOrder(orderService);

            // 测试失败的订单创建
            testFailedOrder(orderService);

            // 测试并发订单
            testConcurrentOrders(orderService);

            // 打印统计信息
            printStats(txManager);

        } finally {
            txManager.shutdown();
        }

        System.out.println("\n=== TCC模式测试完成 ===");
    }

    /**
     * 创建账户服务
     */
    private static AccountServiceTCCParticipant createAccountService() {
        return new AccountServiceTCCParticipant(
                "account-service",
                "jdbc:mysql://localhost:3306/account_db",
                "test_user",
                "test_password"
        );
    }

    /**
     * 创建库存服务
     */
    private static InventoryServiceTCCParticipant createInventoryService() {
        return new InventoryServiceTCCParticipant(
                "inventory-service",
                "jdbc:mysql://localhost:3306/inventory_db",
                "test_user",
                "test_password"
        );
    }

    /**
     * 测试成功的订单创建
     */
    private static void testSuccessfulOrder(ECommerceOrderService orderService) throws Exception {
        System.out.println("=== 测试成功的订单创建 ===");

        List<OrderItem> items = Arrays.asList(
                new OrderItem("PRODUCT_001", 2, new BigDecimal("50.00")),
                new OrderItem("PRODUCT_002", 1, new BigDecimal("30.00"))
        );

        CreateOrderRequest request = new CreateOrderRequest(
                "ORDER_" + System.currentTimeMillis(),
                "CUSTOMER_001",
                items,
                new BigDecimal("130.00")
        );

        OrderResult result = orderService.createOrder(request);
        System.out.println("订单创建结果: " + result);

        if (result.isSuccess()) {
            boolean commitSuccess = orderService.commitOrder();
            System.out.println("订单提交结果: " + commitSuccess);
        }

        System.out.println("=== 成功订单测试完成 ===\n");
    }

    /**
     * 测试失败的订单创建
     */
    private static void testFailedOrder(ECommerceOrderService orderService) throws Exception {
        System.out.println("=== 测试失败的订单创建 ===");

        // 创建一个会导致库存不足的订单
        List<OrderItem> items = Arrays.asList(
                new OrderItem("PRODUCT_003", 1000, new BigDecimal("10.00")) // 大量库存
        );

        CreateOrderRequest request = new CreateOrderRequest(
                "ORDER_FAIL_" + System.currentTimeMillis(),
                "CUSTOMER_002",
                items,
                new BigDecimal("10000.00")
        );

        OrderResult result = orderService.createOrder(request);
        System.out.println("订单创建结果: " + result);

        if (!result.isSuccess()) {
            boolean rollbackSuccess = orderService.rollbackOrder();
            System.out.println("订单回滚结果: " + rollbackSuccess);
        }

        System.out.println("=== 失败订单测试完成 ===\n");
    }

    /**
     * 测试并发订单
     */
    private static void testConcurrentOrders(ECommerceOrderService orderService) throws Exception {
        System.out.println("=== 测试并发订单 ===");

        int concurrentCount = 5;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentCount);
        CountDownLatch latch = new CountDownLatch(concurrentCount);
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failureCount = new AtomicInteger(0);

        for (int i = 0; i < concurrentCount; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    List<OrderItem> items = Arrays.asList(
                            new OrderItem("PRODUCT_" + threadId, 1, new BigDecimal("20.00"))
                    );

                    CreateOrderRequest request = new CreateOrderRequest(
                            "CONCURRENT_ORDER_" + threadId + "_" + System.currentTimeMillis(),
                            "CUSTOMER_" + threadId,
                            items,
                            new BigDecimal("20.00")
                    );

                    OrderResult result = orderService.createOrder(request);

                    if (result.isSuccess()) {
                        boolean commitSuccess = orderService.commitOrder();
                        if (commitSuccess) {
                            successCount.incrementAndGet();
                            System.out.println("并发订单 " + threadId + " 成功");
                        } else {
                            failureCount.incrementAndGet();
                            System.err.println("并发订单 " + threadId + " 提交失败");
                        }
                    } else {
                        orderService.rollbackOrder();
                        failureCount.incrementAndGet();
                        System.err.println("并发订单 " + threadId + " 创建失败: " + result.getMessage());
                    }

                } catch (Exception e) {
                    failureCount.incrementAndGet();
                    System.err.println("并发订单 " + threadId + " 异常: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(60, TimeUnit.SECONDS);
        executor.shutdown();

        System.out.println("并发订单结果 - 成功: " + successCount.get() + ", 失败: " + failureCount.get());
        System.out.println("=== 并发订单测试完成 ===\n");
    }

    /**
     * 打印统计信息
     */
    private static void printStats(TCCTransactionManager txManager) {
        TCCTransactionManagerStats stats = txManager.getStats();
        System.out.println("=== TCC事务统计 ===");
        System.out.println("节点ID: " + stats.getNodeId());
        System.out.println("总事务数: " + stats.getTotalTransactions());
        System.out.println("活跃事务数: " + stats.getActiveTransactions());
        System.out.println("状态分布: " + stats.getStatusDistribution());
        System.out.println("=================\n");
    }

    /**
     * 性能测试
     */
    private static void performanceTest() throws Exception {
        System.out.println("=== TCC性能测试 ===");

        TCCTransactionManager txManager = new TCCTransactionManager("perf-node");

        try {
            AccountServiceTCCParticipant accountService = createAccountService();
            InventoryServiceTCCParticipant inventoryService = createInventoryService();
            ECommerceOrderService orderService = new ECommerceOrderService(
                    txManager, accountService, inventoryService);

            int testCount = 100;
            long startTime = System.currentTimeMillis();

            for (int i = 0; i < testCount; i++) {
                List<OrderItem> items = Arrays.asList(
                        new OrderItem("PERF_PRODUCT_" + i, 1, new BigDecimal("10.00"))
                );

                CreateOrderRequest request = new CreateOrderRequest(
                        "PERF_ORDER_" + i,
                        "PERF_CUSTOMER_" + i,
                        items,
                        new BigDecimal("10.00")
                );

                OrderResult result = orderService.createOrder(request);
                if (result.isSuccess()) {
                    orderService.commitOrder();
                } else {
                    orderService.rollbackOrder();
                }
            }

            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            System.out.println("性能测试结果:");
            System.out.println("事务数量: " + testCount);
            System.out.println("总耗时: " + duration + "ms");
            System.out.println("平均耗时: " + (duration / (double) testCount) + "ms/事务");
            System.out.println("吞吐量: " + (testCount * 1000.0 / duration) + " 事务/秒");

        } finally {
            txManager.shutdown();
        }

        System.out.println("=== 性能测试完成 ===\n");
    }
}
```

## 8. 总结

TCC（Try-Confirm-Cancel）模式是一种重要的分布式事务解决方案，具有以下特点：

### 8.1 核心优势
- **业务无侵入性较低**：通过业务层面的补偿实现事务
- **性能优秀**：避免长时间锁定资源，提高并发性
- **灵活性高**：可以根据业务需求定制补偿逻辑
- **适应性强**：适用于微服务和分布式系统架构

### 8.2 关键机制
- **三阶段协议**：Try、Confirm、Cancel保证事务原子性
- **资源预留**：Try阶段预留资源而不立即执行
- **最终一致性**：通过补偿机制实现数据最终一致
- **幂等性**：Confirm和Cancel操作必须支持幂等

### 8.3 应用场景
- **电商订单**：涉及库存、支付、物流等多个服务
- **金融转账**：跨银行或跨系统的资金转移
- **预订系统**：酒店、机票等资源预订
- **资源分配**：云计算资源的分配和释放

### 8.4 实现要点
- **Try阶段**：检查业务规则，预留资源
- **Confirm阶段**：确认执行，完成业务操作
- **Cancel阶段**：释放资源，回滚预留操作
- **异常处理**：完善的重试和恢复机制

### 8.5 与其他方案比较
- **vs XA事务**：TCC性能更好，但实现复杂度更高
- **vs Saga模式**：TCC提供更强的一致性保证
- **vs 本地消息表**：TCC实时性更好，Saga适合长流程
- **vs 最大努力通知**：TCC保证强一致性

### 8.6 最佳实践
- **幂等设计**：所有TCC操作都要支持幂等
- **超时处理**：合理设置超时时间和重试策略
- **监控告警**：完善的事务监控和异常告警
- **数据一致性**：确保Try和Cancel操作的数据一致性

通过本文的详细实现，你可以深入理解TCC模式的工作原理和实现细节，为构建高性能的分布式事务系统提供有力支持。