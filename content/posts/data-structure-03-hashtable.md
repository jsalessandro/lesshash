---
title: "数据结构详解：哈希表(Hash Table) - 快速查找的魔法"
date: 2025-01-03T10:03:00+08:00
draft: false
tags: ["数据结构", "哈希表", "Hash Table", "Java", "算法"]
categories: ["数据结构"]
series: ["数据结构入门教程"]
author: "lesshash"
description: "深入浅出讲解哈希表数据结构，从哈希函数到冲突解决，包含HashMap实现原理等实战技巧，让你彻底掌握快速查找的精髓"
---

## 🎯 什么是哈希表？

### 概念图解
#### 流程图表


**关系流向：**
```
A[Key键] → B[哈希函数]
B → C[哈希值/索引]
C → D[数组位置]
D → E[Value值]
F["apple"] → G[hash("apple")]
```

### 生活中的例子
哈希表就像生活中的各种"快速查找"系统：

```
📚 图书馆索引系统:
书名: "Java编程思想" → 索引号: J001 → 书架位置: 第3排第5层
搜索: O(1)时间直接定位，不用逐个查找

🏥 医院挂号系统:
身份证号: 110101199001011234 → 取后3位: 234 → 排队号: 234
根据号码直接找到对应窗口

🏪 超市条码系统:
商品条码: 6901234567890 → 哈希处理 → 数据库索引 → 商品信息
扫码瞬间显示价格和名称

🚗 停车场车位分配:
车牌号: 京A12345 → 哈希函数 → 车位编号: B-15
下次来直接去B-15找车
```

### 核心优势
- ⚡ **O(1)查找** - 平均情况下常数时间访问
- 🔍 **快速搜索** - 不需要比较，直接定位
- 💾 **空间换时间** - 用额外空间获得时间效率
- 🎯 **灵活键值** - 支持任意类型作为键

## 🏗️ 哈希表原理

### 基本结构
#### 流程图表


**关系流向：**
```
A[哈希表] → B[哈希函数]
A → C[存储数组]
A → D[冲突解决机制]
B → E[除法散列]
B → F[乘法散列]
```

### 哈希函数设计原则
```
1. 均匀性: 键值应该均匀分布在整个数组中
2. 确定性: 同一个键总是产生同一个哈希值
3. 高效性: 哈希函数本身计算要快
4. 雪崩效应: 输入的小变化导致输出大变化

常见哈希函数:
┌─────────────────────────────────┐
│ 除法散列: h(k) = k mod m        │
│ 乘法散列: h(k) = ⌊m(kA mod 1)⌋ │
│ 字符串散列: 多项式滚动哈希      │
└─────────────────────────────────┘
```

## 💻 哈希表实现

### 1. 简单哈希表实现

