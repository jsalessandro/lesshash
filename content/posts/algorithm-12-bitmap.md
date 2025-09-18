---
title: "算法详解：位图(Bitmap) - 海量数据的高效筛选"
date: 2025-01-20T10:12:00+08:00
tags: ["算法", "位图", "Bitmap", "Java", "数据结构"]
categories: ["算法"]
series: ["高级算法入门教程"]
author: "lesshash"
---

# 算法详解：位图(Bitmap) - 海量数据的高效筛选

## 引言

在处理海量数据的场景中，我们经常会遇到需要快速判断某个元素是否存在、统计元素个数、或者进行集合运算的问题。传统的数据结构如HashSet或数组在面对亿级别数据时会消耗大量内存，而位图(Bitmap)作为一种高效的数据结构，能够以极低的内存成本解决这些问题。

位图本质上是一个由0和1组成的位序列，每一位代表一个可能的值是否存在。这种设计使得位图在空间效率和查询速度方面都表现出色，成为了大数据处理、分布式系统和数据库索引中的重要工具。

## 什么是位图(Bitmap)

### 基本概念

位图是一种使用位(bit)来映射数据存在性的数据结构。每个位只能存储0或1两种状态，分别表示对应位置的数据不存在或存在。

```
数字序列：[1, 3, 5, 7, 9]
位图表示：
索引：0 1 2 3 4 5 6 7 8 9
位值：0 1 0 1 0 1 0 1 0 1
```

### 位级可视化

让我们通过一个具体的例子来理解位图的工作原理：

```
假设我们要存储集合 {2, 5, 8, 11, 15}
数字范围：0-15 (需要16个位)

二进制表示：
位置: 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
位值:  1  0  0  0  1  0  0  1  0  0  1  0  0  1  0  0
十六进制: 0x8908

内存占用：仅需2字节(16位)
```

### 位图的优势

1. **空间效率极高**：每个元素仅占用1位，相比传统存储方式节省90%以上空间
2. **查询速度快**：位操作的时间复杂度为O(1)
3. **支持并行操作**：可以利用位运算进行批量处理
4. **集合运算简单**：通过位运算直接实现交集、并集、差集

## 位图的Java实现

### 基础位图类

```java
/**
 * 基础位图实现
 * 支持基本的设置、清除、查询操作
 */
public class BasicBitmap {
    private long[] bits;
    private int size;

    // 每个long包含64位
    private static final int BITS_PER_WORD = 64;
    private static final int LOG_BITS_PER_WORD = 6; // log2(64) = 6

    public BasicBitmap(int size) {
        this.size = size;
        int wordCount = (size + BITS_PER_WORD - 1) / BITS_PER_WORD;
        this.bits = new long[wordCount];
    }

    /**
     * 设置指定位置的位为1
     * @param index 位置索引
     */
    public void set(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }

        int wordIndex = index >> LOG_BITS_PER_WORD;  // index / 64
        int bitIndex = index & (BITS_PER_WORD - 1); // index % 64

        bits[wordIndex] |= (1L << bitIndex);
    }

    /**
     * 设置指定位置的位为0
     * @param index 位置索引
     */
    public void clear(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }

        int wordIndex = index >> LOG_BITS_PER_WORD;
        int bitIndex = index & (BITS_PER_WORD - 1);

        bits[wordIndex] &= ~(1L << bitIndex);
    }

    /**
     * 检查指定位置的位是否为1
     * @param index 位置索引
     * @return true表示位为1，false表示位为0
     */
    public boolean get(int index) {
        if (index < 0 || index >= size) {
            return false;
        }

        int wordIndex = index >> LOG_BITS_PER_WORD;
        int bitIndex = index & (BITS_PER_WORD - 1);

        return (bits[wordIndex] & (1L << bitIndex)) != 0;
    }

    /**
     * 翻转指定位置的位
     * @param index 位置索引
     */
    public void flip(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }

        int wordIndex = index >> LOG_BITS_PER_WORD;
        int bitIndex = index & (BITS_PER_WORD - 1);

        bits[wordIndex] ^= (1L << bitIndex);
    }

    /**
     * 统计位图中1的个数
     * @return 1的个数
     */
    public int cardinality() {
        int count = 0;
        for (long word : bits) {
            count += Long.bitCount(word);
        }
        return count;
    }

    /**
     * 检查位图是否为空（所有位都是0）
     * @return true表示为空
     */
    public boolean isEmpty() {
        for (long word : bits) {
            if (word != 0) return false;
        }
        return true;
    }

    /**
     * 清空所有位
     */
    public void clear() {
        java.util.Arrays.fill(bits, 0L);
    }

    /**
     * 获取位图大小
     * @return 位图大小
     */
    public int size() {
        return size;
    }
}
```

### 高级位图操作

