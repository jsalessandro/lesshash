---
title: "设计模式详解：享元模式(Flyweight) - 高效共享相似对象"
date: 2025-09-19T02:00:00+08:00
draft: false
tags: ["设计模式", "享元模式", "Flyweight", "Java", "结构型模式"]
categories: ["设计模式"]
author: "lesshash"
description: "深入浅出讲解享元模式，从基础概念到高级实现，包含内部状态、外部状态、对象池等实战技巧，让你彻底掌握内存优化的终极方案"
---

## 🎯 什么是享元模式？

### 生活中的例子
想象一下一个**图书馆**的运营方式：图书馆里有很多相同的书（比如《Java编程思想》），但不会为每个读者都准备一本。相反，图书馆只保存一本书，当有读者要借阅时，记录下"谁在什么时间借了这本书"这些信息。书本身的内容（内部状态）是共享的，而借阅信息（外部状态）是独立的。这样大大节省了空间和成本。这就是享元模式的核心思想：**通过共享相同的对象来减少内存使用，将对象的状态分为内部状态（可共享）和外部状态（不可共享）**。

### 问题背景
在软件开发中，经常遇到需要大量相似对象的场景：
- 🎮 **游戏开发** - 大量相同类型的子弹、粒子、NPC
- 📝 **文本编辑器** - 大量相同字体、颜色的字符
- 🌳 **图形渲染** - 大量相同纹理的树木、建筑
- 📊 **数据可视化** - 大量相同样式的图表元素
- 🎨 **UI组件** - 大量相同样式的按钮、图标

如果为每个使用场景都创建独立对象，会导致：
- 内存消耗巨大
- 对象创建开销大
- 垃圾回收压力大
- 系统性能下降

## 🧠 设计思想

### 核心角色
1. **Flyweight（享元接口）** - 定义享元对象的接口
2. **ConcreteFlyweight（具体享元）** - 实现享元接口的具体类
3. **FlyweightFactory（享元工厂）** - 管理和创建享元对象
4. **Context（环境类）** - 包含外部状态，使用享元对象

### 核心概念
- **内部状态（Intrinsic State）**：可以共享的状态，存储在享元对象内部
- **外部状态（Extrinsic State）**：不可共享的状态，由客户端管理
- **享元池**：存储享元对象的集合，避免重复创建

### 记忆口诀
> **"内部共享，外部独立，池化管理，节约内存"**

## 💻 代码实现

### 1. 基础享元模式 - 文本编辑器

