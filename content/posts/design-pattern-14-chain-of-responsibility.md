---
title: "设计模式详解：责任链模式(Chain of Responsibility) - 请求处理的链式传递"
date: 2025-09-19T05:00:00+08:00
draft: false
tags: ["设计模式", "责任链模式", "Chain of Responsibility", "Java", "行为型模式"]
categories: ["设计模式"]
author: "lesshash"
description: "深入浅出讲解责任链模式，从基础概念到高级实现，包含纯责任链、不纯责任链、过滤器链等实战技巧，让你彻底掌握请求传递的艺术"
---

## 🎯 什么是责任链模式？

### 生活中的例子
想象一下**公司的请假审批流程**：你要请假，需要按级别逐级审批。普通请假找直接主管；超过3天找部门经理；超过一周找总监；超过半个月找VP。每一级都有自己的审批权限，如果超出权限就传递给上级。这样形成了一条**审批链**，每个环节都有机会处理请求，也可以将请求传递给下一个环节。这就是责任链模式的核心思想：**将请求的发送者和接收者解耦，让多个对象都有机会处理请求，将这些对象连成一条链，沿着这条链传递请求，直到有对象处理它为止**。

### 问题背景
在软件开发中，经常遇到需要多级处理的场景：
- 🏢 **审批流程** - 请假、报销、采购等多级审批
- 🌐 **Web过滤器** - 认证、授权、日志、缓存等过滤器链
- 🎮 **游戏事件** - 输入处理、碰撞检测、AI响应等
- 📊 **数据处理** - 验证、转换、清洗、存储等管道
- 🔧 **中间件** - 消息处理、错误处理、性能监控等

如果用传统的if-else或switch来处理，会导致：
- 代码耦合度高
- 难以扩展和维护
- 违反开闭原则
- 处理逻辑混乱

## 🧠 设计思想

### 核心角色
1. **Handler（抽象处理者）** - 定义处理请求的接口，包含下一个处理者的引用
2. **ConcreteHandler（具体处理者）** - 实现具体的处理逻辑
3. **Client（客户端）** - 创建责任链并发送请求

### 责任链类型
- **纯责任链**：只有一个处理者处理请求
- **不纯责任链**：每个处理者都可以处理请求的一部分

### 记忆口诀
> **"链式传递，逐级处理，解耦发送者，灵活又优雅"**

## 💻 代码实现

### 1. 基础责任链模式 - 请假审批系统

