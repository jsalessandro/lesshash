---
title: "braft 完全指南：从零掌握分布式一致性编程"
date: 2025-09-18T15:00:00+08:00
draft: false
tags: ["braft", "Raft", "分布式一致性", "分布式系统", "共识算法"]
categories: ["技术分享"]
author: "lesshash"
description: "braft 是百度开源的基于 Raft 算法的分布式一致性库，本文将深入介绍 braft 的核心概念、使用方法和最佳实践"
---

## 一、为什么需要 braft？

### 1.1 分布式系统的一致性挑战

在分布式系统中，**数据一致性**是最核心的挑战之一。当多个节点需要对某个状态达成一致时，面临诸多困难：

- **网络分区**：节点间通信可能中断
- **节点故障**：任何节点都可能随时宕机
- **消息乱序**：网络延迟导致消息到达顺序不确定
- **脑裂问题**：网络分区可能导致集群分裂

### 1.2 Raft 算法简介

Raft 是一个易于理解的分布式一致性算法，相比 Paxos 更加简单明了：

- **Leader 选举**：在任意时刻，集群中最多只有一个 Leader
- **日志复制**：Leader 负责接收客户端请求并复制到其他节点
- **安全性保证**：确保已提交的日志条目不会丢失

### 1.3 braft 的优势

**braft** 是百度开源的 Raft 算法 C++ 实现，具有以下优势：

#### 性能优势
- **高吞吐量**：单集群可达 100万+ QPS
- **低延迟**：Leader 选举通常在 200ms 内完成
- **批量处理**：支持日志批量提交，提高效率

#### 工程优势
- **生产就绪**：在百度内部大规模使用，经过充分验证
- **易于集成**：与 brpc 无缝集成，API 设计友好
- **可观测性**：丰富的监控指标和调试工具

#### 功能完整性
- **快照支持**：支持数据快照，减少日志占用空间
- **成员变更**：支持动态添加/删除节点
- **线性一致性读**：支持强一致性读操作

## 二、快速入门

### 2.1 环境搭建

#### 依赖安装

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake git
sudo apt-get install -y libssl-dev libprotobuf-dev protobuf-compiler
sudo apt-get install -y libgflags-dev libgoogle-glog-dev

# 安装 brpc（braft 依赖）
git clone https://github.com/apache/brpc.git
cd brpc && mkdir build && cd build
cmake .. && make -j$(nproc) && sudo make install
```

#### 编译 braft

```bash
# 克隆源码
git clone https://github.com/baidu/braft.git
cd braft

# 编译
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# 安装
sudo make install
```

### 2.2 第一个 braft 程序

我们来实现一个简单的分布式计数器，它能在多个节点间保持一致。

#### Step 1: 定义状态机

```cpp
#include <braft/raft.h>
#include <braft/util.h>
#include <braft/storage.h>

// 操作类型
enum OpType {
    OP_INCREMENT = 1,
    OP_DECREMENT = 2,
    OP_SET = 3
};

// 操作日志
struct CounterOp {
    OpType type;
    int64_t value;

    // 序列化
    std::string serialize() const {
        return std::to_string(type) + ":" + std::to_string(value);
    }

    // 反序列化
    static CounterOp deserialize(const std::string& data) {
        size_t pos = data.find(':');
        CounterOp op;
        op.type = static_cast<OpType>(std::stoi(data.substr(0, pos)));
        op.value = std::stoll(data.substr(pos + 1));
        return op;
    }
};

// 状态机实现
class CounterStateMachine : public braft::StateMachine {
public:
    CounterStateMachine() : _counter(0) {}

    // 应用日志到状态机
    void on_apply(braft::Iterator& iter) override {
        for (; iter.valid(); iter.next()) {
            braft::AsyncClosureGuard closure_guard(iter.done());

            if (iter.done()) {
                // 这是来自客户端的请求
                CounterOp op = CounterOp::deserialize(iter.data().to_string());
                int64_t old_value = _counter;

                switch (op.type) {
                    case OP_INCREMENT:
                        _counter += op.value;
                        break;
                    case OP_DECREMENT:
                        _counter -= op.value;
                        break;
                    case OP_SET:
                        _counter = op.value;
                        break;
                }

                LOG(INFO) << "Applied operation: " << op.serialize()
                         << ", counter: " << old_value << " -> " << _counter;

                // 返回结果给客户端
                if (iter.done()) {
                    static_cast<CounterClosure*>(iter.done())->set_result(_counter);
                }
            } else {
                // 这是从快照恢复或日志回放
                CounterOp op = CounterOp::deserialize(iter.data().to_string());
                switch (op.type) {
                    case OP_INCREMENT: _counter += op.value; break;
                    case OP_DECREMENT: _counter -= op.value; break;
                    case OP_SET: _counter = op.value; break;
                }
            }
        }
    }

    // 保存快照
    void on_snapshot_save(braft::SnapshotWriter* writer, braft::Closure* done) override {
        brpc::ClosureGuard done_guard(done);

        // 保存计数器值到快照
        std::string snapshot_path = writer->get_path() + "/counter";
        std::ofstream file(snapshot_path);
        if (!file.is_open()) {
            LOG(ERROR) << "Failed to open snapshot file: " << snapshot_path;
            done->status().set_error(EIO, "Failed to save snapshot");
            return;
        }

        file << _counter;
        file.close();

        // 添加文件到快照
        if (writer->add_file("counter") != 0) {
            LOG(ERROR) << "Failed to add file to snapshot";
            done->status().set_error(EIO, "Failed to add file to snapshot");
            return;
        }

        LOG(INFO) << "Saved snapshot with counter: " << _counter;
    }

    // 加载快照
    int on_snapshot_load(braft::SnapshotReader* reader) override {
        if (!reader->list_files().count("counter")) {
            LOG(ERROR) << "Counter file not found in snapshot";
            return -1;
        }

        std::string snapshot_path = reader->get_path() + "/counter";
        std::ifstream file(snapshot_path);
        if (!file.is_open()) {
            LOG(ERROR) << "Failed to open snapshot file: " << snapshot_path;
            return -1;
        }

        file >> _counter;
        file.close();

        LOG(INFO) << "Loaded snapshot with counter: " << _counter;
        return 0;
    }

    // 处理 Leader 变更
    void on_leader_start(int64_t term) override {
        LOG(INFO) << "Became leader at term: " << term;
    }

    void on_leader_stop(const butil::Status& status) override {
        LOG(INFO) << "Stepped down as leader: " << status;
    }

    // 获取当前计数器值
    int64_t get_counter() const { return _counter; }

private:
    int64_t _counter;
};

// 异步回调
class CounterClosure : public braft::Closure {
public:
    CounterClosure() : _result(0) {}

    void Run() override {
        if (status().ok()) {
            LOG(INFO) << "Operation succeeded, result: " << _result;
        } else {
            LOG(ERROR) << "Operation failed: " << status();
        }
        delete this;
    }

    void set_result(int64_t result) { _result = result; }
    int64_t get_result() const { return _result; }

private:
    int64_t _result;
};
```

#### Step 2: 实现 Raft 节点

```cpp
class CounterServer {
public:
    CounterServer() : _node(nullptr), _state_machine(new CounterStateMachine()) {}

    ~CounterServer() {
        if (_node) {
            _node->shutdown(nullptr);
            _node->join();
            delete _node;
        }
        delete _state_machine;
    }

    // 启动节点
    int start(const std::string& listen_addr,
              const std::string& raft_addr,
              const std::string& peers,
              const std::string& data_dir) {

        // 创建 RPC 服务器
        if (_server.Start(listen_addr.c_str(), nullptr) != 0) {
            LOG(ERROR) << "Failed to start RPC server";
            return -1;
        }

        // 配置 Raft 节点
        braft::NodeOptions node_options;

        // 设置状态机
        node_options.fsm = _state_machine;

        // 设置存储路径
        node_options.log_uri = data_dir + "/log";
        node_options.raft_meta_uri = data_dir + "/raft_meta";
        node_options.snapshot_uri = data_dir + "/snapshot";

        // 设置选举超时（毫秒）
        node_options.election_timeout_ms = 5000;

        // 设置快照间隔
        node_options.snapshot_interval_s = 30;

        // 禁用 CLI（命令行接口），生产环境中通常启用
        node_options.disable_cli = false;

        // 创建 Raft 节点
        _node = new braft::Node("counter_group", braft::PeerId(raft_addr));

        if (_node->init(node_options) != 0) {
            LOG(ERROR) << "Failed to init raft node";
            return -1;
        }

        // 如果指定了 peers，则作为集群成员启动
        if (!peers.empty()) {
            std::vector<braft::PeerId> peer_list;
            butil::StringSplitter sp(peers.c_str(), ',');
            for (; sp; ++sp) {
                braft::PeerId peer(sp.field(), sp.length());
                peer_list.push_back(peer);
            }

            braft::Configuration conf(peer_list);
            if (_node->bootstrap(conf) != 0) {
                LOG(ERROR) << "Failed to bootstrap raft node";
                return -1;
            }
        }

        LOG(INFO) << "Counter server started at " << listen_addr
                  << ", raft at " << raft_addr;
        return 0;
    }