```java
/**
 * 享元接口 - 字符
 */
public interface Character {
    void display(int x, int y, int size, String color);
}

/**
 * 具体享元 - 具体字符
 * 内部状态：字符内容（可共享）
 * 外部状态：位置、大小、颜色（不可共享，由外部传入）
 */
public class ConcreteCharacter implements Character {
    private final char character; // 内部状态 - 字符内容

    public ConcreteCharacter(char character) {
        this.character = character;
    }

    @Override
    public void display(int x, int y, int size, String color) {
        // 使用内部状态和外部状态进行显示
        System.out.println("显示字符 '" + character + "' 在位置(" + x + "," + y +
                          ") 大小:" + size + " 颜色:" + color);
    }

    public char getCharacter() {
        return character;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ConcreteCharacter that = (ConcreteCharacter) obj;
        return character == that.character;
    }

    @Override
    public int hashCode() {
        return Objects.hash(character);
    }

    @Override
    public String toString() {
        return "ConcreteCharacter{'" + character + "'}";
    }
}

/**
 * 享元工厂 - 管理字符享元对象
 */
public class CharacterFactory {
    private static final Map<java.lang.Character, Character> flyweights = new HashMap<>();
    private static int createdCount = 0;

    public static Character getCharacter(char c) {
        Character character = flyweights.get(c);

        if (character == null) {
            character = new ConcreteCharacter(c);
            flyweights.put(c, character);
            createdCount++;
            System.out.println("创建新的享元字符: '" + c + "' (总数: " + createdCount + ")");
        } else {
            System.out.println("复用享元字符: '" + c + "'");
        }

        return character;
    }

    public static int getCreatedCount() {
        return createdCount;
    }

    public static int getPoolSize() {
        return flyweights.size();
    }

    public static void printPool() {
        System.out.println("=== 享元池状态 ===");
        System.out.println("池大小: " + flyweights.size());
        System.out.println("创建总数: " + createdCount);
        System.out.println("池中字符: " + flyweights.keySet());
    }

    public static void clearPool() {
        flyweights.clear();
        createdCount = 0;
        System.out.println("享元池已清空");
    }
}

/**
 * 环境类 - 文档中的字符实例
 * 包含外部状态：位置、大小、颜色
 */
public class CharacterContext {
    private Character character; // 享元对象
    private int x, y;           // 外部状态 - 位置
    private int size;           // 外部状态 - 大小
    private String color;       // 外部状态 - 颜色

    public CharacterContext(char c, int x, int y, int size, String color) {
        this.character = CharacterFactory.getCharacter(c); // 获取享元
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
    }

    public void display() {
        character.display(x, y, size, color);
    }

    // 外部状态的修改方法
    public void moveTo(int newX, int newY) {
        this.x = newX;
        this.y = newY;
    }

    public void resize(int newSize) {
        this.size = newSize;
    }

    public void changeColor(String newColor) {
        this.color = newColor;
    }

    @Override
    public String toString() {
        return "CharacterContext{x=" + x + ", y=" + y + ", size=" + size + ", color='" + color + "'}";
    }
}

/**
 * 文档类 - 使用享元的客户端
 */
public class Document {
    private List<CharacterContext> characters = new ArrayList<>();
    private String title;

    public Document(String title) {
        this.title = title;
    }

    public void addCharacter(char c, int x, int y, int size, String color) {
        CharacterContext context = new CharacterContext(c, x, y, size, color);
        characters.add(context);
    }

    public void addText(String text, int startX, int startY, int size, String color) {
        int x = startX;
        for (char c : text.toCharArray()) {
            if (c == ' ') {
                x += size / 2; // 空格占位
            } else {
                addCharacter(c, x, startY, size, color);
                x += size; // 字符间距
            }
        }
    }

    public void display() {
        System.out.println("=== 文档: " + title + " ===");
        for (CharacterContext context : characters) {
            context.display();
        }
    }

    public void displaySummary() {
        System.out.println("文档 '" + title + "' 包含 " + characters.size() + " 个字符");
        CharacterFactory.printPool();
    }

    public void updateCharacterAt(int index, int newX, int newY, String newColor) {
        if (index >= 0 && index < characters.size()) {
            CharacterContext context = characters.get(index);
            context.moveTo(newX, newY);
            context.changeColor(newColor);
            System.out.println("更新第 " + index + " 个字符的外部状态");
        }
    }
}

// 文本编辑器享元模式演示
public class TextEditorFlyweightDemo {
    public static void main(String[] args) {
        System.out.println("=== 文本编辑器享元模式演示 ===");

        Document doc = new Document("Java设计模式教程");

        System.out.println("\n=== 添加文本内容 ===");
        doc.addText("Hello", 10, 10, 12, "black");
        doc.addText("World", 10, 30, 14, "red");
        doc.addText("Hello", 10, 50, 16, "blue"); // 重复使用 H,e,l,l,o

        System.out.println("\n=== 显示文档内容 ===");
        doc.display();

        System.out.println("\n=== 文档统计信息 ===");
        doc.displaySummary();

        System.out.println("\n=== 内存使用对比分析 ===");
        System.out.println("字符总数: 10 个");
        System.out.println("享元对象数: " + CharacterFactory.getPoolSize() + " 个");
        System.out.println("内存节约率: " +
            String.format("%.1f", (1.0 - (double)CharacterFactory.getPoolSize() / 10) * 100) + "%");

        System.out.println("\n=== 动态修改外部状态 ===");
        doc.updateCharacterAt(0, 100, 100, "green");
        System.out.println("修改后第一个字符的显示:");
        // 注意：享元对象本身没有改变，只是外部状态改变了

        System.out.println("\n=== 大量文本测试 ===");
        Document largDoc = new Document("大文档测试");
        String longText = "The quick brown fox jumps over the lazy dog. ";

        // 添加重复文本
        for (int i = 0; i < 5; i++) {
            largDoc.addText(longText, 10, 70 + i * 20, 10, "black");
        }

        largDoc.displaySummary();

        System.out.println("\n=== 享元模式效果 ===");
        int totalChars = longText.length() * 5;
        System.out.println("总字符数: " + totalChars);
        System.out.println("享元对象数: " + CharacterFactory.getPoolSize());
        System.out.println("复用率: " +
            String.format("%.1f", ((double)(totalChars - CharacterFactory.getPoolSize()) / totalChars) * 100) + "%");

        // 清理
        CharacterFactory.clearPool();
    }
}
```

### 2. 游戏粒子系统享元模式