```java
/**
 * 高级位图实现，支持集合运算
 */
public class AdvancedBitmap extends BasicBitmap {

    public AdvancedBitmap(int size) {
        super(size);
    }

    /**
     * 与运算（交集）
     * @param other 另一个位图
     * @return 新的位图表示交集结果
     */
    public AdvancedBitmap and(AdvancedBitmap other) {
        int minSize = Math.min(this.size(), other.size());
        AdvancedBitmap result = new AdvancedBitmap(minSize);

        int wordCount = Math.min(this.bits.length, other.bits.length);
        for (int i = 0; i < wordCount; i++) {
            result.bits[i] = this.bits[i] & other.bits[i];
        }

        return result;
    }

    /**
     * 或运算（并集）
     * @param other 另一个位图
     * @return 新的位图表示并集结果
     */
    public AdvancedBitmap or(AdvancedBitmap other) {
        int maxSize = Math.max(this.size(), other.size());
        AdvancedBitmap result = new AdvancedBitmap(maxSize);

        // 复制较长位图的内容
        if (this.size() >= other.size()) {
            System.arraycopy(this.bits, 0, result.bits, 0, this.bits.length);
            for (int i = 0; i < other.bits.length; i++) {
                result.bits[i] |= other.bits[i];
            }
        } else {
            System.arraycopy(other.bits, 0, result.bits, 0, other.bits.length);
            for (int i = 0; i < this.bits.length; i++) {
                result.bits[i] |= this.bits[i];
            }
        }

        return result;
    }

    /**
     * 异或运算（对称差集）
     * @param other 另一个位图
     * @return 新的位图表示对称差集结果
     */
    public AdvancedBitmap xor(AdvancedBitmap other) {
        int maxSize = Math.max(this.size(), other.size());
        AdvancedBitmap result = new AdvancedBitmap(maxSize);

        int minWords = Math.min(this.bits.length, other.bits.length);
        int maxWords = Math.max(this.bits.length, other.bits.length);

        // 对公共部分进行异或运算
        for (int i = 0; i < minWords; i++) {
            result.bits[i] = this.bits[i] ^ other.bits[i];
        }

        // 复制较长位图的剩余部分
        if (this.bits.length > other.bits.length) {
            System.arraycopy(this.bits, minWords, result.bits, minWords,
                           this.bits.length - minWords);
        } else if (other.bits.length > this.bits.length) {
            System.arraycopy(other.bits, minWords, result.bits, minWords,
                           other.bits.length - minWords);
        }

        return result;
    }

    /**
     * 非运算（补集）
     * @return 新的位图表示补集结果
     */
    public AdvancedBitmap not() {
        AdvancedBitmap result = new AdvancedBitmap(this.size());

        for (int i = 0; i < this.bits.length; i++) {
            result.bits[i] = ~this.bits[i];
        }

        // 清除超出范围的位
        int lastWordBits = size() % BITS_PER_WORD;
        if (lastWordBits != 0 && result.bits.length > 0) {
            long mask = (1L << lastWordBits) - 1;
            int lastIndex = result.bits.length - 1;
            result.bits[lastIndex] &= mask;
        }

        return result;
    }

    /**
     * 差集运算 (A - B)
     * @param other 要减去的位图
     * @return 新的位图表示差集结果
     */
    public AdvancedBitmap andNot(AdvancedBitmap other) {
        AdvancedBitmap result = new AdvancedBitmap(this.size());

        int minWords = Math.min(this.bits.length, other.bits.length);

        // 对公共部分进行差集运算
        for (int i = 0; i < minWords; i++) {
            result.bits[i] = this.bits[i] & (~other.bits[i]);
        }

        // 复制this剩余的部分
        if (this.bits.length > other.bits.length) {
            System.arraycopy(this.bits, minWords, result.bits, minWords,
                           this.bits.length - minWords);
        }

        return result;
    }

    /**
     * 获取所有设置为1的位的索引
     * @return 索引列表
     */
    public java.util.List<Integer> getSetBits() {
        java.util.List<Integer> result = new java.util.ArrayList<>();

        for (int wordIndex = 0; wordIndex < bits.length; wordIndex++) {
            long word = bits[wordIndex];
            if (word != 0) {
                for (int bitIndex = 0; bitIndex < BITS_PER_WORD; bitIndex++) {
                    if ((word & (1L << bitIndex)) != 0) {
                        int index = (wordIndex << LOG_BITS_PER_WORD) + bitIndex;
                        if (index < size()) {
                            result.add(index);
                        }
                    }
                }
            }
        }

        return result;
    }

    /**
     * 获取下一个设置为1的位的索引
     * @param fromIndex 起始索引
     * @return 下一个设置为1的位的索引，如果没有返回-1
     */
    public int nextSetBit(int fromIndex) {
        if (fromIndex < 0) fromIndex = 0;
        if (fromIndex >= size()) return -1;

        int wordIndex = fromIndex >> LOG_BITS_PER_WORD;
        if (wordIndex >= bits.length) return -1;

        // 获取当前word，并清除fromIndex之前的位
        long word = bits[wordIndex] & ((-1L) << fromIndex);

        while (true) {
            if (word != 0) {
                int bitIndex = Long.numberOfTrailingZeros(word);
                int index = (wordIndex << LOG_BITS_PER_WORD) + bitIndex;
                return index < size() ? index : -1;
            }

            // 移动到下一个word
            if (++wordIndex >= bits.length) return -1;
            word = bits[wordIndex];
        }
    }
}
```

