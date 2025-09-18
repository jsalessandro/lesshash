---
title: "Netty 完全指南：构建高性能网络应用的终极秘籍"
date: 2025-09-18T15:55:00+08:00
draft: false
tags: ["Netty", "Java", "NIO", "网络编程", "高性能", "异步编程"]
categories: ["技术分享"]
author: "lesshash"
description: "Netty 是当今最流行的 Java 网络编程框架，本文将从零开始深入讲解 Netty 的核心概念、使用方法和性能优化技巧"
---

## 一、为什么选择 Netty？

### 1.1 网络编程的挑战

在现代应用开发中，网络编程面临诸多挑战：

- **高并发连接**：需要同时处理成千上万的连接
- **低延迟要求**：毫秒级的响应时间
- **复杂协议处理**：HTTP、WebSocket、自定义协议
- **资源管理**：内存泄漏、线程池管理
- **跨平台兼容性**：Windows、Linux、macOS

### 1.2 Netty 的优势

**Netty** 是一个高性能、异步的网络应用框架，为快速开发可维护的高性能网络服务器和客户端提供了强大支持。

#### 核心优势

- **🚀 高性能**：基于 Java NIO，零拷贝、内存池等优化
- **🎯 低延迟**：事件驱动的异步架构
- **💪 高并发**：单机支持数万甚至数十万连接
- **🔧 易用性**：简洁的 API 设计，丰富的编解码器
- **🛡️ 稳定性**：久经考验，大量知名项目使用

#### 性能表现

让我们看看 Netty 与其他框架的性能对比：

![Netty 吞吐量对比](/images/netty-benchmarks/throughput_comparison.png)

从上图可以看出，Netty 在各种响应大小下都表现出色，特别是在小数据包场景下性能优势明显。

![Netty 延迟对比](/images/netty-benchmarks/latency_comparison.png)

在延迟方面，Netty 同样表现优异，P99 延迟控制在 3ms 以内。

## 二、核心概念详解

### 2.1 EventLoop 和 EventLoopGroup

#### 概念理解

```java
// EventLoop 是 Netty 的核心抽象
public class EventLoopExample {
    public static void main(String[] args) {
        // Boss EventLoopGroup：负责接受连接
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);

        // Worker EventLoopGroup：负责处理 I/O 事件
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 public void initChannel(SocketChannel ch) {
                     // 配置 pipeline
                 }
             });

            System.out.println("Boss EventLoopGroup 线程数: " +
                ((NioEventLoopGroup) bossGroup).executorCount());
            System.out.println("Worker EventLoopGroup 线程数: " +
                ((NioEventLoopGroup) workerGroup).executorCount());

        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }
}
```

#### EventLoop 线程模型

```java
// 自定义 EventLoop 配置
public class EventLoopConfiguration {

    public static EventLoopGroup createOptimizedEventLoopGroup() {
        // 根据 CPU 核数确定线程数
        int threads = Runtime.getRuntime().availableProcessors() * 2;

        return new NioEventLoopGroup(threads, new ThreadFactory() {
            private final AtomicInteger counter = new AtomicInteger(0);

            @Override
            public Thread newThread(Runnable r) {
                Thread thread = new Thread(r);
                thread.setName("Netty-Worker-" + counter.incrementAndGet());
                thread.setDaemon(true);
                // 设置线程优先级
                thread.setPriority(Thread.MAX_PRIORITY);
                return thread;
            }
        });
    }

    // EventLoop 任务调度示例
    public static void scheduleTask(EventLoop eventLoop) {
        // 延迟执行任务
        eventLoop.schedule(() -> {
            System.out.println("延迟任务执行: " + Thread.currentThread().getName());
        }, 5, TimeUnit.SECONDS);

        // 周期性任务
        eventLoop.scheduleAtFixedRate(() -> {
            System.out.println("周期性任务: " + new Date());
        }, 0, 10, TimeUnit.SECONDS);
    }
}
```

### 2.2 Channel 和 ChannelHandler

#### Channel 生命周期

```java
// 自定义 ChannelHandler 演示完整生命周期
public class LifecycleChannelHandler extends ChannelInboundHandlerAdapter {

    @Override
    public void handlerAdded(ChannelHandlerContext ctx) {
        System.out.println("Handler 被添加到 pipeline");
    }

    @Override
    public void channelRegistered(ChannelHandlerContext ctx) {
        System.out.println("Channel 注册到 EventLoop");
    }

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        System.out.println("Channel 变为活跃状态，可以读写数据");

        // 发送欢迎消息
        String welcomeMsg = "欢迎连接到 Netty 服务器！\n";
        ctx.writeAndFlush(Unpooled.copiedBuffer(welcomeMsg, CharsetUtil.UTF_8));
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        ByteBuf buf = (ByteBuf) msg;
        try {
            String receivedData = buf.toString(CharsetUtil.UTF_8);
            System.out.println("接收到数据: " + receivedData);

            // 回显数据
            String response = "Echo: " + receivedData;
            ctx.writeAndFlush(Unpooled.copiedBuffer(response, CharsetUtil.UTF_8));

        } finally {
            buf.release(); // 重要：释放 ByteBuf
        }
    }

    @Override
    public void channelReadComplete(ChannelHandlerContext ctx) {
        System.out.println("Channel 读取完成");
        ctx.flush(); // 确保数据被发送
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        System.out.println("Channel 变为非活跃状态");
    }

    @Override
    public void channelUnregistered(ChannelHandlerContext ctx) {
        System.out.println("Channel 从 EventLoop 注销");
    }

    @Override
    public void handlerRemoved(ChannelHandlerContext ctx) {
        System.out.println("Handler 从 pipeline 移除");
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        System.err.println("异常处理: " + cause.getMessage());
        cause.printStackTrace();
        ctx.close(); // 关闭连接
    }
}
```

#### ChannelPipeline 深入理解

