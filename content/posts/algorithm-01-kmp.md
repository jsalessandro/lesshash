---
title: "算法详解：KMP算法 - 字符串匹配的高效利器"
date: 2025-01-09T10:01:00+08:00
draft: false
tags: ["算法", "KMP", "字符串匹配", "Java", "数据结构"]
categories: ["算法"]
series: ["高级算法入门教程"]
author: "lesshash"
description: "深入浅出讲解KMP字符串匹配算法，从失败函数到状态机，包含完整实现和优化技巧，让你彻底掌握高效字符串匹配的精髓"
---

## 🎯 什么是KMP算法？

### 概念图解
#### 算法对比

| 概念 | 说明 | 时间复杂度 | 关键技术 |
|------|------|------------|----------|
| **文本串 T** | 待搜索的长文本 | - | - |
| **模式串 P** | 要查找的目标字符串 | - | - |
| **朴素匹配** | 逐字符比较，失配后回退 | O(mn) | 暴力搜索 |
| **KMP算法** | 利用已匹配信息，避免回退 | O(m+n) | 失败函数 |

**KMP核心机制：**
```
失败函数π → 部分匹配表 → 避免回退 → 高效匹配
```

### 生活中的例子
KMP算法就像智能搜索，能够从失败中学习：

```
📖 阅读书籍查找关键词:
普通人: 逐字逐句查找，遇到不匹配就从头开始
聪明人: 记住已经匹配的部分，跳过不必要的重复检查

🔍 文档搜索场景:
文本: "ABABCABCABCABC"
模式: "ABCABC"

朴素算法: 每次失败都回到文本开始位置重新比较
KMP算法: 利用已知信息，跳过不可能匹配的位置

🎯 智能推理:
如果我们知道"ABCAB"已经匹配，但第6个字符不匹配
我们不需要回到最开始，而是利用"AB"的重复模式
```

### 核心思想
KMP算法的核心在于：**当失配时，利用已经匹配的信息来决定下一步的匹配位置，避免不必要的回退**。

## 🧠 算法原理

### 失败函数（前缀函数）
#### 失败函数原理

| 概念 | 定义 | 作用 |
|------|------|------|
| **失败函数 π[i]** | 模式串P[0..i]的最长真前缀等于真后缀的长度 | 确定失配后的跳转位置 |
| **真前缀** | 不包含整个字符串的前缀 | 用于匹配计算 |
| **真后缀** | 不包含整个字符串的后缀 | 用于匹配计算 |

**示例：**
- 字符串："abcab"
- π[4] = 2
- 原因：前缀"ab" = 后缀"ab"

失败函数π[i]表示模式串P[0...i]中，**最长真前缀等于真后缀的长度**。

```
模式串: A B C A B C A B C A B
索引:   0 1 2 3 4 5 6 7 8 9 10
π值:   0 0 0 1 2 3 4 5 6 7 8

解释:
π[0] = 0  (单个字符没有真前缀)
π[1] = 0  ("AB"无相等前后缀)
π[2] = 0  ("ABC"无相等前后缀)
π[3] = 1  ("ABCA": "A" = "A")
π[4] = 2  ("ABCAB": "AB" = "AB")
π[5] = 3  ("ABCABC": "ABC" = "ABC")
...
```

### 状态转移机制
```
文本: A B C A B C A B D
模式: A B C A B D
匹配:     ↑
     失配位置

传统方法: 回退到文本位置1重新开始
KMP方法: 利用π[4]=2，将模式串移动到合适位置
```

## 💻 完整实现

### 1. 基础KMP算法实现

