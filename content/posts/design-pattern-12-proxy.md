---
title: "设计模式详解12：代理模式(Proxy) - 控制对象访问的智能代理"
date: 2024-12-12T10:12:00+08:00
draft: false
tags: ["设计模式", "代理模式", "Proxy", "Java", "结构型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解代理模式，从基础概念到高级实现，包含虚拟代理、保护代理、远程代理等实战技巧，让你彻底掌握访问控制的艺术"
---

## 🎯 什么是代理模式？

### 生活中的例子
想象你要买一套房子，但你不直接和房主交易，而是通过**房产中介**。中介代表房主处理各种事务：带你看房、谈判价格、处理合同、办理手续等。中介不仅简化了你的操作，还可以：验证你的购买资格、保护房主的隐私、在合适的时候才联系房主。这个房产中介就是一个"代理"，它控制着你对房主的访问。这就是代理模式的核心思想：**为其他对象提供代理以控制对这个对象的访问**。

### 问题背景
在软件开发中，直接访问某些对象可能存在问题：
- 🚀 **性能问题** - 对象创建或操作成本很高
- 🔒 **安全问题** - 需要控制访问权限
- 🌐 **网络问题** - 对象位于远程服务器
- 💾 **资源问题** - 对象占用大量内存或资源
- 📊 **监控问题** - 需要记录对象的访问日志

如果直接访问这些对象，会导致：
- 性能低下
- 安全隐患
- 资源浪费
- 难以监控和管理

## 🧠 设计思想

### 核心角色
1. **Subject（抽象主题）** - 定义了真实主题和代理的公共接口
2. **RealSubject（真实主题）** - 定义了代理所代表的真实对象
3. **Proxy（代理）** - 保存对真实主题的引用，控制对它的访问
4. **Client（客户端）** - 通过代理访问真实主题

### 代理类型
- **虚拟代理**：延迟创建开销大的对象
- **保护代理**：控制对原始对象的访问权限
- **远程代理**：为远程对象提供本地代表
- **智能引用代理**：在访问对象时执行额外操作

### 记忆口诀
> **"代理控制，透明访问，延迟创建，权限检查"**

## 💻 代码实现

### 1. 虚拟代理 - 大图片延迟加载

```java
/**
 * 抽象主题 - 图片接口
 */
public interface Image {
    void display();
    void setPosition(int x, int y);
    String getImageInfo();
}

/**
 * 真实主题 - 高清图片
 */
public class HighResolutionImage implements Image {
    private String filename;
    private int x, y;
    private byte[] imageData; // 模拟图片数据
    private long loadTime;

    public HighResolutionImage(String filename) {
        this.filename = filename;
        this.x = 0;
        this.y = 0;
        loadImageFromDisk(); // 立即加载
    }

    private void loadImageFromDisk() {
        System.out.println("📸 正在从磁盘加载高清图片: " + filename);
        loadTime = System.currentTimeMillis();

        try {
            // 模拟大图片加载的耗时过程
            Thread.sleep(1000 + (int)(Math.random() * 1000)); // 1-2秒
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 模拟大图片数据
        imageData = new byte[10 * 1024 * 1024]; // 10MB
        System.out.println("✅ 图片加载完成: " + filename + " (10MB)");
    }

    @Override
    public void display() {
        long currentTime = System.currentTimeMillis();
        System.out.println("🖼️ 显示高清图片: " + filename +
                          " 在位置(" + x + "," + y + ")" +
                          " 加载于 " + (currentTime - loadTime) + "ms 前");
    }

    @Override
    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
        System.out.println("📍 移动图片 " + filename + " 到位置(" + x + "," + y + ")");
    }

    @Override
    public String getImageInfo() {
        return "HighResolutionImage{" +
               "filename='" + filename + "'" +
               ", size=" + (imageData != null ? imageData.length : 0) + " bytes" +
               ", position=(" + x + "," + y + ")" +
               '}';
    }
}

/**
 * 虚拟代理 - 图片代理
 */
public class ImageProxy implements Image {
    private String filename;
    private int x, y;
    private HighResolutionImage realImage; // 真实图片对象

    public ImageProxy(String filename) {
        this.filename = filename;
        this.x = 0;
        this.y = 0;
        // 注意：这里不立即创建真实对象
        System.out.println("🔗 创建图片代理: " + filename + " (未加载真实图片)");
    }

    @Override
    public void display() {
        // 延迟加载：只有在真正需要显示时才创建真实对象
        if (realImage == null) {
            System.out.println("🕐 首次显示，触发真实图片加载...");
            realImage = new HighResolutionImage(filename);
            realImage.setPosition(x, y); // 同步位置
        }
        realImage.display();
    }

    @Override
    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
        System.out.println("📍 代理记录位置: " + filename + " -> (" + x + "," + y + ")");

        // 如果真实对象已存在，同步位置
        if (realImage != null) {
            realImage.setPosition(x, y);
        }
    }

    @Override
    public String getImageInfo() {
        if (realImage == null) {
            return "ImageProxy{" +
                   "filename='" + filename + "'" +
                   ", position=(" + x + "," + y + ")" +
                   ", status=NOT_LOADED" +
                   '}';
        } else {
            return "ImageProxy{" +
                   "filename='" + filename + "'" +
                   ", realImage=" + realImage.getImageInfo() +
                   ", status=LOADED" +
                   '}';
        }
    }

    public boolean isLoaded() {
        return realImage != null;
    }
}

/**
 * 图片浏览器 - 客户端
 */
public class ImageViewer {
    private List<Image> images;
    private String viewerName;

    public ImageViewer(String viewerName) {
        this.viewerName = viewerName;
        this.images = new ArrayList<>();
    }

    public void loadImage(String filename) {
        // 使用代理而不是直接创建真实对象
        Image image = new ImageProxy(filename);
        images.add(image);
        System.out.println("📁 " + viewerName + " 加载图片: " + filename);
    }

    public void displayImage(int index) {
        if (index >= 0 && index < images.size()) {
            System.out.println("\n=== " + viewerName + " 显示第 " + index + " 张图片 ===");
            images.get(index).display();
        }
    }

    public void positionImage(int index, int x, int y) {
        if (index >= 0 && index < images.size()) {
            images.get(index).setPosition(x, y);
        }
    }

    public void displayAllImages() {
        System.out.println("\n=== " + viewerName + " 显示所有图片 ===");
        for (int i = 0; i < images.size(); i++) {
            System.out.println("图片 " + i + ":");
            images.get(i).display();
        }
    }

    public void printImageStatus() {
        System.out.println("\n=== " + viewerName + " 图片状态 ===");
        for (int i = 0; i < images.size(); i++) {
            System.out.println("图片 " + i + ": " + images.get(i).getImageInfo());
            if (images.get(i) instanceof ImageProxy) {
                ImageProxy proxy = (ImageProxy) images.get(i);
                System.out.println("  加载状态: " + (proxy.isLoaded() ? "已加载" : "未加载"));
            }
        }
    }

    public int getImageCount() {
        return images.size();
    }
}

// 虚拟代理演示
public class VirtualProxyDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 虚拟代理模式演示 ===");

        ImageViewer viewer = new ImageViewer("图片浏览器");

        System.out.println("\n=== 1. 快速加载多张图片（代理模式） ===");
        long startTime = System.currentTimeMillis();

        viewer.loadImage("landscape.jpg");
        viewer.loadImage("portrait.jpg");
        viewer.loadImage("abstract.jpg");

        long loadTime = System.currentTimeMillis() - startTime;
        System.out.println("📊 加载3张图片用时: " + loadTime + "ms");

        System.out.println("\n=== 2. 查看图片状态（未真正加载） ===");
        viewer.printImageStatus();

        System.out.println("\n=== 3. 操作图片位置（代理缓存操作） ===");
        viewer.positionImage(0, 100, 50);
        viewer.positionImage(1, 200, 100);
        viewer.positionImage(2, 300, 150);

        System.out.println("\n=== 4. 第一次显示图片（触发真实加载） ===");
        viewer.displayImage(1); // 只加载第2张图片

        System.out.println("\n=== 5. 再次查看状态（部分已加载） ===");
        viewer.printImageStatus();

        System.out.println("\n=== 6. 显示所有图片（触发剩余加载） ===");
        viewer.displayAllImages();

        System.out.println("\n=== 7. 最终状态检查 ===");
        viewer.printImageStatus();

        System.out.println("\n=== 8. 性能对比分析 ===");
        System.out.println("使用虚拟代理的好处:");
        System.out.println("✅ 快速创建：3张图片代理瞬间创建");
        System.out.println("✅ 延迟加载：只在需要时加载真实图片");
        System.out.println("✅ 内存节约：未显示的图片不占用内存");
        System.out.println("✅ 操作缓存：位置等操作先缓存在代理中");

        System.out.println("\n=== 9. 无代理模式对比 ===");
        System.out.println("如果不使用代理模式:");
        System.out.println("❌ 启动慢：所有图片立即加载");
        System.out.println("❌ 内存占用大：所有图片都在内存中");
        System.out.println("❌ 用户体验差：长时间等待");

        // 模拟无代理的情况（仅作演示）
        System.out.println("\n=== 模拟无代理模式的加载时间 ===");
        startTime = System.currentTimeMillis();
        System.out.println("模拟直接创建3个HighResolutionImage对象...");
        // 这里只是输出，不真正创建，因为会很慢
        System.out.println("预估时间: 3-6秒（每个图片1-2秒加载时间）");
        System.out.println("对比之下，代理模式的优势明显！");
    }
}
```

### 2. 保护代理 - 权限控制

```java
/**
 * 抽象主题 - 用户服务接口
 */
public interface UserService {
    String getUserInfo(String userId);
    boolean updateUserInfo(String userId, String newInfo);
    boolean deleteUser(String userId);
    List<String> getAllUsers();
}

/**
 * 用户信息类
 */
public class User {
    private String userId;
    private String name;
    private String email;
    private String role;

    public User(String userId, String name, String email, String role) {
        this.userId = userId;
        this.name = name;
        this.email = email;
        this.role = role;
    }

    @Override
    public String toString() {
        return "User{" +
               "userId='" + userId + "'" +
               ", name='" + name + "'" +
               ", email='" + email + "'" +
               ", role='" + role + "'" +
               '}';
    }

    // getter和setter方法
    public String getUserId() { return userId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    public void setName(String name) { this.name = name; }
    public void setEmail(String email) { this.email = email; }
}

/**
 * 真实主题 - 用户服务实现
 */
public class UserServiceImpl implements UserService {
    private Map<String, User> users;

    public UserServiceImpl() {
        this.users = new HashMap<>();
        initializeUsers();
    }

    private void initializeUsers() {
        users.put("admin001", new User("admin001", "管理员", "admin@company.com", "ADMIN"));
        users.put("user001", new User("user001", "张三", "zhangsan@company.com", "USER"));
        users.put("user002", new User("user002", "李四", "lisi@company.com", "USER"));
        users.put("manager001", new User("manager001", "王经理", "manager@company.com", "MANAGER"));
    }

    @Override
    public String getUserInfo(String userId) {
        System.out.println("💾 从数据库查询用户信息: " + userId);
        User user = users.get(userId);
        return user != null ? user.toString() : "用户不存在";
    }

    @Override
    public boolean updateUserInfo(String userId, String newInfo) {
        System.out.println("✏️ 更新用户信息: " + userId + " -> " + newInfo);
        User user = users.get(userId);
        if (user != null) {
            // 简化：这里只是演示，实际会解析newInfo并更新具体字段
            System.out.println("数据库更新成功");
            return true;
        }
        return false;
    }

    @Override
    public boolean deleteUser(String userId) {
        System.out.println("🗑️ 从数据库删除用户: " + userId);
        User removedUser = users.remove(userId);
        if (removedUser != null) {
            System.out.println("用户删除成功: " + removedUser.getName());
            return true;
        }
        return false;
    }

    @Override
    public List<String> getAllUsers() {
        System.out.println("📋 查询所有用户列表");
        return users.values().stream()
                   .map(User::toString)
                   .collect(Collectors.toList());
    }
}

/**
 * 当前用户会话
 */
public class UserSession {
    private String currentUserId;
    private String currentUserRole;

    public UserSession(String userId, String role) {
        this.currentUserId = userId;
        this.currentUserRole = role;
    }

    public String getCurrentUserId() { return currentUserId; }
    public String getCurrentUserRole() { return currentUserRole; }

    public boolean isAdmin() { return "ADMIN".equals(currentUserRole); }
    public boolean isManager() { return "MANAGER".equals(currentUserRole); }
    public boolean isUser() { return "USER".equals(currentUserRole); }

    @Override
    public String toString() {
        return "UserSession{userId='" + currentUserId + "', role='" + currentUserRole + "'}";
    }
}

/**
 * 保护代理 - 用户服务权限代理
 */
public class UserServiceProtectionProxy implements UserService {
    private UserServiceImpl realUserService;
    private UserSession currentSession;

    public UserServiceProtectionProxy(UserSession session) {
        this.currentSession = session;
        this.realUserService = new UserServiceImpl();
    }

    @Override
    public String getUserInfo(String userId) {
        System.out.println("🔒 权限检查 - 查询用户信息");

        // 权限检查：用户只能查询自己的信息，管理员和经理可以查询任何人
        if (currentSession.isAdmin() || currentSession.isManager()) {
            System.out.println("✅ 管理员/经理权限：允许查询任何用户信息");
            return realUserService.getUserInfo(userId);
        } else if (currentSession.getCurrentUserId().equals(userId)) {
            System.out.println("✅ 用户权限：允许查询自己的信息");
            return realUserService.getUserInfo(userId);
        } else {
            System.out.println("❌ 权限不足：普通用户只能查询自己的信息");
            return "权限不足：无法查询其他用户信息";
        }
    }

    @Override
    public boolean updateUserInfo(String userId, String newInfo) {
        System.out.println("🔒 权限检查 - 更新用户信息");

        // 权限检查：用户只能更新自己的信息，管理员可以更新任何人
        if (currentSession.isAdmin()) {
            System.out.println("✅ 管理员权限：允许更新任何用户信息");
            return realUserService.updateUserInfo(userId, newInfo);
        } else if (currentSession.getCurrentUserId().equals(userId)) {
            System.out.println("✅ 用户权限：允许更新自己的信息");
            return realUserService.updateUserInfo(userId, newInfo);
        } else {
            System.out.println("❌ 权限不足：只能更新自己的信息");
            return false;
        }
    }

    @Override
    public boolean deleteUser(String userId) {
        System.out.println("🔒 权限检查 - 删除用户");

        // 权限检查：只有管理员可以删除用户
        if (currentSession.isAdmin()) {
            System.out.println("✅ 管理员权限：允许删除用户");
            return realUserService.deleteUser(userId);
        } else {
            System.out.println("❌ 权限不足：只有管理员可以删除用户");
            return false;
        }
    }

    @Override
    public List<String> getAllUsers() {
        System.out.println("🔒 权限检查 - 查询所有用户");

        // 权限检查：只有管理员和经理可以查看所有用户
        if (currentSession.isAdmin() || currentSession.isManager()) {
            System.out.println("✅ 管理员/经理权限：允许查看所有用户");
            return realUserService.getAllUsers();
        } else {
            System.out.println("❌ 权限不足：只有管理员和经理可以查看所有用户");
            return Arrays.asList("权限不足：无法查看用户列表");
        }
    }

    public void changeSession(UserSession newSession) {
        this.currentSession = newSession;
        System.out.println("🔄 会话切换: " + newSession);
    }
}

// 保护代理演示
public class ProtectionProxyDemo {
    public static void main(String[] args) {
        System.out.println("=== 保护代理模式演示 ===");

        System.out.println("\n=== 1. 普通用户登录 ===");
        UserSession userSession = new UserSession("user001", "USER");
        UserService userService = new UserServiceProtectionProxy(userSession);

        System.out.println("当前用户: " + userSession);

        // 普通用户操作测试
        System.out.println("\n--- 普通用户操作测试 ---");
        System.out.println("1. 查询自己的信息:");
        String result1 = userService.getUserInfo("user001");
        System.out.println("结果: " + result1);

        System.out.println("\n2. 查询其他用户信息:");
        String result2 = userService.getUserInfo("user002");
        System.out.println("结果: " + result2);

        System.out.println("\n3. 更新自己的信息:");
        boolean result3 = userService.updateUserInfo("user001", "新邮箱: new@email.com");
        System.out.println("结果: " + (result3 ? "成功" : "失败"));

        System.out.println("\n4. 尝试删除用户:");
        boolean result4 = userService.deleteUser("user002");
        System.out.println("结果: " + (result4 ? "成功" : "失败"));

        System.out.println("\n5. 查看所有用户:");
        List<String> result5 = userService.getAllUsers();
        result5.forEach(System.out::println);

        System.out.println("\n=== 2. 经理登录 ===");
        UserSession managerSession = new UserSession("manager001", "MANAGER");
        UserServiceProtectionProxy proxy = (UserServiceProtectionProxy) userService;
        proxy.changeSession(managerSession);

        // 经理操作测试
        System.out.println("\n--- 经理操作测试 ---");
        System.out.println("1. 查询任何用户信息:");
        String result6 = userService.getUserInfo("user001");
        System.out.println("结果: " + result6);

        System.out.println("\n2. 查看所有用户:");
        List<String> result7 = userService.getAllUsers();
        result7.forEach(System.out::println);

        System.out.println("\n3. 尝试删除用户:");
        boolean result8 = userService.deleteUser("user002");
        System.out.println("结果: " + (result8 ? "成功" : "失败"));

        System.out.println("\n=== 3. 管理员登录 ===");
        UserSession adminSession = new UserSession("admin001", "ADMIN");
        proxy.changeSession(adminSession);

        // 管理员操作测试
        System.out.println("\n--- 管理员操作测试 ---");
        System.out.println("1. 查询任何用户信息:");
        String result9 = userService.getUserInfo("user001");
        System.out.println("结果: " + result9);

        System.out.println("\n2. 更新任何用户信息:");
        boolean result10 = userService.updateUserInfo("user001", "管理员修改的信息");
        System.out.println("结果: " + (result10 ? "成功" : "失败"));

        System.out.println("\n3. 删除用户:");
        boolean result11 = userService.deleteUser("user002");
        System.out.println("结果: " + (result11 ? "成功" : "失败"));

        System.out.println("\n4. 查看所有用户:");
        List<String> result12 = userService.getAllUsers();
        result12.forEach(System.out::println);

        System.out.println("\n=== 4. 权限总结 ===");
        System.out.println("用户权限(USER):");
        System.out.println("  ✅ 查询自己的信息");
        System.out.println("  ✅ 更新自己的信息");
        System.out.println("  ❌ 查询他人信息");
        System.out.println("  ❌ 删除用户");
        System.out.println("  ❌ 查看所有用户");

        System.out.println("\n经理权限(MANAGER):");
        System.out.println("  ✅ 查询任何用户信息");
        System.out.println("  ✅ 查看所有用户");
        System.out.println("  ❌ 删除用户");

        System.out.println("\n管理员权限(ADMIN):");
        System.out.println("  ✅ 所有操作权限");

        System.out.println("\n=== 保护代理的价值 ===");
        System.out.println("🔒 安全性：基于角色的访问控制");
        System.out.println("🔒 透明性：客户端无需关心权限逻辑");
        System.out.println("🔒 灵活性：可以动态切换用户会话");
        System.out.println("🔒 可维护性：权限逻辑集中管理");
    }
}
```

### 3. 远程代理 - 网络服务代理

```java
/**
 * 抽象主题 - 文件服务接口
 */
public interface FileService {
    String downloadFile(String filename);
    boolean uploadFile(String filename, String content);
    List<String> listFiles();
    boolean deleteFile(String filename);
    long getFileSize(String filename);
}

/**
 * 网络响应对象
 */
public class NetworkResponse {
    private boolean success;
    private String data;
    private String errorMessage;
    private long responseTime;

    public NetworkResponse(boolean success, String data, String errorMessage) {
        this.success = success;
        this.data = data;
        this.errorMessage = errorMessage;
        this.responseTime = System.currentTimeMillis();
    }

    public boolean isSuccess() { return success; }
    public String getData() { return data; }
    public String getErrorMessage() { return errorMessage; }
    public long getResponseTime() { return responseTime; }
}

/**
 * 真实主题 - 远程文件服务
 */
public class RemoteFileService implements FileService {
    private String serverUrl;
    private Map<String, String> files; // 模拟远程文件系统

    public RemoteFileService(String serverUrl) {
        this.serverUrl = serverUrl;
        this.files = new HashMap<>();
        initializeFiles();
    }

    private void initializeFiles() {
        files.put("document.txt", "这是一个文档文件的内容...");
        files.put("image.jpg", "这是一个图片文件的二进制数据...");
        files.put("config.json", "{\"setting1\":\"value1\",\"setting2\":\"value2\"}");
    }

    @Override
    public String downloadFile(String filename) {
        System.out.println("🌐 正在从远程服务器下载文件: " + serverUrl + "/" + filename);

        // 模拟网络延迟
        simulateNetworkDelay(500, 1500);

        String content = files.get(filename);
        if (content != null) {
            System.out.println("✅ 文件下载成功: " + filename);
            return content;
        } else {
            System.out.println("❌ 文件不存在: " + filename);
            throw new RuntimeException("文件不存在: " + filename);
        }
    }

    @Override
    public boolean uploadFile(String filename, String content) {
        System.out.println("🌐 正在上传文件到远程服务器: " + serverUrl + "/" + filename);

        // 模拟网络延迟
        simulateNetworkDelay(1000, 2000);

        files.put(filename, content);
        System.out.println("✅ 文件上传成功: " + filename);
        return true;
    }

    @Override
    public List<String> listFiles() {
        System.out.println("🌐 正在获取远程文件列表: " + serverUrl);

        // 模拟网络延迟
        simulateNetworkDelay(300, 800);

        List<String> fileList = new ArrayList<>(files.keySet());
        System.out.println("✅ 获取文件列表成功，共 " + fileList.size() + " 个文件");
        return fileList;
    }

    @Override
    public boolean deleteFile(String filename) {
        System.out.println("🌐 正在删除远程文件: " + serverUrl + "/" + filename);

        // 模拟网络延迟
        simulateNetworkDelay(400, 1000);

        String removed = files.remove(filename);
        if (removed != null) {
            System.out.println("✅ 文件删除成功: " + filename);
            return true;
        } else {
            System.out.println("❌ 文件不存在: " + filename);
            return false;
        }
    }

    @Override
    public long getFileSize(String filename) {
        System.out.println("🌐 正在获取远程文件大小: " + serverUrl + "/" + filename);

        // 模拟网络延迟
        simulateNetworkDelay(200, 500);

        String content = files.get(filename);
        if (content != null) {
            long size = content.length();
            System.out.println("✅ 获取文件大小成功: " + filename + " (" + size + " 字节)");
            return size;
        } else {
            System.out.println("❌ 文件不存在: " + filename);
            throw new RuntimeException("文件不存在: " + filename);
        }
    }

    private void simulateNetworkDelay(int minMs, int maxMs) {
        try {
            int delay = minMs + (int)(Math.random() * (maxMs - minMs));
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * 远程代理 - 文件服务代理
 */
public class RemoteFileServiceProxy implements FileService {
    private RemoteFileService remoteService;
    private String serverUrl;
    private Map<String, String> cache; // 缓存
    private Map<String, Long> cacheTimestamps; // 缓存时间戳
    private long cacheExpireTime = 30000; // 缓存过期时间30秒

    public RemoteFileServiceProxy(String serverUrl) {
        this.serverUrl = serverUrl;
        this.cache = new HashMap<>();
        this.cacheTimestamps = new HashMap<>();
        // 延迟创建真实的远程服务
    }

    private RemoteFileService getRemoteService() {
        if (remoteService == null) {
            System.out.println("🔗 创建远程服务连接: " + serverUrl);
            remoteService = new RemoteFileService(serverUrl);
        }
        return remoteService;
    }

    @Override
    public String downloadFile(String filename) {
        System.out.println("📥 代理处理下载请求: " + filename);

        // 检查缓存
        if (isCacheValid(filename)) {
            System.out.println("💾 从缓存返回文件内容: " + filename);
            return cache.get(filename);
        }

        try {
            // 调用远程服务
            String content = getRemoteService().downloadFile(filename);

            // 缓存结果
            cache.put(filename, content);
            cacheTimestamps.put(filename, System.currentTimeMillis());
            System.out.println("💾 文件内容已缓存: " + filename);

            return content;
        } catch (Exception e) {
            System.out.println("❌ 下载失败: " + e.getMessage());
            // 可以返回缓存的旧版本或默认内容
            if (cache.containsKey(filename)) {
                System.out.println("🔄 返回缓存的旧版本: " + filename);
                return cache.get(filename);
            }
            throw e;
        }
    }

    @Override
    public boolean uploadFile(String filename, String content) {
        System.out.println("📤 代理处理上传请求: " + filename);

        try {
            boolean success = getRemoteService().uploadFile(filename, content);

            if (success) {
                // 更新缓存
                cache.put(filename, content);
                cacheTimestamps.put(filename, System.currentTimeMillis());
                System.out.println("💾 上传成功，更新缓存: " + filename);
            }

            return success;
        } catch (Exception e) {
            System.out.println("❌ 上传失败: " + e.getMessage());
            return false;
        }
    }

    @Override
    public List<String> listFiles() {
        System.out.println("📋 代理处理文件列表请求");

        // 文件列表通常不缓存，因为变化频繁
        try {
            return getRemoteService().listFiles();
        } catch (Exception e) {
            System.out.println("❌ 获取文件列表失败: " + e.getMessage());
            return new ArrayList<>();
        }
    }

    @Override
    public boolean deleteFile(String filename) {
        System.out.println("🗑️ 代理处理删除请求: " + filename);

        try {
            boolean success = getRemoteService().deleteFile(filename);

            if (success) {
                // 清除缓存
                cache.remove(filename);
                cacheTimestamps.remove(filename);
                System.out.println("💾 删除成功，清除缓存: " + filename);
            }

            return success;
        } catch (Exception e) {
            System.out.println("❌ 删除失败: " + e.getMessage());
            return false;
        }
    }

    @Override
    public long getFileSize(String filename) {
        System.out.println("📏 代理处理文件大小查询: " + filename);

        try {
            return getRemoteService().getFileSize(filename);
        } catch (Exception e) {
            System.out.println("❌ 获取文件大小失败: " + e.getMessage());
            return -1;
        }
    }

    private boolean isCacheValid(String filename) {
        if (!cache.containsKey(filename)) {
            return false;
        }

        Long timestamp = cacheTimestamps.get(filename);
        if (timestamp == null) {
            return false;
        }

        return (System.currentTimeMillis() - timestamp) < cacheExpireTime;
    }

    public void clearCache() {
        cache.clear();
        cacheTimestamps.clear();
        System.out.println("💾 缓存已清空");
    }

    public void printCacheStatus() {
        System.out.println("=== 缓存状态 ===");
        System.out.println("缓存项数: " + cache.size());
        for (String filename : cache.keySet()) {
            Long timestamp = cacheTimestamps.get(filename);
            long age = System.currentTimeMillis() - timestamp;
            boolean valid = age < cacheExpireTime;
            System.out.println("  " + filename + ": " + (valid ? "有效" : "过期") + " (年龄: " + age + "ms)");
        }
    }
}

/**
 * 文件管理器 - 客户端
 */
public class FileManager {
    private FileService fileService;
    private String managerName;

    public FileManager(String managerName, FileService fileService) {
        this.managerName = managerName;
        this.fileService = fileService;
    }

    public void performFileOperations() {
        System.out.println("=== " + managerName + " 执行文件操作 ===");

        try {
            // 1. 列出文件
            System.out.println("\n1. 查看文件列表:");
            List<String> files = fileService.listFiles();
            files.forEach(file -> System.out.println("  - " + file));

            // 2. 下载文件
            System.out.println("\n2. 下载文件:");
            String content1 = fileService.downloadFile("document.txt");
            System.out.println("内容预览: " + content1.substring(0, Math.min(50, content1.length())) + "...");

            // 3. 再次下载相同文件（测试缓存）
            System.out.println("\n3. 再次下载相同文件（测试缓存）:");
            String content2 = fileService.downloadFile("document.txt");
            System.out.println("内容预览: " + content2.substring(0, Math.min(50, content2.length())) + "...");

            // 4. 上传新文件
            System.out.println("\n4. 上传新文件:");
            boolean uploaded = fileService.uploadFile("newfile.txt", "这是新上传的文件内容");
            System.out.println("上传结果: " + (uploaded ? "成功" : "失败"));

            // 5. 查看文件大小
            System.out.println("\n5. 查看文件大小:");
            long size = fileService.getFileSize("config.json");
            System.out.println("config.json 大小: " + size + " 字节");

            // 6. 删除文件
            System.out.println("\n6. 删除文件:");
            boolean deleted = fileService.deleteFile("image.jpg");
            System.out.println("删除结果: " + (deleted ? "成功" : "失败"));

        } catch (Exception e) {
            System.out.println("操作过程中出现错误: " + e.getMessage());
        }
    }
}

// 远程代理演示
public class RemoteProxyDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== 远程代理模式演示 ===");

        String serverUrl = "https://fileserver.example.com";

        System.out.println("\n=== 1. 使用远程代理 ===");
        FileService proxyService = new RemoteFileServiceProxy(serverUrl);
        FileManager manager1 = new FileManager("代理文件管理器", proxyService);

        long startTime = System.currentTimeMillis();
        manager1.performFileOperations();
        long proxyTime = System.currentTimeMillis() - startTime;

        System.out.println("\n=== 2. 查看代理缓存状态 ===");
        if (proxyService instanceof RemoteFileServiceProxy) {
            RemoteFileServiceProxy proxy = (RemoteFileServiceProxy) proxyService;
            proxy.printCacheStatus();
        }

        System.out.println("\n=== 3. 测试缓存效果 ===");
        System.out.println("再次下载已缓存的文件:");
        startTime = System.currentTimeMillis();
        String content = proxyService.downloadFile("document.txt");
        long cacheHitTime = System.currentTimeMillis() - startTime;
        System.out.println("缓存命中耗时: " + cacheHitTime + "ms");

        System.out.println("\n=== 4. 与直接远程调用对比 ===");
        System.out.println("模拟直接使用远程服务（无代理）:");
        RemoteFileService directService = new RemoteFileService(serverUrl);
        FileManager manager2 = new FileManager("直接远程管理器", directService);

        startTime = System.currentTimeMillis();
        // 只执行一个操作进行对比
        System.out.println("直接下载文件:");
        String directContent = directService.downloadFile("document.txt");
        long directTime = System.currentTimeMillis() - startTime;

        System.out.println("\n=== 5. 性能对比 ===");
        System.out.println("代理首次操作耗时: " + proxyTime + "ms");
        System.out.println("代理缓存命中耗时: " + cacheHitTime + "ms");
        System.out.println("直接远程调用耗时: " + directTime + "ms");

        System.out.println("\n=== 6. 远程代理的优势 ===");
        System.out.println("✅ 透明性: 客户端不知道服务是本地还是远程");
        System.out.println("✅ 缓存机制: 减少网络调用，提高响应速度");
        System.out.println("✅ 错误处理: 网络失败时可以返回缓存数据");
        System.out.println("✅ 延迟连接: 只在需要时才建立网络连接");
        System.out.println("✅ 智能路由: 可以选择最优的服务器节点");

        System.out.println("\n=== 7. 缓存过期测试 ===");
        System.out.println("等待缓存过期...");
        Thread.sleep(2000); // 等待2秒（实际中缓存过期时间是30秒，这里仅作演示）

        System.out.println("再次访问（模拟缓存过期后的行为）:");
        String expiredContent = proxyService.downloadFile("document.txt");
        System.out.println("内容获取成功");

        // 清理
        if (proxyService instanceof RemoteFileServiceProxy) {
            RemoteFileServiceProxy proxy = (RemoteFileServiceProxy) proxyService;
            proxy.clearCache();
        }
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **透明性**
   - 客户端无需知道是否使用代理
   - 代理与真实对象实现相同接口

2. **控制访问**
   - 可以在访问真实对象前后进行额外操作
   - 权限检查、日志记录、性能监控等

3. **延迟初始化**
   - 虚拟代理可以延迟创建开销大的对象
   - 提高系统启动速度

4. **缓存机制**
   - 远程代理可以缓存结果，减少网络调用
   - 提高系统响应速度

### ❌ 缺点

1. **增加系统复杂性**
   - 引入了额外的代理层
   - 增加了类的数量

2. **可能影响性能**
   - 代理调用增加了间接层次
   - 某些场景下可能降低响应速度

3. **代理逻辑复杂**
   - 需要处理各种异常情况
   - 缓存策略、权限控制等逻辑复杂

## 🎯 使用场景总结

### 适合使用代理模式的场景：
- 🚀 **虚拟代理** - 延迟加载大对象，提高启动性能
- 🔒 **保护代理** - 权限控制，安全访问敏感资源
- 🌐 **远程代理** - 访问远程对象，网络透明性
- 🧠 **智能引用** - 引用计数、缓存、日志等附加功能
- 📊 **监控代理** - 性能监控、访问统计

### 不适合使用代理模式的场景：
- 简单对象，无需控制访问
- 性能要求极高，不能承受额外开销
- 对象创建成本很低的场景
- 不需要额外功能的直接访问

## 🧠 记忆技巧

### 形象比喻
> **代理模式就像是 "房产中介"**：
> - 买家不直接接触房主（客户端不直接访问真实对象）
> - 中介代表房主处理事务（代理控制访问）
> - 中介可以筛选客户（权限控制）
> - 中介可以提供额外服务（附加功能）

### 设计要点
> **"代理控制，透明访问，按需创建，智能增强"**

### 与装饰模式的区别
- **代理模式**：控制访问，通常不改变接口功能
- **装饰模式**：增强功能，动态添加新行为

## 🔧 最佳实践

### 1. 动态代理实现

```java
/**
 * 使用JDK动态代理
 */
public class DynamicProxy implements InvocationHandler {
    private Object target;

    public DynamicProxy(Object target) {
        this.target = target;
    }

    public static Object createProxy(Object target) {
        return Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            new DynamicProxy(target)
        );
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 前置处理
        System.out.println("调用方法: " + method.getName());
        long startTime = System.currentTimeMillis();

        try {
            // 调用真实方法
            Object result = method.invoke(target, args);

            // 后置处理
            long endTime = System.currentTimeMillis();
            System.out.println("方法执行耗时: " + (endTime - startTime) + "ms");

            return result;
        } catch (Exception e) {
            System.out.println("方法执行异常: " + e.getMessage());
            throw e;
        }
    }
}
```

### 2. 代理工厂模式

```java
/**
 * 代理工厂
 */
