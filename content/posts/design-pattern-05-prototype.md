---
title: "设计模式详解：原型模式(Prototype) - 对象克隆的高效实现"
date: 2025-09-18T20:00:00+08:00
draft: false
tags: ["设计模式", "原型模式", "Prototype", "Java", "创建型模式"]
categories: ["设计模式"]
author: "lesshash"
description: "深入浅出讲解原型模式，从基础概念到高级实现，包含深克隆、浅克隆等实战技巧，让你彻底掌握对象克隆的艺术"
---

## 🎯 什么是原型模式？

### 生活中的例子
想象一下，你有一张精美的手工贺卡，朋友们都想要同样的贺卡。与其重新设计制作，不如直接**复印**这张贺卡。这就是原型模式的核心思想：**通过克隆现有对象来创建新对象，而不是重新构造**。

### 问题背景
在软件开发中，有些对象创建成本很高：
- 🎨 复杂的图形对象
- 📊 包含大量数据的报表
- 🌐 网络请求获得的对象
- 🗄️ 数据库查询结果对象
- ⚙️ 配置复杂的系统对象

如果每次都从头创建，会导致：
- 性能问题（创建耗时）
- 资源浪费（重复计算）
- 代码复杂（重复初始化逻辑）

## 🧠 设计思想

### 核心原则
1. **复制接口** - 定义克隆方法
2. **具体原型** - 实现克隆逻辑
3. **浅克隆 vs 深克隆** - 选择合适的克隆深度
4. **原型管理器** - 管理原型对象

### 记忆口诀
> **"复制粘贴，原样再来"**

## 💻 代码实现

### 1. 基础原型模式

```java
/**
 * 抽象原型类
 */
public abstract class Prototype implements Cloneable {
    protected String name;

    public Prototype(String name) {
        this.name = name;
    }

    public abstract Prototype clone() throws CloneNotSupportedException;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}

/**
 * 具体原型：简历类
 */
public class Resume extends Prototype {
    private String education;
    private String experience;
    private String skills;

    public Resume(String name) {
        super(name);
    }

    public Resume(String name, String education, String experience, String skills) {
        super(name);
        this.education = education;
        this.experience = experience;
        this.skills = skills;
    }

    @Override
    public Resume clone() throws CloneNotSupportedException {
        // 浅克隆：只复制基本类型和String
        return (Resume) super.clone();
    }

    public void display() {
        System.out.println("=== 个人简历 ===");
        System.out.println("姓名: " + name);
        System.out.println("学历: " + education);
        System.out.println("经验: " + experience);
        System.out.println("技能: " + skills);
    }

    // getter和setter方法
    public String getEducation() { return education; }
    public void setEducation(String education) { this.education = education; }

    public String getExperience() { return experience; }
    public void setExperience(String experience) { this.experience = experience; }

    public String getSkills() { return skills; }
    public void setSkills(String skills) { this.skills = skills; }
}

// 使用示例
public class BasicPrototypeDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 原型模式基础示例 ===");

        // 创建原始简历
        Resume originalResume = new Resume("张三", "本科", "3年Java开发", "Spring, MySQL, Redis");
        System.out.println("\n原始简历：");
        originalResume.display();

        // 克隆简历并修改
        Resume clonedResume = originalResume.clone();
        clonedResume.setName("李四");
        clonedResume.setExperience("5年Java开发");

        System.out.println("\n克隆后的简历：");
        clonedResume.display();

        // 验证是不同的对象
        System.out.println("\n对象比较：");
        System.out.println("originalResume == clonedResume: " + (originalResume == clonedResume));
        System.out.println("originalResume.equals(clonedResume): " + originalResume.equals(clonedResume));
    }
}
```

### 2. 深克隆实现

