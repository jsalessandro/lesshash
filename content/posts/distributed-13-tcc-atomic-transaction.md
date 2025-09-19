---
title: "分布式系统核心技术详解：TCC原子性执行原理与Java实现"
date: 2024-12-19T15:00:00+08:00
draft: false
tags: ["分布式系统", "TCC", "分布式事务", "补偿事务", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入解析TCC分布式事务模式的工作原理、三阶段补偿机制以及在微服务架构中的应用实践，包含完整的Java实现代码"
---

## 1. TCC模式概述

TCC（Try-Confirm-Cancel）是一种分布式事务处理模式，它将一个完整的业务操作分解为三个阶段：Try（尝试）、Confirm（确认）、Cancel（取消）。TCC模式通过业务逻辑的分解来实现分布式事务的一致性，是一种应用层的两阶段提交协议。

### 1.1 核心思想

```
传统ACID事务：
- 依赖数据库的事务机制
- 锁定资源直到事务结束
- 可能导致长时间锁定

TCC模式：
- 业务层面的事务控制
- 通过补偿机制保证一致性
- 避免长时间资源锁定
```

### 1.2 三阶段流程

#### 序列图

| 步骤 | 参与者 | 动作 | 目标 | 说明 |
|------|--------|------|------|------|
| 1 | TM | 发送 | A | Try操作 |
| 2 | A | 发送 | TM | 成功/失败 |
| 3 | TM | 发送 | B | Try操作 |
| 4 | B | 发送 | TM | 成功/失败 |
| 5 | TM | 发送 | C | Try操作 |
| 6 | C | 发送 | TM | 成功/失败 |
| 7 | TM | 发送 | A | Confirm操作 |
| 8 | TM | 发送 | B | Confirm操作 |
| 9 | TM | 发送 | C | Confirm操作 |
| 10 | TM | 发送 | A | Cancel操作 |
| 11 | TM | 发送 | B | Cancel操作 |
| 12 | TM | 发送 | C | Cancel操作 |


## 2. TCC模式核心概念

### 2.1 三个阶段详解

1. **Try阶段**：预留资源，进行参数校验和业务检查
2. **Confirm阶段**：执行真正的业务逻辑，使用Try阶段预留的资源
3. **Cancel阶段**：释放Try阶段预留的资源，进行补偿操作

### 2.2 TCC特性

- **业务层面控制**：由业务代码控制事务逻辑
- **资源预留**：Try阶段预留而非锁定资源
- **补偿机制**：通过Cancel实现回滚逻辑
- **最终一致性**：确保数据最终达到一致状态

## 3. TCC框架基础实现

### 3.1 TCC注解和接口定义

```java
import java.lang.annotation.*;
import java.util.concurrent.CompletableFuture;

/**
 * TCC事务注解
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface TCCTransaction {
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
     * 事务传播行为
     */
    TCCPropagation propagation() default TCCPropagation.REQUIRED;
}

/**
 * TCC传播行为
 */
enum TCCPropagation {
    REQUIRED,       // 需要事务
    REQUIRES_NEW,   // 总是创建新事务
    SUPPORTS,       // 支持当前事务
    NOT_SUPPORTED   // 不支持事务
}

/**
 * TCC参与者接口
 */
public interface TCCParticipant {
    /**
     * Try阶段
     */
    boolean tryExecute(TCCTransactionContext context, Object... args);

    /**
     * Confirm阶段
     */
    boolean confirmExecute(TCCTransactionContext context, Object... args);

    /**
     * Cancel阶段
     */
    boolean cancelExecute(TCCTransactionContext context, Object... args);

    /**
     * 获取参与者ID
     */
    String getParticipantId();
}

/**
 * TCC事务上下文
 */
public class TCCTransactionContext {
    private final String transactionId;
    private final String participantId;
    private final long createTime;
    private final Map<String, Object> attributes = new ConcurrentHashMap<>();
    private volatile TCCTransactionStatus status;

    public TCCTransactionContext(String transactionId, String participantId) {
        this.transactionId = transactionId;
        this.participantId = participantId;
        this.createTime = System.currentTimeMillis();
        this.status = TCCTransactionStatus.TRYING;
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
    @SuppressWarnings("unchecked")
    public <T> T getAttribute(String key, Class<T> type) {
        Object value = attributes.get(key);
        return type.isInstance(value) ? (T) value : null;
    }

    /**
     * 获取所有属性
     */
    public Map<String, Object> getAllAttributes() {
        return new HashMap<>(attributes);
    }

    // Getters and Setters
    public String getTransactionId() { return transactionId; }
    public String getParticipantId() { return participantId; }
    public long getCreateTime() { return createTime; }
    public TCCTransactionStatus getStatus() { return status; }
    public void setStatus(TCCTransactionStatus status) { this.status = status; }

    @Override
    public String toString() {
        return String.format("TCCTransactionContext{txId='%s', participantId='%s', status=%s}",
                transactionId, participantId, status);
    }
}

/**
 * TCC事务状态
 */
public enum TCCTransactionStatus {
    TRYING,         // Try阶段
    CONFIRMING,     // Confirm阶段
    CONFIRMED,      // 已确认
    CANCELLING,     // Cancel阶段
    CANCELLED,      // 已取消
    FAILED          // 失败
}
```

### 3.2 TCC事务管理器

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * TCC事务管理器
 */
public class TCCTransactionManager {
    private final String nodeId;
    private final AtomicLong transactionCounter = new AtomicLong(0);

    // 事务存储
    private final Map<String, TCCGlobalTransaction> globalTransactions = new ConcurrentHashMap<>();
    private final Map<String, TCCParticipant> participants = new ConcurrentHashMap<>();

    // 线程池
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(4);
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // 配置参数
    private final long defaultTimeout = 30000; // 30秒
    private final int maxRetryCount = 3;
    private final long retryInterval = 5000; // 5秒

    public TCCTransactionManager(String nodeId) {
        this.nodeId = nodeId;

        // 启动定时任务
        scheduler.scheduleAtFixedRate(this::timeoutCheck, 10, 10, TimeUnit.SECONDS);
        scheduler.scheduleAtFixedRate(this::retryFailedTransactions, 30, 30, TimeUnit.SECONDS);
    }

    /**
     * 注册TCC参与者
     */
    public void registerParticipant(TCCParticipant participant) {
        participants.put(participant.getParticipantId(), participant);
        System.out.println("注册TCC参与者: " + participant.getParticipantId());
    }

    /**
     * 开始TCC全局事务
     */
    public String beginGlobalTransaction() {
        return beginGlobalTransaction(defaultTimeout);
    }

    /**
     * 开始TCC全局事务（指定超时时间）
     */
    public String beginGlobalTransaction(long timeout) {
        String transactionId = generateTransactionId();
        TCCGlobalTransaction globalTx = new TCCGlobalTransaction(transactionId, timeout);
        globalTransactions.put(transactionId, globalTx);

        System.out.println("开始TCC全局事务: " + transactionId);
        return transactionId;
    }

    /**
     * 添加事务参与者
     */
    public void enlistParticipant(String transactionId, String participantId, Object... args) throws TCCException {
        TCCGlobalTransaction globalTx = globalTransactions.get(transactionId);
        if (globalTx == null) {
            throw new TCCException("全局事务不存在: " + transactionId);
        }

        if (globalTx.getStatus() != TCCTransactionStatus.TRYING) {
            throw new TCCException("事务状态错误，无法添加参与者: " + globalTx.getStatus());
        }

        TCCParticipant participant = participants.get(participantId);
        if (participant == null) {
            throw new TCCException("参与者不存在: " + participantId);
        }

        // 执行Try阶段
        TCCTransactionContext context = new TCCTransactionContext(transactionId, participantId);
        boolean tryResult = participant.tryExecute(context, args);

        if (tryResult) {
            globalTx.addParticipant(participantId, context, args);
            System.out.println("参与者Try成功: " + participantId + " in " + transactionId);
        } else {
            throw new TCCException("参与者Try失败: " + participantId);
        }
    }

    /**
     * 提交TCC事务
     */
    public void commitGlobalTransaction(String transactionId) throws TCCException {
        TCCGlobalTransaction globalTx = globalTransactions.get(transactionId);
        if (globalTx == null) {
            throw new TCCException("全局事务不存在: " + transactionId);
        }

        try {
            globalTx.setStatus(TCCTransactionStatus.CONFIRMING);
            confirmAllParticipants(globalTx);
            globalTx.setStatus(TCCTransactionStatus.CONFIRMED);

            System.out.println("TCC全局事务提交成功: " + transactionId);

        } catch (Exception e) {
            globalTx.setStatus(TCCTransactionStatus.FAILED);
            throw new TCCException("TCC事务提交失败: " + transactionId, e);
        } finally {
            globalTransactions.remove(transactionId);
        }
    }

    /**
     * 回滚TCC事务
     */
    public void rollbackGlobalTransaction(String transactionId) throws TCCException {
        TCCGlobalTransaction globalTx = globalTransactions.get(transactionId);
        if (globalTx == null) {
            throw new TCCException("全局事务不存在: " + transactionId);
        }

        try {
            globalTx.setStatus(TCCTransactionStatus.CANCELLING);
            cancelAllParticipants(globalTx);
            globalTx.setStatus(TCCTransactionStatus.CANCELLED);

            System.out.println("TCC全局事务回滚成功: " + transactionId);

        } catch (Exception e) {
            globalTx.setStatus(TCCTransactionStatus.FAILED);
            throw new TCCException("TCC事务回滚失败: " + transactionId, e);
        } finally {
            globalTransactions.remove(transactionId);
        }
    }

    /**
     * 确认所有参与者
     */
    private void confirmAllParticipants(TCCGlobalTransaction globalTx) throws TCCException {
        List<CompletableFuture<Boolean>> futures = new ArrayList<>();
        List<TCCException> exceptions = Collections.synchronizedList(new ArrayList<>());

        for (TCCParticipantInfo participantInfo : globalTx.getParticipants()) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    TCCParticipant participant = participants.get(participantInfo.getParticipantId());
                    if (participant == null) {
                        throw new TCCException("参与者不存在: " + participantInfo.getParticipantId());
                    }

                    participantInfo.getContext().setStatus(TCCTransactionStatus.CONFIRMING);
                    boolean result = participant.confirmExecute(participantInfo.getContext(), participantInfo.getArgs());

                    if (result) {
                        participantInfo.getContext().setStatus(TCCTransactionStatus.CONFIRMED);
                        System.out.println("参与者Confirm成功: " + participantInfo.getParticipantId());
                    } else {
                        throw new TCCException("参与者Confirm失败: " + participantInfo.getParticipantId());
                    }

                    return result;

                } catch (Exception e) {
                    participantInfo.getContext().setStatus(TCCTransactionStatus.FAILED);
                    exceptions.add(new TCCException("Confirm参与者失败: " + participantInfo.getParticipantId(), e));
                    return false;
                }
            }, executor);

            futures.add(future);
        }

        // 等待所有Confirm完成
        try {
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                    .get(globalTx.getTimeout(), TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            throw new TCCException("Confirm阶段超时或异常", e);
        }

        if (!exceptions.isEmpty()) {
            TCCException combined = new TCCException("部分参与者Confirm失败");
            for (TCCException ex : exceptions) {
                combined.addSuppressed(ex);
            }
            throw combined;
        }
    }

    /**
     * 取消所有参与者
     */
    private void cancelAllParticipants(TCCGlobalTransaction globalTx) throws TCCException {
        List<CompletableFuture<Boolean>> futures = new ArrayList<>();
        List<TCCException> exceptions = Collections.synchronizedList(new ArrayList<>());

        for (TCCParticipantInfo participantInfo : globalTx.getParticipants()) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    TCCParticipant participant = participants.get(participantInfo.getParticipantId());
                    if (participant == null) {
                        System.err.println("参与者不存在: " + participantInfo.getParticipantId());
                        return false;
                    }

                    participantInfo.getContext().setStatus(TCCTransactionStatus.CANCELLING);
                    boolean result = participant.cancelExecute(participantInfo.getContext(), participantInfo.getArgs());

                    if (result) {
                        participantInfo.getContext().setStatus(TCCTransactionStatus.CANCELLED);
                        System.out.println("参与者Cancel成功: " + participantInfo.getParticipantId());
                    } else {
                        System.err.println("参与者Cancel失败: " + participantInfo.getParticipantId());
                    }

                    return result;

                } catch (Exception e) {
                    participantInfo.getContext().setStatus(TCCTransactionStatus.FAILED);
                    exceptions.add(new TCCException("Cancel参与者失败: " + participantInfo.getParticipantId(), e));
                    return false;
                }
            }, executor);

            futures.add(future);
        }

        // 等待所有Cancel完成
        try {
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                    .get(globalTx.getTimeout(), TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            System.err.println("Cancel阶段超时或异常: " + e.getMessage());
        }

        // Cancel阶段不抛出异常，但记录失败的参与者
        if (!exceptions.isEmpty()) {
            System.err.println("部分参与者Cancel失败，需要人工介入");
            for (TCCException ex : exceptions) {
                System.err.println("Cancel失败: " + ex.getMessage());
            }
        }
    }

    /**
     * 超时检查
     */
    private void timeoutCheck() {
        long currentTime = System.currentTimeMillis();
        List<String> timeoutTransactions = new ArrayList<>();

        for (TCCGlobalTransaction globalTx : globalTransactions.values()) {
            if (currentTime - globalTx.getCreateTime() > globalTx.getTimeout()) {
                timeoutTransactions.add(globalTx.getTransactionId());
            }
        }

        for (String transactionId : timeoutTransactions) {
            try {
                System.out.println("事务超时，自动回滚: " + transactionId);
                rollbackGlobalTransaction(transactionId);
            } catch (TCCException e) {
                System.err.println("超时回滚失败: " + transactionId + ", " + e.getMessage());
            }
        }
    }

    /**
     * 重试失败的事务
     */
    private void retryFailedTransactions() {
        // 在实际实现中，这里应该从持久化存储中恢复失败的事务并重试
        System.out.println("检查失败事务重试...");
    }

    /**
     * 生成事务ID
     */
    private String generateTransactionId() {
        return nodeId + "-" + System.currentTimeMillis() + "-" + transactionCounter.incrementAndGet();
    }

    /**
     * 获取事务统计信息
     */
    public TCCTransactionManagerStats getStats() {
        int activeTransactions = globalTransactions.size();
        Map<TCCTransactionStatus, Long> statusCount = globalTransactions.values().stream()
                .collect(Collectors.groupingBy(TCCGlobalTransaction::getStatus, Collectors.counting()));

        return new TCCTransactionManagerStats(
                nodeId,
                transactionCounter.get(),
                activeTransactions,
                participants.size(),
                statusCount
        );
    }

    /**
     * 关闭事务管理器
     */
    public void shutdown() {
        // 回滚所有活跃事务
        for (String transactionId : new ArrayList<>(globalTransactions.keySet())) {
            try {
                rollbackGlobalTransaction(transactionId);
            } catch (TCCException e) {
                System.err.println("关闭时回滚事务失败: " + transactionId + ", " + e.getMessage());
            }
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
 * TCC异常
 */
public class TCCException extends Exception {
    public TCCException(String message) {
        super(message);
    }

    public TCCException(String message, Throwable cause) {
        super(message, cause);
    }
}

/**
 * TCC全局事务
 */
class TCCGlobalTransaction {
    private final String transactionId;
    private final long createTime;
    private final long timeout;
    private volatile TCCTransactionStatus status;
    private final List<TCCParticipantInfo> participants = new CopyOnWriteArrayList<>();

    public TCCGlobalTransaction(String transactionId, long timeout) {
        this.transactionId = transactionId;
        this.createTime = System.currentTimeMillis();
        this.timeout = timeout;
        this.status = TCCTransactionStatus.TRYING;
    }

    public void addParticipant(String participantId, TCCTransactionContext context, Object[] args) {
        participants.add(new TCCParticipantInfo(participantId, context, args));
    }

    // Getters and Setters
    public String getTransactionId() { return transactionId; }
    public long getCreateTime() { return createTime; }
    public long getTimeout() { return timeout; }
    public TCCTransactionStatus getStatus() { return status; }
    public void setStatus(TCCTransactionStatus status) { this.status = status; }
    public List<TCCParticipantInfo> getParticipants() { return new ArrayList<>(participants); }
}

/**
 * TCC参与者信息
 */
class TCCParticipantInfo {
    private final String participantId;
    private final TCCTransactionContext context;
    private final Object[] args;

    public TCCParticipantInfo(String participantId, TCCTransactionContext context, Object[] args) {
        this.participantId = participantId;
        this.context = context;
        this.args = args != null ? args.clone() : new Object[0];
    }

    public String getParticipantId() { return participantId; }
    public TCCTransactionContext getContext() { return context; }
    public Object[] getArgs() { return args.clone(); }
}

/**
 * TCC事务管理器统计信息
 */
class TCCTransactionManagerStats {
    private final String nodeId;
    private final long totalTransactions;
    private final int activeTransactions;
    private final int registeredParticipants;
    private final Map<TCCTransactionStatus, Long> statusDistribution;

    public TCCTransactionManagerStats(String nodeId, long totalTransactions, int activeTransactions,
                                    int registeredParticipants, Map<TCCTransactionStatus, Long> statusDistribution) {
        this.nodeId = nodeId;
        this.totalTransactions = totalTransactions;
        this.activeTransactions = activeTransactions;
        this.registeredParticipants = registeredParticipants;
        this.statusDistribution = new HashMap<>(statusDistribution);
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public long getTotalTransactions() { return totalTransactions; }
    public int getActiveTransactions() { return activeTransactions; }
    public int getRegisteredParticipants() { return registeredParticipants; }
    public Map<TCCTransactionStatus, Long> getStatusDistribution() { return new HashMap<>(statusDistribution); }

    @Override
    public String toString() {
        return String.format("TCCTransactionManagerStats{nodeId='%s', total=%d, active=%d, participants=%d, status=%s}",
                nodeId, totalTransactions, activeTransactions, registeredParticipants, statusDistribution);
    }
}
```

## 4. TCC业务参与者实现

### 4.1 账户服务TCC实现

```java
import java.math.BigDecimal;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 账户服务TCC参与者
 */
public class AccountServiceTCC implements TCCParticipant {
    private final String participantId = "account-service";

    // 模拟账户数据存储
    private final Map<String, BigDecimal> accounts = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> frozenAmounts = new ConcurrentHashMap<>();

    public AccountServiceTCC() {
        // 初始化一些测试账户
        accounts.put("user001", new BigDecimal("1000.00"));
        accounts.put("user002", new BigDecimal("500.00"));
        accounts.put("user003", new BigDecimal("2000.00"));
    }

    @Override
    public boolean tryExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String accountId = (String) args[1];
            BigDecimal amount = (BigDecimal) args[2];

            System.out.println("账户服务Try: " + operation + ", 账户=" + accountId + ", 金额=" + amount);

            switch (operation) {
                case "DEBIT":
                    return tryDebit(context, accountId, amount);
                case "CREDIT":
                    return tryCredit(context, accountId, amount);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("账户服务Try异常: " + e.getMessage());
            return false;
        }
    }

    @Override
    public boolean confirmExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String accountId = (String) args[1];
            BigDecimal amount = (BigDecimal) args[2];

            System.out.println("账户服务Confirm: " + operation + ", 账户=" + accountId + ", 金额=" + amount);

            switch (operation) {
                case "DEBIT":
                    return confirmDebit(context, accountId, amount);
                case "CREDIT":
                    return confirmCredit(context, accountId, amount);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("账户服务Confirm异常: " + e.getMessage());
            return false;
        }
    }

    @Override
    public boolean cancelExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String accountId = (String) args[1];
            BigDecimal amount = (BigDecimal) args[2];

            System.out.println("账户服务Cancel: " + operation + ", 账户=" + accountId + ", 金额=" + amount);

            switch (operation) {
                case "DEBIT":
                    return cancelDebit(context, accountId, amount);
                case "CREDIT":
                    return cancelCredit(context, accountId, amount);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("账户服务Cancel异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * Try扣款：冻结金额
     */
    private boolean tryDebit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        BigDecimal currentBalance = accounts.get(accountId);
        if (currentBalance == null) {
            System.err.println("账户不存在: " + accountId);
            return false;
        }

        BigDecimal currentFrozen = frozenAmounts.getOrDefault(accountId, BigDecimal.ZERO);
        BigDecimal availableBalance = currentBalance.subtract(currentFrozen);

        if (availableBalance.compareTo(amount) < 0) {
            System.err.println("余额不足: 可用=" + availableBalance + ", 需要=" + amount);
            return false;
        }

        // 冻结金额
        frozenAmounts.put(accountId, currentFrozen.add(amount));

        // 在上下文中记录冻结信息
        context.setAttribute("frozen_amount", amount);
        context.setAttribute("account_id", accountId);

        System.out.println("冻结金额成功: 账户=" + accountId + ", 金额=" + amount);
        return true;
    }

    /**
     * Confirm扣款：执行真正的扣款
     */
    private boolean confirmDebit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        BigDecimal currentBalance = accounts.get(accountId);
        BigDecimal currentFrozen = frozenAmounts.getOrDefault(accountId, BigDecimal.ZERO);

        if (currentBalance == null || currentFrozen.compareTo(amount) < 0) {
            System.err.println("Confirm扣款失败: 账户状态异常");
            return false;
        }

        // 执行扣款
        accounts.put(accountId, currentBalance.subtract(amount));
        frozenAmounts.put(accountId, currentFrozen.subtract(amount));

        System.out.println("扣款成功: 账户=" + accountId + ", 金额=" + amount + ", 余额=" + accounts.get(accountId));
        return true;
    }

    /**
     * Cancel扣款：释放冻结金额
     */
    private boolean cancelDebit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        BigDecimal currentFrozen = frozenAmounts.getOrDefault(accountId, BigDecimal.ZERO);

        if (currentFrozen.compareTo(amount) >= 0) {
            frozenAmounts.put(accountId, currentFrozen.subtract(amount));
            System.out.println("释放冻结金额: 账户=" + accountId + ", 金额=" + amount);
        } else {
            System.err.println("冻结金额不足，无法释放: 账户=" + accountId + ", 冻结=" + currentFrozen + ", 释放=" + amount);
        }

        return true; // Cancel操作通常不会失败
    }

    /**
     * Try存款：预留存款记录
     */
    private boolean tryCredit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        // 存款的Try阶段只需要验证参数
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            System.err.println("存款金额必须大于0: " + amount);
            return false;
        }

        if (accounts.get(accountId) == null) {
            System.err.println("账户不存在: " + accountId);
            return false;
        }

        context.setAttribute("credit_amount", amount);
        context.setAttribute("account_id", accountId);

        System.out.println("存款Try成功: 账户=" + accountId + ", 金额=" + amount);
        return true;
    }

    /**
     * Confirm存款：执行真正的存款
     */
    private boolean confirmCredit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        BigDecimal currentBalance = accounts.get(accountId);
        if (currentBalance == null) {
            System.err.println("Confirm存款失败: 账户不存在");
            return false;
        }

        accounts.put(accountId, currentBalance.add(amount));
        System.out.println("存款成功: 账户=" + accountId + ", 金额=" + amount + ", 余额=" + accounts.get(accountId));
        return true;
    }

    /**
     * Cancel存款：取消存款操作
     */
    private boolean cancelCredit(TCCTransactionContext context, String accountId, BigDecimal amount) {
        // 存款的Cancel阶段什么都不用做，因为Try阶段没有实际改变状态
        System.out.println("取消存款: 账户=" + accountId + ", 金额=" + amount);
        return true;
    }

    /**
     * 获取账户余额
     */
    public BigDecimal getBalance(String accountId) {
        return accounts.getOrDefault(accountId, BigDecimal.ZERO);
    }

    /**
     * 获取冻结金额
     */
    public BigDecimal getFrozenAmount(String accountId) {
        return frozenAmounts.getOrDefault(accountId, BigDecimal.ZERO);
    }

    /**
     * 获取可用余额
     */
    public BigDecimal getAvailableBalance(String accountId) {
        BigDecimal balance = getBalance(accountId);
        BigDecimal frozen = getFrozenAmount(accountId);
        return balance.subtract(frozen);
    }

    @Override
    public String getParticipantId() {
        return participantId;
    }

    /**
     * 打印账户状态
     */
    public void printAccountStatus() {
        System.out.println("\n=== 账户状态 ===");
        for (Map.Entry<String, BigDecimal> entry : accounts.entrySet()) {
            String accountId = entry.getKey();
            BigDecimal balance = entry.getValue();
            BigDecimal frozen = frozenAmounts.getOrDefault(accountId, BigDecimal.ZERO);
            BigDecimal available = balance.subtract(frozen);

            System.out.println("账户: " + accountId +
                             ", 余额: " + balance +
                             ", 冻结: " + frozen +
                             ", 可用: " + available);
        }
        System.out.println("===============\n");
    }
}
```

### 4.2 库存服务TCC实现

```java
/**
 * 库存服务TCC参与者
 */
