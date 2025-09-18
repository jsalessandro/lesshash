---
title: "设计模式详解：建造者模式(Builder) - 复杂对象的分步构建艺术"
date: 2024-12-04T10:04:00+08:00
draft: false
tags: ["设计模式", "建造者模式", "Builder", "Java", "创建型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解建造者模式，通过房屋建造和电脑配置的生动例子，让你轻松掌握复杂对象构建的最佳实践"
---

## 🎯 什么是建造者模式？

### 生活中的例子
想象你要建造一栋房子：

**传统方式**：一次性给包工头所有要求
- 客厅要多大？卧室几个？厨房什么样？阳台要吗？...
- 要求太多，容易遗漏，包工头也容易搞混

**建造者方式**：分步骤逐一建造
1. 🏗️ 先打地基（必需）
2. 🧱 建墙体（必需）
3. 🏠 加屋顶（必需）
4. 🚪 安门窗（可选）
5. 🎨 装修（可选）
6. 🌸 园林绿化（可选）

这就是建造者模式：**将复杂对象的构建过程分解为多个简单的步骤，使得同样的构建过程可以创建不同的表示**。

## 🧠 设计思想

### 核心概念
- **Builder（抽象建造者）**：定义构建步骤的接口
- **ConcreteBuilder（具体建造者）**：实现具体的构建步骤
- **Director（指挥者）**：控制构建过程
- **Product（产品）**：被构建的复杂对象

### 解决的问题
1. **构造函数参数过多**：避免telescoping constructor反模式
2. **可选参数处理**：优雅处理大量可选参数
3. **对象创建复杂**：分步骤创建复杂对象
4. **创建过程复用**：同样的过程创建不同的对象

### 记忆口诀
> **"分步建造复杂物，指挥建造有条理，建造过程可复用，最终产品各不同"**

## 💻 代码实现

### 经典实现：房屋建造

```java
// === 产品类：房屋 ===

class House {
    // 必需属性
    private String foundation;    // 地基
    private String structure;     // 结构
    private String roof;         // 屋顶

    // 可选属性
    private boolean hasGarage;   // 车库
    private boolean hasPool;     // 游泳池
    private boolean hasGarden;   // 花园
    private String interiorDesign; // 室内设计
    private String paintColor;   // 墙漆颜色

    // 私有构造函数，只能通过建造者创建
    private House(HouseBuilder builder) {
        this.foundation = builder.foundation;
        this.structure = builder.structure;
        this.roof = builder.roof;
        this.hasGarage = builder.hasGarage;
        this.hasPool = builder.hasPool;
        this.hasGarden = builder.hasGarden;
        this.interiorDesign = builder.interiorDesign;
        this.paintColor = builder.paintColor;
    }

    // 显示房屋信息
    public void showHouseInfo() {
        System.out.println("=== 房屋建造完成 ===");
        System.out.println("地基：" + foundation);
        System.out.println("结构：" + structure);
        System.out.println("屋顶：" + roof);
        System.out.println("车库：" + (hasGarage ? "有" : "无"));
        System.out.println("游泳池：" + (hasPool ? "有" : "无"));
        System.out.println("花园：" + (hasGarden ? "有" : "无"));
        System.out.println("室内设计：" + (interiorDesign != null ? interiorDesign : "标准设计"));
        System.out.println("墙漆颜色：" + (paintColor != null ? paintColor : "白色"));
    }

    // 建造者类（静态内部类）
    public static class HouseBuilder {
        // 必需属性
        private String foundation;
        private String structure;
        private String roof;

        // 可选属性（有默认值）
        private boolean hasGarage = false;
        private boolean hasPool = false;
        private boolean hasGarden = false;
        private String interiorDesign;
        private String paintColor;

        // 构造函数只接收必需参数
        public HouseBuilder(String foundation, String structure, String roof) {
            this.foundation = foundation;
            this.structure = structure;
            this.roof = roof;
        }

        // 可选属性的设置方法（返回自身，支持链式调用）
        public HouseBuilder hasGarage(boolean hasGarage) {
            this.hasGarage = hasGarage;
            return this;
        }

        public HouseBuilder hasPool(boolean hasPool) {
            this.hasPool = hasPool;
            return this;
        }

        public HouseBuilder hasGarden(boolean hasGarden) {
            this.hasGarden = hasGarden;
            return this;
        }

        public HouseBuilder withInteriorDesign(String interiorDesign) {
            this.interiorDesign = interiorDesign;
            return this;
        }

        public HouseBuilder withPaintColor(String paintColor) {
            this.paintColor = paintColor;
            return this;
        }

        // 构建最终产品
        public House build() {
            return new House(this);
        }
    }
}
```

### 传统建造者模式：电脑配置

```java
// === 产品类：电脑 ===

class Computer {
    private String cpu;
    private String memory;
    private String storage;
    private String motherboard;
    private String graphicsCard;
    private String powerSupply;
    private String computerCase;
    private String cooling;

    public Computer() {}

    // Getter和Setter方法
    public String getCpu() { return cpu; }
    public void setCpu(String cpu) { this.cpu = cpu; }

    public String getMemory() { return memory; }
    public void setMemory(String memory) { this.memory = memory; }

    public String getStorage() { return storage; }
    public void setStorage(String storage) { this.storage = storage; }

    public String getMotherboard() { return motherboard; }
    public void setMotherboard(String motherboard) { this.motherboard = motherboard; }

    public String getGraphicsCard() { return graphicsCard; }
    public void setGraphicsCard(String graphicsCard) { this.graphicsCard = graphicsCard; }

    public String getPowerSupply() { return powerSupply; }
    public void setPowerSupply(String powerSupply) { this.powerSupply = powerSupply; }

    public String getComputerCase() { return computerCase; }
    public void setComputerCase(String computerCase) { this.computerCase = computerCase; }

    public String getCooling() { return cooling; }
    public void setCooling(String cooling) { this.cooling = cooling; }

    public void showSpecs() {
        System.out.println("=== 电脑配置信息 ===");
        System.out.println("CPU: " + cpu);
        System.out.println("内存: " + memory);
        System.out.println("存储: " + storage);
        System.out.println("主板: " + motherboard);
        System.out.println("显卡: " + graphicsCard);
        System.out.println("电源: " + powerSupply);
        System.out.println("机箱: " + computerCase);
        System.out.println("散热: " + cooling);
    }
}

// === 抽象建造者 ===

abstract class ComputerBuilder {
    protected Computer computer;

    public ComputerBuilder() {
        this.computer = new Computer();
    }

    public abstract ComputerBuilder buildCPU();
    public abstract ComputerBuilder buildMemory();
    public abstract ComputerBuilder buildStorage();
    public abstract ComputerBuilder buildMotherboard();
    public abstract ComputerBuilder buildGraphicsCard();
    public abstract ComputerBuilder buildPowerSupply();
    public abstract ComputerBuilder buildCase();
    public abstract ComputerBuilder buildCooling();

    public Computer getResult() {
        return computer;
    }
}

// === 具体建造者：游戏电脑 ===

class GamingComputerBuilder extends ComputerBuilder {

    @Override
    public ComputerBuilder buildCPU() {
        computer.setCpu("Intel i9-13900K (24核32线程, 3.0-5.8GHz)");
        return this;
    }

    @Override
    public ComputerBuilder buildMemory() {
        computer.setMemory("DDR5-6000 32GB (2x16GB) RGB内存");
        return this;
    }

    @Override
    public ComputerBuilder buildStorage() {
        computer.setStorage("1TB NVMe SSD (PCIe 4.0) + 2TB HDD");
        return this;
    }

    @Override
    public ComputerBuilder buildMotherboard() {
        computer.setMotherboard("ASUS ROG STRIX Z790-E GAMING WIFI");
        return this;
    }

    @Override
    public ComputerBuilder buildGraphicsCard() {
        computer.setGraphicsCard("NVIDIA RTX 4090 24GB GDDR6X");
        return this;
    }

    @Override
    public ComputerBuilder buildPowerSupply() {
        computer.setPowerSupply("1000W 80PLUS金牌全模组电源");
        return this;
    }

    @Override
    public ComputerBuilder buildCase() {
        computer.setComputerCase("全塔式钢化玻璃RGB机箱");
        return this;
    }

    @Override
    public ComputerBuilder buildCooling() {
        computer.setCooling("360mm一体式水冷散热器");
        return this;
    }
}

// === 具体建造者：办公电脑 ===

class OfficeComputerBuilder extends ComputerBuilder {

    @Override
    public ComputerBuilder buildCPU() {
        computer.setCpu("Intel i5-13400 (10核16线程, 2.5-4.6GHz)");
        return this;
    }

    @Override
    public ComputerBuilder buildMemory() {
        computer.setMemory("DDR4-3200 16GB (2x8GB)");
        return this;
    }

    @Override
    public ComputerBuilder buildStorage() {
        computer.setStorage("512GB NVMe SSD");
        return this;
    }

    @Override
    public ComputerBuilder buildMotherboard() {
        computer.setMotherboard("华硕 PRIME B760M-A WIFI");
        return this;
    }

    @Override
    public ComputerBuilder buildGraphicsCard() {
        computer.setGraphicsCard("集成显卡 Intel UHD Graphics 770");
        return this;
    }

    @Override
    public ComputerBuilder buildPowerSupply() {
        computer.setPowerSupply("550W 80PLUS铜牌电源");
        return this;
    }

    @Override
    public ComputerBuilder buildCase() {
        computer.setComputerCase("标准ATX黑色机箱");
        return this;
    }

    @Override
    public ComputerBuilder buildCooling() {
        computer.setCooling("CPU自带散热器");
        return this;
    }
}

// === 具体建造者：服务器 ===

class ServerComputerBuilder extends ComputerBuilder {

    @Override
    public ComputerBuilder buildCPU() {
        computer.setCpu("Intel Xeon Silver 4314 (16核32线程, 2.4-3.4GHz)");
        return this;
    }

    @Override
    public ComputerBuilder buildMemory() {
        computer.setMemory("DDR4-3200 64GB (4x16GB) ECC内存");
        return this;
    }

    @Override
    public ComputerBuilder buildStorage() {
        computer.setStorage("2TB NVMe SSD + 8TB RAID10 企业级硬盘");
        return this;
    }

    @Override
    public ComputerBuilder buildMotherboard() {
        computer.setMotherboard("超微 X12SPL-F 服务器主板");
        return this;
    }

    @Override
    public ComputerBuilder buildGraphicsCard() {
        computer.setGraphicsCard("无独立显卡（远程管理）");
        return this;
    }

    @Override
    public ComputerBuilder buildPowerSupply() {
        computer.setPowerSupply("800W 80PLUS白金冗余电源");
        return this;
    }

    @Override
    public ComputerBuilder buildCase() {
        computer.setComputerCase("2U机架式服务器机箱");
        return this;
    }

    @Override
    public ComputerBuilder buildCooling() {
        computer.setCooling("工业级风扇散热系统");
        return this;
    }
}

// === 指挥者 ===

class ComputerDirector {
    private ComputerBuilder builder;

    public ComputerDirector(ComputerBuilder builder) {
        this.builder = builder;
    }

    public void setBuilder(ComputerBuilder builder) {
        this.builder = builder;
    }

    // 构建完整的电脑
    public Computer constructComputer() {
        System.out.println("开始组装电脑...");

        return builder
                .buildMotherboard()
                .buildCPU()
                .buildMemory()
                .buildStorage()
                .buildGraphicsCard()
                .buildPowerSupply()
                .buildCase()
                .buildCooling()
                .getResult();
    }

    // 构建基础版本（只包含核心组件）
    public Computer constructBasicComputer() {
        System.out.println("开始组装基础版电脑...");

        return builder
                .buildMotherboard()
                .buildCPU()
                .buildMemory()
                .buildStorage()
                .getResult();
    }
}
```

### 使用示例

```java
public class BuilderPatternDemo {
    public static void main(String[] args) {
        System.out.println("=== 建造者模式演示 ===\n");

        // 1. 使用内部建造者模式创建房屋
        demonstrateHouseBuilder();

        System.out.println("\n" + "=".repeat(60) + "\n");

        // 2. 使用传统建造者模式创建电脑
        demonstrateComputerBuilder();
    }

    private static void demonstrateHouseBuilder() {
        System.out.println(">>> 使用内部建造者创建房屋 <<<");

        // 创建简单房屋
        House simpleHouse = new House.HouseBuilder(
                "钢筋混凝土地基",
                "砖混结构",
                "平屋顶"
        ).build();

        simpleHouse.showHouseInfo();

        System.out.println();

        // 创建豪华房屋
        House luxuryHouse = new House.HouseBuilder(
                "钢筋混凝土桩基",
                "框架结构",
                "坡屋顶"
        )
                .hasGarage(true)
                .hasPool(true)
                .hasGarden(true)
                .withInteriorDesign("欧式豪华装修")
                .withPaintColor("米白色")
                .build();

        luxuryHouse.showHouseInfo();

        System.out.println();

        // 创建现代房屋
        House modernHouse = new House.HouseBuilder(
                "预制混凝土地基",
                "钢结构",
                "现代平屋顶"
        )
                .hasGarage(true)
                .hasGarden(true)
                .withInteriorDesign("现代简约风格")
                .withPaintColor("极简灰色")
                .build();

        modernHouse.showHouseInfo();
    }

    private static void demonstrateComputerBuilder() {
        System.out.println(">>> 使用传统建造者创建电脑 <<<");

        // 创建游戏电脑
        ComputerBuilder gamingBuilder = new GamingComputerBuilder();
        ComputerDirector director = new ComputerDirector(gamingBuilder);

        System.out.println("--- 游戏电脑 ---");
        Computer gamingPC = director.constructComputer();
        gamingPC.showSpecs();

        System.out.println();

        // 创建办公电脑
        ComputerBuilder officeBuilder = new OfficeComputerBuilder();
        director.setBuilder(officeBuilder);

        System.out.println("--- 办公电脑 ---");
        Computer officePC = director.constructComputer();
        officePC.showSpecs();

        System.out.println();

        // 创建服务器（只构建基础版本）
        ComputerBuilder serverBuilder = new ServerComputerBuilder();
        director.setBuilder(serverBuilder);

        System.out.println("--- 服务器（基础版）---");
        Computer server = director.constructBasicComputer();
        server.showSpecs();
    }
}
```

## 🌟 实际应用场景

### 1. SQL查询建造者

```java
// SQL 查询建造者
class SQLQueryBuilder {
    private StringBuilder query;
    private String tableName;
    private List<String> selectFields;
    private List<String> whereConditions;
    private List<String> joinClauses;
    private String orderBy;
    private String groupBy;
    private Integer limit;

    public SQLQueryBuilder() {
        this.query = new StringBuilder();
        this.selectFields = new ArrayList<>();
        this.whereConditions = new ArrayList<>();
        this.joinClauses = new ArrayList<>();
    }

    public SQLQueryBuilder select(String... fields) {
        Collections.addAll(selectFields, fields);
        return this;
    }

    public SQLQueryBuilder from(String table) {
        this.tableName = table;
        return this;
    }

    public SQLQueryBuilder where(String condition) {
        whereConditions.add(condition);
        return this;
    }

    public SQLQueryBuilder and(String condition) {
        if (!whereConditions.isEmpty()) {
            whereConditions.add("AND " + condition);
        } else {
            whereConditions.add(condition);
        }
        return this;
    }

    public SQLQueryBuilder or(String condition) {
        if (!whereConditions.isEmpty()) {
            whereConditions.add("OR " + condition);
        } else {
            whereConditions.add(condition);
        }
        return this;
    }

    public SQLQueryBuilder join(String table, String condition) {
        joinClauses.add("INNER JOIN " + table + " ON " + condition);
        return this;
    }

    public SQLQueryBuilder leftJoin(String table, String condition) {
        joinClauses.add("LEFT JOIN " + table + " ON " + condition);
        return this;
    }

    public SQLQueryBuilder rightJoin(String table, String condition) {
        joinClauses.add("RIGHT JOIN " + table + " ON " + condition);
        return this;
    }

    public SQLQueryBuilder orderBy(String field, String direction) {
        this.orderBy = field + " " + direction;
        return this;
    }

    public SQLQueryBuilder orderBy(String field) {
        return orderBy(field, "ASC");
    }

    public SQLQueryBuilder groupBy(String field) {
        this.groupBy = field;
        return this;
    }

    public SQLQueryBuilder limit(int count) {
        this.limit = count;
        return this;
    }

    public String build() {
        if (tableName == null) {
            throw new IllegalStateException("Table name is required");
        }

        StringBuilder sql = new StringBuilder();

        // SELECT 子句
        if (selectFields.isEmpty()) {
            sql.append("SELECT * ");
        } else {
            sql.append("SELECT ").append(String.join(", ", selectFields)).append(" ");
        }

        // FROM 子句
        sql.append("FROM ").append(tableName).append(" ");

        // JOIN 子句
        for (String joinClause : joinClauses) {
            sql.append(joinClause).append(" ");
        }

        // WHERE 子句
        if (!whereConditions.isEmpty()) {
            sql.append("WHERE ");
            for (int i = 0; i < whereConditions.size(); i++) {
                if (i > 0 && !whereConditions.get(i).startsWith("AND") &&
                    !whereConditions.get(i).startsWith("OR")) {
                    sql.append("AND ");
                }
                sql.append(whereConditions.get(i)).append(" ");
            }
        }

        // GROUP BY 子句
        if (groupBy != null) {
            sql.append("GROUP BY ").append(groupBy).append(" ");
        }

        // ORDER BY 子句
        if (orderBy != null) {
            sql.append("ORDER BY ").append(orderBy).append(" ");
        }

        // LIMIT 子句
        if (limit != null) {
            sql.append("LIMIT ").append(limit).append(" ");
        }

        return sql.toString().trim();
    }

    @Override
    public String toString() {
        return build();
    }
}

// 使用示例
public class SQLBuilderDemo {
    public static void main(String[] args) {
        System.out.println("=== SQL 查询建造者演示 ===\n");

        // 简单查询
        String query1 = new SQLQueryBuilder()
                .select("id", "name", "email")
                .from("users")
                .where("age > 18")
                .and("status = 'active'")
                .orderBy("name")
                .limit(10)
                .build();

        System.out.println("简单查询：");
        System.out.println(query1);

        System.out.println();

        // 复杂连接查询
        String query2 = new SQLQueryBuilder()
                .select("u.name", "u.email", "p.title", "c.name as category")
                .from("users u")
                .leftJoin("posts p", "p.user_id = u.id")
                .leftJoin("categories c", "c.id = p.category_id")
                .where("u.created_at > '2023-01-01'")
                .and("p.status = 'published'")
                .or("p.featured = true")
                .orderBy("u.name")
                .groupBy("u.id")
                .limit(20)
                .build();

        System.out.println("复杂连接查询：");
        System.out.println(query2);

        System.out.println();

        // 聚合查询
        String query3 = new SQLQueryBuilder()
                .select("category", "COUNT(*) as post_count", "AVG(views) as avg_views")
                .from("posts")
                .where("status = 'published'")
                .groupBy("category")
                .orderBy("post_count", "DESC")
                .build();

        System.out.println("聚合查询：");
        System.out.println(query3);
    }
}
```

### 2. HTTP请求建造者

```java
// HTTP 请求建造者
class HttpRequestBuilder {
    private String url;
    private String method = "GET";
    private Map<String, String> headers = new HashMap<>();
    private Map<String, String> queryParams = new HashMap<>();
    private String body;
    private int timeout = 30000; // 默认30秒超时

    public HttpRequestBuilder url(String url) {
        this.url = url;
        return this;
    }

    public HttpRequestBuilder get() {
        this.method = "GET";
        return this;
    }

    public HttpRequestBuilder post() {
        this.method = "POST";
        return this;
    }

    public HttpRequestBuilder put() {
        this.method = "PUT";
        return this;
    }

    public HttpRequestBuilder delete() {
        this.method = "DELETE";
        return this;
    }

    public HttpRequestBuilder header(String name, String value) {
        headers.put(name, value);
        return this;
    }

    public HttpRequestBuilder headers(Map<String, String> headers) {
        this.headers.putAll(headers);
        return this;
    }

    public HttpRequestBuilder contentType(String contentType) {
        return header("Content-Type", contentType);
    }

    public HttpRequestBuilder authorization(String token) {
        return header("Authorization", "Bearer " + token);
    }

    public HttpRequestBuilder param(String name, String value) {
        queryParams.put(name, value);
        return this;
    }

    public HttpRequestBuilder params(Map<String, String> params) {
        queryParams.putAll(params);
        return this;
    }

    public HttpRequestBuilder body(String body) {
        this.body = body;
        return this;
    }

    public HttpRequestBuilder jsonBody(Object obj) {
        // 这里简化处理，实际应该使用JSON库
        this.body = obj.toString();
        return contentType("application/json");
    }

    public HttpRequestBuilder timeout(int timeoutMs) {
        this.timeout = timeoutMs;
        return this;
    }

    public HttpRequest build() {
        if (url == null) {
            throw new IllegalStateException("URL is required");
        }

        return new HttpRequest(url, method, headers, queryParams, body, timeout);
    }
}

// HTTP 请求对象
class HttpRequest {
    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final Map<String, String> queryParams;
    private final String body;
    private final int timeout;

    public HttpRequest(String url, String method, Map<String, String> headers,
                      Map<String, String> queryParams, String body, int timeout) {
        this.url = url;
        this.method = method;
        this.headers = new HashMap<>(headers);
        this.queryParams = new HashMap<>(queryParams);
        this.body = body;
        this.timeout = timeout;
    }

    public String execute() {
        // 模拟HTTP请求执行
        StringBuilder result = new StringBuilder();
        result.append("执行HTTP请求:\n");
        result.append("URL: ").append(getFullUrl()).append("\n");
        result.append("Method: ").append(method).append("\n");
        result.append("Headers: ").append(headers).append("\n");
        if (body != null) {
            result.append("Body: ").append(body).append("\n");
        }
        result.append("Timeout: ").append(timeout).append("ms\n");
        result.append("请求执行成功!");

        return result.toString();
    }

    private String getFullUrl() {
        if (queryParams.isEmpty()) {
            return url;
        }

        StringBuilder fullUrl = new StringBuilder(url);
        fullUrl.append("?");

        boolean first = true;
        for (Map.Entry<String, String> param : queryParams.entrySet()) {
            if (!first) {
                fullUrl.append("&");
            }
            fullUrl.append(param.getKey()).append("=").append(param.getValue());
            first = false;
        }

        return fullUrl.toString();
    }

    // Getter methods
    public String getUrl() { return url; }
    public String getMethod() { return method; }
    public Map<String, String> getHeaders() { return new HashMap<>(headers); }
    public Map<String, String> getQueryParams() { return new HashMap<>(queryParams); }
    public String getBody() { return body; }
    public int getTimeout() { return timeout; }
}

// 使用示例
public class HttpRequestBuilderDemo {
    public static void main(String[] args) {
        System.out.println("=== HTTP 请求建造者演示 ===\n");

        // GET 请求
        HttpRequest getRequest = new HttpRequestBuilder()
                .url("https://api.example.com/users")
                .get()
                .param("page", "1")
                .param("limit", "10")
                .header("User-Agent", "MyApp/1.0")
                .authorization("abc123token")
                .timeout(5000)
                .build();

        System.out.println("GET 请求：");
        System.out.println(getRequest.execute());

        System.out.println("\n" + "=".repeat(50) + "\n");

        // POST 请求
        HttpRequest postRequest = new HttpRequestBuilder()
                .url("https://api.example.com/users")
                .post()
                .contentType("application/json")
                .authorization("abc123token")
                .body("{\"name\": \"张三\", \"email\": \"zhangsan@example.com\"}")
                .timeout(10000)
                .build();

        System.out.println("POST 请求：");
        System.out.println(postRequest.execute());

        System.out.println("\n" + "=".repeat(50) + "\n");

        // PUT 请求
        Map<String, String> commonHeaders = new HashMap<>();
        commonHeaders.put("Accept", "application/json");
        commonHeaders.put("Cache-Control", "no-cache");

        HttpRequest putRequest = new HttpRequestBuilder()
                .url("https://api.example.com/users/123")
                .put()
                .headers(commonHeaders)
                .contentType("application/json")
                .authorization("abc123token")
                .body("{\"name\": \"李四\", \"email\": \"lisi@example.com\"}")
                .build();

        System.out.println("PUT 请求：");
        System.out.println(putRequest.execute());
    }
}
```

### 3. 邮件建造者

```java
// 邮件建造者
class EmailBuilder {
    private String from;
    private List<String> to = new ArrayList<>();
    private List<String> cc = new ArrayList<>();
    private List<String> bcc = new ArrayList<>();
    private String subject;
    private String textContent;
    private String htmlContent;
    private List<String> attachments = new ArrayList<>();
    private boolean isHighPriority = false;
    private boolean requestReadReceipt = false;

    public EmailBuilder from(String from) {
        this.from = from;
        return this;
    }

    public EmailBuilder to(String... recipients) {
        Collections.addAll(this.to, recipients);
        return this;
    }

    public EmailBuilder cc(String... recipients) {
        Collections.addAll(this.cc, recipients);
        return this;
    }

    public EmailBuilder bcc(String... recipients) {
        Collections.addAll(this.bcc, recipients);
        return this;
    }

    public EmailBuilder subject(String subject) {
        this.subject = subject;
        return this;
    }

    public EmailBuilder textContent(String content) {
        this.textContent = content;
        return this;
    }

    public EmailBuilder htmlContent(String content) {
        this.htmlContent = content;
        return this;
    }

    public EmailBuilder attachment(String filePath) {
        this.attachments.add(filePath);
        return this;
    }

    public EmailBuilder attachments(String... filePaths) {
        Collections.addAll(this.attachments, filePaths);
        return this;
    }

    public EmailBuilder highPriority() {
        this.isHighPriority = true;
        return this;
    }

    public EmailBuilder requestReadReceipt() {
        this.requestReadReceipt = true;
        return this;
    }

    public Email build() {
        // 验证必需字段
        if (from == null || from.isEmpty()) {
            throw new IllegalStateException("发件人不能为空");
        }
        if (to.isEmpty()) {
            throw new IllegalStateException("收件人不能为空");
        }
        if (subject == null || subject.isEmpty()) {
            throw new IllegalStateException("邮件主题不能为空");
        }
        if (textContent == null && htmlContent == null) {
            throw new IllegalStateException("邮件内容不能为空");
        }

        return new Email(from, to, cc, bcc, subject, textContent, htmlContent,
                        attachments, isHighPriority, requestReadReceipt);
    }
}

// 邮件对象
class Email {
    private final String from;
    private final List<String> to;
    private final List<String> cc;
    private final List<String> bcc;
    private final String subject;
    private final String textContent;
    private final String htmlContent;
    private final List<String> attachments;
    private final boolean isHighPriority;
    private final boolean requestReadReceipt;

    public Email(String from, List<String> to, List<String> cc, List<String> bcc,
                String subject, String textContent, String htmlContent,
                List<String> attachments, boolean isHighPriority, boolean requestReadReceipt) {
        this.from = from;
        this.to = new ArrayList<>(to);
        this.cc = new ArrayList<>(cc);
        this.bcc = new ArrayList<>(bcc);
        this.subject = subject;
        this.textContent = textContent;
        this.htmlContent = htmlContent;
        this.attachments = new ArrayList<>(attachments);
        this.isHighPriority = isHighPriority;
        this.requestReadReceipt = requestReadReceipt;
    }

    public void send() {
        System.out.println("=== 发送邮件 ===");
        System.out.println("发件人: " + from);
        System.out.println("收件人: " + String.join(", ", to));

        if (!cc.isEmpty()) {
            System.out.println("抄送: " + String.join(", ", cc));
        }
        if (!bcc.isEmpty()) {
            System.out.println("密送: " + String.join(", ", bcc));
        }

        System.out.println("主题: " + subject);

        if (isHighPriority) {
            System.out.println("优先级: 高");
        }
        if (requestReadReceipt) {
            System.out.println("已请求阅读回执");
        }

        System.out.println("--- 邮件内容 ---");
        if (textContent != null) {
            System.out.println("纯文本内容:");
            System.out.println(textContent);
        }
        if (htmlContent != null) {
            System.out.println("HTML内容:");
            System.out.println(htmlContent);
        }

        if (!attachments.isEmpty()) {
            System.out.println("附件: " + String.join(", ", attachments));
        }

        System.out.println("邮件发送成功!");
    }

    // Getter方法
    public String getFrom() { return from; }
    public List<String> getTo() { return new ArrayList<>(to); }
    public List<String> getCc() { return new ArrayList<>(cc); }
    public List<String> getBcc() { return new ArrayList<>(bcc); }
    public String getSubject() { return subject; }
    public String getTextContent() { return textContent; }
    public String getHtmlContent() { return htmlContent; }
    public List<String> getAttachments() { return new ArrayList<>(attachments); }
    public boolean isHighPriority() { return isHighPriority; }
    public boolean isRequestReadReceipt() { return requestReadReceipt; }
}

// 使用示例
public class EmailBuilderDemo {
    public static void main(String[] args) {
        System.out.println("=== 邮件建造者演示 ===\n");

        // 简单邮件
        Email simpleEmail = new EmailBuilder()
                .from("sender@example.com")
                .to("recipient@example.com")
                .subject("简单邮件测试")
                .textContent("这是一封简单的测试邮件。")
                .build();

        simpleEmail.send();

        System.out.println("\n" + "=".repeat(50) + "\n");

        // 复杂邮件
        Email complexEmail = new EmailBuilder()
                .from("admin@company.com")
                .to("team@company.com", "manager@company.com")
                .cc("hr@company.com")
                .bcc("audit@company.com")
                .subject("【紧急】系统维护通知")
                .htmlContent("""
                    <h2>系统维护通知</h2>
                    <p>各位同事：</p>
                    <p>我们将在 <strong>今晚22:00-次日02:00</strong> 进行系统维护。</p>
                    <ul>
                        <li>维护期间系统将无法访问</li>
                        <li>请提前保存工作内容</li>
                        <li>如有紧急情况请联系运维团队</li>
                    </ul>
                    <p>感谢理解与配合！</p>
                    """)
                .textContent("""
                    系统维护通知

                    各位同事：
                    我们将在今晚22:00-次日02:00进行系统维护。
                    维护期间系统将无法访问，请提前保存工作内容。

                    感谢理解与配合！
                    """)
                .attachment("/path/to/maintenance-plan.pdf")
                .attachment("/path/to/backup-instructions.doc")
                .highPriority()
                .requestReadReceipt()
                .build();

        complexEmail.send();

        System.out.println("\n" + "=".repeat(50) + "\n");

        // 营销邮件
        Email marketingEmail = new EmailBuilder()
                .from("marketing@shop.com")
                .to("customer1@example.com", "customer2@example.com")
                .subject("🎉 双11大促销 - 限时优惠！")
                .htmlContent("""
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h1 style="color: #ff6600;">🎉 双11狂欢节</h1>
                        <p>亲爱的客户：</p>
                        <p>双11大促销来啦！<strong>全场商品5折起</strong></p>
                        <div style="background: #fffacd; padding: 20px; border-radius: 5px;">
                            <h3>限时优惠码：<span style="color: red;">DOUBLE11</span></h3>
                            <p>立享额外9折优惠！</p>
                        </div>
                        <p><a href="https://shop.com/sale" style="background: #ff6600; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">立即购买</a></p>
                    </body>
                    </html>
                    """)
                .textContent("""
                    双11狂欢节

                    亲爱的客户：
                    双11大促销来啦！全场商品5折起

                    限时优惠码：DOUBLE11
                    立享额外9折优惠！

                    访问 https://shop.com/sale 立即购买
                    """)
                .build();

        marketingEmail.send();
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **封装性好**
   - 客户端不需要知道产品内部组成细节

2. **建造代码复用**
   - 同样的建造过程可以创建不同的产品表示

3. **精确控制构建过程**
   - 可以更精细地控制产品构建步骤

4. **符合单一职责原则**
   - 将复杂构建逻辑从产品类中分离出来

5. **链式调用友好**
   - 支持流畅的链式调用语法

### ❌ 缺点

1. **增加代码复杂度**
   - 需要创建多个建造者类

2. **产品必须有共同特点**
   - 建造的产品应该有足够的相似性

3. **内部变化影响建造者**
   - 如果产品的内部变化复杂，建造者也会变得复杂

## 🎯 使用场景总结

### 适合使用建造者模式的场景：

1. **构造函数参数过多**
   - 特别是有很多可选参数的情况

2. **对象创建过程复杂**
   - 需要多个步骤才能创建完整对象

3. **需要创建不同表示的同一类对象**
   - 如不同配置的电脑、不同风格的房屋

4. **希望将构建过程和表示分离**
   - 同样的构建过程创建不同的产品

### 不适合使用的场景：

- 产品的内部变化复杂，会导致建造者过于复杂
- 产品之间差异很大，缺乏共同接口
- 对象创建很简单，使用建造者反而复杂化

## 🧠 记忆技巧

### 形象比喻
> **建造者模式就像是"装修房子"**：
> - 设计师（Director）制定装修方案
> - 包工头（Builder）负责具体施工
> - 不同包工头有不同专长（ConcreteBuilder）
> - 最终交付精装房子（Product）
> - 可以用同样方案装修不同风格

### 与工厂模式的区别

| 特性 | 工厂模式 | 建造者模式 |
|------|----------|------------|
| 目的 | 创建产品 | 构建复杂产品 |
| 关注点 | 产品类型 | 构建过程 |
| 结果 | 一次性创建 | 分步骤构建 |
| 适用场景 | 产品简单 | 产品复杂 |

### 选择建议
1. **参数很多** → 建造者模式
2. **构建过程复杂** → 建造者模式
3. **需要不同表示** → 建造者模式
4. **对象简单** → 直接构造或工厂

## 🚀 总结

建造者模式通过分离构建过程和表示，解决了复杂对象创建的问题：

- ✅ 避免构造函数参数过多
- ✅ 支持链式调用，语法优雅
- ✅ 构建过程可以复用
- ✅ 可以精确控制构建步骤

**记住**：当你发现构造函数有很多参数，特别是有很多可选参数时，就该考虑建造者模式了！

---
*下一篇：原型模式 - 对象克隆的高效实现*