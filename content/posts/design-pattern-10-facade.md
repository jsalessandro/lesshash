---
title: "设计模式详解：外观模式(Facade) - 简化复杂子系统的访问"
date: 2025-09-19T01:00:00+08:00
draft: false
tags: ["设计模式", "外观模式", "Facade", "Java", "结构型模式"]
categories: ["设计模式"]
author: "lesshash"
description: "深入浅出讲解外观模式，从基础概念到高级实现，包含子系统封装、接口简化等实战技巧，让你彻底掌握复杂系统的优雅包装艺术"
---

## 🎯 什么是外观模式？

### 生活中的例子
想象一下你要在家里看电影。如果没有遥控器，你需要：打开电视 → 调整音响 → 设置投影仪 → 关闭灯光 → 准备爆米花 → 选择影片。每次都要操作这么多设备很麻烦。但有了**智能家居系统**，你只需要按一个"观影模式"按钮，所有设备就会自动配置好。这个智能家居系统就是一个"外观"，它把复杂的子系统操作包装成了一个简单的接口。这就是外观模式的核心思想：**为复杂的子系统提供一个简单的统一接口**。

### 问题背景
在软件开发中，经常面临复杂子系统的使用：
- 🏠 **智能家居** - 灯光、音响、温控、安防等多个子系统
- 💰 **支付系统** - 账户验证、风控检查、银行接口、通知服务等
- 🔧 **编译系统** - 词法分析、语法分析、优化、代码生成等
- 🌐 **Web框架** - 路由、中间件、模板、数据库等组件
- 📊 **报表系统** - 数据采集、计算、格式化、输出等步骤

如果客户端直接使用这些子系统，会导致：
- 客户端代码复杂
- 与子系统紧耦合
- 子系统变化影响客户端
- 使用门槛高

## 🧠 设计思想

### 核心角色
1. **Facade（外观类）** - 提供简化的统一接口
2. **SubSystem（子系统类）** - 实现具体的业务功能
3. **Client（客户端）** - 通过Facade访问子系统

### 核心思想
- 简化复杂接口
- 降低客户端与子系统的耦合
- 提供更高层次的接口
- 隐藏子系统的复杂性

### 记忆口诀
> **"复杂内部，简单外表，统一入口，降低耦合"**

## 💻 代码实现

### 1. 基础外观模式 - 家庭影院系统