```java
/**
 * 享元接口 - 粒子类型
 */
public interface ParticleType {
    void render(int x, int y, double velocity, String color, int size);
    String getTypeName();
}

/**
 * 具体享元 - 火花粒子
 */
public class SparkParticle implements ParticleType {
    private final String texture; // 内部状态 - 纹理
    private final String shape;   // 内部状态 - 形状

    public SparkParticle() {
        this.texture = "spark_texture.png";
        this.shape = "star";
        System.out.println("创建火花粒子享元对象");
    }

    @Override
    public void render(int x, int y, double velocity, String color, int size) {
        System.out.println("渲染火花粒子: 位置(" + x + "," + y + ") " +
                          "速度:" + velocity + " 颜色:" + color + " 大小:" + size +
                          " 纹理:" + texture + " 形状:" + shape);
    }

    @Override
    public String getTypeName() {
        return "Spark";
    }
}

/**
 * 具体享元 - 烟雾粒子
 */
public class SmokeParticle implements ParticleType {
    private final String texture; // 内部状态
    private final String shape;   // 内部状态

    public SmokeParticle() {
        this.texture = "smoke_texture.png";
        this.shape = "cloud";
        System.out.println("创建烟雾粒子享元对象");
    }

    @Override
    public void render(int x, int y, double velocity, String color, int size) {
        System.out.println("渲染烟雾粒子: 位置(" + x + "," + y + ") " +
                          "速度:" + velocity + " 颜色:" + color + " 大小:" + size +
                          " 纹理:" + texture + " 形状:" + shape);
    }

    @Override
    public String getTypeName() {
        return "Smoke";
    }
}

/**
 * 具体享元 - 爆炸粒子
 */
public class ExplosionParticle implements ParticleType {
    private final String texture; // 内部状态
    private final String shape;   // 内部状态
    private final String[] frames; // 内部状态 - 动画帧

    public ExplosionParticle() {
        this.texture = "explosion_texture.png";
        this.shape = "burst";
        this.frames = new String[]{"frame1", "frame2", "frame3", "frame4"};
        System.out.println("创建爆炸粒子享元对象");
    }

    @Override
    public void render(int x, int y, double velocity, String color, int size) {
        // 模拟动画帧选择
        String currentFrame = frames[(int)(Math.random() * frames.length)];
        System.out.println("渲染爆炸粒子: 位置(" + x + "," + y + ") " +
                          "速度:" + velocity + " 颜色:" + color + " 大小:" + size +
                          " 纹理:" + texture + " 形状:" + shape + " 帧:" + currentFrame);
    }

    @Override
    public String getTypeName() {
        return "Explosion";
    }
}

/**
 * 粒子类型枚举
 */
public enum ParticleTypeEnum {
    SPARK, SMOKE, EXPLOSION
}

/**
 * 粒子享元工厂
 */
public class ParticleTypeFactory {
    private static final Map<ParticleTypeEnum, ParticleType> particleTypes = new HashMap<>();
    private static int totalCreated = 0;

    public static ParticleType getParticleType(ParticleTypeEnum type) {
        ParticleType particleType = particleTypes.get(type);

        if (particleType == null) {
            switch (type) {
                case SPARK:
                    particleType = new SparkParticle();
                    break;
                case SMOKE:
                    particleType = new SmokeParticle();
                    break;
                case EXPLOSION:
                    particleType = new ExplosionParticle();
                    break;
                default:
                    throw new IllegalArgumentException("未知的粒子类型: " + type);
            }
            particleTypes.put(type, particleType);
            totalCreated++;
        }

        return particleType;
    }

    public static void printStatistics() {
        System.out.println("=== 粒子工厂统计 ===");
        System.out.println("享元对象总数: " + totalCreated);
        System.out.println("当前池大小: " + particleTypes.size());
        for (Map.Entry<ParticleTypeEnum, ParticleType> entry : particleTypes.entrySet()) {
            System.out.println("- " + entry.getKey() + ": " + entry.getValue().getTypeName());
        }
    }

    public static void clear() {
        particleTypes.clear();
        totalCreated = 0;
    }
}

/**
 * 粒子实例 - 环境类
 * 包含外部状态：位置、速度、颜色、大小、生命周期等
 */
public class Particle {
    private ParticleType type;    // 享元对象
    private int x, y;            // 外部状态 - 位置
    private double velocityX, velocityY; // 外部状态 - 速度
    private String color;        // 外部状态 - 颜色
    private int size;           // 外部状态 - 大小
    private long creationTime;  // 外部状态 - 创建时间
    private int lifespan;       // 外部状态 - 生命周期(毫秒)

    public Particle(ParticleTypeEnum typeEnum, int x, int y,
                   double velocityX, double velocityY, String color, int size, int lifespan) {
        this.type = ParticleTypeFactory.getParticleType(typeEnum);
        this.x = x;
        this.y = y;
        this.velocityX = velocityX;
        this.velocityY = velocityY;
        this.color = color;
        this.size = size;
        this.lifespan = lifespan;
        this.creationTime = System.currentTimeMillis();
    }

    public void update(int deltaTime) {
        // 更新位置
        x += velocityX * deltaTime / 1000.0;
        y += velocityY * deltaTime / 1000.0;

        // 重力效果
        velocityY += 9.8 * deltaTime / 1000.0;
    }

    public void render() {
        type.render(x, y, Math.sqrt(velocityX * velocityX + velocityY * velocityY), color, size);
    }

    public boolean isAlive() {
        return (System.currentTimeMillis() - creationTime) < lifespan;
    }

    public String getTypeName() {
        return type.getTypeName();
    }

    @Override
    public String toString() {
        return "Particle{" +
               "type=" + type.getTypeName() +
               ", x=" + x + ", y=" + y +
               ", velocity=(" + String.format("%.1f", velocityX) + "," + String.format("%.1f", velocityY) + ")" +
               ", color='" + color + "'" +
               ", size=" + size +
               '}';
    }
}

/**
 * 粒子系统 - 管理大量粒子
 */
public class ParticleSystem {
    private List<Particle> particles;
    private String systemName;

    public ParticleSystem(String systemName) {
        this.systemName = systemName;
        this.particles = new ArrayList<>();
    }

    public void addParticle(ParticleTypeEnum type, int x, int y,
                           double velocityX, double velocityY, String color, int size, int lifespan) {
        Particle particle = new Particle(type, x, y, velocityX, velocityY, color, size, lifespan);
        particles.add(particle);
    }

    public void createExplosion(int centerX, int centerY) {
        System.out.println("🔥 在位置(" + centerX + "," + centerY + ")创建爆炸效果");

        // 创建爆炸粒子
        for (int i = 0; i < 5; i++) {
            double angle = Math.random() * 2 * Math.PI;
            double speed = 50 + Math.random() * 100;
            addParticle(ParticleTypeEnum.EXPLOSION,
                       centerX, centerY,
                       Math.cos(angle) * speed, Math.sin(angle) * speed,
                       "orange", 8 + (int)(Math.random() * 5), 2000);
        }

        // 创建火花粒子
        for (int i = 0; i < 10; i++) {
            double angle = Math.random() * 2 * Math.PI;
            double speed = 80 + Math.random() * 120;
            addParticle(ParticleTypeEnum.SPARK,
                       centerX, centerY,
                       Math.cos(angle) * speed, Math.sin(angle) * speed,
                       "yellow", 3 + (int)(Math.random() * 3), 1500);
        }

        // 创建烟雾粒子
        for (int i = 0; i < 3; i++) {
            double angle = Math.random() * 2 * Math.PI;
            double speed = 20 + Math.random() * 40;
            addParticle(ParticleTypeEnum.SMOKE,
                       centerX, centerY,
                       Math.cos(angle) * speed, Math.sin(angle) * speed,
                       "gray", 12 + (int)(Math.random() * 8), 3000);
        }
    }

    public void update(int deltaTime) {
        // 更新所有粒子
        Iterator<Particle> iterator = particles.iterator();
        while (iterator.hasNext()) {
            Particle particle = iterator.next();
            particle.update(deltaTime);

            // 移除死亡的粒子
            if (!particle.isAlive()) {
                iterator.remove();
            }
        }
    }

    public void render() {
        System.out.println("=== 渲染粒子系统: " + systemName + " ===");
        for (Particle particle : particles) {
            particle.render();
        }
    }

    public void printStatistics() {
        Map<String, Integer> typeCounts = new HashMap<>();
        for (Particle particle : particles) {
            String typeName = particle.getTypeName();
            typeCounts.put(typeName, typeCounts.getOrDefault(typeName, 0) + 1);
        }

        System.out.println("=== 粒子系统统计: " + systemName + " ===");
        System.out.println("活跃粒子总数: " + particles.size());
        for (Map.Entry<String, Integer> entry : typeCounts.entrySet()) {
            System.out.println("- " + entry.getKey() + ": " + entry.getValue() + " 个");
        }
    }

    public int getParticleCount() {
        return particles.size();
    }
}

// 游戏粒子系统演示
public class ParticleSystemFlyweightDemo {
    public static void main(String[] args) {
        System.out.println("=== 游戏粒子系统享元模式演示 ===");

        ParticleSystem gameParticleSystem = new ParticleSystem("游戏主场景");

        System.out.println("\n=== 创建第一次爆炸 ===");
        gameParticleSystem.createExplosion(100, 100);

        System.out.println("\n=== 创建第二次爆炸 ===");
        gameParticleSystem.createExplosion(200, 150);

        System.out.println("\n=== 粒子工厂统计 ===");
        ParticleTypeFactory.printStatistics();

        System.out.println("\n=== 粒子系统统计 ===");
        gameParticleSystem.printStatistics();

        System.out.println("\n=== 渲染当前帧 ===");
        gameParticleSystem.render();

        System.out.println("\n=== 模拟时间流逝 ===");
        for (int frame = 1; frame <= 3; frame++) {
            System.out.println("\n--- 第 " + frame + " 帧更新 ---");
            gameParticleSystem.update(500); // 每帧500ms

            System.out.println("更新后粒子数量: " + gameParticleSystem.getParticleCount());

            if (frame == 2) {
                System.out.println("第2帧渲染部分粒子:");
                gameParticleSystem.render();
            }
        }

        System.out.println("\n=== 大规模粒子测试 ===");
        ParticleSystem massiveSystem = new ParticleSystem("大规模测试");

        // 创建10次爆炸
        for (int i = 0; i < 10; i++) {
            massiveSystem.createExplosion(i * 50, i * 50);
        }

        massiveSystem.printStatistics();
        ParticleTypeFactory.printStatistics();

        System.out.println("\n=== 享元模式效果分析 ===");
        int totalParticles = massiveSystem.getParticleCount();
        int flyweightCount = 3; // SPARK, SMOKE, EXPLOSION

        System.out.println("粒子实例总数: " + totalParticles);
        System.out.println("享元对象数量: " + flyweightCount);
        System.out.println("内存节约: " + (totalParticles - flyweightCount) + " 个对象");
        System.out.println("节约率: " + String.format("%.1f",
            ((double)(totalParticles - flyweightCount) / totalParticles) * 100) + "%");

        System.out.println("\n=== 内存使用对比 ===");
        System.out.println("不使用享元模式: 每个粒子都是独立对象");
        System.out.println("- 内存占用: " + totalParticles + " × 完整对象大小");
        System.out.println("使用享元模式: 共享类型定义，独立外部状态");
        System.out.println("- 内存占用: " + flyweightCount + " × 享元对象 + " +
                          totalParticles + " × 外部状态");

        System.out.println("\n=== 运行时添加新粒子类型 ===");
        // 注意：这里我们复用现有的享元对象
        massiveSystem.addParticle(ParticleTypeEnum.SPARK, 300, 300, 0, -50, "blue", 5, 1000);
        System.out.println("添加了一个蓝色火花粒子（复用SPARK享元）");

        // 清理
        ParticleTypeFactory.clear();
    }
}
```