public class InventoryServiceTCC implements TCCParticipant {
    private final String participantId = "inventory-service";

    // 模拟库存数据存储
    private final Map<String, Integer> inventory = new ConcurrentHashMap<>();
    private final Map<String, Integer> reservedInventory = new ConcurrentHashMap<>();

    public InventoryServiceTCC() {
        // 初始化一些测试商品库存
        inventory.put("product001", 100);
        inventory.put("product002", 50);
        inventory.put("product003", 200);
    }

    @Override
    public boolean tryExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String productId = (String) args[1];
            Integer quantity = (Integer) args[2];

            System.out.println("库存服务Try: " + operation + ", 商品=" + productId + ", 数量=" + quantity);

            switch (operation) {
                case "RESERVE":
                    return tryReserve(context, productId, quantity);
                case "RELEASE":
                    return tryRelease(context, productId, quantity);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("库存服务Try异常: " + e.getMessage());
            return false;
        }
    }

    @Override
    public boolean confirmExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String productId = (String) args[1];
            Integer quantity = (Integer) args[2];

            System.out.println("库存服务Confirm: " + operation + ", 商品=" + productId + ", 数量=" + quantity);

            switch (operation) {
                case "RESERVE":
                    return confirmReserve(context, productId, quantity);
                case "RELEASE":
                    return confirmRelease(context, productId, quantity);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("库存服务Confirm异常: " + e.getMessage());
            return false;
        }
    }

    @Override
    public boolean cancelExecute(TCCTransactionContext context, Object... args) {
        try {
            String operation = (String) args[0];
            String productId = (String) args[1];
            Integer quantity = (Integer) args[2];

            System.out.println("库存服务Cancel: " + operation + ", 商品=" + productId + ", 数量=" + quantity);

            switch (operation) {
                case "RESERVE":
                    return cancelReserve(context, productId, quantity);
                case "RELEASE":
                    return cancelRelease(context, productId, quantity);
                default:
                    System.err.println("不支持的操作: " + operation);
                    return false;
            }

        } catch (Exception e) {
            System.err.println("库存服务Cancel异常: " + e.getMessage());
            return false;
        }
    }

    /**
     * Try预留库存：预留指定数量的库存
     */
    private boolean tryReserve(TCCTransactionContext context, String productId, Integer quantity) {
        Integer currentInventory = inventory.get(productId);
        if (currentInventory == null) {
            System.err.println("商品不存在: " + productId);
            return false;
        }

        Integer currentReserved = reservedInventory.getOrDefault(productId, 0);
        Integer availableInventory = currentInventory - currentReserved;

        if (availableInventory < quantity) {
            System.err.println("库存不足: 可用=" + availableInventory + ", 需要=" + quantity);
            return false;
        }

        // 预留库存
        reservedInventory.put(productId, currentReserved + quantity);

        // 在上下文中记录预留信息
        context.setAttribute("reserved_quantity", quantity);
        context.setAttribute("product_id", productId);

        System.out.println("预留库存成功: 商品=" + productId + ", 数量=" + quantity);
        return true;
    }

    /**
     * Confirm预留库存：真正扣减库存
     */
    private boolean confirmReserve(TCCTransactionContext context, String productId, Integer quantity) {
        Integer currentInventory = inventory.get(productId);
        Integer currentReserved = reservedInventory.getOrDefault(productId, 0);

        if (currentInventory == null || currentReserved < quantity) {
            System.err.println("Confirm预留失败: 库存状态异常");
            return false;
        }

        // 扣减库存
        inventory.put(productId, currentInventory - quantity);
        reservedInventory.put(productId, currentReserved - quantity);

        System.out.println("扣减库存成功: 商品=" + productId + ", 数量=" + quantity + ", 剩余=" + inventory.get(productId));
        return true;
    }

    /**
     * Cancel预留库存：释放预留的库存
     */
    private boolean cancelReserve(TCCTransactionContext context, String productId, Integer quantity) {
        Integer currentReserved = reservedInventory.getOrDefault(productId, 0);

        if (currentReserved >= quantity) {
            reservedInventory.put(productId, currentReserved - quantity);
            System.out.println("释放预留库存: 商品=" + productId + ", 数量=" + quantity);
        } else {
            System.err.println("预留库存不足，无法释放: 商品=" + productId + ", 预留=" + currentReserved + ", 释放=" + quantity);
        }

        return true; // Cancel操作通常不会失败
    }

    /**
     * Try释放库存：验证释放操作
     */
    private boolean tryRelease(TCCTransactionContext context, String productId, Integer quantity) {
        if (quantity <= 0) {
            System.err.println("释放数量必须大于0: " + quantity);
            return false;
        }

        if (inventory.get(productId) == null) {
            System.err.println("商品不存在: " + productId);
            return false;
        }

        context.setAttribute("release_quantity", quantity);
        context.setAttribute("product_id", productId);

        System.out.println("释放库存Try成功: 商品=" + productId + ", 数量=" + quantity);
        return true;
    }

    /**
     * Confirm释放库存：真正增加库存
     */
    private boolean confirmRelease(TCCTransactionContext context, String productId, Integer quantity) {
        Integer currentInventory = inventory.get(productId);
        if (currentInventory == null) {
            System.err.println("Confirm释放失败: 商品不存在");
            return false;
        }

        inventory.put(productId, currentInventory + quantity);
        System.out.println("释放库存成功: 商品=" + productId + ", 数量=" + quantity + ", 库存=" + inventory.get(productId));
        return true;
    }

    /**
     * Cancel释放库存：取消释放操作
     */
    private boolean cancelRelease(TCCTransactionContext context, String productId, Integer quantity) {
        // 释放的Cancel阶段什么都不用做，因为Try阶段没有实际改变状态
        System.out.println("取消释放库存: 商品=" + productId + ", 数量=" + quantity);
        return true;
    }

    /**
     * 获取库存数量
     */
    public Integer getInventory(String productId) {
        return inventory.getOrDefault(productId, 0);
    }

    /**
     * 获取预留数量
     */
    public Integer getReservedQuantity(String productId) {
        return reservedInventory.getOrDefault(productId, 0);
    }

    /**
     * 获取可用库存
     */
    public Integer getAvailableInventory(String productId) {
        Integer total = getInventory(productId);
        Integer reserved = getReservedQuantity(productId);
        return total - reserved;
    }

    @Override
    public String getParticipantId() {
        return participantId;
    }

    /**
     * 打印库存状态
     */
    public void printInventoryStatus() {
        System.out.println("\n=== 库存状态 ===");
        for (Map.Entry<String, Integer> entry : inventory.entrySet()) {
            String productId = entry.getKey();
            Integer total = entry.getValue();
            Integer reserved = reservedInventory.getOrDefault(productId, 0);
            Integer available = total - reserved;

            System.out.println("商品: " + productId +
                             ", 总库存: " + total +
                             ", 预留: " + reserved +
                             ", 可用: " + available);
        }
        System.out.println("===============\n");
    }
}
```

## 5. TCC应用层封装

### 5.1 订单服务示例

```java
/**
 * 订单服务，演示TCC模式的应用
 */
