---
title: "分布式系统核心算法详解：ZAB协议原理与Java实现"
date: 2024-12-19T13:00:00+08:00
draft: false
tags: ["分布式系统", "ZAB协议", "原子广播", "ZooKeeper", "Java"]
categories: ["分布式系统"]
author: "LessHash"
description: "深入解析ZAB协议的工作原理、原子广播机制以及在ZooKeeper中的应用实践，包含完整的Java实现代码"
---

## 1. ZAB协议概述

ZAB（ZooKeeper Atomic Broadcast）是ZooKeeper系统中使用的原子广播协议，用于保证分布式数据的一致性。ZAB协议由Yahoo研究院开发，专门为ZooKeeper的需求设计，是一种支持崩溃恢复的原子广播协议。

### 1.1 核心目标

- **原子性**：所有节点要么都接受某个更新，要么都不接受
- **一致性**：所有节点看到相同的数据视图
- **有序性**：保证所有更新操作的全局顺序
- **持久性**：一旦更新被确认，就不会丢失

### 1.2 ZAB与Paxos的区别

```
Paxos特点：
- 设计用于任意的分布式应用
- 容忍网络分区
- 不保证消息的全局顺序

ZAB特点：
- 专为主从复制系统设计
- 简化了Paxos的复杂性
- 保证全局消息顺序
- 支持快速的领导者选举
```

## 2. ZAB协议核心概念

### 2.1 协议模式

ZAB协议有两种基本模式：

#### 图表内容

*[Mermaid图表已转换为表格形式]*


### 2.2 关键概念

1. **事务ID (ZXID)**：64位标识符，高32位是epoch，低32位是counter
2. **Epoch**：每个Leader的任期编号
3. **事务日志**：记录所有状态变更的日志
4. **快照**：系统状态的周期性备份

## 3. ZAB核心数据结构

### 3.1 消息定义

```java
import java.io.Serializable;
import java.util.*;
import java.util.concurrent.*;

/**
 * ZAB协议中的事务ID
 */
public class ZXID implements Comparable<ZXID>, Serializable {
    private final long epoch;    // 选举轮次（高32位）
    private final long counter;  // 事务计数器（低32位）

    public ZXID(long epoch, long counter) {
        this.epoch = epoch;
        this.counter = counter;
    }

    /**
     * 从long值构造ZXID
     */
    public static ZXID fromLong(long zxid) {
        long epoch = zxid >> 32;
        long counter = zxid & 0xFFFFFFFFL;
        return new ZXID(epoch, counter);
    }

    /**
     * 转换为long值
     */
    public long toLong() {
        return (epoch << 32) | counter;
    }

    /**
     * 获取下一个ZXID
     */
    public ZXID next() {
        return new ZXID(epoch, counter + 1);
    }

    /**
     * 新epoch的第一个ZXID
     */
    public static ZXID newEpoch(long epoch) {
        return new ZXID(epoch, 0);
    }

    @Override
    public int compareTo(ZXID other) {
        if (this.epoch != other.epoch) {
            return Long.compare(this.epoch, other.epoch);
        }
        return Long.compare(this.counter, other.counter);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ZXID zxid = (ZXID) obj;
        return epoch == zxid.epoch && counter == zxid.counter;
    }

    @Override
    public int hashCode() {
        return Objects.hash(epoch, counter);
    }

    @Override
    public String toString() {
        return String.format("0x%x%08x", epoch, counter);
    }

    // Getters
    public long getEpoch() { return epoch; }
    public long getCounter() { return counter; }
}

/**
 * ZAB事务提议
 */
public class Proposal implements Serializable {
    private final ZXID zxid;
    private final byte[] data;
    private final String type;
    private final long timestamp;

    public Proposal(ZXID zxid, byte[] data, String type) {
        this.zxid = zxid;
        this.data = data.clone();
        this.type = type;
        this.timestamp = System.currentTimeMillis();
    }

    // Getters
    public ZXID getZxid() { return zxid; }
    public byte[] getData() { return data.clone(); }
    public String getType() { return type; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("Proposal{zxid=%s, type='%s', dataSize=%d}",
                zxid, type, data.length);
    }
}

/**
 * ZAB消息类型
 */
public enum ZabMessageType {
    // 选举相关
    LOOKING,            // 寻找Leader
    FOLLOWING,          // 跟随Leader
    LEADING,            // 作为Leader
    OBSERVING,          // 观察者模式

    // 同步相关
    LEADERINFO,         // Leader信息
    ACKEPOCH,           // 确认epoch
    DIFF,               // 差异同步
    SNAP,               // 快照同步
    NEWLEADER,          // 新Leader通知
    UPTODATE,           // 同步完成

    // 广播相关
    PROPOSAL,           // 事务提议
    ACK,                // 确认
    COMMIT,             // 提交
    PING,               // 心跳
    REVALIDATE          // 重新验证
}

/**
 * ZAB协议消息
 */
public class ZabMessage implements Serializable {
    private final ZabMessageType type;
    private final String senderId;
    private final ZXID zxid;
    private final long epoch;
    private final byte[] data;
    private final long timestamp;

    public ZabMessage(ZabMessageType type, String senderId, ZXID zxid, long epoch, byte[] data) {
        this.type = type;
        this.senderId = senderId;
        this.zxid = zxid;
        this.epoch = epoch;
        this.data = data != null ? data.clone() : null;
        this.timestamp = System.currentTimeMillis();
    }

    public ZabMessage(ZabMessageType type, String senderId, ZXID zxid, long epoch) {
        this(type, senderId, zxid, epoch, null);
    }

    // Getters
    public ZabMessageType getType() { return type; }
    public String getSenderId() { return senderId; }
    public ZXID getZxid() { return zxid; }
    public long getEpoch() { return epoch; }
    public byte[] getData() { return data != null ? data.clone() : null; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("ZabMessage{type=%s, sender='%s', zxid=%s, epoch=%d}",
                type, senderId, zxid, epoch);
    }
}
```

### 3.2 节点状态管理