```java
/**
 * KMP字符串匹配算法实现
 */
public class KMPAlgorithm {

    /**
     * KMP主算法：在文本中查找模式串
     * @param text 文本串
     * @param pattern 模式串
     * @return 第一次匹配的位置，未找到返回-1
     */
    public static int kmpSearch(String text, String pattern) {
        if (text == null || pattern == null || pattern.length() == 0) {
            return -1;
        }

        // 构建失败函数
        int[] pi = buildFailureFunction(pattern);

        int n = text.length();
        int m = pattern.length();
        int j = 0; // 模式串指针

        System.out.println("=== KMP匹配过程 ===");
        System.out.println("文本: " + text);
        System.out.println("模式: " + pattern);
        System.out.println("失败函数: " + java.util.Arrays.toString(pi));
        System.out.println();

        for (int i = 0; i < n; i++) {
            // 处理失配情况
            while (j > 0 && text.charAt(i) != pattern.charAt(j)) {
                System.out.printf("位置%d失配: '%c' != '%c', 利用π[%d]=%d跳转%n",
                                i, text.charAt(i), pattern.charAt(j), j-1, pi[j-1]);
                j = pi[j - 1];
            }

            // 字符匹配
            if (text.charAt(i) == pattern.charAt(j)) {
                System.out.printf("位置%d匹配: '%c' = '%c'%n", i, text.charAt(i), pattern.charAt(j));
                j++;
            }

            // 找到完整匹配
            if (j == m) {
                int matchStart = i - m + 1;
                System.out.printf("找到匹配! 起始位置: %d%n", matchStart);
                return matchStart;
            }

            // 显示当前匹配状态
            printMatchingState(text, pattern, i, j, matchStart(i, j, m));
        }

        System.out.println("未找到匹配");
        return -1;
    }

    /**
     * 构建失败函数（部分匹配表）
     */
    public static int[] buildFailureFunction(String pattern) {
        int m = pattern.length();
        int[] pi = new int[m];

        System.out.println("\n=== 构建失败函数过程 ===");
        pi[0] = 0; // 第一个字符的失败函数总是0

        for (int i = 1; i < m; i++) {
            int j = pi[i - 1]; // 从前一个位置的失败函数值开始

            // 寻找最长匹配前后缀
            while (j > 0 && pattern.charAt(i) != pattern.charAt(j)) {
                j = pi[j - 1];
            }

            if (pattern.charAt(i) == pattern.charAt(j)) {
                j++;
            }

            pi[i] = j;

            // 详细解释当前计算
            System.out.printf("π[%d] = %d: \"%s\"的最长相等前后缀长度%n",
                             i, pi[i], pattern.substring(0, i + 1));
            if (pi[i] > 0) {
                String prefix = pattern.substring(0, pi[i]);
                String suffix = pattern.substring(i - pi[i] + 1, i + 1);
                System.out.printf("  前缀: \"%s\", 后缀: \"%s\"%n", prefix, suffix);
            }
        }

        return pi;
    }

    /**
     * 查找所有匹配位置
     */
    public static java.util.List<Integer> kmpSearchAll(String text, String pattern) {
        java.util.List<Integer> matches = new java.util.ArrayList<>();

        if (text == null || pattern == null || pattern.length() == 0) {
            return matches;
        }

        int[] pi = buildFailureFunction(pattern);
        int n = text.length();
        int m = pattern.length();
        int j = 0;

        for (int i = 0; i < n; i++) {
            while (j > 0 && text.charAt(i) != pattern.charAt(j)) {
                j = pi[j - 1];
            }

            if (text.charAt(i) == pattern.charAt(j)) {
                j++;
            }

            if (j == m) {
                matches.add(i - m + 1);
                j = pi[j - 1]; // 继续寻找下一个匹配
            }
        }

        return matches;
    }

    /**
     * 显示匹配状态的辅助方法
     */
    private static void printMatchingState(String text, String pattern, int textPos, int patternPos, int matchStart) {
        if (matchStart < 0) return;

        System.out.print("文本: ");
        for (int i = 0; i < text.length(); i++) {
            if (i == textPos) {
                System.out.print("[" + text.charAt(i) + "]");
            } else {
                System.out.print(text.charAt(i));
            }
        }
        System.out.println();

        System.out.print("模式: ");
        for (int i = 0; i < matchStart; i++) {
            System.out.print(" ");
        }
        for (int i = 0; i < pattern.length(); i++) {
            if (i < patternPos) {
                System.out.print(pattern.charAt(i));
            } else if (i == patternPos) {
                System.out.print("[" + pattern.charAt(i) + "]");
            } else {
                System.out.print(pattern.charAt(i));
            }
        }
        System.out.println("\n");
    }

    private static int matchStart(int textPos, int patternPos, int patternLength) {
        return patternPos > 0 ? textPos - patternPos + 1 : -1;
    }
}
```

