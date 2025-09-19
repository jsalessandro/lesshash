---
title: "分布式系统核心算法详解：PBFT算法原理与Java实现"
date: 2024-12-19T11:00:00+08:00
draft: false
tags: ["分布式系统", "PBFT算法", "拜占庭容错", "共识算法", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入解析PBFT算法的工作原理、三阶段共识协议以及在区块链和分布式系统中的应用实践，包含完整的Java实现代码"
---

## 1. PBFT算法概述

PBFT（Practical Byzantine Fault Tolerance）算法是一种实用的拜占庭容错算法，由Barbara Liskov和Miguel Castro在1999年提出。该算法可以在异步网络环境中容忍最多1/3的拜占庭故障节点，是第一个将拜占庭容错的复杂度降低到多项式时间的实用算法。

### 1.1 核心特点

- **拜占庭容错**：能容忍恶意节点的任意行为
- **异步网络**：不依赖同步假设，适用于互联网环境
- **高效性**：复杂度为O(n²)，相比传统算法大幅优化
- **确定性**：达成的共识具有最终性，不会回滚

### 1.2 算法约束

```
安全性约束：
- 需要至少 3f+1 个节点来容忍 f 个拜占庭故障节点
- 诚实节点数量必须严格大于 2/3

网络假设：
- 消息最终会被传递（异步网络）
- 节点具有数字签名能力
- 存在最大消息延迟上界（但实际运行时不需要知道）
```

## 2. PBFT三阶段协议

PBFT算法采用三阶段协议来达成共识：

### 2.1 协议阶段图解

#### 序列图

| 步骤 | 参与者 | 动作 | 目标 | 说明 |
|------|--------|------|------|------|
| 1 | C | 发送 | P | 1. Request |
| 2 | P | 发送 | B1 | 2. Pre-prepare |
| 3 | P | 发送 | B2 | 2. Pre-prepare |
| 4 | P | 发送 | B3 | 2. Pre-prepare |
| 5 | B1 | 发送 | B2 | 3. Prepare |
| 6 | B1 | 发送 | B3 | 3. Prepare |
| 7 | B2 | 发送 | B1 | 3. Prepare |
| 8 | B2 | 发送 | B3 | 3. Prepare |
| 9 | B3 | 发送 | B1 | 3. Prepare |
| 10 | B3 | 发送 | B2 | 3. Prepare |
| 11 | B1 | 发送 | B2 | 4. Commit |
| 12 | B1 | 发送 | B3 | 4. Commit |
| 13 | B2 | 发送 | B1 | 4. Commit |
| 14 | B2 | 发送 | B3 | 4. Commit |
| 15 | B3 | 发送 | B1 | 4. Commit |
| 16 | B3 | 发送 | B2 | 4. Commit |
| 17 | P | 发送 | C | 5. Reply |
| 18 | B1 | 发送 | C | 5. Reply |


### 2.2 三阶段详解

1. **Pre-prepare阶段**：主节点为请求分配序列号并广播
2. **Prepare阶段**：备份节点验证并广播Prepare消息
3. **Commit阶段**：节点收集足够消息后广播Commit，最终执行

## 3. PBFT核心数据结构

### 3.1 消息定义

```java
import java.io.Serializable;
import java.security.*;
import java.util.*;

/**
 * PBFT消息基类
 */
public abstract class PBFTMessage implements Serializable {
    protected final int view;           // 视图编号
    protected final int sequence;       // 序列号
    protected final String nodeId;      // 发送节点ID
    protected final long timestamp;     // 时间戳
    protected byte[] signature;         // 数字签名

    public PBFTMessage(int view, int sequence, String nodeId) {
        this.view = view;
        this.sequence = sequence;
        this.nodeId = nodeId;
        this.timestamp = System.currentTimeMillis();
    }

    // 签名消息
    public void sign(PrivateKey privateKey) throws Exception {
        Signature sig = Signature.getInstance("SHA256withRSA");
        sig.initSign(privateKey);
        sig.update(getMessageBytes());
        this.signature = sig.sign();
    }

    // 验证签名
    public boolean verify(PublicKey publicKey) throws Exception {
        if (signature == null) return false;

        Signature sig = Signature.getInstance("SHA256withRSA");
        sig.initVerify(publicKey);
        sig.update(getMessageBytes());
        return sig.verify(signature);
    }

    // 获取消息字节用于签名
    protected abstract byte[] getMessageBytes();

    // Getters
    public int getView() { return view; }
    public int getSequence() { return sequence; }
    public String getNodeId() { return nodeId; }
    public long getTimestamp() { return timestamp; }
    public byte[] getSignature() { return signature; }
}

/**
 * 客户端请求消息
 */
public class RequestMessage extends PBFTMessage {
    private final String operation;     // 操作内容
    private final String clientId;      // 客户端ID

    public RequestMessage(String operation, String clientId) {
        super(0, 0, clientId);
        this.operation = operation;
        this.clientId = clientId;
    }

    @Override
    protected byte[] getMessageBytes() {
        return (clientId + operation + timestamp).getBytes();
    }

    public String getOperation() { return operation; }
    public String getClientId() { return clientId; }
}

/**
 * Pre-prepare消息
 */
public class PrePrepareMessage extends PBFTMessage {
    private final RequestMessage request;
    private final String digest;        // 请求摘要

    public PrePrepareMessage(int view, int sequence, String nodeId, RequestMessage request) {
        super(view, sequence, nodeId);
        this.request = request;
        this.digest = calculateDigest(request);
    }

    private String calculateDigest(RequestMessage request) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(request.getOperation().getBytes());
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("计算摘要失败", e);
        }
    }

    @Override
    protected byte[] getMessageBytes() {
        return (view + ":" + sequence + ":" + nodeId + ":" + digest).getBytes();
    }

    public RequestMessage getRequest() { return request; }
    public String getDigest() { return digest; }
}

/**
 * Prepare消息
 */
public class PrepareMessage extends PBFTMessage {
    private final String digest;

    public PrepareMessage(int view, int sequence, String nodeId, String digest) {
        super(view, sequence, nodeId);
        this.digest = digest;
    }

    @Override
    protected byte[] getMessageBytes() {
        return (view + ":" + sequence + ":" + nodeId + ":" + digest).getBytes();
    }

    public String getDigest() { return digest; }
}

/**
 * Commit消息
 */
public class CommitMessage extends PBFTMessage {
    private final String digest;

    public CommitMessage(int view, int sequence, String nodeId, String digest) {
        super(view, sequence, nodeId);
        this.digest = digest;
    }

    @Override
    protected byte[] getMessageBytes() {
        return (view + ":" + sequence + ":" + nodeId + ":" + digest).getBytes();
    }

    public String getDigest() { return digest; }
}

/**
 * Reply消息
 */
public class ReplyMessage extends PBFTMessage {
    private final String result;
    private final String clientId;

    public ReplyMessage(int view, int sequence, String nodeId, String result, String clientId) {
        super(view, sequence, nodeId);
        this.result = result;
        this.clientId = clientId;
    }

    @Override
    protected byte[] getMessageBytes() {
        return (view + ":" + sequence + ":" + nodeId + ":" + result + ":" + clientId).getBytes();
    }

    public String getResult() { return result; }
    public String getClientId() { return clientId; }
}
```

### 3.2 节点状态管理

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * PBFT节点状态
 */
public class PBFTNodeState {
    private final String nodeId;
    private final AtomicInteger currentView = new AtomicInteger(0);
    private final AtomicInteger sequenceNumber = new AtomicInteger(0);
    private final AtomicInteger lastExecuted = new AtomicInteger(-1);

    // 消息日志
    private final Map<Integer, PrePrepareMessage> prePrepareLog = new ConcurrentHashMap<>();
    private final Map<String, Set<PrepareMessage>> prepareLog = new ConcurrentHashMap<>();
    private final Map<String, Set<CommitMessage>> commitLog = new ConcurrentHashMap<>();

    // 客户端请求追踪
    private final Map<String, RequestMessage> clientRequests = new ConcurrentHashMap<>();
    private final Map<String, ReplyMessage> clientReplies = new ConcurrentHashMap<>();

    // 节点管理
    private final Set<String> nodeList = ConcurrentHashMap.newKeySet();
    private final int faultTolerance;

    public PBFTNodeState(String nodeId, List<String> nodes) {
        this.nodeId = nodeId;
        this.nodeList.addAll(nodes);
        this.faultTolerance = (nodes.size() - 1) / 3;

        if (nodes.size() < 3 * faultTolerance + 1) {
            throw new IllegalArgumentException("节点数量不足以容忍 " + faultTolerance + " 个拜占庭故障");
        }
    }

    /**
     * 检查是否为主节点
     */
    public boolean isPrimary() {
        return isPrimary(currentView.get());
    }

    /**
     * 检查在指定视图中是否为主节点
     */
    public boolean isPrimary(int view) {
        List<String> sortedNodes = new ArrayList<>(nodeList);
        Collections.sort(sortedNodes);
        int primaryIndex = view % sortedNodes.size();
        return nodeId.equals(sortedNodes.get(primaryIndex));
    }

    /**
     * 获取主节点ID
     */
    public String getPrimary() {
        return getPrimary(currentView.get());
    }

    /**
     * 获取指定视图的主节点ID
     */
    public String getPrimary(int view) {
        List<String> sortedNodes = new ArrayList<>(nodeList);
        Collections.sort(sortedNodes);
        int primaryIndex = view % sortedNodes.size();
        return sortedNodes.get(primaryIndex);
    }

    /**
     * 添加Pre-prepare消息
     */
    public void addPrePrepare(PrePrepareMessage msg) {
        prePrepareLog.put(msg.getSequence(), msg);
    }

    /**
     * 添加Prepare消息
     */
    public void addPrepare(PrepareMessage msg) {
        String key = msg.getView() + ":" + msg.getSequence() + ":" + msg.getDigest();
        prepareLog.computeIfAbsent(key, k -> ConcurrentHashMap.newKeySet()).add(msg);
    }

    /**
     * 添加Commit消息
     */
    public void addCommit(CommitMessage msg) {
        String key = msg.getView() + ":" + msg.getSequence() + ":" + msg.getDigest();
        commitLog.computeIfAbsent(key, k -> ConcurrentHashMap.newKeySet()).add(msg);
    }

    /**
     * 检查是否已准备好（收到足够的Prepare消息）
     */
    public boolean isPrepared(int view, int sequence, String digest) {
        String key = view + ":" + sequence + ":" + digest;
        Set<PrepareMessage> prepares = prepareLog.get(key);
        return prepares != null && prepares.size() >= 2 * faultTolerance;
    }

    /**
     * 检查是否已提交准备好（收到足够的Commit消息）
     */
    public boolean isCommittedLocal(int view, int sequence, String digest) {
        String key = view + ":" + sequence + ":" + digest;
        Set<CommitMessage> commits = commitLog.get(key);
        return commits != null && commits.size() >= 2 * faultTolerance + 1;
    }

    /**
     * 检查消息是否已经处理过
     */
    public boolean isAlreadyProcessed(int sequence) {
        return sequence <= lastExecuted.get();
    }

    /**
     * 更新最后执行的序列号
     */
    public void updateLastExecuted(int sequence) {
        lastExecuted.set(Math.max(lastExecuted.get(), sequence));
    }

    /**
     * 获取下一个序列号
     */
    public int getNextSequenceNumber() {
        return sequenceNumber.incrementAndGet();
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public int getCurrentView() { return currentView.get(); }
    public int getLastExecuted() { return lastExecuted.get(); }
    public int getFaultTolerance() { return faultTolerance; }
    public int getNodeCount() { return nodeList.size(); }
    public Set<String> getNodeList() { return new HashSet<>(nodeList); }

    /**
     * 视图变更
     */
    public void changeView(int newView) {
        if (newView > currentView.get()) {
            currentView.set(newView);
            // 清理旧视图的消息
            cleanupOldViewMessages(newView);
        }
    }

    /**
     * 清理旧视图消息
     */
    private void cleanupOldViewMessages(int currentView) {
        // 清理prepare和commit日志中的旧视图消息
        prepareLog.entrySet().removeIf(entry -> {
            String[] parts = entry.getKey().split(":");
            return Integer.parseInt(parts[0]) < currentView;
        });

        commitLog.entrySet().removeIf(entry -> {
            String[] parts = entry.getKey().split(":");
            return Integer.parseInt(parts[0]) < currentView;
        });
    }
}
```

## 4. PBFT节点核心实现

### 4.1 PBFT节点主体

```java
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * PBFT节点实现
 */
public class PBFTNode {
    private final String nodeId;
    private final String address;
    private final int port;
    private final PBFTNodeState state;

    // 密钥管理
    private final KeyPair keyPair;
    private final Map<String, PublicKey> publicKeys = new ConcurrentHashMap<>();

    // 网络通信
    private ServerSocket serverSocket;
    private final ExecutorService networkExecutor = Executors.newCachedThreadPool();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

    // 运行状态
    private final AtomicBoolean running = new AtomicBoolean(false);

    // 状态机
    private final StateMachine stateMachine = new StateMachine();

    // 超时管理
    private final long requestTimeout = 10000; // 10秒
    private final Map<Integer, ScheduledFuture<?>> timeouts = new ConcurrentHashMap<>();

    public PBFTNode(String nodeId, String address, int port, List<String> allNodes) throws Exception {
        this.nodeId = nodeId;
        this.address = address;
        this.port = port;
        this.state = new PBFTNodeState(nodeId, allNodes);

        // 生成密钥对
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
        keyGen.initialize(2048);
        this.keyPair = keyGen.generateKeyPair();
    }

    /**
     * 启动节点
     */
    public void start() throws IOException {
        if (running.compareAndSet(false, true)) {
            serverSocket = new ServerSocket(port);
            networkExecutor.submit(this::acceptConnections);

            System.out.println("PBFT节点启动: " + nodeId + " 在 " + address + ":" + port);
            System.out.println("节点角色: " + (state.isPrimary() ? "主节点" : "备份节点"));
        }
    }

    /**
     * 停止节点
     */
    public void stop() throws IOException {
        if (running.compareAndSet(true, false)) {
            if (serverSocket != null) {
                serverSocket.close();
            }
            networkExecutor.shutdown();
            scheduler.shutdown();

            System.out.println("PBFT节点停止: " + nodeId);
        }
    }

    /**
     * 接受网络连接
     */
    private void acceptConnections() {
        while (running.get() && !serverSocket.isClosed()) {
            try {
                Socket clientSocket = serverSocket.accept();
                networkExecutor.submit(() -> handleConnection(clientSocket));
            } catch (IOException e) {
                if (running.get()) {
                    System.err.println("接受连接错误: " + e.getMessage());
                }
            }
        }
    }

    /**
     * 处理网络连接
     */
    private void handleConnection(Socket socket) {
        try (ObjectInputStream input = new ObjectInputStream(socket.getInputStream());
             ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream())) {

            Object message = input.readObject();

            if (message instanceof RequestMessage) {
                handleClientRequest((RequestMessage) message, output);
            } else if (message instanceof PrePrepareMessage) {
                handlePrePrepare((PrePrepareMessage) message);
            } else if (message instanceof PrepareMessage) {
                handlePrepare((PrepareMessage) message);
            } else if (message instanceof CommitMessage) {
                handleCommit((CommitMessage) message);
            }

        } catch (Exception e) {
            System.err.println("处理连接错误: " + e.getMessage());
        } finally {
            try {
                socket.close();
            } catch (IOException e) {
                // 忽略关闭错误
            }
        }
    }

    /**
     * 处理客户端请求
     */
    private void handleClientRequest(RequestMessage request, ObjectOutputStream output) throws Exception {
        System.out.println("收到客户端请求: " + request.getOperation());

        if (!state.isPrimary()) {
            // 非主节点，返回主节点信息
            output.writeObject("NOT_PRIMARY:" + state.getPrimary());
            return;
        }

        // 验证客户端请求（这里简化处理）
        if (!isValidRequest(request)) {
            output.writeObject("INVALID_REQUEST");
            return;
        }

        // 分配序列号
        int sequence = state.getNextSequenceNumber();

        // 创建Pre-prepare消息
        PrePrepareMessage prePrepare = new PrePrepareMessage(
            state.getCurrentView(), sequence, nodeId, request);
        prePrepare.sign(keyPair.getPrivate());

        // 保存到本地日志
        state.addPrePrepare(prePrepare);

        // 广播Pre-prepare消息
        broadcastMessage(prePrepare);

        // 设置超时
        scheduleTimeout(sequence);

        output.writeObject("REQUEST_ACCEPTED:" + sequence);
    }

    /**
     * 处理Pre-prepare消息
     */
    private void handlePrePrepare(PrePrepareMessage prePrepare) throws Exception {
        System.out.println("收到Pre-prepare: view=" + prePrepare.getView() +
                          ", seq=" + prePrepare.getSequence());

        // 验证消息
        if (!isValidPrePrepare(prePrepare)) {
            System.out.println("无效的Pre-prepare消息");
            return;
        }

        // 保存Pre-prepare消息
        state.addPrePrepare(prePrepare);

        // 发送Prepare消息
        PrepareMessage prepare = new PrepareMessage(
            prePrepare.getView(), prePrepare.getSequence(),
            nodeId, prePrepare.getDigest());
        prepare.sign(keyPair.getPrivate());

        // 保存自己的Prepare消息
        state.addPrepare(prepare);

        // 广播Prepare消息
        broadcastMessage(prepare);
    }

    /**
     * 处理Prepare消息
     */
    private void handlePrepare(PrepareMessage prepare) throws Exception {
        System.out.println("收到Prepare: view=" + prepare.getView() +
                          ", seq=" + prepare.getSequence() +
                          ", from=" + prepare.getNodeId());

        // 验证消息
        if (!isValidPrepare(prepare)) {
            System.out.println("无效的Prepare消息");
            return;
        }

        // 保存Prepare消息
        state.addPrepare(prepare);

        // 检查是否可以进入Commit阶段
        if (state.isPrepared(prepare.getView(), prepare.getSequence(), prepare.getDigest())) {
            // 发送Commit消息
            CommitMessage commit = new CommitMessage(
                prepare.getView(), prepare.getSequence(),
                nodeId, prepare.getDigest());
            commit.sign(keyPair.getPrivate());

            // 保存自己的Commit消息
            state.addCommit(commit);

            // 广播Commit消息
            broadcastMessage(commit);

            System.out.println("进入Commit阶段: seq=" + prepare.getSequence());
        }
    }

    /**
     * 处理Commit消息
     */
    private void handleCommit(CommitMessage commit) throws Exception {
        System.out.println("收到Commit: view=" + commit.getView() +
                          ", seq=" + commit.getSequence() +
                          ", from=" + commit.getNodeId());

        // 验证消息
        if (!isValidCommit(commit)) {
            System.out.println("无效的Commit消息");
            return;
        }

        // 保存Commit消息
        state.addCommit(commit);

        // 检查是否可以执行请求
        if (state.isCommittedLocal(commit.getView(), commit.getSequence(), commit.getDigest())) {
            executeRequest(commit.getSequence());
        }
    }

    /**
     * 执行请求
     */
    private void executeRequest(int sequence) {
        if (state.isAlreadyProcessed(sequence)) {
            return;
        }

        // 按序执行（简化实现，实际应该处理乱序情况）
        if (sequence == state.getLastExecuted() + 1) {
            PrePrepareMessage prePrepare = state.prePrepareLog.get(sequence);
            if (prePrepare != null) {
                RequestMessage request = prePrepare.getRequest();

                // 执行操作
                String result = stateMachine.execute(request.getOperation());

                // 更新状态
                state.updateLastExecuted(sequence);

                // 清理超时
                ScheduledFuture<?> timeout = timeouts.remove(sequence);
                if (timeout != null) {
                    timeout.cancel(false);
                }

                System.out.println("执行请求: seq=" + sequence +
                                  ", op=" + request.getOperation() +
                                  ", result=" + result);

                // 回复客户端（如果是主节点）
                if (state.isPrimary()) {
                    // 这里应该发送回复给客户端
                    // 简化实现中省略网络发送部分
                }
            }
        }
    }

    /**
     * 广播消息
     */
    private void broadcastMessage(PBFTMessage message) {
        for (String nodeId : state.getNodeList()) {
            if (!nodeId.equals(this.nodeId)) {
                networkExecutor.submit(() -> sendMessage(nodeId, message));
            }
        }
    }

    /**
     * 发送消息到指定节点
     */
    private void sendMessage(String targetNodeId, PBFTMessage message) {
        try {
            // 这里需要实现节点地址解析
            // 简化实现中假设节点ID包含地址信息
            String[] parts = targetNodeId.split(":");
            String targetAddress = parts.length > 1 ? parts[0] : "localhost";
            int targetPort = parts.length > 2 ? Integer.parseInt(parts[2]) : 8000;

            try (Socket socket = new Socket(targetAddress, targetPort);
                 ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream())) {

                output.writeObject(message);

            }
        } catch (Exception e) {
            System.err.println("发送消息到 " + targetNodeId + " 失败: " + e.getMessage());
        }
    }

    /**
     * 验证请求
     */
    private boolean isValidRequest(RequestMessage request) {
        // 简化验证逻辑
        return request.getOperation() != null && !request.getOperation().trim().isEmpty();
    }

    /**
     * 验证Pre-prepare消息
     */
    private boolean isValidPrePrepare(PrePrepareMessage prePrepare) {
        try {
            // 检查视图号
            if (prePrepare.getView() != state.getCurrentView()) {
                return false;
            }

            // 检查是否来自主节点
            if (!prePrepare.getNodeId().equals(state.getPrimary(prePrepare.getView()))) {
                return false;
            }

            // 验证签名
            PublicKey primaryKey = publicKeys.get(prePrepare.getNodeId());
            if (primaryKey != null && !prePrepare.verify(primaryKey)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            System.err.println("验证Pre-prepare消息失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 验证Prepare消息
     */
    private boolean isValidPrepare(PrepareMessage prepare) {
        try {
            // 检查视图号
            if (prepare.getView() != state.getCurrentView()) {
                return false;
            }

            // 验证签名
            PublicKey senderKey = publicKeys.get(prepare.getNodeId());
            if (senderKey != null && !prepare.verify(senderKey)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            System.err.println("验证Prepare消息失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 验证Commit消息
     */
    private boolean isValidCommit(CommitMessage commit) {
        try {
            // 检查视图号
            if (commit.getView() != state.getCurrentView()) {
                return false;
            }

            // 验证签名
            PublicKey senderKey = publicKeys.get(commit.getNodeId());
            if (senderKey != null && !commit.verify(senderKey)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            System.err.println("验证Commit消息失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 设置请求超时
     */
    private void scheduleTimeout(int sequence) {
        ScheduledFuture<?> timeout = scheduler.schedule(() -> {
            System.out.println("请求超时: seq=" + sequence);
            // 触发视图变更
            initiateViewChange();
        }, requestTimeout, TimeUnit.MILLISECONDS);

        timeouts.put(sequence, timeout);
    }

    /**
     * 发起视图变更
     */
    private void initiateViewChange() {
        // 简化的视图变更实现
        int newView = state.getCurrentView() + 1;
        System.out.println("发起视图变更: " + state.getCurrentView() + " -> " + newView);

        // 这里应该实现完整的视图变更协议
        // 包括VIEW-CHANGE和NEW-VIEW消息的处理
    }

    /**
     * 注册节点公钥
     */
    public void registerPublicKey(String nodeId, PublicKey publicKey) {
        publicKeys.put(nodeId, publicKey);
    }

    /**
     * 获取节点公钥
     */
    public PublicKey getPublicKey() {
        return keyPair.getPublic();
    }

    /**
     * 获取节点状态
     */
    public void printNodeStatus() {
        System.out.println("\n=== PBFT节点状态 ===");
        System.out.println("节点ID: " + nodeId);
        System.out.println("当前视图: " + state.getCurrentView());
        System.out.println("角色: " + (state.isPrimary() ? "主节点" : "备份节点"));
        System.out.println("最后执行序列号: " + state.getLastExecuted());
        System.out.println("容错能力: " + state.getFaultTolerance() + " 个拜占庭故障");
        System.out.println("集群大小: " + state.getNodeCount());
        System.out.println("================\n");
    }

    // Getters
    public String getNodeId() { return nodeId; }
    public boolean isRunning() { return running.get(); }
    public boolean isPrimary() { return state.isPrimary(); }
}

/**
 * 简单状态机实现
 */
class StateMachine {
    private final Map<String, String> state = new ConcurrentHashMap<>();
    private final AtomicInteger operationCount = new AtomicInteger(0);

    /**
     * 执行操作
     */
    public String execute(String operation) {
        operationCount.incrementAndGet();

        try {
            // 解析操作 (简化实现)
            String[] parts = operation.split("\\s+", 3);
            String command = parts[0].toUpperCase();

            switch (command) {
                case "SET":
                    if (parts.length >= 3) {
                        String key = parts[1];
                        String value = parts[2];
                        state.put(key, value);
                        return "OK";
                    }
                    return "ERROR: SET requires key and value";

                case "GET":
                    if (parts.length >= 2) {
                        String key = parts[1];
                        String value = state.get(key);
                        return value != null ? value : "NULL";
                    }
                    return "ERROR: GET requires key";

                case "DELETE":
                    if (parts.length >= 2) {
                        String key = parts[1];
                        String removed = state.remove(key);
                        return removed != null ? "OK" : "NOT_FOUND";
                    }
                    return "ERROR: DELETE requires key";

                default:
                    return "ERROR: Unknown command " + command;
            }

        } catch (Exception e) {
            return "ERROR: " + e.getMessage();
        }
    }

    /**
     * 获取状态机状态
     */
    public Map<String, String> getState() {
        return new HashMap<>(state);
    }

    /**
     * 获取操作计数
     */
    public int getOperationCount() {
        return operationCount.get();
    }
}
```

## 5. 视图变更协议

### 5.1 视图变更消息

```java
/**
 * View-Change消息
 */
public class ViewChangeMessage extends PBFTMessage {
    private final int newView;
    private final Set<PreparedProof> prepared;

    public ViewChangeMessage(int newView, String nodeId, Set<PreparedProof> prepared) {
        super(newView, 0, nodeId);
        this.newView = newView;
        this.prepared = prepared;
    }

    @Override
    protected byte[] getMessageBytes() {
        StringBuilder sb = new StringBuilder();
        sb.append(newView).append(":").append(nodeId);
        for (PreparedProof proof : prepared) {
            sb.append(":").append(proof.toString());
        }
        return sb.toString().getBytes();
    }

    public int getNewView() { return newView; }
    public Set<PreparedProof> getPrepared() { return prepared; }
}

/**
 * New-View消息
 */
public class NewViewMessage extends PBFTMessage {
    private final Set<ViewChangeMessage> viewChangeMessages;
    private final Set<PrePrepareMessage> prePrepareMessages;

    public NewViewMessage(int view, String nodeId,
                         Set<ViewChangeMessage> viewChangeMessages,
                         Set<PrePrepareMessage> prePrepareMessages) {
        super(view, 0, nodeId);
        this.viewChangeMessages = viewChangeMessages;
        this.prePrepareMessages = prePrepareMessages;
    }

    @Override
    protected byte[] getMessageBytes() {
        return (view + ":" + nodeId + ":" + viewChangeMessages.size() + ":" +
                prePrepareMessages.size()).getBytes();
    }

    public Set<ViewChangeMessage> getViewChangeMessages() { return viewChangeMessages; }
    public Set<PrePrepareMessage> getPrePrepareMessages() { return prePrepareMessages; }
}

/**
 * 准备证明
 */
class PreparedProof {
    private final int sequence;
    private final String digest;
    private final int view;
    private final Set<PrepareMessage> prepareMessages;

    public PreparedProof(int sequence, String digest, int view, Set<PrepareMessage> prepareMessages) {
        this.sequence = sequence;
        this.digest = digest;
        this.view = view;
        this.prepareMessages = prepareMessages;
    }

    // Getters
    public int getSequence() { return sequence; }
    public String getDigest() { return digest; }
    public int getView() { return view; }
    public Set<PrepareMessage> getPrepareMessages() { return prepareMessages; }

    @Override
    public String toString() {
        return sequence + ":" + digest + ":" + view;
    }
}
```

### 5.2 视图变更处理

```java
/**
 * 视图变更管理器
 */
public class ViewChangeManager {
    private final PBFTNode node;
    private final PBFTNodeState state;
    private final Map<Integer, Set<ViewChangeMessage>> viewChangeMessages = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    public ViewChangeManager(PBFTNode node, PBFTNodeState state) {
        this.node = node;
        this.state = state;
    }

    /**
     * 发起视图变更
     */
    public void initiateViewChange() {
        int newView = state.getCurrentView() + 1;
        System.out.println("节点 " + state.getNodeId() + " 发起视图变更: " +
                          state.getCurrentView() + " -> " + newView);

        // 收集已准备的证明
        Set<PreparedProof> prepared = collectPreparedProofs();

        // 创建View-Change消息
        ViewChangeMessage viewChange = new ViewChangeMessage(newView, state.getNodeId(), prepared);

        try {
            viewChange.sign(node.getKeyPair().getPrivate());
        } catch (Exception e) {
            System.err.println("签名View-Change消息失败: " + e.getMessage());
            return;
        }

        // 保存自己的View-Change消息
        viewChangeMessages.computeIfAbsent(newView, k -> ConcurrentHashMap.newKeySet()).add(viewChange);

        // 广播View-Change消息
        node.broadcastMessage(viewChange);

        // 设置超时，如果视图变更失败则重试
        scheduler.schedule(() -> {
            if (state.getCurrentView() < newView) {
                System.out.println("视图变更超时，重试...");
                initiateViewChange();
            }
        }, 10000, TimeUnit.MILLISECONDS);
    }

    /**
     * 处理View-Change消息
     */
    public void handleViewChange(ViewChangeMessage viewChange) {
        System.out.println("收到View-Change消息: view=" + viewChange.getNewView() +
                          ", from=" + viewChange.getNodeId());

        // 验证消息
        if (!isValidViewChange(viewChange)) {
            System.out.println("无效的View-Change消息");
            return;
        }

        // 保存View-Change消息
        viewChangeMessages.computeIfAbsent(viewChange.getNewView(),
            k -> ConcurrentHashMap.newKeySet()).add(viewChange);

        // 检查是否收到足够的View-Change消息
        int newView = viewChange.getNewView();
        Set<ViewChangeMessage> messages = viewChangeMessages.get(newView);

        if (messages != null && messages.size() >= 2 * state.getFaultTolerance() + 1) {
            // 如果是新视图的主节点，发送New-View消息
            if (state.isPrimary(newView)) {
                sendNewView(newView, messages);
            }
        }
    }

    /**
     * 发送New-View消息
     */
    private void sendNewView(int newView, Set<ViewChangeMessage> viewChangeMessages) {
        System.out.println("发送New-View消息: view=" + newView);

        // 计算需要重新提议的Pre-prepare消息
        Set<PrePrepareMessage> prePrepares = computeNewViewPrePrepares(viewChangeMessages);

        // 创建New-View消息
        NewViewMessage newViewMsg = new NewViewMessage(newView, state.getNodeId(),
                                                       viewChangeMessages, prePrepares);

        try {
            newViewMsg.sign(node.getKeyPair().getPrivate());
        } catch (Exception e) {
            System.err.println("签名New-View消息失败: " + e.getMessage());
            return;
        }

        // 广播New-View消息
        node.broadcastMessage(newViewMsg);

        // 更新本地视图
        state.changeView(newView);
    }

    /**
     * 处理New-View消息
     */
    public void handleNewView(NewViewMessage newView) {
        System.out.println("收到New-View消息: view=" + newView.getView() +
                          ", from=" + newView.getNodeId());

        // 验证消息
        if (!isValidNewView(newView)) {
            System.out.println("无效的New-View消息");
            return;
        }

        // 更新视图
        state.changeView(newView.getView());

        // 处理新的Pre-prepare消息
        for (PrePrepareMessage prePrepare : newView.getPrePrepareMessages()) {
            node.handlePrePrepare(prePrepare);
        }

        System.out.println("视图变更完成: " + newView.getView());
    }

    /**
     * 收集已准备的证明
     */
    private Set<PreparedProof> collectPreparedProofs() {
        Set<PreparedProof> proofs = new HashSet<>();

        // 这里需要从节点状态中收集已经准备好但未提交的请求
        // 简化实现中返回空集合

        return proofs;
    }

    /**
     * 计算新视图的Pre-prepare消息
     */
    private Set<PrePrepareMessage> computeNewViewPrePrepares(Set<ViewChangeMessage> viewChangeMessages) {
        Set<PrePrepareMessage> prePrepares = new HashSet<>();

        // 根据View-Change消息中的准备证明，重新构造Pre-prepare消息
        // 这是PBFT协议中较为复杂的部分，需要仔细处理
        // 简化实现中返回空集合

        return prePrepares;
    }

    /**
     * 验证View-Change消息
     */
    private boolean isValidViewChange(ViewChangeMessage viewChange) {
        try {
            // 检查新视图号
            if (viewChange.getNewView() <= state.getCurrentView()) {
                return false;
            }

            // 验证签名
            PublicKey senderKey = node.getPublicKeys().get(viewChange.getNodeId());
            if (senderKey != null && !viewChange.verify(senderKey)) {
                return false;
            }

            // 验证准备证明
            for (PreparedProof proof : viewChange.getPrepared()) {
                if (!isValidPreparedProof(proof)) {
                    return false;
                }
            }

            return true;

        } catch (Exception e) {
            System.err.println("验证View-Change消息失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 验证New-View消息
     */
    private boolean isValidNewView(NewViewMessage newView) {
        try {
            // 检查是否来自正确的主节点
            if (!newView.getNodeId().equals(state.getPrimary(newView.getView()))) {
                return false;
            }

            // 验证View-Change消息数量
            if (newView.getViewChangeMessages().size() < 2 * state.getFaultTolerance() + 1) {
                return false;
            }

            // 验证签名
            PublicKey primaryKey = node.getPublicKeys().get(newView.getNodeId());
            if (primaryKey != null && !newView.verify(primaryKey)) {
                return false;
            }

            return true;

        } catch (Exception e) {
            System.err.println("验证New-View消息失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 验证准备证明
     */
    private boolean isValidPreparedProof(PreparedProof proof) {
        // 检查Prepare消息数量
        if (proof.getPrepareMessages().size() < 2 * state.getFaultTolerance()) {
            return false;
        }

        // 验证所有Prepare消息
        for (PrepareMessage prepare : proof.getPrepareMessages()) {
            if (prepare.getView() != proof.getView() ||
                prepare.getSequence() != proof.getSequence() ||
                !prepare.getDigest().equals(proof.getDigest())) {
                return false;
            }
        }

        return true;
    }

    /**
     * 停止视图变更管理器
     */
    public void shutdown() {
        scheduler.shutdown();
    }
}
```

## 6. 性能优化和监控

### 6.1 批处理优化

```java
/**
 * PBFT批处理优化
 */
public class PBFTBatchProcessor {
    private final PBFTNode node;
    private final Queue<RequestMessage> pendingRequests = new ConcurrentLinkedQueue<>();
    private final int batchSize;
    private final long batchTimeout; // 毫秒
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    public PBFTBatchProcessor(PBFTNode node, int batchSize, long batchTimeout) {
        this.node = node;
        this.batchSize = batchSize;
        this.batchTimeout = batchTimeout;

        // 启动批处理定时器
        scheduler.scheduleAtFixedRate(this::processBatch, batchTimeout, batchTimeout, TimeUnit.MILLISECONDS);
    }

    /**
     * 添加请求到批次
     */
    public void addRequest(RequestMessage request) {
        pendingRequests.offer(request);

        // 如果达到批次大小，立即处理
        if (pendingRequests.size() >= batchSize) {
            processBatch();
        }
    }

    /**
     * 处理批次
     */
    private void processBatch() {
        if (pendingRequests.isEmpty()) {
            return;
        }

        List<RequestMessage> batch = new ArrayList<>();
        for (int i = 0; i < batchSize && !pendingRequests.isEmpty(); i++) {
            batch.add(pendingRequests.poll());
        }

        if (!batch.isEmpty()) {
            processBatchRequests(batch);
        }
    }

    /**
     * 处理批量请求
     */
    private void processBatchRequests(List<RequestMessage> requests) {
        // 创建批量请求消息
        BatchRequestMessage batchRequest = new BatchRequestMessage(requests);

        // 按照正常PBFT流程处理批量请求
        if (node.isPrimary()) {
            int sequence = node.getState().getNextSequenceNumber();

            PrePrepareMessage prePrepare = new PrePrepareMessage(
                node.getState().getCurrentView(), sequence, node.getNodeId(), batchRequest);

            try {
                prePrepare.sign(node.getKeyPair().getPrivate());
                node.getState().addPrePrepare(prePrepare);
                node.broadcastMessage(prePrepare);

                System.out.println("处理批量请求: " + requests.size() + " 个请求, seq=" + sequence);

            } catch (Exception e) {
                System.err.println("处理批量请求失败: " + e.getMessage());
            }
        }
    }

    /**
     * 停止批处理器
     */
    public void shutdown() {
        scheduler.shutdown();
    }
}

/**
 * 批量请求消息
 */
class BatchRequestMessage extends RequestMessage {
    private final List<RequestMessage> requests;

    public BatchRequestMessage(List<RequestMessage> requests) {
        super("BATCH", "system");
        this.requests = requests;
    }

    public List<RequestMessage> getRequests() {
        return requests;
    }

    @Override
    public String getOperation() {
        return "BATCH:" + requests.size();
    }
}
```

### 6.2 性能监控

```java
/**
 * PBFT性能监控器
 */
public class PBFTPerformanceMonitor {
    private final AtomicLong requestsProcessed = new AtomicLong(0);
    private final AtomicLong consensusRounds = new AtomicLong(0);
    private final AtomicLong viewChanges = new AtomicLong(0);
    private final AtomicLong messagesSent = new AtomicLong(0);
    private final AtomicLong messagesReceived = new AtomicLong(0);

    private final Map<Integer, Long> consensusLatency = new ConcurrentHashMap<>();
    private final ScheduledExecutorService reportScheduler = Executors.newSingleThreadScheduledExecutor();

    public PBFTPerformanceMonitor() {
        // 每30秒输出性能报告
        reportScheduler.scheduleAtFixedRate(this::printPerformanceReport,
            30, 30, TimeUnit.SECONDS);
    }

    /**
     * 记录请求处理
     */
    public void recordRequestProcessed() {
        requestsProcessed.incrementAndGet();
    }

    /**
     * 记录共识轮次
     */
    public void recordConsensusRound(int sequence, long latency) {
        consensusRounds.incrementAndGet();
        consensusLatency.put(sequence, latency);
    }

    /**
     * 记录视图变更
     */
    public void recordViewChange() {
        viewChanges.incrementAndGet();
    }

    /**
     * 记录消息发送
     */
    public void recordMessageSent() {
        messagesSent.incrementAndGet();
    }

    /**
     * 记录消息接收
     */
    public void recordMessageReceived() {
        messagesReceived.incrementAndGet();
    }

    /**
     * 打印性能报告
     */
    private void printPerformanceReport() {
        System.out.println("\n=== PBFT性能报告 ===");
        System.out.println("处理请求数: " + requestsProcessed.get());
        System.out.println("共识轮次数: " + consensusRounds.get());
        System.out.println("视图变更数: " + viewChanges.get());
        System.out.println("发送消息数: " + messagesSent.get());
        System.out.println("接收消息数: " + messagesReceived.get());

        if (!consensusLatency.isEmpty()) {
            double avgLatency = consensusLatency.values().stream()
                .mapToLong(Long::longValue)
                .average()
                .orElse(0.0);
            System.out.println("平均共识延迟: " + String.format("%.2f", avgLatency) + "ms");
        }

        long totalMessages = messagesSent.get() + messagesReceived.get();
        if (consensusRounds.get() > 0) {
            double messagesPerConsensus = (double) totalMessages / consensusRounds.get();
            System.out.println("每轮共识消息数: " + String.format("%.2f", messagesPerConsensus));
        }

        System.out.println("================\n");
    }

    /**
     * 获取性能指标
     */
    public PerformanceMetrics getMetrics() {
        double avgLatency = consensusLatency.isEmpty() ? 0 :
            consensusLatency.values().stream().mapToLong(Long::longValue).average().orElse(0.0);

        return new PerformanceMetrics(
            requestsProcessed.get(),
            consensusRounds.get(),
            viewChanges.get(),
            messagesSent.get(),
            messagesReceived.get(),
            avgLatency
        );
    }

    /**
     * 停止监控
     */
    public void shutdown() {
        reportScheduler.shutdown();
    }
}

/**
 * 性能指标
 */
class PerformanceMetrics {
    private final long requestsProcessed;
    private final long consensusRounds;
    private final long viewChanges;
    private final long messagesSent;
    private final long messagesReceived;
    private final double averageLatency;

    public PerformanceMetrics(long requestsProcessed, long consensusRounds, long viewChanges,
                            long messagesSent, long messagesReceived, double averageLatency) {
        this.requestsProcessed = requestsProcessed;
        this.consensusRounds = consensusRounds;
        this.viewChanges = viewChanges;
        this.messagesSent = messagesSent;
        this.messagesReceived = messagesReceived;
        this.averageLatency = averageLatency;
    }

    // Getters
    public long getRequestsProcessed() { return requestsProcessed; }
    public long getConsensusRounds() { return consensusRounds; }
    public long getViewChanges() { return viewChanges; }
    public long getMessagesSent() { return messagesSent; }
    public long getMessagesReceived() { return messagesReceived; }
    public double getAverageLatency() { return averageLatency; }

    @Override
    public String toString() {
        return String.format("PerformanceMetrics{处理请求=%d, 共识轮次=%d, 视图变更=%d, " +
                           "发送消息=%d, 接收消息=%d, 平均延迟=%.2fms}",
                           requestsProcessed, consensusRounds, viewChanges,
                           messagesSent, messagesReceived, averageLatency);
    }
}
```

## 7. 完整测试示例

### 7.1 PBFT集群测试

```java
/**
 * PBFT集群测试
 */
public class PBFTClusterTest {

    public static void main(String[] args) throws Exception {
        testPBFTCluster();
    }

    /**
     * 测试PBFT集群
     */
    private static void testPBFTCluster() throws Exception {
        System.out.println("=== 启动PBFT集群测试 ===\n");

        // 创建4个节点的PBFT集群（可以容忍1个拜占庭故障）
        List<PBFTNode> nodes = new ArrayList<>();
        List<String> nodeIds = Arrays.asList("node-0", "node-1", "node-2", "node-3");
        int basePort = 9000;

        // 创建并启动所有节点
        for (int i = 0; i < nodeIds.size(); i++) {
            String nodeId = nodeIds.get(i);
            PBFTNode node = new PBFTNode(nodeId, "localhost", basePort + i, nodeIds);
            node.start();
            nodes.add(node);

            Thread.sleep(500); // 等待节点启动
        }

        // 交换公钥（简化的密钥分发）
        for (int i = 0; i < nodes.size(); i++) {
            for (int j = 0; j < nodes.size(); j++) {
                if (i != j) {
                    nodes.get(i).registerPublicKey(nodeIds.get(j), nodes.get(j).getPublicKey());
                }
            }
        }

        Thread.sleep(2000);

        // 打印初始状态
        System.out.println("PBFT集群启动完成：");
        for (PBFTNode node : nodes) {
            node.printNodeStatus();
        }

        // 测试正常共识流程
        System.out.println("=== 测试正常共识流程 ===");
        testNormalConsensus(nodes);

        Thread.sleep(3000);

        // 测试并发请求
        System.out.println("=== 测试并发请求处理 ===");
        testConcurrentRequests(nodes);

        Thread.sleep(3000);

        // 模拟节点故障
        System.out.println("=== 模拟节点故障 ===");
        testNodeFailure(nodes);

        Thread.sleep(5000);

        // 测试视图变更
        System.out.println("=== 测试视图变更 ===");
        testViewChange(nodes);

        Thread.sleep(3000);

        // 性能测试
        System.out.println("=== 性能测试 ===");
        performanceTest(nodes);

        // 清理资源
        for (PBFTNode node : nodes) {
            if (node.isRunning()) {
                node.stop();
            }
        }

        System.out.println("\n=== PBFT测试完成 ===");
    }

    /**
     * 测试正常共识流程
     */
    private static void testNormalConsensus(List<PBFTNode> nodes) throws Exception {
        PBFTNode primary = nodes.stream()
            .filter(PBFTNode::isPrimary)
            .findFirst()
            .orElseThrow(() -> new RuntimeException("未找到主节点"));

        System.out.println("主节点: " + primary.getNodeId());

        // 发送请求到主节点
        try (Socket socket = new Socket("localhost", 9000);
             ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
             ObjectInputStream input = new ObjectInputStream(socket.getInputStream())) {

            RequestMessage request = new RequestMessage("SET key1 value1", "client-1");
            output.writeObject(request);

            Object response = input.readObject();
            System.out.println("请求响应: " + response);
        }

        Thread.sleep(2000);

        // 再发送几个请求
        String[] operations = {"SET key2 value2", "GET key1", "DELETE key2"};
        for (String operation : operations) {
            try (Socket socket = new Socket("localhost", 9000);
                 ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                 ObjectInputStream input = new ObjectInputStream(socket.getInputStream())) {

                RequestMessage request = new RequestMessage(operation, "client-1");
                output.writeObject(request);

                Object response = input.readObject();
                System.out.println("操作: " + operation + ", 响应: " + response);
            }

            Thread.sleep(1000);
        }
    }

    /**
     * 测试并发请求
     */
    private static void testConcurrentRequests(List<PBFTNode> nodes) throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(20);

        for (int i = 0; i < 20; i++) {
            final int requestId = i;
            executor.submit(() -> {
                try (Socket socket = new Socket("localhost", 9000);
                     ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                     ObjectInputStream input = new ObjectInputStream(socket.getInputStream())) {

                    RequestMessage request = new RequestMessage(
                        "SET concurrent_key_" + requestId + " value_" + requestId,
                        "client-" + requestId);
                    output.writeObject(request);

                    Object response = input.readObject();
                    System.out.println("并发请求 " + requestId + " 响应: " + response);

                } catch (Exception e) {
                    System.err.println("并发请求 " + requestId + " 失败: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();
    }

    /**
     * 测试节点故障
     */
    private static void testNodeFailure(List<PBFTNode> nodes) throws Exception {
        // 停止一个备份节点
        PBFTNode nodeToStop = null;
        for (PBFTNode node : nodes) {
            if (!node.isPrimary()) {
                nodeToStop = node;
                break;
            }
        }

        if (nodeToStop != null) {
            System.out.println("停止节点: " + nodeToStop.getNodeId());
            nodeToStop.stop();

            // 在故障情况下继续发送请求
            try (Socket socket = new Socket("localhost", 9000);
                 ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                 ObjectInputStream input = new ObjectInputStream(socket.getInputStream())) {

                RequestMessage request = new RequestMessage("SET fault_test_key fault_value", "client-fault");
                output.writeObject(request);

                Object response = input.readObject();
                System.out.println("故障测试请求响应: " + response);
            }
        }
    }

    /**
     * 测试视图变更
     */
    private static void testViewChange(List<PBFTNode> nodes) throws Exception {
        // 停止主节点以触发视图变更
        PBFTNode primary = nodes.stream()
            .filter(node -> node.isRunning() && node.isPrimary())
            .findFirst()
            .orElse(null);

        if (primary != null) {
            System.out.println("停止主节点触发视图变更: " + primary.getNodeId());
            primary.stop();

            Thread.sleep(5000); // 等待视图变更完成

            // 向新主节点发送请求
            for (PBFTNode node : nodes) {
                if (node.isRunning() && node.isPrimary()) {
                    System.out.println("新主节点: " + node.getNodeId());

                    // 尝试发送请求到新主节点
                    // 这里需要知道新主节点的端口，简化实现中省略
                    break;
                }
            }
        }
    }

    /**
     * 性能测试
     */
    private static void performanceTest(List<PBFTNode> nodes) throws Exception {
        PBFTNode primary = nodes.stream()
            .filter(node -> node.isRunning() && node.isPrimary())
            .findFirst()
            .orElse(null);

        if (primary == null) {
            System.out.println("没有可用的主节点，跳过性能测试");
            return;
        }

        System.out.println("开始性能测试...");
        long startTime = System.currentTimeMillis();
        int requestCount = 50;

        ExecutorService executor = Executors.newFixedThreadPool(5);
        CountDownLatch latch = new CountDownLatch(requestCount);

        for (int i = 0; i < requestCount; i++) {
            final int requestId = i;
            executor.submit(() -> {
                try (Socket socket = new Socket("localhost", 9000);
                     ObjectOutputStream output = new ObjectOutputStream(socket.getOutputStream());
                     ObjectInputStream input = new ObjectInputStream(socket.getInputStream())) {

                    RequestMessage request = new RequestMessage(
                        "SET perf_key_" + requestId + " perf_value_" + requestId,
                        "perf-client");
                    output.writeObject(request);

                    input.readObject(); // 读取响应

                } catch (Exception e) {
                    System.err.println("性能测试请求失败: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(60, TimeUnit.SECONDS);
        long endTime = System.currentTimeMillis();

        double throughput = (double) requestCount / ((endTime - startTime) / 1000.0);
        System.out.println("性能测试结果:");
        System.out.println("总请求数: " + requestCount);
        System.out.println("总耗时: " + (endTime - startTime) + "ms");
        System.out.println("吞吐量: " + String.format("%.2f", throughput) + " 请求/秒");

        executor.shutdown();
    }
}
```

## 8. 总结

PBFT算法是分布式系统中重要的拜占庭容错共识算法，具有以下特点：

### 8.1 核心优势
- **实用性强**：首个将拜占庭容错复杂度降低到多项式时间的算法
- **异步网络支持**：不依赖同步假设，适用于互联网环境
- **确定性共识**：达成的共识具有最终性，不会回滚
- **容错能力强**：可容忍最多1/3的恶意节点

### 8.2 应用场景
- **区块链系统**：联盟链和私有链的共识机制
- **分布式数据库**：需要强一致性的数据库系统
- **关键基础设施**：航空、金融等对安全性要求极高的系统
- **云计算**：多云环境下的一致性保证

### 8.3 性能特点
- **消息复杂度**：O(n²)，每轮共识需要大量消息交换
- **网络开销**：相比CFT算法网络开销较大
- **延迟特性**：至少需要两轮消息传递才能达成共识
- **吞吐量**：受网络带宽和节点数量影响

### 8.4 实际部署考虑
- **节点数量**：建议不超过20个节点以控制消息复杂度
- **网络质量**：需要相对稳定的网络环境
- **密钥管理**：需要可靠的密钥分发和管理机制
- **监控运维**：需要完善的监控和故障恢复机制

通过本文的详细实现，你可以深入理解PBFT算法的工作原理，并在需要拜占庭容错的分布式系统中应用这一重要的共识协议。