```java
/**
 * ZAB节点状态
 */
public enum ZabNodeState {
    LOOKING,     // 寻找Leader状态
    FOLLOWING,   // Follower状态
    LEADING,     // Leader状态
    OBSERVING    // Observer状态
}

/**
 * ZAB服务器状态
 */
public class ZabServerState {
    private final String serverId;
    private volatile ZabNodeState state;
    private volatile String leaderId;
    private volatile long currentEpoch;
    private volatile ZXID lastZxid;
    private volatile long acceptedEpoch;

    // 事务日志
    private final Map<ZXID, Proposal> proposalLog = new ConcurrentSkipListMap<>();
    private final Map<ZXID, Set<String>> ackLog = new ConcurrentHashMap<>();

    // 跟随者状态
    private final Set<String> followers = ConcurrentHashMap.newKeySet();
    private final Map<String, ZXID> followerProgress = new ConcurrentHashMap<>();

    public ZabServerState(String serverId) {
        this.serverId = serverId;
        this.state = ZabNodeState.LOOKING;
        this.leaderId = null;
        this.currentEpoch = 0;
        this.lastZxid = new ZXID(0, 0);
        this.acceptedEpoch = 0;
    }

    /**
     * 切换到新状态
     */
    public synchronized void changeState(ZabNodeState newState) {
        ZabNodeState oldState = this.state;
        this.state = newState;

        System.out.println("节点 " + serverId + " 状态变更: " + oldState + " -> " + newState);

        // 状态变更时的清理工作
        if (newState == ZabNodeState.LOOKING) {
            leaderId = null;
            followers.clear();
            followerProgress.clear();
        }
    }

    /**
     * 添加提议到日志
     */
    public void addProposal(Proposal proposal) {
        proposalLog.put(proposal.getZxid(), proposal);
        // 保持日志大小在合理范围内
        if (proposalLog.size() > 10000) {
            ZXID oldestToKeep = proposal.getZxid().toLong() > 5000 ?
                ZXID.fromLong(proposal.getZxid().toLong() - 5000) :
                new ZXID(0, 0);

            proposalLog.entrySet().removeIf(entry -> entry.getKey().compareTo(oldestToKeep) < 0);
        }
    }

    /**
     * 记录ACK
     */
    public void recordAck(ZXID zxid, String followerId) {
        ackLog.computeIfAbsent(zxid, k -> ConcurrentHashMap.newKeySet()).add(followerId);
    }

    /**
     * 检查是否收到足够的ACK
     */
    public boolean hasQuorum(ZXID zxid) {
        Set<String> acks = ackLog.get(zxid);
        if (acks == null) {
            return false;
        }
        // 需要超过半数的ACK（包括Leader自己）
        return acks.size() + 1 > (followers.size() + 1) / 2;
    }

    /**
     * 添加跟随者
     */
    public void addFollower(String followerId, ZXID followerZxid) {
        followers.add(followerId);
        followerProgress.put(followerId, followerZxid);
        System.out.println("添加跟随者: " + followerId + ", ZXID: " + followerZxid);
    }

    /**
     * 移除跟随者
     */
    public void removeFollower(String followerId) {
        followers.remove(followerId);
        followerProgress.remove(followerId);
        System.out.println("移除跟随者: " + followerId);
    }

    /**
     * 更新跟随者进度
     */
    public void updateFollowerProgress(String followerId, ZXID zxid) {
        if (followers.contains(followerId)) {
            followerProgress.put(followerId, zxid);
        }
    }

    /**
     * 获取建议的同步类型
     */
    public String getSyncType(ZXID followerZxid) {
        if (followerZxid.compareTo(lastZxid) == 0) {
            return "UPTODATE";
        } else if (followerZxid.compareTo(lastZxid) < 0 &&
                   proposalLog.containsKey(followerZxid)) {
            return "DIFF";
        } else {
            return "SNAP";
        }
    }

    /**
     * 获取从指定ZXID开始的提议列表
     */
    public List<Proposal> getProposalsFrom(ZXID fromZxid) {
        return proposalLog.entrySet().stream()
                .filter(entry -> entry.getKey().compareTo(fromZxid) > 0)
                .map(Map.Entry::getValue)
                .collect(Collectors.toList());
    }

    // Getters and Setters
    public String getServerId() { return serverId; }
    public ZabNodeState getState() { return state; }
    public String getLeaderId() { return leaderId; }
    public void setLeaderId(String leaderId) { this.leaderId = leaderId; }
    public long getCurrentEpoch() { return currentEpoch; }
    public void setCurrentEpoch(long currentEpoch) { this.currentEpoch = currentEpoch; }
    public ZXID getLastZxid() { return lastZxid; }
    public void setLastZxid(ZXID lastZxid) { this.lastZxid = lastZxid; }
    public long getAcceptedEpoch() { return acceptedEpoch; }
    public void setAcceptedEpoch(long acceptedEpoch) { this.acceptedEpoch = acceptedEpoch; }
    public Set<String> getFollowers() { return new HashSet<>(followers); }
    public Map<String, ZXID> getFollowerProgress() { return new HashMap<>(followerProgress); }
    public Map<ZXID, Proposal> getProposalLog() { return new TreeMap<>(proposalLog); }
}
```

## 4. Leader选举算法

### 4.1 Fast Leader Election