### 3. 网页图标缓存享元模式

```java
/**
 * 享元接口 - 图标
 */
public interface Icon {
    void display(int x, int y, int size);
    String getIconName();
    byte[] getIconData(); // 模拟图标数据
}

/**
 * 具体享元 - 具体图标
 */
public class ConcreteIcon implements Icon {
    private final String iconName;  // 内部状态 - 图标名称
    private final String iconPath;  // 内部状态 - 图标路径
    private final byte[] iconData;  // 内部状态 - 图标数据

    public ConcreteIcon(String iconName, String iconPath) {
        this.iconName = iconName;
        this.iconPath = iconPath;
        this.iconData = loadIconData(iconPath); // 模拟加载图标数据
        System.out.println("🎨 加载图标: " + iconName + " 从 " + iconPath);
    }

    private byte[] loadIconData(String path) {
        // 模拟从文件系统或网络加载图标数据
        try {
            Thread.sleep(10); // 模拟IO延迟
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 生成模拟的图标数据
        return new byte[1024]; // 假设每个图标1KB
    }

    @Override
    public void display(int x, int y, int size) {
        System.out.println("显示图标 '" + iconName + "' 在位置(" + x + "," + y + ") 大小:" + size + "px");
    }

    @Override
    public String getIconName() {
        return iconName;
    }

    @Override
    public byte[] getIconData() {
        return iconData.clone(); // 返回副本，保护内部数据
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ConcreteIcon that = (ConcreteIcon) obj;
        return Objects.equals(iconName, that.iconName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(iconName);
    }
}

/**
 * 图标享元工厂
 */
public class IconFactory {
    private static final Map<String, Icon> iconCache = new ConcurrentHashMap<>();
    private static final AtomicInteger loadCount = new AtomicInteger(0);
    private static final AtomicInteger hitCount = new AtomicInteger(0);

    // 预定义的图标路径
    private static final Map<String, String> iconPaths = new HashMap<>();

    static {
        iconPaths.put("home", "/icons/home.png");
        iconPaths.put("user", "/icons/user.png");
        iconPaths.put("settings", "/icons/settings.png");
        iconPaths.put("search", "/icons/search.png");
        iconPaths.put("logout", "/icons/logout.png");
        iconPaths.put("menu", "/icons/menu.png");
        iconPaths.put("notification", "/icons/notification.png");
        iconPaths.put("download", "/icons/download.png");
        iconPaths.put("upload", "/icons/upload.png");
        iconPaths.put("delete", "/icons/delete.png");
        iconPaths.put("edit", "/icons/edit.png");
        iconPaths.put("save", "/icons/save.png");
    }

    public static Icon getIcon(String iconName) {
        Icon icon = iconCache.get(iconName);

        if (icon == null) {
            String iconPath = iconPaths.get(iconName);
            if (iconPath == null) {
                throw new IllegalArgumentException("未知的图标: " + iconName);
            }

            icon = new ConcreteIcon(iconName, iconPath);
            iconCache.put(iconName, icon);
            loadCount.incrementAndGet();
        } else {
            hitCount.incrementAndGet();
            System.out.println("📋 从缓存获取图标: " + iconName);
        }

        return icon;
    }

    public static void printStatistics() {
        System.out.println("=== 图标工厂统计 ===");
        System.out.println("缓存大小: " + iconCache.size());
        System.out.println("加载次数: " + loadCount.get());
        System.out.println("缓存命中: " + hitCount.get());
        if (loadCount.get() + hitCount.get() > 0) {
            double hitRate = (double) hitCount.get() / (loadCount.get() + hitCount.get()) * 100;
            System.out.println("命中率: " + String.format("%.1f", hitRate) + "%");
        }
        System.out.println("缓存图标: " + iconCache.keySet());
    }

    public static void clearCache() {
        iconCache.clear();
        loadCount.set(0);
        hitCount.set(0);
        System.out.println("图标缓存已清空");
    }

    public static int getCacheSize() {
        return iconCache.size();
    }

    public static long estimateMemoryUsage() {
        // 估算内存使用（每个图标约1KB + 对象开销）
        return iconCache.size() * 1100L; // 1KB数据 + 100字节对象开销
    }
}

/**
 * UI元素 - 包含外部状态
 */
public class UIElement {
    private Icon icon;      // 享元对象
    private int x, y;       // 外部状态 - 位置
    private int size;       // 外部状态 - 大小
    private String tooltip; // 外部状态 - 提示文本
    private boolean visible; // 外部状态 - 可见性
    private String elementId; // 外部状态 - 元素ID

    public UIElement(String iconName, int x, int y, int size, String tooltip, String elementId) {
        this.icon = IconFactory.getIcon(iconName);
        this.x = x;
        this.y = y;
        this.size = size;
        this.tooltip = tooltip;
        this.elementId = elementId;
        this.visible = true;
    }

    public void render() {
        if (visible) {
            icon.display(x, y, size);
            System.out.println("  ID: " + elementId + ", 提示: " + tooltip);
        }
    }

    public void moveTo(int newX, int newY) {
        this.x = newX;
        this.y = newY;
    }

    public void resize(int newSize) {
        this.size = newSize;
    }

    public void setVisible(boolean visible) {
        this.visible = visible;
    }

    public void setTooltip(String tooltip) {
        this.tooltip = tooltip;
    }

    public String getIconName() {
        return icon.getIconName();
    }

    @Override
    public String toString() {
        return "UIElement{" +
               "icon=" + icon.getIconName() +
               ", position=(" + x + "," + y + ")" +
               ", size=" + size +
               ", tooltip='" + tooltip + "'" +
               ", visible=" + visible +
               ", id='" + elementId + "'" +
               '}';
    }
}

/**
 * 网页 - 包含多个UI元素
 */
public class WebPage {
    private List<UIElement> elements;
    private String pageTitle;

    public WebPage(String pageTitle) {
        this.pageTitle = pageTitle;
        this.elements = new ArrayList<>();
    }

    public void addElement(String iconName, int x, int y, int size, String tooltip, String elementId) {
        UIElement element = new UIElement(iconName, x, y, size, tooltip, elementId);
        elements.add(element);
    }

    public void render() {
        System.out.println("=== 渲染页面: " + pageTitle + " ===");
        for (UIElement element : elements) {
            element.render();
        }
    }

    public void createNavigationBar() {
        System.out.println("🧭 创建导航栏");
        addElement("home", 10, 10, 24, "首页", "nav-home");
        addElement("user", 50, 10, 24, "用户中心", "nav-user");
        addElement("settings", 90, 10, 24, "设置", "nav-settings");
        addElement("search", 130, 10, 24, "搜索", "nav-search");
        addElement("logout", 170, 10, 24, "退出", "nav-logout");
    }

    public void createSidebar() {
        System.out.println("📋 创建侧边栏");
        addElement("menu", 10, 60, 20, "菜单", "sidebar-menu");
        addElement("notification", 10, 90, 20, "通知", "sidebar-notification");
        addElement("download", 10, 120, 20, "下载", "sidebar-download");
        addElement("upload", 10, 150, 20, "上传", "sidebar-upload");
    }

    public void createToolbar() {
        System.out.println("🔧 创建工具栏");
        addElement("save", 250, 60, 18, "保存", "toolbar-save");
        addElement("edit", 280, 60, 18, "编辑", "toolbar-edit");
        addElement("delete", 310, 60, 18, "删除", "toolbar-delete");
    }

    public void updateElement(String elementId, int newX, int newY) {
        for (UIElement element : elements) {
            if (element.toString().contains(elementId)) {
                element.moveTo(newX, newY);
                System.out.println("移动元素 " + elementId + " 到位置(" + newX + "," + newY + ")");
                break;
            }
        }
    }

    public void printStatistics() {
        Map<String, Integer> iconCounts = new HashMap<>();
        for (UIElement element : elements) {
            String iconName = element.getIconName();
            iconCounts.put(iconName, iconCounts.getOrDefault(iconName, 0) + 1);
        }

        System.out.println("=== 页面统计: " + pageTitle + " ===");
        System.out.println("UI元素总数: " + elements.size());
        System.out.println("图标使用统计:");
        for (Map.Entry<String, Integer> entry : iconCounts.entrySet()) {
            System.out.println("  " + entry.getKey() + ": " + entry.getValue() + " 次");
        }
    }

    public int getElementCount() {
        return elements.size();
    }
}

/**
 * 网站 - 管理多个页面
 */
public class Website {
    private List<WebPage> pages;
    private String siteName;

    public Website(String siteName) {
        this.siteName = siteName;
        this.pages = new ArrayList<>();
    }

    public WebPage createPage(String pageTitle) {
        WebPage page = new WebPage(pageTitle);
        pages.add(page);
        return page;
    }

    public void renderAllPages() {
        System.out.println("🌐 === 渲染整个网站: " + siteName + " ===");
        for (WebPage page : pages) {
            page.render();
            System.out.println();
        }
    }

    public void printOverallStatistics() {
        int totalElements = 0;
        for (WebPage page : pages) {
            totalElements += page.getElementCount();
        }

        System.out.println("=== 网站整体统计: " + siteName + " ===");
        System.out.println("页面总数: " + pages.size());
        System.out.println("UI元素总数: " + totalElements);
        System.out.println("估算内存使用: " + IconFactory.estimateMemoryUsage() + " 字节");

        if (totalElements > 0) {
            double memoryPerElement = (double) IconFactory.estimateMemoryUsage() / totalElements;
            System.out.println("平均每元素内存: " + String.format("%.1f", memoryPerElement) + " 字节");
        }
    }
}

// 网页图标缓存演示
public class WebPageIconFlyweightDemo {
    public static void main(String[] args) {
        System.out.println("=== 网页图标缓存享元模式演示 ===");

        Website corporateWebsite = new Website("企业官网");

        System.out.println("\n=== 创建首页 ===");
        WebPage homePage = corporateWebsite.createPage("首页");
        homePage.createNavigationBar();
        homePage.createSidebar();

        System.out.println("\n=== 创建用户页面 ===");
        WebPage userPage = corporateWebsite.createPage("用户中心");
        userPage.createNavigationBar(); // 复用导航栏图标
        userPage.createToolbar();

        System.out.println("\n=== 创建设置页面 ===");
        WebPage settingsPage = corporateWebsite.createPage("系统设置");
        settingsPage.createNavigationBar(); // 再次复用导航栏图标
        settingsPage.createSidebar(); // 复用侧边栏图标
        settingsPage.createToolbar(); // 复用工具栏图标

        System.out.println("\n=== 图标工厂统计 ===");
        IconFactory.printStatistics();

        System.out.println("\n=== 各页面统计 ===");
        homePage.printStatistics();
        userPage.printStatistics();
        settingsPage.printStatistics();

        System.out.println("\n=== 渲染所有页面 ===");
        corporateWebsite.renderAllPages();

        System.out.println("\n=== 网站整体统计 ===");
        corporateWebsite.printOverallStatistics();

        System.out.println("\n=== 享元模式效果分析 ===");
        int totalUIElements = homePage.getElementCount() + userPage.getElementCount() + settingsPage.getElementCount();
        int uniqueIcons = IconFactory.getCacheSize();

        System.out.println("UI元素总数: " + totalUIElements);
        System.out.println("唯一图标数: " + uniqueIcons);
        System.out.println("复用比例: " + String.format("%.1f",
            ((double)(totalUIElements - uniqueIcons) / totalUIElements) * 100) + "%");

        System.out.println("\n=== 内存节约分析 ===");
        long actualMemory = IconFactory.estimateMemoryUsage();
        long wouldBeMemory = totalUIElements * 1100L; // 如果每个元素都有独立图标
        long savedMemory = wouldBeMemory - actualMemory;

        System.out.println("实际内存使用: " + actualMemory + " 字节");
        System.out.println("不使用享元的内存: " + wouldBeMemory + " 字节");
        System.out.println("节约内存: " + savedMemory + " 字节");
        System.out.println("节约比例: " + String.format("%.1f",
            ((double)savedMemory / wouldBeMemory) * 100) + "%");

        System.out.println("\n=== 动态操作演示 ===");
        System.out.println("移动首页的搜索按钮:");
        homePage.updateElement("nav-search", 200, 10);

        System.out.println("\n添加更多相同类型的元素:");
        // 在设置页面添加更多使用现有图标的元素
        settingsPage.addElement("save", 50, 200, 16, "保存配置", "config-save");
        settingsPage.addElement("user", 80, 200, 16, "用户管理", "user-mgmt");

        System.out.println("\n更新后的图标工厂统计:");
        IconFactory.printStatistics();

        // 清理
        IconFactory.clearCache();
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **大幅减少内存使用**
   - 通过共享相同对象避免重复创建
   - 特别适合大量相似对象的场景

2. **提高系统性能**
   - 减少对象创建的时间开销
   - 降低垃圾回收的压力

3. **集中管理相似对象**
   - 享元工厂统一管理对象创建
   - 便于监控和优化

4. **透明性**
   - 客户端使用享元对象与普通对象无差异
   - 不影响现有代码结构

### ❌ 缺点

1. **增加系统复杂性**
   - 需要区分内部状态和外部状态
   - 代码设计更复杂

2. **运行时间可能增加**
   - 需要计算外部状态
   - 查找享元对象的开销

3. **状态管理复杂**
   - 外部状态必须由客户端管理
   - 容易造成状态混乱

## 🎯 使用场景总结

### 适合使用享元模式的场景：
- 🎮 **游戏开发** - 大量相同类型的粒子、子弹、NPC
- 📝 **文本编辑器** - 大量字符对象的渲染
- 🌐 **Web应用** - 大量相同图标、按钮的缓存
- 🎨 **图形渲染** - 大量相同纹理、材质的对象
- 📊 **数据可视化** - 大量相同样式的图表元素

### 不适合使用享元模式的场景：
- 对象数量不多的情况
- 对象的内部状态变化频繁
- 外部状态过于复杂
- 对象创建成本本身就很低

## 🧠 记忆技巧

### 形象比喻
> **享元模式就像是 "图书馆"**：
> - 书籍内容是内部状态（可共享）
> - 借阅信息是外部状态（不可共享）
> - 图书馆管理书籍（享元工厂）
> - 读者带着借阅卡使用书籍（客户端管理外部状态）

### 设计要点
> **"内部共享，外部独立，工厂管理，减少浪费"**

### 状态分离原则
- **内部状态**：不随环境变化的固有属性
- **外部状态**：随环境变化的可变属性

## 🔧 最佳实践

### 1. 线程安全的享元工厂

```java
/**
 * 线程安全的享元工厂
 */
