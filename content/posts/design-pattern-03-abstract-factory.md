---
title: "设计模式详解03：抽象工厂模式(Abstract Factory) - 产品家族的统一创建"
date: 2024-12-03T10:03:00+08:00
draft: false
tags: ["设计模式", "抽象工厂模式", "Abstract Factory", "Java", "创建型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解抽象工厂模式，通过生动的GUI主题和汽车制造例子，让你轻松掌握产品族创建的最佳实践"
---

## 🎯 什么是抽象工厂模式？

### 生活中的例子
想象你要装修房子，需要选择一个风格主题：

**现代简约风**：现代沙发 + 简约茶几 + 极简灯具
**中式古典风**：红木沙发 + 古典茶几 + 宫灯
**北欧风格**：布艺沙发 + 木质茶几 + 工业灯具

每种风格都是一个**产品家族**，家族内的产品需要**相互匹配**。你不会想要现代沙发配古典茶几，那样会很奇怪！

这就是抽象工厂模式：**为创建一系列相关或相互依赖的对象提供接口，而无需指定它们具体的类**。

## 🧠 设计思想

### 核心概念
- **抽象工厂**：定义创建产品家族的接口
- **具体工厂**：实现创建具体产品家族
- **抽象产品**：定义产品的接口
- **具体产品**：实现具体的产品
- **产品家族**：一组相关的产品

### 与工厂方法的区别
- **工厂方法**：创建一种产品的不同实现
- **抽象工厂**：创建多种相关产品的不同实现

### 记忆口诀
> **"家族产品成套造，风格统一不混淆，抽象工厂定接口，具体实现各不同"**

## 💻 代码实现

### 经典实现：GUI 主题工厂

```java
// === 抽象产品接口 ===

// 按钮产品族
interface Button {
    void render();
    void onClick();
    String getStyle();
}

// 复选框产品族
interface Checkbox {
    void render();
    void toggle();
    String getStyle();
}

// 文本框产品族
interface TextField {
    void render();
    void setText(String text);
    String getText();
    String getStyle();
}

// === Windows 风格产品族 ===

class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 Windows 风格按钮 [确定]");
    }

    @Override
    public void onClick() {
        System.out.println("Windows 按钮点击效果：立体按下");
    }

    @Override
    public String getStyle() {
        return "Windows 经典风格";
    }
}

class WindowsCheckbox implements Checkbox {
    private boolean checked = false;

    @Override
    public void render() {
        String state = checked ? "☑" : "☐";
        System.out.println("渲染 Windows 复选框 " + state + " 同意条款");
    }

    @Override
    public void toggle() {
        checked = !checked;
        System.out.println("Windows 复选框状态切换：" + (checked ? "已选中" : "未选中"));
    }

    @Override
    public String getStyle() {
        return "Windows 方形复选框";
    }
}

class WindowsTextField implements TextField {
    private String text = "";

    @Override
    public void render() {
        System.out.println("渲染 Windows 文本框: [" + text + "]");
    }

    @Override
    public void setText(String text) {
        this.text = text;
        System.out.println("Windows 文本框输入：" + text);
    }

    @Override
    public String getText() {
        return text;
    }

    @Override
    public String getStyle() {
        return "Windows 内嵌边框文本框";
    }
}

// === macOS 风格产品族 ===

class MacOSButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 macOS 风格按钮 (确定)");
    }

    @Override
    public void onClick() {
        System.out.println("macOS 按钮点击效果：优雅渐变");
    }

    @Override
    public String getStyle() {
        return "macOS Aqua 风格";
    }
}

class MacOSCheckbox implements Checkbox {
    private boolean checked = false;

    @Override
    public void render() {
        String state = checked ? "✓" : "○";
        System.out.println("渲染 macOS 复选框 " + state + " 同意条款");
    }

    @Override
    public void toggle() {
        checked = !checked;
        System.out.println("macOS 复选框状态切换：" + (checked ? "优雅选中" : "平滑取消"));
    }

    @Override
    public String getStyle() {
        return "macOS 圆形复选框";
    }
}

class MacOSTextField implements TextField {
    private String text = "";

    @Override
    public void render() {
        System.out.println("渲染 macOS 文本框: (" + text + ")");
    }

    @Override
    public void setText(String text) {
        this.text = text;
        System.out.println("macOS 文本框输入：" + text);
    }

    @Override
    public String getText() {
        return text;
    }

    @Override
    public String getStyle() {
        return "macOS 圆角边框文本框";
    }
}

// === Linux 风格产品族 ===

class LinuxButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 Linux GTK 按钮 <确定>");
    }

    @Override
    public void onClick() {
        System.out.println("Linux 按钮点击效果：简单高亮");
    }

    @Override
    public String getStyle() {
        return "GTK 主题风格";
    }
}

class LinuxCheckbox implements Checkbox {
    private boolean checked = false;

    @Override
    public void render() {
        String state = checked ? "[×]" : "[ ]";
        System.out.println("渲染 Linux 复选框 " + state + " 同意条款");
    }

    @Override
    public void toggle() {
        checked = !checked;
        System.out.println("Linux 复选框状态切换：" + (checked ? "已勾选" : "已清空"));
    }

    @Override
    public String getStyle() {
        return "GTK 方形复选框";
    }
}

class LinuxTextField implements TextField {
    private String text = "";

    @Override
    public void render() {
        System.out.println("渲染 Linux 文本框: {" + text + "}");
    }

    @Override
    public void setText(String text) {
        this.text = text;
        System.out.println("Linux 文本框输入：" + text);
    }

    @Override
    public String getText() {
        return text;
    }

    @Override
    public String getStyle() {
        return "GTK 平直边框文本框";
    }
}

// === 抽象工厂接口 ===

abstract class GUIFactory {
    // 创建产品家族的方法
    public abstract Button createButton();
    public abstract Checkbox createCheckbox();
    public abstract TextField createTextField();

    // 静态工厂方法 - 根据操作系统创建对应工厂
    public static GUIFactory getFactory(String osType) {
        switch (osType.toLowerCase()) {
            case "windows":
                return new WindowsFactory();
            case "macos":
                return new MacOSFactory();
            case "linux":
                return new LinuxFactory();
            default:
                throw new IllegalArgumentException("不支持的操作系统类型: " + osType);
        }
    }

    // 便捷方法 - 自动检测操作系统
    public static GUIFactory getFactory() {
        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win")) {
            return new WindowsFactory();
        } else if (os.contains("mac")) {
            return new MacOSFactory();
        } else {
            return new LinuxFactory();
        }
    }
}

// === 具体工厂实现 ===

class WindowsFactory extends GUIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }

    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }

    @Override
    public TextField createTextField() {
        return new WindowsTextField();
    }
}

class MacOSFactory extends GUIFactory {
    @Override
    public Button createButton() {
        return new MacOSButton();
    }

    @Override
    public Checkbox createCheckbox() {
        return new MacOSCheckbox();
    }

    @Override
    public TextField createTextField() {
        return new MacOSTextField();
    }
}

class LinuxFactory extends GUIFactory {
    @Override
    public Button createButton() {
        return new LinuxButton();
    }

    @Override
    public Checkbox createCheckbox() {
        return new LinuxCheckbox();
    }

    @Override
    public TextField createTextField() {
        return new LinuxTextField();
    }
}

// === 应用程序类 ===

class Application {
    private Button button;
    private Checkbox checkbox;
    private TextField textField;

    public Application(GUIFactory factory) {
        // 使用工厂创建整个产品家族
        button = factory.createButton();
        checkbox = factory.createCheckbox();
        textField = factory.createTextField();
    }

    public void createUI() {
        System.out.println("=== 创建用户界面 ===");
        button.render();
        checkbox.render();
        textField.render();

        System.out.println("\n界面风格统一性检查：");
        System.out.println("按钮风格：" + button.getStyle());
        System.out.println("复选框风格：" + checkbox.getStyle());
        System.out.println("文本框风格：" + textField.getStyle());
    }

    public void simulateUserInteraction() {
        System.out.println("\n=== 模拟用户交互 ===");

        textField.setText("Hello World");
        checkbox.toggle();
        button.onClick();

        System.out.println("文本框内容：" + textField.getText());
    }
}
```

### 使用示例

```java
public class AbstractFactoryDemo {
    public static void main(String[] args) {
        System.out.println("当前操作系统：" + System.getProperty("os.name"));

        // 自动检测操作系统并创建对应的工厂
        System.out.println("\n=== 自动检测操作系统 ===");
        GUIFactory autoFactory = GUIFactory.getFactory();
        Application autoApp = new Application(autoFactory);
        autoApp.createUI();
        autoApp.simulateUserInteraction();

        // 手动指定不同的操作系统风格
        System.out.println("\n" + "=".repeat(50));
        System.out.println("=== 演示不同操作系统风格 ===");

        String[] systems = {"windows", "macos", "linux"};

        for (String system : systems) {
            System.out.println("\n>>> " + system.toUpperCase() + " 风格 <<<");
            GUIFactory factory = GUIFactory.getFactory(system);
            Application app = new Application(factory);
            app.createUI();
        }
    }
}
```

## 🌟 实际应用场景

### 1. 汽车制造工厂

```java
// === 汽车零部件抽象产品 ===

interface Engine {
    void start();
    void stop();
    String getType();
    int getPower();
}

interface Wheel {
    void rotate();
    String getSize();
    String getMaterial();
}

interface Interior {
    void configure();
    String getStyle();
    String getMaterial();
}

// === 豪华车产品族 ===

class LuxuryEngine implements Engine {
    @Override
    public void start() {
        System.out.println("豪华V8引擎启动 - 声音低沉有力");
    }

    @Override
    public void stop() {
        System.out.println("豪华引擎停止 - 静音模式");
    }

    @Override
    public String getType() {
        return "V8涡轮增压引擎";
    }

    @Override
    public int getPower() {
        return 500; // 500马力
    }
}

class LuxuryWheel implements Wheel {
    @Override
    public void rotate() {
        System.out.println("合金轮毂平滑转动");
    }

    @Override
    public String getSize() {
        return "20寸";
    }

    @Override
    public String getMaterial() {
        return "锻造合金";
    }
}

class LuxuryInterior implements Interior {
    @Override
    public void configure() {
        System.out.println("配置豪华内饰：真皮座椅、实木装饰、氛围灯");
    }

    @Override
    public String getStyle() {
        return "奢华商务风格";
    }

    @Override
    public String getMaterial() {
        return "意大利真皮 + 胡桃木";
    }
}

// === 经济型车产品族 ===

class EconomyEngine implements Engine {
    @Override
    public void start() {
        System.out.println("经济型4缸引擎启动 - 节能环保");
    }

    @Override
    public void stop() {
        System.out.println("经济型引擎停止");
    }

    @Override
    public String getType() {
        return "1.6L自然吸气引擎";
    }

    @Override
    public int getPower() {
        return 120; // 120马力
    }
}

class EconomyWheel implements Wheel {
    @Override
    public void rotate() {
        System.out.println("钢制轮毂稳定转动");
    }

    @Override
    public String getSize() {
        return "16寸";
    }

    @Override
    public String getMaterial() {
        return "钢制";
    }
}

class EconomyInterior implements Interior {
    @Override
    public void configure() {
        System.out.println("配置经济内饰：织物座椅、塑料装饰");
    }

    @Override
    public String getStyle() {
        return "简约实用风格";
    }

    @Override
    public String getMaterial() {
        return "织物 + 硬塑料";
    }
}

// === 运动型车产品族 ===

class SportEngine implements Engine {
    @Override
    public void start() {
        System.out.println("运动引擎启动 - 轰鸣咆哮");
    }

    @Override
    public void stop() {
        System.out.println("运动引擎停止 - 余音绕梁");
    }

    @Override
    public String getType() {
        return "2.0T高性能引擎";
    }

    @Override
    public int getPower() {
        return 350; // 350马力
    }
}

class SportWheel implements Wheel {
    @Override
    public void rotate() {
        System.out.println("运动轮毂高速转动");
    }

    @Override
    public String getSize() {
        return "19寸";
    }

    @Override
    public String getMaterial() {
        return "碳纤维";
    }
}

class SportInterior implements Interior {
    @Override
    public void configure() {
        System.out.println("配置运动内饰：赛车座椅、碳纤维装饰、运动仪表");
    }

    @Override
    public String getStyle() {
        return "激进运动风格";
    }

    @Override
    public String getMaterial() {
        return "Alcantara + 碳纤维";
    }
}

// === 汽车工厂抽象类 ===

abstract class CarFactory {
    // 创建汽车产品家族
    public abstract Engine createEngine();
    public abstract Wheel createWheel();
    public abstract Interior createInterior();

    // 模板方法 - 装配汽车
    public Car assembleCar(String model) {
        System.out.println("\n开始装配 " + model + "...");

        Engine engine = createEngine();
        Wheel wheel = createWheel();
        Interior interior = createInterior();

        Car car = new Car(model, engine, wheel, interior);

        System.out.println("装配完成！");
        return car;
    }

    // 静态工厂方法
    public static CarFactory getFactory(String carType) {
        switch (carType.toLowerCase()) {
            case "luxury":
                return new LuxuryCarFactory();
            case "economy":
                return new EconomyCarFactory();
            case "sport":
                return new SportCarFactory();
            default:
                throw new IllegalArgumentException("未知的汽车类型: " + carType);
        }
    }
}

// === 具体汽车工厂 ===

class LuxuryCarFactory extends CarFactory {
    @Override
    public Engine createEngine() {
        return new LuxuryEngine();
    }

    @Override
    public Wheel createWheel() {
        return new LuxuryWheel();
    }

    @Override
    public Interior createInterior() {
        return new LuxuryInterior();
    }
}

class EconomyCarFactory extends CarFactory {
    @Override
    public Engine createEngine() {
        return new EconomyEngine();
    }

    @Override
    public Wheel createWheel() {
        return new EconomyWheel();
    }

    @Override
    public Interior createInterior() {
        return new EconomyInterior();
    }
}

class SportCarFactory extends CarFactory {
    @Override
    public Engine createEngine() {
        return new SportEngine();
    }

    @Override
    public Wheel createWheel() {
        return new SportWheel();
    }

    @Override
    public Interior createInterior() {
        return new SportInterior();
    }
}

// === 汽车类 ===

class Car {
    private String model;
    private Engine engine;
    private Wheel wheel;
    private Interior interior;

    public Car(String model, Engine engine, Wheel wheel, Interior interior) {
        this.model = model;
        this.engine = engine;
        this.wheel = wheel;
        this.interior = interior;
    }

    public void showSpecs() {
        System.out.println("\n=== " + model + " 规格信息 ===");
        System.out.println("引擎：" + engine.getType() + " (" + engine.getPower() + "马力)");
        System.out.println("轮毂：" + wheel.getSize() + " " + wheel.getMaterial() + "轮毂");
        System.out.println("内饰：" + interior.getStyle() + " (" + interior.getMaterial() + ")");
    }

    public void startCar() {
        System.out.println("\n=== 启动 " + model + " ===");
        interior.configure();
        engine.start();
        wheel.rotate();
        System.out.println(model + " 启动完成，准备出发！");
    }

    public void stopCar() {
        System.out.println("\n=== 停止 " + model + " ===");
        engine.stop();
        System.out.println(model + " 已停止");
    }
}

// 使用示例
public class CarFactoryDemo {
    public static void main(String[] args) {
        String[] carTypes = {"luxury", "economy", "sport"};
        String[] modelNames = {"奔驰S级", "丰田卡罗拉", "保时捷911"};

        for (int i = 0; i < carTypes.length; i++) {
            CarFactory factory = CarFactory.getFactory(carTypes[i]);
            Car car = factory.assembleCar(modelNames[i]);

            car.showSpecs();
            car.startCar();
            car.stopCar();

            System.out.println("\n" + "=".repeat(60));
        }
    }
}
```

### 2. 数据库访问工厂

```java
// === 数据库访问抽象产品 ===

interface Connection {
    void connect();
    void disconnect();
    String getConnectionInfo();
}

interface Command {
    void execute(String sql);
    String getDialect();
}

interface Transaction {
    void begin();
    void commit();
    void rollback();
    String getIsolationLevel();
}

// === MySQL 产品族 ===

class MySQLConnection implements Connection {
    private String host;
    private String database;

    public MySQLConnection(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public void connect() {
        System.out.println("连接到 MySQL 数据库：mysql://" + host + "/" + database);
    }

    @Override
    public void disconnect() {
        System.out.println("断开 MySQL 连接");
    }

    @Override
    public String getConnectionInfo() {
        return "MySQL Connection - " + host + "/" + database;
    }
}

class MySQLCommand implements Command {
    @Override
    public void execute(String sql) {
        System.out.println("MySQL 执行：" + sql);
        System.out.println("使用 MySQL 优化器处理查询");
    }

    @Override
    public String getDialect() {
        return "MySQL SQL 方言";
    }
}

class MySQLTransaction implements Transaction {
    @Override
    public void begin() {
        System.out.println("MySQL 开始事务：START TRANSACTION");
    }

    @Override
    public void commit() {
        System.out.println("MySQL 提交事务：COMMIT");
    }

    @Override
    public void rollback() {
        System.out.println("MySQL 回滚事务：ROLLBACK");
    }

    @Override
    public String getIsolationLevel() {
        return "REPEATABLE READ";
    }
}

// === PostgreSQL 产品族 ===

class PostgreSQLConnection implements Connection {
    private String host;
    private String database;

    public PostgreSQLConnection(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public void connect() {
        System.out.println("连接到 PostgreSQL 数据库：postgresql://" + host + "/" + database);
    }

    @Override
    public void disconnect() {
        System.out.println("断开 PostgreSQL 连接");
    }

    @Override
    public String getConnectionInfo() {
        return "PostgreSQL Connection - " + host + "/" + database;
    }
}

class PostgreSQLCommand implements Command {
    @Override
    public void execute(String sql) {
        System.out.println("PostgreSQL 执行：" + sql);
        System.out.println("使用 PostgreSQL 查询规划器优化");
    }

    @Override
    public String getDialect() {
        return "PostgreSQL SQL 方言";
    }
}

class PostgreSQLTransaction implements Transaction {
    @Override
    public void begin() {
        System.out.println("PostgreSQL 开始事务：BEGIN");
    }

    @Override
    public void commit() {
        System.out.println("PostgreSQL 提交事务：COMMIT");
    }

    @Override
    public void rollback() {
        System.out.println("PostgreSQL 回滚事务：ROLLBACK");
    }

    @Override
    public String getIsolationLevel() {
        return "READ COMMITTED";
    }
}

// === Oracle 产品族 ===

class OracleConnection implements Connection {
    private String host;
    private String database;

    public OracleConnection(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public void connect() {
        System.out.println("连接到 Oracle 数据库：oracle://" + host + "/" + database);
    }

    @Override
    public void disconnect() {
        System.out.println("断开 Oracle 连接");
    }

    @Override
    public String getConnectionInfo() {
        return "Oracle Connection - " + host + "/" + database;
    }
}

class OracleCommand implements Command {
    @Override
    public void execute(String sql) {
        System.out.println("Oracle 执行：" + sql);
        System.out.println("使用 Oracle CBO 优化器处理");
    }

    @Override
    public String getDialect() {
        return "Oracle PL/SQL 方言";
    }
}

class OracleTransaction implements Transaction {
    @Override
    public void begin() {
        System.out.println("Oracle 开始事务（自动开始）");
    }

    @Override
    public void commit() {
        System.out.println("Oracle 提交事务：COMMIT");
    }

    @Override
    public void rollback() {
        System.out.println("Oracle 回滚事务：ROLLBACK");
    }

    @Override
    public String getIsolationLevel() {
        return "READ COMMITTED";
    }
}

// === 数据库工厂抽象类 ===

abstract class DatabaseFactory {
    public abstract Connection createConnection();
    public abstract Command createCommand();
    public abstract Transaction createTransaction();

    // 模板方法 - 执行数据库操作
    public void performDatabaseOperations() {
        Connection conn = createConnection();
        Command cmd = createCommand();
        Transaction tx = createTransaction();

        try {
            conn.connect();
            tx.begin();

            cmd.execute("SELECT * FROM users");
            cmd.execute("UPDATE users SET last_login = NOW()");

            tx.commit();

            System.out.println("数据库操作成功完成");
        } catch (Exception e) {
            tx.rollback();
            System.out.println("操作失败，已回滚");
        } finally {
            conn.disconnect();
        }
    }

    // 静态工厂方法
    public static DatabaseFactory getFactory(String dbType, String host, String database) {
        switch (dbType.toLowerCase()) {
            case "mysql":
                return new MySQLFactory(host, database);
            case "postgresql":
                return new PostgreSQLFactory(host, database);
            case "oracle":
                return new OracleFactory(host, database);
            default:
                throw new IllegalArgumentException("不支持的数据库类型: " + dbType);
        }
    }
}

// === 具体数据库工厂 ===

class MySQLFactory extends DatabaseFactory {
    private String host;
    private String database;

    public MySQLFactory(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public Connection createConnection() {
        return new MySQLConnection(host, database);
    }

    @Override
    public Command createCommand() {
        return new MySQLCommand();
    }

    @Override
    public Transaction createTransaction() {
        return new MySQLTransaction();
    }
}

class PostgreSQLFactory extends DatabaseFactory {
    private String host;
    private String database;

    public PostgreSQLFactory(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public Connection createConnection() {
        return new PostgreSQLConnection(host, database);
    }

    @Override
    public Command createCommand() {
        return new PostgreSQLCommand();
    }

    @Override
    public Transaction createTransaction() {
        return new PostgreSQLTransaction();
    }
}

class OracleFactory extends DatabaseFactory {
    private String host;
    private String database;

    public OracleFactory(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public Connection createConnection() {
        return new OracleConnection(host, database);
    }

    @Override
    public Command createCommand() {
        return new OracleCommand();
    }

    @Override
    public Transaction createTransaction() {
        return new OracleTransaction();
    }
}

// 使用示例
public class DatabaseFactoryDemo {
    public static void main(String[] args) {
        String[][] databases = {
            {"mysql", "localhost", "ecommerce"},
            {"postgresql", "127.0.0.1", "analytics"},
            {"oracle", "db-server", "enterprise"}
        };

        for (String[] db : databases) {
            System.out.println("=== " + db[0].toUpperCase() + " 数据库操作 ===");

            DatabaseFactory factory = DatabaseFactory.getFactory(db[0], db[1], db[2]);
            factory.performDatabaseOperations();

            System.out.println();
        }
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **产品家族一致性**
   - 确保同一家族的产品能够良好协作

2. **易于交换产品系列**
   - 只需更换工厂就能更换整个产品家族

3. **有利于产品的一致性**
   - 当一个产品家族中的多个对象被设计成一起工作时，能够保证客户端始终使用同一家族的对象

4. **符合开闭原则**
   - 增加新的产品家族很容易，无需修改已有代码

### ❌ 缺点

1. **难以支持新种类的产品**
   - 如果要在产品家族中增加新的产品，需要修改抽象工厂接口，违反了开闭原则

2. **增加了系统的抽象性和理解难度**
   - 产品族概念需要时间理解

3. **代码结构复杂**
   - 需要创建很多类和接口

## 🎯 使用场景总结

### 适合使用抽象工厂的场景：

1. **系统需要独立于产品的创建、组合和表示**
   - 如跨平台应用的UI组件

2. **系统需要由多个产品系列中的一个来配置**
   - 如数据库访问层的不同数据库支持

3. **需要强调一系列相关产品的设计以便进行联合使用**
   - 如家具风格、汽车零部件等

4. **需要提供产品类库，而只想显示接口而不是实现**
   - 框架设计时隐藏具体实现

### 不适合使用的场景：

- 产品族很少变化
- 产品族内的产品种类经常变化
- 单纯的对象创建，没有产品族概念

## 🧠 记忆技巧

### 形象比喻
> **抽象工厂就像是"套装搭配师"**：
> - 不同场合有不同套装（产品家族）
> - 商务套装：西装+皮鞋+公文包
> - 运动套装：运动服+运动鞋+运动包
> - 休闲套装：牛仔+帆布鞋+背包
> - 每套搭配风格统一，不会混搭

### 三大工厂模式对比

| 模式 | 用途 | 特点 | 举例 |
|------|------|------|------|
| 简单工厂 | 创建单一产品的不同实现 | 一个工厂类 | 汽车工厂造各种车 |
| 工厂方法 | 创建单一产品，由子类决定 | 一个产品一个工厂 | 专业工厂各造一种车 |
| 抽象工厂 | 创建产品家族 | 一套产品一个工厂 | 豪华车工厂造全套豪华配件 |

### 选择指南
1. **单一产品，简单创建** → 直接new或简单工厂
2. **单一产品，需要扩展** → 工厂方法
3. **产品家族，套装创建** → 抽象工厂

## 🚀 总结

抽象工厂模式最适合创建**产品家族**的场景：

- ✅ 确保产品家族的一致性
- ✅ 易于切换不同的产品系列
- ✅ 符合开闭原则
- ❌ 扩展产品种类困难

**记住**：当你需要创建一系列相关产品，并且这些产品必须一起使用时，就该考虑抽象工厂模式了！

---
*下一篇：建造者模式 - 复杂对象的分步构建*