```java
/**
 * 请假申请
 */
public class LeaveRequest {
    private String employeeName;
    private int days;
    private String reason;
    private String urgency; // NORMAL, URGENT, EMERGENCY

    public LeaveRequest(String employeeName, int days, String reason, String urgency) {
        this.employeeName = employeeName;
        this.days = days;
        this.reason = reason;
        this.urgency = urgency;
    }

    @Override
    public String toString() {
        return String.format("请假申请[员工:%s, 天数:%d天, 原因:%s, 紧急程度:%s]",
                           employeeName, days, reason, urgency);
    }

    // getter方法
    public String getEmployeeName() { return employeeName; }
    public int getDays() { return days; }
    public String getReason() { return reason; }
    public String getUrgency() { return urgency; }
}

/**
 * 抽象处理者 - 审批者
 */
public abstract class Approver {
    protected String name;
    protected String position;
    protected Approver nextApprover; // 下一个处理者

    public Approver(String name, String position) {
        this.name = name;
        this.position = position;
    }

    /**
     * 设置下一个处理者
     */
    public void setNextApprover(Approver nextApprover) {
        this.nextApprover = nextApprover;
    }

    /**
     * 处理请求的模板方法
     */
    public final void handleRequest(LeaveRequest request) {
        System.out.println("📋 " + position + " " + name + " 收到" + request);

        if (canHandle(request)) {
            approve(request);
        } else if (nextApprover != null) {
            System.out.println("⬆️ " + position + " " + name + " 将请求转发给上级");
            nextApprover.handleRequest(request);
        } else {
            reject(request);
        }
    }

    /**
     * 判断是否能处理请求
     */
    protected abstract boolean canHandle(LeaveRequest request);

    /**
     * 批准请求
     */
    protected void approve(LeaveRequest request) {
        System.out.println("✅ " + position + " " + name + " 批准了" + request);
        logApproval(request, "APPROVED");
    }

    /**
     * 拒绝请求
     */
    protected void reject(LeaveRequest request) {
        System.out.println("❌ " + position + " " + name + " 拒绝了" + request + " (超出审批权限且无上级)");
        logApproval(request, "REJECTED");
    }

    /**
     * 记录审批日志
     */
    private void logApproval(LeaveRequest request, String result) {
        System.out.println("📝 审批记录: " + name + " -> " + request.getEmployeeName() +
                          " -> " + request.getDays() + "天 -> " + result);
    }

    public String getName() { return name; }
    public String getPosition() { return position; }
}

/**
 * 具体处理者 - 直接主管
 */
public class DirectSupervisor extends Approver {
    public DirectSupervisor(String name) {
        super(name, "直接主管");
    }

    @Override
    protected boolean canHandle(LeaveRequest request) {
        // 直接主管可以审批2天以内的普通请假
        return request.getDays() <= 2 && "NORMAL".equals(request.getUrgency());
    }
}

/**
 * 具体处理者 - 部门经理
 */
public class DepartmentManager extends Approver {
    public DepartmentManager(String name) {
        super(name, "部门经理");
    }

    @Override
    protected boolean canHandle(LeaveRequest request) {
        // 部门经理可以审批7天以内的请假，或者紧急情况下3天以内
        return request.getDays() <= 7 ||
               (request.getDays() <= 3 && "URGENT".equals(request.getUrgency()));
    }
}

/**
 * 具体处理者 - 总监
 */
public class Director extends Approver {
    public Director(String name) {
        super(name, "总监");
    }

    @Override
    protected boolean canHandle(LeaveRequest request) {
        // 总监可以审批15天以内的请假，或者紧急情况下7天以内
        return request.getDays() <= 15 ||
               (request.getDays() <= 7 && "URGENT".equals(request.getUrgency()));
    }
}

/**
 * 具体处理者 - VP
 */
public class VicePresident extends Approver {
    public VicePresident(String name) {
        super(name, "VP");
    }

    @Override
    protected boolean canHandle(LeaveRequest request) {
        // VP可以审批30天以内的请假，或者任何紧急情况
        return request.getDays() <= 30 || "URGENT".equals(request.getUrgency()) ||
               "EMERGENCY".equals(request.getUrgency());
    }
}

/**
 * 具体处理者 - CEO
 */
public class CEO extends Approver {
    public CEO(String name) {
        super(name, "CEO");
    }

    @Override
    protected boolean canHandle(LeaveRequest request) {
        // CEO可以处理任何请假申请
        return true;
    }

    @Override
    protected void approve(LeaveRequest request) {
        System.out.println("👑 CEO " + name + " 特殊批准了" + request);
        if (request.getDays() > 30) {
            System.out.println("💼 CEO提醒: 长期请假可能需要人事部门配合安排工作交接");
        }
        logApproval(request, "CEO_APPROVED");
    }

    private void logApproval(LeaveRequest request, String result) {
        System.out.println("📝 高级审批记录: " + name + " -> " + request.getEmployeeName() +
                          " -> " + request.getDays() + "天 -> " + result);
    }
}

/**
 * 审批链管理器
 */
public class ApprovalChainManager {
    private Approver chainHead;

    public ApprovalChainManager() {
        buildApprovalChain();
    }

    /**
     * 构建审批链
     */
    private void buildApprovalChain() {
        // 创建审批者
        Approver supervisor = new DirectSupervisor("张主管");
        Approver manager = new DepartmentManager("李经理");
        Approver director = new Director("王总监");
        Approver vp = new VicePresident("陈VP");
        Approver ceo = new CEO("刘CEO");

        // 构建责任链
        supervisor.setNextApprover(manager);
        manager.setNextApprover(director);
        director.setNextApprover(vp);
        vp.setNextApprover(ceo);

        this.chainHead = supervisor;

        System.out.println("🔗 审批链构建完成:");
        System.out.println("   直接主管 -> 部门经理 -> 总监 -> VP -> CEO");
    }

    /**
     * 处理请假申请
     */
    public void processLeaveRequest(LeaveRequest request) {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("🚀 开始处理" + request);
        chainHead.handleRequest(request);
    }

    /**
     * 批量处理请假申请
     */
    public void processBatchRequests(LeaveRequest... requests) {
        System.out.println("📊 批量处理 " + requests.length + " 个请假申请");
        for (LeaveRequest request : requests) {
            processLeaveRequest(request);
        }
    }
}

// 请假审批责任链演示
public class LeaveApprovalChainDemo {
    public static void main(String[] args) {
        System.out.println("=== 请假审批责任链模式演示 ===");

        ApprovalChainManager chainManager = new ApprovalChainManager();

        // 创建不同的请假申请
        LeaveRequest[] requests = {
            new LeaveRequest("小张", 1, "感冒休息", "NORMAL"),           // 直接主管可批准
            new LeaveRequest("小李", 5, "旅游度假", "NORMAL"),           // 部门经理可批准
            new LeaveRequest("小王", 3, "家庭紧急情况", "URGENT"),       // 部门经理可批准(紧急)
            new LeaveRequest("小赵", 10, "婚假", "NORMAL"),             // 总监可批准
            new LeaveRequest("小陈", 20, "产假", "NORMAL"),             // VP可批准
            new LeaveRequest("小刘", 6, "父亲病重", "URGENT"),          // 总监可批准(紧急)
            new LeaveRequest("小吴", 45, "长期病假", "NORMAL"),         // 需要CEO批准
            new LeaveRequest("小孙", 15, "突发疾病", "EMERGENCY")       // VP可批准(紧急)
        };

        // 处理所有请假申请
        chainManager.processBatchRequests(requests);

        System.out.println("\n" + "=".repeat(60));
        System.out.println("=== 责任链模式优势总结 ===");
        System.out.println("✅ 解耦: 请求者无需知道具体的处理者");
        System.out.println("✅ 灵活: 可以动态改变责任链的结构");
        System.out.println("✅ 扩展: 易于增加新的处理者");
        System.out.println("✅ 职责: 每个处理者专注于自己的职责范围");
        System.out.println("✅ 流程: 符合实际业务的审批流程");
    }
}
```

### 2. Web过滤器链模式