## 实际应用场景

### 1. 布隆过滤器(Bloom Filter)

布隆过滤器是位图的经典应用，用于快速判断元素是否可能存在于集合中。

```java
/**
 * 基于位图的简单布隆过滤器实现
 */
public class SimpleBloomFilter {
    private AdvancedBitmap bitmap;
    private int hashFunctions;
    private int expectedElements;

    public SimpleBloomFilter(int expectedElements, double falsePositiveRate) {
        this.expectedElements = expectedElements;

        // 计算最优位图大小和哈希函数个数
        int optimalBits = (int) Math.ceil(expectedElements * Math.log(falsePositiveRate) /
                                        Math.log(1.0 / (Math.pow(2.0, Math.log(2.0)))));
        this.hashFunctions = (int) Math.ceil((double) optimalBits / expectedElements * Math.log(2.0));

        this.bitmap = new AdvancedBitmap(optimalBits);
    }

    /**
     * 添加元素到布隆过滤器
     */
    public void add(String element) {
        for (int i = 0; i < hashFunctions; i++) {
            int hash = hash(element, i) % bitmap.size();
            if (hash < 0) hash += bitmap.size();
            bitmap.set(hash);
        }
    }

    /**
     * 检查元素是否可能存在
     * @param element 要检查的元素
     * @return true表示可能存在，false表示一定不存在
     */
    public boolean mightContain(String element) {
        for (int i = 0; i < hashFunctions; i++) {
            int hash = hash(element, i) % bitmap.size();
            if (hash < 0) hash += bitmap.size();
            if (!bitmap.get(hash)) {
                return false;
            }
        }
        return true;
    }

    /**
     * 简单的哈希函数
     */
    private int hash(String element, int seed) {
        int hash = 0;
        for (char c : element.toCharArray()) {
            hash = hash * 31 + c + seed;
        }
        return hash;
    }
}
```

### 2. 重复数据检测

在大数据处理中，位图常用于快速检测重复数据：

```java
/**
 * 基于位图的重复数据检测器
 */
public class DuplicateDetector {
    private AdvancedBitmap seen;
    private int maxValue;

    public DuplicateDetector(int maxValue) {
        this.maxValue = maxValue;
        this.seen = new AdvancedBitmap(maxValue + 1);
    }

    /**
     * 检查并记录数字，返回是否为重复
     * @param number 要检查的数字
     * @return true表示是重复数据
     */
    public boolean checkAndMark(int number) {
        if (number < 0 || number > maxValue) {
            throw new IllegalArgumentException("Number out of range: " + number);
        }

        if (seen.get(number)) {
            return true; // 重复
        }

        seen.set(number);
        return false; // 首次出现
    }

    /**
     * 获取所有重复出现的数字
     */
    public java.util.List<Integer> getDuplicates() {
        // 这里需要额外的位图来跟踪重复项
        return new java.util.ArrayList<>();
    }

    /**
     * 获取唯一数字的个数
     */
    public int getUniqueCount() {
        return seen.cardinality();
    }

    /**
     * 重置检测器
     */
    public void reset() {
        seen.clear();
    }
}
```

### 3. 数据库索引优化

位图索引在数据库中广泛应用，特别适合低基数(cardinality)的列：

```java
/**
 * 简化的位图索引实现
 */
public class BitmapIndex {
    private java.util.Map<String, AdvancedBitmap> index;
    private int recordCount;

    public BitmapIndex(int recordCount) {
        this.recordCount = recordCount;
        this.index = new java.util.HashMap<>();
    }

    /**
     * 为指定值的记录位置设置索引
     * @param value 索引值
     * @param recordId 记录ID
     */
    public void setIndex(String value, int recordId) {
        if (recordId < 0 || recordId >= recordCount) {
            throw new IllegalArgumentException("Invalid record ID: " + recordId);
        }

        AdvancedBitmap bitmap = index.computeIfAbsent(value,
            k -> new AdvancedBitmap(recordCount));
        bitmap.set(recordId);
    }

    /**
     * 查询包含指定值的所有记录ID
     * @param value 查询值
     * @return 记录ID列表
     */
    public java.util.List<Integer> query(String value) {
        AdvancedBitmap bitmap = index.get(value);
        return bitmap != null ? bitmap.getSetBits() : new java.util.ArrayList<>();
    }

    /**
     * 执行AND查询（交集）
     * @param values 查询值列表
     * @return 满足所有条件的记录ID列表
     */
    public java.util.List<Integer> queryAnd(java.util.List<String> values) {
        if (values.isEmpty()) return new java.util.ArrayList<>();

        AdvancedBitmap result = index.get(values.get(0));
        if (result == null) return new java.util.ArrayList<>();

        result = new AdvancedBitmap(recordCount);
        System.arraycopy(index.get(values.get(0)).bits, 0,
                        result.bits, 0, result.bits.length);

        for (int i = 1; i < values.size(); i++) {
            AdvancedBitmap bitmap = index.get(values.get(i));
            if (bitmap == null) {
                return new java.util.ArrayList<>();
            }
            result = result.and(bitmap);
        }

        return result.getSetBits();
    }

    /**
     * 执行OR查询（并集）
     * @param values 查询值列表
     * @return 满足任一条件的记录ID列表
     */
    public java.util.List<Integer> queryOr(java.util.List<String> values) {
        if (values.isEmpty()) return new java.util.ArrayList<>();

        AdvancedBitmap result = new AdvancedBitmap(recordCount);

        for (String value : values) {
            AdvancedBitmap bitmap = index.get(value);
            if (bitmap != null) {
                result = result.or(bitmap);
            }
        }

        return result.getSetBits();
    }

    /**
     * 获取索引统计信息
     */
    public void printStats() {
        System.out.println("位图索引统计:");
        System.out.println("总记录数: " + recordCount);
        System.out.println("索引值个数: " + index.size());

        for (java.util.Map.Entry<String, AdvancedBitmap> entry : index.entrySet()) {
            System.out.printf("值 '%s': %d 条记录\n",
                            entry.getKey(), entry.getValue().cardinality());
        }
    }
}
```