### 2. KMP算法演示和测试

```java
/**
 * KMP算法演示类
 */
public class KMPDemo {

    public static void main(String[] args) {
        // 演示1: 基本匹配
        demonstrateBasicMatching();

        // 演示2: 失败函数构建
        demonstrateFailureFunction();

        // 演示3: 复杂匹配场景
        demonstrateComplexMatching();

        // 演示4: 性能对比
        performanceComparison();
    }

    /**
     * 基本匹配演示
     */
    public static void demonstrateBasicMatching() {
        System.out.println("=".repeat(50));
        System.out.println("基本KMP匹配演示");
        System.out.println("=".repeat(50));

        String text = "ABABCABCABCABC";
        String pattern = "ABCABC";

        System.out.println("示例1: 简单匹配");
        int result = KMPAlgorithm.kmpSearch(text, pattern);
        System.out.println("匹配结果: " + (result != -1 ? "位置 " + result : "未找到"));

        System.out.println("\n示例2: 查找所有匹配");
        java.util.List<Integer> allMatches = KMPAlgorithm.kmpSearchAll(text, pattern);
        System.out.println("所有匹配位置: " + allMatches);
    }

    /**
     * 失败函数构建演示
     */
    public static void demonstrateFailureFunction() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("失败函数构建详解");
        System.out.println("=".repeat(50));

        String[] patterns = {
            "ABCABC",
            "AABAABA",
            "ABABABAB",
            "ABABCABAB"
        };

        for (String pattern : patterns) {
            System.out.println("\n模式串: " + pattern);
            int[] pi = KMPAlgorithm.buildFailureFunction(pattern);

            // 可视化失败函数
            System.out.println("失败函数可视化:");
            System.out.print("字符: ");
            for (char c : pattern.toCharArray()) {
                System.out.printf("%2c ", c);
            }
            System.out.println();

            System.out.print("索引: ");
            for (int i = 0; i < pattern.length(); i++) {
                System.out.printf("%2d ", i);
            }
            System.out.println();

            System.out.print("π值:  ");
            for (int value : pi) {
                System.out.printf("%2d ", value);
            }
            System.out.println();
        }
    }

    /**
     * 复杂匹配场景演示
     */
    public static void demonstrateComplexMatching() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("复杂匹配场景");
        System.out.println("=".repeat(50));

        // 场景1: 文本中有重复模式
        System.out.println("场景1: 重复模式匹配");
        String text1 = "ABABABABABCABABABAB";
        String pattern1 = "ABABAB";
        System.out.println("在文本中查找重复模式:");
        KMPAlgorithm.kmpSearch(text1, pattern1);

        // 场景2: 模式串本身有周期性
        System.out.println("\n场景2: 周期性模式");
        String text2 = "AAAAABAAABA";
        String pattern2 = "AAABA";
        KMPAlgorithm.kmpSearch(text2, pattern2);

        // 场景3: 长文本匹配
        System.out.println("\n场景3: 实际文本匹配");
        String text3 = "The quick brown fox jumps over the lazy dog";
        String pattern3 = "brown fox";
        int pos = KMPAlgorithm.kmpSearch(text3, pattern3);
        if (pos != -1) {
            System.out.println("在位置 " + pos + " 找到匹配: \"" +
                             text3.substring(pos, pos + pattern3.length()) + "\"");
        }
    }

    /**
     * 性能对比演示
     */
    public static void performanceComparison() {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("性能对比测试");
        System.out.println("=".repeat(50));

        // 生成测试数据
        String longText = generateTestText(100000);
        String pattern = "ABCDEFGHIJ";

        // 朴素算法
        long startTime = System.nanoTime();
        int result1 = naiveSearch(longText, pattern);
        long naiveTime = System.nanoTime() - startTime;

        // KMP算法
        startTime = System.nanoTime();
        int result2 = KMPAlgorithm.kmpSearch(longText, pattern);
        long kmpTime = System.nanoTime() - startTime;

        System.out.printf("文本长度: %d, 模式长度: %d%n", longText.length(), pattern.length());
        System.out.printf("朴素算法: %.2f ms, 结果: %d%n", naiveTime / 1e6, result1);
        System.out.printf("KMP算法:  %.2f ms, 结果: %d%n", kmpTime / 1e6, result2);
        System.out.printf("性能提升: %.2f倍%n", (double) naiveTime / kmpTime);
    }

    /**
     * 朴素字符串匹配算法（用于性能对比）
     */
    private static int naiveSearch(String text, String pattern) {
        int n = text.length();
        int m = pattern.length();

        for (int i = 0; i <= n - m; i++) {
            int j;
            for (j = 0; j < m; j++) {
                if (text.charAt(i + j) != pattern.charAt(j)) {
                    break;
                }
            }
            if (j == m) {
                return i;
            }
        }
        return -1;
    }

    /**
     * 生成测试文本
     */
    private static String generateTestText(int length) {
        StringBuilder sb = new StringBuilder();
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        java.util.Random random = new java.util.Random(42);

        for (int i = 0; i < length; i++) {
            sb.append(chars.charAt(random.nextInt(chars.length())));
        }

        // 在随机位置插入目标模式
        int insertPos = length / 2;
        sb.replace(insertPos, insertPos + 10, "ABCDEFGHIJ");

        return sb.toString();
    }
}
```