```java
// Pipeline 配置和管理
public class PipelineManager {

    public static void configurePipeline(SocketChannel ch) {
        ChannelPipeline pipeline = ch.pipeline();

        // 1. 日志处理器（最前面）
        pipeline.addFirst("logger", new LoggingHandler(LogLevel.INFO));

        // 2. 空闲检测
        pipeline.addLast("idleState", new IdleStateHandler(30, 0, 0, TimeUnit.SECONDS));

        // 3. 协议解码器
        pipeline.addLast("frameDecoder", new LengthFieldBasedFrameDecoder(1024 * 1024, 0, 4, 0, 4));
        pipeline.addLast("frameEncoder", new LengthFieldPrepender(4));

        // 4. 字符串编解码
        pipeline.addLast("stringDecoder", new StringDecoder(CharsetUtil.UTF_8));
        pipeline.addLast("stringEncoder", new StringEncoder(CharsetUtil.UTF_8));

        // 5. 业务处理器
        pipeline.addLast("businessHandler", new BusinessHandler());

        // 6. 异常处理器（最后面）
        pipeline.addLast("exceptionHandler", new ExceptionHandler());
    }

    // 动态添加处理器
    public static void addSSLHandler(ChannelPipeline pipeline, SslContext sslContext) {
        pipeline.addFirst("ssl", sslContext.newHandler(pipeline.channel().alloc()));
    }

    // 动态移除处理器
    public static void removeHandler(ChannelPipeline pipeline, String name) {
        if (pipeline.get(name) != null) {
            pipeline.remove(name);
        }
    }
}

// 空闲状态处理
class IdleHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) throws Exception {
        if (evt instanceof IdleStateEvent) {
            IdleStateEvent event = (IdleStateEvent) evt;
            if (event.state() == IdleState.READER_IDLE) {
                System.out.println("读空闲，关闭连接");
                ctx.close();
            }
        } else {
            super.userEventTriggered(ctx, evt);
        }
    }
}
```

### 2.3 ByteBuf 内存管理

#### ByteBuf 基础操作

```java
// ByteBuf 详细使用示例
public class ByteBufExample {

    public static void basicOperations() {
        // 创建 ByteBuf
        ByteBuf buffer = Unpooled.buffer(256);

        System.out.println("初始状态:");
        printBufferInfo(buffer);

        // 写入数据
        buffer.writeBytes("Hello".getBytes());
        buffer.writeInt(42);
        buffer.writeLong(System.currentTimeMillis());

        System.out.println("写入数据后:");
        printBufferInfo(buffer);

        // 读取数据
        byte[] helloBytes = new byte[5];
        buffer.readBytes(helloBytes);
        int number = buffer.readInt();
        long timestamp = buffer.readLong();

        System.out.println("读取的数据:");
        System.out.println("String: " + new String(helloBytes));
        System.out.println("Int: " + number);
        System.out.println("Long: " + timestamp);

        System.out.println("读取数据后:");
        printBufferInfo(buffer);

        // 重要：释放 ByteBuf
        buffer.release();
    }

    private static void printBufferInfo(ByteBuf buf) {
        System.out.println("readerIndex: " + buf.readerIndex());
        System.out.println("writerIndex: " + buf.writerIndex());
        System.out.println("capacity: " + buf.capacity());
        System.out.println("readableBytes: " + buf.readableBytes());
        System.out.println("writableBytes: " + buf.writableBytes());
        System.out.println("---");
    }

    // 内存池使用
    public static void pooledByteBuf() {
        ByteBufAllocator allocator = PooledByteBufAllocator.DEFAULT;

        // 申请堆内存
        ByteBuf heapBuf = allocator.heapBuffer(256);

        // 申请直接内存（堆外内存）
        ByteBuf directBuf = allocator.directBuffer(256);

        try {
            // 使用缓冲区
            heapBuf.writeBytes("Heap Buffer".getBytes());
            directBuf.writeBytes("Direct Buffer".getBytes());

            System.out.println("Heap Buffer: " + heapBuf.toString(CharsetUtil.UTF_8));
            System.out.println("Direct Buffer: " + directBuf.toString(CharsetUtil.UTF_8));

        } finally {
            // 释放内存
            heapBuf.release();
            directBuf.release();
        }
    }

    // 复合缓冲区
    public static void compositeByteBuf() {
        CompositeByteBuf composite = Unpooled.compositeBuffer();

        ByteBuf header = Unpooled.copiedBuffer("Header", CharsetUtil.UTF_8);
        ByteBuf body = Unpooled.copiedBuffer("Body Content", CharsetUtil.UTF_8);

        // 将多个 ByteBuf 组合
        composite.addComponents(true, header, body);

        System.out.println("Composite Buffer: " + composite.toString(CharsetUtil.UTF_8));

        composite.release();
    }
}
```

#### 内存泄漏检测

```java
// 内存泄漏检测配置
public class MemoryLeakDetection {

    static {
        // 设置内存泄漏检测级别
        System.setProperty("io.netty.leakDetection.level", "ADVANCED");
        // 可选值：DISABLED, SIMPLE, ADVANCED, PARANOID
    }

    // 正确的 ByteBuf 使用模式
    public static void correctByteBufUsage(ChannelHandlerContext ctx, Object msg) {
        ByteBuf buf = (ByteBuf) msg;
        try {
            // 处理数据
            String data = buf.toString(CharsetUtil.UTF_8);
            System.out.println("Received: " + data);

            // 创建响应
            ByteBuf response = ctx.alloc().buffer();
            try {
                response.writeBytes("Response".getBytes());
                ctx.writeAndFlush(response);
                response = null; // 防止在 finally 中重复释放
            } finally {
                if (response != null) {
                    response.release();
                }
            }

        } finally {
            buf.release(); // 确保释放输入缓冲区
        }
    }

    // 使用 ReferenceCountUtil 安全释放
    public static void safeByteBufUsage(Object msg) {
        try {
            if (msg instanceof ByteBuf) {
                ByteBuf buf = (ByteBuf) msg;
                String data = buf.toString(CharsetUtil.UTF_8);
                System.out.println("Data: " + data);
            }
        } finally {
            ReferenceCountUtil.release(msg); // 安全释放
        }
    }
}
```

