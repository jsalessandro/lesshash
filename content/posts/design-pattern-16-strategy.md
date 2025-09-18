---
title: "设计模式入门教程16：策略模式 - 让算法选择更灵活"
date: 2024-12-16T10:16:00+08:00
draft: false
tags: ["设计模式", "策略模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是策略模式？

策略模式（Strategy Pattern）是一种行为型设计模式，它定义了一系列算法，把它们一个个封装起来，并且使它们可以相互替换。策略模式让算法的变化独立于使用算法的客户端。

### 🌟 现实生活中的例子

想象一下出行的场景：
- **目标**：从家到公司
- **策略**：开车、坐地铁、骑自行车、步行
- **选择**：根据天气、时间、预算等因素选择最合适的策略
- **替换**：可以随时改变出行方式

这就是策略模式的精髓！

## 🏗️ 模式结构

```java
// 策略接口
interface Strategy {
    void execute();
}

// 具体策略A
class ConcreteStrategyA implements Strategy {
    @Override
    public void execute() {
        System.out.println("执行策略A");
    }
}

// 具体策略B
class ConcreteStrategyB implements Strategy {
    @Override
    public void execute() {
        System.out.println("执行策略B");
    }
}

// 上下文类
class Context {
    private Strategy strategy;

    public Context(Strategy strategy) {
        this.strategy = strategy;
    }

    public void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }

    public void executeStrategy() {
        strategy.execute();
    }
}
```

## 💡 核心组件详解

### 1. 抽象策略（Strategy）
```java
// 排序策略接口
interface SortStrategy {
    void sort(int[] array);
    String getStrategyName();
}
```

### 2. 具体策略（ConcreteStrategy）
```java
// 冒泡排序策略
class BubbleSortStrategy implements SortStrategy {
    @Override
    public void sort(int[] array) {
        System.out.println("使用冒泡排序...");
        int n = array.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (array[j] > array[j + 1]) {
                    // 交换元素
                    int temp = array[j];
                    array[j] = array[j + 1];
                    array[j + 1] = temp;
                }
            }
        }
    }

    @Override
    public String getStrategyName() {
        return "冒泡排序";
    }
}

// 快速排序策略
class QuickSortStrategy implements SortStrategy {
    @Override
    public void sort(int[] array) {
        System.out.println("使用快速排序...");
        quickSort(array, 0, array.length - 1);
    }

    private void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high);
            quickSort(arr, low, pi - 1);
            quickSort(arr, pi + 1, high);
        }
    }

    private int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = (low - 1);

        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }

        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        return i + 1;
    }

    @Override
    public String getStrategyName() {
        return "快速排序";
    }
}

// 归并排序策略
class MergeSortStrategy implements SortStrategy {
    @Override
    public void sort(int[] array) {
        System.out.println("使用归并排序...");
        mergeSort(array, 0, array.length - 1);
    }

    private void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }

    private void merge(int[] arr, int left, int mid, int right) {
        int n1 = mid - left + 1;
        int n2 = right - mid;

        int[] leftArr = new int[n1];
        int[] rightArr = new int[n2];

        System.arraycopy(arr, left, leftArr, 0, n1);
        System.arraycopy(arr, mid + 1, rightArr, 0, n2);

        int i = 0, j = 0, k = left;

        while (i < n1 && j < n2) {
            if (leftArr[i] <= rightArr[j]) {
                arr[k] = leftArr[i];
                i++;
            } else {
                arr[k] = rightArr[j];
                j++;
            }
            k++;
        }

        while (i < n1) {
            arr[k] = leftArr[i];
            i++;
            k++;
        }

        while (j < n2) {
            arr[k] = rightArr[j];
            j++;
            k++;
        }
    }

    @Override
    public String getStrategyName() {
        return "归并排序";
    }
}
```

### 3. 上下文（Context）
```java
// 排序上下文
class SortContext {
    private SortStrategy strategy;

    public SortContext(SortStrategy strategy) {
        this.strategy = strategy;
    }

    public void setStrategy(SortStrategy strategy) {
        this.strategy = strategy;
        System.out.println("切换到：" + strategy.getStrategyName());
    }

    public void performSort(int[] array) {
        System.out.println("排序前：" + Arrays.toString(array));

        long startTime = System.currentTimeMillis();
        strategy.sort(array);
        long endTime = System.currentTimeMillis();

        System.out.println("排序后：" + Arrays.toString(array));
        System.out.println("耗时：" + (endTime - startTime) + " ms");
        System.out.println("策略：" + strategy.getStrategyName());
        System.out.println("=".repeat(50));
    }
}
```

## 🎮 实际应用示例

### 示例1：支付方式选择
```java
// 支付策略接口
interface PaymentStrategy {
    boolean pay(double amount);
    String getPaymentMethod();
}

// 信用卡支付策略
class CreditCardPayment implements PaymentStrategy {
    private String cardNumber;
    private String holderName;
    private String cvv;
    private String expiry;

    public CreditCardPayment(String cardNumber, String holderName, String cvv, String expiry) {
        this.cardNumber = cardNumber;
        this.holderName = holderName;
        this.cvv = cvv;
        this.expiry = expiry;
    }

    @Override
    public boolean pay(double amount) {
        System.out.println("使用信用卡支付 $" + amount);
        System.out.println("卡号：" + maskCardNumber(cardNumber));
        System.out.println("持卡人：" + holderName);
        // 模拟支付处理
        System.out.println("连接银行网关...");
        System.out.println("验证信用卡信息...");
        System.out.println("支付成功！");
        return true;
    }

    private String maskCardNumber(String cardNumber) {
        return "**** **** **** " + cardNumber.substring(cardNumber.length() - 4);
    }

    @Override
    public String getPaymentMethod() {
        return "信用卡";
    }
}

// PayPal支付策略
class PayPalPayment implements PaymentStrategy {
    private String email;
    private String password;

    public PayPalPayment(String email, String password) {
        this.email = email;
        this.password = password;
    }

    @Override
    public boolean pay(double amount) {
        System.out.println("使用PayPal支付 $" + amount);
        System.out.println("邮箱：" + email);
        // 模拟支付处理
        System.out.println("连接PayPal API...");
        System.out.println("验证用户凭据...");
        System.out.println("支付成功！");
        return true;
    }

    @Override
    public String getPaymentMethod() {
        return "PayPal";
    }
}

// 微信支付策略
class WeChatPayment implements PaymentStrategy {
    private String phoneNumber;

    public WeChatPayment(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    @Override
    public boolean pay(double amount) {
        System.out.println("使用微信支付 ¥" + amount);
        System.out.println("手机号：" + phoneNumber);
        // 模拟支付处理
        System.out.println("生成二维码...");
        System.out.println("等待用户扫码...");
        System.out.println("支付成功！");
        return true;
    }

    @Override
    public String getPaymentMethod() {
        return "微信支付";
    }
}

// 支付宝支付策略
class AlipayPayment implements PaymentStrategy {
    private String account;

    public AlipayPayment(String account) {
        this.account = account;
    }

    @Override
    public boolean pay(double amount) {
        System.out.println("使用支付宝支付 ¥" + amount);
        System.out.println("账户：" + account);
        // 模拟支付处理
        System.out.println("连接支付宝网关...");
        System.out.println("验证用户身份...");
        System.out.println("支付成功！");
        return true;
    }

    @Override
    public String getPaymentMethod() {
        return "支付宝";
    }
}

// 支付上下文
class PaymentContext {
    private PaymentStrategy strategy;

    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.strategy = strategy;
        System.out.println("已选择支付方式：" + strategy.getPaymentMethod());
    }

    public boolean executePayment(double amount) {
        if (strategy == null) {
            System.out.println("请先选择支付方式！");
            return false;
        }
        return strategy.pay(amount);
    }
}

// 使用示例
public class PaymentExample {
    public static void main(String[] args) {
        PaymentContext paymentContext = new PaymentContext();

        // 场景1：使用信用卡支付
        System.out.println("=== 国外购物场景 ===");
        paymentContext.setPaymentStrategy(
            new CreditCardPayment("1234567890123456", "张三", "123", "12/25")
        );
        paymentContext.executePayment(299.99);

        System.out.println("\n=== 国内网购场景 ===");
        // 场景2：使用支付宝支付
        paymentContext.setPaymentStrategy(new AlipayPayment("zhangsan@example.com"));
        paymentContext.executePayment(159.00);

        System.out.println("\n=== 线下扫码支付场景 ===");
        // 场景3：使用微信支付
        paymentContext.setPaymentStrategy(new WeChatPayment("138****8888"));
        paymentContext.executePayment(88.88);

        System.out.println("\n=== 跨境电商场景 ===");
        // 场景4：使用PayPal支付
        paymentContext.setPaymentStrategy(new PayPalPayment("user@example.com", "password"));
        paymentContext.executePayment(199.99);
    }
}
```

### 示例2：数据压缩策略
```java
// 压缩策略接口
interface CompressionStrategy {
    byte[] compress(String data);
    String decompress(byte[] compressedData);
    String getCompressionType();
    double getCompressionRatio(String originalData, byte[] compressedData);
}

// ZIP压缩策略
class ZipCompressionStrategy implements CompressionStrategy {
    @Override
    public byte[] compress(String data) {
        System.out.println("使用ZIP压缩算法...");
        // 模拟ZIP压缩
        return simulateCompression(data, 0.6);
    }

    @Override
    public String decompress(byte[] compressedData) {
        System.out.println("使用ZIP解压算法...");
        return "解压后的数据";
    }

    @Override
    public String getCompressionType() {
        return "ZIP";
    }

    @Override
    public double getCompressionRatio(String originalData, byte[] compressedData) {
        return (double) compressedData.length / originalData.getBytes().length;
    }

    private byte[] simulateCompression(String data, double ratio) {
        int compressedSize = (int) (data.getBytes().length * ratio);
        return new byte[compressedSize];
    }
}

// GZIP压缩策略
class GzipCompressionStrategy implements CompressionStrategy {
    @Override
    public byte[] compress(String data) {
        System.out.println("使用GZIP压缩算法...");
        return simulateCompression(data, 0.5);
    }

    @Override
    public String decompress(byte[] compressedData) {
        System.out.println("使用GZIP解压算法...");
        return "解压后的数据";
    }

    @Override
    public String getCompressionType() {
        return "GZIP";
    }

    @Override
    public double getCompressionRatio(String originalData, byte[] compressedData) {
        return (double) compressedData.length / originalData.getBytes().length;
    }

    private byte[] simulateCompression(String data, double ratio) {
        int compressedSize = (int) (data.getBytes().length * ratio);
        return new byte[compressedSize];
    }
}

// LZ4压缩策略
class Lz4CompressionStrategy implements CompressionStrategy {
    @Override
    public byte[] compress(String data) {
        System.out.println("使用LZ4压缩算法...");
        return simulateCompression(data, 0.7);
    }

    @Override
    public String decompress(byte[] compressedData) {
        System.out.println("使用LZ4解压算法...");
        return "解压后的数据";
    }

    @Override
    public String getCompressionType() {
        return "LZ4";
    }

    @Override
    public double getCompressionRatio(String originalData, byte[] compressedData) {
        return (double) compressedData.length / originalData.getBytes().length;
    }

    private byte[] simulateCompression(String data, double ratio) {
        int compressedSize = (int) (data.getBytes().length * ratio);
        return new byte[compressedSize];
    }
}

// 压缩上下文
class CompressionContext {
    private CompressionStrategy strategy;

    public void setCompressionStrategy(CompressionStrategy strategy) {
        this.strategy = strategy;
    }

    public CompressionResult compressData(String data) {
        if (strategy == null) {
            throw new IllegalStateException("压缩策略未设置");
        }

        System.out.println("原始数据大小：" + data.getBytes().length + " 字节");

        long startTime = System.currentTimeMillis();
        byte[] compressedData = strategy.compress(data);
        long endTime = System.currentTimeMillis();

        double ratio = strategy.getCompressionRatio(data, compressedData);

        return new CompressionResult(
            compressedData,
            strategy.getCompressionType(),
            ratio,
            endTime - startTime
        );
    }
}

// 压缩结果类
class CompressionResult {
    private byte[] compressedData;
    private String algorithm;
    private double compressionRatio;
    private long compressionTime;

    public CompressionResult(byte[] compressedData, String algorithm,
                           double compressionRatio, long compressionTime) {
        this.compressedData = compressedData;
        this.algorithm = algorithm;
        this.compressionRatio = compressionRatio;
        this.compressionTime = compressionTime;
    }

    public void printResults() {
        System.out.println("压缩算法：" + algorithm);
        System.out.println("压缩后大小：" + compressedData.length + " 字节");
        System.out.println("压缩比：" + String.format("%.2f", compressionRatio * 100) + "%");
        System.out.println("压缩时间：" + compressionTime + " ms");
        System.out.println("压缩效率：" + (compressionRatio < 0.6 ? "高" :
                          compressionRatio < 0.8 ? "中" : "低"));
    }

    // Getters
    public double getCompressionRatio() { return compressionRatio; }
    public long getCompressionTime() { return compressionTime; }
    public String getAlgorithm() { return algorithm; }
}

// 智能压缩策略选择器
class CompressionStrategySelector {
    public static CompressionStrategy selectBestStrategy(String data, boolean prioritizeSpeed) {
        if (prioritizeSpeed) {
            // 优先考虑速度，选择LZ4
            return new Lz4CompressionStrategy();
        } else if (data.length() > 10000) {
            // 大文件优先考虑压缩比，选择GZIP
            return new GzipCompressionStrategy();
        } else {
            // 中等大小文件，平衡压缩比和速度，选择ZIP
            return new ZipCompressionStrategy();
        }
    }
}

// 使用示例
public class CompressionExample {
    public static void main(String[] args) {
        CompressionContext context = new CompressionContext();
        String testData = "这是一段测试数据，用于演示不同的压缩策略。".repeat(100);

        System.out.println("=== 压缩策略比较 ===");

        // 测试ZIP压缩
        System.out.println("\n--- ZIP压缩 ---");
        context.setCompressionStrategy(new ZipCompressionStrategy());
        CompressionResult zipResult = context.compressData(testData);
        zipResult.printResults();

        // 测试GZIP压缩
        System.out.println("\n--- GZIP压缩 ---");
        context.setCompressionStrategy(new GzipCompressionStrategy());
        CompressionResult gzipResult = context.compressData(testData);
        gzipResult.printResults();

        // 测试LZ4压缩
        System.out.println("\n--- LZ4压缩 ---");
        context.setCompressionStrategy(new Lz4CompressionStrategy());
        CompressionResult lz4Result = context.compressData(testData);
        lz4Result.printResults();

        // 智能选择策略
        System.out.println("\n=== 智能策略选择 ===");
        System.out.println("优先速度：");
        CompressionStrategy speedStrategy = CompressionStrategySelector.selectBestStrategy(testData, true);
        context.setCompressionStrategy(speedStrategy);
        context.compressData(testData).printResults();

        System.out.println("\n优先压缩比：");
        CompressionStrategy ratioStrategy = CompressionStrategySelector.selectBestStrategy(testData, false);
        context.setCompressionStrategy(ratioStrategy);
        context.compressData(testData).printResults();
    }
}
```

### 示例3：游戏角色行为策略
```java
// 攻击策略接口
interface AttackStrategy {
    void attack(String target);
    int getDamage();
    String getAttackType();
}

// 近战攻击策略
class MeleeAttackStrategy implements AttackStrategy {
    @Override
    public void attack(String target) {
        System.out.println("使用剑砍向 " + target + "！");
        System.out.println("造成 " + getDamage() + " 点物理伤害");
    }

    @Override
    public int getDamage() {
        return 100;
    }

    @Override
    public String getAttackType() {
        return "近战攻击";
    }
}

// 远程攻击策略
class RangedAttackStrategy implements AttackStrategy {
    @Override
    public void attack(String target) {
        System.out.println("向 " + target + " 射出一箭！");
        System.out.println("造成 " + getDamage() + " 点物理伤害");
    }

    @Override
    public int getDamage() {
        return 80;
    }

    @Override
    public String getAttackType() {
        return "远程攻击";
    }
}

// 魔法攻击策略
class MagicAttackStrategy implements AttackStrategy {
    @Override
    public void attack(String target) {
        System.out.println("对 " + target + " 释放火球术！");
        System.out.println("造成 " + getDamage() + " 点魔法伤害");
    }

    @Override
    public int getDamage() {
        return 120;
    }

    @Override
    public String getAttackType() {
        return "魔法攻击";
    }
}

// 防御策略接口
interface DefenseStrategy {
    int defendAgainst(int incomingDamage, String attackType);
    String getDefenseType();
}

// 盾牌防御策略
class ShieldDefenseStrategy implements DefenseStrategy {
    @Override
    public int defendAgainst(int incomingDamage, String attackType) {
        int reducedDamage = (int)(incomingDamage * 0.5); // 减少50%伤害
        System.out.println("举起盾牌防御！减少伤害：" + (incomingDamage - reducedDamage));
        return reducedDamage;
    }

    @Override
    public String getDefenseType() {
        return "盾牌防御";
    }
}

// 闪避策略
class DodgeStrategy implements DefenseStrategy {
    @Override
    public int defendAgainst(int incomingDamage, String attackType) {
        // 30%概率完全闪避
        if (Math.random() < 0.3) {
            System.out.println("敏捷闪避！完全避开攻击");
            return 0;
        } else {
            System.out.println("闪避失败，承受全部伤害");
            return incomingDamage;
        }
    }

    @Override
    public String getDefenseType() {
        return "敏捷闪避";
    }
}

// 魔法护盾策略
class MagicShieldStrategy implements DefenseStrategy {
    @Override
    public int defendAgainst(int incomingDamage, String attackType) {
        if ("魔法攻击".equals(attackType)) {
            int reducedDamage = (int)(incomingDamage * 0.2); // 对魔法攻击减少80%伤害
            System.out.println("魔法护盾激活！大幅减少魔法伤害：" + (incomingDamage - reducedDamage));
            return reducedDamage;
        } else {
            int reducedDamage = (int)(incomingDamage * 0.8); // 对物理攻击只减少20%伤害
            System.out.println("魔法护盾对物理攻击效果有限：" + (incomingDamage - reducedDamage));
            return reducedDamage;
        }
    }

    @Override
    public String getDefenseType() {
        return "魔法护盾";
    }
}

// 游戏角色类
class GameCharacter {
    private String name;
    private int health;
    private int maxHealth;
    private AttackStrategy attackStrategy;
    private DefenseStrategy defenseStrategy;

    public GameCharacter(String name, int health) {
        this.name = name;
        this.health = health;
        this.maxHealth = health;
    }

    public void setAttackStrategy(AttackStrategy attackStrategy) {
        this.attackStrategy = attackStrategy;
        System.out.println(name + " 切换到：" + attackStrategy.getAttackType());
    }

    public void setDefenseStrategy(DefenseStrategy defenseStrategy) {
        this.defenseStrategy = defenseStrategy;
        System.out.println(name + " 切换到：" + defenseStrategy.getDefenseType());
    }

    public void attackTarget(GameCharacter target) {
        if (attackStrategy == null) {
            System.out.println(name + " 没有设置攻击策略！");
            return;
        }

        System.out.println(name + " 攻击 " + target.getName() + "：");
        attackStrategy.attack(target.getName());
        target.takeDamage(attackStrategy.getDamage(), attackStrategy.getAttackType());
    }

    public void takeDamage(int damage, String attackType) {
        int actualDamage = damage;

        if (defenseStrategy != null) {
            actualDamage = defenseStrategy.defendAgainst(damage, attackType);
        }

        health -= actualDamage;
        if (health < 0) health = 0;

        System.out.println(name + " 受到 " + actualDamage + " 点伤害，剩余生命值：" + health);

        if (health <= 0) {
            System.out.println(name + " 被击败了！");
        }
    }

    // Getters
    public String getName() { return name; }
    public int getHealth() { return health; }
    public boolean isAlive() { return health > 0; }
}

// 游戏战斗示例
public class GameBattleExample {
    public static void main(String[] args) {
        // 创建角色
        GameCharacter warrior = new GameCharacter("战士", 300);
        GameCharacter archer = new GameCharacter("弓箭手", 200);
        GameCharacter mage = new GameCharacter("法师", 150);

        System.out.println("=== 角色初始化 ===");

        // 设置战士策略
        warrior.setAttackStrategy(new MeleeAttackStrategy());
        warrior.setDefenseStrategy(new ShieldDefenseStrategy());

        // 设置弓箭手策略
        archer.setAttackStrategy(new RangedAttackStrategy());
        archer.setDefenseStrategy(new DodgeStrategy());

        // 设置法师策略
        mage.setAttackStrategy(new MagicAttackStrategy());
        mage.setDefenseStrategy(new MagicShieldStrategy());

        System.out.println("\n=== 战斗开始 ===");

        // 第一轮攻击
        System.out.println("\n--- 第一轮 ---");
        warrior.attackTarget(mage);
        System.out.println();
        mage.attackTarget(warrior);
        System.out.println();
        archer.attackTarget(mage);

        // 动态切换策略
        System.out.println("\n=== 策略切换 ===");
        System.out.println("法师发现对手有魔法抗性，切换为近战！");
        mage.setAttackStrategy(new MeleeAttackStrategy());

        System.out.println("战士面对法师，切换为魔法护盾！");
        warrior.setDefenseStrategy(new MagicShieldStrategy());

        // 第二轮攻击
        System.out.println("\n--- 第二轮 ---");
        mage.attackTarget(archer);
        System.out.println();
        warrior.attackTarget(archer);

        // 显示最终状态
        System.out.println("\n=== 战斗结果 ===");
        System.out.println(warrior.getName() + " 生命值：" + warrior.getHealth());
        System.out.println(archer.getName() + " 生命值：" + archer.getHealth());
        System.out.println(mage.getName() + " 生命值：" + mage.getHealth());
    }
}
```

## ⚡ 现代应用场景

### Lambda表达式和函数式编程
```java
// 使用函数式接口简化策略模式
@FunctionalInterface
interface DiscountStrategy {
    double calculateDiscount(double amount);
}

public class ModernStrategyExample {
    public static void main(String[] args) {
        double amount = 1000.0;

        // 使用Lambda表达式定义策略
        DiscountStrategy regularCustomer = amount -> amount * 0.05;
        DiscountStrategy vipCustomer = amount -> amount * 0.10;
        DiscountStrategy premiumCustomer = amount -> amount * 0.15;

        // 动态选择策略
        Map<String, DiscountStrategy> strategies = Map.of(
            "REGULAR", regularCustomer,
            "VIP", vipCustomer,
            "PREMIUM", premiumCustomer
        );

        String customerType = "VIP";
        DiscountStrategy strategy = strategies.get(customerType);
        double discount = strategy.calculateDiscount(amount);

        System.out.println("客户类型：" + customerType);
        System.out.println("原价：$" + amount);
        System.out.println("折扣：$" + discount);
        System.out.println("实付：$" + (amount - discount));
    }
}
```

### 工厂模式结合策略模式
```java
// 策略工厂
class StrategyFactory {
    private static final Map<String, Supplier<SortStrategy>> strategies = Map.of(
        "bubble", BubbleSortStrategy::new,
        "quick", QuickSortStrategy::new,
        "merge", MergeSortStrategy::new
    );

    public static SortStrategy createStrategy(String type) {
        Supplier<SortStrategy> supplier = strategies.get(type.toLowerCase());
        if (supplier == null) {
            throw new IllegalArgumentException("不支持的排序策略：" + type);
        }
        return supplier.get();
    }

    public static Set<String> getSupportedStrategies() {
        return strategies.keySet();
    }
}

// 智能策略选择
class SmartSortContext {
    public void smartSort(int[] array) {
        SortStrategy strategy;

        if (array.length < 10) {
            strategy = StrategyFactory.createStrategy("bubble");
        } else if (array.length < 1000) {
            strategy = StrategyFactory.createStrategy("quick");
        } else {
            strategy = StrategyFactory.createStrategy("merge");
        }

        SortContext context = new SortContext(strategy);
        context.performSort(array);
    }
}
```

## ✅ 优势分析

### 1. **算法族封装**
将相关的算法组织成一个家族，便于管理和扩展。

### 2. **运行时切换**
可以在运行时动态切换算法，提供更好的灵活性。

### 3. **消除条件语句**
避免大量的if-else或switch语句，使代码更清晰。

### 4. **开闭原则**
对扩展开放，对修改关闭，新增策略不影响现有代码。

## ⚠️ 注意事项

### 1. **策略数量控制**
```java
// 避免策略过多导致复杂性
// 错误示例：为每个细微差别创建策略
class TaxCalculator {
    // 不要为每个税率创建单独的策略
}

// 正确做法：参数化策略
class ParameterizedTaxStrategy implements TaxStrategy {
    private double taxRate;

    public ParameterizedTaxStrategy(double taxRate) {
        this.taxRate = taxRate;
    }

    @Override
    public double calculateTax(double amount) {
        return amount * taxRate;
    }
}
```

### 2. **客户端复杂性**
客户端需要了解不同策略的区别，可能增加使用复杂度。

### 3. **性能考虑**
频繁切换策略可能带来性能开销，需要权衡。

## 🆚 与其他模式对比

| 特性 | 策略模式 | 状态模式 | 命令模式 |
|------|----------|----------|----------|
| 目的 | 选择算法 | 管理状态 | 封装请求 |
| 切换方式 | 外部切换 | 内部切换 | 不切换 |
| 上下文感知 | 不感知 | 感知 | 不感知 |
| 适用场景 | 算法选择 | 状态转换 | 操作封装 |

## 🎯 实战建议

### 1. **何时使用策略模式**
- 有多种算法可以解决同一问题
- 需要在运行时选择算法
- 想避免复杂的条件语句
- 算法独立于使用它的客户端

### 2. **设计原则**
```java
// 好的策略设计
interface Strategy {
    Result execute(Context context);  // 清晰的接口
}

// 避免策略泄露实现细节
interface BadStrategy {
    void setInternalParam(String param);  // 不好的设计
    Result execute();
}
```

### 3. **与Spring框架结合**
```java
@Component
public class PaymentService {
    private final Map<String, PaymentStrategy> strategies;

    public PaymentService(List<PaymentStrategy> strategies) {
        this.strategies = strategies.stream()
            .collect(Collectors.toMap(
                PaymentStrategy::getPaymentMethod,
                Function.identity()
            ));
    }

    public boolean processPayment(String method, double amount) {
        PaymentStrategy strategy = strategies.get(method);
        if (strategy == null) {
            throw new UnsupportedOperationException("不支持的支付方式：" + method);
        }
        return strategy.pay(amount);
    }
}
```

## 🧠 记忆技巧

**口诀：策略算法可替换**
- **策**划多种解决方案
- **略**有不同各有长
- **算**法封装成家族
- **法**则统一接口齐
- **可**以动态来切换
- **替**代条件判断语句
- **换**得灵活好扩展

**形象比喻：**
策略模式就像**出行方式的选择**：
- 目标是一样的（到达目的地）
- 方式有多种（开车、地铁、步行）
- 可以根据情况选择（天气、时间、距离）
- 随时可以改变策略

## 🎉 总结

策略模式是一种强大的设计模式，它让我们能够优雅地处理算法的选择和切换。通过将算法封装成可互换的策略，我们获得了更好的灵活性和可扩展性。

**核心思想：** 🎯 让算法的选择变得灵活，让代码的扩展变得简单！

下一篇我们将学习**模板方法模式**，看看如何定义算法的骨架，让子类填充具体实现！ 🚀