```java
/**
 * 需要深克隆的复杂对象
 */
public class Address implements Cloneable {
    private String country;
    private String city;
    private String street;

    public Address(String country, String city, String street) {
        this.country = country;
        this.city = city;
        this.street = street;
    }

    @Override
    public Address clone() throws CloneNotSupportedException {
        return (Address) super.clone();
    }

    @Override
    public String toString() {
        return country + " " + city + " " + street;
    }

    // getter和setter方法
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getStreet() { return street; }
    public void setStreet(String street) { this.street = street; }
}

/**
 * 员工类 - 演示深克隆
 */
public class Employee implements Cloneable {
    private String name;
    private int age;
    private Address address; // 引用类型，需要深克隆
    private List<String> projects; // 集合类型，需要深克隆

    public Employee(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
        this.projects = new ArrayList<>();
    }

    // 浅克隆 - 只克隆基本类型，引用类型共享
    public Employee shallowClone() throws CloneNotSupportedException {
        return (Employee) super.clone();
    }

    // 深克隆 - 递归克隆所有引用类型
    public Employee deepClone() throws CloneNotSupportedException {
        Employee cloned = (Employee) super.clone();

        // 深克隆Address对象
        cloned.address = this.address.clone();

        // 深克隆List对象
        cloned.projects = new ArrayList<>(this.projects);

        return cloned;
    }

    // 使用序列化实现深克隆（更通用的方法）
    public Employee deepCloneBySerializable() {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(this);

            ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bis);
            return (Employee) ois.readObject();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public void addProject(String project) {
        this.projects.add(project);
    }

    public void display() {
        System.out.println("员工信息:");
        System.out.println("  姓名: " + name);
        System.out.println("  年龄: " + age);
        System.out.println("  地址: " + address);
        System.out.println("  项目: " + projects);
        System.out.println("  对象哈希: " + this.hashCode());
        System.out.println("  地址对象哈希: " + address.hashCode());
        System.out.println("  项目列表哈希: " + projects.hashCode());
    }

    // getter和setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    public Address getAddress() { return address; }
    public void setAddress(Address address) { this.address = address; }

    public List<String> getProjects() { return projects; }
}

// 深克隆演示
public class DeepCloneDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 深克隆 vs 浅克隆演示 ===");

        // 创建原始员工对象
        Address address = new Address("中国", "北京", "中关村大街1号");
        Employee original = new Employee("王五", 30, address);
        original.addProject("电商系统");
        original.addProject("支付系统");

        System.out.println("\n原始对象:");
        original.display();

        // 浅克隆
        Employee shallowCloned = original.shallowClone();
        shallowCloned.setName("赵六");
        shallowCloned.setAge(25);
        shallowCloned.getAddress().setCity("上海"); // 修改地址
        shallowCloned.addProject("CRM系统"); // 添加项目

        System.out.println("\n浅克隆后:");
        System.out.println("原始对象:");
        original.display();
        System.out.println("\n浅克隆对象:");
        shallowCloned.display();

        System.out.println("\n观察：浅克隆共享引用类型对象，修改会相互影响！");

        // 深克隆
        Employee deepCloned = original.deepClone();
        deepCloned.setName("孙七");
        deepCloned.setAge(28);
        deepCloned.getAddress().setCity("广州"); // 修改地址
        deepCloned.addProject("物流系统"); // 添加项目

        System.out.println("\n深克隆后:");
        System.out.println("原始对象:");
        original.display();
        System.out.println("\n深克隆对象:");
        deepCloned.display();

        System.out.println("\n观察：深克隆完全独立，修改不会相互影响！");
    }
}
```

### 3. 原型管理器模式