```java
/**
 * 子系统 - 电视
 */
public class Television {
    public void turnOn() {
        System.out.println("📺 电视开机");
    }

    public void turnOff() {
        System.out.println("📺 电视关机");
    }

    public void setChannel(int channel) {
        System.out.println("📺 切换到频道 " + channel);
    }

    public void setVolume(int volume) {
        System.out.println("📺 电视音量设为 " + volume);
    }
}

/**
 * 子系统 - 音响
 */
public class SoundSystem {
    public void turnOn() {
        System.out.println("🔊 音响开机");
    }

    public void turnOff() {
        System.out.println("🔊 音响关机");
    }

    public void setVolume(int volume) {
        System.out.println("🔊 音响音量设为 " + volume);
    }

    public void setSurroundSound(boolean enabled) {
        System.out.println("🔊 环绕声: " + (enabled ? "开启" : "关闭"));
    }
}

/**
 * 子系统 - 投影仪
 */
public class Projector {
    public void turnOn() {
        System.out.println("📽️ 投影仪开机");
    }

    public void turnOff() {
        System.out.println("📽️ 投影仪关机");
    }

    public void setInput(String input) {
        System.out.println("📽️ 投影仪输入源设为 " + input);
    }

    public void adjustBrightness(int brightness) {
        System.out.println("📽️ 投影仪亮度调整为 " + brightness + "%");
    }
}

/**
 * 子系统 - 灯光控制
 */
public class LightControl {
    public void turnOn() {
        System.out.println("💡 灯光开启");
    }

    public void turnOff() {
        System.out.println("💡 灯光关闭");
    }

    public void dimLights(int level) {
        System.out.println("💡 灯光调暗至 " + level + "%");
    }

    public void setAmbientLighting() {
        System.out.println("💡 设置环境灯光");
    }
}

/**
 * 子系统 - DVD播放器
 */
public class DVDPlayer {
    public void turnOn() {
        System.out.println("📀 DVD播放器开机");
    }

    public void turnOff() {
        System.out.println("📀 DVD播放器关机");
    }

    public void play(String movie) {
        System.out.println("📀 播放电影: " + movie);
    }

    public void pause() {
        System.out.println("📀 暂停播放");
    }

    public void stop() {
        System.out.println("📀 停止播放");
    }
}

/**
 * 子系统 - 爆米花机
 */
public class PopcornMaker {
    public void turnOn() {
        System.out.println("🍿 爆米花机开机");
    }

    public void turnOff() {
        System.out.println("🍿 爆米花机关机");
    }

    public void makePopcorn() {
        System.out.println("🍿 开始制作爆米花");
    }
}

/**
 * 外观类 - 家庭影院系统
 */
public class HomeTheaterFacade {
    private Television tv;
    private SoundSystem soundSystem;
    private Projector projector;
    private LightControl lightControl;
    private DVDPlayer dvdPlayer;
    private PopcornMaker popcornMaker;

    public HomeTheaterFacade() {
        this.tv = new Television();
        this.soundSystem = new SoundSystem();
        this.projector = new Projector();
        this.lightControl = new LightControl();
        this.dvdPlayer = new DVDPlayer();
        this.popcornMaker = new PopcornMaker();
    }

    /**
     * 观影模式 - 一键开启观影环境
     */
    public void startMovie(String movieName) {
        System.out.println("🎬 启动观影模式: " + movieName);
        System.out.println("正在准备观影环境...");

        // 按顺序启动各个设备
        popcornMaker.turnOn();
        popcornMaker.makePopcorn();

        lightControl.dimLights(10);
        lightControl.setAmbientLighting();

        projector.turnOn();
        projector.setInput("HDMI1");
        projector.adjustBrightness(75);

        soundSystem.turnOn();
        soundSystem.setVolume(6);
        soundSystem.setSurroundSound(true);

        dvdPlayer.turnOn();
        dvdPlayer.play(movieName);

        System.out.println("🎬 观影环境已就绪，开始享受电影！");
    }

    /**
     * 结束观影模式
     */
    public void endMovie() {
        System.out.println("🎬 结束观影模式");
        System.out.println("正在关闭观影环境...");

        dvdPlayer.stop();
        dvdPlayer.turnOff();

        soundSystem.turnOff();

        projector.turnOff();

        lightControl.turnOn();

        popcornMaker.turnOff();

        System.out.println("🎬 观影环境已关闭");
    }

    /**
     * 游戏模式
     */
    public void startGaming() {
        System.out.println("🎮 启动游戏模式");

        lightControl.dimLights(30);

        tv.turnOn();
        tv.setChannel(3); // 游戏频道
        tv.setVolume(8);

        soundSystem.turnOn();
        soundSystem.setVolume(7);
        soundSystem.setSurroundSound(true);

        System.out.println("🎮 游戏环境已就绪！");
    }

    /**
     * 音乐模式
     */
    public void startMusic() {
        System.out.println("🎵 启动音乐模式");

        lightControl.setAmbientLighting();

        soundSystem.turnOn();
        soundSystem.setVolume(5);
        soundSystem.setSurroundSound(false);

        System.out.println("🎵 音乐环境已就绪！");
    }

    /**
     * 全部关闭
     */
    public void shutdownAll() {
        System.out.println("🔌 关闭所有设备");

        dvdPlayer.turnOff();
        tv.turnOff();
        soundSystem.turnOff();
        projector.turnOff();
        lightControl.turnOff();
        popcornMaker.turnOff();

        System.out.println("🔌 所有设备已关闭");
    }

    /**
     * 获取系统状态（可选方法）
     */
    public void getSystemStatus() {
        System.out.println("📊 系统状态检查");
        System.out.println("各子系统运行正常");
    }
}

// 家庭影院外观模式演示
public class HomeTheaterFacadeDemo {
    public static void main(String[] args) {
        System.out.println("=== 家庭影院外观模式演示 ===");

        // 创建家庭影院外观
        HomeTheaterFacade homeTheater = new HomeTheaterFacade();

        System.out.println("\n=== 客户端使用外观模式 ===");

        // 如果没有外观模式，客户端需要这样做：
        System.out.println("❌ 没有外观模式时的复杂操作:");
        System.out.println("客户端需要了解并操作每个子系统...");
        /*
        Television tv = new Television();
        SoundSystem sound = new SoundSystem();
        Projector proj = new Projector();
        LightControl lights = new LightControl();
        DVDPlayer dvd = new DVDPlayer();
        PopcornMaker popcorn = new PopcornMaker();

        // 客户端需要知道正确的启动顺序
        popcorn.turnOn();
        popcorn.makePopcorn();
        lights.dimLights(10);
        proj.turnOn();
        proj.setInput("HDMI1");
        sound.turnOn();
        sound.setVolume(6);
        dvd.turnOn();
        dvd.play("阿凡达");
        */

        System.out.println("\n✅ 使用外观模式后的简单操作:");

        // 观影模式
        homeTheater.startMovie("阿凡达");

        System.out.println("\n--- 暂停观影，切换到游戏模式 ---");
        homeTheater.endMovie();

        System.out.println();
        homeTheater.startGaming();

        System.out.println("\n--- 切换到音乐模式 ---");
        homeTheater.startMusic();

        System.out.println("\n--- 检查系统状态 ---");
        homeTheater.getSystemStatus();

        System.out.println("\n--- 关闭所有设备 ---");
        homeTheater.shutdownAll();

        System.out.println("\n=== 对比总结 ===");
        System.out.println("🔴 没有外观模式:");
        System.out.println("   - 客户端需要了解6个子系统");
        System.out.println("   - 需要记住复杂的操作顺序");
        System.out.println("   - 代码复杂度高，容易出错");
        System.out.println("   - 与子系统紧耦合");

        System.out.println("\n🟢 使用外观模式:");
        System.out.println("   - 客户端只需要了解1个外观类");
        System.out.println("   - 一行代码完成复杂操作");
        System.out.println("   - 代码简洁，不容易出错");
        System.out.println("   - 与子系统松耦合");

        System.out.println("\n观察：外观模式大大简化了客户端的使用！");
    }
}
```

