---
title: "设计模式入门教程20：中介者模式 - 让对象间交互更简洁"
date: 2024-12-20T10:20:00+08:00
draft: false
tags: ["设计模式", "中介者模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是中介者模式？

中介者模式（Mediator Pattern）是一种行为型设计模式，它定义了一个中介对象来封装一系列对象之间的交互。中介者模式使各对象不需要显式地相互引用，从而使其耦合松散，而且可以独立地改变它们之间的交互。

### 🌟 现实生活中的例子

想象一下**机场塔台管制**：
- **飞机**：各个航班不能直接互相通信
- **塔台**：作为中介者协调所有飞机的起降
- **好处**：避免飞机间的混乱交流，统一管理空域

又比如**房产中介**：
- **买家和卖家**：不直接接触
- **中介**：协调双方需求，处理交易流程
- **简化**：避免复杂的多方沟通

这就是中介者模式的典型应用！

## 🏗️ 模式结构

```java
// 抽象中介者
abstract class Mediator {
    public abstract void notify(Component sender, String event);
}

// 抽象组件
abstract class Component {
    protected Mediator mediator;

    public Component(Mediator mediator) {
        this.mediator = mediator;
    }

    public void setMediator(Mediator mediator) {
        this.mediator = mediator;
    }
}

// 具体中介者
class ConcreteMediator extends Mediator {
    private ComponentA componentA;
    private ComponentB componentB;

    public void setComponents(ComponentA a, ComponentB b) {
        this.componentA = a;
        this.componentB = b;
    }

    @Override
    public void notify(Component sender, String event) {
        if (sender == componentA) {
            if ("EventA".equals(event)) {
                componentB.operationB();
            }
        } else if (sender == componentB) {
            if ("EventB".equals(event)) {
                componentA.operationA();
            }
        }
    }
}

// 具体组件
class ComponentA extends Component {
    public ComponentA(Mediator mediator) {
        super(mediator);
    }

    public void operationA() {
        System.out.println("执行操作A");
        mediator.notify(this, "EventA");
    }
}

class ComponentB extends Component {
    public ComponentB(Mediator mediator) {
        super(mediator);
    }

    public void operationB() {
        System.out.println("执行操作B");
        mediator.notify(this, "EventB");
    }
}
```

## 💡 核心组件详解

### 1. 抽象中介者（Mediator）
```java
// 智能家居中介者接口
interface SmartHomeMediator {
    void notify(SmartDevice sender, String event, Object data);
    void registerDevice(SmartDevice device);
    void removeDevice(SmartDevice device);
}
```

### 2. 具体中介者（ConcreteMediator）
```java
// 智能家居控制中心
class SmartHomeControlCenter implements SmartHomeMediator {
    private List<SmartDevice> devices = new ArrayList<>();
    private Map<String, Object> environmentData = new HashMap<>();
    private boolean securityMode = false;
    private boolean energySavingMode = false;

    @Override
    public void registerDevice(SmartDevice device) {
        devices.add(device);
        device.setMediator(this);
        System.out.println("设备已注册：" + device.getName());
    }

    @Override
    public void removeDevice(SmartDevice device) {
        devices.remove(device);
        System.out.println("设备已移除：" + device.getName());
    }

    @Override
    public void notify(SmartDevice sender, String event, Object data) {
        System.out.println("收到事件：" + sender.getName() + " -> " + event);

        switch (event) {
            case "MOTION_DETECTED":
                handleMotionDetected(sender, data);
                break;
            case "TEMPERATURE_CHANGED":
                handleTemperatureChanged(sender, data);
                break;
            case "DOOR_OPENED":
                handleDoorOpened(sender, data);
                break;
            case "DOOR_CLOSED":
                handleDoorClosed(sender, data);
                break;
            case "LIGHT_TURNED_ON":
                handleLightTurnedOn(sender, data);
                break;
            case "LIGHT_TURNED_OFF":
                handleLightTurnedOff(sender, data);
                break;
            case "SECURITY_ARMED":
                handleSecurityArmed(sender, data);
                break;
            case "SECURITY_DISARMED":
                handleSecurityDisarmed(sender, data);
                break;
            default:
                System.out.println("未知事件：" + event);
        }
    }

    private void handleMotionDetected(SmartDevice sender, Object data) {
        String location = (String) data;
        environmentData.put("lastMotionLocation", location);

        // 如果是夜间，自动开灯
        if (isNightTime()) {
            getDevicesByType("SmartLight")
                .stream()
                .filter(device -> device.getName().contains(location))
                .forEach(light -> ((SmartLight) light).turnOn());
        }

        // 如果启用了安全模式，触发警报
        if (securityMode) {
            getDevicesByType("SecurityCamera")
                .forEach(camera -> ((SecurityCamera) camera).startRecording());

            getDevicesByType("AlarmSystem")
                .forEach(alarm -> ((AlarmSystem) alarm).triggerAlarm());
        }
    }

    private void handleTemperatureChanged(SmartDevice sender, Object data) {
        double temperature = (Double) data;
        environmentData.put("currentTemperature", temperature);

        // 自动调节空调
        if (temperature > 26.0) {
            getDevicesByType("AirConditioner")
                .forEach(ac -> ((AirConditioner) ac).setCooling(22.0));
        } else if (temperature < 18.0) {
            getDevicesByType("AirConditioner")
                .forEach(ac -> ((AirConditioner) ac).setHeating(22.0));
        }

        // 节能模式下调整设备
        if (energySavingMode && temperature > 24.0) {
            getDevicesByType("SmartLight")
                .forEach(light -> ((SmartLight) light).dimTo(50));
        }
    }

    private void handleDoorOpened(SmartDevice sender, Object data) {
        // 门开启时的联动
        if (securityMode) {
            // 安全模式下记录开门事件
            System.out.println("安全警告：门被打开 - " + sender.getName());
        } else {
            // 正常模式下开启入口灯光
            getDevicesByType("SmartLight")
                .stream()
                .filter(light -> light.getName().contains("entrance"))
                .forEach(light -> ((SmartLight) light).turnOn());
        }
    }

    private void handleDoorClosed(SmartDevice sender, Object data) {
        // 所有门关闭时，可以启用节能模式
        boolean allDoorsClosed = getDevicesByType("SmartDoor")
                .stream()
                .allMatch(door -> !((SmartDoor) door).isOpen());

        if (allDoorsClosed && !hasRecentMotion()) {
            enableEnergySavingMode();
        }
    }

    private void handleLightTurnedOn(SmartDevice sender, Object data) {
        // 灯光开启时的联动（如果不是自动开启的话）
        if (!energySavingMode) {
            // 可以调整其他相关设备
        }
    }

    private void handleLightTurnedOff(SmartDevice sender, Object data) {
        // 检查是否所有灯都关闭，进入深度节能模式
        boolean allLightsOff = getDevicesByType("SmartLight")
                .stream()
                .noneMatch(light -> ((SmartLight) light).isOn());

        if (allLightsOff) {
            enableDeepEnergySavingMode();
        }
    }

    private void handleSecurityArmed(SmartDevice sender, Object data) {
        securityMode = true;
        System.out.println("安全模式已启用");

        // 关闭所有非必要设备
        getDevicesByType("SmartLight")
                .forEach(light -> ((SmartLight) light).turnOff());

        // 启动所有安全设备
        getDevicesByType("SecurityCamera")
                .forEach(camera -> ((SecurityCamera) camera).startMonitoring());
    }

    private void handleSecurityDisarmed(SmartDevice sender, Object data) {
        securityMode = false;
        System.out.println("安全模式已关闭");

        // 停止录制
        getDevicesByType("SecurityCamera")
                .forEach(camera -> ((SecurityCamera) camera).stopRecording());
    }

    // 辅助方法
    private List<SmartDevice> getDevicesByType(String type) {
        return devices.stream()
                .filter(device -> device.getClass().getSimpleName().equals(type))
                .collect(Collectors.toList());
    }

    private boolean isNightTime() {
        // 简化实现：假设22:00-06:00为夜间
        int hour = LocalDateTime.now().getHour();
        return hour >= 22 || hour <= 6;
    }

    private boolean hasRecentMotion() {
        // 检查最近5分钟是否有移动
        return environmentData.containsKey("lastMotionTime") &&
               System.currentTimeMillis() - (Long) environmentData.get("lastMotionTime") < 300000;
    }

    private void enableEnergySavingMode() {
        energySavingMode = true;
        System.out.println("已启用节能模式");

        // 调暗所有灯光
        getDevicesByType("SmartLight")
                .forEach(light -> ((SmartLight) light).dimTo(30));

        // 调整空调温度
        getDevicesByType("AirConditioner")
                .forEach(ac -> ((AirConditioner) ac).setEcoMode(true));
    }

    private void enableDeepEnergySavingMode() {
        System.out.println("已启用深度节能模式");

        // 关闭非必要设备
        getDevicesByType("AirConditioner")
                .forEach(ac -> ((AirConditioner) ac).turnOff());
    }

    public void showSystemStatus() {
        System.out.println("=== 智能家居系统状态 ===");
        System.out.println("安全模式：" + (securityMode ? "启用" : "关闭"));
        System.out.println("节能模式：" + (energySavingMode ? "启用" : "关闭"));
        System.out.println("注册设备数：" + devices.size());
        System.out.println("环境数据：" + environmentData);
        System.out.println("========================");
    }
}
```

### 3. 抽象组件（Component）
```java
// 智能设备抽象类
abstract class SmartDevice {
    protected String name;
    protected SmartHomeMediator mediator;
    protected boolean isOnline;

    public SmartDevice(String name) {
        this.name = name;
        this.isOnline = true;
    }

    public void setMediator(SmartHomeMediator mediator) {
        this.mediator = mediator;
    }

    public String getName() {
        return name;
    }

    public boolean isOnline() {
        return isOnline;
    }

    public void setOnline(boolean online) {
        this.isOnline = online;
        if (mediator != null) {
            mediator.notify(this, online ? "DEVICE_ONLINE" : "DEVICE_OFFLINE", null);
        }
    }

    protected void notifyMediator(String event, Object data) {
        if (mediator != null && isOnline) {
            mediator.notify(this, event, data);
        }
    }
}
```

### 4. 具体组件（ConcreteComponent）
```java
// 智能灯具
class SmartLight extends SmartDevice {
    private boolean isOn;
    private int brightness; // 0-100

    public SmartLight(String name) {
        super(name);
        this.isOn = false;
        this.brightness = 100;
    }

    public void turnOn() {
        if (!isOn) {
            isOn = true;
            System.out.println(name + " 灯光已开启");
            notifyMediator("LIGHT_TURNED_ON", null);
        }
    }

    public void turnOff() {
        if (isOn) {
            isOn = false;
            System.out.println(name + " 灯光已关闭");
            notifyMediator("LIGHT_TURNED_OFF", null);
        }
    }

    public void dimTo(int percentage) {
        if (isOn) {
            this.brightness = Math.max(0, Math.min(100, percentage));
            System.out.println(name + " 亮度调节至：" + brightness + "%");
            notifyMediator("LIGHT_DIMMED", brightness);
        }
    }

    public boolean isOn() {
        return isOn;
    }

    public int getBrightness() {
        return brightness;
    }
}

// 智能门锁
class SmartDoor extends SmartDevice {
    private boolean isOpen;
    private boolean isLocked;

    public SmartDoor(String name) {
        super(name);
        this.isOpen = false;
        this.isLocked = true;
    }

    public void open() {
        if (!isOpen && !isLocked) {
            isOpen = true;
            System.out.println(name + " 门已打开");
            notifyMediator("DOOR_OPENED", null);
        } else if (isLocked) {
            System.out.println(name + " 门被锁定，无法打开");
        }
    }

    public void close() {
        if (isOpen) {
            isOpen = false;
            System.out.println(name + " 门已关闭");
            notifyMediator("DOOR_CLOSED", null);
        }
    }

    public void lock() {
        if (!isLocked) {
            isLocked = true;
            if (isOpen) {
                close();
            }
            System.out.println(name + " 门已锁定");
            notifyMediator("DOOR_LOCKED", null);
        }
    }

    public void unlock() {
        if (isLocked) {
            isLocked = false;
            System.out.println(name + " 门已解锁");
            notifyMediator("DOOR_UNLOCKED", null);
        }
    }

    public boolean isOpen() {
        return isOpen;
    }

    public boolean isLocked() {
        return isLocked;
    }
}

// 温度传感器
class TemperatureSensor extends SmartDevice {
    private double currentTemperature;

    public TemperatureSensor(String name) {
        super(name);
        this.currentTemperature = 22.0; // 默认室温
    }

    public void updateTemperature(double temperature) {
        this.currentTemperature = temperature;
        System.out.println(name + " 检测到温度：" + temperature + "°C");
        notifyMediator("TEMPERATURE_CHANGED", temperature);
    }

    public double getCurrentTemperature() {
        return currentTemperature;
    }

    // 模拟温度变化
    public void simulateTemperatureChange() {
        // 随机温度变化
        double change = (Math.random() - 0.5) * 4; // -2°C 到 +2°C
        updateTemperature(currentTemperature + change);
    }
}

// 移动传感器
class MotionSensor extends SmartDevice {
    private boolean motionDetected;

    public MotionSensor(String name) {
        super(name);
        this.motionDetected = false;
    }

    public void detectMotion(String location) {
        motionDetected = true;
        System.out.println(name + " 检测到移动：" + location);
        notifyMediator("MOTION_DETECTED", location);

        // 模拟移动检测持续一段时间
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                motionDetected = false;
                System.out.println(name + " 移动检测结束");
            }
        }, 5000); // 5秒后结束移动检测
    }

    public boolean isMotionDetected() {
        return motionDetected;
    }
}

// 空调设备
class AirConditioner extends SmartDevice {
    private boolean isOn;
    private double targetTemperature;
    private String mode; // "cooling", "heating", "off"
    private boolean ecoMode;

    public AirConditioner(String name) {
        super(name);
        this.isOn = false;
        this.targetTemperature = 22.0;
        this.mode = "off";
        this.ecoMode = false;
    }

    public void turnOn() {
        isOn = true;
        mode = "cooling";
        System.out.println(name + " 空调已开启（制冷模式）");
        notifyMediator("AC_TURNED_ON", mode);
    }

    public void turnOff() {
        isOn = false;
        mode = "off";
        System.out.println(name + " 空调已关闭");
        notifyMediator("AC_TURNED_OFF", null);
    }

    public void setCooling(double temperature) {
        isOn = true;
        mode = "cooling";
        targetTemperature = temperature;
        System.out.println(name + " 设置制冷温度：" + temperature + "°C");
        notifyMediator("AC_MODE_CHANGED", "cooling");
    }

    public void setHeating(double temperature) {
        isOn = true;
        mode = "heating";
        targetTemperature = temperature;
        System.out.println(name + " 设置制热温度：" + temperature + "°C");
        notifyMediator("AC_MODE_CHANGED", "heating");
    }

    public void setEcoMode(boolean eco) {
        this.ecoMode = eco;
        if (eco) {
            targetTemperature += mode.equals("cooling") ? 2 : -2; // 节能调整
        }
        System.out.println(name + " 节能模式：" + (eco ? "启用" : "关闭"));
        notifyMediator("AC_ECO_MODE_CHANGED", eco);
    }

    public boolean isOn() { return isOn; }
    public double getTargetTemperature() { return targetTemperature; }
    public String getMode() { return mode; }
    public boolean isEcoMode() { return ecoMode; }
}

// 安全摄像头
class SecurityCamera extends SmartDevice {
    private boolean isRecording;
    private boolean isMonitoring;

    public SecurityCamera(String name) {
        super(name);
        this.isRecording = false;
        this.isMonitoring = false;
    }

    public void startMonitoring() {
        isMonitoring = true;
        System.out.println(name + " 开始监控");
        notifyMediator("CAMERA_MONITORING_STARTED", null);
    }

    public void stopMonitoring() {
        isMonitoring = false;
        if (isRecording) {
            stopRecording();
        }
        System.out.println(name + " 停止监控");
        notifyMediator("CAMERA_MONITORING_STOPPED", null);
    }

    public void startRecording() {
        if (isMonitoring) {
            isRecording = true;
            System.out.println(name + " 开始录制");
            notifyMediator("CAMERA_RECORDING_STARTED", null);
        }
    }

    public void stopRecording() {
        if (isRecording) {
            isRecording = false;
            System.out.println(name + " 停止录制");
            notifyMediator("CAMERA_RECORDING_STOPPED", null);
        }
    }

    public boolean isRecording() { return isRecording; }
    public boolean isMonitoring() { return isMonitoring; }
}

// 警报系统
class AlarmSystem extends SmartDevice {
    private boolean isArmed;
    private boolean isAlarming;

    public AlarmSystem(String name) {
        super(name);
        this.isArmed = false;
        this.isAlarming = false;
    }

    public void arm() {
        isArmed = true;
        System.out.println(name + " 警报系统已启用");
        notifyMediator("SECURITY_ARMED", null);
    }

    public void disarm() {
        isArmed = false;
        if (isAlarming) {
            stopAlarm();
        }
        System.out.println(name + " 警报系统已关闭");
        notifyMediator("SECURITY_DISARMED", null);
    }

    public void triggerAlarm() {
        if (isArmed && !isAlarming) {
            isAlarming = true;
            System.out.println(name + " 🚨 警报响起！");
            notifyMediator("ALARM_TRIGGERED", null);

            // 模拟警报持续30秒
            Timer timer = new Timer();
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    stopAlarm();
                }
            }, 30000);
        }
    }

    public void stopAlarm() {
        if (isAlarming) {
            isAlarming = false;
            System.out.println(name + " 警报已停止");
            notifyMediator("ALARM_STOPPED", null);
        }
    }

    public boolean isArmed() { return isArmed; }
    public boolean isAlarming() { return isAlarming; }
}
```

## 🎮 实际应用示例

### 示例1：聊天室系统
```java
// 聊天室中介者接口
interface ChatRoomMediator {
    void sendMessage(String message, User user);
    void addUser(User user);
    void removeUser(User user);
    void notifyUsers(String message, User excludeUser);
}

// 聊天室实现
class ChatRoom implements ChatRoomMediator {
    private List<User> users = new ArrayList<>();
    private List<String> messageHistory = new ArrayList<>();
    private Map<String, Integer> userMessageCount = new HashMap<>();

    @Override
    public void addUser(User user) {
        users.add(user);
        user.setMediator(this);
        String joinMessage = user.getName() + " 加入了聊天室";
        messageHistory.add(joinMessage);
        notifyUsers(joinMessage, user);
        System.out.println("用户 " + user.getName() + " 已加入聊天室");
    }

    @Override
    public void removeUser(User user) {
        users.remove(user);
        String leaveMessage = user.getName() + " 离开了聊天室";
        messageHistory.add(leaveMessage);
        notifyUsers(leaveMessage, null);
        userMessageCount.remove(user.getName());
        System.out.println("用户 " + user.getName() + " 已离开聊天室");
    }

    @Override
    public void sendMessage(String message, User sender) {
        String fullMessage = sender.getName() + ": " + message;
        messageHistory.add(fullMessage);

        // 统计用户消息数
        userMessageCount.put(sender.getName(),
                userMessageCount.getOrDefault(sender.getName(), 0) + 1);

        // 检查消息是否为命令
        if (message.startsWith("/")) {
            handleCommand(message, sender);
        } else {
            // 普通消息广播给所有其他用户
            for (User user : users) {
                if (user != sender) {
                    user.receive(fullMessage);
                }
            }
        }

        System.out.println("消息已发送：" + fullMessage);
    }

    @Override
    public void notifyUsers(String message, User excludeUser) {
        for (User user : users) {
            if (user != excludeUser) {
                user.receive("系统消息：" + message);
            }
        }
    }

    private void handleCommand(String command, User sender) {
        String[] parts = command.split(" ", 2);
        String cmd = parts[0].toLowerCase();

        switch (cmd) {
            case "/list":
                String userList = "在线用户：" + users.stream()
                        .map(User::getName)
                        .collect(Collectors.joining(", "));
                sender.receive(userList);
                break;

            case "/history":
                sender.receive("=== 聊天记录 ===");
                messageHistory.stream()
                        .skip(Math.max(0, messageHistory.size() - 10)) // 最近10条
                        .forEach(sender::receive);
                break;

            case "/stats":
                String stats = userMessageCount.entrySet().stream()
                        .map(entry -> entry.getKey() + ": " + entry.getValue() + "条消息")
                        .collect(Collectors.joining(", "));
                sender.receive("消息统计：" + stats);
                break;

            case "/private":
                if (parts.length > 1) {
                    handlePrivateMessage(parts[1], sender);
                } else {
                    sender.receive("用法：/private 用户名 消息内容");
                }
                break;

            case "/help":
                sender.receive("可用命令：/list, /history, /stats, /private, /help");
                break;

            default:
                sender.receive("未知命令：" + cmd + "，输入 /help 查看可用命令");
        }
    }

    private void handlePrivateMessage(String content, User sender) {
        String[] parts = content.split(" ", 2);
        if (parts.length < 2) {
            sender.receive("用法：/private 用户名 消息内容");
            return;
        }

        String targetName = parts[0];
        String message = parts[1];

        User target = users.stream()
                .filter(user -> user.getName().equals(targetName))
                .findFirst()
                .orElse(null);

        if (target != null) {
            target.receive("[私聊] " + sender.getName() + ": " + message);
            sender.receive("[私聊] 已发送给 " + targetName + ": " + message);
        } else {
            sender.receive("用户 " + targetName + " 不在线");
        }
    }

    public void showRoomStats() {
        System.out.println("=== 聊天室统计 ===");
        System.out.println("在线用户：" + users.size());
        System.out.println("历史消息：" + messageHistory.size());
        System.out.println("活跃用户：" + userMessageCount.size());
        System.out.println("================");
    }
}

// 用户抽象类
abstract class User {
    protected String name;
    protected ChatRoomMediator mediator;

    public User(String name) {
        this.name = name;
    }

    public void setMediator(ChatRoomMediator mediator) {
        this.mediator = mediator;
    }

    public String getName() {
        return name;
    }

    public abstract void send(String message);
    public abstract void receive(String message);
}

// 普通用户
class RegularUser extends User {
    public RegularUser(String name) {
        super(name);
    }

    @Override
    public void send(String message) {
        System.out.println(name + " 发送消息：" + message);
        if (mediator != null) {
            mediator.sendMessage(message, this);
        }
    }

    @Override
    public void receive(String message) {
        System.out.println(name + " 收到消息：" + message);
    }
}

// 管理员用户
class AdminUser extends User {
    public AdminUser(String name) {
        super(name);
    }

    @Override
    public void send(String message) {
        System.out.println("[管理员] " + name + " 发送消息：" + message);
        if (mediator != null) {
            mediator.sendMessage(message, this);
        }
    }

    @Override
    public void receive(String message) {
        System.out.println("[管理员] " + name + " 收到消息：" + message);
    }

    public void sendAnnouncement(String announcement) {
        System.out.println("[系统公告] " + announcement);
        if (mediator != null) {
            mediator.notifyUsers("📢 " + announcement, null);
        }
    }

    public void kickUser(User user) {
        System.out.println("[管理员] " + name + " 踢出用户：" + user.getName());
        if (mediator != null) {
            mediator.removeUser(user);
        }
    }
}

// 使用示例
public class ChatRoomExample {
    public static void main(String[] args) throws InterruptedException {
        ChatRoom chatRoom = new ChatRoom();

        // 创建用户
        User alice = new RegularUser("Alice");
        User bob = new RegularUser("Bob");
        User charlie = new RegularUser("Charlie");
        AdminUser admin = new AdminUser("Admin");

        // 用户加入聊天室
        chatRoom.addUser(alice);
        chatRoom.addUser(bob);
        chatRoom.addUser(charlie);
        chatRoom.addUser(admin);

        System.out.println("\n=== 聊天开始 ===");

        // 普通聊天
        alice.send("大家好！");
        Thread.sleep(1000);

        bob.send("你好 Alice！");
        Thread.sleep(1000);

        charlie.send("嗨，大家！");
        Thread.sleep(1000);

        // 使用命令
        System.out.println("\n=== 命令测试 ===");
        alice.send("/list");
        Thread.sleep(500);

        bob.send("/stats");
        Thread.sleep(500);

        // 私聊
        alice.send("/private Bob 你好，这是私聊消息");
        Thread.sleep(500);

        // 管理员功能
        System.out.println("\n=== 管理员功能 ===");
        admin.sendAnnouncement("欢迎大家来到聊天室！");
        Thread.sleep(1000);

        // 显示统计
        chatRoom.showRoomStats();

        // 用户离开
        System.out.println("\n=== 用户离开 ===");
        chatRoom.removeUser(charlie);
    }
}
```

### 示例2：游戏对战系统
```java
// 游戏对战中介者接口
interface GameMediator {
    void registerPlayer(Player player);
    void removePlayer(Player player);
    void playerAction(Player player, String action, Object data);
    void broadcastMessage(String message, Player excludePlayer);
    void startGame();
    void endGame(Player winner);
}

// 游戏房间中介者
class GameRoom implements GameMediator {
    private List<Player> players = new ArrayList<>();
    private GameState gameState = GameState.WAITING;
    private Map<Player, Integer> playerScores = new HashMap<>();
    private int roundNumber = 0;
    private Timer gameTimer;

    @Override
    public void registerPlayer(Player player) {
        if (players.size() < 4) { // 最多4人
            players.add(player);
            player.setMediator(this);
            playerScores.put(player, 0);
            System.out.println("玩家 " + player.getName() + " 加入游戏 (" + players.size() + "/4)");
            broadcastMessage("玩家 " + player.getName() + " 加入了游戏", player);

            if (players.size() >= 2) {
                broadcastMessage("人数足够，可以开始游戏！输入 'ready' 准备", null);
            }
        } else {
            player.receiveMessage("游戏房间已满");
        }
    }

    @Override
    public void removePlayer(Player player) {
        players.remove(player);
        playerScores.remove(player);
        System.out.println("玩家 " + player.getName() + " 离开游戏");
        broadcastMessage("玩家 " + player.getName() + " 离开了游戏", null);

        if (gameState == GameState.PLAYING && players.size() < 2) {
            endGame(null); // 人数不足，结束游戏
        }
    }

    @Override
    public void playerAction(Player player, String action, Object data) {
        switch (action) {
            case "ready":
                handlePlayerReady(player);
                break;
            case "attack":
                handlePlayerAttack(player, (Player) data);
                break;
            case "defend":
                handlePlayerDefend(player);
                break;
            case "use_skill":
                handlePlayerSkill(player, (String) data);
                break;
            case "chat":
                handlePlayerChat(player, (String) data);
                break;
            default:
                player.receiveMessage("未知动作：" + action);
        }
    }

    @Override
    public void broadcastMessage(String message, Player excludePlayer) {
        for (Player player : players) {
            if (player != excludePlayer) {
                player.receiveMessage(message);
            }
        }
    }

    @Override
    public void startGame() {
        if (players.size() < 2) {
            broadcastMessage("人数不足，无法开始游戏", null);
            return;
        }

        gameState = GameState.PLAYING;
        roundNumber = 1;

        // 初始化玩家状态
        for (Player player : players) {
            player.resetForNewGame();
            playerScores.put(player, 0);
        }

        broadcastMessage("🎮 游戏开始！第" + roundNumber + "轮", null);
        System.out.println("游戏开始，" + players.size() + " 名玩家参与");

        // 设置游戏时间限制
        startGameTimer();
    }

    @Override
    public void endGame(Player winner) {
        gameState = GameState.ENDED;

        if (gameTimer != null) {
            gameTimer.cancel();
        }

        if (winner != null) {
            broadcastMessage("🏆 游戏结束！获胜者：" + winner.getName(), null);
            playerScores.put(winner, playerScores.get(winner) + 10);
        } else {
            broadcastMessage("游戏结束！平局", null);
        }

        showFinalScores();
        gameState = GameState.WAITING;
    }

    private void handlePlayerReady(Player player) {
        if (gameState == GameState.WAITING) {
            player.setReady(true);
            broadcastMessage("玩家 " + player.getName() + " 已准备", player);

            boolean allReady = players.stream().allMatch(Player::isReady);
            if (allReady && players.size() >= 2) {
                startGame();
            }
        } else {
            player.receiveMessage("游戏已经开始或结束");
        }
    }

    private void handlePlayerAttack(Player player, Player target) {
        if (gameState != GameState.PLAYING) {
            player.receiveMessage("游戏未开始");
            return;
        }

        if (target == null || !players.contains(target)) {
            player.receiveMessage("目标玩家无效");
            return;
        }

        if (player == target) {
            player.receiveMessage("不能攻击自己");
            return;
        }

        // 计算伤害
        int damage = calculateDamage(player, target);
        target.takeDamage(damage);

        String attackMessage = "⚔️ " + player.getName() + " 攻击了 " + target.getName() +
                " 造成 " + damage + " 点伤害";
        broadcastMessage(attackMessage, null);

        // 检查目标是否被击败
        if (target.getHealth() <= 0) {
            playerScores.put(player, playerScores.get(player) + 5);
            broadcastMessage("💀 " + target.getName() + " 被击败了！", null);
            target.setAlive(false);

            // 检查游戏是否结束
            List<Player> alivePlayers = players.stream()
                    .filter(Player::isAlive)
                    .collect(Collectors.toList());

            if (alivePlayers.size() <= 1) {
                endGame(alivePlayers.isEmpty() ? null : alivePlayers.get(0));
            }
        }
    }

    private void handlePlayerDefend(Player player) {
        if (gameState != GameState.PLAYING) {
            player.receiveMessage("游戏未开始");
            return;
        }

        player.setDefending(true);
        broadcastMessage("🛡️ " + player.getName() + " 进入防御姿态", player);

        // 防御状态持续一定时间
        Timer defenseTimer = new Timer();
        defenseTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                player.setDefending(false);
                player.receiveMessage("防御状态结束");
            }
        }, 5000); // 5秒防御时间
    }

    private void handlePlayerSkill(Player player, String skillName) {
        if (gameState != GameState.PLAYING) {
            player.receiveMessage("游戏未开始");
            return;
        }

        boolean skillUsed = player.useSkill(skillName);
        if (skillUsed) {
            String skillMessage = "✨ " + player.getName() + " 使用了技能：" + skillName;
            broadcastMessage(skillMessage, player);

            // 根据技能类型执行效果
            executeSkillEffect(player, skillName);
        } else {
            player.receiveMessage("技能冷却中或能量不足");
        }
    }

    private void handlePlayerChat(Player player, String message) {
        String chatMessage = "[聊天] " + player.getName() + ": " + message;
        broadcastMessage(chatMessage, player);
    }

    private int calculateDamage(Player attacker, Player target) {
        int baseDamage = attacker.getAttackPower();

        // 如果目标在防御，伤害减半
        if (target.isDefending()) {
            baseDamage /= 2;
        }

        // 添加随机因素
        int randomFactor = (int) (Math.random() * 20) - 10; // -10 到 +10
        return Math.max(1, baseDamage + randomFactor);
    }

    private void executeSkillEffect(Player player, String skillName) {
        switch (skillName) {
            case "heal":
                player.heal(30);
                player.receiveMessage("你恢复了30点生命值");
                break;
            case "boost":
                player.setAttackPower(player.getAttackPower() + 10);
                player.receiveMessage("你的攻击力提升了10点");
                break;
            case "fireball":
                // 对所有其他玩家造成伤害
                for (Player target : players) {
                    if (target != player && target.isAlive()) {
                        target.takeDamage(15);
                    }
                }
                broadcastMessage("🔥 火球术对所有敌人造成15点伤害", player);
                break;
        }
    }

    private void startGameTimer() {
        gameTimer = new Timer();
        gameTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                broadcastMessage("⏰ 游戏时间到！", null);
                // 根据生命值判断胜负
                Player winner = players.stream()
                        .filter(Player::isAlive)
                        .max(Comparator.comparingInt(Player::getHealth))
                        .orElse(null);
                endGame(winner);
            }
        }, 300000); // 5分钟游戏时间
    }

    private void showFinalScores() {
        System.out.println("=== 最终积分 ===");
        playerScores.entrySet().stream()
                .sorted(Map.Entry.<Player, Integer>comparingByValue().reversed())
                .forEach(entry -> {
                    String result = entry.getKey().getName() + ": " + entry.getValue() + "分";
                    System.out.println(result);
                    broadcastMessage(result, null);
                });
    }

    public GameState getGameState() {
        return gameState;
    }
}

// 游戏状态枚举
enum GameState {
    WAITING, PLAYING, ENDED
}

// 玩家抽象类
abstract class Player {
    protected String name;
    protected GameMediator mediator;
    protected int health;
    protected int maxHealth;
    protected int attackPower;
    protected boolean isReady;
    protected boolean isAlive;
    protected boolean isDefending;
    protected Map<String, Long> skillCooldowns;

    public Player(String name) {
        this.name = name;
        this.maxHealth = 100;
        this.health = maxHealth;
        this.attackPower = 20;
        this.isReady = false;
        this.isAlive = true;
        this.isDefending = false;
        this.skillCooldowns = new HashMap<>();
    }

    public void setMediator(GameMediator mediator) {
        this.mediator = mediator;
    }

    public void resetForNewGame() {
        health = maxHealth;
        attackPower = 20;
        isReady = false;
        isAlive = true;
        isDefending = false;
        skillCooldowns.clear();
    }

    public void takeDamage(int damage) {
        health = Math.max(0, health - damage);
        receiveMessage("你受到了 " + damage + " 点伤害，当前生命值：" + health);
    }

    public void heal(int amount) {
        health = Math.min(maxHealth, health + amount);
    }

    public boolean useSkill(String skillName) {
        long currentTime = System.currentTimeMillis();
        Long lastUsed = skillCooldowns.get(skillName);

        if (lastUsed != null && currentTime - lastUsed < 10000) { // 10秒冷却
            return false;
        }

        skillCooldowns.put(skillName, currentTime);
        return true;
    }

    public abstract void receiveMessage(String message);

    // Getters and Setters
    public String getName() { return name; }
    public int getHealth() { return health; }
    public int getAttackPower() { return attackPower; }
    public void setAttackPower(int attackPower) { this.attackPower = attackPower; }
    public boolean isReady() { return isReady; }
    public void setReady(boolean ready) { isReady = ready; }
    public boolean isAlive() { return isAlive; }
    public void setAlive(boolean alive) { isAlive = alive; }
    public boolean isDefending() { return isDefending; }
    public void setDefending(boolean defending) { isDefending = defending; }
}

// 具体玩家实现
class GamePlayer extends Player {
    public GamePlayer(String name) {
        super(name);
    }

    @Override
    public void receiveMessage(String message) {
        System.out.println("[" + name + "] " + message);
    }

    public void attack(Player target) {
        if (mediator != null) {
            mediator.playerAction(this, "attack", target);
        }
    }

    public void defend() {
        if (mediator != null) {
            mediator.playerAction(this, "defend", null);
        }
    }

    public void useSkill(String skillName) {
        if (mediator != null) {
            mediator.playerAction(this, "use_skill", skillName);
        }
    }

    public void chat(String message) {
        if (mediator != null) {
            mediator.playerAction(this, "chat", message);
        }
    }

    public void ready() {
        if (mediator != null) {
            mediator.playerAction(this, "ready", null);
        }
    }
}

// 使用示例
public class GameRoomExample {
    public static void main(String[] args) throws InterruptedException {
        GameRoom gameRoom = new GameRoom();

        // 创建玩家
        GamePlayer alice = new GamePlayer("Alice");
        GamePlayer bob = new GamePlayer("Bob");
        GamePlayer charlie = new GamePlayer("Charlie");

        // 玩家加入游戏
        gameRoom.registerPlayer(alice);
        Thread.sleep(1000);

        gameRoom.registerPlayer(bob);
        Thread.sleep(1000);

        gameRoom.registerPlayer(charlie);
        Thread.sleep(1000);

        // 玩家聊天
        alice.chat("大家好，准备开始游戏吗？");
        Thread.sleep(500);

        bob.chat("我准备好了！");
        Thread.sleep(500);

        // 玩家准备
        alice.ready();
        Thread.sleep(500);

        bob.ready();
        Thread.sleep(500);

        charlie.ready();
        Thread.sleep(2000);

        // 游戏开始后的战斗
        System.out.println("\n=== 战斗开始 ===");
        alice.attack(bob);
        Thread.sleep(1000);

        bob.defend();
        Thread.sleep(1000);

        charlie.useSkill("fireball");
        Thread.sleep(1000);

        alice.useSkill("heal");
        Thread.sleep(1000);

        bob.attack(charlie);
        Thread.sleep(1000);

        // 继续战斗直到有玩家被击败
        while (gameRoom.getGameState() == GameState.PLAYING) {
            Thread.sleep(2000);
            // 模拟随机战斗
            List<Player> alivePlayers = List.of(alice, bob, charlie).stream()
                    .filter(Player::isAlive)
                    .collect(Collectors.toList());

            if (alivePlayers.size() > 1) {
                Player attacker = alivePlayers.get((int) (Math.random() * alivePlayers.size()));
                Player target = alivePlayers.stream()
                        .filter(p -> p != attacker)
                        .findFirst()
                        .orElse(null);

                if (target != null) {
                    ((GamePlayer) attacker).attack(target);
                }
            } else {
                break;
            }
        }
    }
}
```

## ✅ 优势分析

### 1. **减少对象间耦合**
对象不需要直接引用其他对象，降低了系统的耦合度。

### 2. **集中控制逻辑**
复杂的交互逻辑集中在中介者中，便于管理和修改。

### 3. **提高可重用性**
组件可以独立复用，不依赖特定的交互对象。

### 4. **简化对象协议**
对象只需要与中介者通信，简化了通信协议。

## ⚠️ 注意事项

### 1. **中介者复杂性**
```java
// 避免中介者变得过于复杂
class OvercomplicatedMediator implements Mediator {
    // 不要在中介者中实现太多业务逻辑
    public void handleComplexBusinessLogic() {
        // 太多逻辑会使中介者难以维护
    }
}

// 正确做法：保持中介者简洁
class SimpleMediator implements Mediator {
    public void notify(Component sender, String event) {
        // 只处理组件间的协调，不包含复杂业务逻辑
        routeEvent(sender, event);
    }
}
```

### 2. **性能考虑**
所有通信都经过中介者，可能成为性能瓶颈。

### 3. **单点故障**
中介者故障会影响整个系统的通信。

## 🆚 与其他模式对比

| 特性 | 中介者模式 | 观察者模式 | 外观模式 |
|------|----------|------------|----------|
| 目的 | 协调交互 | 通知变化 | 简化接口 |
| 通信方式 | 双向通信 | 单向通知 | 单向调用 |
| 耦合度 | 解耦对象 | 解耦观察者 | 解耦客户端 |
| 复杂度 | 中等 | 简单 | 简单 |

## 🎯 实战建议

### 1. **何时使用中介者模式**
- 对象间存在复杂的交互关系
- 想要复用对象但交互复杂
- 想要定制一个分布在多个类中的行为
- 对象间的依赖关系混乱且难以理解

### 2. **设计原则**
```java
// 好的中介者设计
interface Mediator {
    void register(Component component);
    void unregister(Component component);
    void notify(Component sender, Event event);
}

// 保持组件简单
abstract class Component {
    protected Mediator mediator;

    // 组件只关注自己的职责
    public abstract void doWork();

    // 通过中介者与其他组件交互
    protected void notifyMediator(Event event) {
        if (mediator != null) {
            mediator.notify(this, event);
        }
    }
}
```

### 3. **避免常见陷阱**
```java
// 避免：中介者知道太多组件细节
class BadMediator implements Mediator {
    public void notify(Component sender, Event event) {
        // 不要直接操作组件的内部状态
        ((ConcreteComponent) sender).setInternalState("new state");
    }
}

// 推荐：使用事件驱动的方式
class GoodMediator implements Mediator {
    public void notify(Component sender, Event event) {
        // 基于事件类型进行路由，不直接操作组件
        routeEvent(event);
    }
}
```

## 🧠 记忆技巧

**口诀：中介协调减耦合**
- **中**介者统一管理
- **介**入对象间交互
- **协**调各方的关系
- **调**节通信的流程
- **减**少直接的依赖
- **耦**合度大大降低
- **合**作更加简洁

**形象比喻：**
中介者模式就像**交通信号灯**：
- 各个方向的车辆（组件）不直接交流
- 信号灯（中介者）协调所有车辆的通行
- 避免了车辆间的混乱和冲突
- 统一管理交通规则

## 🎉 总结

中介者模式是一种强大的设计模式，它通过引入中介者对象来管理对象间的复杂交互。虽然中介者可能变得复杂，但它显著降低了系统的耦合度，提高了代码的可维护性和可重用性。

**核心思想：** 🤝 用中介者来协调对象间的交互，让系统更简洁，关系更清晰！

下一篇我们将学习**备忘录模式**，看看如何优雅地保存和恢复对象状态！ 🚀