## 三、实战入门案例

### 3.1 Echo 服务器

#### 服务器端实现

```java
// 完整的 Echo 服务器实现
public class EchoServer {
    private final int port;

    public EchoServer(int port) {
        this.port = port;
    }

    public void start() throws InterruptedException {
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .option(ChannelOption.SO_BACKLOG, 1024)
             .option(ChannelOption.SO_REUSEADDR, true)
             .childOption(ChannelOption.SO_KEEPALIVE, true)
             .childOption(ChannelOption.TCP_NODELAY, true)
             .childOption(ChannelOption.SO_RCVBUF, 32 * 1024)
             .childOption(ChannelOption.SO_SNDBUF, 32 * 1024)
             .handler(new LoggingHandler(LogLevel.INFO))
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 public void initChannel(SocketChannel ch) {
                     ChannelPipeline p = ch.pipeline();

                     // 添加处理器
                     p.addLast(new IdleStateHandler(60, 30, 0, TimeUnit.SECONDS));
                     p.addLast(new EchoServerHandler());
                 }
             });

            // 绑定端口并启动服务器
            ChannelFuture f = b.bind(port).sync();
            System.out.println("Echo Server started on port " + port);

            // 等待服务器 socket 关闭
            f.channel().closeFuture().sync();

        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8080;
        new EchoServer(port).start();
    }
}

// Echo 服务器处理器
class EchoServerHandler extends ChannelInboundHandlerAdapter {
    private static final AtomicLong connectionCount = new AtomicLong(0);
    private static final AtomicLong messageCount = new AtomicLong(0);

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        long connections = connectionCount.incrementAndGet();
        System.out.println("Client connected: " + ctx.channel().remoteAddress() +
                          ", Total connections: " + connections);
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        long connections = connectionCount.decrementAndGet();
        System.out.println("Client disconnected: " + ctx.channel().remoteAddress() +
                          ", Total connections: " + connections);
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        ByteBuf in = (ByteBuf) msg;
        try {
            String message = in.toString(CharsetUtil.UTF_8);
            long msgCount = messageCount.incrementAndGet();

            System.out.println("Received message #" + msgCount + ": " + message.trim());

            // 构建响应
            String response = "Echo #" + msgCount + ": " + message;
            ByteBuf responseBuffer = Unpooled.copiedBuffer(response, CharsetUtil.UTF_8);

            ctx.writeAndFlush(responseBuffer);

        } finally {
            in.release();
        }
    }

    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) throws Exception {
        if (evt instanceof IdleStateEvent) {
            IdleStateEvent event = (IdleStateEvent) evt;
            String eventType = null;
            switch (event.state()) {
                case READER_IDLE:
                    eventType = "读空闲";
                    break;
                case WRITER_IDLE:
                    eventType = "写空闲";
                    break;
                case ALL_IDLE:
                    eventType = "读写空闲";
                    break;
            }
            System.out.println(ctx.channel().remoteAddress() + " 超时事件: " + eventType);
            ctx.channel().close();
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        System.err.println("Server exception: " + cause.getMessage());
        cause.printStackTrace();
        ctx.close();
    }
}
```

#### 客户端实现

```java
// Echo 客户端实现
public class EchoClient {
    private final String host;
    private final int port;

    public EchoClient(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public void start() throws InterruptedException {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioSocketChannel.class)
             .option(ChannelOption.TCP_NODELAY, true)
             .option(ChannelOption.SO_KEEPALIVE, true)
             .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
             .handler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 public void initChannel(SocketChannel ch) {
                     ChannelPipeline p = ch.pipeline();
                     p.addLast(new EchoClientHandler());
                 }
             });

            // 连接服务器
            ChannelFuture f = b.connect(host, port).sync();
            System.out.println("Connected to " + host + ":" + port);

            // 等待连接关闭
            f.channel().closeFuture().sync();

        } finally {
            group.shutdownGracefully();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        String host = args.length > 0 ? args[0] : "localhost";
        int port = args.length > 1 ? Integer.parseInt(args[1]) : 8080;

        new EchoClient(host, port).start();
    }
}

// Echo 客户端处理器
class EchoClientHandler extends ChannelInboundHandlerAdapter {
    private final AtomicInteger messageCounter = new AtomicInteger(0);

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        System.out.println("Connected to server: " + ctx.channel().remoteAddress());

        // 开始发送消息
        sendMessage(ctx);
    }

    private void sendMessage(ChannelHandlerContext ctx) {
        // 定时发送消息
        ctx.executor().schedule(() -> {
            if (ctx.channel().isActive()) {
                int msgNum = messageCounter.incrementAndGet();
                String message = "Hello Netty! Message #" + msgNum +
                               " at " + new Date() + "\n";

                ByteBuf buffer = Unpooled.copiedBuffer(message, CharsetUtil.UTF_8);
                ctx.writeAndFlush(buffer);

                // 继续发送下一条消息
                sendMessage(ctx);
            }
        }, 2, TimeUnit.SECONDS);
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        ByteBuf in = (ByteBuf) msg;
        try {
            String response = in.toString(CharsetUtil.UTF_8);
            System.out.println("Server response: " + response.trim());
        } finally {
            in.release();
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        System.err.println("Client exception: " + cause.getMessage());
        cause.printStackTrace();
        ctx.close();
    }
}
```

### 3.2 HTTP 服务器

#### 完整的 HTTP 服务器

