---
title: "设计模式详解：工厂方法模式(Factory Method) - 对象创建的艺术"
date: 2024-12-02T10:02:00+08:00
draft: false
tags: ["设计模式", "工厂方法模式", "Factory Method", "Java", "创建型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解工厂方法模式，通过生动的例子和完整的代码演示，让你轻松掌握对象创建的最佳实践"
---

## 🎯 什么是工厂方法模式？

### 生活中的例子
想象你要开一家披萨店，顾客可以点不同口味的披萨：玛格丽特、夏威夷、肉食者...

**传统做法**：老板亲自做每种披萨
- 老板要会做所有口味
- 新增口味要修改老板的技能
- 老板累死，效率低下

**工厂方法**：雇佣专业的披萨师傅
- 每种口味有专门的师傅
- 新增口味只需雇佣新师傅
- 老板只负责分配任务

这就是工厂方法模式的核心：**定义创建对象的接口，让子类决定实例化哪个类**。

## 🧠 设计思想

### 核心概念
- **抽象工厂**：定义创建对象的接口
- **具体工厂**：实现创建具体对象的逻辑
- **抽象产品**：定义产品的接口
- **具体产品**：实现具体的产品

### 记忆口诀
> **"工厂生产品，接口定规范，子类做决定，扩展更简单"**

## 💻 代码实现

### 基础版本：披萨工厂

```java
// 抽象产品 - 披萨基类
abstract class Pizza {
    protected String name;
    protected String dough = "Regular Crust";
    protected String sauce = "Marinara Pizza Sauce";
    protected List<String> toppings = new ArrayList<>();

    public void prepare() {
        System.out.println("准备制作 " + name);
        System.out.println("揉面团：" + dough);
        System.out.println("添加酱料：" + sauce);
        System.out.println("添加配菜：");
        for (String topping : toppings) {
            System.out.println("   " + topping);
        }
    }

    public void bake() {
        System.out.println("烘烤 25 分钟，温度 350 度");
    }

    public void cut() {
        System.out.println("将披萨切成对角切片");
    }

    public void box() {
        System.out.println("将披萨装入官方披萨盒");
    }

    public String getName() {
        return name;
    }
}

// 具体产品 - 不同口味的披萨
class MargheritaPizza extends Pizza {
    public MargheritaPizza() {
        name = "玛格丽特披萨";
        toppings.add("新鲜马苏里拉奶酪");
        toppings.add("新鲜番茄");
        toppings.add("新鲜罗勒");
    }
}

class HawaiianPizza extends Pizza {
    public HawaiianPizza() {
        name = "夏威夷披萨";
        toppings.add("马苏里拉奶酪");
        toppings.add("菠萝块");
        toppings.add("加拿大火腿");
    }
}

class MeatLoversPizza extends Pizza {
    public MeatLoversPizza() {
        name = "肉食者披萨";
        toppings.add("马苏里拉奶酪");
        toppings.add("意大利辣肠");
        toppings.add("意大利香肠");
        toppings.add("培根");
        toppings.add("火腿");
    }
}

// 抽象工厂 - 披萨工厂接口
abstract class PizzaFactory {
    // 工厂方法 - 子类必须实现
    public abstract Pizza createPizza(String type);

    // 模板方法 - 定义制作披萨的流程
    public Pizza orderPizza(String type) {
        Pizza pizza = createPizza(type);

        if (pizza != null) {
            pizza.prepare();
            pizza.bake();
            pizza.cut();
            pizza.box();
        }

        return pizza;
    }
}

// 具体工厂 - 纽约风味披萨工厂
class NYPizzaFactory extends PizzaFactory {
    @Override
    public Pizza createPizza(String type) {
        Pizza pizza = null;

        switch (type.toLowerCase()) {
            case "margherita":
                pizza = new NYMargheritaPizza();
                break;
            case "hawaiian":
                pizza = new NYHawaiianPizza();
                break;
            case "meatlover":
                pizza = new NYMeatLoversPizza();
                break;
            default:
                System.out.println("未知的披萨类型：" + type);
        }

        return pizza;
    }
}

// 纽约风味的具体产品
class NYMargheritaPizza extends Pizza {
    public NYMargheritaPizza() {
        name = "纽约风味玛格丽特披萨";
        dough = "薄脆面团";
        sauce = "纽约特制番茄酱";
        toppings.add("纽约新鲜马苏里拉");
        toppings.add("有机番茄");
    }
}

class NYHawaiianPizza extends Pizza {
    public NYHawaiianPizza() {
        name = "纽约风味夏威夷披萨";
        dough = "薄脆面团";
        sauce = "纽约特制番茄酱";
        toppings.add("纽约马苏里拉");
        toppings.add("新鲜菠萝");
        toppings.add("优质火腿");
    }
}

class NYMeatLoversPizza extends Pizza {
    public NYMeatLoversPizza() {
        name = "纽约风味肉食者披萨";
        dough = "厚实面团";
        sauce = "浓郁肉酱";
        toppings.add("三重奶酪");
        toppings.add("纽约香肠");
        toppings.add("烟熏培根");
    }
}

// 具体工厂 - 芝加哥风味披萨工厂
class ChicagoPizzaFactory extends PizzaFactory {
    @Override
    public Pizza createPizza(String type) {
        Pizza pizza = null;

        switch (type.toLowerCase()) {
            case "margherita":
                pizza = new ChicagoMargheritaPizza();
                break;
            case "hawaiian":
                pizza = new ChicagoHawaiianPizza();
                break;
            case "meatlover":
                pizza = new ChicagoMeatLoversPizza();
                break;
            default:
                System.out.println("芝加哥没有这种口味的披萨：" + type);
        }

        return pizza;
    }
}

// 芝加哥风味的具体产品
class ChicagoMargheritaPizza extends Pizza {
    public ChicagoMargheritaPizza() {
        name = "芝加哥深盘玛格丽特披萨";
        dough = "深盘厚底面团";
        sauce = "芝加哥特制厚重番茄酱";
        toppings.add("芝加哥马苏里拉");
        toppings.add("意大利番茄");
    }

    @Override
    public void cut() {
        System.out.println("将披萨切成方块");
    }
}

class ChicagoHawaiianPizza extends Pizza {
    public ChicagoHawaiianPizza() {
        name = "芝加哥深盘夏威夷披萨";
        dough = "深盘厚底面团";
        sauce = "芝加哥特制甜酱";
        toppings.add("芝加哥马苏里拉");
        toppings.add("烤菠萝");
        toppings.add("芝加哥火腿");
    }

    @Override
    public void cut() {
        System.out.println("将披萨切成方块");
    }
}

class ChicagoMeatLoversPizza extends Pizza {
    public ChicagoMeatLoversPizza() {
        name = "芝加哥深盘肉食者披萨";
        dough = "深盘超厚面团";
        sauce = "芝加哥肉汁酱";
        toppings.add("四种奶酪混合");
        toppings.add("芝加哥香肠");
        toppings.add("厚切培根");
        toppings.add("意式腊肠");
    }

    @Override
    public void cut() {
        System.out.println("用特制刀具切成方块");
    }
}
```

### 使用示例

```java
public class PizzaFactoryDemo {
    public static void main(String[] args) {
        // 创建不同地区的披萨工厂
        PizzaFactory nyFactory = new NYPizzaFactory();
        PizzaFactory chicagoFactory = new ChicagoPizzaFactory();

        System.out.println("=== 纽约披萨店 ===");
        Pizza nyPizza1 = nyFactory.orderPizza("margherita");
        System.out.println("制作完成：" + nyPizza1.getName());

        System.out.println("\n=== 芝加哥披萨店 ===");
        Pizza chicagoPizza1 = chicagoFactory.orderPizza("hawaiian");
        System.out.println("制作完成：" + chicagoPizza1.getName());

        System.out.println("\n=== 对比两种工厂 ===");
        Pizza nyMeat = nyFactory.orderPizza("meatlover");
        Pizza chicagoMeat = chicagoFactory.orderPizza("meatlover");

        System.out.println("\n纽约：" + nyMeat.getName());
        System.out.println("芝加哥：" + chicagoMeat.getName());
    }
}
```

## 🌟 实际应用场景

### 1. 数据库连接工厂

```java
// 抽象产品 - 数据库连接接口
interface DatabaseConnection {
    void connect();
    void disconnect();
    void executeQuery(String sql);
    String getConnectionInfo();
}

// 具体产品 - MySQL 连接
class MySQLConnection implements DatabaseConnection {
    private String host;
    private String database;

    public MySQLConnection(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public void connect() {
        System.out.println("连接到 MySQL 数据库：" + host + "/" + database);
    }

    @Override
    public void disconnect() {
        System.out.println("断开 MySQL 连接");
    }

    @Override
    public void executeQuery(String sql) {
        System.out.println("MySQL 执行查询：" + sql);
    }

    @Override
    public String getConnectionInfo() {
        return "MySQL Connection - " + host + "/" + database;
    }
}

// 具体产品 - PostgreSQL 连接
class PostgreSQLConnection implements DatabaseConnection {
    private String host;
    private String database;

    public PostgreSQLConnection(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public void connect() {
        System.out.println("连接到 PostgreSQL 数据库：" + host + "/" + database);
    }

    @Override
    public void disconnect() {
        System.out.println("断开 PostgreSQL 连接");
    }

    @Override
    public void executeQuery(String sql) {
        System.out.println("PostgreSQL 执行查询：" + sql);
    }

    @Override
    public String getConnectionInfo() {
        return "PostgreSQL Connection - " + host + "/" + database;
    }
}

// 抽象工厂 - 数据库工厂
abstract class DatabaseFactory {
    public abstract DatabaseConnection createConnection();

    // 通用的数据库操作模板
    public void performDatabaseOperations() {
        DatabaseConnection conn = createConnection();
        conn.connect();

        // 执行一些示例操作
        conn.executeQuery("SELECT * FROM users");
        conn.executeQuery("SELECT COUNT(*) FROM orders");

        conn.disconnect();
        System.out.println("操作完成：" + conn.getConnectionInfo());
    }
}

// 具体工厂 - MySQL 工厂
class MySQLFactory extends DatabaseFactory {
    private String host;
    private String database;

    public MySQLFactory(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public DatabaseConnection createConnection() {
        return new MySQLConnection(host, database);
    }
}

// 具体工厂 - PostgreSQL 工厂
class PostgreSQLFactory extends DatabaseFactory {
    private String host;
    private String database;

    public PostgreSQLFactory(String host, String database) {
        this.host = host;
        this.database = database;
    }

    @Override
    public DatabaseConnection createConnection() {
        return new PostgreSQLConnection(host, database);
    }
}

// 使用示例
public class DatabaseFactoryDemo {
    public static void main(String[] args) {
        // 使用 MySQL 工厂
        DatabaseFactory mysqlFactory = new MySQLFactory("localhost", "ecommerce");
        System.out.println("=== MySQL 数据库操作 ===");
        mysqlFactory.performDatabaseOperations();

        System.out.println();

        // 使用 PostgreSQL 工厂
        DatabaseFactory postgresFactory = new PostgreSQLFactory("127.0.0.1", "analytics");
        System.out.println("=== PostgreSQL 数据库操作 ===");
        postgresFactory.performDatabaseOperations();
    }
}
```

### 2. 日志记录器工厂

```java
// 抽象产品 - 日志记录器接口
interface Logger {
    void log(String level, String message);
    void info(String message);
    void error(String message);
    void debug(String message);
}

// 具体产品 - 文件日志记录器
class FileLogger implements Logger {
    private String filename;

    public FileLogger(String filename) {
        this.filename = filename;
    }

    @Override
    public void log(String level, String message) {
        String logEntry = String.format("[%s] %s: %s",
            new Date().toString(), level, message);
        System.out.println("写入文件 " + filename + ": " + logEntry);
    }

    @Override
    public void info(String message) { log("INFO", message); }

    @Override
    public void error(String message) { log("ERROR", message); }

    @Override
    public void debug(String message) { log("DEBUG", message); }
}

// 具体产品 - 控制台日志记录器
class ConsoleLogger implements Logger {
    private String prefix;

    public ConsoleLogger(String prefix) {
        this.prefix = prefix;
    }

    @Override
    public void log(String level, String message) {
        System.out.println(String.format("[%s][%s] %s: %s",
            prefix, new Date().toString(), level, message));
    }

    @Override
    public void info(String message) { log("INFO", message); }

    @Override
    public void error(String message) { log("ERROR", message); }

    @Override
    public void debug(String message) { log("DEBUG", message); }
}

// 具体产品 - 数据库日志记录器
class DatabaseLogger implements Logger {
    private String tableName;

    public DatabaseLogger(String tableName) {
        this.tableName = tableName;
    }

    @Override
    public void log(String level, String message) {
        String sql = String.format("INSERT INTO %s (level, message, timestamp) VALUES ('%s', '%s', '%s')",
            tableName, level, message, new Date().toString());
        System.out.println("数据库记录日志：" + sql);
    }

    @Override
    public void info(String message) { log("INFO", message); }

    @Override
    public void error(String message) { log("ERROR", message); }

    @Override
    public void debug(String message) { log("DEBUG", message); }
}

// 抽象工厂 - 日志工厂
abstract class LoggerFactory {
    public abstract Logger createLogger();

    // 便捷的静态工厂方法
    public static LoggerFactory getFactory(String type, String config) {
        switch (type.toLowerCase()) {
            case "file":
                return new FileLoggerFactory(config);
            case "console":
                return new ConsoleLoggerFactory(config);
            case "database":
                return new DatabaseLoggerFactory(config);
            default:
                throw new IllegalArgumentException("未知的日志类型: " + type);
        }
    }
}

// 具体工厂实现
class FileLoggerFactory extends LoggerFactory {
    private String filename;

    public FileLoggerFactory(String filename) {
        this.filename = filename;
    }

    @Override
    public Logger createLogger() {
        return new FileLogger(filename);
    }
}

class ConsoleLoggerFactory extends LoggerFactory {
    private String prefix;

    public ConsoleLoggerFactory(String prefix) {
        this.prefix = prefix;
    }

    @Override
    public Logger createLogger() {
        return new ConsoleLogger(prefix);
    }
}

class DatabaseLoggerFactory extends LoggerFactory {
    private String tableName;

    public DatabaseLoggerFactory(String tableName) {
        this.tableName = tableName;
    }

    @Override
    public Logger createLogger() {
        return new DatabaseLogger(tableName);
    }
}

// 应用程序示例
public class LoggerFactoryDemo {
    public static void main(String[] args) {
        // 根据配置创建不同类型的日志记录器
        String logType = "file"; // 可以从配置文件读取
        String logConfig = "application.log";

        LoggerFactory factory = LoggerFactory.getFactory(logType, logConfig);
        Logger logger = factory.createLogger();

        logger.info("应用程序启动");
        logger.debug("调试信息：初始化完成");
        logger.error("发生错误：连接数据库失败");

        // 切换到控制台日志
        LoggerFactory consoleFactory = LoggerFactory.getFactory("console", "MyApp");
        Logger consoleLogger = consoleFactory.createLogger();

        consoleLogger.info("切换到控制台日志");
        consoleLogger.debug("这是控制台调试信息");

        // 使用数据库日志
        LoggerFactory dbFactory = LoggerFactory.getFactory("database", "application_logs");
        Logger dbLogger = dbFactory.createLogger();

        dbLogger.info("数据库日志记录");
        dbLogger.error("数据库错误日志");
    }
}
```

### 3. 图形界面组件工厂

```java
// 抽象产品 - UI 组件接口
interface Button {
    void render();
    void onClick();
    String getStyle();
}

interface Dialog {
    void show();
    void hide();
    String getTheme();
}

// Windows 风格的具体产品
class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 Windows 风格按钮");
    }

    @Override
    public void onClick() {
        System.out.println("Windows 按钮被点击");
    }

    @Override
    public String getStyle() {
        return "Windows Native Style";
    }
}

class WindowsDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("显示 Windows 对话框");
    }

    @Override
    public void hide() {
        System.out.println("隐藏 Windows 对话框");
    }

    @Override
    public String getTheme() {
        return "Windows Theme";
    }
}

// macOS 风格的具体产品
class MacOSButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 macOS 风格按钮");
    }

    @Override
    public void onClick() {
        System.out.println("macOS 按钮被点击");
    }

    @Override
    public String getStyle() {
        return "macOS Aqua Style";
    }
}

class MacOSDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("显示 macOS 对话框");
    }

    @Override
    public void hide() {
        System.out.println("隐藏 macOS 对话框");
    }

    @Override
    public String getTheme() {
        return "macOS Theme";
    }
}

// Linux 风格的具体产品
class LinuxButton implements Button {
    @Override
    public void render() {
        System.out.println("渲染 Linux GTK 风格按钮");
    }

    @Override
    public void onClick() {
        System.out.println("Linux 按钮被点击");
    }

    @Override
    public String getStyle() {
        return "GTK Style";
    }
}

class LinuxDialog implements Dialog {
    @Override
    public void show() {
        System.out.println("显示 Linux GTK 对话框");
    }

    @Override
    public void hide() {
        System.out.println("隐藏 Linux GTK 对话框");
    }

    @Override
    public String getTheme() {
        return "GTK Theme";
    }
}

// 抽象工厂 - UI 工厂
abstract class UIFactory {
    public abstract Button createButton();
    public abstract Dialog createDialog();

    // 工厂方法：根据操作系统创建对应的工厂
    public static UIFactory getFactory() {
        String os = System.getProperty("os.name").toLowerCase();

        if (os.contains("win")) {
            return new WindowsUIFactory();
        } else if (os.contains("mac")) {
            return new MacOSUIFactory();
        } else {
            return new LinuxUIFactory();
        }
    }
}

// 具体工厂实现
class WindowsUIFactory extends UIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }

    @Override
    public Dialog createDialog() {
        return new WindowsDialog();
    }
}

class MacOSUIFactory extends UIFactory {
    @Override
    public Button createButton() {
        return new MacOSButton();
    }

    @Override
    public Dialog createDialog() {
        return new MacOSDialog();
    }
}

class LinuxUIFactory extends UIFactory {
    @Override
    public Button createButton() {
        return new LinuxButton();
    }

    @Override
    public Dialog createDialog() {
        return new LinuxDialog();
    }
}

// 应用程序
public class UIFactoryDemo {
    private UIFactory uiFactory;
    private Button button;
    private Dialog dialog;

    public UIFactoryDemo() {
        // 根据当前操作系统自动选择UI工厂
        this.uiFactory = UIFactory.getFactory();
    }

    public void createUI() {
        button = uiFactory.createButton();
        dialog = uiFactory.createDialog();

        System.out.println("UI 组件创建完成");
        System.out.println("按钮风格：" + button.getStyle());
        System.out.println("对话框主题：" + dialog.getTheme());
    }

    public void showUI() {
        button.render();
        dialog.show();
    }

    public void handleUserInteraction() {
        button.onClick();
        dialog.hide();
    }

    public static void main(String[] args) {
        System.out.println("当前操作系统：" + System.getProperty("os.name"));

        UIFactoryDemo app = new UIFactoryDemo();
        app.createUI();

        System.out.println("\n=== 显示 UI ===");
        app.showUI();

        System.out.println("\n=== 用户交互 ===");
        app.handleUserInteraction();
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **符合开闭原则**
   - 增加新产品类型无需修改现有代码

2. **符合单一职责原则**
   - 每个工厂只负责创建一种类型的对象

3. **降低耦合度**
   - 客户端不需要知道具体产品类名

4. **易于扩展**
   - 新增产品只需添加对应的工厂类

### ❌ 缺点

1. **增加代码复杂度**
   - 每增加一个产品就要增加一个工厂类

2. **增加系统抽象性**
   - 理解起来比直接创建对象复杂

3. **难以支持产品族**
   - 如果要创建相关的产品组合，需要抽象工厂模式

## 🎯 使用场景总结

### 适合使用工厂方法的场景：

1. **不确定需要创建哪种对象**
   - 根据配置或用户输入决定

2. **希望用户扩展软件库或框架的内部组件**
   - 提供扩展点

3. **希望节约系统资源**
   - 复用现有对象而不是每次都创建

4. **对象的创建过程相对复杂**
   - 需要初始化很多参数

### 不适合使用的场景：

- 产品类较少且不会经常变化
- 创建过程很简单
- 不需要解耦创建过程

## 🧠 记忆技巧

### 形象比喻
> **工厂方法就像是"专业分工"**：
> - 总厂长定标准（抽象工厂）
> - 分厂长做产品（具体工厂）
> - 产品有规范（抽象产品）
> - 成品有特色（具体产品）

### 与简单工厂的区别
- **简单工厂**：一个工厂做所有产品（违反开闭原则）
- **工厂方法**：一个工厂做一类产品（符合开闭原则）

### 选择指南
1. **产品种类少** → 简单工厂
2. **产品种类多且会扩展** → 工厂方法
3. **需要创建产品族** → 抽象工厂

## 🚀 总结

工厂方法模式通过将对象创建委托给子类，实现了：
- ✅ 解耦对象的创建和使用
- ✅ 符合开闭原则，易于扩展
- ✅ 每个工厂职责单一，易于维护

**记住**：当你发现代码中有大量的 `if-else` 或 `switch-case` 来创建对象时，就该考虑使用工厂方法模式了！

---
*下一篇：抽象工厂模式 - 产品家族的统一创建*