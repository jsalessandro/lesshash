---
title: "brpc media-server 完全指南：构建高性能流媒体服务"
date: 2025-09-18T15:30:00+08:00
draft: false
tags: ["brpc", "media-server", "流媒体", "直播", "RTMP", "HLS"]
categories: ["技术分享"]
author: "lesshash"
description: "brpc media-server 是百度开源的高性能流媒体服务器，支持 RTMP、FLV、HLS 等多种协议，本文将详细介绍其使用方法和最佳实践"
---

## 一、brpc media-server 简介

### 1.1 项目概述

**brpc media-server** 是百度云开源的高性能流媒体服务器，基于 brpc 框架构建。它为构建可扩展的直播流媒体平台提供了完整的解决方案。

### 1.2 核心特性

#### 协议支持
- **RTMP 协议**：支持 RTMP 推流和拉流
- **HTTP-FLV**：提供低延迟的 HTTP-FLV 流
- **HLS 协议**：支持标准 HLS 和低延迟 HLS
- **HTTPS 支持**：全面支持加密传输

#### 架构优势
- **源站模式（Origin Server）**：处理推流和播放请求
- **边缘模式（Edge Server）**：作为代理服务器分发内容
- **高性能架构**：基于 brpc 的高并发处理能力
- **灵活配置**：丰富的配置选项满足不同场景需求

#### 功能特性
- **流标识系统**：使用 `vhost/app/stream_name` 格式标识流
- **缓冲队列**：可配置的帧队列缓冲
- **重试策略**：可配置的重试机制
- **监控接口**：基于 HTTP 的状态监控
- **音视频分离**：支持纯音频或纯视频流

## 二、环境搭建

### 2.1 系统要求

```bash
# 支持的系统
- Linux (推荐 Ubuntu 18.04+/CentOS 7+)
- macOS (用于开发测试)

# 依赖
- GCC 4.8+ 或 Clang 3.5+
- CMake 3.10+
- Git
```

### 2.2 依赖安装

#### Ubuntu/Debian 系统

```bash
# 更新包管理器
sudo apt-get update

# 安装基础依赖
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libssl-dev \
    libgflags-dev \
    libprotobuf-dev \
    libprotoc-dev \
    protobuf-compiler \
    libleveldb-dev \
    libsnappy-dev \
    libgoogle-glog-dev

# 安装 FFmpeg (用于测试)
sudo apt-get install -y ffmpeg
```

#### CentOS/RHEL 系统

```bash
# 安装 EPEL 源
sudo yum install -y epel-release

# 安装基础依赖
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    cmake3 \
    git \
    openssl-devel \
    gflags-devel \
    protobuf-devel \
    protobuf-compiler \
    leveldb-devel \
    snappy-devel \
    glog-devel

# 创建 cmake 符号链接
sudo ln -sf /usr/bin/cmake3 /usr/bin/cmake
```

### 2.3 编译 brpc

media-server 依赖 brpc，首先需要编译安装 brpc：

```bash
# 克隆 brpc 源码
git clone https://github.com/apache/brpc.git
cd brpc

# 创建构建目录
mkdir build && cd build

# 配置编译选项
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_GLOG=ON \
    -DWITH_DEBUG_SYMBOLS=OFF

# 编译（使用所有 CPU 核心）
make -j$(nproc)

# 安装到系统
sudo make install

# 更新动态链接库缓存
sudo ldconfig
```

### 2.4 编译 media-server

```bash
# 克隆 media-server 源码
git clone https://github.com/brpc/media-server.git
cd media-server

# 创建构建目录
mkdir build && cd build

# 配置编译
cmake .. -DCMAKE_BUILD_TYPE=Release

# 编译
make -j$(nproc)

# 验证编译结果
ls -la media_server
```

## 三、快速开始

### 3.1 基础启动

#### 启动源站服务器

```bash
# 基础启动（默认端口 8079）
./media_server

# 指定端口启动
./media_server --port=8080

# 启用详细日志
./media_server --v=1
```

#### 启动边缘服务器

```bash
# 作为边缘服务器启动
./media_server --edge_server=true --origin_server="192.168.1.100:8079"
```

### 3.2 基础推流和拉流测试

#### 使用 FFmpeg 推流