```java
/**
 * ZAB快速Leader选举算法
 */
public class FastLeaderElection {
    private final String serverId;
    private final ZabServerState serverState;
    private final Set<String> allServers;
    private final Map<String, Vote> receivedVotes = new ConcurrentHashMap<>();
    private final AtomicBoolean electionFinished = new AtomicBoolean(false);

    public FastLeaderElection(String serverId, ZabServerState serverState, Set<String> allServers) {
        this.serverId = serverId;
        this.serverState = serverState;
        this.allServers = new HashSet<>(allServers);
    }

    /**
     * 开始Leader选举
     */
    public ElectionResult electLeader() {
        System.out.println("节点 " + serverId + " 开始Leader选举");

        electionFinished.set(false);
        receivedVotes.clear();
        long electionEpoch = serverState.getCurrentEpoch() + 1;

        // 投票给自己
        Vote myVote = new Vote(serverId, serverState.getLastZxid(), electionEpoch, serverState.getAcceptedEpoch());
        receivedVotes.put(serverId, myVote);

        // 向所有其他服务器发送投票
        broadcastVote(myVote);

        // 等待选举结果
        return waitForElectionResult(electionEpoch);
    }

    /**
     * 处理接收到的投票
     */
    public void receiveVote(Vote vote) {
        if (electionFinished.get()) {
            return;
        }

        receivedVotes.put(vote.getServerId(), vote);

        // 检查是否需要更新自己的投票
        Vote currentVote = receivedVotes.get(serverId);
        if (shouldUpdateVote(currentVote, vote)) {
            Vote newVote = new Vote(vote.getLeaderId(), vote.getZxid(),
                                   vote.getElectionEpoch(), vote.getPeerEpoch());
            receivedVotes.put(serverId, newVote);
            broadcastVote(newVote);
        }

        // 检查是否达成共识
        checkElectionResult();
    }

    /**
     * 判断是否应该更新投票
     */
    private boolean shouldUpdateVote(Vote currentVote, Vote receivedVote) {
        // 比较election epoch
        if (receivedVote.getElectionEpoch() > currentVote.getElectionEpoch()) {
            return true;
        }

        if (receivedVote.getElectionEpoch() < currentVote.getElectionEpoch()) {
            return false;
        }

        // Election epoch相同，比较peer epoch
        if (receivedVote.getPeerEpoch() > currentVote.getPeerEpoch()) {
            return true;
        }

        if (receivedVote.getPeerEpoch() < currentVote.getPeerEpoch()) {
            return false;
        }

        // Peer epoch相同，比较ZXID
        if (receivedVote.getZxid().compareTo(currentVote.getZxid()) > 0) {
            return true;
        }

        if (receivedVote.getZxid().compareTo(currentVote.getZxid()) < 0) {
            return false;
        }

        // ZXID相同，比较服务器ID
        return receivedVote.getLeaderId().compareTo(currentVote.getLeaderId()) > 0;
    }

    /**
     * 检查选举结果
     */
    private void checkElectionResult() {
        Vote myVote = receivedVotes.get(serverId);
        if (myVote == null) {
            return;
        }

        // 统计投票给同一个leader的票数
        Map<String, Integer> voteCounts = new HashMap<>();
        for (Vote vote : receivedVotes.values()) {
            if (vote.getElectionEpoch() == myVote.getElectionEpoch()) {
                voteCounts.merge(vote.getLeaderId(), 1, Integer::sum);
            }
        }

        // 检查是否有服务器获得过半数投票
        int quorumSize = allServers.size() / 2 + 1;
        for (Map.Entry<String, Integer> entry : voteCounts.entrySet()) {
            if (entry.getValue() >= quorumSize) {
                // 找到Leader
                finishElection(entry.getKey(), myVote.getElectionEpoch());
                return;
            }
        }
    }

    /**
     * 完成选举
     */
    private void finishElection(String leaderId, long electionEpoch) {
        if (electionFinished.compareAndSet(false, true)) {
            System.out.println("选举完成，Leader: " + leaderId + ", Epoch: " + electionEpoch);

            if (leaderId.equals(serverId)) {
                serverState.changeState(ZabNodeState.LEADING);
                serverState.setCurrentEpoch(electionEpoch);
            } else {
                serverState.changeState(ZabNodeState.FOLLOWING);
                serverState.setLeaderId(leaderId);
            }
        }
    }

    /**
     * 广播投票
     */
    private void broadcastVote(Vote vote) {
        // 在实际实现中，这里会通过网络发送投票消息
        System.out.println("广播投票: " + vote);
    }

    /**
     * 等待选举结果
     */
    private ElectionResult waitForElectionResult(long electionEpoch) {
        long startTime = System.currentTimeMillis();
        long timeout = 30000; // 30秒超时

        while (!electionFinished.get() && System.currentTimeMillis() - startTime < timeout) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        if (electionFinished.get()) {
            return new ElectionResult(true, serverState.getLeaderId(), electionEpoch);
        } else {
            return new ElectionResult(false, null, electionEpoch);
        }
    }

    /**
     * 重置选举状态
     */
    public void reset() {
        electionFinished.set(false);
        receivedVotes.clear();
    }
}

/**
 * 投票
 */
class Vote {
    private final String serverId;
    private final String leaderId;
    private final ZXID zxid;
    private final long electionEpoch;
    private final long peerEpoch;

    public Vote(String leaderId, ZXID zxid, long electionEpoch, long peerEpoch) {
        this.serverId = leaderId; // 投票者ID
        this.leaderId = leaderId; // 候选Leader ID
        this.zxid = zxid;
        this.electionEpoch = electionEpoch;
        this.peerEpoch = peerEpoch;
    }

    // Getters
    public String getServerId() { return serverId; }
    public String getLeaderId() { return leaderId; }
    public ZXID getZxid() { return zxid; }
    public long getElectionEpoch() { return electionEpoch; }
    public long getPeerEpoch() { return peerEpoch; }

    @Override
    public String toString() {
        return String.format("Vote{server='%s', leader='%s', zxid=%s, electionEpoch=%d, peerEpoch=%d}",
                serverId, leaderId, zxid, electionEpoch, peerEpoch);
    }
}

/**
 * 选举结果
 */
class ElectionResult {
    private final boolean success;
    private final String leaderId;
    private final long epoch;

    public ElectionResult(boolean success, String leaderId, long epoch) {
        this.success = success;
        this.leaderId = leaderId;
        this.epoch = epoch;
    }

    // Getters
    public boolean isSuccess() { return success; }
    public String getLeaderId() { return leaderId; }
    public long getEpoch() { return epoch; }

    @Override
    public String toString() {
        return String.format("ElectionResult{success=%s, leader='%s', epoch=%d}",
                success, leaderId, epoch);
    }
}
```

## 5. 崩溃恢复实现

### 5.1 Leader恢复