```java
/**
 * 简单哈希表实现 - 使用链地址法解决冲突
 */
public class SimpleHashTable<K, V> {

    // 哈希表节点
    private static class Node<K, V> {
        final K key;
        V value;
        Node<K, V> next;

        Node(K key, V value, Node<K, V> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }

    private Node<K, V>[] buckets;  // 存储桶数组
    private int size;              // 元素个数
    private static final int DEFAULT_CAPACITY = 16;
    private static final double LOAD_FACTOR = 0.75;

    @SuppressWarnings("unchecked")
    public SimpleHashTable() {
        this.buckets = new Node[DEFAULT_CAPACITY];
        this.size = 0;
    }

    /**
     * 哈希函数 - 将键转换为数组索引
     */
    private int hash(K key) {
        if (key == null) return 0;

        int hashCode = key.hashCode();
        // 使用位运算确保正数，并取模
        return (hashCode & 0x7FFFFFFF) % buckets.length;
    }

    /**
     * 插入键值对
     */
    public V put(K key, V value) {
        if (size >= buckets.length * LOAD_FACTOR) {
            resize();  // 负载因子超过阈值时扩容
        }

        int index = hash(key);
        Node<K, V> head = buckets[index];

        // 在链表中查找键是否已存在
        for (Node<K, V> node = head; node != null; node = node.next) {
            if (node.key.equals(key)) {
                V oldValue = node.value;
                node.value = value;  // 更新值
                return oldValue;
            }
        }

        // 键不存在，在链表头部插入新节点
        buckets[index] = new Node<>(key, value, head);
        size++;

        printInsertStep(key, value, index);
        return null;
    }

    /**
     * 获取值
     */
    public V get(K key) {
        int index = hash(key);
        Node<K, V> node = buckets[index];

        // 在链表中查找
        while (node != null) {
            if (node.key.equals(key)) {
                return node.value;
            }
            node = node.next;
        }

        return null;  // 未找到
    }

    /**
     * 删除键值对
     */
    public V remove(K key) {
        int index = hash(key);
        Node<K, V> head = buckets[index];

        if (head == null) return null;

        // 如果要删除的是第一个节点
        if (head.key.equals(key)) {
            buckets[index] = head.next;
            size--;
            return head.value;
        }

        // 在链表中查找要删除的节点
        Node<K, V> prev = head;
        Node<K, V> curr = head.next;

        while (curr != null) {
            if (curr.key.equals(key)) {
                prev.next = curr.next;
                size--;
                return curr.value;
            }
            prev = curr;
            curr = curr.next;
        }

        return null;
    }

    /**
     * 扩容操作
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        Node<K, V>[] oldBuckets = buckets;
        buckets = new Node[oldBuckets.length * 2];
        size = 0;

        System.out.println("扩容前容量: " + oldBuckets.length +
                          ", 扩容后容量: " + buckets.length);

        // 重新哈希所有元素
        for (Node<K, V> head : oldBuckets) {
            while (head != null) {
                put(head.key, head.value);
                head = head.next;
            }
        }
    }

    /**
     * 显示哈希表状态
     */
    public void display() {
        System.out.println("\n=== 哈希表状态 ===");
        System.out.println("容量: " + buckets.length + ", 大小: " + size +
                          ", 负载因子: " + String.format("%.2f", (double)size/buckets.length));

        for (int i = 0; i < buckets.length; i++) {
            System.out.print("桶[" + i + "]: ");
            Node<K, V> node = buckets[i];

            if (node == null) {
                System.out.println("空");
            } else {
                while (node != null) {
                    System.out.print("[" + node.key + ":" + node.value + "]");
                    if (node.next != null) {
                        System.out.print(" -> ");
                    }
                    node = node.next;
                }
                System.out.println();
            }
        }
    }

    private void printInsertStep(K key, V value, int index) {
        System.out.printf("插入 [%s:%s] 到桶[%d]%n", key, value, index);
    }

    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
}
```

### 2. 开放地址法实现