    // 执行操作
    void execute_operation(const CounterOp& op, CounterClosure* closure) {
        if (!_node->is_leader()) {
            closure->status().set_error(EPERM, "Not leader");
            closure->Run();
            return;
        }

        // 构造日志条目
        butil::IOBuf log_data;
        log_data.append(op.serialize());

        // 提交到 Raft
        braft::Task task;
        task.data = &log_data;
        task.done = closure;

        _node->apply(task);
    }

    // 获取当前值（强一致性读）
    int64_t get_counter_consistent() {
        if (!_node->is_leader()) {
            return -1;  // 只有 Leader 才能提供强一致性读
        }

        // 通过 read_index 实现线性一致性读
        braft::ReadIndexClosure* read_closure =
            new braft::ReadIndexClosure([this](const braft::ReadIndexStatus& status) {
                if (status.status.ok()) {
                    // 读取状态机数据
                    return _state_machine->get_counter();
                }
                return (int64_t)-1;
            });

        _node->read_index(butil::IOBuf(), read_closure);
        // 注意：实际应用中需要等待回调完成
        return _state_machine->get_counter();
    }

    // 获取当前值（非强一致性读）
    int64_t get_counter_local() {
        return _state_machine->get_counter();
    }

    // 检查是否为 Leader
    bool is_leader() const {
        return _node && _node->is_leader();
    }

    // 获取 Leader 信息
    braft::PeerId get_leader() const {
        if (_node) {
            return _node->leader_id();
        }
        return braft::PeerId();
    }

private:
    brpc::Server _server;
    braft::Node* _node;
    CounterStateMachine* _state_machine;
};
```

#### Step 3: 实现客户端

```cpp
// 基于 brpc 的客户端
class CounterClient {
public:
    CounterClient() {}

    // 连接到服务器
    int connect(const std::string& server_addr) {
        brpc::ChannelOptions options;
        options.protocol = brpc::PROTOCOL_BAIDU_STD;
        options.timeout_ms = 1000;
        options.max_retry = 3;

        if (_channel.Init(server_addr.c_str(), &options) != 0) {
            LOG(ERROR) << "Failed to connect to " << server_addr;
            return -1;
        }

        return 0;
    }

    // 增加计数器
    bool increment(int64_t value) {
        CounterOp op{OP_INCREMENT, value};
        return execute_operation(op);
    }

    // 减少计数器
    bool decrement(int64_t value) {
        CounterOp op{OP_DECREMENT, value};
        return execute_operation(op);
    }

    // 设置计数器值
    bool set(int64_t value) {
        CounterOp op{OP_SET, value};
        return execute_operation(op);
    }

    // 获取计数器值
    int64_t get() {
        // 这里简化为直接调用服务端方法
        // 实际应用中需要通过 RPC 调用
        return 0;
    }

private:
    bool execute_operation(const CounterOp& op) {
        // 实际实现需要定义 protobuf 接口并通过 RPC 调用
        // 这里只是示例框架
        return true;
    }

private:
    brpc::Channel _channel;
};
```

#### Step 4: 主程序

```cpp
#include <iostream>
#include <signal.h>
#include <gflags/gflags.h>

DEFINE_string(listen_addr, "127.0.0.1:8080", "Listen address for RPC");
DEFINE_string(raft_addr, "127.0.0.1:8081", "Raft listen address");
DEFINE_string(peers, "", "Initial peers, separated by comma");
DEFINE_string(data_dir, "./data", "Data directory");

static CounterServer* g_server = nullptr;

void signal_handler(int sig) {
    if (g_server) {
        LOG(INFO) << "Received signal " << sig << ", shutting down...";
        delete g_server;
        g_server = nullptr;
        exit(0);
    }
}

int main(int argc, char* argv[]) {
    google::ParseCommandLineFlags(&argc, &argv, true);

    // 设置信号处理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // 创建数据目录
    if (system(("mkdir -p " + FLAGS_data_dir).c_str()) != 0) {
        LOG(ERROR) << "Failed to create data directory";
        return -1;
    }

    // 启动服务器
    g_server = new CounterServer();
    if (g_server->start(FLAGS_listen_addr, FLAGS_raft_addr,
                       FLAGS_peers, FLAGS_data_dir) != 0) {
        LOG(ERROR) << "Failed to start counter server";
        return -1;
    }

    // 等待用户输入
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line == "quit" || line == "exit") {
            break;
        }

        if (line == "status") {
            std::cout << "Leader: " << g_server->is_leader() << std::endl;
            std::cout << "Counter: " << g_server->get_counter_local() << std::endl;
            std::cout << "Leader ID: " << g_server->get_leader() << std::endl;
        } else if (line.substr(0, 4) == "inc ") {
            int64_t value = std::stoll(line.substr(4));
            CounterClosure* closure = new CounterClosure();
            CounterOp op{OP_INCREMENT, value};
            g_server->execute_operation(op, closure);
        } else if (line.substr(0, 4) == "dec ") {
            int64_t value = std::stoll(line.substr(4));
            CounterClosure* closure = new CounterClosure();
            CounterOp op{OP_DECREMENT, value};
            g_server->execute_operation(op, closure);
        } else if (line.substr(0, 4) == "set ") {
            int64_t value = std::stoll(line.substr(4));
            CounterClosure* closure = new CounterClosure();
            CounterOp op{OP_SET, value};
            g_server->execute_operation(op, closure);
        } else {
            std::cout << "Commands: status, inc <value>, dec <value>, set <value>, quit" << std::endl;
        }
    }

    delete g_server;
    return 0;
}
```

### 2.3 编译和运行

#### 创建 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(counter_example)

set(CMAKE_CXX_STANDARD 11)

find_package(PkgConfig REQUIRED)
find_package(Protobuf REQUIRED)
find_package(gflags REQUIRED)

# 查找 brpc 和 braft
find_library(BRPC_LIB brpc)
find_library(BRAFT_LIB braft)

add_executable(counter_server
    counter_server.cpp
)

target_link_libraries(counter_server
    ${BRAFT_LIB}
    ${BRPC_LIB}
    ${Protobuf_LIBRARIES}
    gflags
    ssl
    crypto
    dl
    z
)
```

#### 编译运行

```bash
# 编译
mkdir build && cd build
cmake .. && make

# 启动第一个节点（作为引导节点）
./counter_server --listen_addr=127.0.0.1:8080 --raft_addr=127.0.0.1:8081 \
                 --peers=127.0.0.1:8081,127.0.0.1:8082,127.0.0.1:8083 \
                 --data_dir=./node1

# 启动第二个节点
./counter_server --listen_addr=127.0.0.1:8090 --raft_addr=127.0.0.1:8082 \
                 --data_dir=./node2

# 启动第三个节点
./counter_server --listen_addr=127.0.0.1:8100 --raft_addr=127.0.0.1:8083 \
                 --data_dir=./node3
```

## 三、核心概念深入

### 3.1 Raft 状态机

#### 3.1.1 状态机接口详解

```cpp
class StateMachine {
public:
    // 应用日志条目到状态机
    virtual void on_apply(braft::Iterator& iter) = 0;

    // 保存快照
    virtual void on_snapshot_save(braft::SnapshotWriter* writer,
                                 braft::Closure* done) = 0;

    // 加载快照
    virtual int on_snapshot_load(braft::SnapshotReader* reader) = 0;

    // Leader 选举成功回调
    virtual void on_leader_start(int64_t term) {}

    // Leader 退位回调
    virtual void on_leader_stop(const butil::Status& status) {}

    // 启动回调
    virtual void on_start_following(const braft::LeaderChangeContext& ctx) {}

    // 停止 following 回调
    virtual void on_stop_following(const braft::LeaderChangeContext& ctx) {}

    // 配置变更回调
    virtual void on_configuration_committed(const braft::Configuration& conf,
                                           int64_t index) {}

    // 错误回调
    virtual void on_error(const braft::Error& e) {}
};
```

#### 3.1.2 高级状态机示例