```java
/**
 * ZAB崩溃恢复处理器
 */
public class ZabRecoveryHandler {
    private final ZabServerState serverState;
    private final ExecutorService executorService = Executors.newCachedThreadPool();

    public ZabRecoveryHandler(ZabServerState serverState) {
        this.serverState = serverState;
    }

    /**
     * Leader发现阶段
     */
    public void leaderDiscovery(Set<String> followers) {
        System.out.println("Leader " + serverState.getServerId() + " 开始发现阶段");

        long newEpoch = serverState.getCurrentEpoch() + 1;
        Map<String, FollowerInfo> followerInfos = new ConcurrentHashMap<>();
        CountDownLatch latch = new CountDownLatch(followers.size());

        // 向所有Follower发送LEADERINFO
        for (String followerId : followers) {
            executorService.submit(() -> {
                try {
                    FollowerInfo info = sendLeaderInfo(followerId, newEpoch);
                    if (info != null) {
                        followerInfos.put(followerId, info);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 处理Follower响应
        processFollowerInfos(followerInfos, newEpoch);
    }

    /**
     * 发送Leader信息
     */
    private FollowerInfo sendLeaderInfo(String followerId, long newEpoch) {
        try {
            // 模拟网络通信
            ZabMessage leaderInfo = new ZabMessage(
                ZabMessageType.LEADERINFO,
                serverState.getServerId(),
                serverState.getLastZxid(),
                newEpoch
            );

            System.out.println("向 " + followerId + " 发送LEADERINFO: " + leaderInfo);

            // 等待ACKEPOCH响应（模拟）
            Thread.sleep(100);

            // 模拟收到的响应
            long followerEpoch = newEpoch - 1; // 简化的模拟
            ZXID followerZxid = new ZXID(followerEpoch, 100);

            return new FollowerInfo(followerId, followerEpoch, followerZxid);

        } catch (Exception e) {
            System.err.println("向 " + followerId + " 发送LEADERINFO失败: " + e.getMessage());
            return null;
        }
    }

    /**
     * 处理Follower信息
     */
    private void processFollowerInfos(Map<String, FollowerInfo> followerInfos, long newEpoch) {
        // 找到最大的acceptedEpoch
        long maxAcceptedEpoch = followerInfos.values().stream()
                .mapToLong(FollowerInfo::getAcceptedEpoch)
                .max()
                .orElse(serverState.getAcceptedEpoch());

        // 更新当前epoch
        long finalEpoch = Math.max(newEpoch, maxAcceptedEpoch + 1);
        serverState.setCurrentEpoch(finalEpoch);

        System.out.println("Leader确定新epoch: " + finalEpoch);

        // 开始同步阶段
        leaderSynchronization(followerInfos, finalEpoch);
    }

    /**
     * Leader同步阶段
     */
    private void leaderSynchronization(Map<String, FollowerInfo> followerInfos, long epoch) {
        System.out.println("Leader开始同步阶段");

        // 为每个Follower确定同步策略
        for (FollowerInfo followerInfo : followerInfos.values()) {
            String syncType = serverState.getSyncType(followerInfo.getLastZxid());
            executorService.submit(() -> synchronizeFollower(followerInfo, syncType, epoch));
        }

        // 等待所有Follower同步完成
        waitForSynchronization(followerInfos.keySet());

        // 发送NEWLEADER消息
        sendNewLeaderMessage(epoch);
    }

    /**
     * 同步单个Follower
     */
    private void synchronizeFollower(FollowerInfo followerInfo, String syncType, long epoch) {
        String followerId = followerInfo.getFollowerId();

        try {
            switch (syncType) {
                case "DIFF":
                    sendDifferentialSync(followerId, followerInfo.getLastZxid());
                    break;
                case "SNAP":
                    sendSnapshotSync(followerId);
                    break;
                case "UPTODATE":
                    // Follower已经是最新的
                    break;
            }

            serverState.addFollower(followerId, followerInfo.getLastZxid());
            System.out.println("Follower " + followerId + " 同步完成，类型: " + syncType);

        } catch (Exception e) {
            System.err.println("同步Follower " + followerId + " 失败: " + e.getMessage());
        }
    }

    /**
     * 发送差异同步
     */
    private void sendDifferentialSync(String followerId, ZXID followerZxid) {
        List<Proposal> proposals = serverState.getProposalsFrom(followerZxid);

        ZabMessage diffMessage = new ZabMessage(
            ZabMessageType.DIFF,
            serverState.getServerId(),
            serverState.getLastZxid(),
            serverState.getCurrentEpoch(),
            serializeProposals(proposals)
        );

        System.out.println("向 " + followerId + " 发送DIFF，包含 " + proposals.size() + " 个提议");
    }

    /**
     * 发送快照同步
     */
    private void sendSnapshotSync(String followerId) {
        // 生成当前状态快照
        byte[] snapshot = generateSnapshot();

        ZabMessage snapMessage = new ZabMessage(
            ZabMessageType.SNAP,
            serverState.getServerId(),
            serverState.getLastZxid(),
            serverState.getCurrentEpoch(),
            snapshot
        );

        System.out.println("向 " + followerId + " 发送SNAP，快照大小: " + snapshot.length);
    }

    /**
     * 等待同步完成
     */
    private void waitForSynchronization(Set<String> followers) {
        long startTime = System.currentTimeMillis();
        long timeout = 30000; // 30秒超时

        while (System.currentTimeMillis() - startTime < timeout) {
            boolean allSynced = followers.stream()
                    .allMatch(serverState::getFollowers()::contains);

            if (allSynced) {
                System.out.println("所有Follower同步完成");
                return;
            }

            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        System.err.println("同步超时，部分Follower可能未完成同步");
    }

    /**
     * 发送NEWLEADER消息
     */
    private void sendNewLeaderMessage(long epoch) {
        ZabMessage newLeaderMessage = new ZabMessage(
            ZabMessageType.NEWLEADER,
            serverState.getServerId(),
            serverState.getLastZxid(),
            epoch
        );

        System.out.println("向所有Follower发送NEWLEADER: " + newLeaderMessage);

        // 等待ACK（简化实现）
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("崩溃恢复完成，开始正常服务");
    }

    /**
     * 序列化提议列表
     */
    private byte[] serializeProposals(List<Proposal> proposals) {
        // 简化的序列化实现
        StringBuilder sb = new StringBuilder();
        for (Proposal proposal : proposals) {
            sb.append(proposal.getZxid().toString()).append(":").append(proposal.getType()).append(";");
        }
        return sb.toString().getBytes();
    }

    /**
     * 生成状态快照
     */
    private byte[] generateSnapshot() {
        // 简化的快照生成
        String snapshot = "SNAPSHOT:" + serverState.getLastZxid() + ":" +
                         serverState.getCurrentEpoch() + ":" +
                         System.currentTimeMillis();
        return snapshot.getBytes();
    }

    /**
     * 关闭恢复处理器
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Follower信息
 */
class FollowerInfo {
    private final String followerId;
    private final long acceptedEpoch;
    private final ZXID lastZxid;

    public FollowerInfo(String followerId, long acceptedEpoch, ZXID lastZxid) {
        this.followerId = followerId;
        this.acceptedEpoch = acceptedEpoch;
        this.lastZxid = lastZxid;
    }

    // Getters
    public String getFollowerId() { return followerId; }
    public long getAcceptedEpoch() { return acceptedEpoch; }
    public ZXID getLastZxid() { return lastZxid; }

    @Override
    public String toString() {
        return String.format("FollowerInfo{id='%s', acceptedEpoch=%d, lastZxid=%s}",
                followerId, acceptedEpoch, lastZxid);
    }
}
```

## 6. 原子广播实现

### 6.1 消息广播