public class OrderService {
    private final TCCTransactionManager tccManager;
    private final AccountServiceTCC accountService;
    private final InventoryServiceTCC inventoryService;

    public OrderService(TCCTransactionManager tccManager,
                       AccountServiceTCC accountService,
                       InventoryServiceTCC inventoryService) {
        this.tccManager = tccManager;
        this.accountService = accountService;
        this.inventoryService = inventoryService;
    }

    /**
     * 创建订单（使用TCC模式）
     */
    public boolean createOrder(OrderRequest orderRequest) {
        String transactionId = null;

        try {
            // 开始TCC全局事务
            transactionId = tccManager.beginGlobalTransaction(60000); // 60秒超时

            System.out.println("开始处理订单: " + orderRequest);

            // 第一步：扣款
            tccManager.enlistParticipant(transactionId, "account-service",
                    "DEBIT", orderRequest.getAccountId(), orderRequest.getTotalAmount());

            // 第二步：扣减库存
            for (OrderItem item : orderRequest.getItems()) {
                tccManager.enlistParticipant(transactionId, "inventory-service",
                        "RESERVE", item.getProductId(), item.getQuantity());
            }

            // 所有Try操作成功，提交事务
            tccManager.commitGlobalTransaction(transactionId);

            System.out.println("订单创建成功: " + orderRequest.getOrderId());
            return true;

        } catch (TCCException e) {
            System.err.println("订单创建失败: " + e.getMessage());

            if (transactionId != null) {
                try {
                    tccManager.rollbackGlobalTransaction(transactionId);
                } catch (TCCException rollbackEx) {
                    System.err.println("回滚失败: " + rollbackEx.getMessage());
                }
            }

            return false;
        }
    }