```java
/**
 * 开放地址法哈希表 - 使用线性探测解决冲突
 */
public class OpenAddressingHashTable<K, V> {

    private static class Entry<K, V> {
        K key;
        V value;
        boolean deleted;  // 标记删除

        Entry(K key, V value) {
            this.key = key;
            this.value = value;
            this.deleted = false;
        }
    }

    private Entry<K, V>[] table;
    private int size;
    private int capacity;
    private static final double LOAD_FACTOR = 0.5;

    @SuppressWarnings("unchecked")
    public OpenAddressingHashTable(int capacity) {
        this.capacity = capacity;
        this.table = new Entry[capacity];
        this.size = 0;
    }

    private int hash(K key) {
        return (key.hashCode() & 0x7FFFFFFF) % capacity;
    }

    /**
     * 线性探测找到下一个可用位置
     */
    private int probe(K key) {
        int index = hash(key);

        while (table[index] != null &&
               !table[index].deleted &&
               !table[index].key.equals(key)) {
            index = (index + 1) % capacity;  // 线性探测
        }

        return index;
    }

    /**
     * 插入操作
     */
    public V put(K key, V value) {
        if (size >= capacity * LOAD_FACTOR) {
            throw new RuntimeException("哈希表已满，需要扩容");
        }

        int index = probe(key);
        Entry<K, V> entry = table[index];

        if (entry == null || entry.deleted) {
            // 插入新元素
            table[index] = new Entry<>(key, value);
            size++;
            printProbeStep(key, value, index, "插入");
            return null;
        } else {
            // 更新现有元素
            V oldValue = entry.value;
            entry.value = value;
            printProbeStep(key, value, index, "更新");
            return oldValue;
        }
    }

    /**
     * 查找操作
     */
    public V get(K key) {
        int index = hash(key);
        int probeCount = 0;

        while (table[index] != null && probeCount < capacity) {
            if (!table[index].deleted && table[index].key.equals(key)) {
                System.out.printf("查找 %s: 探测%d次找到，位置[%d]%n",
                                key, probeCount + 1, index);
                return table[index].value;
            }
            index = (index + 1) % capacity;
            probeCount++;
        }

        System.out.printf("查找 %s: 未找到，探测了%d次%n", key, probeCount);
        return null;
    }

    /**
     * 删除操作（懒删除）
     */
    public V remove(K key) {
        int index = probe(key);
        Entry<K, V> entry = table[index];

        if (entry != null && !entry.deleted && entry.key.equals(key)) {
            entry.deleted = true;  // 标记删除，不真正删除
            size--;
            return entry.value;
        }

        return null;
    }

    /**
     * 显示哈希表状态
     */
    public void display() {
        System.out.println("\n=== 开放地址哈希表状态 ===");
        System.out.println("容量: " + capacity + ", 大小: " + size +
                          ", 负载因子: " + String.format("%.2f", (double)size/capacity));

        for (int i = 0; i < capacity; i++) {
            Entry<K, V> entry = table[i];
            if (entry == null) {
                System.out.println("位置[" + i + "]: 空");
            } else if (entry.deleted) {
                System.out.println("位置[" + i + "]: 已删除[" + entry.key + ":" + entry.value + "]");
            } else {
                System.out.println("位置[" + i + "]: [" + entry.key + ":" + entry.value + "]");
            }
        }
    }

    private void printProbeStep(K key, V value, int finalIndex, String operation) {
        int originalIndex = hash(key);
        int probeDistance = (finalIndex - originalIndex + capacity) % capacity;
        System.out.printf("%s [%s:%s]: 原始位置[%d] -> 最终位置[%d], 探测距离: %d%n",
                         operation, key, value, originalIndex, finalIndex, probeDistance);
    }
}
```

### 3. 字符串哈希函数

```java
/**
 * 专门针对字符串的哈希函数实现
 */
public class StringHashFunctions {

    /**
     * 简单累加哈希（容易冲突）
     */
    public static int simpleHash(String str) {
        int hash = 0;
        for (char c : str.toCharArray()) {
            hash += c;
        }
        return hash;
    }

    /**
     * 多项式滚动哈希（推荐）
     */
    public static int polynomialHash(String str) {
        final int BASE = 31;  // 常用质数
        int hash = 0;

        for (char c : str.toCharArray()) {
            hash = hash * BASE + c;
        }

        return hash;
    }

    /**
     * FNV哈希算法
     */
    public static int fnvHash(String str) {
        final int FNV_PRIME = 16777619;
        final int OFFSET_BASIS = (int) 2166136261L;

        int hash = OFFSET_BASIS;
        for (byte b : str.getBytes()) {
            hash ^= b;
            hash *= FNV_PRIME;
        }

        return hash;
    }

    /**
     * DJB2哈希算法
     */
    public static int djb2Hash(String str) {
        int hash = 5381;

        for (char c : str.toCharArray()) {
            hash = ((hash << 5) + hash) + c; // hash * 33 + c
        }

        return hash;
    }

    /**
     * 测试不同哈希函数的分布均匀性
     */
    public static void testHashDistribution() {
        String[] testWords = {
            "apple", "banana", "cherry", "date", "elderberry",
            "fig", "grape", "honeydew", "kiwi", "lemon",
            "mango", "nectarine", "orange", "papaya", "quince"
        };

        int buckets = 10;

        System.out.println("=== 哈希函数分布测试 ===\n");

        // 测试各种哈希函数
        testHashFunction("简单累加", testWords, buckets, StringHashFunctions::simpleHash);
        testHashFunction("多项式滚动", testWords, buckets, StringHashFunctions::polynomialHash);
        testHashFunction("FNV算法", testWords, buckets, StringHashFunctions::fnvHash);
        testHashFunction("DJB2算法", testWords, buckets, StringHashFunctions::djb2Hash);
    }

    private static void testHashFunction(String name, String[] words, int buckets,
                                       java.util.function.Function<String, Integer> hashFunc) {
        int[] distribution = new int[buckets];

        System.out.println(name + "哈希分布:");
        for (String word : words) {
            int hash = Math.abs(hashFunc.apply(word)) % buckets;
            distribution[hash]++;
            System.out.printf("  %s -> %d%n", word, hash);
        }

        // 显示分布统计
        System.out.print("桶分布: ");
        for (int count : distribution) {
            System.out.print(count + " ");
        }

        // 计算方差（衡量分布均匀性）
        double mean = (double) words.length / buckets;
        double variance = 0;
        for (int count : distribution) {
            variance += Math.pow(count - mean, 2);
        }
        variance /= buckets;

        System.out.printf(" (方差: %.2f)%n%n", variance);
    }
}
```