## 性能分析与内存优化

### 内存使用分析

传统数据结构与位图的内存对比：

```java
/**
 * 内存使用对比分析
 */
public class MemoryAnalysis {

    /**
     * 分析不同数据结构的内存使用
     */
    public static void compareMemoryUsage() {
        int dataSize = 10_000_000; // 1000万个数字

        // 1. HashSet存储整数
        System.out.println("=== 内存使用对比分析 ===");
        System.out.println("数据规模: " + dataSize + " 个整数");

        // HashSet: 每个Integer对象约16字节 + HashMap开销
        long hashSetMemory = dataSize * 16L + dataSize * 8L; // 估算
        System.out.println("HashSet内存使用: ~" + (hashSetMemory / 1024 / 1024) + " MB");

        // 2. 数组存储
        long arrayMemory = dataSize * 4L; // int数组
        System.out.println("int数组内存使用: " + (arrayMemory / 1024 / 1024) + " MB");

        // 3. 位图存储
        long bitmapMemory = dataSize / 8L; // 每8个数字1字节
        System.out.println("位图内存使用: " + (bitmapMemory / 1024 / 1024) + " MB");

        // 计算节省的内存
        double savingVsHashSet = (1.0 - (double)bitmapMemory / hashSetMemory) * 100;
        double savingVsArray = (1.0 - (double)bitmapMemory / arrayMemory) * 100;

        System.out.printf("相比HashSet节省: %.1f%%\n", savingVsHashSet);
        System.out.printf("相比数组节省: %.1f%%\n", savingVsArray);
    }

    /**
     * 性能测试
     */
    public static void performanceTest() {
        int testSize = 1_000_000;
        AdvancedBitmap bitmap = new AdvancedBitmap(testSize);
        java.util.HashSet<Integer> hashSet = new java.util.HashSet<>();

        // 测试数据
        java.util.Random random = new java.util.Random(42);
        int[] testData = new int[testSize / 10]; // 10%的数据
        for (int i = 0; i < testData.length; i++) {
            testData[i] = random.nextInt(testSize);
        }

        System.out.println("\n=== 性能测试 ===");

        // 位图插入性能
        long startTime = System.nanoTime();
        for (int value : testData) {
            bitmap.set(value);
        }
        long bitmapInsertTime = System.nanoTime() - startTime;

        // HashSet插入性能
        startTime = System.nanoTime();
        for (int value : testData) {
            hashSet.add(value);
        }
        long hashSetInsertTime = System.nanoTime() - startTime;

        System.out.printf("位图插入时间: %.2f ms\n", bitmapInsertTime / 1_000_000.0);
        System.out.printf("HashSet插入时间: %.2f ms\n", hashSetInsertTime / 1_000_000.0);

        // 查询性能测试
        startTime = System.nanoTime();
        int bitmapHits = 0;
        for (int value : testData) {
            if (bitmap.get(value)) bitmapHits++;
        }
        long bitmapQueryTime = System.nanoTime() - startTime;

        startTime = System.nanoTime();
        int hashSetHits = 0;
        for (int value : testData) {
            if (hashSet.contains(value)) hashSetHits++;
        }
        long hashSetQueryTime = System.nanoTime() - startTime;

        System.out.printf("位图查询时间: %.2f ms (命中: %d)\n",
                         bitmapQueryTime / 1_000_000.0, bitmapHits);
        System.out.printf("HashSet查询时间: %.2f ms (命中: %d)\n",
                         hashSetQueryTime / 1_000_000.0, hashSetHits);
    }

    public static void main(String[] args) {
        compareMemoryUsage();
        performanceTest();
    }
}
```

### 位图压缩技术

对于稀疏数据，可以使用压缩技术进一步节省内存：