```java
/**
 * 抽象形状原型
 */
public abstract class Shape implements Cloneable {
    protected String type;
    protected String color;

    public Shape(String type, String color) {
        this.type = type;
        this.color = color;
    }

    public abstract void draw();
    public abstract Shape clone() throws CloneNotSupportedException;

    public String getType() { return type; }
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}

/**
 * 圆形原型
 */
public class Circle extends Shape {
    private int radius;

    public Circle(String color, int radius) {
        super("Circle", color);
        this.radius = radius;
    }

    @Override
    public void draw() {
        System.out.println("绘制 " + color + " 圆形，半径: " + radius);
    }

    @Override
    public Circle clone() throws CloneNotSupportedException {
        return (Circle) super.clone();
    }

    public int getRadius() { return radius; }
    public void setRadius(int radius) { this.radius = radius; }
}

/**
 * 矩形原型
 */
public class Rectangle extends Shape {
    private int width;
    private int height;

    public Rectangle(String color, int width, int height) {
        super("Rectangle", color);
        this.width = width;
        this.height = height;
    }

    @Override
    public void draw() {
        System.out.println("绘制 " + color + " 矩形，宽: " + width + ", 高: " + height);
    }

    @Override
    public Rectangle clone() throws CloneNotSupportedException {
        return (Rectangle) super.clone();
    }

    public int getWidth() { return width; }
    public void setWidth(int width) { this.width = width; }

    public int getHeight() { return height; }
    public void setHeight(int height) { this.height = height; }
}

/**
 * 原型管理器 - 管理所有原型对象
 */
public class ShapePrototypeManager {
    private Map<String, Shape> prototypes = new HashMap<>();
    private static ShapePrototypeManager instance = new ShapePrototypeManager();

    private ShapePrototypeManager() {
        // 初始化预定义的原型
        loadPrototypes();
    }

    public static ShapePrototypeManager getInstance() {
        return instance;
    }

    private void loadPrototypes() {
        // 预设一些常用的原型
        prototypes.put("red-circle", new Circle("红色", 10));
        prototypes.put("blue-circle", new Circle("蓝色", 15));
        prototypes.put("green-rectangle", new Rectangle("绿色", 20, 30));
        prototypes.put("yellow-rectangle", new Rectangle("黄色", 25, 35));

        System.out.println("原型管理器初始化完成，加载了 " + prototypes.size() + " 个原型");
    }

    // 注册新原型
    public void addPrototype(String key, Shape prototype) {
        prototypes.put(key, prototype);
        System.out.println("注册新原型: " + key);
    }

    // 根据key克隆原型
    public Shape createShape(String prototypeKey) throws CloneNotSupportedException {
        Shape prototype = prototypes.get(prototypeKey);
        if (prototype != null) {
            return prototype.clone();
        }
        throw new IllegalArgumentException("找不到原型: " + prototypeKey);
    }

    // 列出所有可用原型
    public void listPrototypes() {
        System.out.println("=== 可用原型列表 ===");
        for (String key : prototypes.keySet()) {
            Shape shape = prototypes.get(key);
            System.out.println(key + " -> " + shape.getType() + " (" + shape.getColor() + ")");
        }
    }
}

// 原型管理器使用示例
public class PrototypeManagerDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 原型管理器模式演示 ===");

        ShapePrototypeManager manager = ShapePrototypeManager.getInstance();

        // 显示所有可用原型
        manager.listPrototypes();

        System.out.println("\n=== 克隆形状 ===");

        // 克隆红色圆形
        Shape redCircle1 = manager.createShape("red-circle");
        Shape redCircle2 = manager.createShape("red-circle");

        redCircle1.draw();
        redCircle2.draw();

        // 验证是不同的对象
        System.out.println("两个红色圆形是不同对象: " + (redCircle1 != redCircle2));

        // 克隆并修改属性
        Circle blueCircle = (Circle) manager.createShape("blue-circle");
        blueCircle.setRadius(25);
        blueCircle.draw();

        // 注册自定义原型
        Circle purpleCircle = new Circle("紫色", 8);
        manager.addPrototype("purple-circle", purpleCircle);

        Shape clonedPurple = manager.createShape("purple-circle");
        clonedPurple.draw();

        System.out.println("\n=== 批量创建形状 ===");
        String[] shapeKeys = {"red-circle", "blue-circle", "green-rectangle", "yellow-rectangle"};

        for (String key : shapeKeys) {
            Shape shape = manager.createShape(key);
            shape.draw();
        }
    }
}
```

## 🌟 实际应用场景