```java
// HTTP 服务器实现
public class HttpServer {
    private final int port;

    public HttpServer(int port) {
        this.port = port;
    }

    public void start() throws InterruptedException {
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .option(ChannelOption.SO_BACKLOG, 1024)
             .childOption(ChannelOption.SO_KEEPALIVE, true)
             .childOption(ChannelOption.TCP_NODELAY, true)
             .childHandler(new HttpServerInitializer());

            ChannelFuture f = b.bind(port).sync();
            System.out.println("HTTP Server started on http://localhost:" + port);

            f.channel().closeFuture().sync();

        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8080;
        new HttpServer(port).start();
    }
}

// HTTP 服务器初始化器
class HttpServerInitializer extends ChannelInitializer<SocketChannel> {
    @Override
    public void initChannel(SocketChannel ch) {
        ChannelPipeline pipeline = ch.pipeline();

        // HTTP 编解码器
        pipeline.addLast(new HttpServerCodec());

        // HTTP 对象聚合器
        pipeline.addLast(new HttpObjectAggregator(65536));

        // HTTP 内容压缩
        pipeline.addLast(new HttpContentCompressor());

        // 自定义业务处理器
        pipeline.addLast(new HttpServerHandler());
    }
}

// HTTP 服务器处理器
class HttpServerHandler extends ChannelInboundHandlerAdapter {
    private static final Map<String, String> routes = new HashMap<>();
    private static final AtomicLong requestCount = new AtomicLong(0);

    static {
        // 配置路由
        routes.put("/", "Welcome to Netty HTTP Server!");
        routes.put("/hello", "Hello, World!");
        routes.put("/time", "Current time: " + new Date());
        routes.put("/stats", "Request count: ");
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        if (msg instanceof FullHttpRequest) {
            FullHttpRequest request = (FullHttpRequest) msg;

            long count = requestCount.incrementAndGet();
            String uri = request.uri();
            HttpMethod method = request.method();

            System.out.println("Request #" + count + ": " + method + " " + uri);

            // 处理请求
            handleHttpRequest(ctx, request, count);
        }
    }

    private void handleHttpRequest(ChannelHandlerContext ctx, FullHttpRequest request, long count) {
        String uri = request.uri();
        String responseContent;
        HttpResponseStatus status = HttpResponseStatus.OK;

        // 路由处理
        if (routes.containsKey(uri)) {
            responseContent = routes.get(uri);
            if (uri.equals("/stats")) {
                responseContent += count;
            }
        } else if (uri.equals("/api/echo")) {
            // API 接口：回显请求体
            ByteBuf content = request.content();
            responseContent = "Echo: " + content.toString(CharsetUtil.UTF_8);
        } else if (uri.startsWith("/api/user/")) {
            // RESTful API 示例
            String userId = uri.substring("/api/user/".length());
            responseContent = "{\"userId\": \"" + userId + "\", \"name\": \"User " + userId + "\"}";
        } else {
            // 404 处理
            responseContent = "404 Not Found: " + uri;
            status = HttpResponseStatus.NOT_FOUND;
        }

        // 构建 HTTP 响应
        sendHttpResponse(ctx, request, responseContent, status);
    }

    private void sendHttpResponse(ChannelHandlerContext ctx, FullHttpRequest request,
                                 String content, HttpResponseStatus status) {

        ByteBuf responseContent = Unpooled.copiedBuffer(content, CharsetUtil.UTF_8);

        FullHttpResponse response = new DefaultFullHttpResponse(
            HttpVersion.HTTP_1_1, status, responseContent);

        // 设置响应头
        response.headers().set(HttpHeaderNames.CONTENT_TYPE, "text/plain; charset=UTF-8");
        response.headers().set(HttpHeaderNames.CONTENT_LENGTH, responseContent.readableBytes());
        response.headers().set(HttpHeaderNames.SERVER, "Netty/4.1");
        response.headers().set(HttpHeaderNames.DATE, new Date());

        // 处理 Keep-Alive
        boolean keepAlive = HttpUtil.isKeepAlive(request);
        if (keepAlive) {
            response.headers().set(HttpHeaderNames.CONNECTION, HttpHeaderValues.KEEP_ALIVE);
        }

        // 发送响应
        ChannelFuture future = ctx.writeAndFlush(response);

        if (!keepAlive) {
            future.addListener(ChannelFutureListener.CLOSE);
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        System.err.println("HTTP Server exception: " + cause.getMessage());
        ctx.close();
    }
}
```

### 3.3 WebSocket 服务器

```java
// WebSocket 服务器实现
public class WebSocketServer {
    private final int port;

    public WebSocketServer(int port) {
        this.port = port;
    }

    public void start() throws InterruptedException {
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .childHandler(new WebSocketServerInitializer());

            ChannelFuture f = b.bind(port).sync();
            System.out.println("WebSocket Server started on ws://localhost:" + port + "/websocket");

            f.channel().closeFuture().sync();

        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8080;
        new WebSocketServer(port).start();
    }
}

// WebSocket 服务器初始化器
class WebSocketServerInitializer extends ChannelInitializer<SocketChannel> {
    @Override
    public void initChannel(SocketChannel ch) {
        ChannelPipeline pipeline = ch.pipeline();

        pipeline.addLast(new HttpServerCodec());
        pipeline.addLast(new HttpObjectAggregator(65536));
        pipeline.addLast(new WebSocketServerProtocolHandler("/websocket", null, true));
        pipeline.addLast(new WebSocketServerHandler());
    }
}

// WebSocket 处理器
class WebSocketServerHandler extends SimpleChannelInboundHandler<WebSocketFrame> {
    private static final Set<Channel> channels = ConcurrentHashMap.newKeySet();

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        channels.add(ctx.channel());
        System.out.println("WebSocket client connected: " + ctx.channel().remoteAddress());
        System.out.println("Total clients: " + channels.size());
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        channels.remove(ctx.channel());
        System.out.println("WebSocket client disconnected: " + ctx.channel().remoteAddress());
        System.out.println("Total clients: " + channels.size());
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, WebSocketFrame frame) {
        if (frame instanceof TextWebSocketFrame) {
            // 处理文本消息
            String text = ((TextWebSocketFrame) frame).text();
            System.out.println("Received: " + text);

            // 广播消息给所有客户端
            String response = "Server Echo: " + text + " (Clients: " + channels.size() + ")";
            TextWebSocketFrame responseFrame = new TextWebSocketFrame(response);

            // 广播给所有连接的客户端
            for (Channel channel : channels) {
                if (channel.isActive()) {
                    channel.writeAndFlush(responseFrame.retainedDuplicate());
                }
            }

        } else if (frame instanceof BinaryWebSocketFrame) {
            // 处理二进制消息
            ByteBuf content = frame.content();
            System.out.println("Received binary data: " + content.readableBytes() + " bytes");

            // 回显二进制数据
            ctx.writeAndFlush(new BinaryWebSocketFrame(content.retain()));

        } else if (frame instanceof PingWebSocketFrame) {
            // 处理 Ping 帧
            ctx.writeAndFlush(new PongWebSocketFrame(frame.content().retain()));

        } else if (frame instanceof CloseWebSocketFrame) {
            // 处理关闭帧
            ctx.close();
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        System.err.println("WebSocket exception: " + cause.getMessage());
        ctx.close();
    }
}
```