```bash
# 推送测试视频流
ffmpeg -re -i test_video.mp4 \
    -c:v libx264 -preset veryfast -tune zerolatency \
    -c:a aac -ar 44100 \
    -f flv rtmp://localhost:8079/live/test

# 推送摄像头直播流
ffmpeg -f v4l2 -i /dev/video0 \
    -c:v libx264 -preset ultrafast \
    -c:a aac -f flv \
    rtmp://localhost:8079/live/webcam

# 推送音频流（用于播客）
ffmpeg -f alsa -i default \
    -c:a aac -b:a 128k \
    -f flv rtmp://localhost:8079/radio/music
```

#### 播放流媒体

```bash
# 播放 RTMP 流
ffplay rtmp://localhost:8079/live/test

# 播放 HTTP-FLV 流
ffplay http://localhost:8079/live/test.flv

# 播放 HLS 流
ffplay http://localhost:8079/live/test.m3u8

# 使用 VLC 播放器
vlc rtmp://localhost:8079/live/test
```

### 3.3 Web 播放器集成

#### HTML5 播放器示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>brpc media-server 流媒体播放</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
    <h1>直播流播放器</h1>

    <!-- HLS 播放器 -->
    <div>
        <h3>HLS 播放器</h3>
        <video id="hlsPlayer" controls width="640" height="360">
            <source src="http://localhost:8079/live/test.m3u8" type="application/vnd.apple.mpegurl">
        </video>
    </div>

    <!-- HTTP-FLV 播放器 -->
    <div>
        <h3>FLV 播放器</h3>
        <video id="flvPlayer" controls width="640" height="360">
            <source src="http://localhost:8079/live/test.flv" type="video/x-flv">
        </video>
    </div>

    <script>
        // HLS.js 配置
        if (Hls.isSupported()) {
            var video = document.getElementById('hlsPlayer');
            var hls = new Hls({
                debug: true,
                enableWorker: false,
                lowLatencyMode: true,
                backBufferLength: 90
            });

            hls.loadSource('http://localhost:8079/live/test.m3u8');
            hls.attachMedia(video);

            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                console.log('HLS manifest parsed, starting playback');
                video.play();
            });

            hls.on(Hls.Events.ERROR, function(event, data) {
                console.error('HLS error:', data);
            });
        }

        // 自动重连机制
        function setupAutoReconnect(videoElement, streamUrl) {
            videoElement.addEventListener('error', function() {
                console.log('播放错误，5秒后重试...');
                setTimeout(function() {
                    videoElement.src = streamUrl + '?t=' + new Date().getTime();
                    videoElement.load();
                    videoElement.play();
                }, 5000);
            });
        }

        // 为播放器设置自动重连
        setupAutoReconnect(
            document.getElementById('flvPlayer'),
            'http://localhost:8079/live/test.flv'
        );
    </script>
</body>
</html>
```

## 四、高级配置

### 4.1 服务器配置

#### 命令行参数详解

```bash
# 基础配置
./media_server \
    --port=8079 \                    # 服务端口
    --idle_timeout_s=-1 \            # 连接空闲超时（-1表示不超时）
    --max_concurrency=0 \            # 最大并发连接数（0表示不限制）
    --internal_port=-1 \             # 内部状态端口（-1表示禁用）

# 边缘服务器配置
    --edge_server=true \             # 启用边缘模式
    --origin_server="origin:8079" \  # 源站地址

# 性能优化
    --worker_thread_num=8 \          # 工作线程数
    --io_thread_num=4 \              # IO线程数

# 日志配置
    --log_dir="./logs" \             # 日志目录
    --v=1 \                          # 日志级别
    --logbufsecs=0                   # 日志缓冲时间
```

#### 配置文件示例

```bash
# 创建配置文件 media_server.conf
cat > media_server.conf << 'EOF'
# 基础配置
port = 8079
max_concurrency = 1000
worker_thread_num = 8

# 流媒体配置
rtmp_port = 1935
http_port = 8080
enable_hls = true
enable_flv = true

# HLS 配置
hls_segment_duration = 2
hls_window_size = 10
hls_low_latency = true

# 录制配置
enable_recording = false
recording_path = "/data/recordings"

# 安全配置
enable_auth = false
auth_secret = "your_secret_key"

# 日志配置
log_level = INFO
log_file = "/var/log/media_server.log"
EOF

