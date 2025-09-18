---
title: "设计模式入门教程17：模板方法模式 - 定义算法骨架的艺术"
date: 2024-12-17T10:17:00+08:00
draft: false
tags: ["设计模式", "模板方法模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是模板方法模式？

模板方法模式（Template Method Pattern）是一种行为型设计模式，它在抽象类中定义一个算法的骨架，允许子类在不改变算法结构的情况下，重新定义算法的某些特定步骤。

### 🌟 现实生活中的例子

想象一下制作饮料的流程：
- **基本步骤**：烧水 → 冲泡 → 倒入杯中 → 添加调料
- **咖啡**：烧水 → 冲泡咖啡 → 倒入杯中 → 加糖和牛奶
- **茶**：烧水 → 冲泡茶叶 → 倒入杯中 → 加柠檬

流程骨架相同，但具体步骤因饮料而异！

## 🏗️ 模式结构

```java
// 抽象模板类
abstract class AbstractClass {
    // 模板方法 - 定义算法骨架
    public final void templateMethod() {
        step1();
        step2();
        if (hook()) {
            step3();
        }
        step4();
    }

    // 具体方法 - 在抽象类中实现
    private void step1() {
        System.out.println("执行步骤1");
    }

    // 抽象方法 - 由子类实现
    protected abstract void step2();
    protected abstract void step4();

    // 可选步骤 - 子类可选择是否执行
    protected void step3() {
        System.out.println("执行可选步骤3");
    }

    // 钩子方法 - 子类可以覆盖以控制算法流程
    protected boolean hook() {
        return true;
    }
}
```

## 💡 核心组件详解

### 1. 抽象模板类（AbstractClass）
```java
// 饮料制作抽象类
abstract class BeverageMaker {
    // 模板方法 - 定义制作饮料的算法骨架
    public final void makeBeverage() {
        System.out.println("=== 开始制作饮料 ===");
        boilWater();
        brew();
        pourInCup();
        if (customerWantsCondiments()) {
            addCondiments();
        }
        System.out.println("=== 饮料制作完成 ===\n");
    }

    // 具体方法 - 所有饮料都需要烧水
    private void boilWater() {
        System.out.println("1. 烧开水");
    }

    // 具体方法 - 所有饮料都需要倒入杯中
    private void pourInCup() {
        System.out.println("3. 将饮料倒入杯中");
    }

    // 抽象方法 - 由子类实现具体的冲泡方式
    protected abstract void brew();

    // 抽象方法 - 由子类实现具体的调料添加
    protected abstract void addCondiments();

    // 钩子方法 - 子类可以控制是否添加调料
    protected boolean customerWantsCondiments() {
        return true;
    }
}
```

### 2. 具体实现类（ConcreteClass）
```java
// 咖啡制作类
class CoffeeMaker extends BeverageMaker {
    @Override
    protected void brew() {
        System.out.println("2. 用沸水冲泡咖啡");
    }

    @Override
    protected void addCondiments() {
        System.out.println("4. 加糖和牛奶");
    }

    @Override
    protected boolean customerWantsCondiments() {
        String answer = getUserInput();
        return answer.toLowerCase().startsWith("y");
    }

    private String getUserInput() {
        // 模拟用户输入
        System.out.print("要加糖和牛奶吗？(y/n)：");
        return "y"; // 模拟用户选择
    }
}

// 茶制作类
class TeaMaker extends BeverageMaker {
    @Override
    protected void brew() {
        System.out.println("2. 用沸水浸泡茶叶");
    }

    @Override
    protected void addCondiments() {
        System.out.println("4. 加柠檬片");
    }

    @Override
    protected boolean customerWantsCondiments() {
        // 茶默认加柠檬
        return true;
    }
}

// 热巧克力制作类
class HotChocolateMaker extends BeverageMaker {
    @Override
    protected void brew() {
        System.out.println("2. 用热水冲调巧克力粉");
    }

    @Override
    protected void addCondiments() {
        System.out.println("4. 加棉花糖和肉桂粉");
    }

    @Override
    protected boolean customerWantsCondiments() {
        // 热巧克力总是加装饰
        return true;
    }
}
```

## 🎮 实际应用示例

### 示例1：数据处理流水线
```java
// 数据处理抽象类
abstract class DataProcessor {
    // 模板方法 - 定义数据处理流程
    public final ProcessResult processData(String inputData) {
        System.out.println("=== 开始数据处理流程 ===");

        // 1. 验证数据
        if (!validateData(inputData)) {
            return new ProcessResult(false, "数据验证失败");
        }

        // 2. 解析数据
        Object parsedData = parseData(inputData);
        if (parsedData == null) {
            return new ProcessResult(false, "数据解析失败");
        }

        // 3. 处理数据
        Object processedData = doProcess(parsedData);

        // 4. 可选的后处理
        if (needPostProcess()) {
            processedData = postProcess(processedData);
        }

        // 5. 保存结果
        boolean saved = saveResult(processedData);

        // 6. 清理资源
        cleanup();

        System.out.println("=== 数据处理流程完成 ===");
        return new ProcessResult(saved, "处理完成");
    }

    // 具体方法 - 通用数据验证
    protected boolean validateData(String data) {
        if (data == null || data.trim().isEmpty()) {
            System.out.println("数据验证：数据为空");
            return false;
        }
        System.out.println("数据验证：通过基础验证");
        return true;
    }

    // 抽象方法 - 由子类实现具体的解析逻辑
    protected abstract Object parseData(String data);

    // 抽象方法 - 由子类实现具体的处理逻辑
    protected abstract Object doProcess(Object data);

    // 抽象方法 - 由子类实现具体的保存逻辑
    protected abstract boolean saveResult(Object result);

    // 钩子方法 - 是否需要后处理
    protected boolean needPostProcess() {
        return false;
    }

    // 默认后处理方法
    protected Object postProcess(Object data) {
        System.out.println("执行默认后处理");
        return data;
    }

    // 清理方法
    protected void cleanup() {
        System.out.println("清理临时资源");
    }
}

// JSON数据处理器
class JsonDataProcessor extends DataProcessor {
    @Override
    protected Object parseData(String data) {
        System.out.println("解析JSON数据：" + data);
        // 模拟JSON解析
        if (data.startsWith("{") && data.endsWith("}")) {
            return new JsonObject(data);
        }
        return null;
    }

    @Override
    protected Object doProcess(Object data) {
        JsonObject json = (JsonObject) data;
        System.out.println("处理JSON对象：验证字段、转换格式");
        json.validate();
        json.transform();
        return json;
    }

    @Override
    protected boolean saveResult(Object result) {
        System.out.println("保存JSON处理结果到数据库");
        return true;
    }

    @Override
    protected boolean needPostProcess() {
        return true; // JSON数据需要后处理
    }

    @Override
    protected Object postProcess(Object data) {
        System.out.println("JSON后处理：格式化和压缩");
        return data;
    }
}

// XML数据处理器
class XmlDataProcessor extends DataProcessor {
    @Override
    protected Object parseData(String data) {
        System.out.println("解析XML数据：" + data);
        // 模拟XML解析
        if (data.startsWith("<") && data.endsWith(">")) {
            return new XmlDocument(data);
        }
        return null;
    }

    @Override
    protected Object doProcess(Object data) {
        XmlDocument xml = (XmlDocument) data;
        System.out.println("处理XML文档：验证DTD、转换节点");
        xml.validateDTD();
        xml.transformNodes();
        return xml;
    }

    @Override
    protected boolean saveResult(Object result) {
        System.out.println("保存XML处理结果到文件系统");
        return true;
    }

    // XML不需要后处理，使用默认值false
}

// CSV数据处理器
class CsvDataProcessor extends DataProcessor {
    @Override
    protected boolean validateData(String data) {
        // 重写验证逻辑，增加CSV特定验证
        if (!super.validateData(data)) {
            return false;
        }

        if (!data.contains(",")) {
            System.out.println("CSV验证：不包含逗号分隔符");
            return false;
        }

        System.out.println("CSV验证：格式正确");
        return true;
    }

    @Override
    protected Object parseData(String data) {
        System.out.println("解析CSV数据：" + data);
        String[] lines = data.split("\n");
        return new CsvTable(lines);
    }

    @Override
    protected Object doProcess(Object data) {
        CsvTable csv = (CsvTable) data;
        System.out.println("处理CSV表格：去重、排序、统计");
        csv.removeDuplicates();
        csv.sort();
        csv.calculateStatistics();
        return csv;
    }

    @Override
    protected boolean saveResult(Object result) {
        System.out.println("保存CSV处理结果到Excel文件");
        return true;
    }
}

// 辅助类
class ProcessResult {
    private boolean success;
    private String message;

    public ProcessResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
}

class JsonObject {
    private String data;
    public JsonObject(String data) { this.data = data; }
    public void validate() { System.out.println("  - 验证JSON字段"); }
    public void transform() { System.out.println("  - 转换JSON格式"); }
}

class XmlDocument {
    private String data;
    public XmlDocument(String data) { this.data = data; }
    public void validateDTD() { System.out.println("  - 验证XML DTD"); }
    public void transformNodes() { System.out.println("  - 转换XML节点"); }
}

class CsvTable {
    private String[] lines;
    public CsvTable(String[] lines) { this.lines = lines; }
    public void removeDuplicates() { System.out.println("  - 去除重复行"); }
    public void sort() { System.out.println("  - 排序数据"); }
    public void calculateStatistics() { System.out.println("  - 计算统计信息"); }
}

// 使用示例
public class DataProcessingExample {
    public static void main(String[] args) {
        // 测试JSON处理
        System.out.println("### JSON数据处理 ###");
        DataProcessor jsonProcessor = new JsonDataProcessor();
        ProcessResult result1 = jsonProcessor.processData("{\"name\":\"张三\",\"age\":30}");
        System.out.println("结果：" + result1.getMessage());

        System.out.println("\n### XML数据处理 ###");
        DataProcessor xmlProcessor = new XmlDataProcessor();
        ProcessResult result2 = xmlProcessor.processData("<person><name>李四</name><age>25</age></person>");
        System.out.println("结果：" + result2.getMessage());

        System.out.println("\n### CSV数据处理 ###");
        DataProcessor csvProcessor = new CsvDataProcessor();
        ProcessResult result3 = csvProcessor.processData("姓名,年龄,城市\n王五,28,北京\n赵六,32,上海");
        System.out.println("结果：" + result3.getMessage());
    }
}
```

### 示例2：文档生成框架
```java
// 文档生成抽象类
abstract class DocumentGenerator {
    // 模板方法 - 定义文档生成流程
    public final void generateDocument(DocumentData data) {
        System.out.println("=== 开始生成文档 ===");

        // 1. 创建文档
        createDocument();

        // 2. 添加头部
        addHeader(data);

        // 3. 添加内容
        addContent(data);

        // 4. 可选的添加附录
        if (needAppendix(data)) {
            addAppendix(data);
        }

        // 5. 添加尾部
        addFooter(data);

        // 6. 应用样式
        applyStyles();

        // 7. 保存文档
        saveDocument(data.getFileName());

        System.out.println("=== 文档生成完成 ===\n");
    }

    // 抽象方法 - 创建文档
    protected abstract void createDocument();

    // 抽象方法 - 添加内容
    protected abstract void addContent(DocumentData data);

    // 抽象方法 - 保存文档
    protected abstract void saveDocument(String fileName);

    // 具体方法 - 通用头部
    protected void addHeader(DocumentData data) {
        System.out.println("添加文档头部：");
        System.out.println("  - 标题：" + data.getTitle());
        System.out.println("  - 作者：" + data.getAuthor());
        System.out.println("  - 日期：" + data.getDate());
    }

    // 具体方法 - 通用尾部
    protected void addFooter(DocumentData data) {
        System.out.println("添加文档尾部：");
        System.out.println("  - 版权信息");
        System.out.println("  - 页码");
    }

    // 钩子方法 - 是否需要附录
    protected boolean needAppendix(DocumentData data) {
        return data.hasAppendixData();
    }

    // 默认附录实现
    protected void addAppendix(DocumentData data) {
        System.out.println("添加附录：参考文献和索引");
    }

    // 抽象方法 - 应用样式
    protected abstract void applyStyles();
}

// PDF文档生成器
class PdfDocumentGenerator extends DocumentGenerator {
    @Override
    protected void createDocument() {
        System.out.println("创建PDF文档对象");
    }

    @Override
    protected void addContent(DocumentData data) {
        System.out.println("添加PDF内容：");
        System.out.println("  - 设置字体和段落");
        System.out.println("  - 插入图片和表格");
        for (String section : data.getSections()) {
            System.out.println("  - 章节：" + section);
        }
    }

    @Override
    protected void applyStyles() {
        System.out.println("应用PDF样式：");
        System.out.println("  - 设置页面布局");
        System.out.println("  - 应用字体样式");
        System.out.println("  - 调整行间距");
    }

    @Override
    protected void saveDocument(String fileName) {
        System.out.println("保存PDF文档：" + fileName + ".pdf");
    }

    @Override
    protected void addAppendix(DocumentData data) {
        System.out.println("添加PDF附录：");
        System.out.println("  - 创建书签");
        System.out.println("  - 添加超链接");
        super.addAppendix(data);
    }
}

// Word文档生成器
class WordDocumentGenerator extends DocumentGenerator {
    @Override
    protected void createDocument() {
        System.out.println("创建Word文档对象");
    }

    @Override
    protected void addContent(DocumentData data) {
        System.out.println("添加Word内容：");
        System.out.println("  - 创建段落和样式");
        System.out.println("  - 插入表格和图表");
        for (String section : data.getSections()) {
            System.out.println("  - 章节：" + section);
        }
    }

    @Override
    protected void applyStyles() {
        System.out.println("应用Word样式：");
        System.out.println("  - 使用模板样式");
        System.out.println("  - 设置页眉页脚");
        System.out.println("  - 应用主题颜色");
    }

    @Override
    protected void saveDocument(String fileName) {
        System.out.println("保存Word文档：" + fileName + ".docx");
    }
}

// HTML文档生成器
class HtmlDocumentGenerator extends DocumentGenerator {
    @Override
    protected void createDocument() {
        System.out.println("创建HTML文档结构");
    }

    @Override
    protected void addHeader(DocumentData data) {
        System.out.println("添加HTML头部：");
        System.out.println("  - <head>标签和元数据");
        System.out.println("  - <title>" + data.getTitle() + "</title>");
        System.out.println("  - CSS样式链接");
    }

    @Override
    protected void addContent(DocumentData data) {
        System.out.println("添加HTML内容：");
        System.out.println("  - 创建div和section");
        System.out.println("  - 添加导航菜单");
        for (String section : data.getSections()) {
            System.out.println("  - <section>" + section + "</section>");
        }
    }

    @Override
    protected void addFooter(DocumentData data) {
        System.out.println("添加HTML尾部：");
        System.out.println("  - <footer>标签");
        System.out.println("  - JavaScript脚本");
    }

    @Override
    protected void applyStyles() {
        System.out.println("应用HTML样式：");
        System.out.println("  - 嵌入CSS样式");
        System.out.println("  - 响应式设计");
        System.out.println("  - 交互效果");
    }

    @Override
    protected void saveDocument(String fileName) {
        System.out.println("保存HTML文档：" + fileName + ".html");
    }

    @Override
    protected boolean needAppendix(DocumentData data) {
        // HTML文档通常不需要传统意义上的附录
        return false;
    }
}

// 文档数据类
class DocumentData {
    private String title;
    private String author;
    private String date;
    private String fileName;
    private List<String> sections;
    private boolean hasAppendixData;

    public DocumentData(String title, String author, String fileName) {
        this.title = title;
        this.author = author;
        this.fileName = fileName;
        this.date = LocalDate.now().toString();
        this.sections = new ArrayList<>();
        this.hasAppendixData = false;
    }

    public void addSection(String section) {
        sections.add(section);
    }

    public void setHasAppendixData(boolean hasAppendixData) {
        this.hasAppendixData = hasAppendixData;
    }

    // Getters
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getDate() { return date; }
    public String getFileName() { return fileName; }
    public List<String> getSections() { return sections; }
    public boolean hasAppendixData() { return hasAppendixData; }
}

// 使用示例
public class DocumentGenerationExample {
    public static void main(String[] args) {
        // 准备文档数据
        DocumentData reportData = new DocumentData(
            "2024年度业务报告", "张三", "annual_report_2024"
        );
        reportData.addSection("执行摘要");
        reportData.addSection("业务概述");
        reportData.addSection("财务分析");
        reportData.addSection("市场展望");
        reportData.setHasAppendixData(true);

        // 生成PDF报告
        System.out.println("### 生成PDF报告 ###");
        DocumentGenerator pdfGenerator = new PdfDocumentGenerator();
        pdfGenerator.generateDocument(reportData);

        // 生成Word文档
        System.out.println("### 生成Word文档 ###");
        DocumentGenerator wordGenerator = new WordDocumentGenerator();
        wordGenerator.generateDocument(reportData);

        // 生成HTML网页
        System.out.println("### 生成HTML网页 ###");
        DocumentGenerator htmlGenerator = new HtmlDocumentGenerator();
        htmlGenerator.generateDocument(reportData);
    }
}
```

### 示例3：游戏关卡加载系统
```java
// 游戏关卡抽象类
abstract class GameLevel {
    // 模板方法 - 定义关卡加载流程
    public final void loadLevel() {
        System.out.println("=== 开始加载关卡 ===");

        showLoadingScreen();

        // 预加载检查
        if (!preloadCheck()) {
            System.out.println("预加载检查失败，停止加载");
            return;
        }

        loadAssets();
        initializeEnvironment();
        spawnPlayer();

        if (hasEnemies()) {
            spawnEnemies();
        }

        if (hasNPCs()) {
            spawnNPCs();
        }

        setupGameplay();

        if (hasIntroduction()) {
            playIntroduction();
        }

        hideLoadingScreen();
        startGameplay();

        System.out.println("=== 关卡加载完成 ===\n");
    }

    // 具体方法 - 显示加载画面
    protected void showLoadingScreen() {
        System.out.println("显示加载画面...");
    }

    // 具体方法 - 隐藏加载画面
    protected void hideLoadingScreen() {
        System.out.println("隐藏加载画面");
    }

    // 具体方法 - 开始游戏
    protected void startGameplay() {
        System.out.println("游戏开始！");
    }

    // 抽象方法 - 子类必须实现
    protected abstract void loadAssets();
    protected abstract void initializeEnvironment();
    protected abstract void spawnPlayer();
    protected abstract void setupGameplay();

    // 钩子方法 - 子类可以覆盖
    protected boolean preloadCheck() {
        System.out.println("执行基础预加载检查");
        return true;
    }

    protected boolean hasEnemies() {
        return true;
    }

    protected boolean hasNPCs() {
        return false;
    }

    protected boolean hasIntroduction() {
        return false;
    }

    // 默认实现 - 子类可以覆盖
    protected void spawnEnemies() {
        System.out.println("生成敌人");
    }

    protected void spawnNPCs() {
        System.out.println("生成NPC");
    }

    protected void playIntroduction() {
        System.out.println("播放关卡介绍");
    }
}

// 第一关 - 新手教程
class TutorialLevel extends GameLevel {
    @Override
    protected void loadAssets() {
        System.out.println("加载教程资源：");
        System.out.println("  - 基础UI元素");
        System.out.println("  - 教程音效");
        System.out.println("  - 简单3D模型");
    }

    @Override
    protected void initializeEnvironment() {
        System.out.println("初始化教程环境：");
        System.out.println("  - 创建安全的练习区域");
        System.out.println("  - 设置柔和的光照");
    }

    @Override
    protected void spawnPlayer() {
        System.out.println("生成玩家：新手角色，基础属性");
    }

    @Override
    protected void setupGameplay() {
        System.out.println("设置教程玩法：");
        System.out.println("  - 开启提示系统");
        System.out.println("  - 限制某些功能");
        System.out.println("  - 设置引导路径");
    }

    @Override
    protected boolean hasEnemies() {
        return false; // 教程关卡没有敌人
    }

    @Override
    protected boolean hasNPCs() {
        return true; // 有教学NPC
    }

    @Override
    protected boolean hasIntroduction() {
        return true; // 需要播放教程介绍
    }

    @Override
    protected void spawnNPCs() {
        System.out.println("生成教学NPC：向导老师");
    }

    @Override
    protected void playIntroduction() {
        System.out.println("播放新手教程介绍动画");
    }
}

// 第二关 - 森林探险
class ForestLevel extends GameLevel {
    @Override
    protected boolean preloadCheck() {
        System.out.println("森林关卡预检查：");
        System.out.println("  - 检查显卡性能");
        System.out.println("  - 验证声音系统");
        // 模拟检查结果
        return true;
    }

    @Override
    protected void loadAssets() {
        System.out.println("加载森林资源：");
        System.out.println("  - 树木和植被模型");
        System.out.println("  - 动物音效");
        System.out.println("  - 环境贴图");
        System.out.println("  - 粒子效果");
    }

    @Override
    protected void initializeEnvironment() {
        System.out.println("初始化森林环境：");
        System.out.println("  - 生成随机地形");
        System.out.println("  - 设置动态天气");
        System.out.println("  - 创建植被系统");
    }

    @Override
    protected void spawnPlayer() {
        System.out.println("生成玩家：探险者装备，提升后的属性");
    }

    @Override
    protected void setupGameplay() {
        System.out.println("设置森林玩法：");
        System.out.println("  - 启用收集系统");
        System.out.println("  - 设置隐藏宝箱");
        System.out.println("  - 开启动态事件");
    }

    @Override
    protected void spawnEnemies() {
        System.out.println("生成森林敌人：");
        System.out.println("  - 野生动物");
        System.out.println("  - 森林守卫");
        System.out.println("  - 魔法生物");
    }

    @Override
    protected boolean hasNPCs() {
        return true;
    }

    @Override
    protected void spawnNPCs() {
        System.out.println("生成森林NPC：");
        System.out.println("  - 隐士老人");
        System.out.println("  - 商人");
    }
}

// Boss关 - 最终决战
class BossLevel extends GameLevel {
    @Override
    protected boolean preloadCheck() {
        System.out.println("Boss关卡预检查：");
        System.out.println("  - 检查内存使用");
        System.out.println("  - 验证网络连接");
        System.out.println("  - 确认存档完整性");
        return true;
    }

    @Override
    protected void loadAssets() {
        System.out.println("加载Boss关资源：");
        System.out.println("  - 高精度Boss模型");
        System.out.println("  - 史诗级音乐");
        System.out.println("  - 特效动画");
        System.out.println("  - 竞技场环境");
    }

    @Override
    protected void initializeEnvironment() {
        System.out.println("初始化Boss竞技场：");
        System.out.println("  - 创建圆形竞技场");
        System.out.println("  - 设置戏剧性光照");
        System.out.println("  - 启用物理破坏");
    }

    @Override
    protected void spawnPlayer() {
        System.out.println("生成玩家：满级装备，所有技能解锁");
    }

    @Override
    protected void setupGameplay() {
        System.out.println("设置Boss战玩法：");
        System.out.println("  - 启用Boss血条");
        System.out.println("  - 设置阶段转换");
        System.out.println("  - 开启特殊机制");
    }

    @Override
    protected boolean hasEnemies() {
        return true; // 有Boss和小怪
    }

    @Override
    protected boolean hasNPCs() {
        return false; // Boss战没有NPC
    }

    @Override
    protected boolean hasIntroduction() {
        return true; // 需要播放Boss介绍
    }

    @Override
    protected void spawnEnemies() {
        System.out.println("生成Boss战敌人：");
        System.out.println("  - 最终Boss：暗影龙王");
        System.out.println("  - 召唤的小龙");
    }

    @Override
    protected void playIntroduction() {
        System.out.println("播放Boss登场动画：暗影龙王觉醒");
    }
}

// 使用示例
public class GameLevelExample {
    public static void main(String[] args) {
        List<GameLevel> levels = Arrays.asList(
            new TutorialLevel(),
            new ForestLevel(),
            new BossLevel()
        );

        for (int i = 0; i < levels.size(); i++) {
            System.out.println("### 第" + (i + 1) + "关 ###");
            levels.get(i).loadLevel();
        }
    }
}
```

## ⚡ 高级应用

### Hook方法的巧妙使用
```java
// 带有多个Hook的抽象类
abstract class DataMigrationTemplate {
    public final void migrateData() {
        if (needBackup()) {
            createBackup();
        }

        validateSource();

        if (needTransformation()) {
            transformData();
        }

        migrateCore();

        if (needVerification()) {
            verifyMigration();
        }

        if (needCleanup()) {
            cleanup();
        }

        notifyCompletion();
    }

    // 抽象方法
    protected abstract void validateSource();
    protected abstract void migrateCore();

    // Hook方法
    protected boolean needBackup() { return true; }
    protected boolean needTransformation() { return false; }
    protected boolean needVerification() { return true; }
    protected boolean needCleanup() { return false; }

    // 默认实现
    protected void createBackup() {
        System.out.println("创建数据备份");
    }

    protected void transformData() {
        System.out.println("转换数据格式");
    }

    protected void verifyMigration() {
        System.out.println("验证迁移结果");
    }

    protected void cleanup() {
        System.out.println("清理临时文件");
    }

    protected void notifyCompletion() {
        System.out.println("发送完成通知");
    }
}
```

### 与策略模式结合
```java
abstract class ConfigurableProcessor {
    protected ProcessingStrategy strategy;

    public final void process(Data data) {
        preProcess(data);

        if (strategy != null) {
            strategy.process(data);
        } else {
            defaultProcess(data);
        }

        postProcess(data);
    }

    protected abstract void preProcess(Data data);
    protected abstract void postProcess(Data data);
    protected abstract void defaultProcess(Data data);

    public void setStrategy(ProcessingStrategy strategy) {
        this.strategy = strategy;
    }
}
```

## ✅ 优势分析

### 1. **代码复用**
在抽象类中实现算法的公共部分，避免重复代码。

### 2. **控制算法结构**
父类控制算法的执行顺序，子类只需关注具体实现。

### 3. **易于扩展**
新增算法变体只需继承抽象类并实现抽象方法。

### 4. **符合开闭原则**
对扩展开放，对修改关闭。

## ⚠️ 注意事项

### 1. **不要过度设计**
```java
// 避免为简单逻辑创建模板方法
// 错误示例：
abstract class SimpleCalculator {
    public final int calculate(int a, int b) {
        return doCalculate(a, b); // 只有一步，不需要模板方法
    }
    protected abstract int doCalculate(int a, int b);
}
```

### 2. **慎用final关键字**
模板方法通常声明为final，防止子类覆盖算法结构。

### 3. **Hook方法的命名**
Hook方法应该有清晰的命名，表明其作用。

## 🆚 与其他模式对比

| 特性 | 模板方法模式 | 策略模式 | 工厂方法模式 |
|------|-------------|----------|-------------|
| 目的 | 定义算法骨架 | 封装算法族 | 创建对象 |
| 结构 | 继承关系 | 组合关系 | 继承关系 |
| 灵活性 | 结构固定 | 算法可替换 | 产品可扩展 |
| 复用性 | 代码复用好 | 算法复用好 | 创建逻辑复用 |

## 🎯 实战建议

### 1. **何时使用模板方法**
- 多个类有相似的算法结构
- 想要控制算法的执行顺序
- 希望子类只实现算法的特定部分
- 需要避免代码重复

### 2. **设计原则**
```java
// 好的模板方法设计
public abstract class GoodTemplate {
    // 1. 使用final防止子类破坏算法结构
    public final void templateMethod() { /* ... */ }

    // 2. 抽象方法明确子类责任
    protected abstract void requiredStep();

    // 3. Hook方法提供扩展点
    protected boolean needOptionalStep() { return false; }

    // 4. 具体方法实现公共逻辑
    protected void commonStep() { /* ... */ }
}
```

### 3. **与框架结合**
```java
// Spring框架中的应用
@Component
public abstract class BaseService {
    public final void processRequest(Request request) {
        validate(request);
        Object result = doProcess(request);
        postProcess(result);
    }

    protected void validate(Request request) {
        // 通用验证逻辑
    }

    protected abstract Object doProcess(Request request);

    protected void postProcess(Object result) {
        // 通用后处理逻辑
    }
}
```

## 🧠 记忆技巧

**口诀：模板骨架定方向**
- **模**式定义算法架构
- **板**上钉钉不可变
- **骨**干流程父类管
- **架**构稳定子类填
- **定**制实现各不同
- **方**法抽象待重写
- **向**导明确步骤清

**形象比喻：**
模板方法模式就像**做菜的基本流程**：
- 备料 → 处理 → 烹饪 → 装盘（固定流程）
- 不同菜品在"处理"和"烹饪"步骤有不同做法
- 但整体流程保持一致

## 🎉 总结

模板方法模式是一种强大的行为型设计模式，它让我们能够定义算法的骨架，同时允许子类自定义算法的特定步骤。通过合理使用抽象方法、具体方法和Hook方法，我们可以实现既灵活又稳定的算法结构。

**核心思想：** 🏗️ 定义算法骨架，让子类填充具体实现，实现代码复用与扩展的完美平衡！

下一篇我们将学习**状态模式**，看看如何优雅地管理对象的状态转换！ 🚀