```java
/**
 * 压缩位图实现 - 使用游程编码(Run-Length Encoding)
 */
public class CompressedBitmap {

    // 游程：存储连续0或1的起始位置和长度
    private static class Run {
        int start;
        int length;
        boolean value; // true表示1，false表示0

        Run(int start, int length, boolean value) {
            this.start = start;
            this.length = length;
            this.value = value;
        }
    }

    private java.util.List<Run> runs;
    private int size;

    public CompressedBitmap(int size) {
        this.size = size;
        this.runs = new java.util.ArrayList<>();
        // 初始时整个位图都是0
        if (size > 0) {
            runs.add(new Run(0, size, false));
        }
    }

    /**
     * 设置指定位置为1
     */
    public void set(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index);
        }

        // 查找包含该索引的游程
        for (int i = 0; i < runs.size(); i++) {
            Run run = runs.get(i);
            if (index >= run.start && index < run.start + run.length) {
                if (run.value) {
                    // 已经是1，无需操作
                    return;
                }

                // 需要分割当前游程
                splitRun(i, index, true);
                return;
            }
        }
    }

    /**
     * 分割游程
     */
    private void splitRun(int runIndex, int splitIndex, boolean newValue) {
        Run originalRun = runs.get(runIndex);

        if (splitIndex == originalRun.start) {
            // 在游程开始处分割
            if (originalRun.length == 1) {
                // 整个游程都变成新值
                originalRun.value = newValue;
            } else {
                // 插入新的单位游程
                runs.add(runIndex, new Run(splitIndex, 1, newValue));
                originalRun.start++;
                originalRun.length--;
            }
        } else if (splitIndex == originalRun.start + originalRun.length - 1) {
            // 在游程结尾处分割
            originalRun.length--;
            runs.add(runIndex + 1, new Run(splitIndex, 1, newValue));
        } else {
            // 在游程中间分割
            int leftLength = splitIndex - originalRun.start;
            int rightStart = splitIndex + 1;
            int rightLength = originalRun.start + originalRun.length - rightStart;

            // 修改原游程为左半部分
            originalRun.length = leftLength;

            // 插入新的单位游程
            runs.add(runIndex + 1, new Run(splitIndex, 1, newValue));

            // 插入右半部分
            if (rightLength > 0) {
                runs.add(runIndex + 2, new Run(rightStart, rightLength, originalRun.value));
            }
        }

        // 合并相邻的相同值游程
        mergeRuns();
    }

    /**
     * 合并相邻的相同值游程
     */
    private void mergeRuns() {
        for (int i = runs.size() - 1; i > 0; i--) {
            Run current = runs.get(i);
            Run previous = runs.get(i - 1);

            if (current.value == previous.value &&
                previous.start + previous.length == current.start) {
                // 合并两个游程
                previous.length += current.length;
                runs.remove(i);
            }
        }
    }

    /**
     * 检查指定位置是否为1
     */
    public boolean get(int index) {
        if (index < 0 || index >= size) {
            return false;
        }

        for (Run run : runs) {
            if (index >= run.start && index < run.start + run.length) {
                return run.value;
            }
        }

        return false;
    }

    /**
     * 统计1的个数
     */
    public int cardinality() {
        int count = 0;
        for (Run run : runs) {
            if (run.value) {
                count += run.length;
            }
        }
        return count;
    }

    /**
     * 获取压缩率
     */
    public double getCompressionRatio() {
        int originalBits = size;
        int compressedSize = runs.size() * 12; // 每个Run约12字节
        return 1.0 - (double) compressedSize / (originalBits / 8.0);
    }

    /**
     * 打印游程信息（用于调试）
     */
    public void printRuns() {
        System.out.println("压缩位图游程信息:");
        for (int i = 0; i < runs.size(); i++) {
            Run run = runs.get(i);
            System.out.printf("游程%d: [%d, %d) = %s (长度: %d)\n",
                            i, run.start, run.start + run.length,
                            run.value ? "1" : "0", run.length);
        }
        System.out.printf("总游程数: %d, 压缩率: %.2f%%\n",
                         runs.size(), getCompressionRatio() * 100);
    }
}
```

## 位图的变体和优化

### Roaring Bitmap

Roaring Bitmap是一种高效的位图实现，特别适合稀疏数据：