## 四、性能分析与优化

### 4.1 性能基准测试

让我们看看 Netty 在不同场景下的性能表现：

![I/O 模型对比](/images/netty-benchmarks/io_models_comparison.png)

从图中可以看出，Netty 的 NIO 模型在 CPU 使用率和吞吐量之间取得了很好的平衡。

![内存使用对比](/images/netty-benchmarks/memory_usage.png)

在内存使用方面，Netty 表现出色，即使在高并发场景下也能保持较低的内存占用。

![并发连接处理](/images/netty-benchmarks/concurrent_connections.png)

Netty 在处理并发连接方面表现优异，能够快速建立大量连接并保持稳定。

### 4.2 性能优化技巧

#### JVM 优化

```bash
# Netty 服务器 JVM 优化参数
java -server \
     -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:+UnlockExperimentalVMOptions \
     -XX:+UseZGC \
     -XX:+DisableExplicitGC \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/netty-heapdump.hprof \
     -Dio.netty.leakDetection.level=SIMPLE \
     -Dio.netty.allocator.type=pooled \
     -Dio.netty.allocator.numDirectArenas=32 \
     -Dio.netty.allocator.numHeapArenas=32 \
     -Dio.netty.recycler.maxCapacityPerThread=0 \
     -cp your-app.jar com.example.NettyServer
```

#### 代码优化

```java
// Netty 性能优化配置
public class NettyPerformanceOptimization {

    public static ServerBootstrap createOptimizedServer() {
        // 创建优化的 EventLoopGroup
        EventLoopGroup bossGroup = new NioEventLoopGroup(1,
            new DefaultThreadFactory("NettyBoss", true));
        EventLoopGroup workerGroup = new NioEventLoopGroup(
            Runtime.getRuntime().availableProcessors() * 2,
            new DefaultThreadFactory("NettyWorker", true));

        ServerBootstrap bootstrap = new ServerBootstrap();
        bootstrap.group(bossGroup, workerGroup)
                .channel(NioServerSocketChannel.class)
                // 网络层优化
                .option(ChannelOption.SO_BACKLOG, 1024)
                .option(ChannelOption.SO_REUSEADDR, true)
                .childOption(ChannelOption.SO_KEEPALIVE, true)
                .childOption(ChannelOption.TCP_NODELAY, true)
                .childOption(ChannelOption.SO_RCVBUF, 32 * 1024)
                .childOption(ChannelOption.SO_SNDBUF, 32 * 1024)
                // 内存优化
                .childOption(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
                .childOption(ChannelOption.RCVBUF_ALLOCATOR,
                    new AdaptiveRecvByteBufAllocator(64, 1024, 65536))
                // 写缓冲区优化
                .childOption(ChannelOption.WRITE_BUFFER_WATER_MARK,
                    new WriteBufferWaterMark(8 * 1024, 32 * 1024));

        return bootstrap;
    }

    // 高性能编解码器
    public static class OptimizedStringDecoder extends MessageToMessageDecoder<ByteBuf> {
        private final Charset charset;

        public OptimizedStringDecoder(Charset charset) {
            this.charset = charset;
        }

        @Override
        protected void decode(ChannelHandlerContext ctx, ByteBuf msg, List<Object> out) {
            // 零拷贝字符串解码
            out.add(msg.toString(charset));
        }
    }

    // 批量写优化
    public static class BatchedWriteHandler extends ChannelOutboundHandlerAdapter {
        private final List<Object> pendingWrites = new ArrayList<>();
        private final int batchSize;

        public BatchedWriteHandler(int batchSize) {
            this.batchSize = batchSize;
        }

        @Override
        public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) {
            pendingWrites.add(msg);

            if (pendingWrites.size() >= batchSize) {
                flushBatch(ctx);
            }
        }

        @Override
        public void flush(ChannelHandlerContext ctx) {
            if (!pendingWrites.isEmpty()) {
                flushBatch(ctx);
            }
            ctx.flush();
        }

        private void flushBatch(ChannelHandlerContext ctx) {
            for (Object msg : pendingWrites) {
                ctx.write(msg);
            }
            pendingWrites.clear();
        }
    }
}
```

#### 操作系统优化

```bash
# Linux 系统优化配置
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 16384 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 16384 134217728' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf

# 文件描述符限制
echo '* soft nofile 1000000' >> /etc/security/limits.conf
echo '* hard nofile 1000000' >> /etc/security/limits.conf

# 应用配置
sysctl -p
```

### 4.3 监控和调试

#### 性能监控