### 3. KMP算法优化版本

```java
/**
 * KMP算法的优化版本
 */
public class OptimizedKMP {

    /**
     * 优化的失败函数（next数组）
     * 避免不必要的比较
     */
    public static int[] buildOptimizedFailureFunction(String pattern) {
        int m = pattern.length();
        int[] next = new int[m];

        next[0] = -1; // 优化版本使用-1表示失败
        int j = -1;

        for (int i = 1; i < m; i++) {
            // 寻找合适的跳转位置
            while (j >= 0 && pattern.charAt(i - 1) != pattern.charAt(j)) {
                j = next[j];
            }
            j++;

            // 优化：如果当前字符与跳转位置字符相同，继续跳转
            if (i < m && pattern.charAt(i) == pattern.charAt(j)) {
                next[i] = next[j];
            } else {
                next[i] = j;
            }
        }

        return next;
    }

    /**
     * 优化的KMP搜索
     */
    public static int optimizedKmpSearch(String text, String pattern) {
        if (pattern.length() == 0) return 0;

        int[] next = buildOptimizedFailureFunction(pattern);
        int n = text.length();
        int m = pattern.length();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (j == -1 || text.charAt(i) == pattern.charAt(j)) {
                i++;
                j++;
            } else {
                j = next[j];
            }
        }

        return j == m ? i - m : -1;
    }

    /**
     * KMP with wildcard support (? matches any character)
     */
    public static int kmpWithWildcard(String text, String pattern) {
        int n = text.length();
        int m = pattern.length();

        // 构建修改的失败函数，考虑通配符
        int[] pi = new int[m];

        for (int i = 1; i < m; i++) {
            int j = pi[i - 1];

            while (j > 0 && !charMatch(pattern.charAt(i), pattern.charAt(j))) {
                j = pi[j - 1];
            }

            if (charMatch(pattern.charAt(i), pattern.charAt(j))) {
                j++;
            }

            pi[i] = j;
        }

        // 匹配过程
        int j = 0;
        for (int i = 0; i < n; i++) {
            while (j > 0 && !charMatch(text.charAt(i), pattern.charAt(j))) {
                j = pi[j - 1];
            }

            if (charMatch(text.charAt(i), pattern.charAt(j))) {
                j++;
            }

            if (j == m) {
                return i - m + 1;
            }
        }

        return -1;
    }

    private static boolean charMatch(char a, char b) {
        return a == b || a == '?' || b == '?';
    }

    /**
     * 多模式串匹配（AC自动机的简化版）
     */
    public static java.util.Map<String, java.util.List<Integer>> multiPatternKMP(
            String text, String[] patterns) {

        java.util.Map<String, java.util.List<Integer>> results = new java.util.HashMap<>();

        for (String pattern : patterns) {
            java.util.List<Integer> matches = new java.util.ArrayList<>();
            int[] pi = KMPAlgorithm.buildFailureFunction(pattern);

            int j = 0;
            for (int i = 0; i < text.length(); i++) {
                while (j > 0 && text.charAt(i) != pattern.charAt(j)) {
                    j = pi[j - 1];
                }

                if (text.charAt(i) == pattern.charAt(j)) {
                    j++;
                }

                if (j == pattern.length()) {
                    matches.add(i - pattern.length() + 1);
                    j = pi[j - 1];
                }
            }

            results.put(pattern, matches);
        }

        return results;
    }
}
```