```java
/**
 * HTTP请求对象
 */
public class HttpRequest {
    private String path;
    private String method;
    private Map<String, String> headers;
    private Map<String, String> parameters;
    private String body;
    private String userToken;

    public HttpRequest(String method, String path) {
        this.method = method;
        this.path = path;
        this.headers = new HashMap<>();
        this.parameters = new HashMap<>();
    }

    public void addHeader(String key, String value) {
        headers.put(key, value);
    }

    public void addParameter(String key, String value) {
        parameters.put(key, value);
    }

    @Override
    public String toString() {
        return method + " " + path + " Headers:" + headers + " Params:" + parameters;
    }

    // getter和setter方法
    public String getPath() { return path; }
    public String getMethod() { return method; }
    public Map<String, String> getHeaders() { return headers; }
    public Map<String, String> getParameters() { return parameters; }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
    public String getUserToken() { return userToken; }
    public void setUserToken(String userToken) { this.userToken = userToken; }
}

/**
 * HTTP响应对象
 */
public class HttpResponse {
    private int statusCode;
    private Map<String, String> headers;
    private String body;
    private boolean processed;

    public HttpResponse() {
        this.statusCode = 200;
        this.headers = new HashMap<>();
        this.processed = false;
    }

    public void setError(int statusCode, String message) {
        this.statusCode = statusCode;
        this.body = message;
        this.processed = true;
    }

    @Override
    public String toString() {
        return "HTTP " + statusCode + " " + (body != null ? body : "OK");
    }

    // getter和setter方法
    public int getStatusCode() { return statusCode; }
    public void setStatusCode(int statusCode) { this.statusCode = statusCode; }
    public Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
    public boolean isProcessed() { return processed; }
    public void setProcessed(boolean processed) { this.processed = processed; }
}

/**
 * 抽象过滤器
 */
public abstract class Filter {
    protected Filter nextFilter;
    protected String filterName;

    public Filter(String filterName) {
        this.filterName = filterName;
    }

    public void setNextFilter(Filter nextFilter) {
        this.nextFilter = nextFilter;
    }

    /**
     * 过滤器处理模板方法
     */
    public final void doFilter(HttpRequest request, HttpResponse response) {
        System.out.println("🔍 " + filterName + " 开始处理: " + request.getMethod() + " " + request.getPath());

        // 前置处理
        boolean continueChain = preProcess(request, response);

        if (continueChain && !response.isProcessed()) {
            if (nextFilter != null) {
                nextFilter.doFilter(request, response);
            }

            // 后置处理
            postProcess(request, response);
        } else {
            System.out.println("⛔ " + filterName + " 终止了请求处理链");
        }
    }

    /**
     * 前置处理 - 子类实现
     * @return true表示继续处理链，false表示终止
     */
    protected abstract boolean preProcess(HttpRequest request, HttpResponse response);

    /**
     * 后置处理 - 子类可选实现
     */
    protected void postProcess(HttpRequest request, HttpResponse response) {
        System.out.println("✅ " + filterName + " 后置处理完成");
    }

    public String getFilterName() { return filterName; }
}

/**
 * 具体过滤器 - 认证过滤器
 */
public class AuthenticationFilter extends Filter {
    private Set<String> validTokens;

    public AuthenticationFilter() {
        super("认证过滤器");
        this.validTokens = new HashSet<>();
        // 模拟一些有效的token
        validTokens.add("token123");
        validTokens.add("token456");
        validTokens.add("admin_token");
    }

    @Override
    protected boolean preProcess(HttpRequest request, HttpResponse response) {
        // 公开路径不需要认证
        if (isPublicPath(request.getPath())) {
            System.out.println("🌐 公开路径，跳过认证: " + request.getPath());
            return true;
        }

        String token = request.getHeaders().get("Authorization");
        if (token == null) {
            response.setError(401, "缺少Authorization header");
            return false;
        }

        if (validTokens.contains(token)) {
            request.setUserToken(token);
            System.out.println("🔐 认证成功: " + token);
            return true;
        } else {
            response.setError(401, "无效的token");
            return false;
        }
    }

    private boolean isPublicPath(String path) {
        return path.equals("/login") || path.equals("/register") || path.startsWith("/public");
    }
}

/**
 * 具体过滤器 - 授权过滤器
 */
public class AuthorizationFilter extends Filter {
    private Map<String, Set<String>> userPermissions;

    public AuthorizationFilter() {
        super("授权过滤器");
        this.userPermissions = new HashMap<>();

        // 模拟用户权限
        userPermissions.put("token123", Set.of("READ", "WRITE"));
        userPermissions.put("token456", Set.of("READ"));
        userPermissions.put("admin_token", Set.of("READ", "WRITE", "DELETE", "ADMIN"));
    }

    @Override
    protected boolean preProcess(HttpRequest request, HttpResponse response) {
        String token = request.getUserToken();
        if (token == null) {
            // 如果没有token（如公开路径），跳过授权检查
            return true;
        }

        String requiredPermission = getRequiredPermission(request);
        if (requiredPermission == null) {
            return true; // 不需要特殊权限
        }

        Set<String> permissions = userPermissions.get(token);
        if (permissions != null && permissions.contains(requiredPermission)) {
            System.out.println("✅ 授权成功: " + requiredPermission);
            return true;
        } else {
            response.setError(403, "权限不足，需要: " + requiredPermission);
            return false;
        }
    }

    private String getRequiredPermission(HttpRequest request) {
        String path = request.getPath();
        String method = request.getMethod();

        if (path.startsWith("/admin")) {
            return "ADMIN";
        } else if ("DELETE".equals(method)) {
            return "DELETE";
        } else if ("POST".equals(method) || "PUT".equals(method)) {
            return "WRITE";
        } else if ("GET".equals(method)) {
            return "READ".toUpperCase();
        }

        return null;
    }
}

/**
 * 具体过滤器 - 日志过滤器
 */
public class LoggingFilter extends Filter {
    public LoggingFilter() {
        super("日志过滤器");
    }

    @Override
    protected boolean preProcess(HttpRequest request, HttpResponse response) {
        long startTime = System.currentTimeMillis();
        request.addParameter("startTime", String.valueOf(startTime));

        System.out.println("📝 请求开始: " + request);
        return true;
    }

    @Override
    protected void postProcess(HttpRequest request, HttpResponse response) {
        long startTime = Long.parseLong(request.getParameters().get("startTime"));
        long duration = System.currentTimeMillis() - startTime;

        System.out.println("📝 请求完成: " + request.getMethod() + " " + request.getPath() +
                          " -> " + response.getStatusCode() + " (耗时: " + duration + "ms)");
        super.postProcess(request, response);
    }
}

/**
 * 具体过滤器 - 缓存过滤器
 */
public class CacheFilter extends Filter {
    private Map<String, String> cache;

    public CacheFilter() {
        super("缓存过滤器");
        this.cache = new HashMap<>();

        // 预置一些缓存数据
        cache.put("GET /api/users", "缓存的用户列表数据");
        cache.put("GET /api/config", "缓存的配置数据");
    }

    @Override
    protected boolean preProcess(HttpRequest request, HttpResponse response) {
        if ("GET".equals(request.getMethod())) {
            String cacheKey = request.getMethod() + " " + request.getPath();
            String cachedData = cache.get(cacheKey);

            if (cachedData != null) {
                response.setBody(cachedData);
                response.setProcessed(true);
                System.out.println("💾 缓存命中: " + cacheKey);
                return false; // 终止处理链，直接返回缓存结果
            } else {
                System.out.println("💾 缓存未命中: " + cacheKey);
            }
        }

        return true;
    }

    @Override
    protected void postProcess(HttpRequest request, HttpResponse response) {
        // 缓存GET请求的成功响应
        if ("GET".equals(request.getMethod()) && response.getStatusCode() == 200) {
            String cacheKey = request.getMethod() + " " + request.getPath();
            cache.put(cacheKey, response.getBody());
            System.out.println("💾 响应已缓存: " + cacheKey);
        }
        super.postProcess(request, response);
    }
}

/**
 * 具体过滤器 - 速率限制过滤器
 */
public class RateLimitFilter extends Filter {
    private Map<String, Integer> requestCounts;
    private Map<String, Long> lastResetTime;
    private static final int RATE_LIMIT = 10; // 每分钟10次
    private static final long WINDOW_SIZE = 60000; // 1分钟窗口

    public RateLimitFilter() {
        super("速率限制过滤器");
        this.requestCounts = new HashMap<>();
        this.lastResetTime = new HashMap<>();
    }

    @Override
    protected boolean preProcess(HttpRequest request, HttpResponse response) {
        String clientKey = getClientKey(request);
        long currentTime = System.currentTimeMillis();

        // 重置计数器（如果窗口过期）
        Long lastReset = lastResetTime.get(clientKey);
        if (lastReset == null || (currentTime - lastReset) >= WINDOW_SIZE) {
            requestCounts.put(clientKey, 0);
            lastResetTime.put(clientKey, currentTime);
        }

        // 检查是否超过限制
        int currentCount = requestCounts.getOrDefault(clientKey, 0);
        if (currentCount >= RATE_LIMIT) {
            response.setError(429, "请求过于频繁，请稍后再试");
            System.out.println("⚠️ 速率限制触发: " + clientKey + " (" + currentCount + "/" + RATE_LIMIT + ")");
            return false;
        }

        // 增加计数
        requestCounts.put(clientKey, currentCount + 1);
        System.out.println("📊 速率检查通过: " + clientKey + " (" + (currentCount + 1) + "/" + RATE_LIMIT + ")");
        return true;
    }

    private String getClientKey(HttpRequest request) {
        // 简化：使用token作为客户端标识
        String token = request.getUserToken();
        return token != null ? token : "anonymous";
    }
}

/**
 * 过滤器链管理器
 */
public class FilterChainManager {
    private Filter filterChain;
    private List<Filter> filters;

    public FilterChainManager() {
        this.filters = new ArrayList<>();
        buildFilterChain();
    }

    /**
     * 构建过滤器链
     */
    private void buildFilterChain() {
        // 创建过滤器实例
        LoggingFilter loggingFilter = new LoggingFilter();
        RateLimitFilter rateLimitFilter = new RateLimitFilter();
        AuthenticationFilter authFilter = new AuthenticationFilter();
        AuthorizationFilter authzFilter = new AuthorizationFilter();
        CacheFilter cacheFilter = new CacheFilter();

        // 构建过滤器链 - 顺序很重要
        loggingFilter.setNextFilter(rateLimitFilter);
        rateLimitFilter.setNextFilter(authFilter);
        authFilter.setNextFilter(authzFilter);
        authzFilter.setNextFilter(cacheFilter);

        this.filterChain = loggingFilter;

        // 保存过滤器列表
        filters.add(loggingFilter);
        filters.add(rateLimitFilter);
        filters.add(authFilter);
        filters.add(authzFilter);
        filters.add(cacheFilter);

        System.out.println("🔗 过滤器链构建完成:");
        System.out.println("   日志 -> 速率限制 -> 认证 -> 授权 -> 缓存");
    }

    /**
     * 处理HTTP请求
     */
    public HttpResponse processRequest(HttpRequest request) {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("🚀 开始处理请求: " + request);

        HttpResponse response = new HttpResponse();
        filterChain.doFilter(request, response);

        // 如果没有被任何过滤器处理，模拟业务逻辑处理
        if (!response.isProcessed()) {
            response.setBody("业务逻辑处理结果: " + request.getPath());
            response.setProcessed(true);
            System.out.println("🎯 业务逻辑处理完成");
        }

        System.out.println("📤 响应: " + response);
        return response;
    }

    public void printFilterChain() {
        System.out.println("=== 当前过滤器链 ===");
        for (int i = 0; i < filters.size(); i++) {
            System.out.println((i + 1) + ". " + filters.get(i).getFilterName());
        }
    }
}

// Web过滤器链演示
public class WebFilterChainDemo {
    public static void main(String[] args) {
        System.out.println("=== Web过滤器链模式演示 ===");

        FilterChainManager chainManager = new FilterChainManager();
        chainManager.printFilterChain();

        // 创建不同的HTTP请求
        HttpRequest[] requests = {
            // 1. 公开路径请求
            createRequest("GET", "/public/info"),

            // 2. 需要认证的请求 - 无token
            createRequest("GET", "/api/users"),

            // 3. 需要认证的请求 - 有效token
            createAuthenticatedRequest("GET", "/api/users", "token123"),

            // 4. 缓存命中的请求
            createAuthenticatedRequest("GET", "/api/config", "token123"),

            // 5. 需要写权限的请求
            createAuthenticatedRequest("POST", "/api/users", "token456"), // 只有读权限

            // 6. 管理员请求
            createAuthenticatedRequest("DELETE", "/admin/users/1", "admin_token"),

            // 7. 超过速率限制的请求
            createAuthenticatedRequest("GET", "/api/data", "token123")
        };

        // 处理所有请求
        for (HttpRequest request : requests) {
            chainManager.processRequest(request);
        }

        // 模拟速率限制 - 快速发送多个请求
        System.out.println("\n" + "=".repeat(80));
        System.out.println("=== 模拟速率限制触发 ===");

        HttpRequest rateLimitTest = createAuthenticatedRequest("GET", "/api/test", "token123");
        for (int i = 0; i < 12; i++) { // 发送12个请求（超过10个限制）
            System.out.println("\n--- 第 " + (i + 1) + " 个请求 ---");
            chainManager.processRequest(rateLimitTest);
        }

        System.out.println("\n" + "=".repeat(80));
        System.out.println("=== 过滤器链模式优势总结 ===");
        System.out.println("✅ 模块化: 每个过滤器职责单一");
        System.out.println("✅ 可配置: 可以动态调整过滤器顺序");
        System.out.println("✅ 可扩展: 易于添加新的过滤器");
        System.out.println("✅ 复用性: 过滤器可以在不同场景复用");
        System.out.println("✅ 流水线: 形成清晰的处理流水线");
    }

    private static HttpRequest createRequest(String method, String path) {
        return new HttpRequest(method, path);
    }

    private static HttpRequest createAuthenticatedRequest(String method, String path, String token) {
        HttpRequest request = new HttpRequest(method, path);
        request.addHeader("Authorization", token);
        return request;
    }
}
```