public class ProxyFactory {
    public static <T> T createProxy(T target, ProxyType type) {
        switch (type) {
            case VIRTUAL:
                return createVirtualProxy(target);
            case PROTECTION:
                return createProtectionProxy(target);
            case REMOTE:
                return createRemoteProxy(target);
            default:
                return target;
        }
    }

    private static <T> T createVirtualProxy(T target) {
        // 创建虚拟代理逻辑
        return (T) DynamicProxy.createProxy(target);
    }

    // 其他代理创建方法...
}

enum ProxyType {
    VIRTUAL, PROTECTION, REMOTE, SMART
}
```

### 3. 代理链模式

```java
/**
 * 代理链 - 多个代理组合
 */
public class ProxyChain {
    private List<ProxyHandler> handlers = new ArrayList<>();

    public ProxyChain addHandler(ProxyHandler handler) {
        handlers.add(handler);
        return this;
    }

    public Object execute(Object target, Method method, Object[] args) throws Throwable {
        return executeChain(0, target, method, args);
    }

    private Object executeChain(int index, Object target, Method method, Object[] args)
            throws Throwable {
        if (index >= handlers.size()) {
            return method.invoke(target, args);
        }

        ProxyHandler handler = handlers.get(index);
        return handler.handle(target, method, args, () -> executeChain(index + 1, target, method, args));
    }
}
```

## 🚀 总结

代理模式通过为其他对象提供代理来控制对这个对象的访问，特别适用于：

- **需要控制访问**的场景
- **延迟初始化**的需求
- **远程对象访问**的情况
- **需要附加功能**的场景

核心思想：
- **控制访问权限**
- **提供透明的代理服务**
- **在不改变接口的前提下增强功能**

设计要点：
- **代理与真实对象实现相同接口**
- **合理选择代理类型**
- **处理好异常和边界情况**

记住，**代理模式是访问控制器，不是功能增强器**，要在合适的访问控制场景下使用！

---

## 🎯 结构型模式总结

至此，我们已经完成了所有7种结构型模式的学习：

1. **适配器模式** - 让不兼容的接口协同工作
2. **桥接模式** - 抽象与实现的分离艺术
3. **组合模式** - 树形结构的统一处理
4. **装饰器模式** - 动态扩展对象功能
5. **外观模式** - 简化复杂子系统的访问
6. **享元模式** - 高效共享相似对象
7. **代理模式** - 控制对象访问的智能代理

这些模式都专注于**如何组合类和对象**以获得更大的结构，为构建灵活、可维护的软件架构提供了强有力的工具！

*下一篇：命令模式 - 行为型模式的开端*