## 🔥 冲突解决策略

### 1. 链地址法演示

```java
/**
 * 链地址法冲突演示
 */
public class ChainHashingDemo {

    public static void demonstrateChaining() {
        SimpleHashTable<String, Integer> hashTable = new SimpleHashTable<>();

        System.out.println("=== 链地址法冲突解决演示 ===\n");

        // 故意选择会产生冲突的键
        String[] keys = {"cat", "dog", "rat", "bat"};  // 假设这些键会哈希到相同位置
        Integer[] values = {1, 2, 3, 4};

        System.out.println("插入可能产生冲突的键值对:");
        for (int i = 0; i < keys.length; i++) {
            hashTable.put(keys[i], values[i]);
        }

        hashTable.display();

        /*
        冲突处理过程：
        1. "cat" -> hash(cat) = 2, 插入到桶[2]
        2. "dog" -> hash(dog) = 2, 冲突！在桶[2]链表头插入
        3. "rat" -> hash(rat) = 2, 冲突！在桶[2]链表头插入
        4. "bat" -> hash(bat) = 2, 冲突！在桶[2]链表头插入

        最终桶[2]: [bat:4] -> [rat:3] -> [dog:2] -> [cat:1]
        */

        System.out.println("\n查找测试:");
        for (String key : keys) {
            Integer value = hashTable.get(key);
            System.out.println("get(\"" + key + "\") = " + value);
        }
    }
}
```

### 2. 开放地址法演示

```java
/**
 * 开放地址法演示
 */
public class OpenAddressingDemo {

    public static void demonstrateLinearProbing() {
        OpenAddressingHashTable<String, Integer> hashTable =
            new OpenAddressingHashTable<>(7);  // 小容量便于演示

        System.out.println("=== 线性探测冲突解决演示 ===\n");

        String[] keys = {"apple", "banana", "cherry", "date"};
        Integer[] values = {1, 2, 3, 4};

        System.out.println("插入演示:");
        for (int i = 0; i < keys.length; i++) {
            hashTable.put(keys[i], values[i]);
        }

        hashTable.display();

        /*
        线性探测过程：
        1. "apple" -> hash = 3, 位置[3]空闲，插入
        2. "banana" -> hash = 3, 位置[3]被占用，探测到位置[4]，插入
        3. "cherry" -> hash = 3, 位置[3],[4]被占用，探测到位置[5]，插入
        4. "date" -> hash = 3, 探测到位置[6]，插入

        探测序列示例:
        原始哈希值3 -> 探测序列: 3, 4, 5, 6, 0, 1, 2, 3...
        */

        System.out.println("\n查找演示:");
        for (String key : keys) {
            Integer value = hashTable.get(key);
        }
    }
}
```

## 📊 Java HashMap 源码解析

### HashMap 核心原理