### 1. 数据库对象克隆

```java
/**
 * 数据库查询结果原型
 */
public class QueryResult implements Cloneable {
    private String sql;
    private List<Map<String, Object>> data;
    private long executeTime;
    private Date queryTime;

    public QueryResult(String sql) {
        this.sql = sql;
        this.data = new ArrayList<>();
        this.queryTime = new Date();

        // 模拟耗时的数据库查询
        executeQuery();
    }

    private void executeQuery() {
        System.out.println("执行数据库查询: " + sql);
        // 模拟查询耗时
        try {
            Thread.sleep(1000); // 模拟1秒查询时间
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 模拟查询结果
        for (int i = 1; i <= 5; i++) {
            Map<String, Object> row = new HashMap<>();
            row.put("id", i);
            row.put("name", "用户" + i);
            row.put("email", "user" + i + "@example.com");
            data.add(row);
        }

        executeTime = System.currentTimeMillis();
        System.out.println("查询完成，返回 " + data.size() + " 条记录");
    }

    @Override
    public QueryResult clone() throws CloneNotSupportedException {
        QueryResult cloned = (QueryResult) super.clone();

        // 深克隆数据列表
        cloned.data = new ArrayList<>();
        for (Map<String, Object> row : this.data) {
            cloned.data.add(new HashMap<>(row));
        }

        // 克隆时间对象
        cloned.queryTime = new Date(this.queryTime.getTime());

        System.out.println("克隆查询结果完成，避免了重新执行数据库查询");
        return cloned;
    }

    public void displayResult() {
        System.out.println("=== 查询结果 ===");
        System.out.println("SQL: " + sql);
        System.out.println("查询时间: " + queryTime);
        System.out.println("执行耗时: " + executeTime + "ms");
        System.out.println("结果数据:");
        for (Map<String, Object> row : data) {
            System.out.println("  " + row);
        }
    }

    // 修改数据的方法
    public void updateUserName(int id, String newName) {
        for (Map<String, Object> row : data) {
            if (Objects.equals(row.get("id"), id)) {
                row.put("name", newName);
                break;
            }
        }
    }
}

// 数据库查询结果克隆演示
public class DatabaseQueryDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 数据库查询结果克隆演示 ===");

        // 首次查询（耗时操作）
        System.out.println("\n1. 首次执行查询:");
        QueryResult originalResult = new QueryResult("SELECT * FROM users WHERE active = 1");
        originalResult.displayResult();

        // 克隆查询结果（避免重新查询）
        System.out.println("\n2. 克隆查询结果:");
        QueryResult clonedResult = originalResult.clone();

        // 修改克隆的结果
        clonedResult.updateUserName(1, "管理员");
        System.out.println("\n3. 修改克隆结果后:");

        System.out.println("原始结果:");
        originalResult.displayResult();

        System.out.println("\n克隆结果:");
        clonedResult.displayResult();
    }
}
```

### 2. 图形编辑器原型