```java
/**
 * ZAB原子广播处理器
 */
public class ZabBroadcastHandler {
    private final ZabServerState serverState;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    private final Queue<ClientRequest> pendingRequests = new ConcurrentLinkedQueue<>();
    private final AtomicBoolean broadcasting = new AtomicBoolean(false);

    public ZabBroadcastHandler(ZabServerState serverState) {
        this.serverState = serverState;

        // 启动定期处理请求的任务
        scheduler.scheduleAtFixedRate(this::processRequests, 10, 10, TimeUnit.MILLISECONDS);
    }

    /**
     * 提交客户端请求
     */
    public CompletableFuture<String> submitRequest(ClientRequest request) {
        if (serverState.getState() != ZabNodeState.LEADING) {
            return CompletableFuture.completedFuture("NOT_LEADER:" + serverState.getLeaderId());
        }

        CompletableFuture<String> future = new CompletableFuture<>();
        request.setResultFuture(future);
        pendingRequests.offer(request);

        System.out.println("收到客户端请求: " + request.getOperation());
        return future;
    }

    /**
     * 处理待处理的请求
     */
    private void processRequests() {
        if (serverState.getState() != ZabNodeState.LEADING || !broadcasting.compareAndSet(false, true)) {
            return;
        }

        try {
            ClientRequest request = pendingRequests.poll();
            if (request != null) {
                processRequest(request);
            }
        } finally {
            broadcasting.set(false);
        }
    }

    /**
     * 处理单个请求
     */
    private void processRequest(ClientRequest request) {
        try {
            // 生成新的ZXID
            ZXID newZxid = serverState.getLastZxid().next();

            // 创建提议
            Proposal proposal = new Proposal(newZxid, request.getData(), request.getOperation());

            // 记录到本地日志
            serverState.addProposal(proposal);
            serverState.setLastZxid(newZxid);

            // 广播PROPOSAL消息给所有Follower
            broadcastProposal(proposal);

            // 设置超时处理
            scheduleTimeout(proposal, request);

            System.out.println("广播提议: " + proposal);

        } catch (Exception e) {
            System.err.println("处理请求失败: " + e.getMessage());
            request.getResultFuture().complete("ERROR:" + e.getMessage());
        }
    }

    /**
     * 广播提议
     */
    private void broadcastProposal(Proposal proposal) {
        ZabMessage proposalMessage = new ZabMessage(
            ZabMessageType.PROPOSAL,
            serverState.getServerId(),
            proposal.getZxid(),
            serverState.getCurrentEpoch(),
            proposal.getData()
        );

        // 向所有Follower发送PROPOSAL
        for (String followerId : serverState.getFollowers()) {
            sendMessage(followerId, proposalMessage);
        }
    }

    /**
     * 处理ACK消息
     */
    public void handleAck(ZabMessage ackMessage) {
        ZXID zxid = ackMessage.getZxid();
        String followerId = ackMessage.getSenderId();

        // 记录ACK
        serverState.recordAck(zxid, followerId);

        // 检查是否收到足够的ACK
        if (serverState.hasQuorum(zxid)) {
            commitProposal(zxid);
        }
    }

    /**
     * 提交提议
     */
    private void commitProposal(ZXID zxid) {
        System.out.println("提交提议: " + zxid);

        // 发送COMMIT消息给所有Follower
        ZabMessage commitMessage = new ZabMessage(
            ZabMessageType.COMMIT,
            serverState.getServerId(),
            zxid,
            serverState.getCurrentEpoch()
        );

        for (String followerId : serverState.getFollowers()) {
            sendMessage(followerId, commitMessage);
        }

        // 在本地提交
        applyProposal(zxid);
    }

    /**
     * 应用提议到状态机
     */
    private void applyProposal(ZXID zxid) {
        // 简化的状态机应用
        System.out.println("应用提议到状态机: " + zxid);

        // 通知客户端请求完成（在实际实现中需要跟踪请求和ZXID的对应关系）
        // 这里简化处理
    }

    /**
     * 设置提议超时
     */
    private void scheduleTimeout(Proposal proposal, ClientRequest request) {
        scheduler.schedule(() -> {
            // 检查提议是否已经提交
            if (!serverState.getProposalLog().containsKey(proposal.getZxid())) {
                System.err.println("提议超时: " + proposal.getZxid());
                request.getResultFuture().complete("TIMEOUT");
            }
        }, 10, TimeUnit.SECONDS);
    }

    /**
     * 发送消息（模拟网络通信）
     */
    private void sendMessage(String targetId, ZabMessage message) {
        // 在实际实现中，这里会通过网络发送消息
        System.out.println("发送消息到 " + targetId + ": " + message.getType());
    }

    /**
     * 关闭广播处理器
     */
    public void shutdown() {
        scheduler.shutdown();
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
 * 客户端请求
 */
class ClientRequest {
    private final String clientId;
    private final String operation;
    private final byte[] data;
    private final long timestamp;
    private CompletableFuture<String> resultFuture;

    public ClientRequest(String clientId, String operation, byte[] data) {
        this.clientId = clientId;
        this.operation = operation;
        this.data = data.clone();
        this.timestamp = System.currentTimeMillis();
    }

    // Getters and Setters
    public String getClientId() { return clientId; }
    public String getOperation() { return operation; }
    public byte[] getData() { return data.clone(); }
    public long getTimestamp() { return timestamp; }
    public CompletableFuture<String> getResultFuture() { return resultFuture; }
    public void setResultFuture(CompletableFuture<String> resultFuture) { this.resultFuture = resultFuture; }

    @Override
    public String toString() {
        return String.format("ClientRequest{client='%s', operation='%s', timestamp=%d}",
                clientId, operation, timestamp);
    }
}
```

### 6.2 Follower处理

```java
/**
 * ZAB Follower处理器
 */
public class ZabFollowerHandler {
    private final ZabServerState serverState;
    private final String leaderId;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    public ZabFollowerHandler(ZabServerState serverState, String leaderId) {
        this.serverState = serverState;
        this.leaderId = leaderId;

        // 启动心跳检测
        scheduler.scheduleAtFixedRate(this::checkLeaderHeartbeat, 5, 5, TimeUnit.SECONDS);
    }

    /**
     * 处理PROPOSAL消息
     */
    public void handleProposal(ZabMessage proposalMessage) {
        ZXID proposalZxid = proposalMessage.getZxid();

        System.out.println("收到PROPOSAL: " + proposalZxid);

        // 验证提议
        if (!isValidProposal(proposalMessage)) {
            System.err.println("无效的PROPOSAL: " + proposalZxid);
            return;
        }

        // 创建并记录提议
        Proposal proposal = new Proposal(proposalZxid, proposalMessage.getData(), "CLIENT_REQUEST");
        serverState.addProposal(proposal);

        // 发送ACK
        sendAck(proposalZxid);
    }

    /**
     * 处理COMMIT消息
     */
    public void handleCommit(ZabMessage commitMessage) {
        ZXID commitZxid = commitMessage.getZxid();

        System.out.println("收到COMMIT: " + commitZxid);

        // 提交提议
        if (serverState.getProposalLog().containsKey(commitZxid)) {
            applyProposal(commitZxid);
            serverState.setLastZxid(commitZxid);
        } else {
            System.err.println("未找到对应的PROPOSAL: " + commitZxid);
        }
    }

    /**
     * 处理NEWLEADER消息
     */
    public void handleNewLeader(ZabMessage newLeaderMessage) {
        System.out.println("收到NEWLEADER: " + newLeaderMessage);

        // 更新epoch
        serverState.setCurrentEpoch(newLeaderMessage.getEpoch());
        serverState.setLeaderId(newLeaderMessage.getSenderId());

        // 发送ACK
        sendAck(newLeaderMessage.getZxid());
    }

    /**
     * 处理同步消息
     */
    public void handleSync(ZabMessage syncMessage) {
        switch (syncMessage.getType()) {
            case DIFF:
                handleDifferentialSync(syncMessage);
                break;
            case SNAP:
                handleSnapshotSync(syncMessage);
                break;
            case UPTODATE:
                System.out.println("已经是最新状态");
                break;
            default:
                System.err.println("未知的同步消息类型: " + syncMessage.getType());
        }
    }

    /**
     * 处理差异同步
     */
    private void handleDifferentialSync(ZabMessage diffMessage) {
        System.out.println("处理差异同步");

        // 解析差异数据
        List<Proposal> proposals = deserializeProposals(diffMessage.getData());

        // 应用所有提议
        for (Proposal proposal : proposals) {
            serverState.addProposal(proposal);
            applyProposal(proposal.getZxid());
        }

        // 更新最后的ZXID
        if (!proposals.isEmpty()) {
            serverState.setLastZxid(proposals.get(proposals.size() - 1).getZxid());
        }

        System.out.println("差异同步完成，应用了 " + proposals.size() + " 个提议");
    }

    /**
     * 处理快照同步
     */
    private void handleSnapshotSync(ZabMessage snapMessage) {
        System.out.println("处理快照同步");

        // 应用快照
        applySnapshot(snapMessage.getData());

        // 更新状态
        serverState.setLastZxid(snapMessage.getZxid());

        System.out.println("快照同步完成");
    }

    /**
     * 验证提议
     */
    private boolean isValidProposal(ZabMessage proposalMessage) {
        // 检查epoch
        if (proposalMessage.getEpoch() != serverState.getCurrentEpoch()) {
            return false;
        }

        // 检查ZXID顺序
        ZXID proposalZxid = proposalMessage.getZxid();
        if (proposalZxid.compareTo(serverState.getLastZxid()) <= 0) {
            return false;
        }

        // 检查是否来自当前Leader
        return proposalMessage.getSenderId().equals(leaderId);
    }

    /**
     * 发送ACK
     */
    private void sendAck(ZXID zxid) {
        ZabMessage ackMessage = new ZabMessage(
            ZabMessageType.ACK,
            serverState.getServerId(),
            zxid,
            serverState.getCurrentEpoch()
        );

        sendMessage(leaderId, ackMessage);
        System.out.println("发送ACK: " + zxid);
    }

    /**
     * 应用提议到状态机
     */
    private void applyProposal(ZXID zxid) {
        // 简化的状态机应用
        System.out.println("Follower应用提议: " + zxid);
    }

    /**
     * 反序列化提议
     */
    private List<Proposal> deserializeProposals(byte[] data) {
        List<Proposal> proposals = new ArrayList<>();

        if (data != null) {
            String content = new String(data);
            String[] parts = content.split(";");

            for (String part : parts) {
                if (!part.trim().isEmpty()) {
                    String[] fields = part.split(":");
                    if (fields.length >= 2) {
                        ZXID zxid = ZXID.fromLong(Long.parseLong(fields[0], 16));
                        String type = fields[1];
                        proposals.add(new Proposal(zxid, new byte[0], type));
                    }
                }
            }
        }

        return proposals;
    }

    /**
     * 应用快照
     */
    private void applySnapshot(byte[] snapshotData) {
        // 简化的快照应用
        String snapshot = new String(snapshotData);
        System.out.println("应用快照: " + snapshot);
    }

    /**
     * 检查Leader心跳
     */
    private void checkLeaderHeartbeat() {
        // 简化的心跳检测逻辑
        // 在实际实现中，会检测是否在指定时间内收到Leader的消息
        System.out.println("检查Leader心跳");
    }

    /**
     * 发送消息
     */
    private void sendMessage(String targetId, ZabMessage message) {
        // 模拟网络通信
        System.out.println("发送消息到 " + targetId + ": " + message.getType());
    }

    /**
     * 关闭Follower处理器
     */
    public void shutdown() {
        scheduler.shutdown();
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
```