# 使用配置文件启动
./media_server --flagfile=media_server.conf
```

### 4.2 流媒体配置优化

#### 低延迟配置

```bash
# 低延迟直播配置
./media_server \
    --port=8079 \
    --rtmp_gop_cache=false \         # 禁用GOP缓存
    --hls_segment_duration=1 \       # 1秒分片
    --hls_window_size=3 \            # 3个分片窗口
    --buffer_time_ms=500 \           # 500ms缓冲
    --max_frame_queue_size=10        # 最大帧队列大小
```

#### 高质量配置

```bash
# 高质量直播配置
./media_server \
    --port=8079 \
    --enable_audio_only=false \      # 启用视频
    --enable_video_only=false \      # 启用音频
    --hls_segment_duration=6 \       # 6秒分片
    --hls_window_size=6 \            # 6个分片窗口
    --buffer_time_ms=3000            # 3秒缓冲
```

### 4.3 集群部署配置

#### 源站集群

```bash
# 源站1
./media_server \
    --port=8079 \
    --cluster_id="origin_cluster" \
    --node_id="origin_1" \
    --redis_host="redis.example.com" \
    --redis_port=6379

# 源站2
./media_server \
    --port=8079 \
    --cluster_id="origin_cluster" \
    --node_id="origin_2" \
    --redis_host="redis.example.com" \
    --redis_port=6379
```

#### 边缘节点部署

```bash
# 边缘节点1（北京）
./media_server \
    --port=8079 \
    --edge_server=true \
    --origin_servers="origin1:8079,origin2:8079" \
    --region="beijing" \
    --cache_size_mb=1024

# 边缘节点2（上海）
./media_server \
    --port=8079 \
    --edge_server=true \
    --origin_servers="origin1:8079,origin2:8079" \
    --region="shanghai" \
    --cache_size_mb=1024
```

## 五、监控和管理

### 5.1 HTTP 状态接口

#### 基础状态查询

```bash
# 查看服务器状态
curl "http://localhost:8079/status"

# 查看活跃流列表
curl "http://localhost:8079/api/streams"

# 查看特定流信息
curl "http://localhost:8079/api/stream/live/test"

# 查看服务器统计
curl "http://localhost:8079/api/stats" | jq .
```

#### 响应示例

```json
{
  "server_info": {
    "version": "1.0.0",
    "start_time": "2025-09-18T15:30:00Z",
    "uptime_seconds": 3600
  },
  "streams": {
    "total": 10,
    "active": 8,
    "inactive": 2
  },
  "connections": {
    "total": 150,
    "rtmp": 50,
    "http_flv": 80,
    "hls": 20
  },
  "bandwidth": {
    "incoming_mbps": 45.2,
    "outgoing_mbps": 180.8
  }
}
```

### 5.2 Prometheus 监控集成

#### 监控指标导出

```cpp
// 自定义监控指标收集器
class MediaServerMetrics {
public:
    static std::string export_prometheus_metrics() {
        std::ostringstream metrics;

        // 基础指标
        metrics << "# HELP media_server_connections_total Total connections\n";
        metrics << "media_server_connections_total{type=\"rtmp\"} " << get_rtmp_connections() << "\n";
        metrics << "media_server_connections_total{type=\"http_flv\"} " << get_flv_connections() << "\n";
        metrics << "media_server_connections_total{type=\"hls\"} " << get_hls_connections() << "\n";

        // 流统计
        metrics << "# HELP media_server_streams_active Active streams count\n";
        metrics << "media_server_streams_active " << get_active_streams() << "\n";

        // 带宽统计
        metrics << "# HELP media_server_bandwidth_bytes Bandwidth usage in bytes/sec\n";
        metrics << "media_server_bandwidth_bytes{direction=\"incoming\"} " << get_incoming_bandwidth() << "\n";
        metrics << "media_server_bandwidth_bytes{direction=\"outgoing\"} " << get_outgoing_bandwidth() << "\n";

        // 性能指标
        metrics << "# HELP media_server_cpu_usage_percent CPU usage percentage\n";
        metrics << "media_server_cpu_usage_percent " << get_cpu_usage() << "\n";

        metrics << "# HELP media_server_memory_usage_bytes Memory usage in bytes\n";
        metrics << "media_server_memory_usage_bytes " << get_memory_usage() << "\n";

        return metrics.str();
    }

private:
    static int get_rtmp_connections() { return 50; }
    static int get_flv_connections() { return 80; }
    static int get_hls_connections() { return 20; }
    static int get_active_streams() { return 8; }
    static long get_incoming_bandwidth() { return 45200000; }  // 字节/秒
    static long get_outgoing_bandwidth() { return 180800000; }
    static double get_cpu_usage() { return 45.2; }
    static long get_memory_usage() { return 512 * 1024 * 1024; }
};
```

#### HTTP 监控端点

```bash
# 添加监控端点到 media-server
curl "http://localhost:8079/metrics"
```

### 5.3 日志管理

#### 日志配置

```bash
# 启动时指定日志配置
./media_server \
    --log_dir="/var/log/media_server" \
    --v=2 \                          # 详细日志级别
    --max_log_size=100 \             # 最大日志文件大小(MB)
    --logbufsecs=0 \                 # 立即刷新日志
    --logtostderr=false              # 不输出到stderr