```cpp
// 支持多种操作的键值存储状态机
class KVStateMachine : public braft::StateMachine {
public:
    enum Operation {
        OP_PUT = 1,
        OP_DELETE = 2,
        OP_CAS = 3  // Compare-And-Swap
    };

    struct LogEntry {
        Operation op;
        std::string key;
        std::string value;
        std::string expected_value;  // for CAS

        std::string serialize() const {
            butil::IOBuf buf;
            buf.append(reinterpret_cast<const char*>(&op), sizeof(op));

            uint32_t key_len = key.length();
            buf.append(reinterpret_cast<const char*>(&key_len), sizeof(key_len));
            buf.append(key);

            uint32_t value_len = value.length();
            buf.append(reinterpret_cast<const char*>(&value_len), sizeof(value_len));
            buf.append(value);

            if (op == OP_CAS) {
                uint32_t expected_len = expected_value.length();
                buf.append(reinterpret_cast<const char*>(&expected_len), sizeof(expected_len));
                buf.append(expected_value);
            }

            return buf.to_string();
        }

        static LogEntry deserialize(const std::string& data) {
            LogEntry entry;
            const char* ptr = data.c_str();
            size_t offset = 0;

            // 读取操作类型
            entry.op = *reinterpret_cast<const Operation*>(ptr + offset);
            offset += sizeof(Operation);

            // 读取 key
            uint32_t key_len = *reinterpret_cast<const uint32_t*>(ptr + offset);
            offset += sizeof(uint32_t);
            entry.key = std::string(ptr + offset, key_len);
            offset += key_len;

            // 读取 value
            uint32_t value_len = *reinterpret_cast<const uint32_t*>(ptr + offset);
            offset += sizeof(uint32_t);
            entry.value = std::string(ptr + offset, value_len);
            offset += value_len;

            // 如果是 CAS 操作，读取期望值
            if (entry.op == OP_CAS && offset < data.length()) {
                uint32_t expected_len = *reinterpret_cast<const uint32_t*>(ptr + offset);
                offset += sizeof(uint32_t);
                entry.expected_value = std::string(ptr + offset, expected_len);
            }

            return entry;
        }
    };

private:
    std::unordered_map<std::string, std::string> _kv_store;
    mutable bthread::Mutex _mutex;
    std::atomic<int64_t> _applied_index{0};

public:
    void on_apply(braft::Iterator& iter) override {
        for (; iter.valid(); iter.next()) {
            braft::AsyncClosureGuard closure_guard(iter.done());

            _applied_index.store(iter.index());

            LogEntry entry = LogEntry::deserialize(iter.data().to_string());
            bool success = false;
            std::string old_value;

            {
                std::unique_lock<bthread::Mutex> lock(_mutex);

                switch (entry.op) {
                    case OP_PUT:
                        old_value = _kv_store[entry.key];
                        _kv_store[entry.key] = entry.value;
                        success = true;
                        break;

                    case OP_DELETE:
                        if (_kv_store.count(entry.key)) {
                            old_value = _kv_store[entry.key];
                            _kv_store.erase(entry.key);
                            success = true;
                        }
                        break;

                    case OP_CAS:
                        if (_kv_store.count(entry.key) &&
                            _kv_store[entry.key] == entry.expected_value) {
                            old_value = _kv_store[entry.key];
                            _kv_store[entry.key] = entry.value;
                            success = true;
                        }
                        break;
                }
            }

            LOG(INFO) << "Applied " << entry.key << ": " << old_value
                     << " -> " << entry.value << ", success: " << success;

            // 返回结果给客户端
            if (iter.done()) {
                KVClosure* kv_closure = dynamic_cast<KVClosure*>(iter.done());
                if (kv_closure) {
                    kv_closure->set_result(success, old_value);
                }
            }
        }
    }

    void on_snapshot_save(braft::SnapshotWriter* writer, braft::Closure* done) override {
        brpc::ClosureGuard done_guard(done);

        std::string snapshot_path = writer->get_path() + "/kv_data";
        std::ofstream file(snapshot_path, std::ios::binary);
        if (!file.is_open()) {
            LOG(ERROR) << "Failed to open snapshot file";
            done->status().set_error(EIO, "Failed to save snapshot");
            return;
        }

        {
            std::unique_lock<bthread::Mutex> lock(_mutex);

            // 保存当前应用的索引
            file.write(reinterpret_cast<const char*>(&_applied_index), sizeof(_applied_index));

            // 保存键值对数量
            uint64_t count = _kv_store.size();
            file.write(reinterpret_cast<const char*>(&count), sizeof(count));

            // 保存所有键值对
            for (const auto& pair : _kv_store) {
                uint32_t key_len = pair.first.length();
                file.write(reinterpret_cast<const char*>(&key_len), sizeof(key_len));
                file.write(pair.first.c_str(), key_len);

                uint32_t value_len = pair.second.length();
                file.write(reinterpret_cast<const char*>(&value_len), sizeof(value_len));
                file.write(pair.second.c_str(), value_len);
            }
        }

        file.close();

        if (writer->add_file("kv_data") != 0) {
            LOG(ERROR) << "Failed to add file to snapshot";
            done->status().set_error(EIO, "Failed to add file");
            return;
        }

        LOG(INFO) << "Saved snapshot with " << _kv_store.size()
                 << " keys at index " << _applied_index.load();
    }

    int on_snapshot_load(braft::SnapshotReader* reader) override {
        if (!reader->list_files().count("kv_data")) {
            LOG(ERROR) << "kv_data not found in snapshot";
            return -1;
        }

        std::string snapshot_path = reader->get_path() + "/kv_data";
        std::ifstream file(snapshot_path, std::ios::binary);
        if (!file.is_open()) {
            LOG(ERROR) << "Failed to open snapshot file";
            return -1;
        }

        {
            std::unique_lock<bthread::Mutex> lock(_mutex);
            _kv_store.clear();

            // 读取应用索引
            int64_t applied_index;
            file.read(reinterpret_cast<char*>(&applied_index), sizeof(applied_index));
            _applied_index.store(applied_index);

            // 读取键值对数量
            uint64_t count;
            file.read(reinterpret_cast<char*>(&count), sizeof(count));

            // 读取所有键值对
            for (uint64_t i = 0; i < count; ++i) {
                uint32_t key_len;
                file.read(reinterpret_cast<char*>(&key_len), sizeof(key_len));
                std::string key(key_len, '\0');
                file.read(&key[0], key_len);

                uint32_t value_len;
                file.read(reinterpret_cast<char*>(&value_len), sizeof(value_len));
                std::string value(value_len, '\0');
                file.read(&value[0], value_len);

                _kv_store[key] = value;
            }
        }

        file.close();

        LOG(INFO) << "Loaded snapshot with " << _kv_store.size()
                 << " keys at index " << _applied_index.load();
        return 0;
    }

    // 获取值
    bool get(const std::string& key, std::string* value) const {
        std::unique_lock<bthread::Mutex> lock(_mutex);
        auto it = _kv_store.find(key);
        if (it != _kv_store.end()) {
            *value = it->second;
            return true;
        }
        return false;
    }

    // 获取所有键
    std::vector<std::string> list_keys() const {
        std::unique_lock<bthread::Mutex> lock(_mutex);
        std::vector<std::string> keys;
        for (const auto& pair : _kv_store) {
            keys.push_back(pair.first);
        }
        return keys;
    }

    size_t size() const {
        std::unique_lock<bthread::Mutex> lock(_mutex);
        return _kv_store.size();
    }
};

// KV 操作的回调
class KVClosure : public braft::Closure {
public:
    void Run() override {
        if (status().ok()) {
            LOG(INFO) << "KV operation succeeded, result: " << _success
                     << ", old_value: " << _old_value;
        } else {
            LOG(ERROR) << "KV operation failed: " << status();
        }
        delete this;
    }

    void set_result(bool success, const std::string& old_value) {
        _success = success;
        _old_value = old_value;
    }

    bool get_success() const { return _success; }
    const std::string& get_old_value() const { return _old_value; }

private:
    bool _success = false;
    std::string _old_value;
};
```

### 3.2 配置管理

#### 3.2.1 动态成员变更