public class ThreadSafeFlyweightFactory {
    private final ConcurrentHashMap<String, Flyweight> flyweights = new ConcurrentHashMap<>();
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    public Flyweight getFlyweight(String key) {
        // 读锁：允许并发读取
        lock.readLock().lock();
        try {
            Flyweight flyweight = flyweights.get(key);
            if (flyweight != null) {
                return flyweight;
            }
        } finally {
            lock.readLock().unlock();
        }

        // 写锁：独占创建
        lock.writeLock().lock();
        try {
            // 双重检查
            Flyweight flyweight = flyweights.get(key);
            if (flyweight == null) {
                flyweight = createFlyweight(key);
                flyweights.put(key, flyweight);
            }
            return flyweight;
        } finally {
            lock.writeLock().unlock();
        }
    }

    private Flyweight createFlyweight(String key) {
        // 创建享元对象的具体逻辑
        return new ConcreteFlyweight(key);
    }
}
```

### 2. 享元对象池管理

```java
/**
 * 带有LRU淘汰策略的享元池
 */
public class LRUFlyweightFactory<K, V extends Flyweight> {
    private final LinkedHashMap<K, V> cache;
    private final int maxSize;

    public LRUFlyweightFactory(int maxSize) {
        this.maxSize = maxSize;
        this.cache = new LinkedHashMap<K, V>(16, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > LRUFlyweightFactory.this.maxSize;
            }
        };
    }

    public synchronized V getFlyweight(K key, Function<K, V> factory) {
        V flyweight = cache.get(key);
        if (flyweight == null) {
            flyweight = factory.apply(key);
            cache.put(key, flyweight);
        }
        return flyweight;
    }
}
```

### 3. 享元模式与建造者模式结合

```java
/**
 * 享元建造者
 */
