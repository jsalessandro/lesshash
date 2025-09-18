---
title: "设计模式详解07：桥接模式(Bridge) - 抽象与实现的分离艺术"
date: 2024-12-07T10:07:00+08:00
draft: false
tags: ["设计模式", "桥接模式", "Bridge", "Java", "结构型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解桥接模式，从基础概念到高级实现，包含抽象层次分离、实现独立变化等实战技巧，让你彻底掌握解耦的艺术"
---

## 🎯 什么是桥接模式？

### 生活中的例子
想象一下，你有一台电视机和一个遥控器。电视机有很多品牌（索尼、三星、LG），遥控器也有很多类型（基础版、高级版、语音版）。如果每个品牌的电视都要配一套不同类型的遥控器，那就需要 3×3=9 种组合。但如果使用**红外线标准协议**作为桥梁，任何遥控器都能控制任何品牌的电视。这就是桥接模式的核心思想：**将抽象与实现分离，使它们可以独立变化**。

### 问题背景
在软件开发中，经常遇到多维度变化的情况：
- 🖥️ **图形系统**：形状（圆形、方形）× 渲染器（OpenGL、DirectX）
- 📱 **消息系统**：消息类型（文本、图片）× 发送方式（邮件、短信、微信）
- 🎮 **游戏角色**：角色类型（战士、法师）× 武器类型（剑、法杖）
- 💾 **数据访问**：业务对象（用户、订单）× 存储方式（MySQL、Redis）

如果使用继承来解决，会导致：
- 类爆炸问题（组合爆炸）
- 扩展困难
- 违反单一职责原则

## 🧠 设计思想

### 核心角色
1. **Abstraction（抽象层）** - 定义抽象接口
2. **RefinedAbstraction（精化抽象层）** - 扩展抽象层
3. **Implementor（实现接口）** - 定义实现接口
4. **ConcreteImplementor（具体实现）** - 具体实现类

### 核心思想
- 将抽象部分与实现部分分离
- 通过组合代替继承
- 两个层次可以独立变化

### 记忆口诀
> **"抽象实现分两边，桥梁连接各自变"**

## 💻 代码实现

### 1. 基础桥接模式

```java
/**
 * 实现接口 - 绘图API接口
 */
public interface DrawingAPI {
    void drawCircle(double x, double y, double radius);
    void drawRectangle(double x, double y, double width, double height);
}

/**
 * 具体实现 - OpenGL绘图API
 */
public class OpenGLDrawingAPI implements DrawingAPI {
    @Override
    public void drawCircle(double x, double y, double radius) {
        System.out.printf("[OpenGL] 绘制圆形: 中心(%.1f, %.1f), 半径%.1f%n", x, y, radius);
    }

    @Override
    public void drawRectangle(double x, double y, double width, double height) {
        System.out.printf("[OpenGL] 绘制矩形: 起点(%.1f, %.1f), 宽%.1f, 高%.1f%n", x, y, width, height);
    }
}

/**
 * 具体实现 - DirectX绘图API
 */
public class DirectXDrawingAPI implements DrawingAPI {
    @Override
    public void drawCircle(double x, double y, double radius) {
        System.out.printf("[DirectX] 绘制圆形: 中心(%.1f, %.1f), 半径%.1f%n", x, y, radius);
    }

    @Override
    public void drawRectangle(double x, double y, double width, double height) {
        System.out.printf("[DirectX] 绘制矩形: 起点(%.1f, %.1f), 宽%.1f, 高%.1f%n", x, y, width, height);
    }
}

/**
 * 抽象层 - 形状抽象类
 */
public abstract class Shape {
    protected DrawingAPI drawingAPI; // 桥接：持有实现接口的引用

    protected Shape(DrawingAPI drawingAPI) {
        this.drawingAPI = drawingAPI;
    }

    public abstract void draw();
    public abstract void resize(double factor);

    // 可以在抽象层定义一些通用方法
    public void changeDrawingAPI(DrawingAPI newAPI) {
        this.drawingAPI = newAPI;
        System.out.println("更换绘图API");
    }
}

/**
 * 精化抽象层 - 圆形
 */
public class Circle extends Shape {
    private double x, y, radius;

    public Circle(double x, double y, double radius, DrawingAPI drawingAPI) {
        super(drawingAPI);
        this.x = x;
        this.y = y;
        this.radius = radius;
    }

    @Override
    public void draw() {
        drawingAPI.drawCircle(x, y, radius);
    }

    @Override
    public void resize(double factor) {
        radius *= factor;
        System.out.printf("圆形大小调整为原来的%.1f倍%n", factor);
    }

    // 圆形特有的方法
    public void setRadius(double radius) {
        this.radius = radius;
    }

    public double getRadius() {
        return radius;
    }
}

/**
 * 精化抽象层 - 矩形
 */
public class Rectangle extends Shape {
    private double x, y, width, height;

    public Rectangle(double x, double y, double width, double height, DrawingAPI drawingAPI) {
        super(drawingAPI);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    @Override
    public void draw() {
        drawingAPI.drawRectangle(x, y, width, height);
    }

    @Override
    public void resize(double factor) {
        width *= factor;
        height *= factor;
        System.out.printf("矩形大小调整为原来的%.1f倍%n", factor);
    }

    // 矩形特有的方法
    public void setDimensions(double width, double height) {
        this.width = width;
        this.height = height;
    }

    public double getArea() {
        return width * height;
    }
}

// 基础桥接模式演示
public class BasicBridgeDemo {
    public static void main(String[] args) {
        System.out.println("=== 桥接模式基础演示 ===");

        // 创建不同的绘图API
        DrawingAPI openGL = new OpenGLDrawingAPI();
        DrawingAPI directX = new DirectXDrawingAPI();

        System.out.println("\n=== 使用OpenGL绘制形状 ===");
        Circle circle1 = new Circle(5, 5, 10, openGL);
        Rectangle rect1 = new Rectangle(0, 0, 20, 15, openGL);

        circle1.draw();
        rect1.draw();

        System.out.println("\n=== 使用DirectX绘制形状 ===");
        Circle circle2 = new Circle(3, 3, 8, directX);
        Rectangle rect2 = new Rectangle(2, 2, 25, 18, directX);

        circle2.draw();
        rect2.draw();

        System.out.println("\n=== 运行时更换绘图API ===");
        circle1.changeDrawingAPI(directX);
        circle1.draw();

        rect1.changeDrawingAPI(directX);
        rect1.draw();

        System.out.println("\n=== 调整形状大小 ===");
        circle1.resize(1.5);
        circle1.draw();

        rect1.resize(0.8);
        rect1.draw();

        System.out.println("\n观察：形状(抽象)和绘图API(实现)可以独立变化！");
    }
}
```

### 2. 消息发送系统桥接

```java
/**
 * 实现接口 - 消息发送方式
 */
public interface MessageSender {
    void sendMessage(String recipient, String content);
    boolean isAvailable();
    String getSenderType();
}

/**
 * 具体实现 - 邮件发送
 */
public class EmailSender implements MessageSender {
    @Override
    public void sendMessage(String recipient, String content) {
        System.out.println("📧 发送邮件");
        System.out.println("  收件人: " + recipient);
        System.out.println("  内容: " + content);
        System.out.println("  状态: 邮件发送成功");
    }

    @Override
    public boolean isAvailable() {
        // 模拟检查邮件服务是否可用
        return true;
    }

    @Override
    public String getSenderType() {
        return "Email";
    }
}

/**
 * 具体实现 - 短信发送
 */
public class SMSSender implements MessageSender {
    @Override
    public void sendMessage(String recipient, String content) {
        System.out.println("📱 发送短信");
        System.out.println("  手机号: " + recipient);
        System.out.println("  内容: " + content);
        System.out.println("  状态: 短信发送成功");
    }

    @Override
    public boolean isAvailable() {
        // 模拟检查短信服务是否可用
        return true;
    }

    @Override
    public String getSenderType() {
        return "SMS";
    }
}

/**
 * 具体实现 - 微信发送
 */
public class WeChatSender implements MessageSender {
    @Override
    public void sendMessage(String recipient, String content) {
        System.out.println("💬 发送微信消息");
        System.out.println("  微信号: " + recipient);
        System.out.println("  内容: " + content);
        System.out.println("  状态: 微信消息发送成功");
    }

    @Override
    public boolean isAvailable() {
        // 模拟检查微信服务是否可用
        return Math.random() > 0.1; // 90%可用
    }

    @Override
    public String getSenderType() {
        return "WeChat";
    }
}

/**
 * 抽象层 - 消息抽象类
 */
public abstract class Message {
    protected MessageSender messageSender; // 桥接：持有发送方式的引用
    protected String recipient;
    protected String content;

    protected Message(MessageSender messageSender) {
        this.messageSender = messageSender;
    }

    public abstract void send();

    // 通用方法
    public void setRecipient(String recipient) {
        this.recipient = recipient;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public void changeSender(MessageSender newSender) {
        this.messageSender = newSender;
        System.out.println("切换发送方式为: " + newSender.getSenderType());
    }

    protected boolean checkSenderAvailability() {
        if (!messageSender.isAvailable()) {
            System.out.println("❌ " + messageSender.getSenderType() + " 服务当前不可用");
            return false;
        }
        return true;
    }
}

/**
 * 精化抽象层 - 普通消息
 */
public class SimpleMessage extends Message {
    public SimpleMessage(MessageSender messageSender) {
        super(messageSender);
    }

    public SimpleMessage(MessageSender messageSender, String recipient, String content) {
        super(messageSender);
        this.recipient = recipient;
        this.content = content;
    }

    @Override
    public void send() {
        if (checkSenderAvailability()) {
            System.out.println("\n--- 发送普通消息 ---");
            messageSender.sendMessage(recipient, content);
        }
    }
}

/**
 * 精化抽象层 - 加密消息
 */
public class EncryptedMessage extends Message {
    public EncryptedMessage(MessageSender messageSender) {
        super(messageSender);
    }

    public EncryptedMessage(MessageSender messageSender, String recipient, String content) {
        super(messageSender);
        this.recipient = recipient;
        this.content = content;
    }

    @Override
    public void send() {
        if (checkSenderAvailability()) {
            System.out.println("\n--- 发送加密消息 ---");
            String encryptedContent = encrypt(content);
            messageSender.sendMessage(recipient, encryptedContent);
        }
    }

    private String encrypt(String content) {
        // 简单的加密模拟
        String encrypted = "[加密]" + content + "[/加密]";
        System.out.println("  🔒 消息已加密");
        return encrypted;
    }
}

/**
 * 精化抽象层 - 群发消息
 */
public class BroadcastMessage extends Message {
    private List<String> recipients;

    public BroadcastMessage(MessageSender messageSender) {
        super(messageSender);
        this.recipients = new ArrayList<>();
    }

    public BroadcastMessage(MessageSender messageSender, List<String> recipients, String content) {
        super(messageSender);
        this.recipients = recipients;
        this.content = content;
    }

    public void addRecipient(String recipient) {
        recipients.add(recipient);
    }

    public void setRecipients(List<String> recipients) {
        this.recipients = recipients;
    }

    @Override
    public void send() {
        if (checkSenderAvailability()) {
            System.out.println("\n--- 群发消息 ---");
            System.out.println("群发对象数量: " + recipients.size());
            for (String recipient : recipients) {
                messageSender.sendMessage(recipient, content);
                System.out.println("  ✓ 已发送给: " + recipient);
            }
        }
    }
}

// 消息发送系统演示
public class MessageBridgeDemo {
    public static void main(String[] args) {
        System.out.println("=== 消息发送系统桥接演示 ===");

        // 创建不同的发送方式
        MessageSender emailSender = new EmailSender();
        MessageSender smsSender = new SMSSender();
        MessageSender wechatSender = new WeChatSender();

        System.out.println("\n=== 不同类型消息使用不同发送方式 ===");

        // 普通消息通过邮件发送
        SimpleMessage simpleEmail = new SimpleMessage(emailSender, "user@example.com", "会议通知：明天下午2点开会");
        simpleEmail.send();

        // 加密消息通过微信发送
        EncryptedMessage encryptedWeChat = new EncryptedMessage(wechatSender, "friend123", "这是机密信息");
        encryptedWeChat.send();

        // 群发消息通过短信发送
        BroadcastMessage broadcastSMS = new BroadcastMessage(smsSender);
        broadcastSMS.setContent("系统维护通知：今晚10点系统维护，请提前保存工作");
        broadcastSMS.addRecipient("138****1234");
        broadcastSMS.addRecipient("139****5678");
        broadcastSMS.addRecipient("136****9012");
        broadcastSMS.send();

        System.out.println("\n=== 运行时切换发送方式 ===");
        System.out.println("微信服务不可用时，自动切换到邮件发送：");

        // 尝试用微信发送普通消息，如果失败则切换到邮件
        SimpleMessage flexibleMessage = new SimpleMessage(wechatSender, "user123", "重要通知");
        flexibleMessage.send();

        // 如果微信不可用，切换到邮件
        if (!wechatSender.isAvailable()) {
            flexibleMessage.changeSender(emailSender);
            flexibleMessage.setRecipient("user@example.com");
            flexibleMessage.send();
        }

        System.out.println("\n=== 同一消息内容，不同发送方式 ===");
        String content = "产品发布会邀请函";
        String recipient = "重要客户";

        SimpleMessage emailNotification = new SimpleMessage(emailSender, recipient + "@company.com", content);
        SimpleMessage smsNotification = new SimpleMessage(smsSender, "138****0000", content);
        SimpleMessage wechatNotification = new SimpleMessage(wechatSender, recipient + "_wechat", content);

        emailNotification.send();
        smsNotification.send();
        wechatNotification.send();

        System.out.println("\n观察：消息类型(抽象)和发送方式(实现)可以独立组合！");
    }
}
```

### 3. 设备控制系统桥接

```java
/**
 * 实现接口 - 设备控制接口
 */
public interface DeviceController {
    void powerOn();
    void powerOff();
    void setVolume(int volume);
    void changeChannel(int channel);
    String getDeviceType();
    boolean isConnected();
}

/**
 * 具体实现 - 电视控制器
 */
public class TVController implements DeviceController {
    private boolean isOn = false;
    private int volume = 50;
    private int channel = 1;

    @Override
    public void powerOn() {
        isOn = true;
        System.out.println("📺 电视已开机");
    }

    @Override
    public void powerOff() {
        isOn = false;
        System.out.println("📺 电视已关机");
    }

    @Override
    public void setVolume(int volume) {
        if (isOn) {
            this.volume = Math.max(0, Math.min(100, volume));
            System.out.println("📺 电视音量设置为: " + this.volume);
        } else {
            System.out.println("📺 电视未开机，无法调节音量");
        }
    }

    @Override
    public void changeChannel(int channel) {
        if (isOn) {
            this.channel = Math.max(1, channel);
            System.out.println("📺 电视频道切换到: " + this.channel);
        } else {
            System.out.println("📺 电视未开机，无法切换频道");
        }
    }

    @Override
    public String getDeviceType() {
        return "Television";
    }

    @Override
    public boolean isConnected() {
        return true; // 模拟连接状态
    }
}

/**
 * 具体实现 - 音响控制器
 */
public class StereoController implements DeviceController {
    private boolean isOn = false;
    private int volume = 30;
    private int station = 1; // 电台

    @Override
    public void powerOn() {
        isOn = true;
        System.out.println("🔊 音响已开机");
    }

    @Override
    public void powerOff() {
        isOn = false;
        System.out.println("🔊 音响已关机");
    }

    @Override
    public void setVolume(int volume) {
        if (isOn) {
            this.volume = Math.max(0, Math.min(100, volume));
            System.out.println("🔊 音响音量设置为: " + this.volume);
        } else {
            System.out.println("🔊 音响未开机，无法调节音量");
        }
    }

    @Override
    public void changeChannel(int channel) {
        if (isOn) {
            this.station = Math.max(1, channel);
            System.out.println("🔊 音响电台切换到: FM " + this.station);
        } else {
            System.out.println("🔊 音响未开机，无法切换电台");
        }
    }

    @Override
    public String getDeviceType() {
        return "Stereo";
    }

    @Override
    public boolean isConnected() {
        return Math.random() > 0.1; // 90%连接成功率
    }
}

/**
 * 具体实现 - 投影仪控制器
 */
public class ProjectorController implements DeviceController {
    private boolean isOn = false;
    private int brightness = 70; // 亮度代替音量
    private int inputSource = 1; // 输入源代替频道

    @Override
    public void powerOn() {
        isOn = true;
        System.out.println("📽️ 投影仪已开机，正在预热...");
    }

    @Override
    public void powerOff() {
        isOn = false;
        System.out.println("📽️ 投影仪已关机，正在冷却...");
    }

    @Override
    public void setVolume(int volume) {
        if (isOn) {
            this.brightness = Math.max(10, Math.min(100, volume));
            System.out.println("📽️ 投影仪亮度设置为: " + this.brightness + "%");
        } else {
            System.out.println("📽️ 投影仪未开机，无法调节亮度");
        }
    }

    @Override
    public void changeChannel(int channel) {
        if (isOn) {
            this.inputSource = Math.max(1, Math.min(4, channel));
            String[] sources = {"", "HDMI1", "HDMI2", "VGA", "USB"};
            System.out.println("📽️ 投影仪输入源切换到: " + sources[this.inputSource]);
        } else {
            System.out.println("📽️ 投影仪未开机，无法切换输入源");
        }
    }

    @Override
    public String getDeviceType() {
        return "Projector";
    }

    @Override
    public boolean isConnected() {
        return true;
    }
}

/**
 * 抽象层 - 遥控器抽象类
 */
public abstract class RemoteControl {
    protected DeviceController device; // 桥接：持有设备控制器的引用

    protected RemoteControl(DeviceController device) {
        this.device = device;
    }

    public abstract void power();
    public abstract void volumeUp();
    public abstract void volumeDown();
    public abstract void channelUp();
    public abstract void channelDown();

    // 通用方法
    public void setDevice(DeviceController device) {
        this.device = device;
        System.out.println("遥控器已连接到: " + device.getDeviceType());
    }

    protected boolean checkConnection() {
        if (!device.isConnected()) {
            System.out.println("❌ 设备连接失败，请检查连接");
            return false;
        }
        return true;
    }
}

/**
 * 精化抽象层 - 基础遥控器
 */
public class BasicRemote extends RemoteControl {
    private boolean deviceOn = false;

    public BasicRemote(DeviceController device) {
        super(device);
    }

    @Override
    public void power() {
        if (checkConnection()) {
            if (deviceOn) {
                device.powerOff();
                deviceOn = false;
            } else {
                device.powerOn();
                deviceOn = true;
            }
        }
    }

    @Override
    public void volumeUp() {
        if (checkConnection() && deviceOn) {
            device.setVolume(getCurrentVolume() + 10);
        }
    }

    @Override
    public void volumeDown() {
        if (checkConnection() && deviceOn) {
            device.setVolume(getCurrentVolume() - 10);
        }
    }

    @Override
    public void channelUp() {
        if (checkConnection() && deviceOn) {
            device.changeChannel(getCurrentChannel() + 1);
        }
    }

    @Override
    public void channelDown() {
        if (checkConnection() && deviceOn) {
            device.changeChannel(getCurrentChannel() - 1);
        }
    }

    // 模拟获取当前状态
    private int getCurrentVolume() {
        return 50; // 简化实现
    }

    private int getCurrentChannel() {
        return 5; // 简化实现
    }
}

/**
 * 精化抽象层 - 高级遥控器
 */
public class AdvancedRemote extends BasicRemote {
    public AdvancedRemote(DeviceController device) {
        super(device);
    }

    // 高级功能：设置具体音量
    public void setVolume(int volume) {
        if (checkConnection()) {
            System.out.println("🎛️ 使用高级遥控器精确调节");
            device.setVolume(volume);
        }
    }

    // 高级功能：直接跳转到指定频道
    public void goToChannel(int channel) {
        if (checkConnection()) {
            System.out.println("🎛️ 使用高级遥控器直接跳转");
            device.changeChannel(channel);
        }
    }

    // 高级功能：静音功能
    public void mute() {
        if (checkConnection()) {
            System.out.println("🔇 静音模式");
            device.setVolume(0);
        }
    }

    // 高级功能：收藏频道
    public void goToFavoriteChannel() {
        if (checkConnection()) {
            System.out.println("⭐ 跳转到收藏频道");
            device.changeChannel(8); // 假设8是收藏频道
        }
    }
}

/**
 * 精化抽象层 - 智能语音遥控器
 */
public class VoiceRemote extends AdvancedRemote {
    public VoiceRemote(DeviceController device) {
        super(device);
    }

    // 语音控制功能
    public void voiceCommand(String command) {
        if (!checkConnection()) return;

        System.out.println("🎤 语音识别: \"" + command + "\"");

        command = command.toLowerCase();

        if (command.contains("开机") || command.contains("打开")) {
            device.powerOn();
        } else if (command.contains("关机") || command.contains("关闭")) {
            device.powerOff();
        } else if (command.contains("音量") && command.contains("大")) {
            volumeUp();
        } else if (command.contains("音量") && command.contains("小")) {
            volumeDown();
        } else if (command.contains("频道") || command.contains("台")) {
            // 简单的频道解析
            try {
                String[] words = command.split(" ");
                for (String word : words) {
                    if (word.matches("\\d+")) {
                        int channel = Integer.parseInt(word);
                        goToChannel(channel);
                        return;
                    }
                }
                channelUp(); // 默认下一个频道
            } catch (NumberFormatException e) {
                channelUp();
            }
        } else if (command.contains("静音")) {
            mute();
        } else {
            System.out.println("❓ 语音命令无法识别");
        }
    }
}

// 设备控制系统演示
public class DeviceBridgeDemo {
    public static void main(String[] args) {
        System.out.println("=== 设备控制系统桥接演示 ===");

        // 创建不同的设备控制器
        DeviceController tv = new TVController();
        DeviceController stereo = new StereoController();
        DeviceController projector = new ProjectorController();

        System.out.println("\n=== 基础遥控器控制不同设备 ===");

        BasicRemote basicRemote = new BasicRemote(tv);
        basicRemote.power();
        basicRemote.volumeUp();
        basicRemote.channelUp();

        // 切换到音响
        basicRemote.setDevice(stereo);
        basicRemote.power();
        basicRemote.volumeDown();
        basicRemote.channelDown();

        System.out.println("\n=== 高级遥控器的精确控制 ===");

        AdvancedRemote advancedRemote = new AdvancedRemote(projector);
        advancedRemote.power();
        advancedRemote.setVolume(80); // 设置亮度为80%
        advancedRemote.goToChannel(3); // 切换到VGA输入
        advancedRemote.goToFavoriteChannel();

        // 切换到电视
        advancedRemote.setDevice(tv);
        advancedRemote.power();
        advancedRemote.setVolume(65);
        advancedRemote.mute();

        System.out.println("\n=== 智能语音遥控器 ===");

        VoiceRemote voiceRemote = new VoiceRemote(tv);
        voiceRemote.voiceCommand("打开电视");
        voiceRemote.voiceCommand("音量调大");
        voiceRemote.voiceCommand("切换到 15 频道");
        voiceRemote.voiceCommand("静音");

        // 切换到音响
        voiceRemote.setDevice(stereo);
        voiceRemote.voiceCommand("开机");
        voiceRemote.voiceCommand("音量调小");
        voiceRemote.voiceCommand("换台");

        System.out.println("\n=== 万能遥控器测试 ===");
        System.out.println("同一个高级遥控器控制所有设备:");

        DeviceController[] devices = {tv, stereo, projector};
        String[] deviceNames = {"电视", "音响", "投影仪"};

        for (int i = 0; i < devices.length; i++) {
            System.out.println("\n--- 控制" + deviceNames[i] + " ---");
            advancedRemote.setDevice(devices[i]);
            advancedRemote.power();
            advancedRemote.setVolume(60);
            advancedRemote.goToChannel(2);
            advancedRemote.power(); // 关机
        }

        System.out.println("\n观察：遥控器类型(抽象)和设备类型(实现)可以自由组合！");
    }
}
```

## 🌟 实际应用场景

### 1. 数据持久化桥接

```java
/**
 * 实现接口 - 数据存储接口
 */
public interface DataStorage {
    void save(String key, Object data);
    Object load(String key);
    void delete(String key);
    boolean exists(String key);
    String getStorageType();
}

/**
 * 具体实现 - MySQL存储
 */
public class MySQLStorage implements DataStorage {
    private Map<String, Object> database = new HashMap<>(); // 模拟数据库

    @Override
    public void save(String key, Object data) {
        database.put(key, data);
        System.out.println("💾 [MySQL] 保存数据: " + key + " -> " + data);
    }

    @Override
    public Object load(String key) {
        Object data = database.get(key);
        System.out.println("💾 [MySQL] 加载数据: " + key + " -> " + data);
        return data;
    }

    @Override
    public void delete(String key) {
        database.remove(key);
        System.out.println("💾 [MySQL] 删除数据: " + key);
    }

    @Override
    public boolean exists(String key) {
        return database.containsKey(key);
    }

    @Override
    public String getStorageType() {
        return "MySQL";
    }
}

/**
 * 具体实现 - Redis存储
 */
public class RedisStorage implements DataStorage {
    private Map<String, Object> cache = new HashMap<>(); // 模拟Redis缓存

    @Override
    public void save(String key, Object data) {
        cache.put(key, data);
        System.out.println("⚡ [Redis] 缓存数据: " + key + " -> " + data);
    }

    @Override
    public Object load(String key) {
        Object data = cache.get(key);
        System.out.println("⚡ [Redis] 读取缓存: " + key + " -> " + data);
        return data;
    }

    @Override
    public void delete(String key) {
        cache.remove(key);
        System.out.println("⚡ [Redis] 删除缓存: " + key);
    }

    @Override
    public boolean exists(String key) {
        return cache.containsKey(key);
    }

    @Override
    public String getStorageType() {
        return "Redis";
    }
}

/**
 * 具体实现 - 文件存储
 */
public class FileStorage implements DataStorage {
    private Map<String, Object> files = new HashMap<>(); // 模拟文件系统

    @Override
    public void save(String key, Object data) {
        files.put(key, data);
        System.out.println("📁 [File] 保存文件: " + key + ".dat -> " + data);
    }

    @Override
    public Object load(String key) {
        Object data = files.get(key);
        System.out.println("📁 [File] 读取文件: " + key + ".dat -> " + data);
        return data;
    }

    @Override
    public void delete(String key) {
        files.remove(key);
        System.out.println("📁 [File] 删除文件: " + key + ".dat");
    }

    @Override
    public boolean exists(String key) {
        return files.containsKey(key);
    }

    @Override
    public String getStorageType() {
        return "File";
    }
}

/**
 * 抽象层 - 数据访问对象抽象类
 */
public abstract class DataAccessObject {
    protected DataStorage storage; // 桥接：持有存储方式的引用

    protected DataAccessObject(DataStorage storage) {
        this.storage = storage;
    }

    public abstract void create(Object entity);
    public abstract Object read(String id);
    public abstract void update(String id, Object entity);
    public abstract void delete(String id);

    // 通用方法
    public void changeStorage(DataStorage newStorage) {
        this.storage = newStorage;
        System.out.println("切换存储方式为: " + newStorage.getStorageType());
    }

    protected String generateKey(String prefix, String id) {
        return prefix + ":" + id;
    }
}

/**
 * 精化抽象层 - 用户数据访问对象
 */
public class UserDAO extends DataAccessObject {
    private static final String PREFIX = "user";

    public UserDAO(DataStorage storage) {
        super(storage);
    }

    @Override
    public void create(Object entity) {
        User user = (User) entity;
        String key = generateKey(PREFIX, user.getId());
        storage.save(key, user);
        System.out.println("✅ 用户创建成功: " + user.getName());
    }

    @Override
    public Object read(String id) {
        String key = generateKey(PREFIX, id);
        User user = (User) storage.load(key);
        if (user != null) {
            System.out.println("👤 用户信息: " + user);
        } else {
            System.out.println("❌ 用户不存在: " + id);
        }
        return user;
    }

    @Override
    public void update(String id, Object entity) {
        String key = generateKey(PREFIX, id);
        if (storage.exists(key)) {
            storage.save(key, entity);
            System.out.println("✅ 用户信息更新成功");
        } else {
            System.out.println("❌ 用户不存在，无法更新: " + id);
        }
    }

    @Override
    public void delete(String id) {
        String key = generateKey(PREFIX, id);
        if (storage.exists(key)) {
            storage.delete(key);
            System.out.println("✅ 用户删除成功: " + id);
        } else {
            System.out.println("❌ 用户不存在，无法删除: " + id);
        }
    }

    // 用户特有的方法
    public User findByEmail(String email) {
        // 简化实现：在实际应用中需要索引支持
        System.out.println("🔍 根据邮箱查找用户: " + email);
        return new User("user001", "张三", email); // 模拟查找结果
    }
}

/**
 * 精化抽象层 - 订单数据访问对象
 */
public class OrderDAO extends DataAccessObject {
    private static final String PREFIX = "order";

    public OrderDAO(DataStorage storage) {
        super(storage);
    }

    @Override
    public void create(Object entity) {
        Order order = (Order) entity;
        String key = generateKey(PREFIX, order.getId());
        storage.save(key, order);
        System.out.println("📦 订单创建成功: " + order.getId());
    }

    @Override
    public Object read(String id) {
        String key = generateKey(PREFIX, id);
        Order order = (Order) storage.load(key);
        if (order != null) {
            System.out.println("📋 订单信息: " + order);
        } else {
            System.out.println("❌ 订单不存在: " + id);
        }
        return order;
    }

    @Override
    public void update(String id, Object entity) {
        String key = generateKey(PREFIX, id);
        if (storage.exists(key)) {
            storage.save(key, entity);
            System.out.println("✅ 订单更新成功");
        } else {
            System.out.println("❌ 订单不存在，无法更新: " + id);
        }
    }

    @Override
    public void delete(String id) {
        String key = generateKey(PREFIX, id);
        if (storage.exists(key)) {
            storage.delete(key);
            System.out.println("✅ 订单删除成功: " + id);
        } else {
            System.out.println("❌ 订单不存在，无法删除: " + id);
        }
    }

    // 订单特有的方法
    public List<Order> findByUserId(String userId) {
        System.out.println("🔍 查找用户的所有订单: " + userId);
        // 简化实现：返回模拟数据
        return Arrays.asList(
            new Order("order001", userId, "商品A", 99.99),
            new Order("order002", userId, "商品B", 199.99)
        );
    }
}

/**
 * 用户实体类
 */
public class User {
    private String id;
    private String name;
    private String email;

    public User(String id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    @Override
    public String toString() {
        return String.format("User{id='%s', name='%s', email='%s'}", id, name, email);
    }

    // getter方法
    public String getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
}

/**
 * 订单实体类
 */
public class Order {
    private String id;
    private String userId;
    private String product;
    private double amount;

    public Order(String id, String userId, String product, double amount) {
        this.id = id;
        this.userId = userId;
        this.product = product;
        this.amount = amount;
    }

    @Override
    public String toString() {
        return String.format("Order{id='%s', userId='%s', product='%s', amount=%.2f}",
                           id, userId, product, amount);
    }

    // getter方法
    public String getId() { return id; }
    public String getUserId() { return userId; }
    public String getProduct() { return product; }
    public double getAmount() { return amount; }
}

// 数据持久化桥接演示
public class DataPersistenceBridgeDemo {
    public static void main(String[] args) {
        System.out.println("=== 数据持久化桥接演示 ===");

        // 创建不同的存储方式
        DataStorage mysqlStorage = new MySQLStorage();
        DataStorage redisStorage = new RedisStorage();
        DataStorage fileStorage = new FileStorage();

        System.out.println("\n=== 用户数据操作 ===");

        // 用户数据使用MySQL存储
        UserDAO userDAO = new UserDAO(mysqlStorage);
        User newUser = new User("user001", "张三", "zhangsan@example.com");

        userDAO.create(newUser);
        userDAO.read("user001");
        userDAO.findByEmail("zhangsan@example.com");

        // 更新用户信息
        User updatedUser = new User("user001", "张三丰", "zhangsan@example.com");
        userDAO.update("user001", updatedUser);
        userDAO.read("user001");

        System.out.println("\n=== 切换存储方式 ===");

        // 将用户数据改为Redis存储（缓存优化）
        userDAO.changeStorage(redisStorage);
        userDAO.create(newUser); // 重新在Redis中创建
        userDAO.read("user001");

        System.out.println("\n=== 订单数据操作 ===");

        // 订单数据使用文件存储
        OrderDAO orderDAO = new OrderDAO(fileStorage);
        Order newOrder = new Order("order001", "user001", "笔记本电脑", 4999.99);

        orderDAO.create(newOrder);
        orderDAO.read("order001");
        orderDAO.findByUserId("user001");

        // 更新订单
        Order updatedOrder = new Order("order001", "user001", "游戏笔记本电脑", 5999.99);
        orderDAO.update("order001", updatedOrder);

        System.out.println("\n=== 多存储策略 ===");

        // 高频读取的数据使用Redis
        userDAO.changeStorage(redisStorage);
        userDAO.read("user001");

        // 持久化数据使用MySQL
        userDAO.changeStorage(mysqlStorage);
        userDAO.create(new User("user002", "李四", "lisi@example.com"));

        // 大文件数据使用文件存储
        orderDAO.changeStorage(fileStorage);
        orderDAO.create(new Order("order002", "user002", "大型设备", 29999.99));

        System.out.println("\n=== 数据迁移模拟 ===");
        System.out.println("从文件存储迁移到MySQL存储:");

        // 从文件存储读取
        orderDAO.changeStorage(fileStorage);
        Order orderToMigrate = (Order) orderDAO.read("order001");

        // 保存到MySQL
        if (orderToMigrate != null) {
            orderDAO.changeStorage(mysqlStorage);
            orderDAO.create(orderToMigrate);
            System.out.println("✅ 数据迁移完成");
        }

        System.out.println("\n观察：业务对象(抽象)和存储方式(实现)可以独立变化！");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **分离抽象和实现**
   - 抽象层和实现层可以独立变化
   - 避免类爆炸问题

2. **提高扩展性**
   - 新增抽象或实现都很简单
   - 符合开闭原则

3. **运行时切换实现**
   - 可以动态更换实现方式
   - 提高系统灵活性

4. **降低耦合度**
   - 客户端只需要知道抽象接口
   - 实现细节对客户端透明

### ❌ 缺点

1. **增加系统复杂性**
   - 引入更多的类和接口
   - 理解成本增加

2. **设计难度较高**
   - 需要正确识别抽象和实现维度
   - 需要合理设计接口

3. **性能开销**
   - 多了一层间接调用
   - 轻微的性能损失

## 🎯 使用场景总结

### 适合使用桥接模式的场景：
- 🎨 **图形系统** - 形状与渲染器分离
- 💾 **数据访问** - 业务对象与存储方式分离
- 📱 **跨平台开发** - 应用逻辑与平台API分离
- 🔌 **设备控制** - 控制逻辑与设备接口分离
- 🌐 **消息系统** - 消息类型与发送方式分离

### 不适合使用桥接模式的场景：
- 只有一个实现的情况
- 抽象和实现紧密耦合
- 系统简单，不需要多维度变化
- 性能要求极高的场景

## 🧠 记忆技巧

### 形象比喻
> **桥接模式就像是 "遥控器和电器"**：
> - 遥控器是抽象层（控制逻辑）
> - 电器是实现层（具体设备）
> - 红外线协议是桥梁（统一接口）
> - 可以用一个遥控器控制多种电器（抽象与实现分离）

### 设计要点
> **"两个维度，独立变化，桥梁连接，组合使用"**

### 与适配器模式的区别
- **适配器模式**：让不兼容的接口协同工作
- **桥接模式**：让抽象和实现可以独立变化

## 🔧 最佳实践

### 1. 接口设计原则

```java
// 好的实现接口设计：职责单一，方法简洁
public interface NotificationSender {
    void send(String recipient, String message);
    boolean isAvailable();
}

// 避免：接口过于复杂
public interface ComplexInterface {
    void send(String recipient, String message, String type, Map<String, Object> options);
    void configure(Properties config);
    void authenticate(String username, String password);
    // 太多职责...
}
```

### 2. 抽象层设计

```java
// 好的抽象层：提供合理的抽象，隐藏实现细节
public abstract class Document {
    protected DocumentRenderer renderer;

    protected Document(DocumentRenderer renderer) {
        this.renderer = renderer;
    }

    public abstract void open();
    public abstract void save();

    // 提供通用的功能
    public void print() {
        renderer.renderForPrint(this);
    }
}
```

### 3. 工厂模式结合

```java
/**
 * 桥接模式与工厂模式结合
 */
public class BridgeFactory {
    public static Shape createShape(String shapeType, String apiType) {
        DrawingAPI api = createAPI(apiType);

        switch (shapeType.toLowerCase()) {
            case "circle":
                return new Circle(0, 0, 10, api);
            case "rectangle":
                return new Rectangle(0, 0, 20, 15, api);
            default:
                throw new IllegalArgumentException("不支持的形状类型: " + shapeType);
        }
    }

    private static DrawingAPI createAPI(String apiType) {
        switch (apiType.toLowerCase()) {
            case "opengl":
                return new OpenGLDrawingAPI();
            case "directx":
                return new DirectXDrawingAPI();
            default:
                throw new IllegalArgumentException("不支持的API类型: " + apiType);
        }
    }
}
```

## 🚀 总结

桥接模式通过将抽象与实现分离，让两个维度可以独立变化，特别适用于：

- **多维度变化**的系统
- **需要运行时切换实现**的场景
- **避免类爆炸**的设计

核心思想：
- **组合优于继承**
- **抽象与实现分离**
- **两个维度独立变化**

设计要点：
- **正确识别抽象和实现维度**
- **设计简洁的实现接口**
- **合理的抽象层次**

记住，**桥接模式是架构师，不是万能钥匙**，要在合适的多维度变化场景下使用！

---
*下一篇：组合模式 - 树形结构的统一处理*