```cpp
class ConfigurationManager {
public:
    // 添加节点
    static void add_peer(braft::Node* node, const std::string& peer_addr,
                        braft::Closure* done) {
        braft::Configuration new_conf;
        node->list_peers(&new_conf);

        braft::PeerId peer_id(peer_addr);
        new_conf.add_peer(peer_id);

        LOG(INFO) << "Adding peer: " << peer_addr;
        node->change_peers(new_conf, done);
    }

    // 移除节点
    static void remove_peer(braft::Node* node, const std::string& peer_addr,
                           braft::Closure* done) {
        braft::Configuration new_conf;
        node->list_peers(&new_conf);

        braft::PeerId peer_id(peer_addr);
        new_conf.remove_peer(peer_id);

        LOG(INFO) << "Removing peer: " << peer_addr;
        node->change_peers(new_conf, done);
    }

    // 查看当前配置
    static std::vector<std::string> list_peers(braft::Node* node) {
        braft::Configuration conf;
        node->list_peers(&conf);

        std::vector<std::string> peers;
        for (auto it = conf.begin(); it != conf.end(); ++it) {
            peers.push_back(it->to_string());
        }
        return peers;
    }

    // 安全的配置变更（逐个添加/删除）
    static void safe_change_peers(braft::Node* node,
                                 const std::vector<std::string>& target_peers,
                                 braft::Closure* final_done) {
        // 获取当前配置
        braft::Configuration current_conf;
        node->list_peers(&current_conf);

        std::set<std::string> current_peers;
        for (auto it = current_conf.begin(); it != current_conf.end(); ++it) {
            current_peers.insert(it->to_string());
        }

        std::set<std::string> target_set(target_peers.begin(), target_peers.end());

        // 找出需要添加和删除的节点
        std::vector<std::string> to_add, to_remove;

        for (const auto& peer : target_set) {
            if (current_peers.find(peer) == current_peers.end()) {
                to_add.push_back(peer);
            }
        }

        for (const auto& peer : current_peers) {
            if (target_set.find(peer) == target_set.end()) {
                to_remove.push_back(peer);
            }
        }

        // 创建批量变更管理器
        BatchConfigChange* batch = new BatchConfigChange(node, to_add, to_remove, final_done);
        batch->start();
    }

private:
    // 批量配置变更管理器
    class BatchConfigChange {
    public:
        BatchConfigChange(braft::Node* node,
                         const std::vector<std::string>& to_add,
                         const std::vector<std::string>& to_remove,
                         braft::Closure* done)
            : _node(node), _to_add(to_add), _to_remove(to_remove),
              _final_done(done), _current_index(0) {}

        void start() {
            if (!_to_add.empty()) {
                process_add();
            } else if (!_to_remove.empty()) {
                process_remove();
            } else {
                finish();
            }
        }

    private:
        void process_add() {
            if (_current_index >= _to_add.size()) {
                _current_index = 0;
                process_remove();
                return;
            }

            braft::Closure* done = new braft::NewCallback(this, &BatchConfigChange::on_add_done);
            add_peer(_node, _to_add[_current_index], done);
        }

        void process_remove() {
            if (_current_index >= _to_remove.size()) {
                finish();
                return;
            }

            braft::Closure* done = new braft::NewCallback(this, &BatchConfigChange::on_remove_done);
            remove_peer(_node, _to_remove[_current_index], done);
        }

        void on_add_done() {
            ++_current_index;
            process_add();
        }

        void on_remove_done() {
            ++_current_index;
            process_remove();
        }

        void finish() {
            if (_final_done) {
                _final_done->Run();
            }
            delete this;
        }

        braft::Node* _node;
        std::vector<std::string> _to_add;
        std::vector<std::string> _to_remove;
        braft::Closure* _final_done;
        size_t _current_index;
    };
};
```

### 3.3 日志压缩和快照

#### 3.3.1 智能快照策略

```cpp
class SmartSnapshotManager {
public:
    struct SnapshotOptions {
        int64_t max_log_size = 100 * 1024 * 1024;  // 100MB
        int64_t max_log_entries = 100000;          // 10万条
        int32_t snapshot_interval_s = 3600;        // 1小时
        int32_t min_snapshot_interval_s = 300;     // 最小5分钟
        double log_growth_threshold = 2.0;         // 日志增长2倍触发快照
    };

    SmartSnapshotManager(braft::Node* node, const SnapshotOptions& options)
        : _node(node), _options(options), _last_snapshot_time(0),
          _last_snapshot_log_size(0) {}

    // 检查是否需要创建快照
    bool should_create_snapshot() {
        time_t now = time(nullptr);

        // 获取当前日志信息
        int64_t current_log_size = get_log_size();
        int64_t current_log_entries = get_log_entries();

        // 检查时间间隔
        if (now - _last_snapshot_time >= _options.snapshot_interval_s) {
            LOG(INFO) << "Snapshot triggered by time interval";
            return true;
        }

        // 检查日志大小
        if (current_log_size >= _options.max_log_size) {
            LOG(INFO) << "Snapshot triggered by log size: " << current_log_size;
            return true;
        }

        // 检查日志条目数
        if (current_log_entries >= _options.max_log_entries) {
            LOG(INFO) << "Snapshot triggered by log entries: " << current_log_entries;
            return true;
        }

        // 检查日志增长率
        if (_last_snapshot_log_size > 0 &&
            current_log_size >= _last_snapshot_log_size * _options.log_growth_threshold &&
            now - _last_snapshot_time >= _options.min_snapshot_interval_s) {
            LOG(INFO) << "Snapshot triggered by log growth: "
                     << _last_snapshot_log_size << " -> " << current_log_size;
            return true;
        }

        return false;
    }

    // 创建快照
    void create_snapshot() {
        if (_creating_snapshot.load()) {
            LOG(WARNING) << "Snapshot creation already in progress";
            return;
        }

        _creating_snapshot.store(true);

        SnapshotClosure* done = new SnapshotClosure([this](bool success) {
            _creating_snapshot.store(false);
            if (success) {
                _last_snapshot_time = time(nullptr);
                _last_snapshot_log_size = get_log_size();
                LOG(INFO) << "Snapshot created successfully";
            } else {
                LOG(ERROR) << "Failed to create snapshot";
            }
        });

        _node->snapshot(done);
    }

    // 定期检查（应该在单独线程中调用）
    void periodic_check() {
        while (!_stopped.load()) {
            if (should_create_snapshot()) {
                create_snapshot();
            }
            bthread_usleep(60 * 1000 * 1000);  // 每分钟检查一次
        }
    }

    void stop() {
        _stopped.store(true);
    }

private:
    int64_t get_log_size() {
        // 实际实现需要从 braft 获取日志大小
        // 这里返回估算值
        return 0;
    }

    int64_t get_log_entries() {
        // 实际实现需要从 braft 获取日志条目数
        return 0;
    }

    class SnapshotClosure : public braft::Closure {
    public:
        SnapshotClosure(std::function<void(bool)> callback)
            : _callback(callback) {}

        void Run() override {
            _callback(status().ok());
            delete this;
        }

    private:
        std::function<void(bool)> _callback;
    };

    braft::Node* _node;
    SnapshotOptions _options;
    std::atomic<bool> _creating_snapshot{false};
    std::atomic<bool> _stopped{false};
    time_t _last_snapshot_time;
    int64_t _last_snapshot_log_size;
};
```

### 3.4 性能优化

#### 3.4.1 批量提交优化

```cpp
class BatchCommitter {
public:
    struct BatchOptions {
        int32_t max_batch_size = 1000;      // 最大批量大小
        int32_t max_batch_bytes = 1024 * 1024;  // 最大批量字节数
        int32_t batch_timeout_ms = 10;       // 批量超时
        int32_t max_inflight_batches = 10;   // 最大并发批次
    };

    BatchCommitter(braft::Node* node, const BatchOptions& options)
        : _node(node), _options(options), _inflight_batches(0) {

        // 启动批量处理线程
        _batch_thread = std::thread([this] { batch_worker(); });
    }

    ~BatchCommitter() {
        _stopped.store(true);
        _cv.notify_all();
        if (_batch_thread.joinable()) {
            _batch_thread.join();
        }
    }

    // 提交单个操作
    void submit(const butil::IOBuf& data, braft::Closure* done) {
        PendingOperation op{data, done, butil::gettimeofday_us()};

        {
            std::unique_lock<std::mutex> lock(_mutex);
            _pending_ops.push_back(std::move(op));
        }

        _cv.notify_one();
    }

private:
    struct PendingOperation {
        butil::IOBuf data;
        braft::Closure* done;
        int64_t submit_time_us;
    };

    struct Batch {
        std::vector<PendingOperation> operations;
        butil::IOBuf combined_data;
        int64_t total_bytes = 0;
    };

    void batch_worker() {
        while (!_stopped.load()) {
            std::unique_lock<std::mutex> lock(_mutex);

            // 等待操作或超时
            _cv.wait_for(lock, std::chrono::milliseconds(_options.batch_timeout_ms),
                        [this] { return !_pending_ops.empty() || _stopped.load(); });

            if (_stopped.load()) break;

            if (_pending_ops.empty()) continue;

            // 检查是否可以创建新批次
            if (_inflight_batches.load() >= _options.max_inflight_batches) {
                continue;
            }

            // 构建批次
            Batch batch = build_batch();
            lock.unlock();

            if (!batch.operations.empty()) {
                submit_batch(std::move(batch));
            }
        }
    }

    Batch build_batch() {
        Batch batch;
        int64_t now_us = butil::gettimeofday_us();

        auto it = _pending_ops.begin();
        while (it != _pending_ops.end() &&
               batch.operations.size() < _options.max_batch_size &&
               batch.total_bytes < _options.max_batch_bytes) {

            // 检查是否超时（强制提交）
            bool timeout = (now_us - it->submit_time_us) >=
                          (_options.batch_timeout_ms * 1000);

            if (!timeout && batch.operations.size() > 0 &&
                batch.total_bytes + it->data.size() > _options.max_batch_bytes) {
                break;  // 避免超过大小限制
            }

            batch.operations.push_back(std::move(*it));
            batch.total_bytes += it->data.size();

            // 合并数据
            batch.combined_data.append(it->data);

            it = _pending_ops.erase(it);

            if (timeout) break;  // 超时操作优先处理
        }

        return batch;
    }

    void submit_batch(Batch batch) {
        _inflight_batches.fetch_add(1);

        // 创建批量回调
        BatchClosure* done = new BatchClosure(
            std::move(batch.operations),
            [this](bool success) {
                _inflight_batches.fetch_sub(1);
            }
        );

        // 提交到 Raft
        braft::Task task;
        task.data = &batch.combined_data;
        task.done = done;

        _node->apply(task);

        LOG(INFO) << "Submitted batch with " << batch.operations.size()
                 << " operations, " << batch.total_bytes << " bytes";
    }

    class BatchClosure : public braft::Closure {
    public:
        BatchClosure(std::vector<PendingOperation> operations,
                    std::function<void(bool)> callback)
            : _operations(std::move(operations)), _callback(callback) {}

        void Run() override {
            bool success = status().ok();

            // 调用所有原始回调
            for (auto& op : _operations) {
                if (op.done) {
                    op.done->status() = status();
                    op.done->Run();
                }
            }

            _callback(success);
            delete this;
        }

    private:
        std::vector<PendingOperation> _operations;
        std::function<void(bool)> _callback;
    };

    braft::Node* _node;
    BatchOptions _options;

    std::mutex _mutex;
    std::condition_variable _cv;
    std::vector<PendingOperation> _pending_ops;

    std::atomic<bool> _stopped{false};
    std::atomic<int32_t> _inflight_batches{0};
    std::thread _batch_thread;
};
```

