---
title: "设计模式入门教程21：备忘录模式 - 优雅地保存和恢复对象状态"
date: 2024-12-21T10:21:00+08:00
draft: false
tags: ["设计模式", "备忘录模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是备忘录模式？

备忘录模式（Memento Pattern）是一种行为型设计模式，它允许在不破坏封装性的前提下，捕获一个对象的内部状态，并在该对象之外保存这个状态。这样以后就可以将该对象恢复到原先保存的状态。

### 🌟 现实生活中的例子

想象一下**游戏存档系统**：
- **存档**：保存当前游戏进度、角色状态、道具等
- **读档**：恢复到之前保存的游戏状态
- **多存档**：可以保存多个不同时间点的状态

又比如**文本编辑器的撤销功能**：
- **快照**：每次编辑前保存文档状态
- **撤销**：恢复到上一个保存的状态
- **重做**：在撤销后还能再恢复

这就是备忘录模式的典型应用！

## 🏗️ 模式结构

```java
// 备忘录接口
interface Memento {
    // 空接口，防止外部访问备忘录内容
}

// 发起者（原发器）
class Originator {
    private String state;

    public void setState(String state) {
        this.state = state;
    }

    public String getState() {
        return state;
    }

    // 创建备忘录
    public Memento createMemento() {
        return new ConcreteMemento(state);
    }

    // 从备忘录恢复
    public void restoreFromMemento(Memento memento) {
        if (memento instanceof ConcreteMemento) {
            this.state = ((ConcreteMemento) memento).getState();
        }
    }

    // 具体备忘录（内部类）
    private static class ConcreteMemento implements Memento {
        private final String state;

        public ConcreteMemento(String state) {
            this.state = state;
        }

        public String getState() {
            return state;
        }
    }
}

// 管理者
class Caretaker {
    private List<Memento> mementos = new ArrayList<>();

    public void addMemento(Memento memento) {
        mementos.add(memento);
    }

    public Memento getMemento(int index) {
        return mementos.get(index);
    }

    public int getMementoCount() {
        return mementos.size();
    }
}
```

## 💡 核心组件详解

### 1. 发起者（Originator）
```java
// 文本编辑器类
class TextEditor {
    private StringBuilder content;
    private String title;
    private int cursorPosition;
    private boolean isModified;

    public TextEditor() {
        this.content = new StringBuilder();
        this.title = "未命名文档";
        this.cursorPosition = 0;
        this.isModified = false;
    }

    // 编辑操作
    public void insertText(String text) {
        content.insert(cursorPosition, text);
        cursorPosition += text.length();
        isModified = true;
        System.out.println("插入文本：\"" + text + "\" 在位置 " + (cursorPosition - text.length()));
    }

    public void deleteText(int length) {
        if (cursorPosition >= length) {
            String deleted = content.substring(cursorPosition - length, cursorPosition);
            content.delete(cursorPosition - length, cursorPosition);
            cursorPosition -= length;
            isModified = true;
            System.out.println("删除文本：\"" + deleted + "\"");
        }
    }

    public void moveCursor(int position) {
        if (position >= 0 && position <= content.length()) {
            this.cursorPosition = position;
            System.out.println("光标移动到位置：" + position);
        }
    }

    public void setTitle(String title) {
        this.title = title;
        isModified = true;
        System.out.println("标题设置为：" + title);
    }

    // 创建备忘录
    public EditorMemento createMemento() {
        return new EditorMemento(
            content.toString(),
            title,
            cursorPosition,
            isModified
        );
    }

    // 从备忘录恢复
    public void restoreFromMemento(EditorMemento memento) {
        this.content = new StringBuilder(memento.getContent());
        this.title = memento.getTitle();
        this.cursorPosition = memento.getCursorPosition();
        this.isModified = memento.isModified();
        System.out.println("已恢复到之前的状态");
    }

    // 显示当前状态
    public void showStatus() {
        System.out.println("=== 编辑器状态 ===");
        System.out.println("标题：" + title);
        System.out.println("内容：\"" + content.toString() + "\"");
        System.out.println("光标位置：" + cursorPosition);
        System.out.println("已修改：" + isModified);
        System.out.println("字符数：" + content.length());
        System.out.println("================");
    }

    // Getters
    public String getContent() { return content.toString(); }
    public String getTitle() { return title; }
    public int getCursorPosition() { return cursorPosition; }
    public boolean isModified() { return isModified; }
}
```

### 2. 备忘录（Memento）
```java
// 编辑器备忘录类
class EditorMemento {
    private final String content;
    private final String title;
    private final int cursorPosition;
    private final boolean isModified;
    private final long timestamp;

    public EditorMemento(String content, String title, int cursorPosition, boolean isModified) {
        this.content = content;
        this.title = title;
        this.cursorPosition = cursorPosition;
        this.isModified = isModified;
        this.timestamp = System.currentTimeMillis();
    }

    // 只提供getter方法，保证不可变性
    public String getContent() { return content; }
    public String getTitle() { return title; }
    public int getCursorPosition() { return cursorPosition; }
    public boolean isModified() { return isModified; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "备忘录[标题=" + title + ", 内容长度=" + content.length() +
               ", 时间=" + new Date(timestamp) + "]";
    }
}
```

### 3. 管理者（Caretaker）
```java
// 撤销重做管理器
class UndoRedoManager {
    private List<EditorMemento> history;
    private int currentIndex;
    private final int maxHistorySize;

    public UndoRedoManager(int maxHistorySize) {
        this.history = new ArrayList<>();
        this.currentIndex = -1;
        this.maxHistorySize = maxHistorySize;
    }

    // 保存状态
    public void saveState(EditorMemento memento) {
        // 如果当前不在历史末尾，删除后面的历史
        if (currentIndex < history.size() - 1) {
            history.subList(currentIndex + 1, history.size()).clear();
        }

        history.add(memento);
        currentIndex++;

        // 限制历史记录大小
        if (history.size() > maxHistorySize) {
            history.remove(0);
            currentIndex--;
        }

        System.out.println("已保存状态，当前历史位置：" + currentIndex + "/" + (history.size() - 1));
    }

    // 撤销
    public EditorMemento undo() {
        if (canUndo()) {
            currentIndex--;
            EditorMemento memento = history.get(currentIndex);
            System.out.println("撤销到：" + memento);
            return memento;
        }
        System.out.println("无法撤销：已到达历史开始");
        return null;
    }

    // 重做
    public EditorMemento redo() {
        if (canRedo()) {
            currentIndex++;
            EditorMemento memento = history.get(currentIndex);
            System.out.println("重做到：" + memento);
            return memento;
        }
        System.out.println("无法重做：已到达历史末尾");
        return null;
    }

    // 检查是否可以撤销
    public boolean canUndo() {
        return currentIndex > 0;
    }

    // 检查是否可以重做
    public boolean canRedo() {
        return currentIndex < history.size() - 1;
    }

    // 获取历史信息
    public void showHistory() {
        System.out.println("=== 撤销历史 ===");
        for (int i = 0; i < history.size(); i++) {
            String prefix = (i == currentIndex) ? "→ " : "  ";
            System.out.println(prefix + i + ": " + history.get(i));
        }
        System.out.println("===============");
    }

    public int getHistorySize() {
        return history.size();
    }

    public int getCurrentIndex() {
        return currentIndex;
    }

    // 清空历史
    public void clearHistory() {
        history.clear();
        currentIndex = -1;
        System.out.println("历史记录已清空");
    }
}
```

## 🎮 实际应用示例

### 示例1：游戏存档系统
```java
// 游戏角色类
class GameCharacter {
    private String name;
    private int level;
    private int health;
    private int mana;
    private int experience;
    private List<String> inventory;
    private String currentLocation;
    private Map<String, Integer> skills;

    public GameCharacter(String name) {
        this.name = name;
        this.level = 1;
        this.health = 100;
        this.mana = 50;
        this.experience = 0;
        this.inventory = new ArrayList<>();
        this.currentLocation = "新手村";
        this.skills = new HashMap<>();
        initializeSkills();
    }

    private void initializeSkills() {
        skills.put("剑术", 1);
        skills.put("魔法", 1);
        skills.put("防御", 1);
    }

    // 游戏操作
    public void gainExperience(int exp) {
        this.experience += exp;
        System.out.println(name + " 获得经验：" + exp + "，总经验：" + experience);

        // 检查升级
        if (experience >= level * 100) {
            levelUp();
        }
    }

    private void levelUp() {
        level++;
        health += 20;
        mana += 10;
        System.out.println("🎉 " + name + " 升级到 " + level + " 级！");
    }

    public void takeDamage(int damage) {
        health = Math.max(0, health - damage);
        System.out.println(name + " 受到 " + damage + " 点伤害，剩余生命：" + health);
    }

    public void heal(int amount) {
        health = Math.min(health + amount, level * 100);
        System.out.println(name + " 恢复 " + amount + " 点生命值");
    }

    public void addItem(String item) {
        inventory.add(item);
        System.out.println(name + " 获得物品：" + item);
    }

    public void useItem(String item) {
        if (inventory.remove(item)) {
            System.out.println(name + " 使用物品：" + item);
            // 根据物品类型执行效果
            if (item.contains("药水")) {
                heal(30);
            }
        }
    }

    public void moveTo(String location) {
        this.currentLocation = location;
        System.out.println(name + " 移动到：" + location);
    }

    public void improveSkill(String skillName, int improvement) {
        skills.put(skillName, skills.getOrDefault(skillName, 0) + improvement);
        System.out.println(name + " 的 " + skillName + " 技能提升到：" + skills.get(skillName));
    }

    // 创建存档
    public GameSave createSave(String saveDescription) {
        return new GameSave(
            name, level, health, mana, experience,
            new ArrayList<>(inventory),
            currentLocation,
            new HashMap<>(skills),
            saveDescription
        );
    }

    // 加载存档
    public void loadFromSave(GameSave save) {
        this.name = save.getName();
        this.level = save.getLevel();
        this.health = save.getHealth();
        this.mana = save.getMana();
        this.experience = save.getExperience();
        this.inventory = new ArrayList<>(save.getInventory());
        this.currentLocation = save.getCurrentLocation();
        this.skills = new HashMap<>(save.getSkills());
        System.out.println("已加载存档：" + save.getDescription());
    }

    public void showStatus() {
        System.out.println("=== " + name + " 状态 ===");
        System.out.println("等级：" + level);
        System.out.println("生命值：" + health);
        System.out.println("魔法值：" + mana);
        System.out.println("经验：" + experience);
        System.out.println("位置：" + currentLocation);
        System.out.println("背包：" + inventory);
        System.out.println("技能：" + skills);
        System.out.println("=================");
    }

    // Getters
    public String getName() { return name; }
    public int getLevel() { return level; }
    public int getHealth() { return health; }
    public int getMana() { return mana; }
    public int getExperience() { return experience; }
    public List<String> getInventory() { return inventory; }
    public String getCurrentLocation() { return currentLocation; }
    public Map<String, Integer> getSkills() { return skills; }
}

// 游戏存档类
class GameSave {
    private final String name;
    private final int level;
    private final int health;
    private final int mana;
    private final int experience;
    private final List<String> inventory;
    private final String currentLocation;
    private final Map<String, Integer> skills;
    private final String description;
    private final long timestamp;

    public GameSave(String name, int level, int health, int mana, int experience,
                   List<String> inventory, String currentLocation, Map<String, Integer> skills,
                   String description) {
        this.name = name;
        this.level = level;
        this.health = health;
        this.mana = mana;
        this.experience = experience;
        this.inventory = inventory;
        this.currentLocation = currentLocation;
        this.skills = skills;
        this.description = description;
        this.timestamp = System.currentTimeMillis();
    }

    // Getters
    public String getName() { return name; }
    public int getLevel() { return level; }
    public int getHealth() { return health; }
    public int getMana() { return mana; }
    public int getExperience() { return experience; }
    public List<String> getInventory() { return inventory; }
    public String getCurrentLocation() { return currentLocation; }
    public Map<String, Integer> getSkills() { return skills; }
    public String getDescription() { return description; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "存档[" + description + " - 等级" + level + " - " +
               new SimpleDateFormat("yyyy-MM-dd HH:mm").format(new Date(timestamp)) + "]";
    }
}

// 存档管理器
class SaveGameManager {
    private Map<String, GameSave> saves;
    private int maxSaves;

    public SaveGameManager(int maxSaves) {
        this.saves = new LinkedHashMap<>();
        this.maxSaves = maxSaves;
    }

    public void saveGame(String saveSlot, GameSave save) {
        if (saves.size() >= maxSaves && !saves.containsKey(saveSlot)) {
            // 删除最老的存档
            String oldestKey = saves.keySet().iterator().next();
            saves.remove(oldestKey);
            System.out.println("已删除最旧存档：" + oldestKey);
        }

        saves.put(saveSlot, save);
        System.out.println("游戏已保存到存档槽：" + saveSlot);
        System.out.println("存档信息：" + save);
    }

    public GameSave loadGame(String saveSlot) {
        GameSave save = saves.get(saveSlot);
        if (save != null) {
            System.out.println("加载存档：" + saveSlot);
            return save;
        } else {
            System.out.println("存档槽 " + saveSlot + " 为空");
            return null;
        }
    }

    public void deleteSave(String saveSlot) {
        if (saves.remove(saveSlot) != null) {
            System.out.println("已删除存档：" + saveSlot);
        } else {
            System.out.println("存档槽 " + saveSlot + " 不存在");
        }
    }

    public void listSaves() {
        System.out.println("=== 存档列表 ===");
        if (saves.isEmpty()) {
            System.out.println("暂无存档");
        } else {
            for (Map.Entry<String, GameSave> entry : saves.entrySet()) {
                System.out.println("槽位 " + entry.getKey() + ": " + entry.getValue());
            }
        }
        System.out.println("==============");
    }

    public boolean hasSave(String saveSlot) {
        return saves.containsKey(saveSlot);
    }

    public int getSaveCount() {
        return saves.size();
    }
}

// 游戏使用示例
public class GameSaveExample {
    public static void main(String[] args) throws InterruptedException {
        // 创建游戏角色和存档管理器
        GameCharacter hero = new GameCharacter("勇者阿尔托");
        SaveGameManager saveManager = new SaveGameManager(5);

        // 初始状态
        hero.showStatus();

        // 游戏进行一段时间
        System.out.println("\n=== 游戏开始 ===");
        hero.addItem("生命药水");
        hero.addItem("魔法药水");
        hero.gainExperience(50);
        hero.improveSkill("剑术", 2);

        // 保存游戏状态1
        saveManager.saveGame("save1", hero.createSave("新手村初期状态"));
        Thread.sleep(1000);

        // 继续游戏
        System.out.println("\n=== 继续冒险 ===");
        hero.moveTo("森林");
        hero.gainExperience(80);
        hero.takeDamage(30);
        hero.addItem("铁剑");
        hero.improveSkill("防御", 1);

        // 保存游戏状态2
        saveManager.saveGame("save2", hero.createSave("森林探险"));
        Thread.sleep(1000);

        // 继续游戏
        System.out.println("\n=== 深入探险 ===");
        hero.moveTo("地下城");
        hero.gainExperience(120); // 这会触发升级
        hero.takeDamage(50);
        hero.useItem("生命药水");
        hero.addItem("魔法书");

        // 保存游戏状态3
        saveManager.saveGame("save3", hero.createSave("地下城探险"));

        // 显示当前状态
        System.out.println("\n=== 当前状态 ===");
        hero.showStatus();

        // 显示所有存档
        saveManager.listSaves();

        // 模拟读档到较早状态
        System.out.println("\n=== 读取存档 ===");
        GameSave loadedSave = saveManager.loadGame("save1");
        if (loadedSave != null) {
            hero.loadFromSave(loadedSave);
            hero.showStatus();
        }

        // 再次读档到最新状态
        System.out.println("\n=== 读取最新存档 ===");
        loadedSave = saveManager.loadGame("save3");
        if (loadedSave != null) {
            hero.loadFromSave(loadedSave);
            hero.showStatus();
        }
    }
}
```

### 示例2：绘图应用撤销重做
```java
// 绘图形状接口
interface Shape extends Cloneable {
    void draw();
    Shape clone();
    String getInfo();
}

// 圆形
class Circle implements Shape {
    private int x, y, radius;
    private String color;

    public Circle(int x, int y, int radius, String color) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
    }

    @Override
    public void draw() {
        System.out.println("绘制圆形：位置(" + x + "," + y + ") 半径=" + radius + " 颜色=" + color);
    }

    @Override
    public Circle clone() {
        return new Circle(x, y, radius, color);
    }

    @Override
    public String getInfo() {
        return "圆形(" + x + "," + y + "," + radius + "," + color + ")";
    }

    // Getters and Setters
    public void setPosition(int x, int y) { this.x = x; this.y = y; }
    public void setRadius(int radius) { this.radius = radius; }
    public void setColor(String color) { this.color = color; }
}

// 矩形
class Rectangle implements Shape {
    private int x, y, width, height;
    private String color;

    public Rectangle(int x, int y, int width, int height, String color) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
    }

    @Override
    public void draw() {
        System.out.println("绘制矩形：位置(" + x + "," + y + ") 尺寸=" + width + "x" + height + " 颜色=" + color);
    }

    @Override
    public Rectangle clone() {
        return new Rectangle(x, y, width, height, color);
    }

    @Override
    public String getInfo() {
        return "矩形(" + x + "," + y + "," + width + "x" + height + "," + color + ")";
    }

    public void setPosition(int x, int y) { this.x = x; this.y = y; }
    public void setSize(int width, int height) { this.width = width; this.height = height; }
    public void setColor(String color) { this.color = color; }
}

// 绘图画布
class DrawingCanvas {
    private List<Shape> shapes;
    private String canvasName;
    private String backgroundColor;

    public DrawingCanvas() {
        this.shapes = new ArrayList<>();
        this.canvasName = "未命名画布";
        this.backgroundColor = "白色";
    }

    // 添加形状
    public void addShape(Shape shape) {
        shapes.add(shape);
        System.out.println("添加形状：" + shape.getInfo());
    }

    // 删除形状
    public void removeShape(int index) {
        if (index >= 0 && index < shapes.size()) {
            Shape removed = shapes.remove(index);
            System.out.println("删除形状：" + removed.getInfo());
        }
    }

    // 移动形状
    public void moveShape(int index, int deltaX, int deltaY) {
        if (index >= 0 && index < shapes.size()) {
            Shape shape = shapes.get(index);
            if (shape instanceof Circle) {
                Circle circle = (Circle) shape;
                // 这里简化处理，实际应该有更好的方法
                System.out.println("移动圆形：" + shape.getInfo());
            } else if (shape instanceof Rectangle) {
                Rectangle rect = (Rectangle) shape;
                System.out.println("移动矩形：" + shape.getInfo());
            }
        }
    }

    // 设置画布属性
    public void setCanvasName(String name) {
        this.canvasName = name;
        System.out.println("画布名称设置为：" + name);
    }

    public void setBackgroundColor(String color) {
        this.backgroundColor = color;
        System.out.println("背景色设置为：" + color);
    }

    // 绘制所有形状
    public void drawAll() {
        System.out.println("=== 绘制画布：" + canvasName + " ===");
        System.out.println("背景色：" + backgroundColor);
        if (shapes.isEmpty()) {
            System.out.println("画布为空");
        } else {
            for (int i = 0; i < shapes.size(); i++) {
                System.out.print((i + 1) + ". ");
                shapes.get(i).draw();
            }
        }
        System.out.println("========================");
    }

    // 创建快照
    public CanvasSnapshot createSnapshot(String description) {
        // 深拷贝所有形状
        List<Shape> shapesCopy = new ArrayList<>();
        for (Shape shape : shapes) {
            shapesCopy.add(shape.clone());
        }

        return new CanvasSnapshot(shapesCopy, canvasName, backgroundColor, description);
    }

    // 从快照恢复
    public void restoreFromSnapshot(CanvasSnapshot snapshot) {
        this.shapes = new ArrayList<>();
        for (Shape shape : snapshot.getShapes()) {
            this.shapes.add(shape.clone());
        }
        this.canvasName = snapshot.getCanvasName();
        this.backgroundColor = snapshot.getBackgroundColor();
        System.out.println("已恢复快照：" + snapshot.getDescription());
    }

    public List<Shape> getShapes() { return shapes; }
    public String getCanvasName() { return canvasName; }
    public String getBackgroundColor() { return backgroundColor; }
}

// 画布快照
class CanvasSnapshot {
    private final List<Shape> shapes;
    private final String canvasName;
    private final String backgroundColor;
    private final String description;
    private final long timestamp;

    public CanvasSnapshot(List<Shape> shapes, String canvasName, String backgroundColor, String description) {
        this.shapes = new ArrayList<>(shapes);
        this.canvasName = canvasName;
        this.backgroundColor = backgroundColor;
        this.description = description;
        this.timestamp = System.currentTimeMillis();
    }

    public List<Shape> getShapes() { return shapes; }
    public String getCanvasName() { return canvasName; }
    public String getBackgroundColor() { return backgroundColor; }
    public String getDescription() { return description; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "快照[" + description + " - " + shapes.size() + "个形状 - " +
               new SimpleDateFormat("HH:mm:ss").format(new Date(timestamp)) + "]";
    }
}

// 绘图应用的撤销重做管理器
class DrawingUndoRedoManager {
    private List<CanvasSnapshot> history;
    private int currentIndex;
    private final int maxHistory;

    public DrawingUndoRedoManager(int maxHistory) {
        this.history = new ArrayList<>();
        this.currentIndex = -1;
        this.maxHistory = maxHistory;
    }

    public void saveSnapshot(CanvasSnapshot snapshot) {
        // 清除当前位置之后的历史
        if (currentIndex < history.size() - 1) {
            history.subList(currentIndex + 1, history.size()).clear();
        }

        history.add(snapshot);
        currentIndex++;

        // 限制历史大小
        if (history.size() > maxHistory) {
            history.remove(0);
            currentIndex--;
        }

        System.out.println("保存快照：" + snapshot);
    }

    public CanvasSnapshot undo() {
        if (canUndo()) {
            currentIndex--;
            CanvasSnapshot snapshot = history.get(currentIndex);
            System.out.println("撤销到：" + snapshot);
            return snapshot;
        }
        System.out.println("无法撤销");
        return null;
    }

    public CanvasSnapshot redo() {
        if (canRedo()) {
            currentIndex++;
            CanvasSnapshot snapshot = history.get(currentIndex);
            System.out.println("重做到：" + snapshot);
            return snapshot;
        }
        System.out.println("无法重做");
        return null;
    }

    public boolean canUndo() {
        return currentIndex > 0;
    }

    public boolean canRedo() {
        return currentIndex < history.size() - 1;
    }

    public void showHistory() {
        System.out.println("=== 操作历史 ===");
        for (int i = 0; i < history.size(); i++) {
            String marker = (i == currentIndex) ? "→ " : "  ";
            System.out.println(marker + i + ": " + history.get(i));
        }
        System.out.println("===============");
    }
}

// 绘图应用使用示例
public class DrawingAppExample {
    public static void main(String[] args) throws InterruptedException {
        DrawingCanvas canvas = new DrawingCanvas();
        DrawingUndoRedoManager undoRedoManager = new DrawingUndoRedoManager(10);

        // 初始状态
        canvas.setCanvasName("我的画作");
        undoRedoManager.saveSnapshot(canvas.createSnapshot("初始空画布"));

        // 添加一些形状
        System.out.println("\n=== 开始绘图 ===");
        canvas.addShape(new Circle(100, 100, 50, "红色"));
        undoRedoManager.saveSnapshot(canvas.createSnapshot("添加红色圆形"));
        Thread.sleep(500);

        canvas.addShape(new Rectangle(200, 150, 80, 60, "蓝色"));
        undoRedoManager.saveSnapshot(canvas.createSnapshot("添加蓝色矩形"));
        Thread.sleep(500);

        canvas.addShape(new Circle(300, 200, 30, "绿色"));
        undoRedoManager.saveSnapshot(canvas.createSnapshot("添加绿色圆形"));

        // 显示当前画布
        canvas.drawAll();

        // 设置背景色
        System.out.println("\n=== 修改背景 ===");
        canvas.setBackgroundColor("浅灰色");
        undoRedoManager.saveSnapshot(canvas.createSnapshot("修改背景色"));

        canvas.drawAll();

        // 显示历史
        undoRedoManager.showHistory();

        // 撤销操作
        System.out.println("\n=== 撤销操作 ===");
        CanvasSnapshot snapshot = undoRedoManager.undo();
        if (snapshot != null) {
            canvas.restoreFromSnapshot(snapshot);
            canvas.drawAll();
        }

        snapshot = undoRedoManager.undo();
        if (snapshot != null) {
            canvas.restoreFromSnapshot(snapshot);
            canvas.drawAll();
        }

        // 重做操作
        System.out.println("\n=== 重做操作 ===");
        snapshot = undoRedoManager.redo();
        if (snapshot != null) {
            canvas.restoreFromSnapshot(snapshot);
            canvas.drawAll();
        }

        // 在中间状态进行新操作
        System.out.println("\n=== 分支操作 ===");
        canvas.addShape(new Rectangle(50, 50, 40, 40, "黄色"));
        undoRedoManager.saveSnapshot(canvas.createSnapshot("添加黄色小矩形"));

        canvas.drawAll();
        undoRedoManager.showHistory();
    }
}
```

## ⚡ 高级应用

### 快照压缩和优化
```java
// 压缩快照管理器
class CompressedSnapshotManager {
    private List<EditorMemento> snapshots = new ArrayList<>();
    private final int compressionThreshold;

    public CompressedSnapshotManager(int compressionThreshold) {
        this.compressionThreshold = compressionThreshold;
    }

    public void addSnapshot(EditorMemento snapshot) {
        snapshots.add(snapshot);

        // 定期压缩旧快照
        if (snapshots.size() > compressionThreshold) {
            compressOldSnapshots();
        }
    }

    private void compressOldSnapshots() {
        // 保留最近的一些快照，压缩较老的
        int keepRecent = compressionThreshold / 2;
        int compressStart = snapshots.size() - keepRecent;

        for (int i = 0; i < compressStart - 1; i += 2) {
            // 删除中间的快照，只保留关键节点
            snapshots.remove(i + 1);
        }

        System.out.println("已压缩历史快照，当前快照数：" + snapshots.size());
    }
}

// 增量快照
class IncrementalSnapshot {
    private final String operation;
    private final Object data;
    private final long timestamp;

    public IncrementalSnapshot(String operation, Object data) {
        this.operation = operation;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }

    public String getOperation() { return operation; }
    public Object getData() { return data; }
    public long getTimestamp() { return timestamp; }
}

// 增量备忘录管理器
class IncrementalMementoManager {
    private EditorMemento baseSnapshot;
    private List<IncrementalSnapshot> increments = new ArrayList<>();

    public void setBaseSnapshot(EditorMemento snapshot) {
        this.baseSnapshot = snapshot;
        this.increments.clear();
    }

    public void addIncrement(String operation, Object data) {
        increments.add(new IncrementalSnapshot(operation, data));

        // 当增量太多时，创建新的基础快照
        if (increments.size() > 50) {
            compactToBase();
        }
    }

    private void compactToBase() {
        // 将所有增量应用到基础快照，创建新的基础快照
        // 这里简化实现
        System.out.println("压缩增量到基础快照");
        increments.clear();
    }
}
```

### 自动保存机制
```java
// 自动保存管理器
class AutoSaveManager {
    private final TextEditor editor;
    private final UndoRedoManager undoRedoManager;
    private Timer autoSaveTimer;
    private final int autoSaveInterval; // 毫秒

    public AutoSaveManager(TextEditor editor, UndoRedoManager undoRedoManager, int autoSaveInterval) {
        this.editor = editor;
        this.undoRedoManager = undoRedoManager;
        this.autoSaveInterval = autoSaveInterval;
    }

    public void startAutoSave() {
        if (autoSaveTimer != null) {
            autoSaveTimer.cancel();
        }

        autoSaveTimer = new Timer(true); // 守护线程
        autoSaveTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                if (editor.isModified()) {
                    EditorMemento autoSave = editor.createMemento();
                    undoRedoManager.saveState(autoSave);
                    System.out.println("💾 自动保存：" + new Date());
                }
            }
        }, autoSaveInterval, autoSaveInterval);

        System.out.println("自动保存已启用，间隔：" + autoSaveInterval + "ms");
    }

    public void stopAutoSave() {
        if (autoSaveTimer != null) {
            autoSaveTimer.cancel();
            autoSaveTimer = null;
            System.out.println("自动保存已停止");
        }
    }
}
```

## ✅ 优势分析

### 1. **封装性保护**
备忘录模式不破坏对象的封装性，外部无法直接访问对象的私有状态。

### 2. **状态恢复**
可以方便地恢复对象到之前的任何一个状态。

### 3. **简化发起者**
发起者不需要管理状态的历史，只负责创建和恢复备忘录。

### 4. **支持撤销操作**
为实现撤销功能提供了优雅的解决方案。

## ⚠️ 注意事项

### 1. **内存消耗**
```java
// 避免保存过多的备忘录导致内存溢出
class MemoryEfficientCaretaker {
    private List<Memento> mementos = new ArrayList<>();
    private final int maxSize;

    public MemoryEfficientCaretaker(int maxSize) {
        this.maxSize = maxSize;
    }

    public void addMemento(Memento memento) {
        if (mementos.size() >= maxSize) {
            mementos.remove(0); // 删除最老的备忘录
        }
        mementos.add(memento);
    }
}
```

### 2. **深拷贝成本**
如果对象状态复杂，创建备忘录的成本可能很高。

### 3. **管理者的责任**
管理者需要负责备忘录的生命周期管理。

## 🆚 与其他模式对比

| 特性 | 备忘录模式 | 原型模式 | 命令模式 |
|------|-----------|----------|----------|
| 目的 | 保存状态 | 克隆对象 | 封装操作 |
| 恢复能力 | 可恢复 | 可复制 | 可撤销 |
| 封装性 | 保护内部状态 | 克隆接口 | 封装请求 |
| 历史管理 | 支持 | 不支持 | 支持 |

## 🎯 实战建议

### 1. **何时使用备忘录模式**
- 需要保存对象的状态快照
- 想要实现撤销/重做功能
- 需要提供事务回滚能力
- 想要在不破坏封装的前提下访问对象状态

### 2. **设计原则**
```java
// 好的备忘录设计
public class GoodOriginator {
    private String state;

    // 内部类确保只有发起者能创建和访问备忘录
    public Memento createMemento() {
        return new MementoImpl(state);
    }

    public void restoreFromMemento(Memento memento) {
        if (memento instanceof MementoImpl) {
            this.state = ((MementoImpl) memento).getState();
        }
    }

    // 私有实现类，外部无法访问
    private static class MementoImpl implements Memento {
        private final String state;

        private MementoImpl(String state) {
            this.state = state;
        }

        private String getState() {
            return state;
        }
    }
}
```

### 3. **性能优化策略**
```java
// 使用写时复制优化
class CopyOnWriteMemento implements Memento {
    private Object state;
    private boolean copied = false;

    public CopyOnWriteMemento(Object state) {
        this.state = state;
    }

    public Object getState() {
        if (!copied) {
            // 只在需要时才进行深拷贝
            state = deepCopy(state);
            copied = true;
        }
        return state;
    }

    private Object deepCopy(Object obj) {
        // 实现深拷贝逻辑
        return obj; // 简化实现
    }
}
```

## 🧠 记忆技巧

**口诀：备忘录保存状态**
- **备**份重要信息
- **忘**记也能找回
- **录**下关键状态
- **保**护对象封装
- **存**储历史快照
- **状**态随时恢复
- **态**度保持谨慎

**形象比喻：**
备忘录模式就像**游戏存档**：
- 存档（备忘录）保存游戏状态
- 可以随时读档回到之前的状态
- 存档不会影响游戏本身的运行
- 玩家（管理者）负责管理存档

## 🎉 总结

备忘录模式是一种实用的设计模式，它为我们提供了优雅的状态保存和恢复机制。通过合理使用备忘录模式，我们可以实现撤销/重做、自动保存、状态回滚等强大功能，同时保持良好的封装性。

**核心思想：** 💾 在不破坏封装的前提下，捕获并保存对象状态，让时光倒流成为可能！

下一篇我们将学习**迭代器模式**，看看如何优雅地遍历集合中的元素！ 🚀