```java
/**
 * 模拟Java 8 HashMap的核心实现
 */
public class MyHashMap<K, V> {

    // 红黑树阈值
    static final int TREEIFY_THRESHOLD = 8;   // 链表转红黑树阈值
    static final int UNTREEIFY_THRESHOLD = 6; // 红黑树转链表阈值
    static final int MIN_TREEIFY_CAPACITY = 64;

    // 哈希表节点
    static class Node<K, V> {
        final int hash;
        final K key;
        V value;
        Node<K, V> next;

        Node(int hash, K key, V value, Node<K, V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }

    private Node<K, V>[] table;
    private int size;
    private int threshold;  // 扩容阈值
    private float loadFactor = 0.75f;

    /**
     * HashMap的哈希函数（扰动函数）
     */
    static final int hash(Object key) {
        int h;
        // null键映射到0，其他键做高16位与低16位异或扰动
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }

    /**
     * 确定在数组中的索引位置
     */
    private int indexFor(int hash, int length) {
        return hash & (length - 1);  // 等价于 hash % length，但更高效
    }

    /**
     * 插入或更新键值对
     */
    public V put(K key, V value) {
        return putVal(hash(key), key, value);
    }

    private V putVal(int hash, K key, V value) {
        Node<K, V>[] tab = table;
        int n = (tab == null) ? 0 : tab.length;

        // 初始化或扩容
        if (tab == null || n == 0) {
            tab = resize();
            n = tab.length;
        }

        int index = indexFor(hash, n);
        Node<K, V> p = tab[index];

        if (p == null) {
            // 位置为空，直接插入
            tab[index] = new Node<>(hash, key, value, null);
        } else {
            Node<K, V> e = null;

            // 检查第一个节点
            if (p.hash == hash && Objects.equals(p.key, key)) {
                e = p;
            } else {
                // 遍历链表或红黑树
                for (int binCount = 0; ; ++binCount) {
                    if ((e = p.next) == null) {
                        // 链表末尾，插入新节点
                        p.next = new Node<>(hash, key, value, null);

                        // 检查是否需要树化
                        if (binCount >= TREEIFY_THRESHOLD - 1) {
                            treeifyBin(tab, index);
                        }
                        break;
                    }

                    // 找到相同键
                    if (e.hash == hash && Objects.equals(e.key, key)) {
                        break;
                    }
                    p = e;
                }
            }

            // 更新已存在的键
            if (e != null) {
                V oldValue = e.value;
                e.value = value;
                return oldValue;
            }
        }

        ++size;
        if (size > threshold) {
            resize();
        }

        return null;
    }

    /**
     * 扩容操作
     */
    @SuppressWarnings("unchecked")
    private Node<K, V>[] resize() {
        Node<K, V>[] oldTab = table;
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        int oldThr = threshold;

        int newCap, newThr = 0;

        if (oldCap > 0) {
            newCap = oldCap << 1;  // 容量翻倍
            newThr = oldThr << 1;  // 阈值翻倍
        } else {
            newCap = 16;  // 默认初始容量
            newThr = (int)(newCap * loadFactor);
        }

        threshold = newThr;
        Node<K, V>[] newTab = new Node[newCap];
        table = newTab;

        // 重新哈希所有元素
        if (oldTab != null) {
            for (int j = 0; j < oldCap; ++j) {
                Node<K, V> e = oldTab[j];
                if (e != null) {
                    oldTab[j] = null;

                    if (e.next == null) {
                        // 单个节点
                        newTab[indexFor(e.hash, newCap)] = e;
                    } else {
                        // 链表需要分裂为两条链表
                        splitChain(e, newTab, j, oldCap);
                    }
                }
            }
        }

        System.out.printf("HashMap扩容: %d -> %d%n", oldCap, newCap);
        return newTab;
    }

    /**
     * 链表分裂（HashMap 1.8优化）
     */
    private void splitChain(Node<K, V> head, Node<K, V>[] newTab, int oldIndex, int oldCap) {
        Node<K, V> loHead = null, loTail = null;  // 低位链表
        Node<K, V> hiHead = null, hiTail = null;  // 高位链表

        Node<K, V> next;
        Node<K, V> e = head;

        do {
            next = e.next;
            // 根据扩容位判断分到哪条链表
            if ((e.hash & oldCap) == 0) {
                if (loTail == null) {
                    loHead = e;
                } else {
                    loTail.next = e;
                }
                loTail = e;
            } else {
                if (hiTail == null) {
                    hiHead = e;
                } else {
                    hiTail.next = e;
                }
                hiTail = e;
            }
        } while ((e = next) != null);

        // 放置到新数组中
        if (loTail != null) {
            loTail.next = null;
            newTab[oldIndex] = loHead;  // 原位置
        }
        if (hiTail != null) {
            hiTail.next = null;
            newTab[oldIndex + oldCap] = hiHead;  // 原位置+旧容量
        }
    }

    private void treeifyBin(Node<K, V>[] tab, int index) {
        // 简化实现，实际会转换为红黑树
        System.out.println("位置 " + index + " 的链表过长，转换为红黑树");
    }
}
```

## 📈 性能分析与优化

### 负载因子的影响