    /**
     * 退款订单（使用TCC模式）
     */
    public boolean refundOrder(RefundRequest refundRequest) {
        String transactionId = null;

        try {
            // 开始TCC全局事务
            transactionId = tccManager.beginGlobalTransaction(60000);

            System.out.println("开始处理退款: " + refundRequest);

            // 第一步：退款
            tccManager.enlistParticipant(transactionId, "account-service",
                    "CREDIT", refundRequest.getAccountId(), refundRequest.getRefundAmount());

            // 第二步：恢复库存
            for (RefundItem item : refundRequest.getItems()) {
                tccManager.enlistParticipant(transactionId, "inventory-service",
                        "RELEASE", item.getProductId(), item.getQuantity());
            }

            // 所有Try操作成功，提交事务
            tccManager.commitGlobalTransaction(transactionId);

            System.out.println("退款处理成功: " + refundRequest.getOrderId());
            return true;

        } catch (TCCException e) {
            System.err.println("退款处理失败: " + e.getMessage());

            if (transactionId != null) {
                try {
                    tccManager.rollbackGlobalTransaction(transactionId);
                } catch (TCCException rollbackEx) {
                    System.err.println("回滚失败: " + rollbackEx.getMessage());
                }
            }

            return false;
        }
    }

    /**
     * 转账操作（使用TCC模式）
     */
    public boolean transfer(String fromAccount, String toAccount, BigDecimal amount) {
        String transactionId = null;

        try {
            // 开始TCC全局事务
            transactionId = tccManager.beginGlobalTransaction(30000);

            System.out.println("开始处理转账: " + fromAccount + " -> " + toAccount + ", 金额: " + amount);

            // 第一步：从源账户扣款
            tccManager.enlistParticipant(transactionId, "account-service",
                    "DEBIT", fromAccount, amount);

            // 第二步：向目标账户存款
            tccManager.enlistParticipant(transactionId, "account-service",
                    "CREDIT", toAccount, amount);

            // 所有Try操作成功，提交事务
            tccManager.commitGlobalTransaction(transactionId);

            System.out.println("转账成功: " + fromAccount + " -> " + toAccount + ", 金额: " + amount);
            return true;

        } catch (TCCException e) {
            System.err.println("转账失败: " + e.getMessage());

            if (transactionId != null) {
                try {
                    tccManager.rollbackGlobalTransaction(transactionId);
                } catch (TCCException rollbackEx) {
                    System.err.println("回滚失败: " + rollbackEx.getMessage());
                }
            }

            return false;
        }
    }
}