#### 3.4.2 读优化

```cpp
class ReadOptimizer {
public:
    // 线性一致性读
    class LinearizableReader {
    public:
        LinearizableReader(braft::Node* node) : _node(node) {}

        // 执行线性一致性读
        void read(const std::function<void(bool, const std::string&)>& callback) {
            if (!_node->is_leader()) {
                callback(false, "Not leader");
                return;
            }

            ReadClosure* done = new ReadClosure(callback);
            _node->read_index(butil::IOBuf(), done);
        }

    private:
        class ReadClosure : public braft::ReadIndexClosure {
        public:
            ReadClosure(std::function<void(bool, const std::string&)> callback)
                : _callback(callback) {}

            void Run() override {
                if (status.ok()) {
                    // 这里可以安全地读取状态机数据
                    _callback(true, "OK");
                } else {
                    _callback(false, status.error_str());
                }
                delete this;
            }

        private:
            std::function<void(bool, const std::string&)> _callback;
        };

        braft::Node* _node;
    };

    // 租约读（降低延迟，但一致性稍弱）
    class LeaseReader {
    public:
        LeaseReader(braft::Node* node, int64_t lease_timeout_ms = 9000)
            : _node(node), _lease_timeout_ms(lease_timeout_ms) {}

        void read(const std::function<void(bool, const std::string&)>& callback) {
            if (!_node->is_leader()) {
                callback(false, "Not leader");
                return;
            }

            int64_t now_ms = butil::gettimeofday_ms();
            if (now_ms - _last_heartbeat_ms < _lease_timeout_ms) {
                // 租约有效，直接读取
                callback(true, "OK");
            } else {
                // 租约过期，需要发送心跳确认 Leader 身份
                refresh_lease([callback](bool success) {
                    callback(success, success ? "OK" : "Lease expired");
                });
            }
        }

        void on_heartbeat_success() {
            _last_heartbeat_ms = butil::gettimeofday_ms();
        }

    private:
        void refresh_lease(const std::function<void(bool)>& callback) {
            // 发送心跳以刷新租约
            HeartbeatClosure* done = new HeartbeatClosure([this, callback](bool success) {
                if (success) {
                    _last_heartbeat_ms = butil::gettimeofday_ms();
                }
                callback(success);
            });

            // 这里需要向 Followers 发送心跳
            // 实际实现需要更复杂的逻辑
            braft::Task task;
            task.data = nullptr;  // 空任务，仅用于确认 Leader 身份
            task.done = done;

            _node->apply(task);
        }

        class HeartbeatClosure : public braft::Closure {
        public:
            HeartbeatClosure(std::function<void(bool)> callback)
                : _callback(callback) {}

            void Run() override {
                _callback(status().ok());
                delete this;
            }

        private:
            std::function<void(bool)> _callback;
        };

        braft::Node* _node;
        int64_t _lease_timeout_ms;
        std::atomic<int64_t> _last_heartbeat_ms{0};
    };

    // 随机读（最终一致性，但延迟最低）
    class EventualReader {
    public:
        EventualReader(const std::vector<braft::Node*>& nodes)
            : _nodes(nodes) {}

        void read(const std::function<void(bool, const std::string&)>& callback) {
            if (_nodes.empty()) {
                callback(false, "No nodes available");
                return;
            }

            // 随机选择一个节点进行读取
            size_t index = rand() % _nodes.size();
            braft::Node* node = _nodes[index];

            // 直接读取状态机数据（不等待一致性确认）
            callback(true, "OK");
        }

    private:
        std::vector<braft::Node*> _nodes;
    };
};
```

## 四、最佳实践

### 4.1 错误处理和恢复

#### 4.1.1 故障检测

```cpp
class FailureDetector {
public:
    enum FailureType {
        LEADER_ELECTION_TIMEOUT,
        LOG_REPLICATION_FAILURE,
        SNAPSHOT_FAILURE,
        CONFIGURATION_CHANGE_FAILURE,
        DISK_IO_ERROR,
        NETWORK_PARTITION
    };

    struct FailureEvent {
        FailureType type;
        std::string description;
        int64_t timestamp;
        butil::Status status;
    };

    class FailureHandler {
    public:
        virtual ~FailureHandler() = default;
        virtual void handle_failure(const FailureEvent& event) = 0;
    };

    FailureDetector(braft::Node* node) : _node(node) {
        _monitor_thread = std::thread([this] { monitor_loop(); });
    }

    ~FailureDetector() {
        _stopped.store(true);
        if (_monitor_thread.joinable()) {
            _monitor_thread.join();
        }
    }

    void add_handler(std::shared_ptr<FailureHandler> handler) {
        std::lock_guard<std::mutex> lock(_handlers_mutex);
        _handlers.push_back(handler);
    }

private:
    void monitor_loop() {
        int64_t last_leader_check = 0;
        int64_t last_health_check = 0;

        while (!_stopped.load()) {
            int64_t now = butil::gettimeofday_ms();

            // 检查 Leader 选举超时
            if (now - last_leader_check > 5000) {  // 5秒检查一次
                check_leader_election();
                last_leader_check = now;
            }

            // 检查节点健康状态
            if (now - last_health_check > 10000) {  // 10秒检查一次
                check_node_health();
                last_health_check = now;
            }

            bthread_usleep(1000 * 1000);  // 1秒
        }
    }

    void check_leader_election() {
        if (!_node->is_leader()) {
            braft::PeerId leader = _node->leader_id();
            if (leader.is_empty()) {
                // 没有 Leader，可能选举超时
                notify_failure({
                    LEADER_ELECTION_TIMEOUT,
                    "No leader elected for extended period",
                    butil::gettimeofday_ms(),
                    butil::Status(ENOENT, "No leader")
                });
            }
        }
    }

    void check_node_health() {
        // 检查磁盘空间
        struct statvfs stat;
        if (statvfs(_data_dir.c_str(), &stat) == 0) {
            double free_space_ratio = static_cast<double>(stat.f_bavail) / stat.f_blocks;
            if (free_space_ratio < 0.1) {  // 磁盘空间不足10%
                notify_failure({
                    DISK_IO_ERROR,
                    "Disk space critically low: " + std::to_string(free_space_ratio * 100) + "%",
                    butil::gettimeofday_ms(),
                    butil::Status(ENOSPC, "Disk space low")
                });
            }
        }
    }

    void notify_failure(const FailureEvent& event) {
        LOG(ERROR) << "Failure detected: " << event.description;

        std::lock_guard<std::mutex> lock(_handlers_mutex);
        for (auto& handler : _handlers) {
            if (auto h = handler.lock()) {
                h->handle_failure(event);
            }
        }
    }

    braft::Node* _node;
    std::string _data_dir;
    std::atomic<bool> _stopped{false};
    std::thread _monitor_thread;

    std::mutex _handlers_mutex;
    std::vector<std::weak_ptr<FailureHandler>> _handlers;
};

// 自动恢复处理器
class AutoRecoveryHandler : public FailureDetector::FailureHandler {
public:
    AutoRecoveryHandler(braft::Node* node) : _node(node) {}

    void handle_failure(const FailureDetector::FailureEvent& event) override {
        switch (event.type) {
            case FailureDetector::LEADER_ELECTION_TIMEOUT:
                handle_leader_election_timeout();
                break;

            case FailureDetector::LOG_REPLICATION_FAILURE:
                handle_log_replication_failure();
                break;

            case FailureDetector::SNAPSHOT_FAILURE:
                handle_snapshot_failure();
                break;

            case FailureDetector::DISK_IO_ERROR:
                handle_disk_error();
                break;

            default:
                LOG(WARNING) << "Unhandled failure type: " << event.type;
        }
    }

private:
    void handle_leader_election_timeout() {
        // 尝试手动触发选举
        LOG(INFO) << "Attempting to trigger leader election";
        _node->vote(0);  // 发起选举
    }

    void handle_log_replication_failure() {
        // 检查是否需要创建快照来帮助落后的节点
        LOG(INFO) << "Creating snapshot to help log replication";
        _node->snapshot(nullptr);
    }

    void handle_snapshot_failure() {
        // 重试快照创建
        LOG(INFO) << "Retrying snapshot creation";
        bthread_usleep(5 * 1000 * 1000);  // 等待5秒
        _node->snapshot(nullptr);
    }

    void handle_disk_error() {
        // 磁盘错误比较严重，可能需要人工干预
        LOG(FATAL) << "Disk error detected, manual intervention required";
        // 可以考虑优雅关闭节点
    }

    braft::Node* _node;
};
```