```java
// Netty 性能监控
public class NettyMonitor {
    private static final MeterRegistry registry = Metrics.globalRegistry;
    private static final Timer requestTimer = Timer.builder("netty.request.duration")
            .register(registry);
    private static final Counter connectionCounter = Counter.builder("netty.connections.total")
            .register(registry);

    // 监控处理器
    public static class MonitoringHandler extends ChannelInboundHandlerAdapter {
        @Override
        public void channelActive(ChannelHandlerContext ctx) {
            connectionCounter.increment();
            super.channelActive(ctx);
        }

        @Override
        public void channelRead(ChannelHandlerContext ctx, Object msg) {
            Timer.Sample sample = Timer.start(registry);

            try {
                super.channelRead(ctx, msg);
            } finally {
                sample.stop(requestTimer);
            }
        }

        @Override
        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
            Counter.builder("netty.errors.total")
                    .tag("error.type", cause.getClass().getSimpleName())
                    .register(registry)
                    .increment();

            super.exceptionCaught(ctx, cause);
        }
    }

    // 定期输出监控指标
    public static void startMetricsReporting() {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

        scheduler.scheduleAtFixedRate(() -> {
            System.out.println("=== Netty Metrics ===");
            System.out.println("Total connections: " + connectionCounter.count());
            System.out.println("Request rate: " + requestTimer.count() + " req/s");
            System.out.println("Average latency: " +
                requestTimer.mean(TimeUnit.MILLISECONDS) + " ms");
            System.out.println("P95 latency: " +
                requestTimer.percentile(0.95, TimeUnit.MILLISECONDS) + " ms");
            System.out.println("P99 latency: " +
                requestTimer.percentile(0.99, TimeUnit.MILLISECONDS) + " ms");

        }, 0, 30, TimeUnit.SECONDS);
    }
}
```

## 五、高级特性

### 5.1 自定义协议

```java
// 自定义协议实现
public class CustomProtocol {

    // 协议格式：[4字节长度][1字节类型][数据]
    public static class CustomMessage {
        private final byte type;
        private final byte[] data;

        public CustomMessage(byte type, byte[] data) {
            this.type = type;
            this.data = data;
        }

        // getter 方法
        public byte getType() { return type; }
        public byte[] getData() { return data; }
        public int getLength() { return 1 + (data != null ? data.length : 0); }
    }

    // 自定义协议编码器
    public static class CustomProtocolEncoder extends MessageToByteEncoder<CustomMessage> {
        @Override
        protected void encode(ChannelHandlerContext ctx, CustomMessage msg, ByteBuf out) {
            // 写入长度（4字节）
            out.writeInt(msg.getLength());
            // 写入类型（1字节）
            out.writeByte(msg.getType());
            // 写入数据
            if (msg.getData() != null) {
                out.writeBytes(msg.getData());
            }
        }
    }

    // 自定义协议解码器
    public static class CustomProtocolDecoder extends LengthFieldBasedFrameDecoder {
        public CustomProtocolDecoder() {
            super(1024 * 1024, 0, 4, 0, 4);
        }

        @Override
        protected Object decode(ChannelHandlerContext ctx, ByteBuf in) throws Exception {
            ByteBuf frame = (ByteBuf) super.decode(ctx, in);
            if (frame == null) {
                return null;
            }

            try {
                byte type = frame.readByte();
                byte[] data = new byte[frame.readableBytes()];
                frame.readBytes(data);

                return new CustomMessage(type, data);
            } finally {
                frame.release();
            }
        }
    }

    // 协议处理器
    public static class CustomProtocolHandler extends SimpleChannelInboundHandler<CustomMessage> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, CustomMessage msg) {
            byte type = msg.getType();
            byte[] data = msg.getData();

            switch (type) {
                case 0x01: // 心跳
                    handleHeartbeat(ctx);
                    break;
                case 0x02: // 数据传输
                    handleDataTransfer(ctx, data);
                    break;
                case 0x03: // 控制命令
                    handleControlCommand(ctx, data);
                    break;
                default:
                    System.err.println("Unknown message type: " + type);
            }
        }

        private void handleHeartbeat(ChannelHandlerContext ctx) {
            // 回复心跳
            CustomMessage pong = new CustomMessage((byte) 0x01, "PONG".getBytes());
            ctx.writeAndFlush(pong);
        }

        private void handleDataTransfer(ChannelHandlerContext ctx, byte[] data) {
            String dataStr = new String(data, CharsetUtil.UTF_8);
            System.out.println("Received data: " + dataStr);

            // 回复确认
            CustomMessage ack = new CustomMessage((byte) 0x04, "ACK".getBytes());
            ctx.writeAndFlush(ack);
        }

        private void handleControlCommand(ChannelHandlerContext ctx, byte[] data) {
            String command = new String(data, CharsetUtil.UTF_8);
            System.out.println("Received command: " + command);

            // 执行命令并回复结果
            String result = executeCommand(command);
            CustomMessage response = new CustomMessage((byte) 0x05, result.getBytes());
            ctx.writeAndFlush(response);
        }

        private String executeCommand(String command) {
            // 简单的命令处理示例
            switch (command.toLowerCase()) {
                case "status":
                    return "Server is running";
                case "time":
                    return new Date().toString();
                case "shutdown":
                    return "Shutdown initiated";
                default:
                    return "Unknown command: " + command;
            }
        }
    }
}
```

### 5.2 SSL/TLS 支持