### 3. 游戏事件处理责任链

```java
/**
 * 游戏事件
 */
public abstract class GameEvent {
    private String eventType;
    private long timestamp;
    private boolean handled;

    public GameEvent(String eventType) {
        this.eventType = eventType;
        this.timestamp = System.currentTimeMillis();
        this.handled = false;
    }

    public String getEventType() { return eventType; }
    public long getTimestamp() { return timestamp; }
    public boolean isHandled() { return handled; }
    public void setHandled(boolean handled) { this.handled = handled; }

    @Override
    public String toString() {
        return eventType + " (时间: " + timestamp + ")";
    }
}

/**
 * 输入事件
 */
public class InputEvent extends GameEvent {
    private String inputType; // KEYBOARD, MOUSE, TOUCH
    private String key;
    private int x, y; // 鼠标位置

    public InputEvent(String inputType, String key, int x, int y) {
        super("INPUT");
        this.inputType = inputType;
        this.key = key;
        this.x = x;
        this.y = y;
    }

    @Override
    public String toString() {
        return super.toString() + " [" + inputType + ": " + key + " (" + x + "," + y + ")]";
    }

    // getter方法
    public String getInputType() { return inputType; }
    public String getKey() { return key; }
    public int getX() { return x; }
    public int getY() { return y; }
}

/**
 * 碰撞事件
 */
public class CollisionEvent extends GameEvent {
    private String object1;
    private String object2;
    private double impactForce;

    public CollisionEvent(String object1, String object2, double impactForce) {
        super("COLLISION");
        this.object1 = object1;
        this.object2 = object2;
        this.impactForce = impactForce;
    }

    @Override
    public String toString() {
        return super.toString() + " [" + object1 + " 碰撞 " + object2 + " (力度: " + impactForce + ")]";
    }

    // getter方法
    public String getObject1() { return object1; }
    public String getObject2() { return object2; }
    public double getImpactForce() { return impactForce; }
}

/**
 * 抽象游戏事件处理器
 */
public abstract class GameEventHandler {
    protected String handlerName;
    protected GameEventHandler nextHandler;
    protected boolean enabled;

    public GameEventHandler(String handlerName) {
        this.handlerName = handlerName;
        this.enabled = true;
    }

    public void setNextHandler(GameEventHandler nextHandler) {
        this.nextHandler = nextHandler;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    /**
     * 处理事件的模板方法
     */
    public final void handleEvent(GameEvent event) {
        if (!enabled) {
            System.out.println("⏸️ " + handlerName + " 已禁用，跳过处理");
            passToNext(event);
            return;
        }

        System.out.println("🎮 " + handlerName + " 收到事件: " + event);

        if (canHandle(event)) {
            processEvent(event);

            // 检查是否需要继续传递
            if (!event.isHandled() || allowContinueChain(event)) {
                passToNext(event);
            } else {
                System.out.println("🛑 " + handlerName + " 终止了事件传递");
            }
        } else {
            passToNext(event);
        }
    }

    private void passToNext(GameEvent event) {
        if (nextHandler != null) {
            nextHandler.handleEvent(event);
        }
    }

    /**
     * 判断是否能处理该事件
     */
    protected abstract boolean canHandle(GameEvent event);

    /**
     * 处理事件的具体逻辑
     */
    protected abstract void processEvent(GameEvent event);

    /**
     * 是否允许继续传递事件（默认不允许）
     */
    protected boolean allowContinueChain(GameEvent event) {
        return false;
    }

    public String getHandlerName() { return handlerName; }
}

/**
 * 输入处理器
 */
public class InputHandler extends GameEventHandler {
    private Set<String> supportedInputTypes;

    public InputHandler() {
        super("输入处理器");
        this.supportedInputTypes = Set.of("KEYBOARD", "MOUSE", "TOUCH");
    }

    @Override
    protected boolean canHandle(GameEvent event) {
        return event instanceof InputEvent;
    }

    @Override
    protected void processEvent(GameEvent event) {
        InputEvent inputEvent = (InputEvent) event;

        if (supportedInputTypes.contains(inputEvent.getInputType())) {
            processInput(inputEvent);
            event.setHandled(true);
        }
    }

    private void processInput(InputEvent inputEvent) {
        switch (inputEvent.getInputType()) {
            case "KEYBOARD":
                System.out.println("⌨️ 处理键盘输入: " + inputEvent.getKey());
                if ("SPACE".equals(inputEvent.getKey())) {
                    System.out.println("   🚀 玩家跳跃");
                } else if ("W".equals(inputEvent.getKey())) {
                    System.out.println("   ⬆️ 玩家向前移动");
                }
                break;

            case "MOUSE":
                System.out.println("🖱️ 处理鼠标输入: " + inputEvent.getKey() +
                                  " 位置(" + inputEvent.getX() + "," + inputEvent.getY() + ")");
                if ("LEFT_CLICK".equals(inputEvent.getKey())) {
                    System.out.println("   ⚔️ 玩家攻击");
                }
                break;

            case "TOUCH":
                System.out.println("👆 处理触摸输入: 位置(" + inputEvent.getX() + "," + inputEvent.getY() + ")");
                break;
        }
    }

    @Override
    protected boolean allowContinueChain(GameEvent event) {
        // 输入事件可以继续传递给其他处理器（如UI处理器）
        return true;
    }
}

/**
 * UI处理器
 */
public class UIHandler extends GameEventHandler {
    public UIHandler() {
        super("UI处理器");
    }

    @Override
    protected boolean canHandle(GameEvent event) {
        if (event instanceof InputEvent) {
            InputEvent inputEvent = (InputEvent) event;
            // 检查是否点击在UI区域
            return inputEvent.getX() < 200 && inputEvent.getY() < 100; // 假设UI在左上角200x100区域
        }
        return false;
    }

    @Override
    protected void processEvent(GameEvent event) {
        InputEvent inputEvent = (InputEvent) event;
        System.out.println("🖼️ UI处理: 位置(" + inputEvent.getX() + "," + inputEvent.getY() + ")");

        if (inputEvent.getX() < 100 && inputEvent.getY() < 50) {
            System.out.println("   📋 显示游戏菜单");
        } else {
            System.out.println("   ℹ️ 显示提示信息");
        }

        event.setHandled(true);
    }
}

/**
 * 碰撞处理器
 */
public class CollisionHandler extends GameEventHandler {
    public CollisionHandler() {
        super("碰撞处理器");
    }

    @Override
    protected boolean canHandle(GameEvent event) {
        return event instanceof CollisionEvent;
    }

    @Override
    protected void processEvent(GameEvent event) {
        CollisionEvent collisionEvent = (CollisionEvent) event;
        System.out.println("💥 碰撞处理: " + collisionEvent.getObject1() +
                          " 撞击 " + collisionEvent.getObject2());

        handleCollision(collisionEvent);
        event.setHandled(true);
    }

    private void handleCollision(CollisionEvent event) {
        String obj1 = event.getObject1();
        String obj2 = event.getObject2();
        double force = event.getImpactForce();

        if (obj1.equals("Player") || obj2.equals("Player")) {
            if (obj1.equals("Enemy") || obj2.equals("Enemy")) {
                System.out.println("   ⚔️ 玩家与敌人碰撞，造成伤害: " + (force * 10));
            } else if (obj1.equals("Coin") || obj2.equals("Coin")) {
                System.out.println("   💰 玩家收集金币 +10");
            } else if (obj1.equals("Wall") || obj2.equals("Wall")) {
                System.out.println("   🧱 玩家撞墙，移动被阻止");
            }
        } else if ((obj1.equals("Bullet") && obj2.equals("Enemy")) ||
                   (obj1.equals("Enemy") && obj2.equals("Bullet"))) {
            System.out.println("   🎯 子弹击中敌人，敌人生命值 -" + (force * 20));
        }
    }

    @Override
    protected boolean allowContinueChain(GameEvent event) {
        // 碰撞事件可能需要触发其他效果（如音效、粒子效果）
        return true;
    }
}

/**
 * 音效处理器
 */
public class AudioHandler extends GameEventHandler {
    public AudioHandler() {
        super("音效处理器");
    }

    @Override
    protected boolean canHandle(GameEvent event) {
        // 音效处理器可以处理任何事件来播放对应音效
        return true;
    }

    @Override
    protected void processEvent(GameEvent event) {
        playAudioForEvent(event);
    }

    private void playAudioForEvent(GameEvent event) {
        if (event instanceof InputEvent) {
            InputEvent inputEvent = (InputEvent) event;
            if ("SPACE".equals(inputEvent.getKey())) {
                System.out.println("🔊 播放跳跃音效");
            } else if ("LEFT_CLICK".equals(inputEvent.getKey())) {
                System.out.println("🔊 播放攻击音效");
            }
        } else if (event instanceof CollisionEvent) {
            CollisionEvent collisionEvent = (CollisionEvent) event;
            if (collisionEvent.getImpactForce() > 5.0) {
                System.out.println("🔊 播放重碰撞音效");
            } else {
                System.out.println("🔊 播放轻碰撞音效");
            }
        }
    }

    @Override
    protected boolean allowContinueChain(GameEvent event) {
        // 音效处理不影响其他处理器
        return true;
    }
}

/**
 * 游戏事件管理器
 */
public class GameEventManager {
    private GameEventHandler eventChain;
    private List<GameEventHandler> handlers;

    public GameEventManager() {
        this.handlers = new ArrayList<>();
        buildEventChain();
    }

    private void buildEventChain() {
        // 创建处理器
        InputHandler inputHandler = new InputHandler();
        UIHandler uiHandler = new UIHandler();
        CollisionHandler collisionHandler = new CollisionHandler();
        AudioHandler audioHandler = new AudioHandler();

        // 构建责任链
        inputHandler.setNextHandler(uiHandler);
        uiHandler.setNextHandler(collisionHandler);
        collisionHandler.setNextHandler(audioHandler);

        this.eventChain = inputHandler;

        // 保存处理器列表
        handlers.addAll(Arrays.asList(inputHandler, uiHandler, collisionHandler, audioHandler));

        System.out.println("🔗 游戏事件链构建完成:");
        System.out.println("   输入处理 -> UI处理 -> 碰撞处理 -> 音效处理");
    }

    public void handleEvent(GameEvent event) {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("⚡ 游戏事件: " + event);
        eventChain.handleEvent(event);
    }

    public void enableHandler(String handlerName) {
        handlers.stream()
                .filter(h -> h.getHandlerName().equals(handlerName))
                .forEach(h -> h.setEnabled(true));
        System.out.println("✅ 启用处理器: " + handlerName);
    }

    public void disableHandler(String handlerName) {
        handlers.stream()
                .filter(h -> h.getHandlerName().equals(handlerName))
                .forEach(h -> h.setEnabled(false));
        System.out.println("⛔ 禁用处理器: " + handlerName);
    }

    public void printHandlerStatus() {
        System.out.println("=== 处理器状态 ===");
        for (GameEventHandler handler : handlers) {
            System.out.println("  " + handler.getHandlerName() + ": " +
                             (handler.enabled ? "启用" : "禁用"));
        }
    }
}

// 游戏事件责任链演示
public class GameEventChainDemo {
    public static void main(String[] args) {
        System.out.println("=== 游戏事件处理责任链演示 ===");

        GameEventManager eventManager = new GameEventManager();
        eventManager.printHandlerStatus();

        // 创建各种游戏事件
        GameEvent[] events = {
            // 键盘输入事件
            new InputEvent("KEYBOARD", "SPACE", 0, 0),
            new InputEvent("KEYBOARD", "W", 0, 0),

            // 鼠标输入事件
            new InputEvent("MOUSE", "LEFT_CLICK", 300, 200), // 游戏区域点击
            new InputEvent("MOUSE", "LEFT_CLICK", 50, 30),   // UI区域点击

            // 触摸事件
            new InputEvent("TOUCH", "TAP", 150, 150),

            // 碰撞事件
            new CollisionEvent("Player", "Enemy", 7.5),
            new CollisionEvent("Player", "Coin", 2.0),
            new CollisionEvent("Bullet", "Enemy", 8.0),
            new CollisionEvent("Player", "Wall", 3.0)
        };

        // 处理所有事件
        for (GameEvent event : events) {
            eventManager.handleEvent(event);
        }

        System.out.println("\n" + "=".repeat(70));
        System.out.println("=== 动态控制处理器 ===");

        // 禁用音效处理器
        eventManager.disableHandler("音效处理器");
        eventManager.printHandlerStatus();

        System.out.println("\n重新处理一个碰撞事件（无音效）:");
        eventManager.handleEvent(new CollisionEvent("Player", "Enemy", 6.0));

        // 重新启用音效处理器
        eventManager.enableHandler("音效处理器");

        System.out.println("\n重新处理一个输入事件（有音效）:");
        eventManager.handleEvent(new InputEvent("KEYBOARD", "SPACE", 0, 0));

        System.out.println("\n" + "=".repeat(70));
        System.out.println("=== 游戏事件责任链优势总结 ===");
        System.out.println("✅ 模块化: 每种事件有专门的处理器");
        System.out.println("✅ 灵活性: 可以动态启用/禁用处理器");
        System.out.println("✅ 扩展性: 易于添加新的事件类型和处理器");
        System.out.println("✅ 复用性: 处理器可以处理多种事件");
        System.out.println("✅ 解耦性: 事件发送者不需要知道具体处理器");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **解耦请求发送者和接收者**
   - 发送者不需要知道具体的处理者
   - 降低系统耦合度

2. **灵活的责任分配**
   - 可以动态改变链内的成员或调整顺序
   - 支持运行时配置

3. **符合开闭原则**
   - 新增处理者无需修改现有代码
   - 扩展性强

4. **职责单一**
   - 每个处理者专注于自己的处理逻辑
   - 代码清晰易维护

### ❌ 缺点

1. **性能问题**
   - 请求需要沿着链传递
   - 链过长时影响性能

2. **调试困难**
   - 运行时才能确定处理者
   - 调试和追踪困难

3. **不保证被处理**
   - 请求可能传递到链末尾仍未被处理
   - 需要有默认处理机制

## 🎯 使用场景总结

### 适合使用责任链模式的场景：
- 🏢 **审批流程** - 多级审批、工作流处理
- 🌐 **Web过滤器** - 请求预处理、响应后处理
- 🎮 **事件处理** - 游戏事件、UI事件处理
- 📊 **数据处理管道** - 数据验证、转换、清洗
- 🔧 **中间件系统** - 消息处理、错误处理

### 不适合使用责任链模式的场景：
- 处理逻辑简单且固定
- 性能要求极高的场景
- 处理者之间有复杂的依赖关系
- 链的结构经常变化

## 🧠 记忆技巧

### 形象比喻
> **责任链模式就像是 "客服热线"**：
> - 客户问题先到一级客服（第一个处理者）
> - 一级解决不了转二级客服（传递给下一个）
> - 层层递进直到问题解决（找到合适的处理者）
> - 每级客服都有自己的职责范围（处理能力）

### 设计要点
> **"链式传递，逐级处理，解耦发送者，灵活且优雅"**

### 与装饰模式的区别
- **责任链模式**：选择性处理，通常只有一个处理者处理
- **装饰模式**：层层增强，每个装饰器都会处理

## 🔧 最佳实践

### 1. 责任链构建器

```java
/**
 * 责任链构建器
 */