```java
/**
 * 简化的Roaring Bitmap概念实现
 * 将32位整数空间分成64K个桶，每个桶使用不同的数据结构
 */
public class SimpleRoaringBitmap {

    // 容器类型
    private enum ContainerType {
        ARRAY,    // 数组容器：存储少量数据
        BITMAP    // 位图容器：存储密集数据
    }

    private static class Container {
        ContainerType type;
        Object data;
        int cardinality;

        Container(ContainerType type, Object data, int cardinality) {
            this.type = type;
            this.data = data;
            this.cardinality = cardinality;
        }
    }

    private java.util.Map<Integer, Container> containers;
    private static final int BUCKET_SIZE = 65536; // 64K
    private static final int ARRAY_THRESHOLD = 4096; // 阈值

    public SimpleRoaringBitmap() {
        this.containers = new java.util.TreeMap<>();
    }

    /**
     * 添加一个值
     */
    public void add(int value) {
        int bucket = value >>> 16;  // 高16位作为桶号
        int offset = value & 0xFFFF; // 低16位作为桶内偏移

        Container container = containers.get(bucket);
        if (container == null) {
            // 创建新的数组容器
            java.util.TreeSet<Integer> array = new java.util.TreeSet<>();
            array.add(offset);
            containers.put(bucket, new Container(ContainerType.ARRAY, array, 1));
        } else {
            addToContainer(container, offset);
        }
    }

    /**
     * 向容器添加值
     */
    private void addToContainer(Container container, int offset) {
        if (container.type == ContainerType.ARRAY) {
            @SuppressWarnings("unchecked")
            java.util.TreeSet<Integer> array = (java.util.TreeSet<Integer>) container.data;

            if (!array.contains(offset)) {
                array.add(offset);
                container.cardinality++;

                // 检查是否需要转换为位图容器
                if (container.cardinality > ARRAY_THRESHOLD) {
                    convertToBitmap(container, array);
                }
            }
        } else {
            // 位图容器
            AdvancedBitmap bitmap = (AdvancedBitmap) container.data;
            if (!bitmap.get(offset)) {
                bitmap.set(offset);
                container.cardinality++;
            }
        }
    }

    /**
     * 将数组容器转换为位图容器
     */
    private void convertToBitmap(Container container, java.util.TreeSet<Integer> array) {
        AdvancedBitmap bitmap = new AdvancedBitmap(BUCKET_SIZE);
        for (Integer offset : array) {
            bitmap.set(offset);
        }

        container.type = ContainerType.BITMAP;
        container.data = bitmap;
    }

    /**
     * 检查值是否存在
     */
    public boolean contains(int value) {
        int bucket = value >>> 16;
        int offset = value & 0xFFFF;

        Container container = containers.get(bucket);
        if (container == null) return false;

        if (container.type == ContainerType.ARRAY) {
            @SuppressWarnings("unchecked")
            java.util.TreeSet<Integer> array = (java.util.TreeSet<Integer>) container.data;
            return array.contains(offset);
        } else {
            AdvancedBitmap bitmap = (AdvancedBitmap) container.data;
            return bitmap.get(offset);
        }
    }

    /**
     * 获取基数（元素个数）
     */
    public long getCardinality() {
        long total = 0;
        for (Container container : containers.values()) {
            total += container.cardinality;
        }
        return total;
    }

    /**
     * 获取内存使用估算
     */
    public long getMemoryUsage() {
        long memory = 0;
        for (Container container : containers.values()) {
            if (container.type == ContainerType.ARRAY) {
                memory += container.cardinality * 4; // 每个int 4字节
            } else {
                memory += BUCKET_SIZE / 8; // 位图占用
            }
        }
        return memory;
    }

    /**
     * 打印统计信息
     */
    public void printStats() {
        System.out.println("Roaring Bitmap 统计:");
        System.out.println("容器数量: " + containers.size());
        System.out.println("总元素数: " + getCardinality());
        System.out.println("内存使用: " + getMemoryUsage() + " 字节");

        int arrayContainers = 0;
        int bitmapContainers = 0;

        for (Container container : containers.values()) {
            if (container.type == ContainerType.ARRAY) {
                arrayContainers++;
            } else {
                bitmapContainers++;
            }
        }

        System.out.println("数组容器: " + arrayContainers);
        System.out.println("位图容器: " + bitmapContainers);
    }
}
```

## 分布式系统中的位图应用

### 分布式位图

在分布式系统中，位图可以用于全局状态管理：

```java
/**
 * 分布式位图管理器
 * 使用分片技术将大位图分布到多个节点
 */
public class DistributedBitmapManager {

    private static class BitmapShard {
        private int shardId;
        private int startRange;
        private int endRange;
        private AdvancedBitmap bitmap;
        private String nodeId;

        BitmapShard(int shardId, int startRange, int endRange, String nodeId) {
            this.shardId = shardId;
            this.startRange = startRange;
            this.endRange = endRange;
            this.nodeId = nodeId;
            this.bitmap = new AdvancedBitmap(endRange - startRange);
        }

        boolean isInRange(int value) {
            return value >= startRange && value < endRange;
        }

        int getLocalIndex(int value) {
            return value - startRange;
        }
    }

    private java.util.List<BitmapShard> shards;
    private int totalRange;
    private int shardSize;

    public DistributedBitmapManager(int totalRange, int shardCount) {
        this.totalRange = totalRange;
        this.shardSize = (totalRange + shardCount - 1) / shardCount;
        this.shards = new java.util.ArrayList<>();

        // 创建分片
        for (int i = 0; i < shardCount; i++) {
            int startRange = i * shardSize;
            int endRange = Math.min(startRange + shardSize, totalRange);
            String nodeId = "node-" + i;

            shards.add(new BitmapShard(i, startRange, endRange, nodeId));
        }
    }

    /**
     * 设置位
     */
    public void set(int value) {
        BitmapShard shard = findShard(value);
        if (shard != null) {
            shard.bitmap.set(shard.getLocalIndex(value));
        }
    }

    /**
     * 检查位
     */
    public boolean get(int value) {
        BitmapShard shard = findShard(value);
        return shard != null && shard.bitmap.get(shard.getLocalIndex(value));
    }

    /**
     * 查找值所在的分片
     */
    private BitmapShard findShard(int value) {
        if (value < 0 || value >= totalRange) {
            return null;
        }

        int shardIndex = value / shardSize;
        return shardIndex < shards.size() ? shards.get(shardIndex) : null;
    }

    /**
     * 全局统计
     */
    public int globalCardinality() {
        int total = 0;
        for (BitmapShard shard : shards) {
            total += shard.bitmap.cardinality();
        }
        return total;
    }

    /**
     * 分片间的并集操作
     */
    public java.util.List<Integer> globalOr(java.util.List<Integer> values) {
        java.util.Map<BitmapShard, java.util.List<Integer>> shardValues = new java.util.HashMap<>();

        // 按分片分组值
        for (int value : values) {
            BitmapShard shard = findShard(value);
            if (shard != null) {
                shardValues.computeIfAbsent(shard, k -> new java.util.ArrayList<>())
                          .add(shard.getLocalIndex(value));
            }
        }

        // 收集结果
        java.util.List<Integer> result = new java.util.ArrayList<>();
        for (java.util.Map.Entry<BitmapShard, java.util.List<Integer>> entry : shardValues.entrySet()) {
            BitmapShard shard = entry.getKey();
            for (int localIndex : entry.getValue()) {
                if (shard.bitmap.get(localIndex)) {
                    result.add(shard.startRange + localIndex);
                }
            }
        }

        return result;
    }

    /**
     * 分片负载均衡信息
     */
    public void printShardInfo() {
        System.out.println("分布式位图分片信息:");
        for (BitmapShard shard : shards) {
            System.out.printf("分片%d [%d-%d): 节点=%s, 基数=%d\n",
                            shard.shardId, shard.startRange, shard.endRange,
                            shard.nodeId, shard.bitmap.cardinality());
        }
    }
}
```