## 7. 完整的ZAB服务器实现

### 7.1 ZAB服务器

```java
/**
 * ZAB协议服务器
 */
public class ZabServer {
    private final String serverId;
    private final ZabServerState serverState;
    private final Set<String> allServers;

    // 组件
    private FastLeaderElection leaderElection;
    private ZabRecoveryHandler recoveryHandler;
    private ZabBroadcastHandler broadcastHandler;
    private ZabFollowerHandler followerHandler;

    // 网络和调度
    private final ExecutorService networkExecutor = Executors.newCachedThreadPool();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(3);
    private final AtomicBoolean running = new AtomicBoolean(false);

    public ZabServer(String serverId, Set<String> allServers) {
        this.serverId = serverId;
        this.allServers = new HashSet<>(allServers);
        this.serverState = new ZabServerState(serverId);

        initializeComponents();
    }

    /**
     * 初始化组件
     */
    private void initializeComponents() {
        this.leaderElection = new FastLeaderElection(serverId, serverState, allServers);
        this.recoveryHandler = new ZabRecoveryHandler(serverState);
        this.broadcastHandler = new ZabBroadcastHandler(serverState);
    }

    /**
     * 启动服务器
     */
    public void start() {
        if (running.compareAndSet(false, true)) {
            System.out.println("ZAB服务器启动: " + serverId);

            // 启动状态机
            scheduler.submit(this::runStateMachine);

            // 启动网络监听（简化实现）
            scheduler.scheduleAtFixedRate(this::processNetworkMessages, 1, 1, TimeUnit.SECONDS);
        }
    }

    /**
     * 停止服务器
     */
    public void stop() {
        if (running.compareAndSet(true, false)) {
            System.out.println("ZAB服务器停止: " + serverId);

            // 关闭组件
            if (recoveryHandler != null) {
                recoveryHandler.shutdown();
            }
            if (broadcastHandler != null) {
                broadcastHandler.shutdown();
            }
            if (followerHandler != null) {
                followerHandler.shutdown();
            }

            // 关闭线程池
            scheduler.shutdown();
            networkExecutor.shutdown();

            try {
                if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                    scheduler.shutdownNow();
                }
                if (!networkExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    networkExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                scheduler.shutdownNow();
                networkExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * 运行状态机
     */
    private void runStateMachine() {
        while (running.get()) {
            try {
                switch (serverState.getState()) {
                    case LOOKING:
                        handleLookingState();
                        break;
                    case LEADING:
                        handleLeadingState();
                        break;
                    case FOLLOWING:
                        handleFollowingState();
                        break;
                    case OBSERVING:
                        handleObservingState();
                        break;
                }

                Thread.sleep(1000); // 状态检查间隔

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                System.err.println("状态机错误: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    /**
     * 处理LOOKING状态
     */
    private void handleLookingState() {
        System.out.println("节点 " + serverId + " 处于LOOKING状态");

        ElectionResult result = leaderElection.electLeader();

        if (result.isSuccess()) {
            if (result.getLeaderId().equals(serverId)) {
                // 当选为Leader
                serverState.changeState(ZabNodeState.LEADING);
                System.out.println("节点 " + serverId + " 当选为Leader");
            } else {
                // 成为Follower
                serverState.changeState(ZabNodeState.FOLLOWING);
                serverState.setLeaderId(result.getLeaderId());
                System.out.println("节点 " + serverId + " 成为Follower，Leader: " + result.getLeaderId());
            }
        } else {
            // 选举失败，继续寻找
            System.out.println("选举失败，继续寻找Leader");
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * 处理LEADING状态
     */
    private void handleLeadingState() {
        if (recoveryHandler != null) {
            // 执行崩溃恢复
            Set<String> followers = new HashSet<>(allServers);
            followers.remove(serverId);
            recoveryHandler.leaderDiscovery(followers);

            System.out.println("Leader " + serverId + " 完成崩溃恢复，开始正常服务");
        }

        // 在LEADING状态下，broadcastHandler会处理客户端请求
        while (serverState.getState() == ZabNodeState.LEADING && running.get()) {
            try {
                Thread.sleep(5000);
                System.out.println("Leader " + serverId + " 正常运行，Followers: " +
                                 serverState.getFollowers().size());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    /**
     * 处理FOLLOWING状态
     */
    private void handleFollowingState() {
        String leaderId = serverState.getLeaderId();
        if (leaderId != null) {
            followerHandler = new ZabFollowerHandler(serverState, leaderId);
            System.out.println("Follower " + serverId + " 开始跟随Leader: " + leaderId);

            // 在FOLLOWING状态下，followerHandler会处理Leader的消息
            while (serverState.getState() == ZabNodeState.FOLLOWING && running.get()) {
                try {
                    Thread.sleep(5000);
                    System.out.println("Follower " + serverId + " 正常运行，Leader: " + leaderId);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }

            if (followerHandler != null) {
                followerHandler.shutdown();
                followerHandler = null;
            }
        }
    }

    /**
     * 处理OBSERVING状态
     */
    private void handleObservingState() {
        System.out.println("节点 " + serverId + " 处于OBSERVING状态");

        while (serverState.getState() == ZabNodeState.OBSERVING && running.get()) {
            try {
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    /**
     * 处理网络消息（简化实现）
     */
    private void processNetworkMessages() {
        // 在实际实现中，这里会处理从网络接收到的消息
        // 简化实现中省略网络层细节
    }

    /**
     * 提交客户端请求
     */
    public CompletableFuture<String> submitRequest(String operation, byte[] data) {
        if (serverState.getState() == ZabNodeState.LEADING && broadcastHandler != null) {
            ClientRequest request = new ClientRequest("client", operation, data);
            return broadcastHandler.submitRequest(request);
        } else {
            String leaderId = serverState.getLeaderId();
            return CompletableFuture.completedFuture("NOT_LEADER:" +
                    (leaderId != null ? leaderId : "UNKNOWN"));
        }
    }

    /**
     * 模拟接收投票
     */
    public void receiveVote(Vote vote) {
        if (serverState.getState() == ZabNodeState.LOOKING && leaderElection != null) {
            leaderElection.receiveVote(vote);
        }
    }

    /**
     * 模拟接收ZAB消息
     */
    public void receiveZabMessage(ZabMessage message) {
        switch (message.getType()) {
            case PROPOSAL:
                if (followerHandler != null) {
                    followerHandler.handleProposal(message);
                }
                break;
            case ACK:
                if (broadcastHandler != null) {
                    broadcastHandler.handleAck(message);
                }
                break;
            case COMMIT:
                if (followerHandler != null) {
                    followerHandler.handleCommit(message);
                }
                break;
            case NEWLEADER:
                if (followerHandler != null) {
                    followerHandler.handleNewLeader(message);
                }
                break;
            default:
                System.out.println("收到消息: " + message);
        }
    }

    /**
     * 获取服务器状态
     */
    public ZabServerStats getStats() {
        return new ZabServerStats(
            serverId,
            serverState.getState(),
            serverState.getLeaderId(),
            serverState.getCurrentEpoch(),
            serverState.getLastZxid(),
            serverState.getFollowers().size(),
            serverState.getProposalLog().size()
        );
    }

    /**
     * 打印服务器状态
     */
    public void printServerStatus() {
        ZabServerStats stats = getStats();
        System.out.println("\n=== ZAB服务器状态 ===");
        System.out.println("服务器ID: " + stats.getServerId());
        System.out.println("当前状态: " + stats.getState());
        System.out.println("Leader ID: " + stats.getLeaderId());
        System.out.println("当前Epoch: " + stats.getCurrentEpoch());
        System.out.println("最后ZXID: " + stats.getLastZxid());
        System.out.println("Follower数量: " + stats.getFollowerCount());
        System.out.println("提议日志大小: " + stats.getProposalLogSize());
        System.out.println("================\n");
    }

    // Getters
    public String getServerId() { return serverId; }
    public ZabNodeState getState() { return serverState.getState(); }
    public boolean isRunning() { return running.get(); }
}

/**
 * ZAB服务器统计信息
 */
class ZabServerStats {
    private final String serverId;
    private final ZabNodeState state;
    private final String leaderId;
    private final long currentEpoch;
    private final ZXID lastZxid;
    private final int followerCount;
    private final int proposalLogSize;

    public ZabServerStats(String serverId, ZabNodeState state, String leaderId,
                         long currentEpoch, ZXID lastZxid, int followerCount, int proposalLogSize) {
        this.serverId = serverId;
        this.state = state;
        this.leaderId = leaderId;
        this.currentEpoch = currentEpoch;
        this.lastZxid = lastZxid;
        this.followerCount = followerCount;
        this.proposalLogSize = proposalLogSize;
    }

    // Getters
    public String getServerId() { return serverId; }
    public ZabNodeState getState() { return state; }
    public String getLeaderId() { return leaderId; }
    public long getCurrentEpoch() { return currentEpoch; }
    public ZXID getLastZxid() { return lastZxid; }
    public int getFollowerCount() { return followerCount; }
    public int getProposalLogSize() { return proposalLogSize; }
}
```