```java
/**
 * 图形元素抽象原型
 */
public abstract class GraphicElement implements Cloneable {
    protected int x, y; // 位置
    protected String color;
    protected int width, height; // 尺寸

    public GraphicElement(int x, int y, String color, int width, int height) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.width = width;
        this.height = height;
    }

    public abstract void render();
    public abstract GraphicElement clone() throws CloneNotSupportedException;

    // 移动元素
    public void moveTo(int newX, int newY) {
        this.x = newX;
        this.y = newY;
    }

    // getter和setter方法
    public int getX() { return x; }
    public int getY() { return y; }
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
    public int getWidth() { return width; }
    public int getHeight() { return height; }
}

/**
 * 文本框元素
 */
public class TextBox extends GraphicElement {
    private String text;
    private String font;
    private int fontSize;

    public TextBox(int x, int y, String color, int width, int height,
                   String text, String font, int fontSize) {
        super(x, y, color, width, height);
        this.text = text;
        this.font = font;
        this.fontSize = fontSize;
    }

    @Override
    public void render() {
        System.out.println("渲染文本框:");
        System.out.println("  位置: (" + x + ", " + y + ")");
        System.out.println("  尺寸: " + width + "x" + height);
        System.out.println("  颜色: " + color);
        System.out.println("  文本: " + text);
        System.out.println("  字体: " + font + ", 大小: " + fontSize);
    }

    @Override
    public TextBox clone() throws CloneNotSupportedException {
        return (TextBox) super.clone();
    }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getFont() { return font; }
    public void setFont(String font) { this.font = font; }

    public int getFontSize() { return fontSize; }
    public void setFontSize(int fontSize) { this.fontSize = fontSize; }
}

/**
 * 按钮元素
 */
public class Button extends GraphicElement {
    private String label;
    private String style;

    public Button(int x, int y, String color, int width, int height,
                  String label, String style) {
        super(x, y, color, width, height);
        this.label = label;
        this.style = style;
    }

    @Override
    public void render() {
        System.out.println("渲染按钮:");
        System.out.println("  位置: (" + x + ", " + y + ")");
        System.out.println("  尺寸: " + width + "x" + height);
        System.out.println("  颜色: " + color);
        System.out.println("  标签: " + label);
        System.out.println("  样式: " + style);
    }

    @Override
    public Button clone() throws CloneNotSupportedException {
        return (Button) super.clone();
    }

    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }

    public String getStyle() { return style; }
    public void setStyle(String style) { this.style = style; }
}

/**
 * 图形编辑器 - 使用原型模式复制元素
 */
public class GraphicEditor {
    private List<GraphicElement> elements = new ArrayList<>();
    private GraphicElement clipboard; // 剪贴板

    // 添加元素
    public void addElement(GraphicElement element) {
        elements.add(element);
        System.out.println("添加了新元素到画布");
    }

    // 复制元素到剪贴板
    public void copyElement(int index) throws CloneNotSupportedException {
        if (index >= 0 && index < elements.size()) {
            clipboard = elements.get(index).clone();
            System.out.println("元素已复制到剪贴板");
        }
    }

    // 粘贴元素从剪贴板
    public void pasteElement(int offsetX, int offsetY) throws CloneNotSupportedException {
        if (clipboard != null) {
            GraphicElement newElement = clipboard.clone();
            newElement.moveTo(newElement.getX() + offsetX, newElement.getY() + offsetY);
            elements.add(newElement);
            System.out.println("从剪贴板粘贴了新元素");
        }
    }

    // 渲染所有元素
    public void renderAll() {
        System.out.println("\n=== 画布渲染 ===");
        for (int i = 0; i < elements.size(); i++) {
            System.out.println("元素 " + i + ":");
            elements.get(i).render();
            System.out.println();
        }
    }

    // 批量复制元素（创建网格布局）
    public void createGrid(int sourceIndex, int rows, int cols, int spacingX, int spacingY)
            throws CloneNotSupportedException {
        if (sourceIndex >= 0 && sourceIndex < elements.size()) {
            GraphicElement template = elements.get(sourceIndex);

            for (int row = 0; row < rows; row++) {
                for (int col = 0; col < cols; col++) {
                    if (row == 0 && col == 0) continue; // 跳过原始元素

                    GraphicElement cloned = template.clone();
                    cloned.moveTo(
                        template.getX() + col * spacingX,
                        template.getY() + row * spacingY
                    );
                    elements.add(cloned);
                }
            }
            System.out.println("创建了 " + (rows * cols - 1) + " 个网格布局元素");
        }
    }
}

// 图形编辑器演示
public class GraphicEditorDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 图形编辑器原型模式演示 ===");

        GraphicEditor editor = new GraphicEditor();

        // 创建原始元素
        TextBox titleText = new TextBox(10, 10, "黑色", 200, 30,
                                       "标题文本", "Arial", 16);
        Button submitButton = new Button(50, 100, "蓝色", 100, 40,
                                       "提交", "圆角");

        editor.addElement(titleText);
        editor.addElement(submitButton);

        System.out.println("\n=== 初始画布 ===");
        editor.renderAll();

        // 复制粘贴操作
        System.out.println("=== 复制粘贴操作 ===");
        editor.copyElement(0); // 复制标题文本
        editor.pasteElement(0, 50); // 粘贴到下方

        // 修改粘贴的文本内容
        TextBox copiedText = (TextBox) editor.elements.get(2);
        copiedText.setText("副标题文本");
        copiedText.setColor("灰色");

        System.out.println("\n=== 复制粘贴后画布 ===");
        editor.renderAll();

        // 创建按钮网格
        System.out.println("=== 创建按钮网格 ===");
        editor.createGrid(1, 2, 3, 120, 60); // 基于索引1的按钮创建2行3列网格

        System.out.println("\n=== 最终画布 ===");
        editor.renderAll();
    }
}
```