## 📊 算法分析

### 时间复杂度分析
```
算法组成部分           时间复杂度
═══════════════════════════════════
构建失败函数          O(m)
文本匹配过程          O(n)
总时间复杂度          O(n + m)

对比:
朴素算法最坏情况      O(n × m)
KMP算法              O(n + m)
```

### 空间复杂度
```
数据结构              空间复杂度
═══════════════════════════════════
失败函数数组          O(m)
临时变量              O(1)
总空间复杂度          O(m)
```

### 性能特点分析

```java
/**
 * KMP算法特性分析
 */
public class KMPAnalysis {

    /**
     * 分析不同模式串的匹配效率
     */
    public static void analyzePatternTypes() {
        System.out.println("=== KMP算法特性分析 ===\n");

        String[] testTexts = {
            "AAAAAAAAAAAAAAAB",
            "ABCDEFGHIJKLMNOP",
            "ABABABABABABAB",
            "The quick brown fox jumps over the lazy dog"
        };

        String[] testPatterns = {
            "AAAAB",      // 重复字符模式
            "DEFGH",      // 无重复模式
            "ABABAB",     // 周期性模式
            "brown fox"   // 实际单词
        };

        for (int i = 0; i < testTexts.length; i++) {
            String text = testTexts[i];
            String pattern = testPatterns[i];

            System.out.println("测试 " + (i + 1) + ":");
            System.out.println("文本: " + text);
            System.out.println("模式: " + pattern);

            // 分析失败函数特征
            int[] pi = KMPAlgorithm.buildFailureFunction(pattern);
            analyzeFailureFunction(pattern, pi);

            // 执行匹配并分析
            long startTime = System.nanoTime();
            int result = KMPAlgorithm.kmpSearch(text, pattern);
            long elapsed = System.nanoTime() - startTime;

            System.out.printf("匹配结果: %s%n", result != -1 ? "位置 " + result : "未找到");
            System.out.printf("执行时间: %.3f μs%n", elapsed / 1000.0);
            System.out.println("-".repeat(40));
        }
    }

    /**
     * 分析失败函数的特征
     */
    private static void analyzeFailureFunction(String pattern, int[] pi) {
        int maxJump = 0;
        int totalJumps = 0;
        int nonZeroCount = 0;

        for (int i = 1; i < pi.length; i++) {
            if (pi[i] > 0) {
                nonZeroCount++;
                totalJumps += pi[i];
                maxJump = Math.max(maxJump, pi[i]);
            }
        }

        double avgJump = nonZeroCount > 0 ? (double) totalJumps / nonZeroCount : 0;

        System.out.println("失败函数分析:");
        System.out.printf("  最大跳转: %d%n", maxJump);
        System.out.printf("  平均跳转: %.2f%n", avgJump);
        System.out.printf("  跳转比例: %.2f%%%n", 100.0 * nonZeroCount / (pi.length - 1));
    }

    /**
     * 边界情况测试
     */
    public static void testEdgeCases() {
        System.out.println("\n=== 边界情况测试 ===");

        Object[][] testCases = {
            {"空模式串", "Hello World", ""},
            {"空文本串", "", "Hello"},
            {"单字符匹配", "A", "A"},
            {"单字符不匹配", "A", "B"},
            {"模式串比文本长", "Hi", "Hello"},
            {"完全匹配", "Hello", "Hello"},
            {"重复字符", "AAAA", "AA"},
            {"Unicode字符", "你好世界", "世界"}
        };

        for (Object[] testCase : testCases) {
            String description = (String) testCase[0];
            String text = (String) testCase[1];
            String pattern = (String) testCase[2];

            System.out.printf("%-15s: ", description);

            try {
                int result = KMPAlgorithm.kmpSearch(text, pattern);
                System.out.printf("结果=%d%n", result);
            } catch (Exception e) {
                System.out.printf("异常: %s%n", e.getMessage());
            }
        }
    }

    public static void main(String[] args) {
        analyzePatternTypes();
        testEdgeCases();
    }
}
```

