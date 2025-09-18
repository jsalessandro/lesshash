---
title: "设计模式详解13：命令模式(Command) - 将请求封装为对象的行为艺术"
date: 2024-12-13T10:13:00+08:00
draft: false
tags: ["设计模式", "命令模式", "Command", "Java", "行为型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解命令模式，从基础概念到高级实现，包含撤销操作、宏命令、命令队列等实战技巧，让你彻底掌握请求对象化的智慧"
---

## 🎯 什么是命令模式？

### 生活中的例子
想象一下**餐厅点餐**的过程：你（客户）不直接告诉厨师（接收者）要做什么菜，而是告诉服务员（调用者）你的需求，服务员把你的需求写在订单上（命令对象），然后把订单传给厨师。订单上清楚地记录了：要做什么菜、桌号、特殊要求等。厨师根据订单制作菜品，如果需要，订单还可以取消。这个**订单**就是一个命令，它封装了请求的所有信息。这就是命令模式的核心思想：**将请求封装为对象，从而可以用不同的请求对客户进行参数化，对请求排队或记录请求日志，以及支持可撤销的操作**。

### 问题背景
在软件开发中，经常遇到需要将操作封装的场景：
- 📱 **GUI应用** - 按钮点击、菜单选择等用户操作
- 🎮 **游戏系统** - 玩家动作、技能释放、撤销操作
- 🏠 **智能家居** - 灯光控制、温度调节、场景切换
- 💾 **文档编辑** - 文本操作的撤销/重做功能
- 🛠️ **任务调度** - 批处理任务、延迟执行、任务队列

如果直接调用接收者的方法，会导致：
- 调用者与接收者紧耦合
- 难以实现撤销功能
- 无法记录操作历史
- 难以实现批量操作

## 🧠 设计思想

### 核心角色
1. **Command（抽象命令）** - 定义执行操作的接口
2. **ConcreteCommand（具体命令）** - 实现具体的操作
3. **Receiver（接收者）** - 知道如何实施与执行一个请求相关的操作
4. **Invoker（调用者）** - 要求该命令执行这个请求
5. **Client（客户端）** - 创建具体命令对象并设置接收者

### 核心思想
- 将请求封装为对象
- 解耦调用者和接收者
- 支持撤销和重做操作
- 支持日志记录和事务处理

### 记忆口诀
> **"请求对象化，调用更灵活，撤销重做易，解耦是王道"**

## 💻 代码实现

### 1. 基础命令模式 - 智能家居控制

```java
/**
 * 抽象命令接口
 */
public interface Command {
    void execute();
    void undo();
    String getDescription();
}

/**
 * 接收者 - 电灯
 */
public class Light {
    private String location;
    private boolean isOn;
    private int brightness; // 亮度 0-100

    public Light(String location) {
        this.location = location;
        this.isOn = false;
        this.brightness = 0;
    }

    public void turnOn() {
        isOn = true;
        brightness = 100;
        System.out.println("💡 " + location + "的灯已打开，亮度: " + brightness + "%");
    }

    public void turnOff() {
        isOn = false;
        brightness = 0;
        System.out.println("💡 " + location + "的灯已关闭");
    }

    public void setBrightness(int brightness) {
        if (brightness < 0) brightness = 0;
        if (brightness > 100) brightness = 100;

        this.brightness = brightness;
        this.isOn = brightness > 0;

        System.out.println("💡 " + location + "的灯亮度调节为: " + brightness + "%" +
                          (isOn ? " (开启)" : " (关闭)"));
    }

    public boolean isOn() { return isOn; }
    public int getBrightness() { return brightness; }
    public String getLocation() { return location; }

    public String getStatus() {
        return location + "的灯: " + (isOn ? "开启" : "关闭") + ", 亮度: " + brightness + "%";
    }
}

/**
 * 接收者 - 空调
 */
public class AirConditioner {
    private String location;
    private boolean isOn;
    private int temperature; // 温度

    public AirConditioner(String location) {
        this.location = location;
        this.isOn = false;
        this.temperature = 25; // 默认25度
    }

    public void turnOn() {
        isOn = true;
        System.out.println("❄️ " + location + "的空调已开启，温度: " + temperature + "°C");
    }

    public void turnOff() {
        isOn = false;
        System.out.println("❄️ " + location + "的空调已关闭");
    }

    public void setTemperature(int temperature) {
        if (temperature < 16) temperature = 16;
        if (temperature > 30) temperature = 30;

        this.temperature = temperature;
        if (isOn) {
            System.out.println("❄️ " + location + "的空调温度调节为: " + temperature + "°C");
        } else {
            System.out.println("❄️ " + location + "的空调温度预设为: " + temperature + "°C (未开启)");
        }
    }

    public boolean isOn() { return isOn; }
    public int getTemperature() { return temperature; }
    public String getLocation() { return location; }

    public String getStatus() {
        return location + "的空调: " + (isOn ? "开启" : "关闭") + ", 温度: " + temperature + "°C";
    }
}

/**
 * 具体命令 - 开灯命令
 */
public class LightOnCommand implements Command {
    private Light light;
    private int previousBrightness;

    public LightOnCommand(Light light) {
        this.light = light;
    }

    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.turnOn();
    }

    @Override
    public void undo() {
        if (previousBrightness > 0) {
            light.setBrightness(previousBrightness);
        } else {
            light.turnOff();
        }
    }

    @Override
    public String getDescription() {
        return "开启" + light.getLocation() + "的灯";
    }
}

/**
 * 具体命令 - 关灯命令
 */
public class LightOffCommand implements Command {
    private Light light;
    private int previousBrightness;

    public LightOffCommand(Light light) {
        this.light = light;
    }

    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.turnOff();
    }

    @Override
    public void undo() {
        if (previousBrightness > 0) {
            light.setBrightness(previousBrightness);
        } else {
            light.turnOn();
        }
    }

    @Override
    public String getDescription() {
        return "关闭" + light.getLocation() + "的灯";
    }
}

/**
 * 具体命令 - 调节灯光亮度命令
 */
public class LightDimCommand implements Command {
    private Light light;
    private int newBrightness;
    private int previousBrightness;

    public LightDimCommand(Light light, int brightness) {
        this.light = light;
        this.newBrightness = brightness;
    }

    @Override
    public void execute() {
        previousBrightness = light.getBrightness();
        light.setBrightness(newBrightness);
    }

    @Override
    public void undo() {
        light.setBrightness(previousBrightness);
    }

    @Override
    public String getDescription() {
        return "调节" + light.getLocation() + "的灯亮度至" + newBrightness + "%";
    }
}

/**
 * 具体命令 - 空调开启命令
 */
public class AirConditionerOnCommand implements Command {
    private AirConditioner airConditioner;
    private boolean previousState;

    public AirConditionerOnCommand(AirConditioner airConditioner) {
        this.airConditioner = airConditioner;
    }

    @Override
    public void execute() {
        previousState = airConditioner.isOn();
        airConditioner.turnOn();
    }

    @Override
    public void undo() {
        if (!previousState) {
            airConditioner.turnOff();
        }
    }

    @Override
    public String getDescription() {
        return "开启" + airConditioner.getLocation() + "的空调";
    }
}

/**
 * 具体命令 - 空调关闭命令
 */
public class AirConditionerOffCommand implements Command {
    private AirConditioner airConditioner;
    private boolean previousState;

    public AirConditionerOffCommand(AirConditioner airConditioner) {
        this.airConditioner = airConditioner;
    }

    @Override
    public void execute() {
        previousState = airConditioner.isOn();
        airConditioner.turnOff();
    }

    @Override
    public void undo() {
        if (previousState) {
            airConditioner.turnOn();
        }
    }

    @Override
    public String getDescription() {
        return "关闭" + airConditioner.getLocation() + "的空调";
    }
}

/**
 * 具体命令 - 空调温度调节命令
 */
public class AirConditionerTempCommand implements Command {
    private AirConditioner airConditioner;
    private int newTemperature;
    private int previousTemperature;

    public AirConditionerTempCommand(AirConditioner airConditioner, int temperature) {
        this.airConditioner = airConditioner;
        this.newTemperature = temperature;
    }

    @Override
    public void execute() {
        previousTemperature = airConditioner.getTemperature();
        airConditioner.setTemperature(newTemperature);
    }

    @Override
    public void undo() {
        airConditioner.setTemperature(previousTemperature);
    }

    @Override
    public String getDescription() {
        return "调节" + airConditioner.getLocation() + "的空调温度至" + newTemperature + "°C";
    }
}

/**
 * 空命令 - 什么都不做
 */
public class NoCommand implements Command {
    @Override
    public void execute() {
        // 什么都不做
    }

    @Override
    public void undo() {
        // 什么都不做
    }

    @Override
    public String getDescription() {
        return "空命令";
    }
}

/**
 * 调用者 - 遥控器
 */
public class RemoteControl {
    private Command[] onCommands;
    private Command[] offCommands;
    private Command lastCommand;
    private int slots;

    public RemoteControl(int slots) {
        this.slots = slots;
        this.onCommands = new Command[slots];
        this.offCommands = new Command[slots];

        // 初始化为空命令
        Command noCommand = new NoCommand();
        for (int i = 0; i < slots; i++) {
            onCommands[i] = noCommand;
            offCommands[i] = noCommand;
        }
        lastCommand = noCommand;
    }

    public void setCommand(int slot, Command onCommand, Command offCommand) {
        if (slot >= 0 && slot < slots) {
            onCommands[slot] = onCommand;
            offCommands[slot] = offCommand;
            System.out.println("📱 遥控器槽位 " + slot + " 已设置命令");
            System.out.println("  ON: " + onCommand.getDescription());
            System.out.println("  OFF: " + offCommand.getDescription());
        }
    }

    public void onButtonPressed(int slot) {
        if (slot >= 0 && slot < slots) {
            System.out.println("📱 按下遥控器 ON 按钮 " + slot);
            onCommands[slot].execute();
            lastCommand = onCommands[slot];
        }
    }

    public void offButtonPressed(int slot) {
        if (slot >= 0 && slot < slots) {
            System.out.println("📱 按下遥控器 OFF 按钮 " + slot);
            offCommands[slot].execute();
            lastCommand = offCommands[slot];
        }
    }

    public void undoButtonPressed() {
        System.out.println("📱 按下撤销按钮");
        lastCommand.undo();
    }

    public void printStatus() {
        System.out.println("\n=== 遥控器状态 ===");
        for (int i = 0; i < slots; i++) {
            System.out.println("槽位 " + i + ": ON=" + onCommands[i].getDescription() +
                             ", OFF=" + offCommands[i].getDescription());
        }
        System.out.println("最后命令: " + lastCommand.getDescription());
    }
}

// 智能家居命令模式演示
public class SmartHomeCommandDemo {
    public static void main(String[] args) {
        System.out.println("=== 智能家居命令模式演示 ===");

        // 创建接收者
        Light livingRoomLight = new Light("客厅");
        Light kitchenLight = new Light("厨房");
        AirConditioner livingRoomAC = new AirConditioner("客厅");

        // 创建命令对象
        Command livingRoomLightOn = new LightOnCommand(livingRoomLight);
        Command livingRoomLightOff = new LightOffCommand(livingRoomLight);
        Command kitchenLightOn = new LightOnCommand(kitchenLight);
        Command kitchenLightOff = new LightOffCommand(kitchenLight);
        Command livingRoomACOn = new AirConditionerOnCommand(livingRoomAC);
        Command livingRoomACOff = new AirConditionerOffCommand(livingRoomAC);

        // 创建调用者
        RemoteControl remote = new RemoteControl(4);

        System.out.println("\n=== 设置遥控器命令 ===");
        remote.setCommand(0, livingRoomLightOn, livingRoomLightOff);
        remote.setCommand(1, kitchenLightOn, kitchenLightOff);
        remote.setCommand(2, livingRoomACOn, livingRoomACOff);

        remote.printStatus();

        System.out.println("\n=== 执行命令 ===");

        // 开启客厅灯
        remote.onButtonPressed(0);
        System.out.println("状态: " + livingRoomLight.getStatus());

        // 开启厨房灯
        remote.onButtonPressed(1);
        System.out.println("状态: " + kitchenLight.getStatus());

        // 关闭客厅灯
        remote.offButtonPressed(0);
        System.out.println("状态: " + livingRoomLight.getStatus());

        // 撤销上一个操作（重新开启客厅灯）
        remote.undoButtonPressed();
        System.out.println("撤销后状态: " + livingRoomLight.getStatus());

        // 开启空调
        remote.onButtonPressed(2);
        System.out.println("状态: " + livingRoomAC.getStatus());

        System.out.println("\n=== 高级命令测试 ===");

        // 创建更复杂的命令
        Command dimLight = new LightDimCommand(livingRoomLight, 30);
        Command setACTemp = new AirConditionerTempCommand(livingRoomAC, 22);

        remote.setCommand(3, dimLight, new LightOffCommand(livingRoomLight));

        // 调节灯光亮度
        remote.onButtonPressed(3);
        System.out.println("状态: " + livingRoomLight.getStatus());

        // 撤销亮度调节
        remote.undoButtonPressed();
        System.out.println("撤销后状态: " + livingRoomLight.getStatus());

        // 直接执行温度调节命令
        System.out.println("\n=== 直接执行命令 ===");
        System.out.println("执行命令: " + setACTemp.getDescription());
        setACTemp.execute();
        System.out.println("状态: " + livingRoomAC.getStatus());

        System.out.println("\n撤销温度调节:");
        setACTemp.undo();
        System.out.println("状态: " + livingRoomAC.getStatus());

        System.out.println("\n=== 命令模式的优势 ===");
        System.out.println("✅ 解耦：遥控器不需要知道具体设备如何工作");
        System.out.println("✅ 扩展：可以轻松添加新的设备和命令");
        System.out.println("✅ 撤销：支持操作的撤销功能");
        System.out.println("✅ 日志：可以记录所有执行的命令");
        System.out.println("✅ 宏命令：可以组合多个命令");
    }
}
```

### 2. 宏命令 - 场景模式

```java
/**
 * 宏命令 - 组合多个命令
 */
public class MacroCommand implements Command {
    private Command[] commands;
    private String description;

    public MacroCommand(Command[] commands, String description) {
        this.commands = commands;
        this.description = description;
    }

    @Override
    public void execute() {
        System.out.println("🎬 执行宏命令: " + description);
        for (Command command : commands) {
            System.out.print("  ");
            command.execute();
        }
    }

    @Override
    public void undo() {
        System.out.println("🎬 撤销宏命令: " + description);
        // 反向撤销所有命令
        for (int i = commands.length - 1; i >= 0; i--) {
            System.out.print("  ");
            commands[i].undo();
        }
    }

    @Override
    public String getDescription() {
        return "宏命令: " + description;
    }
}

/**
 * 智能家居场景管理器
 */
public class SmartHomeSceneManager {
    private Map<String, MacroCommand> scenes;

    public SmartHomeSceneManager() {
        this.scenes = new HashMap<>();
    }

    public void createScene(String sceneName, Command[] commands) {
        MacroCommand scene = new MacroCommand(commands, sceneName);
        scenes.put(sceneName, scene);
        System.out.println("🏠 创建场景: " + sceneName);
    }

    public void activateScene(String sceneName) {
        MacroCommand scene = scenes.get(sceneName);
        if (scene != null) {
            System.out.println("🏠 激活场景: " + sceneName);
            scene.execute();
        } else {
            System.out.println("❌ 场景不存在: " + sceneName);
        }
    }

    public void deactivateScene(String sceneName) {
        MacroCommand scene = scenes.get(sceneName);
        if (scene != null) {
            System.out.println("🏠 取消场景: " + sceneName);
            scene.undo();
        } else {
            System.out.println("❌ 场景不存在: " + sceneName);
        }
    }

    public void listScenes() {
        System.out.println("=== 可用场景 ===");
        for (String sceneName : scenes.keySet()) {
            System.out.println("  " + sceneName);
        }
    }
}

// 智能家居场景演示
public class SmartHomeSceneDemo {
    public static void main(String[] args) {
        System.out.println("=== 智能家居场景宏命令演示 ===");

        // 创建设备
        Light livingRoomLight = new Light("客厅");
        Light bedroomLight = new Light("卧室");
        AirConditioner livingRoomAC = new AirConditioner("客厅");
        AirConditioner bedroomAC = new AirConditioner("卧室");

        // 创建场景管理器
        SmartHomeSceneManager sceneManager = new SmartHomeSceneManager();

        System.out.println("\n=== 创建观影场景 ===");
        Command[] movieCommands = {
            new LightDimCommand(livingRoomLight, 20),  // 客厅灯调暗
            new LightOffCommand(bedroomLight),         // 关闭卧室灯
            new AirConditionerOnCommand(livingRoomAC), // 开启客厅空调
            new AirConditionerTempCommand(livingRoomAC, 24) // 设置适宜温度
        };
        sceneManager.createScene("观影模式", movieCommands);

        System.out.println("\n=== 创建睡眠场景 ===");
        Command[] sleepCommands = {
            new LightOffCommand(livingRoomLight),      // 关闭客厅灯
            new LightOffCommand(bedroomLight),         // 关闭卧室灯
            new AirConditionerOffCommand(livingRoomAC), // 关闭客厅空调
            new AirConditionerOnCommand(bedroomAC),    // 开启卧室空调
            new AirConditionerTempCommand(bedroomAC, 26) // 设置睡眠温度
        };
        sceneManager.createScene("睡眠模式", sleepCommands);

        System.out.println("\n=== 创建回家场景 ===");
        Command[] homeCommands = {
            new LightOnCommand(livingRoomLight),       // 开启客厅灯
            new LightDimCommand(bedroomLight, 50),     // 卧室灯调至50%
            new AirConditionerOnCommand(livingRoomAC), // 开启客厅空调
            new AirConditionerTempCommand(livingRoomAC, 23) // 设置舒适温度
        };
        sceneManager.createScene("回家模式", homeCommands);

        sceneManager.listScenes();

        System.out.println("\n=== 激活观影场景 ===");
        sceneManager.activateScene("观影模式");

        System.out.println("\n当前设备状态:");
        System.out.println(livingRoomLight.getStatus());
        System.out.println(bedroomLight.getStatus());
        System.out.println(livingRoomAC.getStatus());
        System.out.println(bedroomAC.getStatus());

        System.out.println("\n=== 切换到睡眠场景 ===");
        sceneManager.deactivateScene("观影模式"); // 先取消当前场景
        sceneManager.activateScene("睡眠模式");

        System.out.println("\n当前设备状态:");
        System.out.println(livingRoomLight.getStatus());
        System.out.println(bedroomLight.getStatus());
        System.out.println(livingRoomAC.getStatus());
        System.out.println(bedroomAC.getStatus());

        System.out.println("\n=== 激活回家场景 ===");
        sceneManager.deactivateScene("睡眠模式");
        sceneManager.activateScene("回家模式");

        System.out.println("\n最终设备状态:");
        System.out.println(livingRoomLight.getStatus());
        System.out.println(bedroomLight.getStatus());
        System.out.println(livingRoomAC.getStatus());
        System.out.println(bedroomAC.getStatus());

        System.out.println("\n=== 宏命令的优势 ===");
        System.out.println("✅ 一键执行多个操作");
        System.out.println("✅ 场景化管理，用户体验好");
        System.out.println("✅ 支持场景的整体撤销");
        System.out.println("✅ 可以组合任意命令");
    }
}
```

### 3. 命令队列与日志

```java
/**
 * 命令历史记录
 */
public class CommandHistory {
    private List<Command> history;
    private int currentPosition;
    private int maxSize;

    public CommandHistory(int maxSize) {
        this.history = new ArrayList<>();
        this.currentPosition = -1;
        this.maxSize = maxSize;
    }

    public void addCommand(Command command) {
        // 如果当前位置不是最后，删除后面的命令（支持分支撤销）
        if (currentPosition < history.size() - 1) {
            history.subList(currentPosition + 1, history.size()).clear();
        }

        // 添加新命令
        history.add(command);
        currentPosition++;

        // 保持历史记录大小限制
        if (history.size() > maxSize) {
            history.remove(0);
            currentPosition--;
        }

        System.out.println("📝 命令已记录: " + command.getDescription());
    }

    public boolean canUndo() {
        return currentPosition >= 0;
    }

    public boolean canRedo() {
        return currentPosition < history.size() - 1;
    }

    public Command undo() {
        if (canUndo()) {
            Command command = history.get(currentPosition);
            currentPosition--;
            System.out.println("↶ 撤销命令: " + command.getDescription());
            return command;
        }
        return null;
    }

    public Command redo() {
        if (canRedo()) {
            currentPosition++;
            Command command = history.get(currentPosition);
            System.out.println("↷ 重做命令: " + command.getDescription());
            return command;
        }
        return null;
    }

    public void printHistory() {
        System.out.println("=== 命令历史 ===");
        for (int i = 0; i < history.size(); i++) {
            String marker = (i == currentPosition) ? " -> " : "    ";
            System.out.println(marker + i + ": " + history.get(i).getDescription());
        }
        System.out.println("可撤销: " + canUndo() + ", 可重做: " + canRedo());
    }

    public List<Command> getHistory() {
        return new ArrayList<>(history);
    }

    public void clear() {
        history.clear();
        currentPosition = -1;
        System.out.println("📝 命令历史已清空");
    }
}

/**
 * 命令队列处理器
 */
public class CommandQueue {
    private Queue<Command> commandQueue;
    private boolean isProcessing;
    private Thread processingThread;

    public CommandQueue() {
        this.commandQueue = new LinkedList<>();
        this.isProcessing = false;
    }

    public void enqueue(Command command) {
        synchronized (commandQueue) {
            commandQueue.offer(command);
            System.out.println("📬 命令入队: " + command.getDescription() + " (队列长度: " + commandQueue.size() + ")");
            commandQueue.notifyAll();
        }
    }

    public void startProcessing() {
        if (isProcessing) {
            System.out.println("⚠️ 命令队列已在处理中");
            return;
        }

        isProcessing = true;
        processingThread = new Thread(() -> {
            System.out.println("🚀 开始处理命令队列");

            while (isProcessing) {
                Command command = null;

                synchronized (commandQueue) {
                    while (commandQueue.isEmpty() && isProcessing) {
                        try {
                            commandQueue.wait();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            return;
                        }
                    }

                    if (!commandQueue.isEmpty()) {
                        command = commandQueue.poll();
                    }
                }

                if (command != null) {
                    try {
                        System.out.println("⚡ 执行队列命令: " + command.getDescription());
                        command.execute();
                        Thread.sleep(500); // 模拟命令执行时间
                    } catch (Exception e) {
                        System.out.println("❌ 命令执行失败: " + e.getMessage());
                    }
                }
            }

            System.out.println("🛑 命令队列处理已停止");
        });

        processingThread.start();
    }

    public void stopProcessing() {
        isProcessing = false;
        synchronized (commandQueue) {
            commandQueue.notifyAll();
        }

        if (processingThread != null) {
            try {
                processingThread.join(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public int getQueueSize() {
        synchronized (commandQueue) {
            return commandQueue.size();
        }
    }

    public boolean isEmpty() {
        synchronized (commandQueue) {
            return commandQueue.isEmpty();
        }
    }
}

/**
 * 高级智能家居控制器
 */
public class AdvancedSmartHomeController {
    private CommandHistory history;
    private CommandQueue commandQueue;
    private Map<String, Command> savedCommands;

    public AdvancedSmartHomeController() {
        this.history = new CommandHistory(20);
        this.commandQueue = new CommandQueue();
        this.savedCommands = new HashMap<>();
        this.commandQueue.startProcessing();
    }

    public void executeCommand(Command command) {
        command.execute();
        history.addCommand(command);
    }

    public void executeCommandAsync(Command command) {
        commandQueue.enqueue(command);
        history.addCommand(command);
    }

    public void undo() {
        Command command = history.undo();
        if (command != null) {
            command.undo();
        } else {
            System.out.println("❌ 没有可撤销的命令");
        }
    }

    public void redo() {
        Command command = history.redo();
        if (command != null) {
            command.execute();
        } else {
            System.out.println("❌ 没有可重做的命令");
        }
    }

    public void saveCommand(String name, Command command) {
        savedCommands.put(name, command);
        System.out.println("💾 命令已保存: " + name + " -> " + command.getDescription());
    }

    public void loadCommand(String name) {
        Command command = savedCommands.get(name);
        if (command != null) {
            executeCommand(command);
        } else {
            System.out.println("❌ 未找到保存的命令: " + name);
        }
    }

    public void printStatus() {
        history.printHistory();
        System.out.println("队列长度: " + commandQueue.getQueueSize());
        System.out.println("保存的命令: " + savedCommands.keySet());
    }

    public void shutdown() {
        commandQueue.stopProcessing();
        System.out.println("🏠 智能家居控制器已关闭");
    }
}

// 高级命令控制演示
public class AdvancedCommandDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 高级命令控制演示 ===");

        // 创建设备
        Light livingRoomLight = new Light("客厅");
        AirConditioner ac = new AirConditioner("客厅");

        // 创建高级控制器
        AdvancedSmartHomeController controller = new AdvancedSmartHomeController();

        System.out.println("\n=== 执行一系列命令 ===");

        // 执行命令
        controller.executeCommand(new LightOnCommand(livingRoomLight));
        controller.executeCommand(new LightDimCommand(livingRoomLight, 60));
        controller.executeCommand(new AirConditionerOnCommand(ac));
        controller.executeCommand(new AirConditionerTempCommand(ac, 22));

        System.out.println("\n当前状态:");
        System.out.println(livingRoomLight.getStatus());
        System.out.println(ac.getStatus());

        System.out.println("\n=== 撤销重做操作 ===");
        controller.undo(); // 撤销温度设置
        System.out.println(ac.getStatus());

        controller.undo(); // 撤销空调开启
        System.out.println(ac.getStatus());

        controller.redo(); // 重做空调开启
        System.out.println(ac.getStatus());

        controller.printStatus();

        System.out.println("\n=== 保存和加载命令 ===");
        Command favoriteScene = new MacroCommand(new Command[]{
            new LightDimCommand(livingRoomLight, 40),
            new AirConditionerTempCommand(ac, 24)
        }, "我的最爱场景");

        controller.saveCommand("favorite", favoriteScene);
        controller.loadCommand("favorite");

        System.out.println("\n=== 异步命令队列 ===");
        System.out.println("添加命令到队列:");

        controller.executeCommandAsync(new LightDimCommand(livingRoomLight, 80));
        controller.executeCommandAsync(new LightDimCommand(livingRoomLight, 60));
        controller.executeCommandAsync(new LightDimCommand(livingRoomLight, 40));
        controller.executeCommandAsync(new LightDimCommand(livingRoomLight, 20));

        System.out.println("等待队列处理完成...");
        Thread.sleep(3000);

        System.out.println("\n最终状态:");
        System.out.println(livingRoomLight.getStatus());

        controller.printStatus();

        System.out.println("\n=== 命令模式高级特性总结 ===");
        System.out.println("✅ 命令历史：支持撤销/重做");
        System.out.println("✅ 命令队列：支持异步执行");
        System.out.println("✅ 命令保存：支持场景保存和加载");
        System.out.println("✅ 宏命令：支持复合操作");
        System.out.println("✅ 日志记录：支持操作审计");

        // 关闭控制器
        controller.shutdown();
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **解耦调用者和接收者**
   - 调用者不需要知道接收者的具体实现
   - 降低系统耦合度

2. **支持撤销操作**
   - 每个命令可以实现撤销逻辑
   - 支持多级撤销和重做

3. **支持日志和事务**
   - 可以记录所有执行的命令
   - 支持批量操作和事务回滚

4. **易于扩展**
   - 新增命令无需修改现有代码
   - 符合开闭原则

5. **支持宏命令**
   - 可以组合多个命令
   - 实现复杂的业务操作

### ❌ 缺点

1. **增加系统复杂性**
   - 每个操作都需要创建命令类
   - 类的数量可能急剧增加

2. **内存开销**
   - 需要存储命令对象
   - 历史记录可能占用大量内存

3. **设计复杂**
   - 需要仔细设计命令的粒度
   - 撤销逻辑可能很复杂

## 🎯 使用场景总结

### 适合使用命令模式的场景：
- 📱 **GUI应用** - 菜单操作、工具栏按钮的撤销重做
- 📝 **文档编辑器** - 文本操作的撤销重做功能
- 🎮 **游戏系统** - 玩家操作记录、回放系统
- 🏠 **智能家居** - 设备控制、场景模式
- 📊 **事务处理** - 数据库事务、批处理操作

### 不适合使用命令模式的场景：
- 简单的直接调用
- 不需要撤销功能的操作
- 实时性要求极高的场景
- 内存资源极其有限的环境

## 🧠 记忆技巧

### 形象比喻
> **命令模式就像是 "餐厅订单"**：
> - 客户不直接和厨师交流（解耦调用者和接收者）
> - 订单记录了所有信息（请求对象化）
> - 订单可以取消（支持撤销）
> - 可以批量处理订单（宏命令）

### 设计要点
> **"请求对象化，解耦调用者，支持撤销重做，记录操作历史"**

### 与策略模式的区别
- **命令模式**：关注请求的封装和执行控制
- **策略模式**：关注算法的封装和选择

## 🔧 最佳实践

### 1. 命令工厂模式

```java
/**
 * 命令工厂
 */
public class CommandFactory {
    public static Command createCommand(String type, Object receiver, Object... params) {
        switch (type.toLowerCase()) {
            case "light_on":
                return new LightOnCommand((Light) receiver);
            case "light_off":
                return new LightOffCommand((Light) receiver);
            case "light_dim":
                return new LightDimCommand((Light) receiver, (Integer) params[0]);
            case "ac_on":
                return new AirConditionerOnCommand((AirConditioner) receiver);
            case "ac_off":
                return new AirConditionerOffCommand((AirConditioner) receiver);
            default:
                throw new IllegalArgumentException("未知命令类型: " + type);
        }
    }
}
```

### 2. 命令注解

```java
/**
 * 命令注解
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface CommandInfo {
    String name();
    String description();
    boolean undoable() default true;
}

@CommandInfo(name = "light_on", description = "开灯命令")
public class LightOnCommand implements Command {
    // 实现...
}
```

### 3. 命令拦截器

```java
/**
 * 命令拦截器
 */
public interface CommandInterceptor {
    boolean preExecute(Command command);
    void postExecute(Command command, boolean success);
}

public class LoggingInterceptor implements CommandInterceptor {
    @Override
    public boolean preExecute(Command command) {
        System.out.println("准备执行: " + command.getDescription());
        return true;
    }

    @Override
    public void postExecute(Command command, boolean success) {
        System.out.println("执行完成: " + command.getDescription() +
                          " 结果: " + (success ? "成功" : "失败"));
    }
}
```

## 🚀 总结

命令模式通过将请求封装为对象，实现了调用者与接收者的解耦，特别适用于：

- **需要撤销重做功能**的场景
- **需要日志记录**的系统
- **需要批量操作**的业务
- **GUI事件处理**

核心思想：
- **请求对象化**
- **解耦调用者和接收者**
- **支持撤销和重做**
- **支持命令的组合和队列**

设计要点：
- **合理设计命令粒度**
- **实现可靠的撤销逻辑**
- **考虑内存使用优化**
- **提供命令的组合机制**

记住，**命令模式是行为封装器，不是万能控制器**，要在合适的请求处理场景下使用！

---
*下一篇：责任链模式 - 请求处理的链式传递*