/**
 * 订单请求
 */
class OrderRequest {
    private final String orderId;
    private final String accountId;
    private final List<OrderItem> items;
    private final BigDecimal totalAmount;

    public OrderRequest(String orderId, String accountId, List<OrderItem> items, BigDecimal totalAmount) {
        this.orderId = orderId;
        this.accountId = accountId;
        this.items = new ArrayList<>(items);
        this.totalAmount = totalAmount;
    }

    // Getters
    public String getOrderId() { return orderId; }
    public String getAccountId() { return accountId; }
    public List<OrderItem> getItems() { return new ArrayList<>(items); }
    public BigDecimal getTotalAmount() { return totalAmount; }

    @Override
    public String toString() {
        return String.format("OrderRequest{orderId='%s', accountId='%s', items=%d, total=%s}",
                orderId, accountId, items.size(), totalAmount);
    }
}

/**
 * 订单项
 */
class OrderItem {
    private final String productId;
    private final Integer quantity;
    private final BigDecimal price;

    public OrderItem(String productId, Integer quantity, BigDecimal price) {
        this.productId = productId;
        this.quantity = quantity;
        this.price = price;
    }

    // Getters
    public String getProductId() { return productId; }
    public Integer getQuantity() { return quantity; }
    public BigDecimal getPrice() { return price; }