## 实际案例分析

### 案例1：网页爬虫的URL去重

```java
/**
 * 网页爬虫URL去重系统
 * 结合布隆过滤器和位图进行高效去重
 */
public class WebCrawlerDeduplicator {

    private SimpleBloomFilter bloomFilter;
    private java.util.Map<Integer, AdvancedBitmap> hashBitmaps;
    private int urlCount;

    public WebCrawlerDeduplicator(int expectedUrls) {
        // 布隆过滤器用于快速初筛
        this.bloomFilter = new SimpleBloomFilter(expectedUrls, 0.01);

        // 使用多个位图处理哈希冲突
        this.hashBitmaps = new java.util.HashMap<>();
        this.urlCount = 0;
    }

    /**
     * 检查URL是否已经访问过
     * @param url 待检查的URL
     * @return true表示可能已访问，false表示肯定未访问
     */
    public boolean hasVisited(String url) {
        // 第一层过滤：布隆过滤器
        if (!bloomFilter.mightContain(url)) {
            return false; // 肯定没访问过
        }

        // 第二层验证：精确位图检查
        int hashCode = url.hashCode();
        int bitmapId = Math.abs(hashCode) % 100; // 分配到100个位图中
        int bitPosition = Math.abs(hashCode / 100) % (Integer.MAX_VALUE / 100);

        AdvancedBitmap bitmap = hashBitmaps.get(bitmapId);
        return bitmap != null && bitmap.get(bitPosition);
    }

    /**
     * 标记URL为已访问
     * @param url 要标记的URL
     */
    public void markVisited(String url) {
        // 添加到布隆过滤器
        bloomFilter.add(url);

        // 添加到精确位图
        int hashCode = url.hashCode();
        int bitmapId = Math.abs(hashCode) % 100;
        int bitPosition = Math.abs(hashCode / 100) % (Integer.MAX_VALUE / 100);

        AdvancedBitmap bitmap = hashBitmaps.computeIfAbsent(bitmapId,
            k -> new AdvancedBitmap(Integer.MAX_VALUE / 100));

        if (!bitmap.get(bitPosition)) {
            bitmap.set(bitPosition);
            urlCount++;
        }
    }

    /**
     * 获取统计信息
     */
    public void printStats() {
        System.out.println("爬虫去重统计:");
        System.out.println("已访问URL数量: " + urlCount);
        System.out.println("活跃位图数量: " + hashBitmaps.size());

        long totalMemory = 0;
        for (AdvancedBitmap bitmap : hashBitmaps.values()) {
            totalMemory += bitmap.size() / 8; // 估算内存使用
        }

        System.out.println("估算内存使用: " + (totalMemory / 1024 / 1024) + " MB");
    }
}
```

### 案例2：实时数据流的状态跟踪