```

#### 日志轮转

```bash
# 配置 logrotate
sudo tee /etc/logrotate.d/media_server << 'EOF'
/var/log/media_server/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 media_server media_server
    postrotate
        killall -USR1 media_server || true
    endscript
}
EOF
```

## 六、性能优化

### 6.1 系统级优化

#### 内核参数调优

```bash
# 创建优化脚本
cat > optimize_system.sh << 'EOF'
#!/bin/bash

# 网络优化
echo 'net.core.rmem_max = 268435456' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 268435456' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 16384 268435456' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 16384 268435456' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf

# 文件描述符限制
echo 'fs.file-max = 1000000' >> /etc/sysctl.conf
echo '* soft nofile 1000000' >> /etc/security/limits.conf
echo '* hard nofile 1000000' >> /etc/security/limits.conf

# 应用配置
sysctl -p

echo "系统优化完成"
EOF

chmod +x optimize_system.sh
sudo ./optimize_system.sh
```

### 6.2 应用级优化

#### 编译优化

```bash
# 使用优化编译选项
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-O3 -march=native -mtune=native" \
    -DWITH_DEBUG_SYMBOLS=OFF \
    -DWITH_PROFILING=OFF

make -j$(nproc)
```

#### 运行时优化

```bash
# CPU 亲和性设置
taskset -c 0-7 ./media_server --worker_thread_num=8

# 内存锁定
ulimit -l unlimited
./media_server --lock_memory=true

# 实时调度优先级
sudo nice -n -10 ./media_server
```

### 6.3 负载均衡配置

#### Nginx 负载均衡

```nginx
# /etc/nginx/conf.d/media_server.conf
upstream media_servers {
    least_conn;
    server 192.168.1.10:8079 weight=3 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8079 weight=3 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8079 weight=2 max_fails=3 fail_timeout=30s;
}

# RTMP 代理配置
server {
    listen 1935;
    proxy_pass media_servers;
    proxy_timeout 1s;
    proxy_responses 1;
    proxy_bind $remote_addr transparent;
}