## 🎯 实际应用场景

### 1. 文本编辑器的查找功能

```java
/**
 * 模拟文本编辑器的查找替换功能
 */
public class TextEditor {

    private StringBuilder content;

    public TextEditor(String initialContent) {
        this.content = new StringBuilder(initialContent);
    }

    /**
     * 查找所有匹配位置
     */
    public java.util.List<Integer> findAll(String pattern) {
        return KMPAlgorithm.kmpSearchAll(content.toString(), pattern);
    }

    /**
     * 查找并替换
     */
    public int replaceAll(String pattern, String replacement) {
        String text = content.toString();
        java.util.List<Integer> matches = findAll(pattern);

        if (matches.isEmpty()) {
            return 0;
        }

        // 从后往前替换，避免位置偏移
        for (int i = matches.size() - 1; i >= 0; i--) {
            int pos = matches.get(i);
            content.replace(pos, pos + pattern.length(), replacement);
        }

        return matches.size();
    }

    /**
     * 高亮显示匹配内容
     */
    public String highlightMatches(String pattern) {
        String text = content.toString();
        java.util.List<Integer> matches = findAll(pattern);

        if (matches.isEmpty()) {
            return text;
        }

        StringBuilder highlighted = new StringBuilder();
        int lastEnd = 0;

        for (int start : matches) {
            highlighted.append(text, lastEnd, start);
            highlighted.append("【").append(pattern).append("】");
            lastEnd = start + pattern.length();
        }

        highlighted.append(text.substring(lastEnd));
        return highlighted.toString();
    }

    public String getContent() {
        return content.toString();
    }

    // 演示使用
    public static void demonstrateTextEditor() {
        System.out.println("=== 文本编辑器演示 ===");

        String text = "Java is a programming language. Java is powerful. " +
                     "Many applications are written in Java.";

        TextEditor editor = new TextEditor(text);

        System.out.println("原文本:");
        System.out.println(editor.getContent());

        System.out.println("\n查找 'Java':");
        java.util.List<Integer> positions = editor.findAll("Java");
        System.out.println("找到 " + positions.size() + " 个匹配，位置: " + positions);

        System.out.println("\n高亮显示:");
        System.out.println(editor.highlightMatches("Java"));

        System.out.println("\n替换 'Java' 为 'Python':");
        int replacements = editor.replaceAll("Java", "Python");
        System.out.println("替换了 " + replacements + " 处");
        System.out.println("结果: " + editor.getContent());
    }
}
```

### 2. 日志分析系统