## 8. 完整测试示例

### 8.1 ZAB集群测试

```java
/**
 * ZAB协议集群测试
 */
public class ZabClusterTest {

    public static void main(String[] args) throws Exception {
        testZabCluster();
    }

    /**
     * 测试ZAB集群
     */
    private static void testZabCluster() throws Exception {
        System.out.println("=== ZAB协议集群测试开始 ===\n");

        // 创建5个节点的集群
        Set<String> allServers = new HashSet<>(Arrays.asList(
            "server-1", "server-2", "server-3", "server-4", "server-5"
        ));

        List<ZabServer> servers = new ArrayList<>();

        // 创建并启动所有服务器
        for (String serverId : allServers) {
            ZabServer server = new ZabServer(serverId, allServers);
            server.start();
            servers.add(server);

            Thread.sleep(1000); // 间隔启动
        }

        // 等待集群稳定
        Thread.sleep(5000);

        // 模拟选举过程
        simulateElection(servers);

        // 等待选举完成
        Thread.sleep(5000);

        // 打印集群状态
        printClusterStatus(servers);

        // 测试客户端请求
        testClientRequests(servers);

        // 模拟Leader故障
        simulateLeaderFailure(servers);

        // 等待重新选举
        Thread.sleep(10000);

        // 打印最终状态
        printClusterStatus(servers);

        // 清理资源
        for (ZabServer server : servers) {
            server.stop();
        }

        System.out.println("\n=== ZAB协议集群测试完成 ===");
    }

    /**
     * 模拟选举过程
     */
    private static void simulateElection(List<ZabServer> servers) {
        System.out.println("=== 模拟选举过程 ===");

        // 模拟投票交换（简化实现）
        for (ZabServer server : servers) {
            if (server.getState() == ZabNodeState.LOOKING) {
                // 创建模拟投票
                Vote vote = new Vote(
                    server.getServerId(),
                    new ZXID(1, 0),
                    1,
                    0
                );

                // 发送给其他节点
                for (ZabServer otherServer : servers) {
                    if (!otherServer.getServerId().equals(server.getServerId())) {
                        otherServer.receiveVote(vote);
                    }
                }
            }
        }
    }

    /**
     * 测试客户端请求
     */
    private static void testClientRequests(List<ZabServer> servers) throws Exception {
        System.out.println("\n=== 测试客户端请求 ===");

        // 找到Leader
        ZabServer leader = servers.stream()
                .filter(server -> server.getState() == ZabNodeState.LEADING)
                .findFirst()
                .orElse(null);

        if (leader != null) {
            System.out.println("找到Leader: " + leader.getServerId());

            // 发送多个请求
            List<CompletableFuture<String>> futures = new ArrayList<>();

            for (int i = 0; i < 5; i++) {
                String operation = "SET key" + i + " value" + i;
                byte[] data = operation.getBytes();

                CompletableFuture<String> future = leader.submitRequest(operation, data);
                futures.add(future);

                System.out.println("发送请求: " + operation);
            }

            // 等待所有请求完成
            for (int i = 0; i < futures.size(); i++) {
                try {
                    String result = futures.get(i).get(10, TimeUnit.SECONDS);
                    System.out.println("请求 " + i + " 结果: " + result);
                } catch (Exception e) {
                    System.err.println("请求 " + i + " 失败: " + e.getMessage());
                }
            }
        } else {
            System.out.println("未找到Leader，无法测试客户端请求");
        }
    }

    /**
     * 模拟Leader故障
     */
    private static void simulateLeaderFailure(List<ZabServer> servers) {
        System.out.println("\n=== 模拟Leader故障 ===");

        // 找到并停止Leader
        for (ZabServer server : servers) {
            if (server.getState() == ZabNodeState.LEADING) {
                System.out.println("停止Leader: " + server.getServerId());
                server.stop();
                break;
            }
        }

        // 触发重新选举
        for (ZabServer server : servers) {
            if (server.isRunning()) {
                // 在实际实现中，这里会检测到Leader故障并重新进入LOOKING状态
                System.out.println("节点 " + server.getServerId() + " 检测到Leader故障");
            }
        }
    }

    /**
     * 打印集群状态
     */
    private static void printClusterStatus(List<ZabServer> servers) {
        System.out.println("\n=== 集群状态 ===");

        for (ZabServer server : servers) {
            if (server.isRunning()) {
                server.printServerStatus();
            } else {
                System.out.println("服务器 " + server.getServerId() + " 已停止");
            }
        }
    }

    /**
     * 性能测试
     */
    private static void performanceTest() throws Exception {
        System.out.println("\n=== 性能测试 ===");

        Set<String> allServers = new HashSet<>(Arrays.asList("perf-1", "perf-2", "perf-3"));
        List<ZabServer> servers = new ArrayList<>();

        // 创建性能测试集群
        for (String serverId : allServers) {
            ZabServer server = new ZabServer(serverId, allServers);
            server.start();
            servers.add(server);
        }

        Thread.sleep(5000);

        // 找到Leader
        ZabServer leader = servers.stream()
                .filter(server -> server.getState() == ZabNodeState.LEADING)
                .findFirst()
                .orElse(null);

        if (leader != null) {
            System.out.println("开始性能测试，Leader: " + leader.getServerId());

            long startTime = System.currentTimeMillis();
            int requestCount = 100;
            List<CompletableFuture<String>> futures = new ArrayList<>();

            // 并发发送请求
            for (int i = 0; i < requestCount; i++) {
                String operation = "PERF_TEST_" + i;
                CompletableFuture<String> future = leader.submitRequest(operation, operation.getBytes());
                futures.add(future);
            }

            // 等待所有请求完成
            int successCount = 0;
            for (CompletableFuture<String> future : futures) {
                try {
                    future.get(30, TimeUnit.SECONDS);
                    successCount++;
                } catch (Exception e) {
                    // 忽略失败的请求
                }
            }

            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            System.out.println("性能测试结果:");
            System.out.println("总请求数: " + requestCount);
            System.out.println("成功请求数: " + successCount);
            System.out.println("总耗时: " + duration + "ms");
            System.out.println("平均延迟: " + (duration / (double) requestCount) + "ms");
            System.out.println("吞吐量: " + (successCount * 1000.0 / duration) + " 请求/秒");
        }

        // 清理
        for (ZabServer server : servers) {
            server.stop();
        }

        System.out.println("=== 性能测试完成 ===");
    }

    /**
     * 测试ZXID功能
     */
    private static void testZXID() {
        System.out.println("\n=== 测试ZXID功能 ===");

        // 测试ZXID创建和比较
        ZXID zxid1 = new ZXID(1, 100);
        ZXID zxid2 = new ZXID(1, 101);
        ZXID zxid3 = new ZXID(2, 50);

        System.out.println("ZXID1: " + zxid1);
        System.out.println("ZXID2: " + zxid2);
        System.out.println("ZXID3: " + zxid3);

        System.out.println("ZXID1 < ZXID2: " + (zxid1.compareTo(zxid2) < 0));
        System.out.println("ZXID2 < ZXID3: " + (zxid2.compareTo(zxid3) < 0));

        // 测试ZXID转换
        long longValue = zxid1.toLong();
        ZXID reconstructed = ZXID.fromLong(longValue);
        System.out.println("原始ZXID: " + zxid1);
        System.out.println("转换后ZXID: " + reconstructed);
        System.out.println("转换正确: " + zxid1.equals(reconstructed));

        // 测试下一个ZXID
        ZXID next = zxid1.next();
        System.out.println("下一个ZXID: " + next);

        System.out.println("=== ZXID测试完成 ===");
    }
}
```