```java
/**
 * 负载因子性能测试
 */
public class LoadFactorAnalysis {

    public static void analyzeLoadFactor() {
        System.out.println("=== 负载因子对性能的影响 ===\n");

        double[] loadFactors = {0.5, 0.75, 0.9, 1.0};
        int testSize = 10000;

        for (double lf : loadFactors) {
            testLoadFactor(lf, testSize);
        }
    }

    private static void testLoadFactor(double loadFactor, int testSize) {
        // 简化的哈希表测试
        Map<Integer, String> map = new HashMap<>((int)(testSize / loadFactor));

        long startTime = System.nanoTime();

        // 插入测试
        for (int i = 0; i < testSize; i++) {
            map.put(i, "value" + i);
        }

        long insertTime = System.nanoTime() - startTime;

        startTime = System.nanoTime();

        // 查找测试
        for (int i = 0; i < testSize; i++) {
            map.get(i);
        }

        long searchTime = System.nanoTime() - startTime;

        System.out.printf("负载因子 %.2f: 插入%6.2fms, 查找%6.2fms%n",
                         loadFactor, insertTime/1e6, searchTime/1e6);
    }
}
```

### 哈希冲突统计

```java
/**
 * 哈希冲突统计分析
 */
public class HashCollisionAnalysis {

    public static void analyzeCollisions() {
        int[] tableSizes = {16, 32, 64, 128};
        int dataSize = 100;

        for (int tableSize : tableSizes) {
            analyzeCollisionForSize(tableSize, dataSize);
        }
    }

    private static void analyzeCollisionForSize(int tableSize, int dataSize) {
        int[] buckets = new int[tableSize];
        int collisions = 0;

        System.out.println("\n表大小: " + tableSize + ", 数据量: " + dataSize);

        // 模拟插入随机数据
        Random random = new Random(42);  // 固定种子，结果可重现
        for (int i = 0; i < dataSize; i++) {
            int value = random.nextInt(100000);
            int index = Math.abs(value) % tableSize;

            if (buckets[index] > 0) {
                collisions++;
            }
            buckets[index]++;
        }

        // 统计分布
        int emptyBuckets = 0;
        int maxChainLength = 0;
        for (int count : buckets) {
            if (count == 0) {
                emptyBuckets++;
            }
            maxChainLength = Math.max(maxChainLength, count);
        }

        double loadFactor = (double) dataSize / tableSize;
        System.out.printf("负载因子: %.2f%n", loadFactor);
        System.out.printf("冲突次数: %d (%.1f%%)%n", collisions, 100.0 * collisions / dataSize);
        System.out.printf("空桶数量: %d/%d (%.1f%%)%n", emptyBuckets, tableSize, 100.0 * emptyBuckets / tableSize);
        System.out.printf("最大链长: %d%n", maxChainLength);

        // 显示分布直方图
        printDistributionHistogram(buckets);
    }

    private static void printDistributionHistogram(int[] buckets) {
        System.out.println("桶分布直方图:");
        for (int i = 0; i < Math.min(buckets.length, 16); i++) {
            System.out.printf("桶[%2d]: %s (%d)%n",
                             i,
                             "*".repeat(Math.min(buckets[i], 20)),
                             buckets[i]);
        }
        if (buckets.length > 16) {
            System.out.println("... (显示前16个桶)");
        }
    }
}
```

## 🎯 实际应用场景

### 1. 缓存系统

```java
/**
 * 基于哈希表的LRU缓存实现
 */
public class LRUCache<K, V> {

    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev, next;

        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<K, Node<K, V>> cache;
    private final Node<K, V> head, tail;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();

        // 创建双向链表的头尾节点
        this.head = new Node<>(null, null);
        this.tail = new Node<>(null, null);
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K, V> node = cache.get(key);
        if (node == null) {
            return null;
        }

        // 移动到链表头部（表示最近使用）
        moveToHead(node);
        return node.value;
    }

    public void put(K key, V value) {
        Node<K, V> node = cache.get(key);

        if (node != null) {
            // 更新已存在的节点
            node.value = value;
            moveToHead(node);
        } else {
            // 添加新节点
            Node<K, V> newNode = new Node<>(key, value);

            if (cache.size() >= capacity) {
                // 删除最久未使用的节点（链表尾部）
                Node<K, V> last = removeTail();
                cache.remove(last.key);
            }

            cache.put(key, newNode);
            addToHead(newNode);
        }
    }

    private void addToHead(Node<K, V> node) {
        node.prev = head;
        node.next = head.next;
        head.next.prev = node;
        head.next = node;
    }

    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void moveToHead(Node<K, V> node) {
        removeNode(node);
        addToHead(node);
    }

    private Node<K, V> removeTail() {
        Node<K, V> last = tail.prev;
        removeNode(last);
        return last;
    }

    public void display() {
        System.out.print("LRU缓存 (最新 -> 最旧): ");
        Node<K, V> current = head.next;
        while (current != tail) {
            System.out.print("[" + current.key + ":" + current.value + "] ");
            current = current.next;
        }
        System.out.println();
    }
}
```

