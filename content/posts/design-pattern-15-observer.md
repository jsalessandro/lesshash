---
title: "设计模式入门教程15：观察者模式 - 让对象间的通信更优雅"
date: 2024-12-15T10:15:00+08:00
draft: false
tags: ["设计模式", "观察者模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是观察者模式？

观察者模式（Observer Pattern）是一种行为型设计模式，它定义了对象间的一对多依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都会得到通知并自动更新。

### 🌟 现实生活中的例子

想象一下订阅报纸的场景：
- **报社**（主题）负责发布报纸
- **订阅者**（观察者）订阅报纸
- 当有新报纸时，报社会**自动通知**所有订阅者
- 订阅者可以随时**订阅**或**取消订阅**

这就是观察者模式的典型应用！

## 🏗️ 模式结构

```java
// 抽象主题（被观察者）
abstract class Subject {
    private List<Observer> observers = new ArrayList<>();

    // 添加观察者
    public void attach(Observer observer) {
        observers.add(observer);
    }

    // 移除观察者
    public void detach(Observer observer) {
        observers.remove(observer);
    }

    // 通知所有观察者
    protected void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
}

// 抽象观察者
interface Observer {
    void update(Subject subject);
}
```

## 💡 核心组件详解

### 1. 抽象主题（Subject）
```java
// 气象站抽象类
abstract class WeatherStation {
    private List<Observer> observers = new ArrayList<>();
    protected float temperature;
    protected float humidity;
    protected float pressure;

    public void addObserver(Observer observer) {
        observers.add(observer);
        System.out.println("新的观察者已添加！");
    }

    public void removeObserver(Observer observer) {
        observers.remove(observer);
        System.out.println("观察者已移除！");
    }

    protected void notifyObservers() {
        System.out.println("正在通知所有观察者...");
        for (Observer observer : observers) {
            observer.update(temperature, humidity, pressure);
        }
    }

    public abstract void measurementsChanged();
}
```

### 2. 具体主题（ConcreteSubject）
```java
// 具体气象站
class ConcreteWeatherStation extends WeatherStation {

    public void setMeasurements(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        this.pressure = pressure;
        measurementsChanged();
    }

    @Override
    public void measurementsChanged() {
        notifyObservers();
    }

    // Getter方法
    public float getTemperature() { return temperature; }
    public float getHumidity() { return humidity; }
    public float getPressure() { return pressure; }
}
```

### 3. 抽象观察者（Observer）
```java
// 显示设备接口
interface Observer {
    void update(float temperature, float humidity, float pressure);
}

// 显示面板接口
interface DisplayElement {
    void display();
}
```

### 4. 具体观察者（ConcreteObserver）
```java
// 当前天气显示板
class CurrentConditionsDisplay implements Observer, DisplayElement {
    private float temperature;
    private float humidity;
    private WeatherStation weatherStation;

    public CurrentConditionsDisplay(WeatherStation weatherStation) {
        this.weatherStation = weatherStation;
        weatherStation.addObserver(this);
    }

    @Override
    public void update(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        display();
    }

    @Override
    public void display() {
        System.out.println("当前状况：温度 " + temperature + "°C，湿度 " + humidity + "%");
    }
}

// 统计显示板
class StatisticsDisplay implements Observer, DisplayElement {
    private float maxTemp = 0.0f;
    private float minTemp = 200;
    private float tempSum = 0.0f;
    private int numReadings;
    private WeatherStation weatherStation;

    public StatisticsDisplay(WeatherStation weatherStation) {
        this.weatherStation = weatherStation;
        weatherStation.addObserver(this);
    }

    @Override
    public void update(float temperature, float humidity, float pressure) {
        tempSum += temperature;
        numReadings++;

        if (temperature > maxTemp) {
            maxTemp = temperature;
        }

        if (temperature < minTemp) {
            minTemp = temperature;
        }

        display();
    }

    @Override
    public void display() {
        System.out.println("平均/最高/最低温度 = " + (tempSum / numReadings)
                         + "/" + maxTemp + "/" + minTemp);
    }
}

// 预报显示板
class ForecastDisplay implements Observer, DisplayElement {
    private float currentPressure = 29.92f;
    private float lastPressure;
    private WeatherStation weatherStation;

    public ForecastDisplay(WeatherStation weatherStation) {
        this.weatherStation = weatherStation;
        weatherStation.addObserver(this);
    }

    @Override
    public void update(float temperature, float humidity, float pressure) {
        lastPressure = currentPressure;
        currentPressure = pressure;
        display();
    }

    @Override
    public void display() {
        System.out.print("天气预报：");
        if (currentPressure > lastPressure) {
            System.out.println("天气正在好转！");
        } else if (currentPressure == lastPressure) {
            System.out.println("天气保持不变");
        } else if (currentPressure < lastPressure) {
            System.out.println("小心冷空气和雨天");
        }
    }
}
```

## 🎮 实际应用示例

### 示例1：股票价格监控系统
```java
// 股票主题
class Stock extends Subject {
    private String symbol;
    private double price;

    public Stock(String symbol, double price) {
        this.symbol = symbol;
        this.price = price;
    }

    public double getPrice() {
        return price;
    }

    public String getSymbol() {
        return symbol;
    }

    public void setPrice(double price) {
        this.price = price;
        notifyObservers();
    }
}

// 投资者观察者
class Investor implements Observer {
    private String name;

    public Investor(String name) {
        this.name = name;
    }

    @Override
    public void update(Subject subject) {
        if (subject instanceof Stock) {
            Stock stock = (Stock) subject;
            System.out.println("通知投资者 " + name + "：" + stock.getSymbol()
                             + " 股票价格更新为 $" + stock.getPrice());
        }
    }
}

// 使用示例
public class StockMarketExample {
    public static void main(String[] args) {
        // 创建股票
        Stock appleStock = new Stock("AAPL", 150.00);

        // 创建投资者
        Investor investor1 = new Investor("张三");
        Investor investor2 = new Investor("李四");
        Investor investor3 = new Investor("王五");

        // 投资者订阅股票
        appleStock.attach(investor1);
        appleStock.attach(investor2);
        appleStock.attach(investor3);

        // 股票价格变动
        System.out.println("=== 股票价格上涨 ===");
        appleStock.setPrice(155.50);

        System.out.println("\n=== 投资者李四卖出股票 ===");
        appleStock.detach(investor2);

        System.out.println("\n=== 股票价格下跌 ===");
        appleStock.setPrice(148.75);
    }
}
```

### 示例2：新闻发布系统
```java
// 新闻机构
class NewsAgency {
    private String news;
    private List<Channel> channels = new ArrayList<>();

    public void addObserver(Channel channel) {
        channels.add(channel);
    }

    public void removeObserver(Channel channel) {
        channels.remove(channel);
    }

    public void setNews(String news) {
        this.news = news;
        notifyAllChannels();
    }

    public void notifyAllChannels() {
        for (Channel channel : channels) {
            channel.update(this.news);
        }
    }
}

// 媒体频道接口
interface Channel {
    void update(Object news);
}

// 具体媒体频道
class NewsChannel implements Channel {
    private String news;
    private String channelName;

    public NewsChannel(String channelName) {
        this.channelName = channelName;
    }

    @Override
    public void update(Object news) {
        this.news = (String) news;
        System.out.println(channelName + " 收到新闻：" + this.news);
    }
}

class SocialMediaChannel implements Channel {
    private String news;
    private String platformName;

    public SocialMediaChannel(String platformName) {
        this.platformName = platformName;
    }

    @Override
    public void update(Object news) {
        this.news = (String) news;
        System.out.println(platformName + " 发布动态：" + this.news + " #突发新闻");
    }
}

// 使用示例
public class NewsSystemExample {
    public static void main(String[] args) {
        NewsAgency agency = new NewsAgency();

        NewsChannel cnn = new NewsChannel("CNN新闻");
        NewsChannel bbc = new NewsChannel("BBC新闻");
        SocialMediaChannel twitter = new SocialMediaChannel("Twitter");
        SocialMediaChannel weibo = new SocialMediaChannel("微博");

        agency.addObserver(cnn);
        agency.addObserver(bbc);
        agency.addObserver(twitter);
        agency.addObserver(weibo);

        System.out.println("=== 发布重大新闻 ===");
        agency.setNews("科技公司发布革命性AI产品！");

        System.out.println("\n=== BBC停止订阅 ===");
        agency.removeObserver(bbc);

        System.out.println("\n=== 发布第二条新闻 ===");
        agency.setNews("全球气候大会达成重要协议");
    }
}
```

### 示例3：MVC架构中的观察者模式
```java
// 模型（Model）
class UserModel {
    private List<Observer> observers = new ArrayList<>();
    private String userData;

    public void addObserver(Observer observer) {
        observers.add(observer);
    }

    public void removeObserver(Observer observer) {
        observers.remove(observer);
    }

    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(this);
        }
    }

    public String getUserData() {
        return userData;
    }

    public void setUserData(String userData) {
        this.userData = userData;
        notifyObservers();
    }
}

// 视图（View）
class UserView implements Observer {
    private String viewName;

    public UserView(String viewName) {
        this.viewName = viewName;
    }

    @Override
    public void update(Subject subject) {
        if (subject instanceof UserModel) {
            UserModel model = (UserModel) subject;
            System.out.println(viewName + " 更新显示：" + model.getUserData());
        }
    }
}

// 控制器（Controller）
class UserController {
    private UserModel model;

    public UserController(UserModel model) {
        this.model = model;
    }

    public void updateUser(String userData) {
        model.setUserData(userData);
    }
}

// MVC使用示例
public class MVCExample {
    public static void main(String[] args) {
        // 创建模型
        UserModel model = new UserModel();

        // 创建视图
        UserView webView = new UserView("Web页面");
        UserView mobileView = new UserView("手机应用");
        UserView emailView = new UserView("邮件通知");

        // 视图观察模型
        model.addObserver(webView);
        model.addObserver(mobileView);
        model.addObserver(emailView);

        // 创建控制器
        UserController controller = new UserController(model);

        // 更新用户数据
        System.out.println("=== 用户登录 ===");
        controller.updateUser("用户张三已登录");

        System.out.println("\n=== 用户更新资料 ===");
        controller.updateUser("用户张三更新了个人资料");
    }
}
```

## 🔧 Java内置观察者模式

```java
import java.util.Observable;
import java.util.Observer;

// 使用Java内置的Observable类
class WeatherData extends Observable {
    private float temperature;
    private float humidity;
    private float pressure;

    public void measurementsChanged() {
        setChanged();  // 标记状态已改变
        notifyObservers();  // 通知观察者
    }

    public void setMeasurements(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        this.pressure = pressure;
        measurementsChanged();
    }

    public float getTemperature() { return temperature; }
    public float getHumidity() { return humidity; }
    public float getPressure() { return pressure; }
}

// 使用Java内置的Observer接口
class CurrentConditionsDisplayJava implements Observer {
    private float temperature;
    private float humidity;

    @Override
    public void update(Observable observable, Object arg) {
        if (observable instanceof WeatherData) {
            WeatherData weatherData = (WeatherData) observable;
            this.temperature = weatherData.getTemperature();
            this.humidity = weatherData.getHumidity();
            display();
        }
    }

    public void display() {
        System.out.println("当前状况：温度 " + temperature + "°C，湿度 " + humidity + "%");
    }
}
```

## ⚡ 现代框架中的观察者模式

### 事件驱动编程
```java
// 事件监听器
interface EventListener {
    void onEvent(Event event);
}

// 事件发布器
class EventPublisher {
    private Map<Class<? extends Event>, List<EventListener>> listeners = new HashMap<>();

    public void subscribe(Class<? extends Event> eventType, EventListener listener) {
        listeners.computeIfAbsent(eventType, k -> new ArrayList<>()).add(listener);
    }

    public void unsubscribe(Class<? extends Event> eventType, EventListener listener) {
        List<EventListener> eventListeners = listeners.get(eventType);
        if (eventListeners != null) {
            eventListeners.remove(listener);
        }
    }

    public void publish(Event event) {
        List<EventListener> eventListeners = listeners.get(event.getClass());
        if (eventListeners != null) {
            for (EventListener listener : eventListeners) {
                listener.onEvent(event);
            }
        }
    }
}

// 事件类
abstract class Event {
    private long timestamp;

    public Event() {
        this.timestamp = System.currentTimeMillis();
    }

    public long getTimestamp() {
        return timestamp;
    }
}

class UserLoginEvent extends Event {
    private String username;

    public UserLoginEvent(String username) {
        super();
        this.username = username;
    }

    public String getUsername() {
        return username;
    }
}

class OrderCreatedEvent extends Event {
    private String orderId;
    private double amount;

    public OrderCreatedEvent(String orderId, double amount) {
        super();
        this.orderId = orderId;
        this.amount = amount;
    }

    public String getOrderId() { return orderId; }
    public double getAmount() { return amount; }
}

// 具体监听器
class LoggingListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        System.out.println("日志记录：" + event.getClass().getSimpleName() +
                          " 发生于 " + new Date(event.getTimestamp()));
    }
}

class EmailNotificationListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        if (event instanceof UserLoginEvent) {
            UserLoginEvent loginEvent = (UserLoginEvent) event;
            System.out.println("发送邮件：用户 " + loginEvent.getUsername() + " 已登录");
        } else if (event instanceof OrderCreatedEvent) {
            OrderCreatedEvent orderEvent = (OrderCreatedEvent) event;
            System.out.println("发送邮件：订单 " + orderEvent.getOrderId() +
                             " 已创建，金额：$" + orderEvent.getAmount());
        }
    }
}

// 使用示例
public class EventDrivenExample {
    public static void main(String[] args) {
        EventPublisher publisher = new EventPublisher();

        // 注册监听器
        LoggingListener logger = new LoggingListener();
        EmailNotificationListener emailer = new EmailNotificationListener();

        publisher.subscribe(UserLoginEvent.class, logger);
        publisher.subscribe(UserLoginEvent.class, emailer);
        publisher.subscribe(OrderCreatedEvent.class, logger);
        publisher.subscribe(OrderCreatedEvent.class, emailer);

        // 发布事件
        System.out.println("=== 用户登录事件 ===");
        publisher.publish(new UserLoginEvent("张三"));

        System.out.println("\n=== 订单创建事件 ===");
        publisher.publish(new OrderCreatedEvent("ORD-001", 299.99));
    }
}
```

## ✅ 优势分析

### 1. **松耦合**
观察者和主题之间只通过抽象接口联系，彼此不需要知道具体实现细节。

### 2. **动态关系**
可以在运行时动态建立对象间的联系，支持观察者的动态添加和删除。

### 3. **广播通信**
主题可以向所有观察者广播通知，支持一对多的依赖关系。

### 4. **开闭原则**
可以独立扩展主题和观察者，无需修改现有代码。

## ⚠️ 注意事项

### 1. **内存泄漏风险**
```java
// 错误示例：忘记移除观察者
public class MemoryLeakExample {
    private WeatherStation station = new WeatherStation();

    public void createDisplay() {
        CurrentConditionsDisplay display = new CurrentConditionsDisplay(station);
        // 忘记在不需要时移除观察者，可能导致内存泄漏
    }
}

// 正确做法：及时清理
public class ProperCleanup {
    private WeatherStation station = new WeatherStation();
    private CurrentConditionsDisplay display;

    public void createDisplay() {
        display = new CurrentConditionsDisplay(station);
    }

    public void cleanup() {
        if (display != null) {
            station.removeObserver(display);
            display = null;
        }
    }
}
```

### 2. **通知顺序**
观察者的通知顺序可能影响程序行为，需要仔细设计。

### 3. **性能考虑**
大量观察者时通知成本较高，可以考虑异步通知。

```java
// 异步通知示例
class AsyncWeatherStation extends WeatherStation {
    private ExecutorService executor = Executors.newFixedThreadPool(5);

    @Override
    protected void notifyObservers() {
        for (Observer observer : observers) {
            executor.submit(() -> observer.update(temperature, humidity, pressure));
        }
    }

    public void shutdown() {
        executor.shutdown();
    }
}
```

## 🆚 与其他模式对比

| 特性 | 观察者模式 | 发布-订阅模式 | 中介者模式 |
|------|------------|---------------|------------|
| 耦合度 | 低耦合 | 完全解耦 | 中等耦合 |
| 通信方式 | 直接通知 | 通过消息代理 | 通过中介者 |
| 复杂度 | 简单 | 中等 | 较复杂 |
| 适用场景 | 对象状态变化 | 消息系统 | 复杂交互 |

## 🎯 实战建议

### 1. **选择合适的通知粒度**
```java
// 粗粒度通知
interface Observer {
    void update(Subject subject);  // 观察者自己获取需要的数据
}

// 细粒度通知
interface Observer {
    void update(String propertyName, Object newValue);  // 推送具体变化
}
```

### 2. **考虑使用事件总线**
对于复杂系统，可以考虑使用事件总线模式来管理观察者：

```java
@Component
public class EventBus {
    private final Map<Class<?>, List<Object>> subscribers = new ConcurrentHashMap<>();

    public void register(Object subscriber) {
        // 注册逻辑
    }

    public void post(Object event) {
        // 发布逻辑
    }
}
```

## 🧠 记忆技巧

**口诀：观察报纸订阅者**
- **观**察者模式很常见
- **察**看状态变化点
- **报**告所有订阅者
- **纸**上写下接口契约
- **订**阅可以动态调整
- **阅**读更新做响应
- **者**之间松耦合连接

**形象比喻：**
观察者模式就像**电视台和观众**的关系：
- 电视台（主题）播放节目
- 观众（观察者）收看节目
- 新节目播出时，所有观众都能看到
- 观众可以随时换台或关机

## 🎉 总结

观察者模式是一种优雅的设计模式，它实现了对象间的松耦合通信。通过定义一对多的依赖关系，当主题状态发生变化时，所有观察者都能自动得到通知并更新。

**核心思想：** 📡 让对象间的通信更优雅，实现松耦合的依赖关系！

下一篇我们将学习**策略模式**，看看如何让算法的选择变得更加灵活！ 🚀