## 9. 总结

ZAB（ZooKeeper Atomic Broadcast）协议是专门为ZooKeeper设计的原子广播协议，具有以下特点：

### 9.1 核心优势
- **简化设计**：相比Paxos，ZAB针对主从复制场景进行了优化
- **全局顺序**：保证所有操作的全局顺序性
- **高可用性**：支持Leader故障时的快速恢复
- **一致性保证**：确保所有节点的数据一致性

### 9.2 关键机制
- **两阶段协议**：崩溃恢复阶段和消息广播阶段
- **ZXID机制**：64位事务标识符，包含epoch和计数器
- **Leader选举**：Fast Leader Election算法
- **同步机制**：DIFF、SNAP、UPTODATE三种同步方式

### 9.3 应用场景
- **ZooKeeper**：作为ZooKeeper的核心共识协议
- **配置管理**：分布式配置中心
- **服务发现**：服务注册与发现
- **分布式协调**：分布式锁、队列等协调服务

### 9.4 性能特点
- **读性能**：支持从任意节点读取，读性能优秀
- **写性能**：所有写操作需要通过Leader，写性能受限
- **一致性**：强一致性保证，适合对一致性要求高的场景
- **可用性**：只要超过半数节点正常就能提供服务

### 9.5 与其他协议比较
- **vs Paxos**：更简单，更适合主从架构
- **vs Raft**：设计理念相似，但ZAB更早出现
- **vs PBFT**：ZAB不处理拜占庭故障，复杂度更低

通过本文的详细实现，你可以深入理解ZAB协议的工作原理和实现细节，为开发基于ZAB的分布式协调系统提供坚实的基础。