### 3. 游戏角色原型系统

```java
/**
 * 游戏角色属性
 */
public class GameCharacterStats implements Cloneable {
    private int health;
    private int mana;
    private int attack;
    private int defense;
    private int speed;

    public GameCharacterStats(int health, int mana, int attack, int defense, int speed) {
        this.health = health;
        this.mana = mana;
        this.attack = attack;
        this.defense = defense;
        this.speed = speed;
    }

    @Override
    public GameCharacterStats clone() throws CloneNotSupportedException {
        return (GameCharacterStats) super.clone();
    }

    @Override
    public String toString() {
        return String.format("血量:%d, 魔法:%d, 攻击:%d, 防御:%d, 速度:%d",
                           health, mana, attack, defense, speed);
    }

    // getter和setter方法
    public int getHealth() { return health; }
    public void setHealth(int health) { this.health = health; }

    public int getMana() { return mana; }
    public void setMana(int mana) { this.mana = mana; }

    public int getAttack() { return attack; }
    public void setAttack(int attack) { this.attack = attack; }

    public int getDefense() { return defense; }
    public void setDefense(int defense) { this.defense = defense; }

    public int getSpeed() { return speed; }
    public void setSpeed(int speed) { this.speed = speed; }
}

/**
 * 游戏角色原型
 */
public class GameCharacter implements Cloneable {
    private String name;
    private String characterClass;
    private int level;
    private GameCharacterStats stats;
    private List<String> skills;
    private List<String> equipment;

    public GameCharacter(String name, String characterClass, int level, GameCharacterStats stats) {
        this.name = name;
        this.characterClass = characterClass;
        this.level = level;
        this.stats = stats;
        this.skills = new ArrayList<>();
        this.equipment = new ArrayList<>();
    }

    @Override
    public GameCharacter clone() throws CloneNotSupportedException {
        GameCharacter cloned = (GameCharacter) super.clone();

        // 深克隆属性对象
        cloned.stats = this.stats.clone();

        // 深克隆技能列表
        cloned.skills = new ArrayList<>(this.skills);

        // 深克隆装备列表
        cloned.equipment = new ArrayList<>(this.equipment);

        return cloned;
    }

    public void addSkill(String skill) {
        this.skills.add(skill);
    }

    public void addEquipment(String item) {
        this.equipment.add(item);
    }

    public void levelUp() {
        this.level++;
        // 升级时提升属性
        stats.setHealth(stats.getHealth() + 20);
        stats.setMana(stats.getMana() + 10);
        stats.setAttack(stats.getAttack() + 5);
        stats.setDefense(stats.getDefense() + 3);
        stats.setSpeed(stats.getSpeed() + 2);
    }

    public void displayCharacter() {
        System.out.println("=== 角色信息 ===");
        System.out.println("姓名: " + name);
        System.out.println("职业: " + characterClass);
        System.out.println("等级: " + level);
        System.out.println("属性: " + stats);
        System.out.println("技能: " + skills);
        System.out.println("装备: " + equipment);
        System.out.println("对象哈希: " + this.hashCode());
    }

    // getter和setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCharacterClass() { return characterClass; }
    public int getLevel() { return level; }
    public GameCharacterStats getStats() { return stats; }
    public List<String> getSkills() { return skills; }
    public List<String> getEquipment() { return equipment; }
}

/**
 * 游戏角色工厂 - 使用原型模式
 */
public class GameCharacterFactory {
    private Map<String, GameCharacter> characterTemplates = new HashMap<>();

    public GameCharacterFactory() {
        initializeTemplates();
    }

    private void initializeTemplates() {
        // 创建战士模板
        GameCharacterStats warriorStats = new GameCharacterStats(150, 50, 25, 20, 10);
        GameCharacter warrior = new GameCharacter("战士模板", "战士", 1, warriorStats);
        warrior.addSkill("重击");
        warrior.addSkill("格挡");
        warrior.addEquipment("铁剑");
        warrior.addEquipment("铁甲");
        characterTemplates.put("warrior", warrior);

        // 创建法师模板
        GameCharacterStats mageStats = new GameCharacterStats(80, 150, 30, 10, 15);
        GameCharacter mage = new GameCharacter("法师模板", "法师", 1, mageStats);
        mage.addSkill("火球术");
        mage.addSkill("冰箭术");
        mage.addEquipment("法杖");
        mage.addEquipment("法袍");
        characterTemplates.put("mage", mage);

        // 创建弓箭手模板
        GameCharacterStats archerStats = new GameCharacterStats(100, 80, 28, 12, 20);
        GameCharacter archer = new GameCharacter("弓箭手模板", "弓箭手", 1, archerStats);
        archer.addSkill("多重射击");
        archer.addSkill("瞄准射击");
        archer.addEquipment("长弓");
        archer.addEquipment("皮甲");
        characterTemplates.put("archer", archer);

        System.out.println("角色模板初始化完成，共 " + characterTemplates.size() + " 个模板");
    }

    // 创建角色（使用原型克隆）
    public GameCharacter createCharacter(String templateName, String playerName)
            throws CloneNotSupportedException {
        GameCharacter template = characterTemplates.get(templateName);
        if (template != null) {
            GameCharacter newCharacter = template.clone();
            newCharacter.setName(playerName);
            System.out.println("基于模板 '" + templateName + "' 创建角色: " + playerName);
            return newCharacter;
        }
        throw new IllegalArgumentException("未找到角色模板: " + templateName);
    }

    // 列出所有可用模板
    public void listTemplates() {
        System.out.println("=== 可用角色模板 ===");
        for (String key : characterTemplates.keySet()) {
            GameCharacter template = characterTemplates.get(key);
            System.out.println(key + " -> " + template.getCharacterClass() +
                             " (Level " + template.getLevel() + ")");
        }
    }
}

// 游戏角色原型演示
public class GameCharacterDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 游戏角色原型系统演示 ===");

        GameCharacterFactory factory = new GameCharacterFactory();
        factory.listTemplates();

        System.out.println("\n=== 创建玩家角色 ===");

        // 创建多个战士角色
        GameCharacter warrior1 = factory.createCharacter("warrior", "钢铁勇士");
        GameCharacter warrior2 = factory.createCharacter("warrior", "圣光战士");

        // 创建法师角色
        GameCharacter mage1 = factory.createCharacter("mage", "元素法师");

        // 创建弓箭手角色
        GameCharacter archer1 = factory.createCharacter("archer", "精灵射手");

        System.out.println("\n=== 角色个性化定制 ===");

        // 个性化第一个战士
        warrior1.levelUp();
        warrior1.levelUp();
        warrior1.addSkill("狂暴");
        warrior1.addEquipment("烈焰之剑");

        // 个性化法师
        mage1.addSkill("传送术");
        mage1.addEquipment("智慧之帽");

        System.out.println("\n=== 角色展示 ===");

        warrior1.displayCharacter();
        System.out.println();

        warrior2.displayCharacter();
        System.out.println();

        mage1.displayCharacter();
        System.out.println();

        archer1.displayCharacter();

        System.out.println("\n=== 验证独立性 ===");
        System.out.println("warrior1 == warrior2: " + (warrior1 == warrior2));
        System.out.println("两个战士角色是完全独立的对象");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **性能优化**
   - 避免重新创建复杂对象
   - 减少初始化开销

2. **简化对象创建**
   - 无需知道具体创建过程
   - 复制比构造更简单

3. **动态配置**
   - 运行时添加或删除原型
   - 灵活的对象管理

4. **避免子类爆炸**
   - 用克隆替代继承
   - 减少类的数量

### ❌ 缺点

1. **克隆复杂性**
   - 深克隆实现复杂
   - 循环引用问题

2. **克隆方法限制**
   - 必须实现Cloneable接口
   - clone方法的访问权限问题

3. **对象修改困难**
   - 修改原型影响所有克隆
   - 需要谨慎管理原型状态

## 🎯 使用场景总结

### 适合使用原型模式的场景：
- 🎨 **图形编辑软件** - 复制图形元素
- 🎮 **游戏开发** - 批量创建相似对象
- 📊 **报表系统** - 复制复杂报表模板
- 🗄️ **数据库ORM** - 克隆查询结果对象
- ⚙️ **配置管理** - 复制配置对象

### 不适合使用原型模式的场景：
- 对象包含不可克隆的资源
- 深克隆成本过高的对象
- 简单对象（构造成本很低）
- 对象间存在复杂依赖关系

## 🧠 记忆技巧

### 形象比喻
> **原型模式就像是 "复印机"**：
> - 有一份原始文档（原型对象）
> - 想要更多副本时直接复印（克隆）
> - 比重新写一份要快得多（避免重新构造）
> - 每份副本都可以独立修改（对象独立性）

### 实现要点
> **"实现克隆，深浅分清，管理原型，按需复制"**

### 选择建议
1. **简单对象** → 浅克隆
2. **复杂对象** → 深克隆
3. **大量原型** → 原型管理器
4. **特殊需求** → 序列化克隆

## 🔧 最佳实践

### 1. 实现深克隆的通用方法

```java
/**
 * 通用深克隆工具类
 */