public class ChainBuilder<T> {
    private List<T> handlers = new ArrayList<>();

    public ChainBuilder<T> addHandler(T handler) {
        handlers.add(handler);
        return this;
    }

    public T build() {
        if (handlers.isEmpty()) {
            throw new IllegalStateException("责任链不能为空");
        }

        for (int i = 0; i < handlers.size() - 1; i++) {
            // 需要handlers实现setNext方法
            setNext(handlers.get(i), handlers.get(i + 1));
        }

        return handlers.get(0);
    }

    private void setNext(T current, T next) {
        // 使用反射调用setNext方法
        try {
            Method setNextMethod = current.getClass().getMethod("setNext", current.getClass());
            setNextMethod.invoke(current, next);
        } catch (Exception e) {
            throw new RuntimeException("设置下一个处理者失败", e);
        }
    }
}
```

### 2. 责任链工厂

```java
/**
 * 责任链工厂
 */
public class ChainFactory {
    public static Approver createApprovalChain() {
        return new ChainBuilder<Approver>()
            .addHandler(new DirectSupervisor("张主管"))
            .addHandler(new DepartmentManager("李经理"))
            .addHandler(new Director("王总监"))
            .addHandler(new VicePresident("陈VP"))
            .addHandler(new CEO("刘CEO"))
            .build();
    }