```java
/**
 * 实时数据流状态跟踪器
 * 用于跟踪流式数据中的状态变化
 */
public class StreamStateTracker {

    private AdvancedBitmap currentState;
    private AdvancedBitmap previousState;
    private java.util.Queue<AdvancedBitmap> stateHistory;
    private int windowSize;
    private long timestamp;

    public StreamStateTracker(int maxIds, int windowSize) {
        this.currentState = new AdvancedBitmap(maxIds);
        this.previousState = new AdvancedBitmap(maxIds);
        this.stateHistory = new java.util.LinkedList<>();
        this.windowSize = windowSize;
        this.timestamp = System.currentTimeMillis();
    }

    /**
     * 更新状态
     */
    public void updateState(int id, boolean active) {
        if (active) {
            currentState.set(id);
        } else {
            currentState.clear(id);
        }
    }

    /**
     * 提交当前状态快照
     */
    public void commitSnapshot() {
        // 保存到历史
        AdvancedBitmap snapshot = new AdvancedBitmap(currentState.size());
        System.arraycopy(currentState.bits, 0, snapshot.bits, 0, currentState.bits.length);

        stateHistory.offer(snapshot);

        // 维护窗口大小
        if (stateHistory.size() > windowSize) {
            stateHistory.poll();
        }

        // 更新前一状态
        previousState = snapshot;
        timestamp = System.currentTimeMillis();
    }

    /**
     * 获取状态变化（新增的活跃ID）
     */
    public java.util.List<Integer> getNewActiveIds() {
        AdvancedBitmap newActive = currentState.andNot(previousState);
        return newActive.getSetBits();
    }

    /**
     * 获取状态变化（新增的非活跃ID）
     */
    public java.util.List<Integer> getNewInactiveIds() {
        AdvancedBitmap newInactive = previousState.andNot(currentState);
        return newInactive.getSetBits();
    }

    /**
     * 计算状态稳定性（连续相同状态的比例）
     */
    public double calculateStability() {
        if (stateHistory.size() < 2) return 1.0;

        int stableCount = 0;
        int totalComparisons = 0;

        AdvancedBitmap prev = null;
        for (AdvancedBitmap state : stateHistory) {
            if (prev != null) {
                AdvancedBitmap diff = state.xor(prev);
                int changes = diff.cardinality();
                int stable = state.size() - changes;

                stableCount += stable;
                totalComparisons += state.size();
            }
            prev = state;
        }

        return totalComparisons > 0 ? (double) stableCount / totalComparisons : 1.0;
    }

    /**
     * 获取活跃度趋势
     */
    public java.util.List<Double> getActivityTrend() {
        java.util.List<Double> trend = new java.util.ArrayList<>();

        for (AdvancedBitmap state : stateHistory) {
            double activity = (double) state.cardinality() / state.size();
            trend.add(activity);
        }

        return trend;
    }

    /**
     * 打印状态摘要
     */
    public void printStateSummary() {
        System.out.println("=== 流状态摘要 ===");
        System.out.println("时间戳: " + new java.util.Date(timestamp));
        System.out.println("当前活跃数: " + currentState.cardinality());
        System.out.println("状态稳定性: " + String.format("%.2f%%", calculateStability() * 100));

        java.util.List<Integer> newActive = getNewActiveIds();
        java.util.List<Integer> newInactive = getNewInactiveIds();

        System.out.println("新增活跃: " + newActive.size() + " 个");
        System.out.println("新增非活跃: " + newInactive.size() + " 个");

        if (!newActive.isEmpty()) {
            System.out.println("新增活跃ID: " + newActive.subList(0, Math.min(10, newActive.size())));
        }
    }
}
```

## 总结与最佳实践

位图作为一种高效的数据结构，在处理大规模数据时展现出了显著的优势。通过本文的深入分析，我们可以总结出以下关键点：

### 核心优势
1. **极致的空间效率**：相比传统数据结构，位图能够节省90%以上的内存空间
2. **卓越的查询性能**：O(1)时间复杂度的位操作确保了极快的查询速度
3. **天然的并行性**：位运算天然支持并行操作，便于利用现代处理器的并行计算能力
4. **简洁的集合运算**：通过基础的位运算即可实现复杂的集合操作

### 适用场景
- **海量数据去重**：如网页爬虫的URL去重、用户ID去重等
- **布隆过滤器**：作为布隆过滤器的核心组件，用于快速判断元素存在性
- **数据库索引**：特别适用于低基数列的索引优化
- **分布式系统**：用于全局状态管理和一致性检查
- **实时数据流**：跟踪流式数据中的状态变化

### 使用建议
1. **合理选择数据范围**：位图适合处理有明确上界的整数数据
2. **考虑数据密度**：对于稀疏数据，考虑使用压缩位图或Roaring Bitmap
3. **内存预估**：根据数据范围合理估算内存需求，避免过度分配
4. **并发安全**：在多线程环境中需要适当的同步机制
5. **持久化策略**：考虑位图数据的持久化和恢复机制

### 性能优化技巧
- 使用位移操作替代除法和取模运算
- 批量操作优于单个操作
- 合理利用CPU缓存行对齐
- 对于稀疏数据考虑压缩技术

位图数据结构凭借其独特的设计理念和卓越的性能表现，已经成为了现代大数据处理和高性能计算中不可或缺的工具。掌握位图的原理和应用，对于提升系统性能和优化资源使用具有重要意义。

随着数据规模的不断增长和计算需求的日益复杂，位图技术也在不断演进，从基础的位数组到压缩位图，再到分布式位图，每一项技术创新都为我们处理海量数据提供了更强大的工具。未来，位图技术将继续在人工智能、物联网、边缘计算等新兴领域发挥重要作用。