```java
// SSL/TLS 配置
public class SSLNettyServer {

    public static SslContext createSSLContext() throws Exception {
        // 创建自签名证书（仅用于测试）
        SelfSignedCertificate ssc = new SelfSignedCertificate();

        return SslContextBuilder.forServer(ssc.certificate(), ssc.privateKey())
                .sslProvider(SslProvider.OPENSSL) // 使用 OpenSSL（性能更好）
                .ciphers(Http2SecurityUtil.CIPHERS, SupportedCipherSuiteFilter.INSTANCE)
                .applicationProtocolConfig(new ApplicationProtocolConfig(
                    ApplicationProtocolConfig.Protocol.ALPN,
                    ApplicationProtocolConfig.SelectorFailureBehavior.NO_ADVERTISE,
                    ApplicationProtocolConfig.SelectedListenerFailureBehavior.ACCEPT,
                    ApplicationProtocolNames.HTTP_2,
                    ApplicationProtocolNames.HTTP_1_1))
                .build();
    }

    // SSL 初始化器
    public static class SSLChannelInitializer extends ChannelInitializer<SocketChannel> {
        private final SslContext sslContext;

        public SSLChannelInitializer(SslContext sslContext) {
            this.sslContext = sslContext;
        }

        @Override
        protected void initChannel(SocketChannel ch) throws Exception {
            ChannelPipeline pipeline = ch.pipeline();

            // 添加 SSL 处理器（必须是第一个）
            pipeline.addLast(sslContext.newHandler(ch.alloc()));

            // 添加其他处理器
            pipeline.addLast(new HttpServerCodec());
            pipeline.addLast(new HttpObjectAggregator(65536));
            pipeline.addLast(new HttpsServerHandler());
        }
    }

    // HTTPS 处理器
    public static class HttpsServerHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) {
            String uri = request.uri();

            // 构建 HTTPS 响应
            String responseContent = "HTTPS Response for: " + uri + "\nSecure: true\n";
            ByteBuf content = Unpooled.copiedBuffer(responseContent, CharsetUtil.UTF_8);

            FullHttpResponse response = new DefaultFullHttpResponse(
                HttpVersion.HTTP_1_1, HttpResponseStatus.OK, content);

            response.headers().set(HttpHeaderNames.CONTENT_TYPE, "text/plain");
            response.headers().set(HttpHeaderNames.CONTENT_LENGTH, content.readableBytes());
            response.headers().set("Strict-Transport-Security", "max-age=31536000");

            ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
        }
    }
}
```

### 5.3 HTTP/2 支持

```java
// HTTP/2 服务器实现
public class Http2Server {

    public static void main(String[] args) throws Exception {
        SslContext sslCtx = createHttp2SSLContext();

        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .childHandler(new Http2ServerInitializer(sslCtx));

            ChannelFuture f = b.bind(8443).sync();
            System.out.println("HTTP/2 Server started on https://localhost:8443");

            f.channel().closeFuture().sync();

        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }

    private static SslContext createHttp2SSLContext() throws Exception {
        SelfSignedCertificate ssc = new SelfSignedCertificate();

        return SslContextBuilder.forServer(ssc.certificate(), ssc.privateKey())
                .sslProvider(SslProvider.OPENSSL)
                .ciphers(Http2SecurityUtil.CIPHERS, SupportedCipherSuiteFilter.INSTANCE)
                .applicationProtocolConfig(new ApplicationProtocolConfig(
                    ApplicationProtocolConfig.Protocol.ALPN,
                    ApplicationProtocolConfig.SelectorFailureBehavior.NO_ADVERTISE,
                    ApplicationProtocolConfig.SelectedListenerFailureBehavior.ACCEPT,
                    ApplicationProtocolNames.HTTP_2))
                .build();
    }
}

// HTTP/2 初始化器
class Http2ServerInitializer extends ChannelInitializer<SocketChannel> {
    private final SslContext sslCtx;

    public Http2ServerInitializer(SslContext sslCtx) {
        this.sslCtx = sslCtx;
    }

    @Override
    protected void initChannel(SocketChannel ch) {
        ChannelPipeline pipeline = ch.pipeline();
        pipeline.addLast(sslCtx.newHandler(ch.alloc()));
        pipeline.addLast(new ApplicationProtocolNegotiationHandler("") {
            @Override
            protected void configurePipeline(ChannelHandlerContext ctx, String protocol) {
                if (ApplicationProtocolNames.HTTP_2.equals(protocol)) {
                    configureHttp2(ctx);
                } else if (ApplicationProtocolNames.HTTP_1_1.equals(protocol)) {
                    configureHttp1(ctx);
                } else {
                    throw new IllegalStateException("Unknown protocol: " + protocol);
                }
            }
        });
    }

    private void configureHttp2(ChannelHandlerContext ctx) {
        // HTTP/2 配置
        Http2ConnectionHandler connectionHandler = new Http2ConnectionHandlerBuilder()
                .frameListener(new Http2FrameAdapter() {
                    @Override
                    public void onDataRead(ChannelHandlerContext ctx, int streamId,
                                         ByteBuf data, int padding, boolean endOfStream) {
                        // 处理 HTTP/2 数据帧
                    }

                    @Override
                    public void onHeadersRead(ChannelHandlerContext ctx, int streamId,
                                            Http2Headers headers, int padding, boolean endOfStream) {
                        // 处理 HTTP/2 头部帧
                        sendHttp2Response(ctx, streamId, headers);
                    }
                })
                .build();

        ctx.pipeline().addLast(connectionHandler);
    }

    private void configureHttp1(ChannelHandlerContext ctx) {
        // HTTP/1.1 降级配置
        ChannelPipeline pipeline = ctx.pipeline();
        pipeline.addLast(new HttpServerCodec());
        pipeline.addLast(new HttpObjectAggregator(65536));
        pipeline.addLast(new HttpServerHandler());
    }

    private void sendHttp2Response(ChannelHandlerContext ctx, int streamId, Http2Headers headers) {
        // 构建 HTTP/2 响应
        String content = "HTTP/2 Response for stream " + streamId;
        ByteBuf responseContent = Unpooled.copiedBuffer(content, CharsetUtil.UTF_8);

        Http2Headers responseHeaders = new DefaultHttp2Headers()
                .status("200")
                .set("content-type", "text/plain")
                .setInt("content-length", responseContent.readableBytes());

        // 发送响应头
        ctx.writeAndFlush(new DefaultHttp2HeadersFrame(responseHeaders, false).stream(
            Http2CodecUtil.streamIdToInt(streamId)));

        // 发送响应数据
        ctx.writeAndFlush(new DefaultHttp2DataFrame(responseContent, true).stream(
            Http2CodecUtil.streamIdToInt(streamId)));
    }
}
```

## 六、最佳实践

### 6.1 生产环境配置