    public static Filter createFilterChain() {
        return new ChainBuilder<Filter>()
            .addHandler(new LoggingFilter())
            .addHandler(new AuthenticationFilter())
            .addHandler(new AuthorizationFilter())
            .addHandler(new CacheFilter())
            .build();
    }
}
```

### 3. 条件责任链

```java
/**
 * 条件责任链
 */
public abstract class ConditionalHandler<T> {
    protected ConditionalHandler<T> nextHandler;

    public void setNext(ConditionalHandler<T> next) {
        this.nextHandler = next;
    }

    public final void handle(T request) {
        if (shouldHandle(request)) {
            doHandle(request);
        }

        if (shouldContinue(request) && nextHandler != null) {
            nextHandler.handle(request);
        }
    }

    protected abstract boolean shouldHandle(T request);
    protected abstract void doHandle(T request);
    protected boolean shouldContinue(T request) { return true; }
}
```

## 🚀 总结

责任链模式通过将请求沿着处理者链传递，实现了发送者与接收者的解耦，特别适用于：

- **多级处理流程**的场景
- **处理逻辑可能变化**的系统
- **需要灵活配置处理顺序**的业务

核心思想：
- **链式传递请求**
- **解耦发送者和接收者**
- **灵活的责任分配**
- **职责单一的处理者**

设计要点：
- **合理设计处理者的职责范围**
- **考虑链的性能影响**
- **提供默认处理机制**
- **支持动态配置链结构**

记住，**责任链模式是流程控制器，不是万能传递带**，要在合适的逐级处理场景下使用！

---
*下一篇：观察者模式 - 一对多的依赖通知机制*