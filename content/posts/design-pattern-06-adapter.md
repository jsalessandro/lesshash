---
title: "设计模式详解：适配器模式(Adapter) - 让不兼容的接口协同工作"
date: 2024-12-06T10:06:00+08:00
draft: false
tags: ["设计模式", "适配器模式", "Adapter", "Java", "结构型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解适配器模式，从基础概念到高级实现，包含对象适配器、类适配器等实战技巧，让你彻底掌握接口兼容性解决方案"
---

## 🎯 什么是适配器模式？

### 生活中的例子
想象一下，你有一个中国的三孔插头，但现在在美国需要充电，墙上只有美式的两孔插座。这时你需要一个**转换器**（适配器），让中国插头能够插入美式插座。这就是适配器模式的核心思想：**让不兼容的接口能够协同工作**。

### 问题背景
在软件开发中，经常遇到接口不兼容的情况：
- 🔌 **第三方库接口** 与系统接口不匹配
- 📱 **旧系统接口** 与新系统接口不兼容
- 🌐 **外部API接口** 格式与内部接口不一致
- 📊 **数据格式转换** 需要统一接口
- 🔧 **工具类集成** 接口标准不同

如果不使用适配器模式，会导致：
- 大量修改现有代码
- 系统耦合度增加
- 接口标准混乱

## 🧠 设计思想

### 核心角色
1. **Target（目标接口）** - 客户端期望的接口
2. **Adaptee（被适配者）** - 需要被适配的现有接口
3. **Adapter（适配器）** - 转换器，连接Target和Adaptee
4. **Client（客户端）** - 使用Target接口的代码

### 记忆口诀
> **"接口不合，适配器搭桥"**

## 💻 代码实现

### 1. 对象适配器模式（推荐）

```java
/**
 * 目标接口 - 客户端期望的接口
 */
public interface MediaPlayer {
    void play(String audioType, String fileName);
}

/**
 * 被适配者 - 高级媒体播放器
 */
public class AdvancedMediaPlayer {
    public void playVlc(String fileName) {
        System.out.println("播放 VLC 文件: " + fileName);
    }

    public void playMp4(String fileName) {
        System.out.println("播放 MP4 文件: " + fileName);
    }
}

/**
 * 适配器 - 连接MediaPlayer和AdvancedMediaPlayer
 */
public class MediaAdapter implements MediaPlayer {
    private AdvancedMediaPlayer advancedPlayer;

    public MediaAdapter(String audioType) {
        if ("vlc".equalsIgnoreCase(audioType) || "mp4".equalsIgnoreCase(audioType)) {
            advancedPlayer = new AdvancedMediaPlayer();
        }
    }

    @Override
    public void play(String audioType, String fileName) {
        if ("vlc".equalsIgnoreCase(audioType)) {
            advancedPlayer.playVlc(fileName);
        } else if ("mp4".equalsIgnoreCase(audioType)) {
            advancedPlayer.playMp4(fileName);
        } else {
            System.out.println("不支持的媒体格式: " + audioType);
        }
    }
}

/**
 * 音频播放器 - 实现基本的MP3播放功能
 */
public class AudioPlayer implements MediaPlayer {
    private MediaAdapter mediaAdapter;

    @Override
    public void play(String audioType, String fileName) {
        // 内置支持MP3格式
        if ("mp3".equalsIgnoreCase(audioType)) {
            System.out.println("播放 MP3 文件: " + fileName);
        }
        // 通过适配器支持其他格式
        else if ("vlc".equalsIgnoreCase(audioType) || "mp4".equalsIgnoreCase(audioType)) {
            mediaAdapter = new MediaAdapter(audioType);
            mediaAdapter.play(audioType, fileName);
        } else {
            System.out.println("不支持的媒体格式: " + audioType);
        }
    }
}

// 使用示例
public class MediaPlayerDemo {
    public static void main(String[] args) {
        System.out.println("=== 媒体播放器适配器演示 ===");

        AudioPlayer audioPlayer = new AudioPlayer();

        System.out.println("\n播放不同格式的文件：");
        audioPlayer.play("mp3", "歌曲.mp3");
        audioPlayer.play("mp4", "电影.mp4");
        audioPlayer.play("vlc", "视频.vlc");
        audioPlayer.play("avi", "不支持.avi");
    }
}
```

### 2. 类适配器模式

```java
/**
 * 目标接口 - 新的打印接口
 */
public interface NewPrinter {
    void print(String content);
    void printColor(String content, String color);
}

/**
 * 被适配者 - 旧的打印机类
 */
public class OldPrinter {
    public void oldPrint(String text) {
        System.out.println("[旧打印机] 打印: " + text);
    }

    public void oldPrintWithFormat(String text, String format) {
        System.out.println("[旧打印机] " + format + " 格式打印: " + text);
    }
}

/**
 * 类适配器 - 通过继承实现适配
 */
public class PrinterClassAdapter extends OldPrinter implements NewPrinter {

    @Override
    public void print(String content) {
        // 调用父类的旧方法
        super.oldPrint(content);
    }

    @Override
    public void printColor(String content, String color) {
        // 将颜色参数转换为旧接口的格式参数
        String format = "【" + color + "色】";
        super.oldPrintWithFormat(content, format);
    }
}

// 类适配器使用示例
public class ClassAdapterDemo {
    public static void main(String[] args) {
        System.out.println("=== 类适配器模式演示 ===");

        NewPrinter printer = new PrinterClassAdapter();

        printer.print("这是一份文档");
        printer.printColor("这是彩色文档", "红");
        printer.printColor("这是另一份彩色文档", "蓝");
    }
}
```

### 3. 双向适配器

```java
/**
 * 中国电器接口
 */
public interface ChineseSocket {
    void powerOnWith220V();
}

/**
 * 美国电器接口
 */
public interface AmericanSocket {
    void powerOnWith110V();
}

/**
 * 中国电器
 */
public class ChineseElectricDevice implements ChineseSocket {
    private String deviceName;

    public ChineseElectricDevice(String deviceName) {
        this.deviceName = deviceName;
    }

    @Override
    public void powerOnWith220V() {
        System.out.println("中国电器 [" + deviceName + "] 使用220V供电启动");
    }
}

/**
 * 美国电器
 */
public class AmericanElectricDevice implements AmericanSocket {
    private String deviceName;

    public AmericanElectricDevice(String deviceName) {
        this.deviceName = deviceName;
    }

    @Override
    public void powerOnWith110V() {
        System.out.println("美国电器 [" + deviceName + "] 使用110V供电启动");
    }
}

/**
 * 双向适配器 - 既可以让中国电器使用美国插座，也可以让美国电器使用中国插座
 */
public class BidirectionalAdapter implements ChineseSocket, AmericanSocket {
    private ChineseSocket chineseSocket;
    private AmericanSocket americanSocket;

    public BidirectionalAdapter(ChineseSocket chineseSocket, AmericanSocket americanSocket) {
        this.chineseSocket = chineseSocket;
        this.americanSocket = americanSocket;
    }

    // 美国插座供电，但中国电器需要220V
    @Override
    public void powerOnWith220V() {
        System.out.println("适配器：将110V升压转换为220V");
        if (americanSocket != null) {
            americanSocket.powerOnWith110V();
            System.out.println("适配器：转换完成，中国电器可以正常工作");
        } else {
            chineseSocket.powerOnWith220V();
        }
    }

    // 中国插座供电，但美国电器需要110V
    @Override
    public void powerOnWith110V() {
        System.out.println("适配器：将220V降压转换为110V");
        if (chineseSocket != null) {
            chineseSocket.powerOnWith220V();
            System.out.println("适配器：转换完成，美国电器可以正常工作");
        } else {
            americanSocket.powerOnWith110V();
        }
    }
}

// 双向适配器演示
public class BidirectionalAdapterDemo {
    public static void main(String[] args) {
        System.out.println("=== 双向适配器演示 ===");

        // 创建中国和美国电器
        ChineseSocket chineseDevice = new ChineseElectricDevice("电饭煲");
        AmericanSocket americanDevice = new AmericanElectricDevice("咖啡机");

        System.out.println("\n=== 场景1：在美国使用中国电器 ===");
        BidirectionalAdapter adapter1 = new BidirectionalAdapter(chineseDevice, null);
        // 模拟：在美国（110V环境）使用中国电器（需要220V）
        adapter1.powerOnWith220V();

        System.out.println("\n=== 场景2：在中国使用美国电器 ===");
        BidirectionalAdapter adapter2 = new BidirectionalAdapter(null, americanDevice);
        // 模拟：在中国（220V环境）使用美国电器（需要110V）
        adapter2.powerOnWith110V();

        System.out.println("\n=== 场景3：万能适配器 ===");
        BidirectionalAdapter universalAdapter = new BidirectionalAdapter(chineseDevice, americanDevice);
        System.out.println("中国电器通过适配器工作：");
        universalAdapter.powerOnWith220V();

        System.out.println("\n美国电器通过适配器工作：");
        universalAdapter.powerOnWith110V();
    }
}
```

## 🌟 实际应用场景

### 1. 数据库连接适配器

```java
/**
 * 统一的数据库接口
 */
public interface DatabaseConnection {
    void connect(String host, int port, String database);
    void disconnect();
    String executeQuery(String sql);
    boolean executeUpdate(String sql);
}

/**
 * MySQL数据库连接（第三方库）
 */
public class MySQLConnection {
    private String connectionString;

    public void establishConnection(String server, int port, String dbName) {
        this.connectionString = "mysql://" + server + ":" + port + "/" + dbName;
        System.out.println("MySQL连接已建立: " + connectionString);
    }

    public void closeConnection() {
        System.out.println("MySQL连接已关闭");
    }

    public String runQuery(String query) {
        System.out.println("执行MySQL查询: " + query);
        return "MySQL查询结果: " + query;
    }

    public boolean runUpdate(String updateSql) {
        System.out.println("执行MySQL更新: " + updateSql);
        return true;
    }
}

/**
 * Oracle数据库连接（另一个第三方库）
 */
public class OracleConnection {
    private String oracleUrl;

    public void initConnection(String hostname, int portNumber, String sid) {
        this.oracleUrl = "oracle:thin:@" + hostname + ":" + portNumber + ":" + sid;
        System.out.println("Oracle连接已初始化: " + oracleUrl);
    }

    public void terminateConnection() {
        System.out.println("Oracle连接已终止");
    }

    public String performQuery(String sqlStatement) {
        System.out.println("执行Oracle查询: " + sqlStatement);
        return "Oracle查询结果: " + sqlStatement;
    }

    public boolean performUpdate(String sqlStatement) {
        System.out.println("执行Oracle更新: " + sqlStatement);
        return true;
    }
}

/**
 * MySQL适配器
 */
public class MySQLAdapter implements DatabaseConnection {
    private MySQLConnection mysqlConnection;

    public MySQLAdapter() {
        this.mysqlConnection = new MySQLConnection();
    }

    @Override
    public void connect(String host, int port, String database) {
        mysqlConnection.establishConnection(host, port, database);
    }

    @Override
    public void disconnect() {
        mysqlConnection.closeConnection();
    }

    @Override
    public String executeQuery(String sql) {
        return mysqlConnection.runQuery(sql);
    }

    @Override
    public boolean executeUpdate(String sql) {
        return mysqlConnection.runUpdate(sql);
    }
}

/**
 * Oracle适配器
 */
public class OracleAdapter implements DatabaseConnection {
    private OracleConnection oracleConnection;

    public OracleAdapter() {
        this.oracleConnection = new OracleConnection();
    }

    @Override
    public void connect(String host, int port, String database) {
        oracleConnection.initConnection(host, port, database);
    }

    @Override
    public void disconnect() {
        oracleConnection.terminateConnection();
    }

    @Override
    public String executeQuery(String sql) {
        return oracleConnection.performQuery(sql);
    }

    @Override
    public boolean executeUpdate(String sql) {
        return oracleConnection.performUpdate(sql);
    }
}

/**
 * 数据库管理器 - 统一使用各种数据库
 */
public class DatabaseManager {
    private DatabaseConnection connection;

    public DatabaseManager(DatabaseConnection connection) {
        this.connection = connection;
    }

    public void initializeDatabase(String host, int port, String database) {
        connection.connect(host, port, database);
    }

    public void performDataMigration() {
        System.out.println("\n=== 开始数据迁移 ===");

        String[] queries = {
            "SELECT * FROM users",
            "SELECT * FROM orders",
            "SELECT * FROM products"
        };

        for (String query : queries) {
            String result = connection.executeQuery(query);
            System.out.println("查询结果: " + result);
        }

        String[] updates = {
            "UPDATE users SET status = 'active'",
            "INSERT INTO logs VALUES ('migration', NOW())"
        };

        for (String update : updates) {
            boolean success = connection.executeUpdate(update);
            System.out.println("更新操作结果: " + (success ? "成功" : "失败"));
        }
    }

    public void cleanup() {
        connection.disconnect();
        System.out.println("数据库操作完成");
    }
}

// 数据库适配器演示
public class DatabaseAdapterDemo {
    public static void main(String[] args) {
        System.out.println("=== 数据库连接适配器演示 ===");

        System.out.println("\n=== 使用MySQL数据库 ===");
        DatabaseConnection mysqlAdapter = new MySQLAdapter();
        DatabaseManager mysqlManager = new DatabaseManager(mysqlAdapter);
        mysqlManager.initializeDatabase("localhost", 3306, "myapp");
        mysqlManager.performDataMigration();
        mysqlManager.cleanup();

        System.out.println("\n=== 使用Oracle数据库 ===");
        DatabaseConnection oracleAdapter = new OracleAdapter();
        DatabaseManager oracleManager = new DatabaseManager(oracleAdapter);
        oracleManager.initializeDatabase("localhost", 1521, "ORCL");
        oracleManager.performDataMigration();
        oracleManager.cleanup();

        System.out.println("\n观察：相同的DatabaseManager代码可以无缝切换不同的数据库！");
    }
}
```

### 2. 支付系统适配器

```java
/**
 * 统一支付接口
 */
public interface PaymentProcessor {
    PaymentResult processPayment(PaymentRequest request);
    PaymentResult queryPayment(String transactionId);
    RefundResult processRefund(RefundRequest request);
}

/**
 * 支付请求对象
 */
public class PaymentRequest {
    private String orderId;
    private double amount;
    private String currency;
    private String description;

    public PaymentRequest(String orderId, double amount, String currency, String description) {
        this.orderId = orderId;
        this.amount = amount;
        this.currency = currency;
        this.description = description;
    }

    // getter方法
    public String getOrderId() { return orderId; }
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public String getDescription() { return description; }
}

/**
 * 支付结果对象
 */
public class PaymentResult {
    private boolean success;
    private String transactionId;
    private String message;

    public PaymentResult(boolean success, String transactionId, String message) {
        this.success = success;
        this.transactionId = transactionId;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getMessage() { return message; }

    @Override
    public String toString() {
        return String.format("PaymentResult{success=%s, transactionId='%s', message='%s'}",
                           success, transactionId, message);
    }
}

/**
 * 退款请求对象
 */
public class RefundRequest {
    private String originalTransactionId;
    private double refundAmount;
    private String reason;

    public RefundRequest(String originalTransactionId, double refundAmount, String reason) {
        this.originalTransactionId = originalTransactionId;
        this.refundAmount = refundAmount;
        this.reason = reason;
    }

    public String getOriginalTransactionId() { return originalTransactionId; }
    public double getRefundAmount() { return refundAmount; }
    public String getReason() { return reason; }
}

/**
 * 退款结果对象
 */
public class RefundResult {
    private boolean success;
    private String refundId;
    private String message;

    public RefundResult(boolean success, String refundId, String message) {
        this.success = success;
        this.refundId = refundId;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getRefundId() { return refundId; }
    public String getMessage() { return message; }

    @Override
    public String toString() {
        return String.format("RefundResult{success=%s, refundId='%s', message='%s'}",
                           success, refundId, message);
    }
}

/**
 * 支付宝支付SDK（第三方）
 */
public class AlipaySDK {
    public String createPayment(String orderNo, double money, String desc) {
        System.out.println("调用支付宝SDK创建支付订单");
        System.out.println("订单号: " + orderNo + ", 金额: " + money + ", 描述: " + desc);
        return "ALIPAY_" + System.currentTimeMillis();
    }

    public boolean checkPaymentStatus(String alipayTransactionId) {
        System.out.println("查询支付宝支付状态: " + alipayTransactionId);
        return true; // 模拟支付成功
    }

    public String refundPayment(String transactionId, double amount, String reason) {
        System.out.println("支付宝退款: " + transactionId + ", 金额: " + amount + ", 原因: " + reason);
        return "REFUND_" + System.currentTimeMillis();
    }
}

/**
 * 微信支付SDK（第三方）
 */
public class WeChatPaySDK {
    public String submitPayOrder(String orderCode, int amountInCents, String productInfo) {
        System.out.println("调用微信支付SDK提交订单");
        System.out.println("订单码: " + orderCode + ", 金额(分): " + amountInCents + ", 商品信息: " + productInfo);
        return "WECHAT_" + System.currentTimeMillis();
    }

    public int getPaymentResult(String wechatOrderId) {
        System.out.println("查询微信支付结果: " + wechatOrderId);
        return 1; // 1表示成功，0表示失败
    }

    public boolean applyRefund(String originalOrderId, int refundAmountInCents) {
        System.out.println("微信支付退款申请: " + originalOrderId + ", 退款金额(分): " + refundAmountInCents);
        return true;
    }
}

/**
 * 支付宝适配器
 */
public class AlipayAdapter implements PaymentProcessor {
    private AlipaySDK alipaySDK;

    public AlipayAdapter() {
        this.alipaySDK = new AlipaySDK();
    }

    @Override
    public PaymentResult processPayment(PaymentRequest request) {
        try {
            String transactionId = alipaySDK.createPayment(
                request.getOrderId(),
                request.getAmount(),
                request.getDescription()
            );
            return new PaymentResult(true, transactionId, "支付宝支付成功");
        } catch (Exception e) {
            return new PaymentResult(false, null, "支付宝支付失败: " + e.getMessage());
        }
    }

    @Override
    public PaymentResult queryPayment(String transactionId) {
        boolean success = alipaySDK.checkPaymentStatus(transactionId);
        return new PaymentResult(success, transactionId,
                               success ? "支付成功" : "支付失败");
    }

    @Override
    public RefundResult processRefund(RefundRequest request) {
        try {
            String refundId = alipaySDK.refundPayment(
                request.getOriginalTransactionId(),
                request.getRefundAmount(),
                request.getReason()
            );
            return new RefundResult(true, refundId, "支付宝退款成功");
        } catch (Exception e) {
            return new RefundResult(false, null, "支付宝退款失败: " + e.getMessage());
        }
    }
}

/**
 * 微信支付适配器
 */
public class WeChatPayAdapter implements PaymentProcessor {
    private WeChatPaySDK weChatPaySDK;

    public WeChatPayAdapter() {
        this.weChatPaySDK = new WeChatPaySDK();
    }

    @Override
    public PaymentResult processPayment(PaymentRequest request) {
        try {
            // 微信支付金额需要转换为分
            int amountInCents = (int) (request.getAmount() * 100);
            String transactionId = weChatPaySDK.submitPayOrder(
                request.getOrderId(),
                amountInCents,
                request.getDescription()
            );
            return new PaymentResult(true, transactionId, "微信支付成功");
        } catch (Exception e) {
            return new PaymentResult(false, null, "微信支付失败: " + e.getMessage());
        }
    }

    @Override
    public PaymentResult queryPayment(String transactionId) {
        int result = weChatPaySDK.getPaymentResult(transactionId);
        return new PaymentResult(result == 1, transactionId,
                               result == 1 ? "支付成功" : "支付失败");
    }

    @Override
    public RefundResult processRefund(RefundRequest request) {
        try {
            // 微信退款金额需要转换为分
            int refundAmountInCents = (int) (request.getRefundAmount() * 100);
            boolean success = weChatPaySDK.applyRefund(
                request.getOriginalTransactionId(),
                refundAmountInCents
            );
            String refundId = success ? "WECHAT_REFUND_" + System.currentTimeMillis() : null;
            return new RefundResult(success, refundId,
                                  success ? "微信退款成功" : "微信退款失败");
        } catch (Exception e) {
            return new RefundResult(false, null, "微信退款失败: " + e.getMessage());
        }
    }
}

/**
 * 支付服务管理器
 */
public class PaymentService {
    private PaymentProcessor paymentProcessor;

    public PaymentService(PaymentProcessor paymentProcessor) {
        this.paymentProcessor = paymentProcessor;
    }

    public void processOrder(String orderId, double amount, String description) {
        System.out.println("\n=== 处理订单支付 ===");
        System.out.println("订单ID: " + orderId);
        System.out.println("支付金额: ¥" + amount);

        PaymentRequest request = new PaymentRequest(orderId, amount, "CNY", description);
        PaymentResult result = paymentProcessor.processPayment(request);

        System.out.println("支付结果: " + result);

        if (result.isSuccess()) {
            // 查询支付状态
            PaymentResult queryResult = paymentProcessor.queryPayment(result.getTransactionId());
            System.out.println("支付状态查询: " + queryResult);
        }
    }

    public void processRefund(String transactionId, double refundAmount, String reason) {
        System.out.println("\n=== 处理退款申请 ===");
        System.out.println("原交易ID: " + transactionId);
        System.out.println("退款金额: ¥" + refundAmount);

        RefundRequest request = new RefundRequest(transactionId, refundAmount, reason);
        RefundResult result = paymentProcessor.processRefund(request);

        System.out.println("退款结果: " + result);
    }
}

// 支付系统适配器演示
public class PaymentAdapterDemo {
    public static void main(String[] args) {
        System.out.println("=== 支付系统适配器演示 ===");

        // 使用支付宝支付
        System.out.println("\n=== 支付宝支付 ===");
        PaymentProcessor alipayProcessor = new AlipayAdapter();
        PaymentService alipayService = new PaymentService(alipayProcessor);
        alipayService.processOrder("ORDER_001", 99.99, "购买商品A");

        // 模拟退款
        alipayService.processRefund("ALIPAY_" + System.currentTimeMillis(), 50.0, "用户主动退款");

        // 使用微信支付
        System.out.println("\n=== 微信支付 ===");
        PaymentProcessor wechatProcessor = new WeChatPayAdapter();
        PaymentService wechatService = new PaymentService(wechatProcessor);
        wechatService.processOrder("ORDER_002", 199.99, "购买商品B");

        // 模拟退款
        wechatService.processRefund("WECHAT_" + System.currentTimeMillis(), 100.0, "商品质量问题");

        System.out.println("\n观察：相同的PaymentService代码可以处理不同的支付渠道！");
    }
}
```

### 3. 日志系统适配器

```java
/**
 * 统一日志接口
 */
public interface Logger {
    void info(String message);
    void warn(String message);
    void error(String message);
    void debug(String message);
}

/**
 * Log4j日志库（第三方）
 */
public class Log4jLogger {
    private String loggerName;

    public Log4jLogger(String loggerName) {
        this.loggerName = loggerName;
    }

    public void logInfo(String msg) {
        System.out.println("[Log4j-INFO] " + loggerName + ": " + msg);
    }

    public void logWarning(String msg) {
        System.out.println("[Log4j-WARN] " + loggerName + ": " + msg);
    }

    public void logError(String msg) {
        System.out.println("[Log4j-ERROR] " + loggerName + ": " + msg);
    }

    public void logDebug(String msg) {
        System.out.println("[Log4j-DEBUG] " + loggerName + ": " + msg);
    }
}

/**
 * Java Util Logging（JUL）
 */
public class JULLogger {
    private String category;

    public JULLogger(String category) {
        this.category = category;
    }

    public void info(String text) {
        System.out.println("[JUL-INFO] " + category + ": " + text);
    }

    public void warning(String text) {
        System.out.println("[JUL-WARNING] " + category + ": " + text);
    }

    public void severe(String text) {
        System.out.println("[JUL-SEVERE] " + category + ": " + text);
    }

    public void fine(String text) {
        System.out.println("[JUL-FINE] " + category + ": " + text);
    }
}

/**
 * Log4j适配器
 */
public class Log4jAdapter implements Logger {
    private Log4jLogger log4jLogger;

    public Log4jAdapter(String loggerName) {
        this.log4jLogger = new Log4jLogger(loggerName);
    }

    @Override
    public void info(String message) {
        log4jLogger.logInfo(message);
    }

    @Override
    public void warn(String message) {
        log4jLogger.logWarning(message);
    }

    @Override
    public void error(String message) {
        log4jLogger.logError(message);
    }

    @Override
    public void debug(String message) {
        log4jLogger.logDebug(message);
    }
}

/**
 * JUL适配器
 */
public class JULAdapter implements Logger {
    private JULLogger julLogger;

    public JULAdapter(String category) {
        this.julLogger = new JULLogger(category);
    }

    @Override
    public void info(String message) {
        julLogger.info(message);
    }

    @Override
    public void warn(String message) {
        julLogger.warning(message);
    }

    @Override
    public void error(String message) {
        julLogger.severe(message);
    }

    @Override
    public void debug(String message) {
        julLogger.fine(message);
    }
}

/**
 * 应用程序类 - 使用统一的日志接口
 */
public class Application {
    private Logger logger;

    public Application(Logger logger) {
        this.logger = logger;
    }

    public void runApplication() {
        logger.info("应用程序启动");
        logger.debug("加载配置文件");

        try {
            businessLogic();
        } catch (Exception e) {
            logger.error("业务逻辑执行失败: " + e.getMessage());
        }

        logger.info("应用程序结束");
    }

    private void businessLogic() {
        logger.info("开始执行业务逻辑");
        logger.debug("连接数据库");
        logger.warn("检测到性能警告");
        logger.info("业务逻辑执行完成");
    }
}

// 日志适配器演示
public class LoggerAdapterDemo {
    public static void main(String[] args) {
        System.out.println("=== 日志系统适配器演示 ===");

        System.out.println("\n=== 使用Log4j日志库 ===");
        Logger log4jAdapter = new Log4jAdapter("MyApplication");
        Application app1 = new Application(log4jAdapter);
        app1.runApplication();

        System.out.println("\n=== 使用JUL日志库 ===");
        Logger julAdapter = new JULAdapter("MyApplication");
        Application app2 = new Application(julAdapter);
        app2.runApplication();

        System.out.println("\n观察：相同的Application代码可以使用不同的日志库！");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **解耦合**
   - 客户端不需要知道被适配者的具体实现
   - 降低系统间的耦合度

2. **重用现有代码**
   - 无需修改现有类
   - 充分利用已有功能

3. **符合开闭原则**
   - 对扩展开放，对修改关闭
   - 易于添加新的适配器

4. **透明性**
   - 客户端使用统一接口
   - 屏蔽底层实现差异

### ❌ 缺点

1. **增加系统复杂性**
   - 引入额外的适配器类
   - 增加了类的数量

2. **性能开销**
   - 多了一层间接调用
   - 轻微的性能损失

3. **维护成本**
   - 需要维护适配器代码
   - 被适配者变化时需要同步更新

## 🎯 使用场景总结

### 适合使用适配器模式的场景：
- 🔌 **第三方库集成** - 统一不同库的接口
- 🏢 **系统集成** - 连接新旧系统
- 📊 **数据格式转换** - 统一数据访问接口
- 🌐 **API网关** - 统一外部服务调用
- 🔧 **工具类整合** - 统一工具接口

### 不适合使用适配器模式的场景：
- 接口完全一致的情况
- 简单的功能调用
- 性能要求极高的场景
- 被适配者经常变化的情况

## 🧠 记忆技巧

### 形象比喻
> **适配器模式就像是 "翻译官"**：
> - 两个人说不同的语言（接口不兼容）
> - 翻译官负责转换（适配器转换调用）
> - 双方都能正常交流（统一使用目标接口）
> - 不需要学习对方语言（不需要修改现有代码）

### 实现要点
> **"新接口，旧实现，适配器来做转换"**

### 选择建议
1. **对象适配器** → 推荐使用，更灵活
2. **类适配器** → 单继承语言中使用限制
3. **双向适配器** → 需要双向转换时使用

## 🔧 最佳实践

### 1. 适配器工厂模式

```java
/**
 * 适配器工厂 - 统一创建不同类型的适配器
 */
public class AdapterFactory {
    public static PaymentProcessor createPaymentAdapter(String paymentType) {
        switch (paymentType.toLowerCase()) {
            case "alipay":
                return new AlipayAdapter();
            case "wechat":
                return new WeChatPayAdapter();
            default:
                throw new IllegalArgumentException("不支持的支付类型: " + paymentType);
        }
    }

    public static Logger createLoggerAdapter(String loggerType, String name) {
        switch (loggerType.toLowerCase()) {
            case "log4j":
                return new Log4jAdapter(name);
            case "jul":
                return new JULAdapter(name);
            default:
                throw new IllegalArgumentException("不支持的日志类型: " + loggerType);
        }
    }
}
```

### 2. 可配置的适配器

```java
/**
 * 可配置的适配器管理器
 */
public class ConfigurableAdapterManager {
    private Map<String, Class<? extends PaymentProcessor>> adapterClasses = new HashMap<>();

    public void registerAdapter(String type, Class<? extends PaymentProcessor> adapterClass) {
        adapterClasses.put(type, adapterClass);
    }

    public PaymentProcessor createAdapter(String type) throws Exception {
        Class<? extends PaymentProcessor> adapterClass = adapterClasses.get(type);
        if (adapterClass != null) {
            return adapterClass.getDeclaredConstructor().newInstance();
        }
        throw new IllegalArgumentException("未注册的适配器类型: " + type);
    }
}
```

## 🚀 总结

适配器模式通过引入适配器层来解决接口不兼容问题，特别适用于：

- **系统集成**场景
- **第三方库整合**
- **接口标准统一**

核心思想：
- **不修改现有代码**
- **统一接口标准**
- **降低耦合度**

选择建议：
- **对象适配器**：更灵活，推荐使用
- **类适配器**：受继承限制，谨慎使用
- **双向适配器**：特殊场景下使用

记住，**适配器模式是连接器，不是万能药**，要在合适的场景下使用！

---
*下一篇：桥接模式 - 抽象与实现的分离艺术*