# HTTP-FLV 代理配置
server {
    listen 80;
    server_name stream.example.com;

    location /live/ {
        proxy_pass http://media_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 流媒体优化
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # HLS 文件缓存
    location ~* \.(m3u8|ts)$ {
        proxy_pass http://media_servers;
        proxy_cache media_cache;
        proxy_cache_valid 200 1m;
        proxy_cache_lock on;
        expires 1m;
        add_header Cache-Control "public, no-transform";
    }
}

# 缓存配置
proxy_cache_path /var/cache/nginx/media levels=1:2 keys_zone=media_cache:10m inactive=60m max_size=1g;
```

## 七、安全配置

### 7.1 访问控制

#### IP 白名单

```bash
# 启动时指定允许的IP范围
./media_server \
    --allowed_ips="192.168.1.0/24,10.0.0.0/8" \
    --block_private_ips=false
```

#### 推流认证

```cpp
// 自定义认证处理器
class StreamAuthHandler {
public:
    // RTMP 推流认证
    static bool authenticate_publish(const std::string& app,
                                   const std::string& stream_name,
                                   const std::string& auth_token) {
        // 验证推流权限
        std::string expected_token = generate_token(app, stream_name);
        return auth_token == expected_token;
    }

    // 播放认证
    static bool authenticate_play(const std::string& app,
                                const std::string& stream_name,
                                const std::string& client_ip) {
        // 检查播放权限
        return is_allowed_to_play(client_ip, app, stream_name);
    }

private:
    static std::string generate_token(const std::string& app,
                                    const std::string& stream) {
        // 实现token生成逻辑
        return hash_with_secret(app + "/" + stream + "/" + std::to_string(time(nullptr)));
    }

    static bool is_allowed_to_play(const std::string& ip,
                                 const std::string& app,
                                 const std::string& stream) {
        // 实现播放权限检查
        return check_whitelist(ip) && check_stream_permissions(app, stream);
    }
};
```

### 7.2 HTTPS/SSL 配置

#### SSL 证书配置

```bash
# 生成自签名证书（测试用）
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 启用 HTTPS
./media_server \
    --enable_ssl=true \
    --ssl_cert="cert.pem" \
    --ssl_key="key.pem" \
    --ssl_port=8443
```

#### Let's Encrypt 证书

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --standalone -d stream.example.com

# 配置自动续期
sudo crontab -e
# 添加：0 3 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl restart media_server"
```

## 八、实战案例

### 8.1 构建直播平台

#### 架构设计

```
                    ┌─────────────┐
                    │   CDN       │
                    │  (边缘节点)  │
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │ Load        │
                    │ Balancer    │
                    └─────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │ Media       │  │ Media       │  │ Media       │
   │ Server 1    │  │ Server 2    │  │ Server 3    │
   └─────────────┘  └─────────────┘  └─────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌─────────────┐
                    │   Redis     │
                    │  (状态存储)  │
                    └─────────────┘
```

#### 部署脚本

```bash
#!/bin/bash

# 部署脚本 deploy_streaming_platform.sh

# 配置变量
MEDIA_SERVERS=("192.168.1.10" "192.168.1.11" "192.168.1.12")
REDIS_HOST="192.168.1.20"
DOMAIN="stream.example.com"

echo "部署流媒体平台..."

# 1. 部署 Redis
echo "配置 Redis..."
ssh root@${REDIS_HOST} << 'EOF'
# 安装 Redis
apt-get update && apt-get install -y redis-server

# 配置 Redis
cat > /etc/redis/redis.conf << 'REDIS_CONF'
bind 0.0.0.0
port 6379
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
REDIS_CONF

systemctl restart redis-server
systemctl enable redis-server
EOF

# 2. 部署 Media Servers
for i in "${!MEDIA_SERVERS[@]}"; do
    SERVER=${MEDIA_SERVERS[$i]}
    echo "部署 Media Server $((i+1)) 到 $SERVER..."

    ssh root@${SERVER} << EOF
# 创建部署目录
mkdir -p /opt/media_server
cd /opt/media_server

# 下载并编译 media-server
git clone https://github.com/brpc/media-server.git
cd media-server
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j\$(nproc)

# 创建配置文件
cat > /opt/media_server/media_server.conf << 'CONF'
port = 8079
max_concurrency = 1000
worker_thread_num = 8
redis_host = ${REDIS_HOST}
redis_port = 6379
cluster_id = streaming_cluster
node_id = node_$((i+1))
CONF

# 创建 systemd 服务
cat > /etc/systemd/system/media_server.service << 'SERVICE'
[Unit]
Description=Media Server
After=network.target

[Service]
Type=simple
User=media_server
WorkingDirectory=/opt/media_server/media-server/build
ExecStart=/opt/media_server/media-server/build/media_server --flagfile=/opt/media_server/media_server.conf
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# 创建用户
useradd -r -s /bin/false media_server
chown -R media_server:media_server /opt/media_server

# 启动服务
systemctl daemon-reload
systemctl enable media_server
systemctl start media_server
EOF

done

# 3. 配置负载均衡器
echo "配置负载均衡器..."
# 这里可以配置 Nginx 或其他负载均衡器

echo "部署完成！"
```

### 8.2 实时互动直播

#### WebRTC 集成

```javascript
// WebRTC 推流客户端
class WebRTCStreamer {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.localStream = null;
        this.pc = null;
    }

    async startStreaming() {
        try {
            // 获取摄像头和麦克风
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    frameRate: { ideal: 30 }
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            // 创建 RTCPeerConnection
            this.pc = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' }
                ]
            });

            // 添加本地流
            this.localStream.getTracks().forEach(track => {
                this.pc.addTrack(track, this.localStream);
            });

            // 创建 offer
            const offer = await this.pc.createOffer();
            await this.pc.setLocalDescription(offer);

            // 发送到服务器
            const response = await fetch(`${this.serverUrl}/webrtc/offer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ offer: offer })
            });

            const answer = await response.json();
            await this.pc.setRemoteDescription(answer);

            console.log('WebRTC streaming started');
        } catch (error) {
            console.error('Error starting WebRTC stream:', error);
        }
    }

    stopStreaming() {
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        if (this.pc) {
            this.pc.close();
        }
    }
}

