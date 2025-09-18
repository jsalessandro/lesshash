---
title: "设计模式入门教程19：访问者模式 - 在不修改类的情况下扩展功能"
date: 2024-12-19T10:19:00+08:00
draft: false
tags: ["设计模式", "访问者模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是访问者模式？

访问者模式（Visitor Pattern）是一种行为型设计模式，它让你能在不修改已有类的情况下，向类层次结构中加入新的行为。访问者模式将数据结构与数据操作分离，使得操作集合可相对自由地演化。

### 🌟 现实生活中的例子

想象一下**医院的检查流程**：
- **患者**：不同类型的患者（成人、儿童、老人）
- **医生**：不同科室的医生（内科、外科、儿科）
- **检查**：每个医生对不同患者有不同的检查方法
- **扩展**：新来一个专科医生，不需要修改患者类，只需要定义新的检查方法

又比如**文档处理系统**：
- **文档元素**：段落、图片、表格等
- **处理器**：打印处理器、导出处理器、格式化处理器
- **操作**：每个处理器对不同元素有不同的处理方式

这就是访问者模式的典型应用！

## 🏗️ 模式结构

```java
// 访问者接口
interface Visitor {
    void visitConcreteElementA(ConcreteElementA element);
    void visitConcreteElementB(ConcreteElementB element);
}

// 元素接口
interface Element {
    void accept(Visitor visitor);
}

// 具体元素A
class ConcreteElementA implements Element {
    @Override
    public void accept(Visitor visitor) {
        visitor.visitConcreteElementA(this);
    }

    public String getDataA() {
        return "Element A Data";
    }
}

// 具体元素B
class ConcreteElementB implements Element {
    @Override
    public void accept(Visitor visitor) {
        visitor.visitConcreteElementB(this);
    }

    public String getDataB() {
        return "Element B Data";
    }
}

// 具体访问者
class ConcreteVisitor implements Visitor {
    @Override
    public void visitConcreteElementA(ConcreteElementA element) {
        System.out.println("处理元素A：" + element.getDataA());
    }

    @Override
    public void visitConcreteElementB(ConcreteElementB element) {
        System.out.println("处理元素B：" + element.getDataB());
    }
}
```

## 💡 核心组件详解

### 1. 抽象访问者（Visitor）
```java
// 文档访问者接口
interface DocumentVisitor {
    void visitParagraph(Paragraph paragraph);
    void visitImage(Image image);
    void visitTable(Table table);
    void visitHeader(Header header);
}
```

### 2. 具体访问者（ConcreteVisitor）
```java
// HTML导出访问者
class HtmlExportVisitor implements DocumentVisitor {
    private StringBuilder html = new StringBuilder();

    @Override
    public void visitParagraph(Paragraph paragraph) {
        html.append("<p>").append(paragraph.getText()).append("</p>\n");
        System.out.println("导出段落为HTML：" + paragraph.getText());
    }

    @Override
    public void visitImage(Image image) {
        html.append("<img src=\"").append(image.getPath()).append("\" alt=\"")
            .append(image.getAlt()).append("\" />\n");
        System.out.println("导出图片为HTML：" + image.getPath());
    }

    @Override
    public void visitTable(Table table) {
        html.append("<table>\n");
        for (String[] row : table.getRows()) {
            html.append("  <tr>\n");
            for (String cell : row) {
                html.append("    <td>").append(cell).append("</td>\n");
            }
            html.append("  </tr>\n");
        }
        html.append("</table>\n");
        System.out.println("导出表格为HTML，行数：" + table.getRows().size());
    }

    @Override
    public void visitHeader(Header header) {
        html.append("<h").append(header.getLevel()).append(">")
            .append(header.getText()).append("</h").append(header.getLevel()).append(">\n");
        System.out.println("导出标题为HTML：" + header.getText() + " (级别：" + header.getLevel() + ")");
    }

    public String getHtml() {
        return html.toString();
    }
}

// PDF导出访问者
class PdfExportVisitor implements DocumentVisitor {
    private List<String> pdfCommands = new ArrayList<>();

    @Override
    public void visitParagraph(Paragraph paragraph) {
        pdfCommands.add("ADD_PARAGRAPH: " + paragraph.getText());
        System.out.println("导出段落为PDF：" + paragraph.getText());
    }

    @Override
    public void visitImage(Image image) {
        pdfCommands.add("ADD_IMAGE: " + image.getPath() + " [" + image.getWidth() + "x" + image.getHeight() + "]");
        System.out.println("导出图片为PDF：" + image.getPath());
    }

    @Override
    public void visitTable(Table table) {
        pdfCommands.add("ADD_TABLE: " + table.getRows().size() + " rows x " + table.getRows().get(0).length + " cols");
        for (String[] row : table.getRows()) {
            pdfCommands.add("  TABLE_ROW: " + String.join(" | ", row));
        }
        System.out.println("导出表格为PDF，行数：" + table.getRows().size());
    }

    @Override
    public void visitHeader(Header header) {
        pdfCommands.add("ADD_HEADER: " + header.getText() + " (Level " + header.getLevel() + ")");
        System.out.println("导出标题为PDF：" + header.getText());
    }

    public List<String> getPdfCommands() {
        return new ArrayList<>(pdfCommands);
    }
}

// 字数统计访问者
class WordCountVisitor implements DocumentVisitor {
    private int totalWords = 0;
    private int paragraphCount = 0;
    private int imageCount = 0;
    private int tableCount = 0;
    private int headerCount = 0;

    @Override
    public void visitParagraph(Paragraph paragraph) {
        paragraphCount++;
        String[] words = paragraph.getText().split("\\s+");
        totalWords += words.length;
        System.out.println("统计段落：" + words.length + " 个词");
    }

    @Override
    public void visitImage(Image image) {
        imageCount++;
        System.out.println("统计图片：" + image.getPath());
    }

    @Override
    public void visitTable(Table table) {
        tableCount++;
        for (String[] row : table.getRows()) {
            for (String cell : row) {
                String[] words = cell.split("\\s+");
                totalWords += words.length;
            }
        }
        System.out.println("统计表格：" + table.getRows().size() + " 行");
    }

    @Override
    public void visitHeader(Header header) {
        headerCount++;
        String[] words = header.getText().split("\\s+");
        totalWords += words.length;
        System.out.println("统计标题：" + words.length + " 个词");
    }

    public void printStatistics() {
        System.out.println("=== 文档统计信息 ===");
        System.out.println("总字数：" + totalWords);
        System.out.println("段落数：" + paragraphCount);
        System.out.println("图片数：" + imageCount);
        System.out.println("表格数：" + tableCount);
        System.out.println("标题数：" + headerCount);
        System.out.println("===================");
    }
}

// 格式验证访问者
class ValidationVisitor implements DocumentVisitor {
    private List<String> issues = new ArrayList<>();

    @Override
    public void visitParagraph(Paragraph paragraph) {
        if (paragraph.getText().length() > 1000) {
            issues.add("段落过长：" + paragraph.getText().substring(0, 50) + "...");
        }
        if (paragraph.getText().trim().isEmpty()) {
            issues.add("发现空段落");
        }
        System.out.println("验证段落：" + (paragraph.getText().length() <= 1000 ? "通过" : "警告"));
    }

    @Override
    public void visitImage(Image image) {
        if (image.getWidth() > 2000 || image.getHeight() > 2000) {
            issues.add("图片分辨率过高：" + image.getPath());
        }
        if (image.getAlt() == null || image.getAlt().trim().isEmpty()) {
            issues.add("图片缺少alt属性：" + image.getPath());
        }
        System.out.println("验证图片：" + image.getPath());
    }

    @Override
    public void visitTable(Table table) {
        if (table.getRows().size() > 100) {
            issues.add("表格行数过多：" + table.getRows().size() + " 行");
        }
        boolean hasEmptyCell = table.getRows().stream()
                .flatMap(Arrays::stream)
                .anyMatch(cell -> cell == null || cell.trim().isEmpty());
        if (hasEmptyCell) {
            issues.add("表格包含空单元格");
        }
        System.out.println("验证表格：" + (table.getRows().size() <= 100 ? "通过" : "警告"));
    }

    @Override
    public void visitHeader(Header header) {
        if (header.getLevel() < 1 || header.getLevel() > 6) {
            issues.add("标题级别无效：" + header.getLevel());
        }
        if (header.getText().length() > 100) {
            issues.add("标题过长：" + header.getText());
        }
        System.out.println("验证标题：" + header.getText());
    }

    public void printValidationResults() {
        System.out.println("=== 验证结果 ===");
        if (issues.isEmpty()) {
            System.out.println("文档格式正确，无问题发现");
        } else {
            System.out.println("发现 " + issues.size() + " 个问题：");
            for (int i = 0; i < issues.size(); i++) {
                System.out.println((i + 1) + ". " + issues.get(i));
            }
        }
        System.out.println("================");
    }
}
```

### 3. 抽象元素（Element）
```java
// 文档元素接口
interface DocumentElement {
    void accept(DocumentVisitor visitor);
}
```

### 4. 具体元素（ConcreteElement）
```java
// 段落元素
class Paragraph implements DocumentElement {
    private String text;

    public Paragraph(String text) {
        this.text = text;
    }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visitParagraph(this);
    }

    public String getText() {
        return text;
    }
}

// 图片元素
class Image implements DocumentElement {
    private String path;
    private String alt;
    private int width;
    private int height;

    public Image(String path, String alt, int width, int height) {
        this.path = path;
        this.alt = alt;
        this.width = width;
        this.height = height;
    }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visitImage(this);
    }

    public String getPath() { return path; }
    public String getAlt() { return alt; }
    public int getWidth() { return width; }
    public int getHeight() { return height; }
}

// 表格元素
class Table implements DocumentElement {
    private List<String[]> rows;

    public Table() {
        this.rows = new ArrayList<>();
    }

    public void addRow(String... cells) {
        rows.add(cells);
    }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visitTable(this);
    }

    public List<String[]> getRows() {
        return rows;
    }
}

// 标题元素
class Header implements DocumentElement {
    private String text;
    private int level;

    public Header(String text, int level) {
        this.text = text;
        this.level = level;
    }

    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visitHeader(this);
    }

    public String getText() { return text; }
    public int getLevel() { return level; }
}
```

### 5. 对象结构（ObjectStructure）
```java
// 文档类
class Document {
    private List<DocumentElement> elements = new ArrayList<>();

    public void addElement(DocumentElement element) {
        elements.add(element);
    }

    public void accept(DocumentVisitor visitor) {
        for (DocumentElement element : elements) {
            element.accept(visitor);
        }
    }

    public void removeElement(DocumentElement element) {
        elements.remove(element);
    }

    public int getElementCount() {
        return elements.size();
    }

    public void showStructure() {
        System.out.println("=== 文档结构 ===");
        for (int i = 0; i < elements.size(); i++) {
            DocumentElement element = elements.get(i);
            String type = element.getClass().getSimpleName();
            System.out.println((i + 1) + ". " + type);
        }
        System.out.println("===============");
    }
}
```

## 🎮 实际应用示例

### 示例1：编译器抽象语法树（AST）
```java
// AST节点接口
interface ASTNode {
    void accept(ASTVisitor visitor);
}

// AST访问者接口
interface ASTVisitor {
    void visitNumberLiteral(NumberLiteral node);
    void visitBinaryOperation(BinaryOperation node);
    void visitVariableReference(VariableReference node);
    void visitAssignment(Assignment node);
}

// 数字字面量节点
class NumberLiteral implements ASTNode {
    private double value;

    public NumberLiteral(double value) {
        this.value = value;
    }

    @Override
    public void accept(ASTVisitor visitor) {
        visitor.visitNumberLiteral(this);
    }

    public double getValue() { return value; }
}

// 二元操作节点
class BinaryOperation implements ASTNode {
    private ASTNode left;
    private ASTNode right;
    private String operator;

    public BinaryOperation(ASTNode left, String operator, ASTNode right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    @Override
    public void accept(ASTVisitor visitor) {
        visitor.visitBinaryOperation(this);
    }

    public ASTNode getLeft() { return left; }
    public ASTNode getRight() { return right; }
    public String getOperator() { return operator; }
}

// 变量引用节点
class VariableReference implements ASTNode {
    private String name;

    public VariableReference(String name) {
        this.name = name;
    }

    @Override
    public void accept(ASTVisitor visitor) {
        visitor.visitVariableReference(this);
    }

    public String getName() { return name; }
}

// 赋值节点
class Assignment implements ASTNode {
    private String variable;
    private ASTNode expression;

    public Assignment(String variable, ASTNode expression) {
        this.variable = variable;
        this.expression = expression;
    }

    @Override
    public void accept(ASTVisitor visitor) {
        visitor.visitAssignment(this);
    }

    public String getVariable() { return variable; }
    public ASTNode getExpression() { return expression; }
}

// 代码生成访问者
class CodeGeneratorVisitor implements ASTVisitor {
    private StringBuilder code = new StringBuilder();
    private int indentLevel = 0;

    @Override
    public void visitNumberLiteral(NumberLiteral node) {
        code.append(node.getValue());
        System.out.println("生成数字字面量：" + node.getValue());
    }

    @Override
    public void visitBinaryOperation(BinaryOperation node) {
        code.append("(");
        node.getLeft().accept(this);
        code.append(" ").append(node.getOperator()).append(" ");
        node.getRight().accept(this);
        code.append(")");
        System.out.println("生成二元操作：" + node.getOperator());
    }

    @Override
    public void visitVariableReference(VariableReference node) {
        code.append(node.getName());
        System.out.println("生成变量引用：" + node.getName());
    }

    @Override
    public void visitAssignment(Assignment node) {
        addIndent();
        code.append(node.getVariable()).append(" = ");
        node.getExpression().accept(this);
        code.append(";\n");
        System.out.println("生成赋值语句：" + node.getVariable());
    }

    private void addIndent() {
        for (int i = 0; i < indentLevel; i++) {
            code.append("  ");
        }
    }

    public String getGeneratedCode() {
        return code.toString();
    }
}

// 表达式求值访问者
class EvaluatorVisitor implements ASTVisitor {
    private Map<String, Double> variables = new HashMap<>();
    private Stack<Double> valueStack = new Stack<>();

    public void setVariable(String name, double value) {
        variables.put(name, value);
    }

    @Override
    public void visitNumberLiteral(NumberLiteral node) {
        valueStack.push(node.getValue());
        System.out.println("求值数字：" + node.getValue());
    }

    @Override
    public void visitBinaryOperation(BinaryOperation node) {
        node.getLeft().accept(this);
        node.getRight().accept(this);

        double right = valueStack.pop();
        double left = valueStack.pop();
        double result = 0;

        switch (node.getOperator()) {
            case "+": result = left + right; break;
            case "-": result = left - right; break;
            case "*": result = left * right; break;
            case "/": result = left / right; break;
            default: throw new RuntimeException("未知操作符：" + node.getOperator());
        }

        valueStack.push(result);
        System.out.println("求值操作：" + left + " " + node.getOperator() + " " + right + " = " + result);
    }

    @Override
    public void visitVariableReference(VariableReference node) {
        Double value = variables.get(node.getName());
        if (value == null) {
            throw new RuntimeException("未定义的变量：" + node.getName());
        }
        valueStack.push(value);
        System.out.println("求值变量：" + node.getName() + " = " + value);
    }

    @Override
    public void visitAssignment(Assignment node) {
        node.getExpression().accept(this);
        double value = valueStack.pop();
        variables.put(node.getVariable(), value);
        valueStack.push(value);
        System.out.println("赋值：" + node.getVariable() + " = " + value);
    }

    public double getResult() {
        return valueStack.isEmpty() ? 0 : valueStack.peek();
    }
}

// 语法树打印访问者
class PrintVisitor implements ASTVisitor {
    private int indentLevel = 0;

    @Override
    public void visitNumberLiteral(NumberLiteral node) {
        printIndent();
        System.out.println("NumberLiteral: " + node.getValue());
    }

    @Override
    public void visitBinaryOperation(BinaryOperation node) {
        printIndent();
        System.out.println("BinaryOperation: " + node.getOperator());
        indentLevel++;
        node.getLeft().accept(this);
        node.getRight().accept(this);
        indentLevel--;
    }

    @Override
    public void visitVariableReference(VariableReference node) {
        printIndent();
        System.out.println("VariableReference: " + node.getName());
    }

    @Override
    public void visitAssignment(Assignment node) {
        printIndent();
        System.out.println("Assignment: " + node.getVariable());
        indentLevel++;
        node.getExpression().accept(this);
        indentLevel--;
    }

    private void printIndent() {
        for (int i = 0; i < indentLevel; i++) {
            System.out.print("  ");
        }
    }
}

// 使用示例
public class CompilerExample {
    public static void main(String[] args) {
        // 构建AST：x = (5 + 3) * 2
        ASTNode ast = new Assignment("x",
            new BinaryOperation(
                new BinaryOperation(
                    new NumberLiteral(5),
                    "+",
                    new NumberLiteral(3)
                ),
                "*",
                new NumberLiteral(2)
            )
        );

        System.out.println("=== AST结构打印 ===");
        PrintVisitor printVisitor = new PrintVisitor();
        ast.accept(printVisitor);

        System.out.println("\n=== 代码生成 ===");
        CodeGeneratorVisitor codeGen = new CodeGeneratorVisitor();
        ast.accept(codeGen);
        System.out.println("生成的代码：\n" + codeGen.getGeneratedCode());

        System.out.println("=== 表达式求值 ===");
        EvaluatorVisitor evaluator = new EvaluatorVisitor();
        ast.accept(evaluator);
        System.out.println("最终结果：x = " + evaluator.getResult());

        // 测试带变量的表达式：y = x + 10
        System.out.println("\n=== 带变量的表达式 ===");
        evaluator.setVariable("x", 16); // 从上面的结果
        ASTNode ast2 = new Assignment("y",
            new BinaryOperation(
                new VariableReference("x"),
                "+",
                new NumberLiteral(10)
            )
        );

        ast2.accept(evaluator);
        System.out.println("最终结果：y = " + evaluator.getResult());
    }
}
```

### 示例2：文件系统操作
```java
// 文件系统元素接口
interface FileSystemElement {
    void accept(FileSystemVisitor visitor);
    String getName();
}

// 文件系统访问者接口
interface FileSystemVisitor {
    void visitFile(File file);
    void visitDirectory(Directory directory);
    void visitSymLink(SymLink symLink);
}

// 文件类
class File implements FileSystemElement {
    private String name;
    private long size;
    private String extension;
    private LocalDateTime lastModified;

    public File(String name, long size, String extension) {
        this.name = name;
        this.size = size;
        this.extension = extension;
        this.lastModified = LocalDateTime.now();
    }

    @Override
    public void accept(FileSystemVisitor visitor) {
        visitor.visitFile(this);
    }

    @Override
    public String getName() { return name; }
    public long getSize() { return size; }
    public String getExtension() { return extension; }
    public LocalDateTime getLastModified() { return lastModified; }
}

// 目录类
class Directory implements FileSystemElement {
    private String name;
    private List<FileSystemElement> children = new ArrayList<>();

    public Directory(String name) {
        this.name = name;
    }

    public void addChild(FileSystemElement child) {
        children.add(child);
    }

    @Override
    public void accept(FileSystemVisitor visitor) {
        visitor.visitDirectory(this);
        for (FileSystemElement child : children) {
            child.accept(visitor);
        }
    }

    @Override
    public String getName() { return name; }
    public List<FileSystemElement> getChildren() { return children; }
}

// 符号链接类
class SymLink implements FileSystemElement {
    private String name;
    private String target;

    public SymLink(String name, String target) {
        this.name = name;
        this.target = target;
    }

    @Override
    public void accept(FileSystemVisitor visitor) {
        visitor.visitSymLink(this);
    }

    @Override
    public String getName() { return name; }
    public String getTarget() { return target; }
}

// 大小计算访问者
class SizeCalculatorVisitor implements FileSystemVisitor {
    private long totalSize = 0;
    private int fileCount = 0;
    private int dirCount = 0;
    private int linkCount = 0;

    @Override
    public void visitFile(File file) {
        totalSize += file.getSize();
        fileCount++;
        System.out.println("文件：" + file.getName() + " (" + file.getSize() + " bytes)");
    }

    @Override
    public void visitDirectory(Directory directory) {
        dirCount++;
        System.out.println("目录：" + directory.getName());
    }

    @Override
    public void visitSymLink(SymLink symLink) {
        linkCount++;
        System.out.println("符号链接：" + symLink.getName() + " -> " + symLink.getTarget());
    }

    public void printStatistics() {
        System.out.println("=== 文件系统统计 ===");
        System.out.println("总大小：" + totalSize + " bytes");
        System.out.println("文件数：" + fileCount);
        System.out.println("目录数：" + dirCount);
        System.out.println("链接数：" + linkCount);
        System.out.println("=================");
    }
}

// 搜索访问者
class SearchVisitor implements FileSystemVisitor {
    private String searchPattern;
    private List<FileSystemElement> results = new ArrayList<>();

    public SearchVisitor(String searchPattern) {
        this.searchPattern = searchPattern.toLowerCase();
    }

    @Override
    public void visitFile(File file) {
        if (file.getName().toLowerCase().contains(searchPattern) ||
            file.getExtension().toLowerCase().contains(searchPattern)) {
            results.add(file);
            System.out.println("找到文件：" + file.getName());
        }
    }

    @Override
    public void visitDirectory(Directory directory) {
        if (directory.getName().toLowerCase().contains(searchPattern)) {
            results.add(directory);
            System.out.println("找到目录：" + directory.getName());
        }
    }

    @Override
    public void visitSymLink(SymLink symLink) {
        if (symLink.getName().toLowerCase().contains(searchPattern)) {
            results.add(symLink);
            System.out.println("找到链接：" + symLink.getName());
        }
    }

    public List<FileSystemElement> getResults() {
        return results;
    }
}

// 备份访问者
class BackupVisitor implements FileSystemVisitor {
    private String backupPath;
    private List<String> backupLog = new ArrayList<>();

    public BackupVisitor(String backupPath) {
        this.backupPath = backupPath;
    }

    @Override
    public void visitFile(File file) {
        String backupLocation = backupPath + "/" + file.getName();
        backupLog.add("备份文件：" + file.getName() + " -> " + backupLocation);
        System.out.println("备份文件：" + file.getName() + " (" + file.getSize() + " bytes)");
    }

    @Override
    public void visitDirectory(Directory directory) {
        String backupLocation = backupPath + "/" + directory.getName();
        backupLog.add("创建目录：" + backupLocation);
        System.out.println("创建备份目录：" + directory.getName());
    }

    @Override
    public void visitSymLink(SymLink symLink) {
        String backupLocation = backupPath + "/" + symLink.getName();
        backupLog.add("备份链接：" + symLink.getName() + " -> " + backupLocation);
        System.out.println("备份符号链接：" + symLink.getName());
    }

    public List<String> getBackupLog() {
        return backupLog;
    }
}

// 使用示例
public class FileSystemExample {
    public static void main(String[] args) {
        // 构建文件系统结构
        Directory root = new Directory("root");
        Directory documents = new Directory("documents");
        Directory images = new Directory("images");

        File readme = new File("readme.txt", 1024, "txt");
        File config = new File("config.json", 2048, "json");
        File photo1 = new File("vacation.jpg", 3145728, "jpg");
        File photo2 = new File("portrait.png", 2097152, "png");

        SymLink link = new SymLink("latest.txt", "/root/documents/readme.txt");

        // 构建层次结构
        root.addChild(documents);
        root.addChild(images);
        root.addChild(link);

        documents.addChild(readme);
        documents.addChild(config);

        images.addChild(photo1);
        images.addChild(photo2);

        System.out.println("=== 计算文件系统大小 ===");
        SizeCalculatorVisitor sizeCalculator = new SizeCalculatorVisitor();
        root.accept(sizeCalculator);
        sizeCalculator.printStatistics();

        System.out.println("\n=== 搜索jpg文件 ===");
        SearchVisitor searchVisitor = new SearchVisitor("jpg");
        root.accept(searchVisitor);
        System.out.println("搜索结果数量：" + searchVisitor.getResults().size());

        System.out.println("\n=== 备份文件系统 ===");
        BackupVisitor backupVisitor = new BackupVisitor("/backup");
        root.accept(backupVisitor);
        System.out.println("\n备份日志：");
        for (String log : backupVisitor.getBackupLog()) {
            System.out.println("  " + log);
        }
    }
}
```

## ⚡ 高级应用

### 与反射结合的通用访问者
```java
// 通用访问者基类
abstract class ReflectiveVisitor {
    public void visit(Object element) {
        String methodName = "visit" + element.getClass().getSimpleName();
        try {
            Method method = this.getClass().getDeclaredMethod(methodName, element.getClass());
            method.invoke(this, element);
        } catch (Exception e) {
            visitDefault(element);
        }
    }

    protected void visitDefault(Object element) {
        System.out.println("默认处理：" + element.getClass().getSimpleName());
    }
}

// 具体的反射访问者
class LoggingVisitor extends ReflectiveVisitor {
    public void visitString(String str) {
        System.out.println("访问字符串：" + str);
    }

    public void visitInteger(Integer num) {
        System.out.println("访问整数：" + num);
    }

    public void visitList(List<?> list) {
        System.out.println("访问列表，大小：" + list.size());
        for (Object item : list) {
            visit(item);
        }
    }
}
```

### 访问者工厂模式
```java
// 访问者工厂
class VisitorFactory {
    private static final Map<String, Supplier<DocumentVisitor>> visitors = Map.of(
        "html", HtmlExportVisitor::new,
        "pdf", PdfExportVisitor::new,
        "word-count", WordCountVisitor::new,
        "validation", ValidationVisitor::new
    );

    public static DocumentVisitor createVisitor(String type) {
        Supplier<DocumentVisitor> supplier = visitors.get(type.toLowerCase());
        if (supplier == null) {
            throw new IllegalArgumentException("不支持的访问者类型：" + type);
        }
        return supplier.get();
    }

    public static Set<String> getSupportedTypes() {
        return visitors.keySet();
    }
}

// 访问者链
class VisitorChain {
    private List<DocumentVisitor> visitors = new ArrayList<>();

    public VisitorChain add(DocumentVisitor visitor) {
        visitors.add(visitor);
        return this;
    }

    public void visitDocument(Document document) {
        for (DocumentVisitor visitor : visitors) {
            System.out.println("\n--- 执行访问者：" + visitor.getClass().getSimpleName() + " ---");
            document.accept(visitor);
        }
    }
}
```

## ✅ 优势分析

### 1. **开闭原则**
可以在不修改元素类的情况下增加新的操作。

### 2. **操作集中**
将相关的操作集中在访问者类中，便于维护。

### 3. **数据与算法分离**
数据结构与操作算法分离，职责明确。

### 4. **类型安全**
通过重载方法实现类型安全的操作分派。

## ⚠️ 注意事项

### 1. **元素类稳定性要求**
```java
// 访问者模式要求元素类相对稳定
// 如果经常增加新的元素类型，访问者接口需要频繁修改
interface Visitor {
    void visitElementA(ElementA element);
    void visitElementB(ElementB element);
    // 新增元素类型需要修改所有访问者
    void visitElementC(ElementC element); // 违反开闭原则
}
```

### 2. **循环依赖问题**
```java
// 注意避免元素间的循环引用
class DirectoryElement implements Element {
    private List<Element> children;
    private Element parent; // 可能导致循环访问

    @Override
    public void accept(Visitor visitor) {
        visitor.visitDirectory(this);
        // 需要控制递归深度，避免无限循环
        for (Element child : children) {
            child.accept(visitor);
        }
    }
}
```

### 3. **性能考虑**
频繁的访问者模式调用可能影响性能，特别是在大型对象结构中。

## 🆚 与其他模式对比

| 特性 | 访问者模式 | 策略模式 | 命令模式 |
|------|----------|----------|----------|
| 目的 | 扩展操作 | 选择算法 | 封装请求 |
| 结构稳定性 | 元素类稳定 | 上下文稳定 | 接收者稳定 |
| 扩展方向 | 扩展操作 | 扩展策略 | 扩展命令 |
| 双分派 | 支持 | 不支持 | 不支持 |

## 🎯 实战建议

### 1. **何时使用访问者模式**
- 对象结构相对稳定，但操作经常变化
- 需要对对象结构中的元素执行复杂操作
- 想要避免"污染"元素类的接口
- 操作逻辑分散在多个类中

### 2. **设计原则**
```java
// 好的访问者设计
interface Visitor<R> {
    R visitElementA(ElementA element);
    R visitElementB(ElementB element);

    // 提供默认实现，减少访问者实现负担
    default R visitDefault(Element element) {
        throw new UnsupportedOperationException("不支持的元素类型：" + element.getClass());
    }
}

// 元素类提供必要的访问方法
interface Element {
    <R> R accept(Visitor<R> visitor);

    // 提供访问器方法，但不要暴露过多内部细节
    String getId();
    // 避免提供 getInternalState() 等方法
}
```

### 3. **现代化改进**
```java
// 使用函数式接口简化访问者
@FunctionalInterface
interface ElementProcessor<T extends Element, R> {
    R process(T element);
}

class FunctionalVisitor {
    private Map<Class<?>, ElementProcessor<?, ?>> processors = new HashMap<>();

    public <T extends Element> void register(Class<T> elementType, ElementProcessor<T, ?> processor) {
        processors.put(elementType, processor);
    }

    @SuppressWarnings("unchecked")
    public <T extends Element, R> R visit(T element) {
        ElementProcessor<T, R> processor = (ElementProcessor<T, R>) processors.get(element.getClass());
        if (processor != null) {
            return processor.process(element);
        }
        throw new UnsupportedOperationException("未注册的元素类型：" + element.getClass());
    }
}
```

## 🧠 记忆技巧

**口诀：访问操作分离清**
- **访**问者定义新操作
- **问**题在于扩展性
- **操**作集中便维护
- **作**用分派很重要
- **分**离数据与算法
- **离**开元素独立行
- **清**晰职责好设计

**形象比喻：**
访问者模式就像**博物馆的讲解员**：
- 展品（元素）保持不变
- 不同讲解员（访问者）提供不同解说
- 新来的讲解员不需要修改展品
- 每个讲解员专注于自己的专业领域

## 🎉 总结

访问者模式是一种强大但相对复杂的设计模式，它让我们能够在不修改对象结构的情况下定义新的操作。通过将数据结构与操作算法分离，我们获得了更好的扩展性和维护性。

**核心思想：** 🚶‍♂️ 将操作从对象中分离出来，让访问者来定义新的行为，实现数据与算法的优雅分离！

下一篇我们将学习**中介者模式**，看看如何用中介者来管理对象间的复杂交互！ 🚀