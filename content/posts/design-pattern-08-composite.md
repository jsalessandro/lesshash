---
title: "设计模式详解：组合模式(Composite) - 树形结构的统一处理"
date: 2024-12-08T10:08:00+08:00
draft: false
tags: ["设计模式", "组合模式", "Composite", "Java", "结构型模式"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
author: "lesshash"
description: "深入浅出讲解组合模式，从基础概念到高级实现，包含树形结构、递归处理等实战技巧，让你彻底掌握层次结构的统一处理方案"
---

## 🎯 什么是组合模式？

### 生活中的例子
想象一下公司的**组织结构**：公司有多个部门，每个部门又有多个小组，每个小组又有多个员工。当CEO要统计全公司的人数时，不需要关心具体的层级结构，只需要问"你们有多少人？"，每个层级都会给出答案。部门会问小组，小组会问员工，最终汇总给出结果。这就是组合模式的核心思想：**将对象组合成树形结构，使客户端可以统一处理单个对象和组合对象**。

### 问题背景
在软件开发中，经常遇到树形结构的处理：
- 📁 **文件系统**：文件夹包含文件和子文件夹
- 🏢 **组织结构**：部门包含员工和子部门
- 🖥️ **GUI组件**：容器包含控件和子容器
- 📊 **表达式树**：复合表达式包含简单表达式和子表达式
- 🎮 **游戏场景**：场景节点包含物体和子节点

如果分别处理单个对象和组合对象，会导致：
- 客户端代码复杂
- 需要区分对象类型
- 违反开闭原则

## 🧠 设计思想

### 核心角色
1. **Component（组件）** - 定义统一接口
2. **Leaf（叶子节点）** - 表示单个对象，无子节点
3. **Composite（复合节点）** - 表示组合对象，包含子节点
4. **Client（客户端）** - 通过Component接口操作对象

### 核心思想
- 统一单个对象和组合对象的接口
- 递归组合形成树形结构
- 客户端透明地处理整个层次结构

### 记忆口诀
> **"部分整体同接口，树形结构递归妙"**

## 💻 代码实现

### 1. 基础组合模式 - 文件系统

```java
/**
 * 抽象组件 - 文件系统组件
 */
public abstract class FileSystemComponent {
    protected String name;

    public FileSystemComponent(String name) {
        this.name = name;
    }

    // 基本操作
    public abstract void display(int depth);
    public abstract long getSize();

    // 组合相关操作（默认抛出异常，只有Composite实现）
    public void add(FileSystemComponent component) {
        throw new UnsupportedOperationException("不支持添加操作");
    }

    public void remove(FileSystemComponent component) {
        throw new UnsupportedOperationException("不支持删除操作");
    }

    public FileSystemComponent getChild(int index) {
        throw new UnsupportedOperationException("不支持获取子组件操作");
    }

    // 通用方法
    public String getName() {
        return name;
    }

    protected String getIndent(int depth) {
        StringBuilder indent = new StringBuilder();
        for (int i = 0; i < depth; i++) {
            indent.append("  ");
        }
        return indent.toString();
    }
}

/**
 * 叶子节点 - 文件
 */
public class File extends FileSystemComponent {
    private long size;
    private String type;

    public File(String name, long size, String type) {
        super(name);
        this.size = size;
        this.type = type;
    }

    @Override
    public void display(int depth) {
        System.out.println(getIndent(depth) + "📄 " + name + " (" + formatSize(size) + ", " + type + ")");
    }

    @Override
    public long getSize() {
        return size;
    }

    private String formatSize(long bytes) {
        if (bytes < 1024) {
            return bytes + "B";
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024) + "KB";
        } else {
            return (bytes / (1024 * 1024)) + "MB";
        }
    }

    public String getType() {
        return type;
    }
}

/**
 * 复合节点 - 文件夹
 */
public class Directory extends FileSystemComponent {
    private List<FileSystemComponent> children;

    public Directory(String name) {
        super(name);
        this.children = new ArrayList<>();
    }

    @Override
    public void add(FileSystemComponent component) {
        children.add(component);
        System.out.println("📁 添加 " + component.getName() + " 到 " + this.name);
    }

    @Override
    public void remove(FileSystemComponent component) {
        children.remove(component);
        System.out.println("📁 从 " + this.name + " 删除 " + component.getName());
    }

    @Override
    public FileSystemComponent getChild(int index) {
        if (index >= 0 && index < children.size()) {
            return children.get(index);
        }
        throw new IndexOutOfBoundsException("索引超出范围: " + index);
    }

    @Override
    public void display(int depth) {
        System.out.println(getIndent(depth) + "📁 " + name + "/ (" + children.size() + " 项目, " + formatSize(getSize()) + ")");

        // 递归显示子组件
        for (FileSystemComponent child : children) {
            child.display(depth + 1);
        }
    }

    @Override
    public long getSize() {
        long totalSize = 0;
        // 递归计算所有子组件的大小
        for (FileSystemComponent child : children) {
            totalSize += child.getSize();
        }
        return totalSize;
    }

    public int getChildCount() {
        return children.size();
    }

    public List<FileSystemComponent> getChildren() {
        return new ArrayList<>(children); // 返回副本，保护内部数据
    }

    // 查找文件或文件夹
    public FileSystemComponent find(String name) {
        if (this.name.equals(name)) {
            return this;
        }

        for (FileSystemComponent child : children) {
            if (child.getName().equals(name)) {
                return child;
            }
            // 如果是目录，递归查找
            if (child instanceof Directory) {
                FileSystemComponent found = ((Directory) child).find(name);
                if (found != null) {
                    return found;
                }
            }
        }
        return null;
    }

    private String formatSize(long bytes) {
        if (bytes < 1024) {
            return bytes + "B";
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024) + "KB";
        } else {
            return (bytes / (1024 * 1024)) + "MB";
        }
    }
}

// 文件系统组合模式演示
public class FileSystemCompositeDemo {
    public static void main(String[] args) {
        System.out.println("=== 文件系统组合模式演示 ===");

        // 创建根目录
        Directory root = new Directory("root");

        // 创建文件
        File readme = new File("README.md", 2048, "Markdown");
        File config = new File("config.json", 512, "JSON");

        // 创建子目录
        Directory src = new Directory("src");
        Directory docs = new Directory("docs");

        // 根目录添加文件和子目录
        root.add(readme);
        root.add(config);
        root.add(src);
        root.add(docs);

        // src目录添加文件
        File mainJava = new File("Main.java", 4096, "Java");
        File utilJava = new File("Util.java", 2048, "Java");
        src.add(mainJava);
        src.add(utilJava);

        // src目录添加子目录
        Directory models = new Directory("models");
        File userModel = new File("User.java", 1024, "Java");
        File orderModel = new File("Order.java", 1536, "Java");
        models.add(userModel);
        models.add(orderModel);
        src.add(models);

        // docs目录添加文件
        File userGuide = new File("user-guide.pdf", 1048576, "PDF"); // 1MB
        File apiDoc = new File("api-doc.html", 8192, "HTML");
        docs.add(userGuide);
        docs.add(apiDoc);

        System.out.println("\n=== 文件系统结构 ===");
        root.display(0);

        System.out.println("\n=== 大小统计 ===");
        System.out.println("根目录总大小: " + formatSize(root.getSize()));
        System.out.println("src目录大小: " + formatSize(src.getSize()));
        System.out.println("docs目录大小: " + formatSize(docs.getSize()));

        System.out.println("\n=== 查找功能 ===");
        FileSystemComponent found = root.find("models");
        if (found != null) {
            System.out.println("找到了: " + found.getName());
            found.display(0);
        }

        System.out.println("\n=== 删除操作 ===");
        src.remove(utilJava);
        System.out.println("删除文件后的src目录:");
        src.display(0);

        System.out.println("\n观察：无论是文件还是文件夹，都可以用统一的方式处理！");
    }

    private static String formatSize(long bytes) {
        if (bytes < 1024) {
            return bytes + "B";
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024) + "KB";
        } else {
            return (bytes / (1024 * 1024)) + "MB";
        }
    }
}
```

### 2. 组织结构组合模式

```java
/**
 * 抽象组件 - 组织结构组件
 */
public abstract class OrganizationComponent {
    protected String name;
    protected String position;
    protected double salary;

    public OrganizationComponent(String name, String position, double salary) {
        this.name = name;
        this.position = position;
        this.salary = salary;
    }

    // 基本操作
    public abstract void showInfo(int depth);
    public abstract double getTotalSalary();
    public abstract int getEmployeeCount();

    // 组合相关操作
    public void add(OrganizationComponent component) {
        throw new UnsupportedOperationException("不支持添加操作");
    }

    public void remove(OrganizationComponent component) {
        throw new UnsupportedOperationException("不支持删除操作");
    }

    // 通用方法
    public String getName() { return name; }
    public String getPosition() { return position; }
    public double getSalary() { return salary; }

    protected String getIndent(int depth) {
        StringBuilder indent = new StringBuilder();
        for (int i = 0; i < depth; i++) {
            indent.append("  ");
        }
        return indent.toString();
    }
}

/**
 * 叶子节点 - 员工
 */
public class Employee extends OrganizationComponent {
    private String department;
    private String email;

    public Employee(String name, String position, double salary, String department, String email) {
        super(name, position, salary);
        this.department = department;
        this.email = email;
    }

    @Override
    public void showInfo(int depth) {
        System.out.println(getIndent(depth) + "👤 " + name + " | " + position +
                          " | ¥" + String.format("%.0f", salary) +
                          " | " + department + " | " + email);
    }

    @Override
    public double getTotalSalary() {
        return salary;
    }

    @Override
    public int getEmployeeCount() {
        return 1;
    }

    public String getDepartment() { return department; }
    public String getEmail() { return email; }
}

/**
 * 复合节点 - 部门
 */
public class Department extends OrganizationComponent {
    private List<OrganizationComponent> members;
    private String description;

    public Department(String name, String position, double salary, String description) {
        super(name, position, salary);
        this.members = new ArrayList<>();
        this.description = description;
    }

    @Override
    public void add(OrganizationComponent component) {
        members.add(component);
        System.out.println("🏢 " + component.getName() + " 加入了 " + this.name);
    }

    @Override
    public void remove(OrganizationComponent component) {
        members.remove(component);
        System.out.println("🏢 " + component.getName() + " 离开了 " + this.name);
    }

    @Override
    public void showInfo(int depth) {
        System.out.println(getIndent(depth) + "🏢 " + name + " | " + position +
                          " | ¥" + String.format("%.0f", salary) +
                          " | 成员: " + getEmployeeCount() +
                          " | 总薪资: ¥" + String.format("%.0f", getTotalSalary()));
        System.out.println(getIndent(depth) + "   描述: " + description);

        // 递归显示所有成员
        for (OrganizationComponent member : members) {
            member.showInfo(depth + 1);
        }
    }

    @Override
    public double getTotalSalary() {
        double total = salary; // 部门负责人的薪资
        // 递归计算所有成员的薪资
        for (OrganizationComponent member : members) {
            total += member.getTotalSalary();
        }
        return total;
    }

    @Override
    public int getEmployeeCount() {
        int count = 1; // 部门负责人算一个员工
        // 递归计算所有成员数量
        for (OrganizationComponent member : members) {
            count += member.getEmployeeCount();
        }
        return count;
    }

    public String getDescription() { return description; }

    public List<OrganizationComponent> getMembers() {
        return new ArrayList<>(members);
    }

    // 按职位查找员工
    public List<OrganizationComponent> findByPosition(String position) {
        List<OrganizationComponent> result = new ArrayList<>();

        if (this.position.equals(position)) {
            result.add(this);
        }

        for (OrganizationComponent member : members) {
            if (member.getPosition().equals(position)) {
                result.add(member);
            }
            // 如果是部门，递归查找
            if (member instanceof Department) {
                result.addAll(((Department) member).findByPosition(position));
            }
        }
        return result;
    }

    // 计算平均薪资
    public double getAverageSalary() {
        return getTotalSalary() / getEmployeeCount();
    }
}

// 组织结构组合模式演示
public class OrganizationCompositeDemo {
    public static void main(String[] args) {
        System.out.println("=== 组织结构组合模式演示 ===");

        // 创建公司总部
        Department company = new Department("科技有限公司", "CEO", 50000, "专注于软件开发的科技公司");

        // 创建技术部门
        Department techDept = new Department("技术部", "技术总监", 30000, "负责产品研发和技术创新");

        // 技术部员工
        Employee frontendDev = new Employee("张三", "前端工程师", 15000, "技术部", "zhangsan@company.com");
        Employee backendDev = new Employee("李四", "后端工程师", 18000, "技术部", "lisi@company.com");
        Employee qaEngineer = new Employee("王五", "测试工程师", 12000, "技术部", "wangwu@company.com");

        techDept.add(frontendDev);
        techDept.add(backendDev);
        techDept.add(qaEngineer);

        // 创建产品部门
        Department productDept = new Department("产品部", "产品总监", 25000, "负责产品设计和用户体验");

        Employee productManager = new Employee("赵六", "产品经理", 20000, "产品部", "zhaoliu@company.com");
        Employee uiDesigner = new Employee("孙七", "UI设计师", 14000, "产品部", "sunqi@company.com");

        productDept.add(productManager);
        productDept.add(uiDesigner);

        // 创建销售部门
        Department salesDept = new Department("销售部", "销售总监", 28000, "负责市场开拓和客户维护");

        Employee salesManager = new Employee("周八", "销售经理", 16000, "销售部", "zhouba@company.com");
        Employee salesRep = new Employee("吴九", "销售代表", 10000, "销售部", "wujiu@company.com");

        salesDept.add(salesManager);
        salesDept.add(salesRep);

        // 在技术部下创建子部门
        Department frontendTeam = new Department("前端小组", "前端主管", 22000, "负责前端开发和维护");
        Employee seniorFrontend = new Employee("陈十", "高级前端工程师", 20000, "前端小组", "chenshi@company.com");
        Employee juniorFrontend = new Employee("林一", "初级前端工程师", 8000, "前端小组", "linyi@company.com");

        frontendTeam.add(seniorFrontend);
        frontendTeam.add(juniorFrontend);
        techDept.add(frontendTeam);

        // 将各部门加入公司
        company.add(techDept);
        company.add(productDept);
        company.add(salesDept);

        System.out.println("\n=== 公司组织结构 ===");
        company.showInfo(0);

        System.out.println("\n=== 薪资统计 ===");
        System.out.println("公司总薪资: ¥" + String.format("%.0f", company.getTotalSalary()));
        System.out.println("公司总人数: " + company.getEmployeeCount() + " 人");
        System.out.println("公司平均薪资: ¥" + String.format("%.0f", company.getAverageSalary()));

        System.out.println("\n各部门薪资统计:");
        System.out.println("技术部 - 总薪资: ¥" + String.format("%.0f", techDept.getTotalSalary()) +
                          ", 人数: " + techDept.getEmployeeCount() +
                          ", 平均: ¥" + String.format("%.0f", techDept.getAverageSalary()));

        System.out.println("产品部 - 总薪资: ¥" + String.format("%.0f", productDept.getTotalSalary()) +
                          ", 人数: " + productDept.getEmployeeCount() +
                          ", 平均: ¥" + String.format("%.0f", productDept.getAverageSalary()));

        System.out.println("销售部 - 总薪资: ¥" + String.format("%.0f", salesDept.getTotalSalary()) +
                          ", 人数: " + salesDept.getEmployeeCount() +
                          ", 平均: ¥" + String.format("%.0f", salesDept.getAverageSalary()));

        System.out.println("\n=== 按职位查找 ===");
        List<OrganizationComponent> engineers = company.findByPosition("前端工程师");
        System.out.println("前端工程师人员:");
        for (OrganizationComponent engineer : engineers) {
            engineer.showInfo(0);
        }

        List<OrganizationComponent> managers = company.findByPosition("产品经理");
        System.out.println("\n产品经理人员:");
        for (OrganizationComponent manager : managers) {
            manager.showInfo(0);
        }

        System.out.println("\n=== 部门调整 ===");
        System.out.println("李四从技术部转到前端小组:");
        techDept.remove(backendDev);
        frontendTeam.add(backendDev);

        System.out.println("\n调整后的技术部结构:");
        techDept.showInfo(0);

        System.out.println("\n观察：无论是员工还是部门，都可以用统一的方式进行管理！");
    }
}
```

### 3. GUI组件组合模式

```java
/**
 * 抽象组件 - GUI组件
 */
public abstract class GUIComponent {
    protected String name;
    protected int x, y, width, height;
    protected boolean visible;

    public GUIComponent(String name, int x, int y, int width, int height) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.visible = true;
    }

    // 基本操作
    public abstract void render();
    public abstract void handleClick(int mouseX, int mouseY);

    // 组合相关操作
    public void add(GUIComponent component) {
        throw new UnsupportedOperationException("不支持添加子组件");
    }

    public void remove(GUIComponent component) {
        throw new UnsupportedOperationException("不支持删除子组件");
    }

    // 通用方法
    public void setVisible(boolean visible) {
        this.visible = visible;
        System.out.println(name + (visible ? " 显示" : " 隐藏"));
    }

    public void move(int newX, int newY) {
        this.x = newX;
        this.y = newY;
        System.out.println(name + " 移动到 (" + x + ", " + y + ")");
    }

    public void resize(int newWidth, int newHeight) {
        this.width = newWidth;
        this.height = newHeight;
        System.out.println(name + " 调整大小为 " + width + "×" + height);
    }

    public boolean isPointInside(int pointX, int pointY) {
        return pointX >= x && pointX <= x + width && pointY >= y && pointY <= y + height;
    }

    // getter方法
    public String getName() { return name; }
    public boolean isVisible() { return visible; }

    protected String getIndent(int depth) {
        StringBuilder indent = new StringBuilder();
        for (int i = 0; i < depth; i++) {
            indent.append("  ");
        }
        return indent.toString();
    }
}

/**
 * 叶子节点 - 按钮
 */
public class Button extends GUIComponent {
    private String text;
    private String color;

    public Button(String name, int x, int y, int width, int height, String text, String color) {
        super(name, x, y, width, height);
        this.text = text;
        this.color = color;
    }

    @Override
    public void render() {
        if (visible) {
            System.out.println("🔘 渲染按钮: " + name + " | 位置(" + x + "," + y + ") | 大小" + width + "×" + height +
                             " | 文本: \"" + text + "\" | 颜色: " + color);
        }
    }

    @Override
    public void handleClick(int mouseX, int mouseY) {
        if (visible && isPointInside(mouseX, mouseY)) {
            System.out.println("🖱️ 按钮 \"" + text + "\" 被点击！");
            onClick();
        }
    }

    public void onClick() {
        System.out.println("   ✨ 执行按钮动作: " + text);
    }

    public void setText(String text) {
        this.text = text;
        System.out.println("🔘 按钮 " + name + " 文本更新为: \"" + text + "\"");
    }

    public String getText() { return text; }
}

/**
 * 叶子节点 - 文本框
 */
public class TextBox extends GUIComponent {
    private String content;
    private boolean editable;

    public TextBox(String name, int x, int y, int width, int height, boolean editable) {
        super(name, x, y, width, height);
        this.content = "";
        this.editable = editable;
    }

    @Override
    public void render() {
        if (visible) {
            System.out.println("📝 渲染文本框: " + name + " | 位置(" + x + "," + y + ") | 大小" + width + "×" + height +
                             " | 内容: \"" + content + "\" | " + (editable ? "可编辑" : "只读"));
        }
    }

    @Override
    public void handleClick(int mouseX, int mouseY) {
        if (visible && isPointInside(mouseX, mouseY)) {
            if (editable) {
                System.out.println("📝 文本框 " + name + " 获得焦点，可以输入文本");
            } else {
                System.out.println("📝 只读文本框 " + name + " 被点击");
            }
        }
    }

    public void setContent(String content) {
        if (editable) {
            this.content = content;
            System.out.println("📝 文本框 " + name + " 内容更新为: \"" + content + "\"");
        } else {
            System.out.println("❌ 文本框 " + name + " 为只读，无法修改内容");
        }
    }

    public String getContent() { return content; }
}

/**
 * 复合节点 - 面板（容器）
 */
public class Panel extends GUIComponent {
    private List<GUIComponent> children;
    private String backgroundColor;

    public Panel(String name, int x, int y, int width, int height, String backgroundColor) {
        super(name, x, y, width, height);
        this.children = new ArrayList<>();
        this.backgroundColor = backgroundColor;
    }

    @Override
    public void add(GUIComponent component) {
        children.add(component);
        System.out.println("📋 组件 " + component.getName() + " 添加到面板 " + name);
    }

    @Override
    public void remove(GUIComponent component) {
        children.remove(component);
        System.out.println("📋 组件 " + component.getName() + " 从面板 " + name + " 移除");
    }

    @Override
    public void render() {
        if (visible) {
            System.out.println("📋 渲染面板: " + name + " | 位置(" + x + "," + y + ") | 大小" + width + "×" + height +
                             " | 背景: " + backgroundColor + " | 子组件数: " + children.size());

            // 递归渲染所有子组件
            for (GUIComponent child : children) {
                child.render();
            }
        }
    }

    @Override
    public void handleClick(int mouseX, int mouseY) {
        if (visible && isPointInside(mouseX, mouseY)) {
            System.out.println("📋 面板 " + name + " 被点击");

            // 将点击事件传递给子组件（从上到下查找）
            for (int i = children.size() - 1; i >= 0; i--) {
                children.get(i).handleClick(mouseX, mouseY);
            }
        }
    }

    public List<GUIComponent> getChildren() {
        return new ArrayList<>(children);
    }

    public void setBackgroundColor(String backgroundColor) {
        this.backgroundColor = backgroundColor;
        System.out.println("📋 面板 " + name + " 背景色更改为: " + backgroundColor);
    }

    // 查找子组件
    public GUIComponent findComponent(String name) {
        if (this.name.equals(name)) {
            return this;
        }

        for (GUIComponent child : children) {
            if (child.getName().equals(name)) {
                return child;
            }
            // 如果是面板，递归查找
            if (child instanceof Panel) {
                GUIComponent found = ((Panel) child).findComponent(name);
                if (found != null) {
                    return found;
                }
            }
        }
        return null;
    }

    // 设置所有子组件的可见性
    @Override
    public void setVisible(boolean visible) {
        super.setVisible(visible);
        for (GUIComponent child : children) {
            child.setVisible(visible);
        }
    }
}

/**
 * 复合节点 - 窗口
 */
public class Window extends Panel {
    private String title;
    private boolean resizable;

    public Window(String name, int x, int y, int width, int height, String title) {
        super(name, x, y, width, height, "white");
        this.title = title;
        this.resizable = true;
    }

    @Override
    public void render() {
        if (visible) {
            System.out.println("🪟 渲染窗口: " + title + " | 位置(" + x + "," + y + ") | 大小" + width + "×" + height);
            System.out.println("   窗口标题栏: " + title);
            System.out.println("   窗口内容区域:");

            // 渲染子组件（缩进显示）
            for (GUIComponent child : getChildren()) {
                child.render();
            }
        }
    }

    public void setTitle(String title) {
        this.title = title;
        System.out.println("🪟 窗口标题更新为: " + title);
    }

    public String getTitle() { return title; }
}

// GUI组件组合模式演示
public class GUICompositeDemo {
    public static void main(String[] args) {
        System.out.println("=== GUI组件组合模式演示 ===");

        // 创建主窗口
        Window mainWindow = new Window("mainWindow", 100, 100, 800, 600, "用户管理系统");

        // 创建顶部工具栏面板
        Panel toolbarPanel = new Panel("toolbar", 0, 0, 800, 50, "lightgray");
        Button newButton = new Button("newBtn", 10, 10, 80, 30, "新建", "blue");
        Button saveButton = new Button("saveBtn", 100, 10, 80, 30, "保存", "green");
        Button deleteButton = new Button("deleteBtn", 190, 10, 80, 30, "删除", "red");

        toolbarPanel.add(newButton);
        toolbarPanel.add(saveButton);
        toolbarPanel.add(deleteButton);

        // 创建左侧导航面板
        Panel navPanel = new Panel("navigation", 0, 50, 200, 550, "lightblue");
        Button usersButton = new Button("usersBtn", 10, 60, 180, 40, "用户管理", "gray");
        Button ordersButton = new Button("ordersBtn", 10, 110, 180, 40, "订单管理", "gray");
        Button reportsButton = new Button("reportsBtn", 10, 160, 180, 40, "报表统计", "gray");

        navPanel.add(usersButton);
        navPanel.add(ordersButton);
        navPanel.add(reportsButton);

        // 创建主内容面板
        Panel contentPanel = new Panel("content", 200, 50, 600, 550, "white");

        // 用户信息表单面板
        Panel userFormPanel = new Panel("userForm", 20, 20, 560, 300, "lightgray");
        TextBox nameTextBox = new TextBox("nameInput", 100, 30, 200, 25, true);
        TextBox emailTextBox = new TextBox("emailInput", 100, 70, 200, 25, true);
        TextBox phoneTextBox = new TextBox("phoneInput", 100, 110, 200, 25, true);

        nameTextBox.setContent("张三");
        emailTextBox.setContent("zhangsan@example.com");
        phoneTextBox.setContent("138****1234");

        userFormPanel.add(nameTextBox);
        userFormPanel.add(emailTextBox);
        userFormPanel.add(phoneTextBox);

        // 表单操作按钮
        Panel formButtonPanel = new Panel("formButtons", 20, 350, 560, 60, "lightgray");
        Button submitButton = new Button("submitBtn", 200, 15, 80, 30, "提交", "green");
        Button cancelButton = new Button("cancelBtn", 290, 15, 80, 30, "取消", "gray");

        formButtonPanel.add(submitButton);
        formButtonPanel.add(cancelButton);

        contentPanel.add(userFormPanel);
        contentPanel.add(formButtonPanel);

        // 将所有面板添加到主窗口
        mainWindow.add(toolbarPanel);
        mainWindow.add(navPanel);
        mainWindow.add(contentPanel);

        System.out.println("\n=== 渲染整个GUI界面 ===");
        mainWindow.render();

        System.out.println("\n=== 模拟鼠标点击事件 ===");
        System.out.println("点击保存按钮:");
        mainWindow.handleClick(140, 25); // 点击保存按钮

        System.out.println("\n点击用户管理按钮:");
        mainWindow.handleClick(100, 80); // 点击用户管理按钮

        System.out.println("\n点击姓名输入框:");
        mainWindow.handleClick(200, 55); // 点击姓名输入框

        System.out.println("\n点击提交按钮:");
        mainWindow.handleClick(240, 365); // 点击提交按钮

        System.out.println("\n=== 组件查找功能 ===");
        GUIComponent foundComponent = mainWindow.findComponent("emailInput");
        if (foundComponent instanceof TextBox) {
            TextBox emailBox = (TextBox) foundComponent;
            System.out.println("找到邮箱输入框，当前内容: \"" + emailBox.getContent() + "\"");
            emailBox.setContent("newemail@example.com");
        }

        System.out.println("\n=== 动态修改界面 ===");
        System.out.println("隐藏删除按钮:");
        deleteButton.setVisible(false);

        System.out.println("\n更改窗口标题:");
        mainWindow.setTitle("用户管理系统 v2.0");

        System.out.println("\n移动提交按钮:");
        submitButton.move(150, 15);

        System.out.println("\n=== 批量操作 ===");
        System.out.println("隐藏整个表单面板（包括所有子组件）:");
        userFormPanel.setVisible(false);

        System.out.println("\n重新显示表单面板:");
        userFormPanel.setVisible(true);

        System.out.println("\n观察：无论是单个组件还是容器，都可以用统一的方式处理！");
    }
}
```

## 🌟 实际应用场景

### 1. 表达式计算器

```java
/**
 * 抽象表达式组件
 */
public abstract class Expression {
    public abstract double evaluate();
    public abstract String toString();

    // 组合相关操作
    public void add(Expression expression) {
        throw new UnsupportedOperationException("不支持添加子表达式");
    }

    public void remove(Expression expression) {
        throw new UnsupportedOperationException("不支持删除子表达式");
    }
}

/**
 * 叶子节点 - 数字
 */
public class Number extends Expression {
    private double value;

    public Number(double value) {
        this.value = value;
    }

    @Override
    public double evaluate() {
        return value;
    }

    @Override
    public String toString() {
        // 如果是整数，不显示小数点
        if (value == (int) value) {
            return String.valueOf((int) value);
        }
        return String.valueOf(value);
    }

    public double getValue() {
        return value;
    }
}

/**
 * 叶子节点 - 变量
 */
public class Variable extends Expression {
    private String name;
    private static Map<String, Double> variables = new HashMap<>();

    public Variable(String name) {
        this.name = name;
    }

    @Override
    public double evaluate() {
        Double value = variables.get(name);
        if (value == null) {
            throw new RuntimeException("未定义的变量: " + name);
        }
        return value;
    }

    @Override
    public String toString() {
        return name;
    }

    public static void setValue(String name, double value) {
        variables.put(name, value);
        System.out.println("设置变量 " + name + " = " + value);
    }

    public static void clearVariables() {
        variables.clear();
    }

    public String getName() {
        return name;
    }
}

/**
 * 复合节点 - 二元操作表达式
 */
public class BinaryOperation extends Expression {
    private Expression left;
    private Expression right;
    private String operator;

    public BinaryOperation(Expression left, String operator, Expression right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    @Override
    public double evaluate() {
        double leftValue = left.evaluate();
        double rightValue = right.evaluate();

        switch (operator) {
            case "+":
                return leftValue + rightValue;
            case "-":
                return leftValue - rightValue;
            case "*":
                return leftValue * rightValue;
            case "/":
                if (rightValue == 0) {
                    throw new RuntimeException("除零错误");
                }
                return leftValue / rightValue;
            case "^":
                return Math.pow(leftValue, rightValue);
            default:
                throw new RuntimeException("不支持的运算符: " + operator);
        }
    }

    @Override
    public String toString() {
        // 根据运算符优先级决定是否需要括号
        return "(" + left.toString() + " " + operator + " " + right.toString() + ")";
    }

    public Expression getLeft() { return left; }
    public Expression getRight() { return right; }
    public String getOperator() { return operator; }
}

/**
 * 复合节点 - 一元操作表达式
 */
public class UnaryOperation extends Expression {
    private Expression operand;
    private String operator;

    public UnaryOperation(String operator, Expression operand) {
        this.operator = operator;
        this.operand = operand;
    }

    @Override
    public double evaluate() {
        double value = operand.evaluate();

        switch (operator) {
            case "-":
                return -value;
            case "+":
                return value;
            case "sin":
                return Math.sin(value);
            case "cos":
                return Math.cos(value);
            case "sqrt":
                if (value < 0) {
                    throw new RuntimeException("负数不能开平方根");
                }
                return Math.sqrt(value);
            case "log":
                if (value <= 0) {
                    throw new RuntimeException("对数的真数必须大于0");
                }
                return Math.log(value);
            default:
                throw new RuntimeException("不支持的一元运算符: " + operator);
        }
    }

    @Override
    public String toString() {
        if (operator.equals("-") || operator.equals("+")) {
            return operator + operand.toString();
        } else {
            return operator + "(" + operand.toString() + ")";
        }
    }

    public Expression getOperand() { return operand; }
    public String getOperator() { return operator; }
}

/**
 * 表达式构建器
 */
public class ExpressionBuilder {
    public static Expression buildComplexExpression() {
        // 构建表达式: (x + 2) * sqrt(y) - sin(z^2)

        Variable x = new Variable("x");
        Number two = new Number(2);
        Expression xPlus2 = new BinaryOperation(x, "+", two);

        Variable y = new Variable("y");
        Expression sqrtY = new UnaryOperation("sqrt", y);

        Expression leftPart = new BinaryOperation(xPlus2, "*", sqrtY);

        Variable z = new Variable("z");
        Number zPower = new Number(2);
        Expression zSquared = new BinaryOperation(z, "^", zPower);
        Expression sinZSquared = new UnaryOperation("sin", zSquared);

        return new BinaryOperation(leftPart, "-", sinZSquared);
    }

    public static Expression buildSimpleExpression() {
        // 构建表达式: 3 + 4 * 2
        Number three = new Number(3);
        Number four = new Number(4);
        Number two = new Number(2);

        Expression fourTimesTwo = new BinaryOperation(four, "*", two);
        return new BinaryOperation(three, "+", fourTimesTwo);
    }

    public static Expression buildPolynomial() {
        // 构建多项式: 2*x^3 + 3*x^2 - 5*x + 7
        Variable x = new Variable("x");

        // 2*x^3
        Number two = new Number(2);
        Number three = new Number(3);
        Expression xCubed = new BinaryOperation(x, "^", three);
        Expression term1 = new BinaryOperation(two, "*", xCubed);

        // 3*x^2
        Number three2 = new Number(3);
        Number two2 = new Number(2);
        Expression xSquared = new BinaryOperation(x, "^", two2);
        Expression term2 = new BinaryOperation(three2, "*", xSquared);

        // -5*x
        Number five = new Number(5);
        Expression fiveX = new BinaryOperation(five, "*", x);
        Expression term3 = new UnaryOperation("-", fiveX);

        // 常数项 7
        Number seven = new Number(7);

        // 组合所有项
        Expression part1 = new BinaryOperation(term1, "+", term2);
        Expression part2 = new BinaryOperation(part1, "+", term3);
        return new BinaryOperation(part2, "+", seven);
    }
}

// 表达式计算器演示
public class ExpressionCompositeDemo {
    public static void main(String[] args) {
        System.out.println("=== 表达式计算器组合模式演示 ===");

        System.out.println("\n=== 简单表达式计算 ===");
        Expression simpleExpr = ExpressionBuilder.buildSimpleExpression();
        System.out.println("表达式: " + simpleExpr);
        System.out.println("计算结果: " + simpleExpr.evaluate());

        System.out.println("\n=== 复杂表达式计算 ===");
        // 设置变量值
        Variable.setValue("x", 5);
        Variable.setValue("y", 16);
        Variable.setValue("z", Math.PI / 4);

        Expression complexExpr = ExpressionBuilder.buildComplexExpression();
        System.out.println("表达式: " + complexExpr);
        System.out.println("当 x=5, y=16, z=π/4 时:");
        try {
            double result = complexExpr.evaluate();
            System.out.println("计算结果: " + String.format("%.4f", result));
        } catch (RuntimeException e) {
            System.out.println("计算错误: " + e.getMessage());
        }

        System.out.println("\n=== 多项式计算 ===");
        Expression polynomial = ExpressionBuilder.buildPolynomial();
        System.out.println("多项式: " + polynomial);

        // 计算不同x值下的结果
        double[] xValues = {0, 1, 2, -1, 0.5};
        for (double xValue : xValues) {
            Variable.setValue("x", xValue);
            double result = polynomial.evaluate();
            System.out.println("x = " + xValue + " 时，结果 = " + String.format("%.2f", result));
        }

        System.out.println("\n=== 手动构建表达式 ===");
        // 构建 (a + b) / (c - d)
        Variable a = new Variable("a");
        Variable b = new Variable("b");
        Variable c = new Variable("c");
        Variable d = new Variable("d");

        Variable.setValue("a", 10);
        Variable.setValue("b", 5);
        Variable.setValue("c", 8);
        Variable.setValue("d", 3);

        Expression numerator = new BinaryOperation(a, "+", b);
        Expression denominator = new BinaryOperation(c, "-", d);
        Expression fraction = new BinaryOperation(numerator, "/", denominator);

        System.out.println("表达式: " + fraction);
        System.out.println("当 a=10, b=5, c=8, d=3 时:");
        System.out.println("计算结果: " + fraction.evaluate());

        System.out.println("\n=== 错误处理演示 ===");
        // 除零错误
        Variable.setValue("d", 8); // 让分母为0
        System.out.println("设置 d=8，使分母为0:");
        try {
            double result = fraction.evaluate();
            System.out.println("结果: " + result);
        } catch (RuntimeException e) {
            System.out.println("错误: " + e.getMessage());
        }

        // 未定义变量错误
        Variable.clearVariables();
        Variable undefinedVar = new Variable("undefined");
        System.out.println("\n使用未定义的变量:");
        try {
            double result = undefinedVar.evaluate();
            System.out.println("结果: " + result);
        } catch (RuntimeException e) {
            System.out.println("错误: " + e.getMessage());
        }

        System.out.println("\n=== 函数嵌套演示 ===");
        // sin(cos(x)) + sqrt(log(y))
        Variable.setValue("x", Math.PI / 3);
        Variable.setValue("y", Math.E);

        Variable x2 = new Variable("x");
        Variable y2 = new Variable("y");

        Expression cosX = new UnaryOperation("cos", x2);
        Expression sinCosX = new UnaryOperation("sin", cosX);

        Expression logY = new UnaryOperation("log", y2);
        Expression sqrtLogY = new UnaryOperation("sqrt", logY);

        Expression nested = new BinaryOperation(sinCosX, "+", sqrtLogY);

        System.out.println("嵌套函数表达式: " + nested);
        System.out.println("当 x=π/3, y=e 时:");
        System.out.println("计算结果: " + String.format("%.6f", nested.evaluate()));

        System.out.println("\n观察：无论是简单数字还是复杂表达式，都可以用统一的方式计算！");
    }
}
```

## ⚖️ 优缺点分析

### ✅ 优点

1. **统一接口**
   - 客户端可以一致地处理单个对象和组合对象
   - 简化客户端代码

2. **简化复杂性**
   - 将树形结构的复杂性隐藏在内部
   - 客户端不需要区分叶子和复合节点

3. **扩展性好**
   - 容易增加新的组件类型
   - 符合开闭原则

4. **递归处理**
   - 自然支持递归操作
   - 代码结构清晰

### ❌ 缺点

1. **设计复杂**
   - 抽象组件需要同时支持叶子和复合操作
   - 接口可能过于通用

2. **类型安全问题**
   - 难在编译时确保类型安全
   - 运行时才能发现不当操作

3. **性能开销**
   - 递归调用可能影响性能
   - 深层嵌套时尤其明显

## 🎯 使用场景总结

### 适合使用组合模式的场景：
- 📁 **文件系统** - 文件和文件夹的统一处理
- 🏢 **组织结构** - 员工和部门的统一管理
- 🖥️ **GUI组件** - 控件和容器的统一操作
- 📊 **表达式处理** - 简单和复合表达式的统一计算
- 🎮 **游戏场景树** - 游戏对象的层次化管理

### 不适合使用组合模式的场景：
- 结构简单，不需要层次化的系统
- 叶子节点和复合节点差异很大
- 性能要求极高，不能承受递归开销
- 需要严格类型检查的场景

## 🧠 记忆技巧

### 形象比喻
> **组合模式就像是 "公司组织结构"**：
> - 员工是叶子节点（不能再分解）
> - 部门是复合节点（包含员工和子部门）
> - 所有人都有统一的接口（汇报工作、计算薪资）
> - CEO不需要知道具体结构，只要调用统一方法

### 设计要点
> **"树形结构，统一接口，递归处理，透明操作"**

### 与装饰模式的区别
- **组合模式**：强调部分-整体关系，树形结构
- **装饰模式**：强调功能增强，链式结构

## 🔧 最佳实践

### 1. 安全性设计

```java
// 类型安全的组合模式设计
public abstract class SafeComponent {
    // 只在需要时提供组合操作
    public boolean isComposite() {
        return false;
    }

    public List<SafeComponent> getChildren() {
        if (!isComposite()) {
            throw new UnsupportedOperationException("叶子节点没有子组件");
        }
        return Collections.emptyList();
    }
}

public class SafeComposite extends SafeComponent {
    private List<SafeComponent> children = new ArrayList<>();

    @Override
    public boolean isComposite() {
        return true;
    }

    @Override
    public List<SafeComponent> getChildren() {
        return new ArrayList<>(children);
    }
}
```

### 2. 性能优化

```java
// 使用缓存优化递归计算
public abstract class CachedComponent {
    private Double cachedResult;
    private boolean resultValid = false;

    public final double getResult() {
        if (!resultValid) {
            cachedResult = calculateResult();
            resultValid = true;
        }
        return cachedResult;
    }

    protected abstract double calculateResult();

    public void invalidateCache() {
        resultValid = false;
        // 通知父组件也需要重新计算
    }
}
```

### 3. 访问者模式结合

```java
// 组合模式与访问者模式结合
public interface ComponentVisitor {
    void visitFile(File file);
    void visitDirectory(Directory directory);
}

public abstract class VisitableComponent {
    public abstract void accept(ComponentVisitor visitor);
}
```

## 🚀 总结

组合模式通过统一单个对象和组合对象的接口，让客户端可以透明地处理树形结构，特别适用于：

- **层次化结构**的系统
- **部分-整体关系**的场景
- **需要递归处理**的业务

核心思想：
- **统一接口处理**
- **递归组合结构**
- **客户端透明性**

设计要点：
- **合理的抽象组件设计**
- **区分叶子和复合操作**
- **考虑类型安全性**

记住，**组合模式是结构师，不是万能胶**，要在合适的树形结构场景下使用！

---
*下一篇：装饰器模式 - 动态扩展对象功能*