```java
/**
 * 基于KMP的日志分析系统
 */
public class LogAnalyzer {

    /**
     * 分析日志中的错误模式
     */
    public static void analyzeErrorPatterns(String[] logLines) {
        System.out.println("=== 日志错误分析 ===");

        String[] errorPatterns = {
            "ERROR",
            "FATAL",
            "Exception",
            "failed to",
            "timeout"
        };

        java.util.Map<String, Integer> errorCounts = new java.util.HashMap<>();
        java.util.Map<String, java.util.List<String>> errorLines = new java.util.HashMap<>();

        for (String pattern : errorPatterns) {
            errorCounts.put(pattern, 0);
            errorLines.put(pattern, new java.util.ArrayList<>());
        }

        for (String line : logLines) {
            for (String pattern : errorPatterns) {
                if (KMPAlgorithm.kmpSearch(line.toUpperCase(), pattern.toUpperCase()) != -1) {
                    errorCounts.put(pattern, errorCounts.get(pattern) + 1);
                    errorLines.get(pattern).add(line);
                }
            }
        }

        // 输出分析结果
        System.out.println("错误统计:");
        for (String pattern : errorPatterns) {
            int count = errorCounts.get(pattern);
            if (count > 0) {
                System.out.printf("%-12s: %d 次%n", pattern, count);

                // 显示前3个示例
                java.util.List<String> examples = errorLines.get(pattern);
                for (int i = 0; i < Math.min(3, examples.size()); i++) {
                    System.out.println("  例: " + examples.get(i));
                }
                if (examples.size() > 3) {
                    System.out.println("  ... 还有 " + (examples.size() - 3) + " 条");
                }
                System.out.println();
            }
        }
    }

    /**
     * 性能敏感的实时日志监控
     */
    public static class RealTimeLogMonitor {
        private final String[] alertPatterns;
        private final int[] patternPriorities;

        public RealTimeLogMonitor(String[] patterns, int[] priorities) {
            this.alertPatterns = patterns;
            this.patternPriorities = priorities;
        }

        public void processLogLine(String line) {
            for (int i = 0; i < alertPatterns.length; i++) {
                if (KMPAlgorithm.kmpSearch(line, alertPatterns[i]) != -1) {
                    triggerAlert(alertPatterns[i], patternPriorities[i], line);
                }
            }
        }

        private void triggerAlert(String pattern, int priority, String line) {
            String level = priority >= 3 ? "CRITICAL" : priority >= 2 ? "WARNING" : "INFO";
            System.out.printf("[%s] 检测到模式 '%s': %s%n", level, pattern, line);
        }
    }

    // 演示日志分析
    public static void demonstrateLogAnalysis() {
        String[] sampleLogs = {
            "2025-01-09 10:30:15 INFO Application started successfully",
            "2025-01-09 10:31:22 ERROR Database connection failed to establish",
            "2025-01-09 10:31:45 WARN Connection timeout after 30 seconds",
            "2025-01-09 10:32:10 FATAL OutOfMemoryError in thread main",
            "2025-01-09 10:32:33 ERROR NullPointerException in UserService",
            "2025-01-09 10:33:01 INFO Request processed successfully",
            "2025-01-09 10:33:15 ERROR Failed to parse JSON response"
        };

        analyzeErrorPatterns(sampleLogs);

        // 实时监控演示
        System.out.println("=== 实时监控演示 ===");
        String[] alertPatterns = {"FATAL", "ERROR", "timeout"};
        int[] priorities = {3, 2, 2};

        RealTimeLogMonitor monitor = new RealTimeLogMonitor(alertPatterns, priorities);

        for (String log : sampleLogs) {
            monitor.processLogLine(log);
        }
    }
}
```

## ✅ 优缺点总结

### 优点
- ✅ **线性时间复杂度** - O(n+m)，比朴素算法快
- ✅ **避免重复比较** - 利用已匹配信息跳转
- ✅ **适合长模式串** - 模式串越长，优势越明显
- ✅ **稳定性能** - 最坏情况仍是线性时间
- ✅ **广泛应用** - 是许多高级算法的基础

### 缺点
- ❌ **预处理开销** - 需要构建失败函数
- ❌ **空间消耗** - 需要额外O(m)空间
- ❌ **实现复杂** - 比朴素算法复杂
- ❌ **短模式劣势** - 对很短的模式串优势不明显

### 使用场景
```
适用场景:
✓ 长文本中查找模式串
✓ 模式串有重复结构
✓ 需要多次匹配同一模式
✓ 实时文本处理系统

不适用场景:
✗ 非常短的文本和模式
✗ 一次性匹配场景
✗ 内存严格限制的环境
```

## 🧠 记忆技巧

### 核心思想记忆
> **"失败不回头，跳转找最优"**

### 失败函数记忆
```
失败函数三要素:
1. 真前缀 = 真后缀
2. 最长匹配长度
3. 用于跳转位置
```

### 算法流程记忆
> **"构建失败函数，匹配中跳转，成功即返回"**

---

KMP算法是字符串匹配的经典算法，掌握它不仅能解决实际问题，更能深入理解算法设计的精髓。通过失败函数的巧妙设计，我们将暴力搜索变成了智能匹配，这正体现了算法的美妙之处！