### 2. 计算机启动外观模式

```java
/**
 * 子系统 - CPU
 */
public class CPU {
    public void start() {
        System.out.println("🔥 CPU启动");
    }

    public void execute() {
        System.out.println("🔥 CPU开始执行指令");
    }

    public void shutdown() {
        System.out.println("🔥 CPU关闭");
    }
}

/**
 * 子系统 - 内存
 */
public class Memory {
    public void load() {
        System.out.println("💾 内存加载系统数据");
    }

    public void clear() {
        System.out.println("💾 内存清空数据");
    }
}

/**
 * 子系统 - 硬盘
 */
public class HardDisk {
    public void read() {
        System.out.println("💿 硬盘读取启动程序");
    }

    public void write() {
        System.out.println("💿 硬盘写入系统日志");
    }
}

/**
 * 子系统 - 操作系统
 */
public class OperatingSystem {
    public void bootUp() {
        System.out.println("🖥️ 操作系统启动");
    }

    public void loadDrivers() {
        System.out.println("🖥️ 加载设备驱动程序");
    }

    public void startServices() {
        System.out.println("🖥️ 启动系统服务");
    }

    public void shutdown() {
        System.out.println("🖥️ 操作系统关闭");
    }
}

/**
 * 子系统 - 网络
 */
public class NetworkCard {
    public void connect() {
        System.out.println("🌐 网络连接建立");
    }

    public void disconnect() {
        System.out.println("🌐 网络连接断开");
    }
}

/**
 * 外观类 - 计算机
 */
public class ComputerFacade {
    private CPU cpu;
    private Memory memory;
    private HardDisk hardDisk;
    private OperatingSystem os;
    private NetworkCard networkCard;

    public ComputerFacade() {
        this.cpu = new CPU();
        this.memory = new Memory();
        this.hardDisk = new HardDisk();
        this.os = new OperatingSystem();
        this.networkCard = new NetworkCard();
    }

    /**
     * 启动计算机
     */
    public void startComputer() {
        System.out.println("💻 === 计算机启动中 ===");

        // 硬件自检和启动
        cpu.start();
        memory.load();
        hardDisk.read();

        // 系统启动
        os.bootUp();
        os.loadDrivers();

        // 网络连接
        networkCard.connect();

        // 启动系统服务
        os.startServices();

        cpu.execute();

        System.out.println("✅ 计算机启动完成，可以正常使用");
    }

    /**
     * 关闭计算机
     */
    public void shutdownComputer() {
        System.out.println("💻 === 计算机关闭中 ===");

        // 保存数据
        hardDisk.write();

        // 断开网络
        networkCard.disconnect();

        // 关闭系统
        os.shutdown();

        // 清理内存
        memory.clear();

        // 关闭CPU
        cpu.shutdown();

        System.out.println("✅ 计算机已安全关闭");
    }

    /**
     * 重启计算机
     */
    public void restartComputer() {
        System.out.println("💻 === 计算机重启中 ===");

        shutdownComputer();

        System.out.println("\n⏳ 等待3秒后重新启动...");
        try {
            Thread.sleep(1000); // 模拟等待
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        startComputer();

        System.out.println("✅ 计算机重启完成");
    }

    /**
     * 进入休眠模式
     */
    public void sleepMode() {
        System.out.println("💻 === 进入休眠模式 ===");

        hardDisk.write(); // 保存当前状态
        networkCard.disconnect();
        cpu.shutdown();

        System.out.println("😴 计算机已进入休眠模式");
    }

    /**
     * 从休眠模式唤醒
     */
    public void wakeUp() {
        System.out.println("💻 === 从休眠模式唤醒 ===");

        cpu.start();
        memory.load(); // 恢复内存状态
        networkCard.connect();
        cpu.execute();

        System.out.println("😊 计算机已唤醒，可以继续使用");
    }
}

// 计算机外观模式演示
public class ComputerFacadeDemo {
    public static void main(String[] args) {
        System.out.println("=== 计算机外观模式演示 ===");

        ComputerFacade computer = new ComputerFacade();

        System.out.println("=== 正常启动和关闭 ===");
        computer.startComputer();

        System.out.println("\n--- 使用计算机进行工作 ---");
        System.out.println("📝 正在编写代码...");
        System.out.println("📧 正在收发邮件...");
        System.out.println("🌐 正在浏览网页...");

        System.out.println();
        computer.shutdownComputer();

        System.out.println("\n=== 重启操作 ===");
        computer.restartComputer();

        System.out.println("\n=== 休眠和唤醒 ===");
        computer.sleepMode();

        System.out.println("\n--- 过了一会儿，需要继续工作 ---");
        computer.wakeUp();

        System.out.println("\n--- 工作完成，关闭计算机 ---");
        computer.shutdownComputer();

        System.out.println("\n=== 外观模式的优势 ===");
        System.out.println("🎯 简化了复杂的启动/关闭流程");
        System.out.println("🎯 用户不需要了解硬件详细操作");
        System.out.println("🎯 提供了高级的操作接口（重启、休眠等）");
        System.out.println("🎯 隐藏了子系统间的依赖关系");
    }
}
```