// 使用示例
const streamer = new WebRTCStreamer('http://localhost:8079');
streamer.startStreaming();
```

### 8.3 多码率自适应流

#### 转码配置

```bash
# 创建多码率转码脚本
cat > transcode_multirate.sh << 'EOF'
#!/bin/bash

INPUT_STREAM="$1"
OUTPUT_BASE="$2"

# 转码为多种码率
ffmpeg -i "$INPUT_STREAM" \
  -c:v libx264 -preset veryfast \
  -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a \
  \
  -s:v:0 1920x1080 -b:v:0 3000k -maxrate:v:0 3200k -bufsize:v:0 6000k \
  -s:v:1 1280x720  -b:v:1 1500k -maxrate:v:1 1650k -bufsize:v:1 3000k \
  -s:v:2 854x480   -b:v:2 800k  -maxrate:v:2 880k  -bufsize:v:2 1600k \
  \
  -c:a:0 aac -b:a:0 128k \
  -c:a:1 aac -b:a:1 128k \
  -c:a:2 aac -b:a:2 96k \
  \
  -f hls -hls_time 6 -hls_list_size 10 \
  -hls_segment_filename "${OUTPUT_BASE}_%v_%03d.ts" \
  -master_pl_name "master.m3u8" \
  -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
  "${OUTPUT_BASE}_%v.m3u8"
EOF

chmod +x transcode_multirate.sh

# 使用
./transcode_multirate.sh "rtmp://localhost:8079/live/input" "/var/www/hls/stream"
```

## 九、故障排查

### 9.1 常见问题诊断

#### 连接问题

```bash
# 检查端口监听
netstat -tulpn | grep 8079

# 检查防火墙
sudo ufw status
sudo iptables -L

# 测试 RTMP 连接
ffmpeg -f lavfi -i testsrc=duration=10:size=320x240:rate=30 \
       -f flv rtmp://localhost:8079/live/test

# 检查服务器日志
tail -f /var/log/media_server/media_server.log
```

#### 性能问题

```bash
# 系统资源监控
top -p $(pgrep media_server)
iostat -x 1
sar -n DEV 1

# 网络监控
iftop -i eth0
ss -tuln

# 内存使用分析
pmap -x $(pgrep media_server)
valgrind --tool=massif ./media_server
```

### 9.2 调试工具

#### GDB 调试

```bash
# 编译 debug 版本
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)

# GDB 调试
gdb ./media_server
(gdb) set args --port=8079 --v=2
(gdb) run
(gdb) bt  # 查看调用栈
```

#### 性能分析

```bash
# CPU 性能分析
perf record -g ./media_server --port=8079
perf report

# 内存泄漏检测
valgrind --leak-check=full --show-leak-kinds=all ./media_server

# 网络抓包分析
tcpdump -i any -w media_server.pcap port 8079
wireshark media_server.pcap
```

## 十、总结

brpc media-server 是一个功能强大、性能优异的流媒体服务器解决方案。通过本指南，你已经掌握了：

### 核心能力
1. **多协议支持**：RTMP、HTTP-FLV、HLS 等主流协议
2. **高性能架构**：基于 brpc 的高并发处理
3. **灵活部署**：支持源站和边缘节点部署
4. **丰富配置**：满足不同场景的配置需求

### 应用场景
- **直播平台**：构建大规模直播服务
- **在线教育**：实时互动教学
- **视频会议**：企业级视频通信
- **IoT 流媒体**：物联网设备视频传输

### 最佳实践
1. **性能优化**：系统调优和应用配置
2. **安全防护**：访问控制和加密传输
3. **监控运维**：完善的监控和日志系统
4. **故障处理**：快速诊断和恢复机制

brpc media-server 为构建企业级流媒体服务提供了坚实的基础，结合合适的架构设计和运维实践，可以构建出稳定、高效的流媒体平台。