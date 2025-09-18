---
title: "设计模式详解：装饰器模式(Decorator) - 动态扩展对象功能"
date: 2024-12-09T10:09:00+08:00
draft: false
tags: ["设计模式", "装饰器模式", "Decorator", "Java", "结构型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解装饰器模式，从基础概念到高级实现，包含功能扩展、链式装饰等实战技巧，让你彻底掌握动态增强对象能力的艺术"
---

## 🎯 什么是装饰器模式？

### 生活中的例子
想象一下给你的**咖啡加配料**：基础咖啡可以加牛奶、糖、奶泡、巧克力等。每加一种配料，价格就会增加，口味也会改变。你可以选择只加牛奶，也可以加牛奶+糖+奶泡。每一种配料都是对原始咖啡的"装饰"，最终得到一杯定制的咖啡。这就是装饰器模式的核心思想：**动态地给对象添加额外的功能，而不改变其原有结构**。

### 问题背景
在软件开发中，经常需要给对象动态添加功能：
- ☕ **饮品系统**：基础饮品 + 各种配料
- 🎨 **图形系统**：基础图形 + 边框、阴影、颜色等效果
- 📄 **文档处理**：基础文档 + 加密、压缩、格式化等功能
- 🌐 **Web请求**：基础请求 + 认证、缓存、日志等中间件
- 💰 **定价系统**：基础价格 + 折扣、税费、会员优惠等

如果使用继承来实现所有组合，会导致：
- 类爆炸问题（每种组合都需要一个类）
- 静态扩展，运行时无法改变
- 违反单一职责原则

## 🧠 设计思想

### 核心角色
1. **Component（组件接口）** - 定义基本功能接口
2. **ConcreteComponent（具体组件）** - 实现基本功能
3. **Decorator（装饰器抽象类）** - 装饰器基类
4. **ConcreteDecorator（具体装饰器）** - 实现具体的装饰功能

### 核心思想
- 使用组合代替继承
- 装饰器与被装饰对象实现相同接口
- 可以嵌套多层装饰器
- 运行时动态添加功能

### 记忆口诀
> **"包装增强，层层相套，功能叠加，动态灵活"**

## 💻 代码实现

### 1. 基础装饰器模式 - 咖啡订购系统

```java
/**
 * 组件接口 - 饮品
 */
public interface Beverage {
    String getDescription();
    double getCost();
}

/**
 * 具体组件 - 基础咖啡
 */
public class Espresso implements Beverage {
    @Override
    public String getDescription() {
        return "浓缩咖啡";
    }

    @Override
    public double getCost() {
        return 25.0;
    }
}

/**
 * 具体组件 - 美式咖啡
 */
public class Americano implements Beverage {
    @Override
    public String getDescription() {
        return "美式咖啡";
    }

    @Override
    public double getCost() {
        return 20.0;
    }
}

/**
 * 具体组件 - 拿铁
 */
public class Latte implements Beverage {
    @Override
    public String getDescription() {
        return "拿铁咖啡";
    }

    @Override
    public double getCost() {
        return 30.0;
    }
}

/**
 * 装饰器抽象类
 */
public abstract class BeverageDecorator implements Beverage {
    protected Beverage beverage; // 被装饰的饮品

    public BeverageDecorator(Beverage beverage) {
        this.beverage = beverage;
    }

    @Override
    public String getDescription() {
        return beverage.getDescription();
    }

    @Override
    public double getCost() {
        return beverage.getCost();
    }
}

/**
 * 具体装饰器 - 牛奶
 */
public class Milk extends BeverageDecorator {
    public Milk(Beverage beverage) {
        super(beverage);
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + " + 牛奶";
    }

    @Override
    public double getCost() {
        return beverage.getCost() + 3.0;
    }
}

/**
 * 具体装饰器 - 糖
 */
public class Sugar extends BeverageDecorator {
    public Sugar(Beverage beverage) {
        super(beverage);
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + " + 糖";
    }

    @Override
    public double getCost() {
        return beverage.getCost() + 1.0;
    }
}

/**
 * 具体装饰器 - 奶泡
 */
public class Foam extends BeverageDecorator {
    public Foam(Beverage beverage) {
        super(beverage);
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + " + 奶泡";
    }

    @Override
    public double getCost() {
        return beverage.getCost() + 2.5;
    }
}

/**
 * 具体装饰器 - 巧克力
 */
public class Chocolate extends BeverageDecorator {
    public Chocolate(Beverage beverage) {
        super(beverage);
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + " + 巧克力";
    }

    @Override
    public double getCost() {
        return beverage.getCost() + 4.0;
    }
}

/**
 * 具体装饰器 - 香草糖浆
 */
public class VanillaSyrup extends BeverageDecorator {
    public VanillaSyrup(Beverage beverage) {
        super(beverage);
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + " + 香草糖浆";
    }

    @Override
    public double getCost() {
        return beverage.getCost() + 3.5;
    }
}

// 咖啡订购系统演示
public class CoffeeDecoratorDemo {
    public static void main(String[] args) {
        System.out.println("=== 咖啡订购系统装饰器演示 ===");

        System.out.println("\n=== 基础饮品 ===");
        Beverage espresso = new Espresso();
        System.out.println(espresso.getDescription() + " - ¥" + espresso.getCost());

        Beverage americano = new Americano();
        System.out.println(americano.getDescription() + " - ¥" + americano.getCost());

        Beverage latte = new Latte();
        System.out.println(latte.getDescription() + " - ¥" + latte.getCost());

        System.out.println("\n=== 简单装饰 ===");
        // 浓缩咖啡 + 牛奶
        Beverage espressoWithMilk = new Milk(new Espresso());
        System.out.println(espressoWithMilk.getDescription() + " - ¥" + espressoWithMilk.getCost());

        // 美式咖啡 + 糖
        Beverage americanoWithSugar = new Sugar(new Americano());
        System.out.println(americanoWithSugar.getDescription() + " - ¥" + americanoWithSugar.getCost());

        System.out.println("\n=== 多重装饰 ===");
        // 拿铁 + 奶泡 + 巧克力
        Beverage fancyLatte = new Chocolate(new Foam(new Latte()));
        System.out.println(fancyLatte.getDescription() + " - ¥" + fancyLatte.getCost());

        // 浓缩咖啡 + 牛奶 + 糖 + 香草糖浆
        Beverage deluxeEspresso = new VanillaSyrup(new Sugar(new Milk(new Espresso())));
        System.out.println(deluxeEspresso.getDescription() + " - ¥" + deluxeEspresso.getCost());

        System.out.println("\n=== 复杂定制 ===");
        // 美式咖啡 + 双倍牛奶 + 糖 + 奶泡
        Beverage customAmericano = new Foam(new Sugar(new Milk(new Milk(new Americano()))));
        System.out.println(customAmericano.getDescription() + " - ¥" + customAmericano.getCost());

        // 拿铁 + 巧克力 + 香草糖浆 + 奶泡 + 糖
        Beverage ultimateLatte = new Sugar(new Foam(new VanillaSyrup(new Chocolate(new Latte()))));
        System.out.println(ultimateLatte.getDescription() + " - ¥" + ultimateLatte.getCost());

        System.out.println("\n=== 动态装饰演示 ===");
        Beverage dynamicBeverage = new Americano();
        System.out.println("起始: " + dynamicBeverage.getDescription() + " - ¥" + dynamicBeverage.getCost());

        // 逐步添加装饰
        dynamicBeverage = new Milk(dynamicBeverage);
        System.out.println("加奶: " + dynamicBeverage.getDescription() + " - ¥" + dynamicBeverage.getCost());

        dynamicBeverage = new Sugar(dynamicBeverage);
        System.out.println("加糖: " + dynamicBeverage.getDescription() + " - ¥" + dynamicBeverage.getCost());

        dynamicBeverage = new Foam(dynamicBeverage);
        System.out.println("加泡: " + dynamicBeverage.getDescription() + " - ¥" + dynamicBeverage.getCost());

        System.out.println("\n观察：可以灵活地组合各种配料，每种组合都是独特的！");
    }
}
```

### 2. 文本处理装饰器

```java
/**
 * 组件接口 - 文本处理器
 */
public interface TextProcessor {
    String process(String text);
    String getProcessingInfo();
}

/**
 * 具体组件 - 基础文本处理器
 */
public class SimpleTextProcessor implements TextProcessor {
    @Override
    public String process(String text) {
        return text;
    }

    @Override
    public String getProcessingInfo() {
        return "原始文本";
    }
}

/**
 * 装饰器抽象类
 */
public abstract class TextProcessorDecorator implements TextProcessor {
    protected TextProcessor textProcessor;

    public TextProcessorDecorator(TextProcessor textProcessor) {
        this.textProcessor = textProcessor;
    }

    @Override
    public String process(String text) {
        return textProcessor.process(text);
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo();
    }
}

/**
 * 具体装饰器 - 加密装饰器
 */
public class EncryptionDecorator extends TextProcessorDecorator {
    private String encryptionType;

    public EncryptionDecorator(TextProcessor textProcessor, String encryptionType) {
        super(textProcessor);
        this.encryptionType = encryptionType;
    }

    @Override
    public String process(String text) {
        String processedText = textProcessor.process(text);
        return encrypt(processedText);
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo() + " -> " + encryptionType + "加密";
    }

    private String encrypt(String text) {
        // 简单的加密模拟
        switch (encryptionType.toLowerCase()) {
            case "base64":
                return java.util.Base64.getEncoder().encodeToString(text.getBytes());
            case "reverse":
                return new StringBuilder(text).reverse().toString();
            case "caesar":
                return caesarCipher(text, 3);
            default:
                return "[" + encryptionType + "]" + text + "[/" + encryptionType + "]";
        }
    }

    private String caesarCipher(String text, int shift) {
        StringBuilder result = new StringBuilder();
        for (char c : text.toCharArray()) {
            if (Character.isLetter(c)) {
                char base = Character.isUpperCase(c) ? 'A' : 'a';
                c = (char) ((c - base + shift) % 26 + base);
            }
            result.append(c);
        }
        return result.toString();
    }
}

/**
 * 具体装饰器 - 压缩装饰器
 */
public class CompressionDecorator extends TextProcessorDecorator {
    private String compressionType;

    public CompressionDecorator(TextProcessor textProcessor, String compressionType) {
        super(textProcessor);
        this.compressionType = compressionType;
    }

    @Override
    public String process(String text) {
        String processedText = textProcessor.process(text);
        return compress(processedText);
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo() + " -> " + compressionType + "压缩";
    }

    private String compress(String text) {
        // 简单的压缩模拟
        switch (compressionType.toLowerCase()) {
            case "gzip":
                return "[GZIP:" + text.length() + "→" + (text.length() / 2) + "]" + text.substring(0, Math.min(10, text.length())) + "...";
            case "lz4":
                return "[LZ4:" + text.length() + "→" + (text.length() * 2 / 3) + "]" + text.substring(0, Math.min(8, text.length())) + "...";
            case "simple":
                // 简单的重复字符压缩
                return text.replaceAll("(.)\\1+", "$1");
            default:
                return "[" + compressionType + "]" + text;
        }
    }
}

/**
 * 具体装饰器 - 格式化装饰器
 */
public class FormattingDecorator extends TextProcessorDecorator {
    private String formatType;

    public FormattingDecorator(TextProcessor textProcessor, String formatType) {
        super(textProcessor);
        this.formatType = formatType;
    }

    @Override
    public String process(String text) {
        String processedText = textProcessor.process(text);
        return format(processedText);
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo() + " -> " + formatType + "格式化";
    }

    private String format(String text) {
        switch (formatType.toLowerCase()) {
            case "uppercase":
                return text.toUpperCase();
            case "lowercase":
                return text.toLowerCase();
            case "title":
                return toTitleCase(text);
            case "json":
                return "{\"content\":\"" + text.replace("\"", "\\\"") + "\"}";
            case "xml":
                return "<content>" + text.replace("<", "&lt;").replace(">", "&gt;") + "</content>";
            case "html":
                return "<p>" + text + "</p>";
            default:
                return "[" + formatType + "]" + text + "[/" + formatType + "]";
        }
    }

    private String toTitleCase(String text) {
        StringBuilder result = new StringBuilder();
        boolean capitalizeNext = true;

        for (char c : text.toCharArray()) {
            if (Character.isWhitespace(c)) {
                capitalizeNext = true;
                result.append(c);
            } else if (capitalizeNext) {
                result.append(Character.toUpperCase(c));
                capitalizeNext = false;
            } else {
                result.append(Character.toLowerCase(c));
            }
        }

        return result.toString();
    }
}

/**
 * 具体装饰器 - 日志装饰器
 */
public class LoggingDecorator extends TextProcessorDecorator {
    private String logLevel;

    public LoggingDecorator(TextProcessor textProcessor, String logLevel) {
        super(textProcessor);
        this.logLevel = logLevel;
    }

    @Override
    public String process(String text) {
        log("开始处理文本: " + text.substring(0, Math.min(20, text.length())) + "...");

        long startTime = System.currentTimeMillis();
        String result = textProcessor.process(text);
        long endTime = System.currentTimeMillis();

        log("处理完成，耗时: " + (endTime - startTime) + "ms，输出长度: " + result.length());

        return result;
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo() + " -> " + logLevel + "日志";
    }

    private void log(String message) {
        String timestamp = java.time.LocalTime.now().toString();
        System.out.println("[" + logLevel.toUpperCase() + " " + timestamp + "] " + message);
    }
}

/**
 * 具体装饰器 - 验证装饰器
 */
public class ValidationDecorator extends TextProcessorDecorator {
    private String validationType;

    public ValidationDecorator(TextProcessor textProcessor, String validationType) {
        super(textProcessor);
        this.validationType = validationType;
    }

    @Override
    public String process(String text) {
        if (!validate(text)) {
            throw new IllegalArgumentException("文本验证失败: " + validationType);
        }

        return textProcessor.process(text);
    }

    @Override
    public String getProcessingInfo() {
        return textProcessor.getProcessingInfo() + " -> " + validationType + "验证";
    }

    private boolean validate(String text) {
        switch (validationType.toLowerCase()) {
            case "not_empty":
                return text != null && !text.trim().isEmpty();
            case "max_length":
                return text.length() <= 1000;
            case "min_length":
                return text.length() >= 5;
            case "no_special_chars":
                return text.matches("[a-zA-Z0-9\\s]+");
            case "email":
                return text.matches("^[A-Za-z0-9+_.-]+@(.+)$");
            default:
                return true; // 默认通过验证
        }
    }
}

// 文本处理装饰器演示
public class TextProcessorDecoratorDemo {
    public static void main(String[] args) {
        System.out.println("=== 文本处理装饰器演示 ===");

        String sampleText = "Hello World! This is a sample text for processing.";

        System.out.println("\n=== 基础处理 ===");
        TextProcessor basicProcessor = new SimpleTextProcessor();
        System.out.println("处理链: " + basicProcessor.getProcessingInfo());
        System.out.println("结果: " + basicProcessor.process(sampleText));

        System.out.println("\n=== 单一装饰 ===");
        // 只进行格式化
        TextProcessor uppercaseProcessor = new FormattingDecorator(new SimpleTextProcessor(), "uppercase");
        System.out.println("处理链: " + uppercaseProcessor.getProcessingInfo());
        System.out.println("结果: " + uppercaseProcessor.process(sampleText));

        // 只进行加密
        TextProcessor encryptedProcessor = new EncryptionDecorator(new SimpleTextProcessor(), "caesar");
        System.out.println("\n处理链: " + encryptedProcessor.getProcessingInfo());
        System.out.println("结果: " + encryptedProcessor.process(sampleText));

        System.out.println("\n=== 多重装饰 ===");
        // 格式化 -> 加密 -> 压缩
        TextProcessor complexProcessor = new CompressionDecorator(
            new EncryptionDecorator(
                new FormattingDecorator(new SimpleTextProcessor(), "uppercase"),
                "base64"
            ),
            "gzip"
        );

        System.out.println("处理链: " + complexProcessor.getProcessingInfo());
        System.out.println("结果: " + complexProcessor.process(sampleText));

        System.out.println("\n=== 带验证和日志的处理链 ===");
        // 验证 -> 格式化 -> 加密 -> 日志
        TextProcessor secureProcessor = new LoggingDecorator(
            new EncryptionDecorator(
                new FormattingDecorator(
                    new ValidationDecorator(new SimpleTextProcessor(), "not_empty"),
                    "title"
                ),
                "reverse"
            ),
            "info"
        );

        System.out.println("处理链: " + secureProcessor.getProcessingInfo());
        System.out.println("结果: " + secureProcessor.process(sampleText));

        System.out.println("\n=== 动态构建处理链 ===");
        TextProcessor dynamicProcessor = new SimpleTextProcessor();
        System.out.println("初始: " + dynamicProcessor.getProcessingInfo());

        // 逐步添加装饰器
        dynamicProcessor = new ValidationDecorator(dynamicProcessor, "min_length");
        System.out.println("加入验证: " + dynamicProcessor.getProcessingInfo());

        dynamicProcessor = new FormattingDecorator(dynamicProcessor, "json");
        System.out.println("加入格式化: " + dynamicProcessor.getProcessingInfo());

        dynamicProcessor = new CompressionDecorator(dynamicProcessor, "simple");
        System.out.println("加入压缩: " + dynamicProcessor.getProcessingInfo());

        dynamicProcessor = new LoggingDecorator(dynamicProcessor, "debug");
        System.out.println("加入日志: " + dynamicProcessor.getProcessingInfo());

        System.out.println("\n最终处理结果:");
        String finalResult = dynamicProcessor.process("hello world hello world hello");
        System.out.println("输出: " + finalResult);

        System.out.println("\n=== 错误处理演示 ===");
        try {
            TextProcessor failProcessor = new ValidationDecorator(new SimpleTextProcessor(), "min_length");
            failProcessor.process("hi"); // 太短，验证失败
        } catch (Exception e) {
            System.out.println("验证失败: " + e.getMessage());
        }

        System.out.println("\n=== 不同类型文本处理 ===");
        String[] texts = {
            "user@example.com",
            "THIS IS UPPERCASE TEXT",
            "hello world hello world hello world",
            "Special chars: @#$%^&*()"
        };

        for (String text : texts) {
            System.out.println("\n处理文本: \"" + text + "\"");

            // 邮箱验证 + HTML格式化
            try {
                TextProcessor emailProcessor = new FormattingDecorator(
                    new ValidationDecorator(new SimpleTextProcessor(), "email"),
                    "html"
                );
                System.out.println("邮箱处理: " + emailProcessor.process(text));
            } catch (Exception e) {
                System.out.println("邮箱处理失败: " + e.getMessage());
            }

            // 字符验证 + 小写格式化 + 简单压缩
            try {
                TextProcessor cleanProcessor = new CompressionDecorator(
                    new FormattingDecorator(
                        new ValidationDecorator(new SimpleTextProcessor(), "no_special_chars"),
                        "lowercase"
                    ),
                    "simple"
                );
                System.out.println("清洁处理: " + cleanProcessor.process(text));
            } catch (Exception e) {
                System.out.println("清洁处理失败: " + e.getMessage());
            }
        }

        System.out.println("\n观察：可以根据需要动态组合不同的处理步骤！");
    }
}
```

### 3. 网络请求装饰器

```java
/**
 * 组件接口 - HTTP请求
 */
public interface HttpRequest {
    String execute();
    String getRequestInfo();
}

/**
 * 具体组件 - 基础HTTP请求
 */
public class BasicHttpRequest implements HttpRequest {
    private String url;
    private String method;
    private String body;

    public BasicHttpRequest(String url, String method, String body) {
        this.url = url;
        this.method = method;
        this.body = body;
    }

    @Override
    public String execute() {
        // 模拟HTTP请求执行
        return "Response from " + url + " using " + method;
    }

    @Override
    public String getRequestInfo() {
        return method + " " + url;
    }

    public String getUrl() { return url; }
    public String getMethod() { return method; }
    public String getBody() { return body; }
}

/**
 * 装饰器抽象类
 */
public abstract class HttpRequestDecorator implements HttpRequest {
    protected HttpRequest request;

    public HttpRequestDecorator(HttpRequest request) {
        this.request = request;
    }

    @Override
    public String execute() {
        return request.execute();
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo();
    }
}

/**
 * 具体装饰器 - 认证装饰器
 */
public class AuthenticationDecorator extends HttpRequestDecorator {
    private String authType;
    private String credentials;

    public AuthenticationDecorator(HttpRequest request, String authType, String credentials) {
        super(request);
        this.authType = authType;
        this.credentials = credentials;
    }

    @Override
    public String execute() {
        authenticate();
        return request.execute();
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [Auth: " + authType + "]";
    }

    private void authenticate() {
        System.out.println("🔐 执行" + authType + "认证");
        switch (authType.toLowerCase()) {
            case "bearer":
                System.out.println("   添加 Authorization: Bearer " + credentials);
                break;
            case "basic":
                System.out.println("   添加 Authorization: Basic " +
                                 java.util.Base64.getEncoder().encodeToString(credentials.getBytes()));
                break;
            case "api_key":
                System.out.println("   添加 X-API-Key: " + credentials);
                break;
            default:
                System.out.println("   使用自定义认证: " + authType);
        }
    }
}

/**
 * 具体装饰器 - 缓存装饰器
 */
public class CacheDecorator extends HttpRequestDecorator {
    private static Map<String, String> cache = new HashMap<>();
    private int cacheExpireMinutes;

    public CacheDecorator(HttpRequest request, int cacheExpireMinutes) {
        super(request);
        this.cacheExpireMinutes = cacheExpireMinutes;
    }

    @Override
    public String execute() {
        String cacheKey = generateCacheKey();

        // 检查缓存
        if (cache.containsKey(cacheKey)) {
            System.out.println("💾 缓存命中: " + cacheKey);
            return "CACHED: " + cache.get(cacheKey);
        }

        // 执行请求
        System.out.println("🌐 缓存未命中，执行网络请求");
        String response = request.execute();

        // 存入缓存
        cache.put(cacheKey, response);
        System.out.println("💾 结果已缓存，过期时间: " + cacheExpireMinutes + " 分钟");

        return response;
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [Cache: " + cacheExpireMinutes + "min]";
    }

    private String generateCacheKey() {
        return request.getRequestInfo().hashCode() + "";
    }

    public static void clearCache() {
        cache.clear();
        System.out.println("💾 缓存已清空");
    }
}

/**
 * 具体装饰器 - 重试装饰器
 */
public class RetryDecorator extends HttpRequestDecorator {
    private int maxRetries;
    private int retryDelayMs;

    public RetryDecorator(HttpRequest request, int maxRetries, int retryDelayMs) {
        super(request);
        this.maxRetries = maxRetries;
        this.retryDelayMs = retryDelayMs;
    }

    @Override
    public String execute() {
        int attempt = 1;

        while (attempt <= maxRetries) {
            try {
                System.out.println("🔄 第 " + attempt + " 次请求尝试");

                // 模拟网络请求可能失败
                if (Math.random() < 0.3 && attempt < maxRetries) { // 30%失败率
                    throw new RuntimeException("网络请求失败");
                }

                String response = request.execute();

                if (attempt > 1) {
                    System.out.println("✅ 重试成功");
                }

                return response;

            } catch (Exception e) {
                System.out.println("❌ 第 " + attempt + " 次尝试失败: " + e.getMessage());

                if (attempt == maxRetries) {
                    System.out.println("💥 达到最大重试次数，请求最终失败");
                    throw new RuntimeException("请求失败，已重试 " + maxRetries + " 次");
                }

                // 等待后重试
                try {
                    Thread.sleep(retryDelayMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    break;
                }

                attempt++;
            }
        }

        throw new RuntimeException("重试逻辑异常终止");
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [Retry: " + maxRetries + "x]";
    }
}

/**
 * 具体装饰器 - 日志装饰器
 */
public class RequestLoggingDecorator extends HttpRequestDecorator {
    private String logLevel;

    public RequestLoggingDecorator(HttpRequest request, String logLevel) {
        super(request);
        this.logLevel = logLevel;
    }

    @Override
    public String execute() {
        long startTime = System.currentTimeMillis();

        log("开始执行请求: " + request.getRequestInfo());

        try {
            String response = request.execute();
            long duration = System.currentTimeMillis() - startTime;

            log("请求成功完成，耗时: " + duration + "ms");
            log("响应预览: " + response.substring(0, Math.min(50, response.length())) + "...");

            return response;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;

            log("请求失败，耗时: " + duration + "ms，错误: " + e.getMessage());
            throw e;
        }
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [Log: " + logLevel + "]";
    }

    private void log(String message) {
        String timestamp = java.time.LocalTime.now().toString();
        String level = logLevel.toUpperCase();
        System.out.println("[" + level + " " + timestamp + "] " + message);
    }
}

/**
 * 具体装饰器 - 速率限制装饰器
 */
public class RateLimitDecorator extends HttpRequestDecorator {
    private static Map<String, Long> lastRequestTime = new HashMap<>();
    private long minIntervalMs;

    public RateLimitDecorator(HttpRequest request, long minIntervalMs) {
        super(request);
        this.minIntervalMs = minIntervalMs;
    }

    @Override
    public String execute() {
        String rateLimitKey = getRateLimitKey();
        long currentTime = System.currentTimeMillis();

        Long lastTime = lastRequestTime.get(rateLimitKey);
        if (lastTime != null) {
            long timeSinceLastRequest = currentTime - lastTime;
            if (timeSinceLastRequest < minIntervalMs) {
                long waitTime = minIntervalMs - timeSinceLastRequest;
                System.out.println("⏱️ 速率限制：需要等待 " + waitTime + "ms");

                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("等待被中断");
                }
            }
        }

        // 更新最后请求时间
        lastRequestTime.put(rateLimitKey, System.currentTimeMillis());

        return request.execute();
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [RateLimit: " + minIntervalMs + "ms]";
    }

    private String getRateLimitKey() {
        // 简化：使用请求信息作为限流键
        return request.getRequestInfo();
    }
}

/**
 * 具体装饰器 - 性能监控装饰器
 */
public class PerformanceMonitoringDecorator extends HttpRequestDecorator {
    private static Map<String, List<Long>> performanceStats = new HashMap<>();

    public PerformanceMonitoringDecorator(HttpRequest request) {
        super(request);
    }

    @Override
    public String execute() {
        long startTime = System.nanoTime();

        try {
            String response = request.execute();

            long endTime = System.nanoTime();
            long durationMs = (endTime - startTime) / 1_000_000;

            recordPerformance(durationMs);

            return response;

        } catch (Exception e) {
            long endTime = System.nanoTime();
            long durationMs = (endTime - startTime) / 1_000_000;

            recordPerformance(durationMs);
            throw e;
        }
    }

    @Override
    public String getRequestInfo() {
        return request.getRequestInfo() + " [Monitor]";
    }

    private void recordPerformance(long durationMs) {
        String key = request.getRequestInfo();
        performanceStats.computeIfAbsent(key, k -> new ArrayList<>()).add(durationMs);

        System.out.println("📊 性能记录: " + durationMs + "ms");
    }

    public static void printPerformanceStats() {
        System.out.println("\n📊 === 性能统计报告 ===");
        for (Map.Entry<String, List<Long>> entry : performanceStats.entrySet()) {
            List<Long> times = entry.getValue();
            if (!times.isEmpty()) {
                double avgTime = times.stream().mapToLong(Long::longValue).average().orElse(0.0);
                long minTime = times.stream().mapToLong(Long::longValue).min().orElse(0);
                long maxTime = times.stream().mapToLong(Long::longValue).max().orElse(0);

                System.out.println("请求: " + entry.getKey());
                System.out.println("  调用次数: " + times.size());
                System.out.println("  平均耗时: " + String.format("%.2f", avgTime) + "ms");
                System.out.println("  最小耗时: " + minTime + "ms");
                System.out.println("  最大耗时: " + maxTime + "ms");
            }
        }
    }
}

// 网络请求装饰器演示
public class HttpRequestDecoratorDemo {
    public static void main(String[] args) {
        System.out.println("=== 网络请求装饰器演示 ===");

        System.out.println("\n=== 基础请求 ===");
        HttpRequest basicRequest = new BasicHttpRequest("https://api.example.com/users", "GET", null);
        System.out.println("请求信息: " + basicRequest.getRequestInfo());
        System.out.println("响应: " + basicRequest.execute());

        System.out.println("\n=== 带认证的请求 ===");
        HttpRequest authRequest = new AuthenticationDecorator(
            new BasicHttpRequest("https://api.example.com/private", "GET", null),
            "bearer",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        );
        System.out.println("请求信息: " + authRequest.getRequestInfo());
        System.out.println("响应: " + authRequest.execute());

        System.out.println("\n=== 带缓存的请求 ===");
        HttpRequest cachedRequest = new CacheDecorator(
            new BasicHttpRequest("https://api.example.com/products", "GET", null),
            30 // 30分钟缓存
        );

        System.out.println("第一次请求:");
        System.out.println("请求信息: " + cachedRequest.getRequestInfo());
        System.out.println("响应: " + cachedRequest.execute());

        System.out.println("\n第二次请求:");
        System.out.println("响应: " + cachedRequest.execute());

        System.out.println("\n=== 复杂请求链 ===");
        // 认证 + 缓存 + 重试 + 日志 + 性能监控
        HttpRequest complexRequest = new PerformanceMonitoringDecorator(
            new RequestLoggingDecorator(
                new RetryDecorator(
                    new CacheDecorator(
                        new AuthenticationDecorator(
                            new BasicHttpRequest("https://api.example.com/orders", "POST", "{\"item\":\"laptop\"}"),
                            "api_key",
                            "abc123def456"
                        ),
                        15 // 15分钟缓存
                    ),
                    3, // 最多重试3次
                    1000 // 重试间隔1秒
                ),
                "info"
            )
        );

        System.out.println("复杂请求信息: " + complexRequest.getRequestInfo());
        try {
            String response = complexRequest.execute();
            System.out.println("最终响应: " + response);
        } catch (Exception e) {
            System.out.println("请求失败: " + e.getMessage());
        }

        System.out.println("\n=== 速率限制演示 ===");
        HttpRequest rateLimitedRequest = new RateLimitDecorator(
            new BasicHttpRequest("https://api.example.com/search", "GET", null),
            2000 // 2秒间隔
        );

        // 连续发送多个请求
        for (int i = 1; i <= 3; i++) {
            System.out.println("\n第 " + i + " 个请求:");
            long startTime = System.currentTimeMillis();
            rateLimitedRequest.execute();
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("实际耗时: " + duration + "ms");
        }

        System.out.println("\n=== 动态构建请求装饰链 ===");
        HttpRequest dynamicRequest = new BasicHttpRequest("https://api.example.com/analytics", "GET", null);

        System.out.println("基础请求: " + dynamicRequest.getRequestInfo());

        // 逐步添加装饰器
        dynamicRequest = new PerformanceMonitoringDecorator(dynamicRequest);
        System.out.println("添加性能监控: " + dynamicRequest.getRequestInfo());

        dynamicRequest = new CacheDecorator(dynamicRequest, 60);
        System.out.println("添加缓存: " + dynamicRequest.getRequestInfo());

        dynamicRequest = new AuthenticationDecorator(dynamicRequest, "basic", "user:pass");
        System.out.println("添加认证: " + dynamicRequest.getRequestInfo());

        dynamicRequest = new RequestLoggingDecorator(dynamicRequest, "debug");
        System.out.println("添加日志: " + dynamicRequest.getRequestInfo());

        // 执行最终请求
        System.out.println("\n执行动态构建的请求:");
        dynamicRequest.execute();

        System.out.println("\n=== 批量请求测试 ===");
        String[] endpoints = {
            "https://api.example.com/users",
            "https://api.example.com/products",
            "https://api.example.com/orders"
        };

        for (String endpoint : endpoints) {
            HttpRequest batchRequest = new PerformanceMonitoringDecorator(
                new CacheDecorator(
                    new BasicHttpRequest(endpoint, "GET", null),
                    45
                )
            );

            System.out.println("\n请求: " + endpoint);
            batchRequest.execute();
        }

        // 清除缓存
        CacheDecorator.clearCache();

        // 显示性能统计
        PerformanceMonitoringDecorator.printPerformanceStats();

        System.out.println("\n观察：可以灵活组合各种中间件功能，构建强大的HTTP客户端！");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **动态扩展功能**
   - 运行时添加或删除功能
   - 比继承更加灵活

2. **符合开闭原则**
   - 对扩展开放，对修改关闭
   - 新增装饰器不影响现有代码

3. **职责单一**
   - 每个装饰器专注一个功能
   - 便于理解和维护

4. **组合灵活**
   - 可以任意组合装饰器
   - 支持多层嵌套

### ❌ 缺点

1. **对象层次复杂**
   - 多层装饰器可能导致调试困难
   - 对象创建过程复杂

2. **性能开销**
   - 多层委托调用
   - 内存占用增加

3. **接口一致性要求**
   - 装饰器必须与被装饰对象实现相同接口
   - 可能导致接口臃肿

## 🎯 使用场景总结

### 适合使用装饰器模式的场景：
- ☕ **配料系统** - 动态添加各种配料
- 🔐 **中间件系统** - 认证、缓存、日志等功能
- 🎨 **图形渲染** - 边框、阴影、滤镜等效果
- 📄 **文档处理** - 格式化、加密、压缩等操作
- 🌐 **网络请求** - 重试、缓存、认证等增强

### 不适合使用装饰器模式的场景：
- 功能比较固定，不需要动态组合
- 装饰器数量很少
- 性能要求极高，不能承受多层调用
- 被装饰对象的接口经常变化

## 🧠 记忆技巧

### 形象比喻
> **装饰器模式就像是 "穿衣服"**：
> - 人是被装饰的对象（基础功能）
> - 衣服是装饰器（附加功能）
> - 可以穿多层衣服（多重装饰）
> - 每层衣服都有特定作用（单一职责）
> - 脱掉衣服人还是人（不改变原有结构）

### 设计要点
> **"包装一层，功能一层，层层嵌套，功能叠加"**

### 与代理模式的区别
- **装饰器模式**：强调功能增强，一般会改变输出
- **代理模式**：强调控制访问，一般不改变接口功能

## 🔧 最佳实践

### 1. 装饰器工厂模式

```java
/**
 * 装饰器构建器
 */
public class BeverageBuilder {
    private Beverage beverage;

    public BeverageBuilder(Beverage baseBeverage) {
        this.beverage = baseBeverage;
    }

    public BeverageBuilder addMilk() {
        beverage = new Milk(beverage);
        return this;
    }

    public BeverageBuilder addSugar() {
        beverage = new Sugar(beverage);
        return this;
    }

    public BeverageBuilder addFoam() {
        beverage = new Foam(beverage);
        return this;
    }

    public Beverage build() {
        return beverage;
    }
}

// 使用示例
Beverage customCoffee = new BeverageBuilder(new Espresso())
    .addMilk()
    .addSugar()
    .addFoam()
    .build();
```

### 2. 条件装饰器

```java
/**
 * 条件装饰器
 */
public class ConditionalDecorator extends BeverageDecorator {
    private Predicate<Beverage> condition;
    private Function<Beverage, Beverage> decorator;

    public ConditionalDecorator(Beverage beverage, Predicate<Beverage> condition,
                               Function<Beverage, Beverage> decorator) {
        super(beverage);
        this.condition = condition;
        this.decorator = decorator;
    }

    @Override
    public String getDescription() {
        if (condition.test(beverage)) {
            return decorator.apply(beverage).getDescription();
        }
        return beverage.getDescription();
    }

    @Override
    public double getCost() {
        if (condition.test(beverage)) {
            return decorator.apply(beverage).getCost();
        }
        return beverage.getCost();
    }
}
```

### 3. 装饰器注册器

```java
/**
 * 装饰器注册和管理
 */
public class DecoratorRegistry {
    private static final Map<String, Function<Beverage, Beverage>> decorators = new HashMap<>();

    static {
        decorators.put("milk", Milk::new);
        decorators.put("sugar", Sugar::new);
        decorators.put("foam", Foam::new);
        decorators.put("chocolate", Chocolate::new);
    }

    public static Beverage applyDecorators(Beverage base, String... decoratorNames) {
        Beverage result = base;
        for (String name : decoratorNames) {
            Function<Beverage, Beverage> decorator = decorators.get(name.toLowerCase());
            if (decorator != null) {
                result = decorator.apply(result);
            }
        }
        return result;
    }
}
```

## 🚀 总结

装饰器模式通过动态组合的方式为对象添加功能，特别适用于：

- **需要动态扩展功能**的场景
- **功能组合多样化**的系统
- **中间件架构**的设计

核心思想：
- **组合优于继承**
- **动态功能扩展**
- **职责单一原则**

设计要点：
- **统一的组件接口**
- **装饰器的可嵌套性**
- **功能的正交性**

记住，**装饰器模式是功能增强器，不是结构修改器**，要在合适的功能扩展场景下使用！

---
*下一篇：外观模式 - 简化复杂子系统的访问*