public class FlyweightBuilder {
    private Map<String, Object> intrinsicState = new HashMap<>();

    public FlyweightBuilder setTexture(String texture) {
        intrinsicState.put("texture", texture);
        return this;
    }

    public FlyweightBuilder setShape(String shape) {
        intrinsicState.put("shape", shape);
        return this;
    }

    public Flyweight build() {
        String key = generateKey(intrinsicState);
        return FlyweightFactory.getFlyweight(key, intrinsicState);
    }

    private String generateKey(Map<String, Object> state) {
        return state.toString();
    }
}
```

### 4. 享元状态验证

```java
/**
 * 状态验证工具
 */
public class FlyweightStateValidator {
    public static void validateIntrinsicState(Object state) {
        if (state instanceof Mutable) {
            throw new IllegalArgumentException("内部状态不能包含可变对象");
        }
        // 更多验证逻辑...
    }

    public static void validateExtrinsicState(Object state) {
        if (state == null) {
            throw new IllegalArgumentException("外部状态不能为null");
        }
        // 更多验证逻辑...
    }
}
```

## 🚀 总结

享元模式通过共享相同的对象来大幅减少内存使用，特别适用于：

- **大量相似对象**的场景
- **内存优化要求高**的系统
- **对象创建成本高**的情况

核心思想：
- **内部状态共享**
- **外部状态独立**
- **工厂统一管理**

设计要点：
- **正确区分内部和外部状态**
- **线程安全的工厂实现**
- **合理的缓存策略**

记住，**享元模式是内存优化器，不是万能减肥药**，要在合适的大量对象场景下使用！

---
*下一篇：代理模式 - 控制对象访问的智能代理*