### 4.2 监控和观测

#### 4.2.1 指标收集

```cpp
class RaftMetrics {
public:
    struct NodeMetrics {
        // 基础状态
        bool is_leader = false;
        int64_t current_term = 0;
        int64_t last_log_index = 0;
        int64_t commit_index = 0;

        // 性能指标
        int64_t apply_ops_per_second = 0;
        int64_t apply_latency_us = 0;
        int64_t log_replication_latency_us = 0;

        // 资源使用
        size_t log_storage_size = 0;
        size_t snapshot_size = 0;
        int32_t active_connections = 0;

        // 错误统计
        int64_t election_failures = 0;
        int64_t log_replication_failures = 0;
        int64_t snapshot_failures = 0;
    };

    RaftMetrics(braft::Node* node)
        : _node(node), _start_time(butil::gettimeofday_us()) {
        _metrics_thread = std::thread([this] { metrics_loop(); });
    }

    ~RaftMetrics() {
        _stopped.store(true);
        if (_metrics_thread.joinable()) {
            _metrics_thread.join();
        }
    }

    NodeMetrics get_metrics() const {
        std::lock_guard<std::mutex> lock(_metrics_mutex);
        return _current_metrics;
    }

    // 输出 Prometheus 格式的指标
    std::string to_prometheus() const {
        NodeMetrics metrics = get_metrics();
        std::ostringstream oss;

        oss << "# HELP raft_is_leader Whether this node is the leader\n";
        oss << "raft_is_leader " << (metrics.is_leader ? 1 : 0) << "\n";

        oss << "# HELP raft_current_term Current Raft term\n";
        oss << "raft_current_term " << metrics.current_term << "\n";

        oss << "# HELP raft_last_log_index Last log index\n";
        oss << "raft_last_log_index " << metrics.last_log_index << "\n";

        oss << "# HELP raft_commit_index Last committed log index\n";
        oss << "raft_commit_index " << metrics.commit_index << "\n";

        oss << "# HELP raft_apply_ops_per_second Operations applied per second\n";
        oss << "raft_apply_ops_per_second " << metrics.apply_ops_per_second << "\n";

        oss << "# HELP raft_apply_latency_microseconds Apply latency in microseconds\n";
        oss << "raft_apply_latency_microseconds " << metrics.apply_latency_us << "\n";

        oss << "# HELP raft_log_storage_size_bytes Log storage size in bytes\n";
        oss << "raft_log_storage_size_bytes " << metrics.log_storage_size << "\n";

        oss << "# HELP raft_election_failures_total Total election failures\n";
        oss << "raft_election_failures_total " << metrics.election_failures << "\n";

        return oss.str();
    }

    void record_apply_operation(int64_t latency_us) {
        std::lock_guard<std::mutex> lock(_metrics_mutex);
        _apply_operations.push_back({butil::gettimeofday_us(), latency_us});

        // 保留最近1分钟的数据
        int64_t cutoff = butil::gettimeofday_us() - 60 * 1000 * 1000;
        _apply_operations.erase(
            std::remove_if(_apply_operations.begin(), _apply_operations.end(),
                          [cutoff](const ApplyRecord& r) { return r.timestamp < cutoff; }),
            _apply_operations.end()
        );
    }

    void record_election_failure() {
        std::lock_guard<std::mutex> lock(_metrics_mutex);
        _current_metrics.election_failures++;
    }

private:
    struct ApplyRecord {
        int64_t timestamp;
        int64_t latency_us;
    };

    void metrics_loop() {
        while (!_stopped.load()) {
            update_metrics();
            bthread_usleep(5 * 1000 * 1000);  // 5秒更新一次
        }
    }

    void update_metrics() {
        std::lock_guard<std::mutex> lock(_metrics_mutex);

        // 更新基础状态
        _current_metrics.is_leader = _node->is_leader();

        // 计算 QPS
        int64_t now = butil::gettimeofday_us();
        int64_t window_start = now - 60 * 1000 * 1000;  // 1分钟窗口

        auto valid_records = std::count_if(
            _apply_operations.begin(), _apply_operations.end(),
            [window_start](const ApplyRecord& r) { return r.timestamp >= window_start; }
        );

        _current_metrics.apply_ops_per_second = valid_records / 60;

        // 计算平均延迟
        if (!_apply_operations.empty()) {
            int64_t total_latency = 0;
            for (const auto& record : _apply_operations) {
                if (record.timestamp >= window_start) {
                    total_latency += record.latency_us;
                }
            }
            _current_metrics.apply_latency_us =
                valid_records > 0 ? total_latency / valid_records : 0;
        }

        // 更新存储大小（需要从实际存储获取）
        update_storage_metrics();
    }

    void update_storage_metrics() {
        // 这里需要从实际存储后端获取大小信息
        // 具体实现依赖于存储配置
    }

    braft::Node* _node;
    int64_t _start_time;

    mutable std::mutex _metrics_mutex;
    NodeMetrics _current_metrics;
    std::vector<ApplyRecord> _apply_operations;

    std::atomic<bool> _stopped{false};
    std::thread _metrics_thread;
};

// HTTP 指标服务器
class MetricsServer {
public:
    MetricsServer(RaftMetrics* metrics, int port)
        : _metrics(metrics), _port(port) {}

    int start() {
        brpc::ServerOptions options;
        if (_server.AddService(&_service, brpc::SERVER_DOESNT_OWN_SERVICE) != 0) {
            LOG(ERROR) << "Failed to add metrics service";
            return -1;
        }

        if (_server.Start(_port, &options) != 0) {
            LOG(ERROR) << "Failed to start metrics server on port " << _port;
            return -1;
        }

        LOG(INFO) << "Metrics server started on port " << _port;
        return 0;
    }

private:
    class MetricsService : public brpc::HttpService {
    public:
        MetricsService(RaftMetrics* metrics) : _metrics(metrics) {}

        void default_method(google::protobuf::RpcController* cntl_base,
                           const brpc::HttpRequest*,
                           brpc::HttpResponse*,
                           google::protobuf::Closure* done) override {
            brpc::ClosureGuard done_guard(done);
            brpc::Controller* cntl = static_cast<brpc::Controller*>(cntl_base);

            cntl->http_response().set_content_type("text/plain");
            cntl->http_response().set_status_code(brpc::HTTP_STATUS_OK);

            std::string metrics = _metrics->to_prometheus();
            cntl->response_attachment().append(metrics);
        }

    private:
        RaftMetrics* _metrics;
    };

    RaftMetrics* _metrics;
    int _port;
    brpc::Server _server;
    MetricsService _service{_metrics};
};
```

### 4.3 生产环境部署

#### 4.3.1 配置优化

