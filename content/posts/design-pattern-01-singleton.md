---
title: "设计模式详解01：单例模式(Singleton) - 全局唯一实例的优雅实现"
date: 2024-12-01T10:01:00+08:00
draft: false
tags: ["设计模式", "单例模式", "Singleton", "Java", "创建型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解单例模式，从基础概念到高级实现，包含线程安全、性能优化等实战技巧，让你彻底掌握这个最常用的设计模式"
---

## 🎯 什么是单例模式？

### 概念图解
#### 流程图表


**关系流向：**
```
A[多个客户端] → B[请求获取实例]
B → C{单例类}
C → D[唯一实例]
D → E[返回同一个对象]
E → A
```

### 生活中的例子
想象一下，一个国家只能有一个总统，一个公司只能有一个 CEO，一台电脑只能有一个操作系统。这就是单例模式的核心思想：**确保一个类只有一个实例，并提供全局访问点**。

```
🏛️ 政府大楼               🏢 公司总部
   ┌─────────┐              ┌─────────┐
   │   总统   │              │  CEO   │
   │  (唯一)  │              │ (唯一) │
   └─────────┘              └─────────┘
      ↑   ↑                    ↑   ↑
   👨‍💼 👩‍💼 👨‍💼              👨‍💼 👩‍💼 👨‍💼
  (所有人都访问同一个领导)     (所有员工都服务于同一个CEO)
```

### 问题背景
在软件开发中，有些对象我们只需要一个：
- 🖨️ 打印机管理器
- 📊 数据库连接池
- ⚙️ 配置管理器
- 📝 日志记录器
- 🧮 计算器

如果创建多个实例，会导致：
- 资源浪费（内存、CPU）
- 数据不一致
- 配置冲突

## 🧠 设计思想

### UML类图
#### 类图

| 类名 | 属性 | 方法 | 关系 |
|------|------|------|------|
| 详见代码 | - | - | - |


### 核心原则
1. **私有构造函数** - 防止外部直接创建实例
2. **静态实例变量** - 保存唯一实例
3. **静态获取方法** - 提供全局访问点
4. **线程安全** - 确保多线程环境下的正确性

### 结构图解
```
┌─────────────────────────┐
│      Singleton类        │
├─────────────────────────┤
│ - instance: Singleton   │ ← 私有静态实例
│ - Singleton()           │ ← 私有构造函数
├─────────────────────────┤
│ + getInstance()         │ ← 公共获取方法
│ + doSomething()         │ ← 业务方法
└─────────────────────────┘
          ↑
          │
    ┌───────────┐
    │ 全局唯一实例 │
    └───────────┘
```

### 记忆口诀
> **"私有构造，静态实例，全局访问"**

## 💻 代码实现

### 1. 饿汉式（线程安全）

```java
/**
 * 饿汉式单例 - 类加载时就创建实例
 * 优点：线程安全，简单
 * 缺点：可能浪费内存（即使不使用也会创建）
 */
public class EagerSingleton {
    // 在类加载时就创建实例
    private static final EagerSingleton INSTANCE = new EagerSingleton();

    // 私有构造函数，防止外部创建实例
    private EagerSingleton() {
        System.out.println("EagerSingleton 实例被创建");
    }

    // 提供全局访问点
    public static EagerSingleton getInstance() {
        return INSTANCE;
    }

    public void showMessage() {
        System.out.println("我是饿汉式单例！");
    }
}

// 使用示例
public class EagerSingletonDemo {
    public static void main(String[] args) {
        System.out.println("程序启动...");

        // 获取单例实例
        EagerSingleton singleton1 = EagerSingleton.getInstance();
        EagerSingleton singleton2 = EagerSingleton.getInstance();

        // 验证是同一个实例
        System.out.println("singleton1 == singleton2: " + (singleton1 == singleton2));
        System.out.println("singleton1.hashCode(): " + singleton1.hashCode());
        System.out.println("singleton2.hashCode(): " + singleton2.hashCode());

        singleton1.showMessage();
    }
}
```

### 2. 懒汉式（延迟加载）

```java
/**
 * 懒汉式单例 - 需要时才创建实例
 * 基础版本（线程不安全）
 */
public class LazySingletonUnsafe {
    private static LazySingletonUnsafe instance;

    private LazySingletonUnsafe() {
        System.out.println("LazySingleton 实例被创建");
    }

    // 问题：在多线程环境下不安全
    public static LazySingletonUnsafe getInstance() {
        if (instance == null) {
            instance = new LazySingletonUnsafe();
        }
        return instance;
    }
}

/**
 * 懒汉式单例 - 线程安全版本
 * 使用 synchronized 关键字
 */
public class LazySingletonSafe {
    private static LazySingletonSafe instance;

    private LazySingletonSafe() {
        System.out.println("线程安全的 LazySingleton 实例被创建");
    }

    // 同步方法，线程安全但性能较差
    public static synchronized LazySingletonSafe getInstance() {
        if (instance == null) {
            instance = new LazySingletonSafe();
        }
        return instance;
    }

    public void showMessage() {
        System.out.println("我是线程安全的懒汉式单例！");
    }
}
```

### 3. 双检锁（DCL - Double-Checked Locking）

```java
/**
 * 双检锁单例 - 性能最优的线程安全实现
 * 兼顾了性能和线程安全
 */
public class DoubleCheckedSingleton {
    // volatile 确保多线程环境下的可见性
    private static volatile DoubleCheckedSingleton instance;

    private DoubleCheckedSingleton() {
        System.out.println("DoubleCheckedSingleton 实例被创建");
    }

    public static DoubleCheckedSingleton getInstance() {
        // 第一次检查
        if (instance == null) {
            synchronized (DoubleCheckedSingleton.class) {
                // 第二次检查
                if (instance == null) {
                    instance = new DoubleCheckedSingleton();
                }
            }
        }
        return instance;
    }

    public void showMessage() {
        System.out.println("我是双检锁单例，性能和安全性兼备！");
    }
}

// 多线程测试
public class DoubleCheckedSingletonTest {
    public static void main(String[] args) {
        // 创建10个线程同时获取单例
        for (int i = 0; i < 10; i++) {
            new Thread(() -> {
                DoubleCheckedSingleton singleton = DoubleCheckedSingleton.getInstance();
                System.out.println(Thread.currentThread().getName() +
                    " 获取的实例：" + singleton.hashCode());
            }, "Thread-" + i).start();
        }
    }
}
```

### 4. 静态内部类（推荐）

```java
/**
 * 静态内部类单例 - 最优雅的实现
 * 利用类加载机制保证线程安全，延迟加载
 */
public class StaticInnerClassSingleton {

    private StaticInnerClassSingleton() {
        System.out.println("StaticInnerClassSingleton 实例被创建");
    }

    // 静态内部类，只有被引用时才会加载
    private static class SingletonHolder {
        private static final StaticInnerClassSingleton INSTANCE =
            new StaticInnerClassSingleton();
    }

    public static StaticInnerClassSingleton getInstance() {
        return SingletonHolder.INSTANCE;
    }

    public void showMessage() {
        System.out.println("我是静态内部类单例，优雅且高效！");
    }
}
```

### 5. 枚举单例（最安全）

```java
/**
 * 枚举单例 - 最安全的实现方式
 * 天然防止反射和序列化攻击
 */
public enum EnumSingleton {
    INSTANCE;

    private String data;

    EnumSingleton() {
        System.out.println("EnumSingleton 实例被创建");
        data = "我是枚举单例的数据";
    }

    public void showMessage() {
        System.out.println("我是枚举单例，最安全的实现！");
        System.out.println("数据：" + data);
    }

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }
}

// 使用示例
public class EnumSingletonDemo {
    public static void main(String[] args) {
        EnumSingleton singleton1 = EnumSingleton.INSTANCE;
        EnumSingleton singleton2 = EnumSingleton.INSTANCE;

        System.out.println("singleton1 == singleton2: " + (singleton1 == singleton2));

        singleton1.setData("修改后的数据");
        System.out.println("singleton2的数据：" + singleton2.getData());

        singleton1.showMessage();
    }
}
```

## 🌟 实际应用场景

### 1. 数据库连接池

```java
/**
 * 数据库连接池单例
 */
public class DatabasePool {
    private static volatile DatabasePool instance;
    private List<Connection> connectionPool;
    private static final int POOL_SIZE = 10;

    private DatabasePool() {
        initializePool();
    }

    public static DatabasePool getInstance() {
        if (instance == null) {
            synchronized (DatabasePool.class) {
                if (instance == null) {
                    instance = new DatabasePool();
                }
            }
        }
        return instance;
    }

    private void initializePool() {
        connectionPool = new ArrayList<>();
        for (int i = 0; i < POOL_SIZE; i++) {
            // 模拟创建数据库连接
            connectionPool.add(createConnection());
        }
        System.out.println("数据库连接池初始化完成，连接数：" + POOL_SIZE);
    }

    private Connection createConnection() {
        // 模拟数据库连接创建
        return new MockConnection();
    }

    public Connection getConnection() {
        if (!connectionPool.isEmpty()) {
            return connectionPool.remove(0);
        }
        return null;
    }

    public void returnConnection(Connection conn) {
        if (conn != null && connectionPool.size() < POOL_SIZE) {
            connectionPool.add(conn);
        }
    }
}

// 模拟连接类
class MockConnection implements Connection {
    // 省略具体实现...
}
```

### 2. 配置管理器

```java
/**
 * 应用配置管理器单例
 */
public class ConfigManager {
    private static final ConfigManager INSTANCE = new ConfigManager();
    private Properties properties;

    private ConfigManager() {
        loadConfig();
    }

    public static ConfigManager getInstance() {
        return INSTANCE;
    }

    private void loadConfig() {
        properties = new Properties();
        // 模拟加载配置文件
        properties.put("database.url", "jdbc:mysql://localhost:3306/mydb");
        properties.put("database.username", "admin");
        properties.put("server.port", "8080");
        System.out.println("配置文件加载完成");
    }

    public String getProperty(String key) {
        return properties.getProperty(key);
    }

    public void setProperty(String key, String value) {
        properties.setProperty(key, value);
    }

    public void displayAllConfig() {
        System.out.println("=== 当前配置 ===");
        properties.forEach((key, value) ->
            System.out.println(key + " = " + value));
    }
}

// 使用示例
public class ConfigManagerDemo {
    public static void main(String[] args) {
        ConfigManager config = ConfigManager.getInstance();

        config.displayAllConfig();

        System.out.println("\n获取数据库URL: " +
            config.getProperty("database.url"));

        config.setProperty("cache.enabled", "true");
        config.displayAllConfig();
    }
}
```

### 3. 日志管理器

```java
/**
 * 日志管理器单例
 */
public class Logger {
    private static volatile Logger instance;
    private PrintWriter writer;

    private Logger() {
        try {
            writer = new PrintWriter(new FileWriter("application.log", true));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Logger getInstance() {
        if (instance == null) {
            synchronized (Logger.class) {
                if (instance == null) {
                    instance = new Logger();
                }
            }
        }
        return instance;
    }

    public void log(LogLevel level, String message) {
        String logEntry = String.format("[%s] %s: %s",
            new Date(), level, message);

        System.out.println(logEntry);

        if (writer != null) {
            writer.println(logEntry);
            writer.flush();
        }
    }

    public void info(String message) {
        log(LogLevel.INFO, message);
    }

    public void error(String message) {
        log(LogLevel.ERROR, message);
    }

    public void debug(String message) {
        log(LogLevel.DEBUG, message);
    }

    public enum LogLevel {
        INFO, ERROR, DEBUG, WARN
    }
}

// 使用示例
public class LoggerDemo {
    public static void main(String[] args) {
        Logger logger = Logger.getInstance();

        logger.info("应用程序启动");
        logger.debug("调试信息");
        logger.error("发生错误");

        // 在其他地方也使用相同的Logger实例
        Logger anotherLogger = Logger.getInstance();
        anotherLogger.info("这是另一个地方的日志");

        System.out.println("两个Logger是同一个实例：" +
            (logger == anotherLogger));
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **节约内存**
   - 只创建一个实例，避免重复创建对象

2. **全局访问**
   - 提供唯一的全局访问点

3. **延迟初始化**
   - 懒汉式可以延迟加载，节约资源

4. **线程安全**
   - 正确实现的单例是线程安全的

### ❌ 缺点

1. **违反单一职责原则**
   - 既要管理自身实例，又要处理业务逻辑

2. **难以测试**
   - 全局状态难以模拟和测试

3. **隐藏依赖**
   - 不容易看出类之间的依赖关系

4. **扩展困难**
   - 很难继承和扩展单例类

## 🎯 使用场景总结

### 适合使用单例的场景：
- 🗂️ **配置信息管理器** - 全局配置统一管理
- 📊 **数据库连接池** - 避免重复创建连接
- 📝 **日志记录器** - 统一日志输出
- 🖨️ **打印任务管理器** - 控制打印队列
- 💾 **缓存管理器** - 全局缓存访问

### 不适合使用单例的场景：
- 需要创建多个实例的类
- 状态频繁变化的类
- 需要继承的类
- 单元测试困难的类

## 🧠 记忆技巧

### 形象比喻
> **单例模式就像是 "皇帝"**：
> - 一个王朝只能有一个皇帝（单一实例）
> - 皇帝不能被外人创造（私有构造）
> - 要见皇帝必须通过正当途径（静态方法）
> - 皇帝是全天下都认识的（全局访问）

### 实现口诀
> **"饿汉直接造，懒汉检查造，双检锁两道，内部类最妙，枚举是法宝"**

### 选择建议
1. **简单场景** → 饿汉式
2. **延迟加载** → 静态内部类
3. **防破坏** → 枚举单例
4. **高性能** → 双检锁

## 🔧 最佳实践

### 1. 防止反射破坏

```java
public class ReflectionProofSingleton {
    private static final ReflectionProofSingleton INSTANCE =
        new ReflectionProofSingleton();

    private ReflectionProofSingleton() {
        // 防止反射创建多个实例
        if (INSTANCE != null) {
            throw new RuntimeException("Use getInstance() method to create instance.");
        }
    }

    public static ReflectionProofSingleton getInstance() {
        return INSTANCE;
    }
}
```

### 2. 防止序列化破坏

```java
public class SerializationSafeSingleton implements Serializable {
    private static final SerializationSafeSingleton INSTANCE =
        new SerializationSafeSingleton();

    private SerializationSafeSingleton() {}

    public static SerializationSafeSingleton getInstance() {
        return INSTANCE;
    }

    // 防止序列化破坏单例
    protected Object readResolve() {
        return INSTANCE;
    }
}
```

## 🚀 总结

单例模式是最常用的设计模式之一，核心思想是确保全局唯一性。选择合适的实现方式：

- **新手推荐**：静态内部类单例
- **安全至上**：枚举单例
- **高并发**：双检锁单例

记住，**不要滥用单例模式**，只在真正需要全局唯一实例时使用！

---
*下一篇：工厂方法模式 - 对象创建的艺术*