    @Override
    public String toString() {
        return String.format("OrderItem{productId='%s', quantity=%d, price=%s}",
                productId, quantity, price);
    }
}

/**
 * 退款请求
 */
class RefundRequest {
    private final String orderId;
    private final String accountId;
    private final List<RefundItem> items;
    private final BigDecimal refundAmount;

    public RefundRequest(String orderId, String accountId, List<RefundItem> items, BigDecimal refundAmount) {
        this.orderId = orderId;
        this.accountId = accountId;
        this.items = new ArrayList<>(items);
        this.refundAmount = refundAmount;
    }

    // Getters
    public String getOrderId() { return orderId; }
    public String getAccountId() { return accountId; }
    public List<RefundItem> getItems() { return new ArrayList<>(items); }
    public BigDecimal getRefundAmount() { return refundAmount; }

    @Override
    public String toString() {
        return String.format("RefundRequest{orderId='%s', accountId='%s', items=%d, refund=%s}",
                orderId, accountId, items.size(), refundAmount);
    }
}

/**
 * 退款项
 */
class RefundItem {
    private final String productId;
    private final Integer quantity;

    public RefundItem(String productId, Integer quantity) {
        this.productId = productId;
        this.quantity = quantity;
    }

    // Getters
    public String getProductId() { return productId; }
    public Integer getQuantity() { return quantity; }