public class DeepCloneUtil {

    /**
     * 使用序列化实现深克隆（对象必须实现Serializable）
     */
    @SuppressWarnings("unchecked")
    public static <T> T deepClone(T original) {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(original);

            ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bis);
            return (T) ois.readObject();
        } catch (Exception e) {
            throw new RuntimeException("深克隆失败", e);
        }
    }

    /**
     * 使用JSON实现深克隆（需要Gson等JSON库）
     */
    public static <T> T deepCloneByJson(T original, Class<T> clazz) {
        Gson gson = new Gson();
        String json = gson.toJson(original);
        return gson.fromJson(json, clazz);
    }
}
```

### 2. 线程安全的原型管理器

```java
/**
 * 线程安全的原型管理器
 */
public class ThreadSafePrototypeManager<T extends Cloneable> {
    private final ConcurrentHashMap<String, T> prototypes = new ConcurrentHashMap<>();

    public void registerPrototype(String key, T prototype) {
        prototypes.put(key, prototype);
    }

    @SuppressWarnings("unchecked")
    public T createInstance(String key) throws CloneNotSupportedException {
        T prototype = prototypes.get(key);
        if (prototype != null) {
            return (T) prototype.getClass().getMethod("clone").invoke(prototype);
        }
        return null;
    }
}
```

## 🚀 总结

原型模式通过克隆现有对象来创建新对象，特别适用于：

- **对象创建成本高**的场景
- **需要大量相似对象**的场景
- **避免复杂初始化**的场景

选择合适的克隆策略：
- **简单场景**：浅克隆
- **复杂对象**：深克隆
- **大量原型**：原型管理器

记住，**合理使用原型模式**，在性能和复杂性之间找到平衡！

---
*下一篇：适配器模式 - 让不兼容的接口协同工作*