```cpp
class ProductionConfig {
public:
    // 生产环境推荐配置
    static braft::NodeOptions get_production_options(const std::string& data_dir) {
        braft::NodeOptions options;

        // 存储配置
        options.log_uri = data_dir + "/log";
        options.raft_meta_uri = data_dir + "/raft_meta";
        options.snapshot_uri = data_dir + "/snapshot";

        // 选举配置
        options.election_timeout_ms = 1000;        // 1秒选举超时
        options.heartbeat_interval_ms = 250;       // 250ms心跳间隔
        options.apply_batch = 32;                  // 批量应用32个操作

        // 快照配置
        options.snapshot_interval_s = 3600;        // 1小时快照间隔
        options.snapshot_throttle = nullptr;       // 不限制快照速度

        // 日志配置
        options.max_byte_count_per_rpc = 128 * 1024;  // 128KB per RPC
        options.max_entries_per_rpc = 1024;           // 1024 entries per RPC
        options.max_body_size = 512 * 1024;           // 512KB max body

        // 性能优化
        options.sync = true;                       // 同步写入（保证持久性）
        options.sync_meta = true;                  // 同步写入元数据

        // 启用内置服务
        options.disable_cli = false;               // 启用 CLI

        return options;
    }

    // 高性能配置（牺牲一些持久性保证）
    static braft::NodeOptions get_high_performance_options(const std::string& data_dir) {
        auto options = get_production_options(data_dir);

        // 减少同步写入
        options.sync = false;                      // 异步写入（性能优先）
        options.sync_meta = false;

        // 增加批量大小
        options.apply_batch = 128;
        options.max_entries_per_rpc = 4096;

        // 减少选举超时
        options.election_timeout_ms = 500;
        options.heartbeat_interval_ms = 100;

        return options;
    }

    // 高可用配置（最大化可靠性）
    static braft::NodeOptions get_high_availability_options(const std::string& data_dir) {
        auto options = get_production_options(data_dir);

        // 更保守的同步设置
        options.sync = true;
        options.sync_meta = true;

        // 更频繁的快照
        options.snapshot_interval_s = 1800;        // 30分钟快照

        // 更小的批量大小（更快的故障检测）
        options.apply_batch = 16;

        // 更长的选举超时（避免网络抖动导致的选举）
        options.election_timeout_ms = 2000;
        options.heartbeat_interval_ms = 500;

        return options;
    }
};

// 集群部署辅助工具
class ClusterDeployer {
public:
    struct NodeConfig {
        std::string node_id;
        std::string listen_addr;
        std::string raft_addr;
        std::string data_dir;
    };

    // 部署集群
    static std::vector<CounterServer*> deploy_cluster(
        const std::vector<NodeConfig>& configs) {

        std::vector<CounterServer*> servers;

        // 构建初始 peers 列表
        std::string peers;
        for (size_t i = 0; i < configs.size(); ++i) {
            if (i > 0) peers += ",";
            peers += configs[i].raft_addr;
        }

        // 启动所有节点
        for (const auto& config : configs) {
            CounterServer* server = new CounterServer();

            // 创建数据目录
            system(("mkdir -p " + config.data_dir).c_str());

            if (server->start(config.listen_addr, config.raft_addr,
                             peers, config.data_dir) != 0) {
                LOG(ERROR) << "Failed to start server " << config.node_id;
                delete server;
                continue;
            }

            servers.push_back(server);
            LOG(INFO) << "Started server " << config.node_id
                     << " at " << config.listen_addr;
        }

        return servers;
    }

    // 滚动升级
    static bool rolling_upgrade(std::vector<CounterServer*>& servers,
                               const std::string& new_binary_path) {
        for (size_t i = 0; i < servers.size(); ++i) {
            LOG(INFO) << "Upgrading server " << i;

            // 1. 停止当前服务器
            delete servers[i];

            // 2. 替换二进制文件
            std::string backup_cmd = "cp " + new_binary_path + " ./server_" + std::to_string(i);
            if (system(backup_cmd.c_str()) != 0) {
                LOG(ERROR) << "Failed to copy new binary";
                return false;
            }

            // 3. 启动新版本
            // 这里需要重新启动服务器实例
            // 实际实现需要保存启动参数

            // 4. 等待节点重新加入集群
            bthread_usleep(10 * 1000 * 1000);  // 等待10秒

            LOG(INFO) << "Server " << i << " upgraded successfully";
        }

        return true;
    }

    // 集群健康检查
    static bool health_check(const std::vector<CounterServer*>& servers) {
        int leader_count = 0;
        int healthy_count = 0;

        for (const auto* server : servers) {
            if (server->is_leader()) {
                leader_count++;
            }

            // 简单的健康检查
            try {
                server->get_counter_local();
                healthy_count++;
            } catch (...) {
                LOG(WARNING) << "Server health check failed";
            }
        }

        bool healthy = (leader_count == 1) &&
                      (healthy_count >= (servers.size() + 1) / 2);

        LOG(INFO) << "Cluster health: " << healthy_count << "/" << servers.size()
                 << " healthy, " << leader_count << " leaders";

        return healthy;
    }
};
```

## 五、故障排查和调试

### 5.1 常见问题诊断

#### 5.1.1 选举问题

```cpp
class ElectionDiagnostics {
public:
    static void diagnose_election_issues(braft::Node* node) {
        LOG(INFO) << "=== Election Diagnostics ===";

        // 检查当前状态
        bool is_leader = node->is_leader();
        braft::PeerId leader_id = node->leader_id();

        LOG(INFO) << "Current state - Is leader: " << is_leader
                 << ", Leader: " << leader_id;

        // 检查配置
        braft::Configuration conf;
        node->list_peers(&conf);

        LOG(INFO) << "Cluster configuration:";
        for (auto it = conf.begin(); it != conf.end(); ++it) {
            LOG(INFO) << "  Peer: " << *it;
        }

        // 检查网络连通性
        check_network_connectivity(conf);

        // 检查时钟同步
        check_clock_sync();

        // 检查磁盘IO
        check_disk_io();
    }

private:
    static void check_network_connectivity(const braft::Configuration& conf) {
        LOG(INFO) << "Checking network connectivity...";

        for (auto it = conf.begin(); it != conf.end(); ++it) {
            std::string addr = it->addr.ip.to_string() + ":" +
                              std::to_string(it->addr.port);

            // 简单的连通性检查
            brpc::Channel channel;
            brpc::ChannelOptions options;
            options.timeout_ms = 1000;

            if (channel.Init(addr.c_str(), &options) == 0) {
                LOG(INFO) << "  " << addr << ": OK";
            } else {
                LOG(ERROR) << "  " << addr << ": FAILED";
            }
        }
    }

    static void check_clock_sync() {
        // 检查系统时钟是否同步
        LOG(INFO) << "System time: " << time(nullptr);
        // 在生产环境中，应该检查 NTP 同步状态
    }

    static void check_disk_io() {
        // 检查磁盘 IO 性能
        auto start = std::chrono::high_resolution_clock::now();

        std::string test_file = "/tmp/braft_io_test";
        std::ofstream file(test_file);
        if (file.is_open()) {
            file << "test data";
            file.flush();
            file.close();
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end - start).count();

        LOG(INFO) << "Disk write latency: " << duration << "us";

        unlink(test_file.c_str());
    }
};
```

#### 5.1.2 性能问题诊断

```cpp
class PerformanceDiagnostics {
public:
    struct PerformanceReport {
        double apply_latency_p50_ms = 0;
        double apply_latency_p99_ms = 0;
        double throughput_ops_per_sec = 0;
        double log_replication_latency_ms = 0;
        size_t pending_tasks = 0;
        double cpu_usage_percent = 0;
        double memory_usage_mb = 0;
    };

    static PerformanceReport generate_report(braft::Node* node) {
        PerformanceReport report;

        // 收集延迟统计
        collect_latency_stats(report);

        // 收集吞吐量统计
        collect_throughput_stats(report);

        // 收集系统资源使用
        collect_system_stats(report);

        // 收集 Raft 特定指标
        collect_raft_stats(node, report);

        return report;
    }

    static void print_report(const PerformanceReport& report) {
        LOG(INFO) << "=== Performance Report ===";
        LOG(INFO) << "Apply Latency P50: " << report.apply_latency_p50_ms << "ms";
        LOG(INFO) << "Apply Latency P99: " << report.apply_latency_p99_ms << "ms";
        LOG(INFO) << "Throughput: " << report.throughput_ops_per_sec << " ops/sec";
        LOG(INFO) << "Log Replication Latency: " << report.log_replication_latency_ms << "ms";
        LOG(INFO) << "Pending Tasks: " << report.pending_tasks;
        LOG(INFO) << "CPU Usage: " << report.cpu_usage_percent << "%";
        LOG(INFO) << "Memory Usage: " << report.memory_usage_mb << "MB";
        LOG(INFO) << "========================";
    }

    static std::vector<std::string> analyze_bottlenecks(const PerformanceReport& report) {
        std::vector<std::string> issues;

        if (report.apply_latency_p99_ms > 100) {
            issues.push_back("High apply latency detected - consider optimizing state machine");
        }

        if (report.log_replication_latency_ms > 50) {
            issues.push_back("High log replication latency - check network or reduce batch size");
        }

        if (report.pending_tasks > 1000) {
            issues.push_back("High number of pending tasks - system may be overloaded");
        }

        if (report.cpu_usage_percent > 80) {
            issues.push_back("High CPU usage - consider scaling or optimizing");
        }

        if (report.memory_usage_mb > 1024) {
            issues.push_back("High memory usage - check for memory leaks");
        }

        if (report.throughput_ops_per_sec < 100) {
            issues.push_back("Low throughput - investigate performance bottlenecks");
        }

        return issues;
    }

private:
    static void collect_latency_stats(PerformanceReport& report) {
        // 这里需要从实际的延迟统计中收集数据
        // 示例数据
        report.apply_latency_p50_ms = 5.2;
        report.apply_latency_p99_ms = 25.8;
    }

    static void collect_throughput_stats(PerformanceReport& report) {
        // 从指标收集器获取吞吐量数据
        report.throughput_ops_per_sec = 1500;
    }

    static void collect_system_stats(PerformanceReport& report) {
        // 获取系统资源使用情况
        std::ifstream stat_file("/proc/stat");
        std::ifstream mem_file("/proc/meminfo");

        // 简化的系统统计收集
        report.cpu_usage_percent = 35.2;
        report.memory_usage_mb = 512.7;
    }

    static void collect_raft_stats(braft::Node* node, PerformanceReport& report) {
        // 收集 Raft 相关统计
        report.log_replication_latency_ms = 12.3;
        report.pending_tasks = 45;
    }
};
```