    @Override
    public String toString() {
        return String.format("RefundItem{productId='%s', quantity=%d}", productId, quantity);
    }
}
```

## 6. 完整测试示例

### 6.1 TCC事务测试

```java
/**
 * TCC分布式事务综合测试
 */
public class TCCTransactionTest {

    public static void main(String[] args) throws Exception {
        testTCCTransaction();
    }

    /**
     * 测试TCC事务
     */
    private static void testTCCTransaction() throws Exception {
        System.out.println("=== TCC分布式事务测试开始 ===\n");

        // 创建TCC事务管理器
        TCCTransactionManager tccManager = new TCCTransactionManager("test-node");

        // 创建业务服务
        AccountServiceTCC accountService = new AccountServiceTCC();
        InventoryServiceTCC inventoryService = new InventoryServiceTCC();

        // 注册参与者
        tccManager.registerParticipant(accountService);
        tccManager.registerParticipant(inventoryService);

        // 创建订单服务
        OrderService orderService = new OrderService(tccManager, accountService, inventoryService);

        try {
            // 打印初始状态
            printInitialStatus(accountService, inventoryService);

            // 测试成功的订单创建
            testSuccessfulOrder(orderService, accountService, inventoryService);

            // 测试失败的订单创建（余额不足）
            testFailedOrderInsufficientBalance(orderService, accountService, inventoryService);

            // 测试失败的订单创建（库存不足）
            testFailedOrderInsufficientInventory(orderService, accountService, inventoryService);

            // 测试转账功能
            testTransfer(orderService, accountService);

            // 测试退款功能
            testRefund(orderService, accountService, inventoryService);

            // 测试并发事务
            testConcurrentTransactions(tccManager, accountService, inventoryService);

            // 性能测试
            performanceTest(tccManager, accountService, inventoryService);

        } finally {
            tccManager.shutdown();
        }

        System.out.println("\n=== TCC分布式事务测试完成 ===");
    }

    /**
     * 打印初始状态
     */
    private static void printInitialStatus(AccountServiceTCC accountService, InventoryServiceTCC inventoryService) {
        System.out.println("=== 初始状态 ===");
        accountService.printAccountStatus();
        inventoryService.printInventoryStatus();
    }

    /**
     * 测试成功的订单创建
     */
    private static void testSuccessfulOrder(OrderService orderService,
                                          AccountServiceTCC accountService,
                                          InventoryServiceTCC inventoryService) {
        System.out.println("=== 测试成功的订单创建 ===");

        List<OrderItem> items = Arrays.asList(
                new OrderItem("product001", 2, new BigDecimal("50.00")),
                new OrderItem("product002", 1, new BigDecimal("30.00"))
        );

        OrderRequest orderRequest = new OrderRequest("order001", "user001", items, new BigDecimal("130.00"));

        boolean result = orderService.createOrder(orderRequest);
        System.out.println("订单创建结果: " + (result ? "成功" : "失败"));

        // 验证状态变化
        accountService.printAccountStatus();
        inventoryService.printInventoryStatus();
    }

    /**
     * 测试余额不足的订单创建
     */
    private static void testFailedOrderInsufficientBalance(OrderService orderService,
                                                         AccountServiceTCC accountService,
                                                         InventoryServiceTCC inventoryService) {
        System.out.println("=== 测试余额不足的订单创建 ===");

        List<OrderItem> items = Arrays.asList(
                new OrderItem("product001", 5, new BigDecimal("200.00"))
        );

        OrderRequest orderRequest = new OrderRequest("order002", "user001", items, new BigDecimal("1000.00"));

        boolean result = orderService.createOrder(orderRequest);
        System.out.println("订单创建结果: " + (result ? "成功" : "失败"));

        // 验证状态未变化
        accountService.printAccountStatus();
        inventoryService.printInventoryStatus();
    }