### 3. 在线支付外观模式

```java
/**
 * 子系统 - 账户验证服务
 */
public class AccountVerificationService {
    public boolean verifyAccount(String accountId, String password) {
        System.out.println("🔐 验证账户: " + accountId);
        // 模拟验证过程
        if (accountId.startsWith("user") && password.length() >= 6) {
            System.out.println("✅ 账户验证成功");
            return true;
        } else {
            System.out.println("❌ 账户验证失败");
            return false;
        }
    }

    public boolean checkAccountStatus(String accountId) {
        System.out.println("📊 检查账户状态: " + accountId);
        // 模拟状态检查
        System.out.println("✅ 账户状态正常");
        return true;
    }
}

/**
 * 子系统 - 余额检查服务
 */
public class BalanceService {
    private static final Map<String, Double> balances = new HashMap<>();

    static {
        balances.put("user001", 1500.0);
        balances.put("user002", 800.0);
        balances.put("user003", 2000.0);
    }

    public boolean checkBalance(String accountId, double amount) {
        System.out.println("💰 检查账户余额: " + accountId);
        Double balance = balances.get(accountId);

        if (balance == null) {
            System.out.println("❌ 账户不存在");
            return false;
        }

        System.out.println("当前余额: ¥" + balance + ", 支付金额: ¥" + amount);

        if (balance >= amount) {
            System.out.println("✅ 余额充足");
            return true;
        } else {
            System.out.println("❌ 余额不足");
            return false;
        }
    }

    public void deductBalance(String accountId, double amount) {
        Double balance = balances.get(accountId);
        if (balance != null && balance >= amount) {
            balances.put(accountId, balance - amount);
            System.out.println("💸 扣除金额: ¥" + amount + ", 剩余余额: ¥" + (balance - amount));
        }
    }
}

/**
 * 子系统 - 风控服务
 */
public class RiskControlService {
    public boolean assessRisk(String accountId, double amount, String merchantId) {
        System.out.println("🛡️ 风险评估中...");
        System.out.println("账户: " + accountId + ", 金额: ¥" + amount + ", 商户: " + merchantId);

        // 模拟风险评估规则
        if (amount > 10000) {
            System.out.println("⚠️ 大额交易，需要额外验证");
            return false;
        }

        if (accountId.contains("suspicious")) {
            System.out.println("⚠️ 账户存在风险");
            return false;
        }

        System.out.println("✅ 风险评估通过");
        return true;
    }

    public void recordTransaction(String accountId, double amount, String merchantId) {
        System.out.println("📝 记录交易信息用于风控分析");
    }
}

/**
 * 子系统 - 银行接口服务
 */
public class BankGatewayService {
    public String processPayment(String accountId, double amount, String bankCode) {
        System.out.println("🏦 连接银行网关: " + bankCode);
        System.out.println("处理支付请求: 账户" + accountId + ", 金额¥" + amount);

        // 模拟银行处理
        try {
            Thread.sleep(500); // 模拟网络延迟
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 生成交易流水号
        String transactionId = "TXN" + System.currentTimeMillis();
        System.out.println("✅ 银行处理成功，交易号: " + transactionId);

        return transactionId;
    }

    public boolean confirmTransaction(String transactionId) {
        System.out.println("🏦 确认交易: " + transactionId);
        System.out.println("✅ 交易确认成功");
        return true;
    }
}

/**
 * 子系统 - 通知服务
 */
public class NotificationService {
    public void sendSMS(String phoneNumber, String message) {
        System.out.println("📱 发送短信到 " + phoneNumber + ": " + message);
    }

    public void sendEmail(String email, String subject, String content) {
        System.out.println("📧 发送邮件到 " + email);
        System.out.println("主题: " + subject);
        System.out.println("内容: " + content);
    }

    public void sendPushNotification(String userId, String message) {
        System.out.println("🔔 发送推送通知给用户 " + userId + ": " + message);
    }
}

/**
 * 子系统 - 订单服务
 */
public class OrderService {
    public String createOrder(String userId, String merchantId, double amount, String description) {
        String orderId = "ORDER" + System.currentTimeMillis();
        System.out.println("📦 创建订单: " + orderId);
        System.out.println("用户: " + userId + ", 商户: " + merchantId);
        System.out.println("金额: ¥" + amount + ", 描述: " + description);
        return orderId;
    }

    public void updateOrderStatus(String orderId, String status) {
        System.out.println("📦 更新订单状态: " + orderId + " -> " + status);
    }
}

/**
 * 支付请求对象
 */
public class PaymentRequest {
    private String userId;
    private String password;
    private String merchantId;
    private double amount;
    private String description;
    private String phoneNumber;
    private String email;

    public PaymentRequest(String userId, String password, String merchantId,
                         double amount, String description, String phoneNumber, String email) {
        this.userId = userId;
        this.password = password;
        this.merchantId = merchantId;
        this.amount = amount;
        this.description = description;
        this.phoneNumber = phoneNumber;
        this.email = email;
    }

    // getter方法
    public String getUserId() { return userId; }
    public String getPassword() { return password; }
    public String getMerchantId() { return merchantId; }
    public double getAmount() { return amount; }
    public String getDescription() { return description; }
    public String getPhoneNumber() { return phoneNumber; }
    public String getEmail() { return email; }
}

/**
 * 支付结果对象
 */
public class PaymentResult {
    private boolean success;
    private String transactionId;
    private String orderId;
    private String message;
    private double amount;

    public PaymentResult(boolean success, String transactionId, String orderId,
                        String message, double amount) {
        this.success = success;
        this.transactionId = transactionId;
        this.orderId = orderId;
        this.message = message;
        this.amount = amount;
    }

    @Override
    public String toString() {
        return String.format("PaymentResult{success=%s, transactionId='%s', orderId='%s', message='%s', amount=%.2f}",
                           success, transactionId, orderId, message, amount);
    }

    // getter方法
    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getOrderId() { return orderId; }
    public String getMessage() { return message; }
    public double getAmount() { return amount; }
}

/**
 * 外观类 - 支付系统外观
 */
public class PaymentSystemFacade {
    private AccountVerificationService accountService;
    private BalanceService balanceService;
    private RiskControlService riskService;
    private BankGatewayService bankService;
    private NotificationService notificationService;
    private OrderService orderService;

    public PaymentSystemFacade() {
        this.accountService = new AccountVerificationService();
        this.balanceService = new BalanceService();
        this.riskService = new RiskControlService();
        this.bankService = new BankGatewayService();
        this.notificationService = new NotificationService();
        this.orderService = new OrderService();
    }

    /**
     * 处理支付请求 - 主要外观方法
     */
    public PaymentResult processPayment(PaymentRequest request) {
        System.out.println("💳 === 开始处理支付请求 ===");
        System.out.println("用户: " + request.getUserId() + ", 金额: ¥" + request.getAmount());

        try {
            // 1. 账户验证
            if (!accountService.verifyAccount(request.getUserId(), request.getPassword())) {
                return new PaymentResult(false, null, null, "账户验证失败", 0);
            }

            if (!accountService.checkAccountStatus(request.getUserId())) {
                return new PaymentResult(false, null, null, "账户状态异常", 0);
            }

            // 2. 余额检查
            if (!balanceService.checkBalance(request.getUserId(), request.getAmount())) {
                return new PaymentResult(false, null, null, "余额不足", 0);
            }

            // 3. 风险评估
            if (!riskService.assessRisk(request.getUserId(), request.getAmount(), request.getMerchantId())) {
                return new PaymentResult(false, null, null, "风险评估未通过", 0);
            }

            // 4. 创建订单
            String orderId = orderService.createOrder(request.getUserId(), request.getMerchantId(),
                                                    request.getAmount(), request.getDescription());

            // 5. 银行支付处理
            String transactionId = bankService.processPayment(request.getUserId(),
                                                            request.getAmount(), "ICBC");

            // 6. 扣除余额
            balanceService.deductBalance(request.getUserId(), request.getAmount());

            // 7. 确认交易
            bankService.confirmTransaction(transactionId);

            // 8. 更新订单状态
            orderService.updateOrderStatus(orderId, "PAID");

            // 9. 记录风控信息
            riskService.recordTransaction(request.getUserId(), request.getAmount(), request.getMerchantId());

            // 10. 发送通知
            sendSuccessNotifications(request, transactionId, orderId);

            System.out.println("✅ 支付处理完成");

            return new PaymentResult(true, transactionId, orderId, "支付成功", request.getAmount());

        } catch (Exception e) {
            System.out.println("❌ 支付处理失败: " + e.getMessage());
            return new PaymentResult(false, null, null, "系统错误: " + e.getMessage(), 0);
        }
    }

    /**
     * 查询支付状态
     */
    public PaymentResult queryPaymentStatus(String transactionId) {
        System.out.println("🔍 查询支付状态: " + transactionId);

        boolean confirmed = bankService.confirmTransaction(transactionId);

        if (confirmed) {
            return new PaymentResult(true, transactionId, null, "交易成功", 0);
        } else {
            return new PaymentResult(false, transactionId, null, "交易失败或不存在", 0);
        }
    }

    /**
     * 退款处理
     */
    public PaymentResult processRefund(String transactionId, double refundAmount, String reason) {
        System.out.println("💰 === 处理退款请求 ===");
        System.out.println("交易号: " + transactionId + ", 退款金额: ¥" + refundAmount);

        // 简化的退款流程
        try {
            // 1. 验证原交易
            if (!bankService.confirmTransaction(transactionId)) {
                return new PaymentResult(false, null, null, "原交易不存在", 0);
            }

            // 2. 处理退款
            String refundId = "REFUND" + System.currentTimeMillis();
            System.out.println("🏦 处理退款，退款单号: " + refundId);

            // 3. 发送退款通知
            System.out.println("📧 发送退款通知");

            return new PaymentResult(true, refundId, null, "退款成功", refundAmount);

        } catch (Exception e) {
            return new PaymentResult(false, null, null, "退款失败: " + e.getMessage(), 0);
        }
    }

    /**
     * 发送成功通知
     */
    private void sendSuccessNotifications(PaymentRequest request, String transactionId, String orderId) {
        // 短信通知
        String smsMessage = "您的支付已成功，金额¥" + request.getAmount() + "，交易号" + transactionId;
        notificationService.sendSMS(request.getPhoneNumber(), smsMessage);

        // 邮件通知
        String emailSubject = "支付成功通知";
        String emailContent = "您在商户" + request.getMerchantId() + "的支付已成功完成。\n" +
                             "订单号: " + orderId + "\n" +
                             "交易号: " + transactionId + "\n" +
                             "支付金额: ¥" + request.getAmount();
        notificationService.sendEmail(request.getEmail(), emailSubject, emailContent);

        // 推送通知
        String pushMessage = "支付成功¥" + request.getAmount();
        notificationService.sendPushNotification(request.getUserId(), pushMessage);
    }
}

// 在线支付外观模式演示
public class PaymentSystemFacadeDemo {
    public static void main(String[] args) {
        System.out.println("=== 在线支付系统外观模式演示 ===");

        PaymentSystemFacade paymentSystem = new PaymentSystemFacade();

        System.out.println("\n=== 场景1: 成功支付 ===");
        PaymentRequest request1 = new PaymentRequest(
            "user001", "password123", "merchant_abc", 299.99,
            "购买笔记本电脑", "138****1234", "user001@example.com"
        );

        PaymentResult result1 = paymentSystem.processPayment(request1);
        System.out.println("\n支付结果: " + result1);

        if (result1.isSuccess()) {
            System.out.println("\n--- 查询支付状态 ---");
            PaymentResult queryResult = paymentSystem.queryPaymentStatus(result1.getTransactionId());
            System.out.println("查询结果: " + queryResult);
        }

        System.out.println("\n=== 场景2: 余额不足 ===");
        PaymentRequest request2 = new PaymentRequest(
            "user002", "password456", "merchant_xyz", 999.99,
            "购买相机", "139****5678", "user002@example.com"
        );

        PaymentResult result2 = paymentSystem.processPayment(request2);
        System.out.println("\n支付结果: " + result2);

        System.out.println("\n=== 场景3: 大额交易风控拦截 ===");
        PaymentRequest request3 = new PaymentRequest(
            "user003", "password789", "merchant_big", 15000.0,
            "购买奢侈品", "136****9012", "user003@example.com"
        );

        PaymentResult result3 = paymentSystem.processPayment(request3);
        System.out.println("\n支付结果: " + result3);

        System.out.println("\n=== 场景4: 账户验证失败 ===");
        PaymentRequest request4 = new PaymentRequest(
            "invalid_user", "wrong_password", "merchant_test", 50.0,
            "测试商品", "137****3456", "invalid@example.com"
        );

        PaymentResult result4 = paymentSystem.processPayment(request4);
        System.out.println("\n支付结果: " + result4);

        System.out.println("\n=== 场景5: 退款处理 ===");
        if (result1.isSuccess()) {
            PaymentResult refundResult = paymentSystem.processRefund(
                result1.getTransactionId(), 100.0, "用户申请部分退款"
            );
            System.out.println("退款结果: " + refundResult);
        }

        System.out.println("\n=== 外观模式的价值体现 ===");
        System.out.println("🎯 简化了复杂的支付流程");
        System.out.println("🎯 客户端只需调用一个方法即可完成支付");
        System.out.println("🎯 隐藏了6个子系统的复杂交互");
        System.out.println("🎯 提供了统一的错误处理和异常管理");
        System.out.println("🎯 易于维护和扩展");

        System.out.println("\n如果没有外观模式，客户端需要:");
        System.out.println("❌ 了解并直接调用6个不同的子系统");
        System.out.println("❌ 处理复杂的调用顺序和依赖关系");
        System.out.println("❌ 自己处理各种异常和错误情况");
        System.out.println("❌ 代码重复且容易出错");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **简化接口**
   - 为复杂系统提供简单的接口
   - 降低客户端使用难度

2. **降低耦合**
   - 客户端与子系统解耦
   - 子系统变化不影响客户端

3. **更好的层次结构**
   - 定义系统中每层的入口点
   - 提高子系统的独立性

4. **符合迪米特法则**
   - 减少客户端与子系统的直接交互
   - 最少知识原则

### ❌ 缺点

1. **不符合开闭原则**
   - 增加新的子系统可能需要修改外观类
   - 外观类可能变得过于复杂

2. **过度封装**
   - 可能隐藏了客户端需要的细节
   - 降低了系统的灵活性

3. **单点故障风险**
   - 外观类成为系统瓶颈
   - 外观类出错影响整个系统

## 🎯 使用场景总结

### 适合使用外观模式的场景：
- 🏠 **复杂子系统整合** - 多个相关子系统的统一访问
- 🔧 **第三方库封装** - 简化复杂API的使用
- 🏢 **分层架构** - 为每层提供清晰的入口点
- 📚 **遗留系统包装** - 为老系统提供现代化接口
- 🌐 **微服务聚合** - 将多个微服务组合为单一接口

### 不适合使用外观模式的场景：
- 子系统简单，不需要额外抽象
- 客户端需要细粒度控制子系统
- 系统设计已经很简洁
- 过度设计的风险

## 🧠 记忆技巧

### 形象比喻
> **外观模式就像是 "酒店前台"**：
> - 客人不需要直接联系保洁、维修、餐饮等部门
> - 前台统一处理各种需求
> - 前台知道如何协调各个部门
> - 客人享受简单统一的服务体验

### 设计要点
> **"一个入口，多个出口，统一协调，简化使用"**

### 与适配器模式的区别
- **外观模式**：简化复杂接口，定义新的上层接口
- **适配器模式**：让不兼容的接口能够协同工作

## 🔧 最佳实践

### 1. 分层外观设计

```java
/**
 * 多层外观设计
 */