### 5.2 调试工具

#### 5.2.1 状态查看器

```cpp
class StateViewer {
public:
    static void dump_node_state(braft::Node* node, std::ostream& os) {
        os << "=== Node State Dump ===" << std::endl;

        // 基本信息
        os << "Node ID: " << node->node_id() << std::endl;
        os << "Is Leader: " << (node->is_leader() ? "Yes" : "No") << std::endl;
        os << "Leader ID: " << node->leader_id() << std::endl;

        // 配置信息
        braft::Configuration conf;
        node->list_peers(&conf);
        os << "Cluster Members:" << std::endl;
        for (auto it = conf.begin(); it != conf.end(); ++it) {
            os << "  " << *it << std::endl;
        }

        // 日志信息
        dump_log_info(node, os);

        // 状态机信息
        dump_state_machine_info(node, os);

        os << "======================" << std::endl;
    }

    static void dump_log_info(braft::Node* node, std::ostream& os) {
        os << "Log Information:" << std::endl;
        // 这里需要从 braft 内部获取日志信息
        // 由于接口限制，这里只能输出可访问的信息
        os << "  Last Log Index: " << "N/A" << std::endl;
        os << "  Commit Index: " << "N/A" << std::endl;
        os << "  Last Applied: " << "N/A" << std::endl;
    }

    static void dump_state_machine_info(braft::Node* node, std::ostream& os) {
        os << "State Machine Information:" << std::endl;
        // 这里需要从状态机获取信息
        os << "  Implementation specific data would go here" << std::endl;
    }

    // 导出配置历史
    static void dump_config_history(braft::Node* node, std::ostream& os) {
        os << "Configuration Change History:" << std::endl;
        // 配置变更历史需要自己维护
        os << "  Implementation needed" << std::endl;
    }
};

// 交互式调试器
class InteractiveDebugger {
public:
    InteractiveDebugger(braft::Node* node) : _node(node) {}

    void start_interactive_session() {
        std::cout << "braft Interactive Debugger" << std::endl;
        std::cout << "Type 'help' for available commands" << std::endl;

        std::string line;
        while (std::getline(std::cin, line)) {
            if (line == "quit" || line == "exit") {
                break;
            }

            process_command(line);
        }
    }

private:
    void process_command(const std::string& cmd) {
        std::istringstream iss(cmd);
        std::string command;
        iss >> command;

        if (command == "help") {
            show_help();
        } else if (command == "status") {
            show_status();
        } else if (command == "peers") {
            show_peers();
        } else if (command == "logs") {
            show_logs();
        } else if (command == "snapshot") {
            create_snapshot();
        } else if (command == "transfer") {
            std::string target;
            iss >> target;
            transfer_leadership(target);
        } else if (command == "add_peer") {
            std::string peer;
            iss >> peer;
            add_peer(peer);
        } else if (command == "remove_peer") {
            std::string peer;
            iss >> peer;
            remove_peer(peer);
        } else {
            std::cout << "Unknown command: " << command << std::endl;
        }
    }

    void show_help() {
        std::cout << "Available commands:" << std::endl;
        std::cout << "  status         - Show node status" << std::endl;
        std::cout << "  peers          - Show cluster members" << std::endl;
        std::cout << "  logs           - Show log information" << std::endl;
        std::cout << "  snapshot       - Create snapshot" << std::endl;
        std::cout << "  transfer <peer> - Transfer leadership" << std::endl;
        std::cout << "  add_peer <addr> - Add cluster member" << std::endl;
        std::cout << "  remove_peer <addr> - Remove cluster member" << std::endl;
        std::cout << "  quit/exit      - Exit debugger" << std::endl;
    }

    void show_status() {
        StateViewer::dump_node_state(_node, std::cout);
    }

    void show_peers() {
        braft::Configuration conf;
        _node->list_peers(&conf);

        std::cout << "Cluster Members:" << std::endl;
        for (auto it = conf.begin(); it != conf.end(); ++it) {
            std::cout << "  " << *it;
            if (*it == _node->leader_id()) {
                std::cout << " (Leader)";
            }
            std::cout << std::endl;
        }
    }

    void show_logs() {
        std::cout << "Log information display not implemented" << std::endl;
    }

    void create_snapshot() {
        std::cout << "Creating snapshot..." << std::endl;
        _node->snapshot(nullptr);
        std::cout << "Snapshot creation initiated" << std::endl;
    }

    void transfer_leadership(const std::string& target) {
        if (target.empty()) {
            std::cout << "Usage: transfer <peer_address>" << std::endl;
            return;
        }

        braft::PeerId target_peer(target);
        std::cout << "Transferring leadership to " << target << "..." << std::endl;

        int ret = _node->transfer_leadership_to(target_peer);
        if (ret == 0) {
            std::cout << "Leadership transfer initiated" << std::endl;
        } else {
            std::cout << "Failed to transfer leadership: " << ret << std::endl;
        }
    }

    void add_peer(const std::string& peer_addr) {
        if (peer_addr.empty()) {
            std::cout << "Usage: add_peer <peer_address>" << std::endl;
            return;
        }

        std::cout << "Adding peer " << peer_addr << "..." << std::endl;

        class AddPeerClosure : public braft::Closure {
        public:
            void Run() override {
                if (status().ok()) {
                    std::cout << "Peer added successfully" << std::endl;
                } else {
                    std::cout << "Failed to add peer: " << status() << std::endl;
                }
                delete this;
            }
        };

        ConfigurationManager::add_peer(_node, peer_addr, new AddPeerClosure());
    }

    void remove_peer(const std::string& peer_addr) {
        if (peer_addr.empty()) {
            std::cout << "Usage: remove_peer <peer_address>" << std::endl;
            return;
        }

        std::cout << "Removing peer " << peer_addr << "..." << std::endl;

        class RemovePeerClosure : public braft::Closure {
        public:
            void Run() override {
                if (status().ok()) {
                    std::cout << "Peer removed successfully" << std::endl;
                } else {
                    std::cout << "Failed to remove peer: " << status() << std::endl;
                }
                delete this;
            }
        };

        ConfigurationManager::remove_peer(_node, peer_addr, new RemovePeerClosure());
    }

    braft::Node* _node;
};
```

## 六、学习资源和总结

### 6.1 深入学习路径

1. **基础阶段**（1-2周）
   - 理解 Raft 算法原理
   - 完成基础的计数器示例
   - 掌握状态机接口

2. **进阶阶段**（2-4周）
   - 实现复杂的状态机（如 KV 存储）
   - 掌握快照机制
   - 理解配置变更

3. **高级阶段**（1-2月）
   - 性能优化和调优
   - 生产环境部署
   - 故障处理和恢复

4. **专家阶段**
   - 源码阅读和定制
   - 与其他系统集成
   - 贡献开源社区

### 6.2 最佳实践总结

1. **设计原则**
   - 状态机操作要幂等
   - 日志条目要自包含
   - 避免阻塞操作

2. **性能优化**
   - 使用批量提交
   - 合理设置快照间隔
   - 优化网络和磁盘 I/O

3. **可靠性保证**
   - 确保数据持久化
   - 监控集群健康状态
   - 准备故障恢复方案

### 6.3 常见陷阱

1. **状态机非幂等**：确保重复应用相同日志条目不会产生副作用
2. **阻塞状态机**：避免在状态机中执行耗时操作
3. **忽略错误处理**：必须正确处理各种异常情况
4. **配置变更不当**：配置变更要谨慎，避免脑裂

### 6.4 参考资源

- [braft GitHub 仓库](https://github.com/baidu/braft)
- [Raft 论文](https://raft.github.io/raft.pdf)
- [braft 文档](https://github.com/baidu/braft/tree/master/docs)
- [百度 braft 实践经验](https://github.com/baidu/braft/wiki)

braft 作为生产级的 Raft 实现，为构建分布式一致性系统提供了强大的基础。通过本指南的学习，相信你已经掌握了使用 braft 构建可靠分布式系统的核心技能。记住，分布式系统的精髓在于处理各种异常情况，只有在实践中不断积累经验，才能真正掌握这门艺术。