### 2. 单词频次统计

```java
/**
 * 文本分析工具 - 统计单词频次
 */
public class WordFrequencyAnalyzer {

    public static Map<String, Integer> analyzeText(String text) {
        Map<String, Integer> wordFreq = new HashMap<>();

        // 文本预处理：转小写，移除标点符号，分词
        String[] words = text.toLowerCase()
                            .replaceAll("[^a-zA-Z\\s]", "")
                            .split("\\s+");

        for (String word : words) {
            if (!word.isEmpty()) {
                wordFreq.put(word, wordFreq.getOrDefault(word, 0) + 1);
            }
        }

        return wordFreq;
    }

    public static void printTopWords(Map<String, Integer> wordFreq, int topN) {
        System.out.println("词频统计 Top " + topN + ":");

        wordFreq.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .limit(topN)
                .forEach(entry ->
                    System.out.printf("%-15s: %d%n", entry.getKey(), entry.getValue()));
    }

    public static void demonstrateWordAnalysis() {
        String text = """
            HashMap is a widely used data structure in Java programming.
            HashMap provides O(1) average time complexity for basic operations.
            The performance of HashMap depends on the hash function quality.
            HashMap uses an array of buckets to store key-value pairs.
            When hash collisions occur, HashMap uses chaining or open addressing.
            HashMap is not synchronized and not thread-safe by default.
            """;

        System.out.println("=== 文本词频分析演示 ===");
        System.out.println("原文本:");
        System.out.println(text);

        Map<String, Integer> wordFreq = analyzeText(text);
        printTopWords(wordFreq, 10);

        System.out.println("\n统计信息:");
        System.out.println("总词数: " + wordFreq.values().stream().mapToInt(Integer::intValue).sum());
        System.out.println("不重复词数: " + wordFreq.size());
    }
}
```

## ✅ 优缺点总结

### 优点
- ✅ **超快查找** - 平均O(1)时间复杂度
- ✅ **简单实现** - 概念清晰，实现相对简单
- ✅ **灵活键类型** - 支持任意可哈希的数据类型
- ✅ **动态扩容** - 可根据数据量自动调整大小
- ✅ **广泛应用** - 数据库索引、缓存系统等

### 缺点
- ❌ **空间开销** - 需要额外空间，负载因子不能太高
- ❌ **哈希冲突** - 最坏情况退化为O(n)
- ❌ **无序存储** - 不保持插入顺序
- ❌ **哈希函数依赖** - 性能严重依赖哈希函数质量
- ❌ **扩容成本** - 需要重新哈希所有元素

### 选择指南
```
使用哈希表的场景:
✓ 需要快速的插入、删除、查找操作
✓ 数据量大，对时间复杂度要求高
✓ 键值对存储，如配置管理、缓存
✓ 去重操作，如Set的实现

不适合的场景:
✗ 需要保持数据有序
✗ 频繁的范围查询
✗ 内存空间严格限制
✗ 键的比较代价很高
```

## 🧠 记忆技巧

### 核心概念记忆
> **"键经哈希变索引，数组定位存键值"**

### 冲突解决记忆
```
链地址法: 拉链子，挂链表
开放地址法: 占位了，往后找
```

### 性能记忆口诀
> **"哈希表查找快如闪，冲突处理是关键"**

---

哈希表是计算机科学中最重要的数据结构之一，理解其原理和实现对于成为优秀程序员至关重要。掌握了哈希表，你就掌握了快速数据访问的核心技术！