```java
// 生产环境 Netty 服务器配置
public class ProductionNettyServer {

    public static ServerBootstrap createProductionServer() {
        // 优化的线程组配置
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup(
            Math.min(Runtime.getRuntime().availableProcessors() * 2, 32));

        ServerBootstrap bootstrap = new ServerBootstrap();
        bootstrap.group(bossGroup, workerGroup)
                .channel(NioServerSocketChannel.class)
                // Socket 选项优化
                .option(ChannelOption.SO_BACKLOG, 1024)
                .option(ChannelOption.SO_REUSEADDR, true)
                .childOption(ChannelOption.SO_KEEPALIVE, true)
                .childOption(ChannelOption.TCP_NODELAY, true)
                .childOption(ChannelOption.SO_RCVBUF, 32 * 1024)
                .childOption(ChannelOption.SO_SNDBUF, 32 * 1024)
                // 内存分配器优化
                .childOption(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
                .childOption(ChannelOption.RCVBUF_ALLOCATOR,
                    new AdaptiveRecvByteBufAllocator(64, 1024, 65536))
                // 写缓冲区优化
                .childOption(ChannelOption.WRITE_BUFFER_WATER_MARK,
                    new WriteBufferWaterMark(8 * 1024, 32 * 1024))
                // 连接超时
                .childOption(ChannelOption.CONNECT_TIMEOUT_MILLIS, 10000);

        return bootstrap;
    }

    // 优雅关闭
    public static void gracefulShutdown(EventLoopGroup... groups) {
        for (EventLoopGroup group : groups) {
            try {
                group.shutdownGracefully(5, 15, TimeUnit.SECONDS).sync();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
```

### 6.2 错误处理

```java
// 全局异常处理器
public class GlobalExceptionHandler extends ChannelInboundHandlerAdapter {
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        if (cause instanceof IOException) {
            logger.debug("Connection reset by peer: {}", ctx.channel().remoteAddress());
        } else if (cause instanceof TooLongFrameException) {
            logger.warn("Frame too long from: {}", ctx.channel().remoteAddress());
            sendErrorResponse(ctx, HttpResponseStatus.REQUEST_ENTITY_TOO_LARGE);
        } else if (cause instanceof DecoderException) {
            logger.warn("Decode error from: {}, error: {}",
                       ctx.channel().remoteAddress(), cause.getMessage());
            sendErrorResponse(ctx, HttpResponseStatus.BAD_REQUEST);
        } else {
            logger.error("Unexpected exception from: {}",
                        ctx.channel().remoteAddress(), cause);
            sendErrorResponse(ctx, HttpResponseStatus.INTERNAL_SERVER_ERROR);
        }

        ctx.close();
    }

    private void sendErrorResponse(ChannelHandlerContext ctx, HttpResponseStatus status) {
        String content = "Error: " + status.toString();
        ByteBuf buf = Unpooled.copiedBuffer(content, CharsetUtil.UTF_8);

        FullHttpResponse response = new DefaultFullHttpResponse(
            HttpVersion.HTTP_1_1, status, buf);

        response.headers().set(HttpHeaderNames.CONTENT_TYPE, "text/plain");
        response.headers().set(HttpHeaderNames.CONTENT_LENGTH, buf.readableBytes());

        ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
    }
}
```

### 6.3 日志和监控

```java
// 日志配置
public class NettyLogging {

    // 自定义日志处理器
    public static class CustomLoggingHandler extends LoggingHandler {
        public CustomLoggingHandler() {
            super("NettyServer", LogLevel.INFO);
        }

        @Override
        public void channelActive(ChannelHandlerContext ctx) throws Exception {
            logger.info("Client connected from: {}", ctx.channel().remoteAddress());
            super.channelActive(ctx);
        }

        @Override
        public void channelInactive(ChannelHandlerContext ctx) throws Exception {
            logger.info("Client disconnected: {}", ctx.channel().remoteAddress());
            super.channelInactive(ctx);
        }
    }

    // 请求日志处理器
    public static class RequestLoggingHandler extends ChannelInboundHandlerAdapter {
        private long startTime;

        @Override
        public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
            startTime = System.currentTimeMillis();
            super.channelRead(ctx, msg);
        }

        @Override
        public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) throws Exception {
            promise.addListener(future -> {
                long duration = System.currentTimeMillis() - startTime;
                logger.info("Request processed in {}ms", duration);
            });
            super.write(ctx, msg, promise);
        }
    }
}
```

## 七、总结

Netty 作为业界领先的异步网络编程框架，在构建高性能网络应用方面具有无可比拟的优势。通过本文的深入讲解，你应该已经掌握了：

### 核心收获

1. **理论基础**：EventLoop、Channel、Pipeline 等核心概念
2. **实战技能**：HTTP 服务器、WebSocket、自定义协议实现
3. **性能优化**：JVM 调优、系统优化、代码优化技巧
4. **高级特性**：SSL/TLS、HTTP/2、自定义协议
5. **最佳实践**：生产环境配置、错误处理、监控日志

### 性能优势总结

从我们的性能测试图表中可以看出：

- **吞吐量**：Netty 在各种负载下都表现出色，特别是小数据包场景
- **延迟**：P99 延迟控制在 3ms 以内，远优于传统框架
- **并发**：单机可支持数万并发连接，内存占用合理
- **资源利用**：CPU 和内存使用效率高，扩展性好

### 应用场景

Netty 适用于以下场景：

- **微服务架构**：服务间高性能通信
- **游戏服务器**：实时通信和状态同步
- **消息中间件**：高吞吐量消息处理
- **Web 服务器**：高并发 HTTP 服务
- **IoT 平台**：设备连接和数据收集

掌握 Netty，就掌握了构建高性能网络应用的核心技能。随着微服务和云原生技术的发展，Netty 的重要性将会越来越突出。

---

*延伸学习：建议深入研究 Netty 源码，理解其内部实现机制，这对于编写高质量的网络应用代码大有裨益。*