    /**
     * 测试库存不足的订单创建
     */
    private static void testFailedOrderInsufficientInventory(OrderService orderService,
                                                           AccountServiceTCC accountService,
                                                           InventoryServiceTCC inventoryService) {
        System.out.println("=== 测试库存不足的订单创建 ===");

        List<OrderItem> items = Arrays.asList(
                new OrderItem("product002", 100, new BigDecimal("10.00"))
        );

        OrderRequest orderRequest = new OrderRequest("order003", "user002", items, new BigDecimal("100.00"));

        boolean result = orderService.createOrder(orderRequest);
        System.out.println("订单创建结果: " + (result ? "成功" : "失败"));

        // 验证状态未变化
        accountService.printAccountStatus();
        inventoryService.printInventoryStatus();
    }

    /**
     * 测试转账功能
     */
    private static void testTransfer(OrderService orderService, AccountServiceTCC accountService) {
        System.out.println("=== 测试转账功能 ===");

        boolean result = orderService.transfer("user002", "user003", new BigDecimal("100.00"));
        System.out.println("转账结果: " + (result ? "成功" : "失败"));

        accountService.printAccountStatus();
    }

    /**
     * 测试退款功能
     */
    private static void testRefund(OrderService orderService,
                                 AccountServiceTCC accountService,
                                 InventoryServiceTCC inventoryService) {
        System.out.println("=== 测试退款功能 ===");

        List<RefundItem> items = Arrays.asList(
                new RefundItem("product001", 1),
                new RefundItem("product002", 1)
        );

        RefundRequest refundRequest = new RefundRequest("order001", "user001", items, new BigDecimal("80.00"));

        boolean result = orderService.refundOrder(refundRequest);
        System.out.println("退款结果: " + (result ? "成功" : "失败"));

        accountService.printAccountStatus();
        inventoryService.printInventoryStatus();
    }

    /**
     * 测试并发事务
     */
    private static void testConcurrentTransactions(TCCTransactionManager tccManager,
                                                 AccountServiceTCC accountService,
                                                 InventoryServiceTCC inventoryService) throws Exception {
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
                    String transactionId = tccManager.beginGlobalTransaction();

                    // 执行转账操作
                    tccManager.enlistParticipant(transactionId, "account-service",
                            "DEBIT", "user003", new BigDecimal("10.00"));
                    tccManager.enlistParticipant(transactionId, "account-service",
                            "CREDIT", "user001", new BigDecimal("10.00"));

                    tccManager.commitGlobalTransaction(transactionId);
                    successCount.incrementAndGet();

                    System.out.println("并发事务 " + threadId + " 成功");

                } catch (Exception e) {
                    failureCount.incrementAndGet();
                    System.err.println("并发事务 " + threadId + " 失败: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();

        System.out.println("并发事务结果 - 成功: " + successCount.get() + ", 失败: " + failureCount.get());

        accountService.printAccountStatus();
    }

    /**
     * 性能测试
     */
    private static void performanceTest(TCCTransactionManager tccManager,
                                      AccountServiceTCC accountService,
                                      InventoryServiceTCC inventoryService) throws Exception {
        System.out.println("=== 性能测试 ===");

        int testCount = 100;
        long startTime = System.currentTimeMillis();

        for (int i = 0; i < testCount; i++) {
            try {
                String transactionId = tccManager.beginGlobalTransaction();

                // 执行简单的转账操作
                tccManager.enlistParticipant(transactionId, "account-service",
                        "DEBIT", "user001", new BigDecimal("1.00"));
                tccManager.enlistParticipant(transactionId, "account-service",
                        "CREDIT", "user002", new BigDecimal("1.00"));

                tccManager.commitGlobalTransaction(transactionId);

            } catch (Exception e) {
                System.err.println("性能测试事务失败: " + e.getMessage());
            }
        }

        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;

        System.out.println("性能测试结果:");
        System.out.println("事务数量: " + testCount);
        System.out.println("总耗时: " + duration + "ms");
        System.out.println("平均耗时: " + (duration / (double) testCount) + "ms/事务");
        System.out.println("吞吐量: " + (testCount * 1000.0 / duration) + " 事务/秒");

        // 打印TCC管理器统计信息
        System.out.println("TCC管理器统计: " + tccManager.getStats());
    }

    /**
     * 异常恢复测试
     */
    private static void testExceptionRecovery() {
        System.out.println("=== 异常恢复测试 ===");

        // 模拟各种异常情况
        // 1. Try阶段部分失败
        // 2. Confirm阶段部分失败
        // 3. Cancel阶段部分失败
        // 4. 网络异常
        // 5. 超时处理

        System.out.println("异常恢复测试完成");
    }
}
```

## 7. 总结

TCC（Try-Confirm-Cancel）模式是一种重要的分布式事务解决方案，具有以下特点：

### 7.1 核心优势
- **业务层控制**：事务逻辑由业务代码控制，灵活性高
- **资源预留**：Try阶段预留而非锁定资源，减少锁时间
- **补偿机制**：通过Cancel实现业务级别的回滚
- **性能较好**：相比2PC减少了锁定时间，提高并发性

### 7.2 关键机制
- **三阶段协议**：Try-Confirm-Cancel三个阶段
- **幂等性**：Confirm和Cancel操作必须幂等
- **资源预留**：Try阶段预留业务资源
- **补偿逻辑**：Cancel阶段实现业务补偿

### 7.3 应用场景
- **电商订单**：涉及账户扣款和库存扣减
- **金融转账**：跨账户的资金转移
- **积分兑换**：积分扣减和奖品发放
- **预约系统**：资源预留和确认机制

### 7.4 实现要点
- **幂等设计**：所有操作必须支持重复执行
- **状态管理**：需要记录和管理资源状态
- **异常处理**：完善的异常恢复机制
- **监控告警**：及时发现和处理异常事务

### 7.5 与其他方案比较
- **vs 2PC**：减少锁定时间，提高性能
- **vs Saga**：更适合短时间事务，一致性更强
- **vs 本地消息表**：实时性更好，但复杂度更高
- **vs 最终一致性**：强一致性保证，但实现复杂

### 7.6 最佳实践
- **合理设计Try操作**：预留而非锁定资源
- **确保操作幂等**：支持重复执行
- **完善补偿逻辑**：Cancel操作必须可靠
- **监控和告警**：及时发现异常事务
- **渐进式改造**：从简单场景开始应用

通过本文的详细实现，你可以深入理解TCC模式的工作原理和实现细节，为构建高可靠的分布式事务系统提供坚实的技术基础。