public class ApplicationFacade {
    private BusinessFacade businessFacade;
    private SecurityFacade securityFacade;

    public ApplicationFacade() {
        this.businessFacade = new BusinessFacade();
        this.securityFacade = new SecurityFacade();
    }

    public void processUserRequest(UserRequest request) {
        // 先安全检查
        if (securityFacade.validateAndAuthorize(request)) {
            // 再处理业务
            businessFacade.handleBusinessLogic(request);
        }
    }
}
```

### 2. 配置化外观

```java
/**
 * 可配置的外观类
 */
public class ConfigurableFacade {
    private Properties config;
    private Map<String, Object> services;

    public ConfigurableFacade(Properties config) {
        this.config = config;
        this.services = new HashMap<>();
        initializeServices();
    }

    private void initializeServices() {
        // 根据配置初始化不同的子系统
        if (config.getProperty("enable.cache", "false").equals("true")) {
            services.put("cache", new CacheService());
        }
        // 更多配置化初始化...
    }
}
```

### 3. 异步外观模式

```java
/**
 * 异步外观模式
 */
public class AsyncPaymentFacade {
    private ExecutorService executor = Executors.newFixedThreadPool(10);

    public CompletableFuture<PaymentResult> processPaymentAsync(PaymentRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            // 异步执行复杂的支付流程
            return processPaymentInternal(request);
        }, executor);
    }

    private PaymentResult processPaymentInternal(PaymentRequest request) {
        // 具体的支付处理逻辑
        return new PaymentResult(true, "TXN123", "ORDER123", "成功", request.getAmount());
    }
}
```

### 4. 外观工厂模式

```java
/**
 * 外观工厂
 */
public class FacadeFactory {
    public static PaymentSystemFacade createPaymentFacade(String environment) {
        switch (environment.toLowerCase()) {
            case "test":
                return new TestPaymentSystemFacade();
            case "prod":
                return new ProductionPaymentSystemFacade();
            default:
                return new PaymentSystemFacade();
        }
    }
}
```

## 🚀 总结

外观模式通过提供统一的简化接口来隐藏复杂子系统的细节，特别适用于：

- **复杂子系统的简化访问**
- **系统集成和整合**
- **API的高层封装**

核心思想：
- **简化复杂性**
- **统一访问入口**
- **降低系统耦合**

设计要点：
- **合理的抽象层次**
- **明确的职责边界**
- **适度的封装粒度**

记住，**外观模式是简化器，不是万能包装器**，要在合适的复杂系统简化场景下使用！

---
*下一篇：享元模式 - 高效共享相似对象*