---
title: "数据结构入门教程(11)：Redis常用数据类型背后的数据结构深度解析"
date: 2025-01-18T11:00:00+08:00
draft: false
categories: ["数据结构", "Redis"]
tags: ["Redis", "数据结构", "算法", "Java", "NoSQL", "内存数据库", "高性能"]
series: ["数据结构入门教程"]
description: "深入剖析Redis五大数据类型背后的数据结构实现原理，包括字符串、列表、哈希、集合、有序集合的底层存储机制和性能优化"
keywords: ["Redis", "数据结构", "SDS", "ziplist", "skiplist", "hashtable", "intset"]
---

## Redis简介与核心思想

Redis(Remote Dictionary Server)是一个开源的内存数据结构存储系统，可以用作数据库、缓存和消息中间件。Redis的高性能来源于其巧妙的数据结构设计和内存存储特性。

### Redis的核心设计哲学

```mermaid
graph TD
    A[Redis核心设计] --> B[内存存储]
    A --> C[多数据结构]
    A --> D[高性能算法]
    A --> E[空间优化]

    B --> B1[纳秒级访问]
    B --> B2[无磁盘IO]

    C --> C1[String字符串]
    C --> C2[List列表]
    C --> C3[Hash散列]
    C --> C4[Set集合]
    C --> C5[ZSet有序集合]

    D --> D1[O1时间复杂度]
    D --> D2[跳表算法]
    D --> D3[渐进式rehash]

    E --> E1[压缩列表]
    E --> E2[整数集合]
    E --> E3[动态字符串]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e8
    style E fill:#fce4ec
```

## Redis数据类型与底层数据结构映射

### 数据结构对应关系总览

| Redis数据类型 | 底层数据结构 | 使用场景 | 主要算法 |
|--------------|-------------|----------|----------|
| String | SDS (Simple Dynamic String) | 缓存、计数器、分布式锁 | 动态扩容 |
| List | ziplist / quicklist | 消息队列、时间线、栈/队列 | 双向链表 + 压缩列表 |
| Hash | ziplist / hashtable | 对象存储、购物车 | 哈希表 + 渐进式rehash |
| Set | intset / hashtable | 标签、好友关系、去重 | 哈希表 / 整数集合 |
| ZSet | ziplist / skiplist + hashtable | 排行榜、延时队列 | 跳表 + 哈希表 |

## 1. String类型 - SDS动态字符串

### SDS(Simple Dynamic String)结构设计

Redis没有直接使用C语言的字符串，而是构建了SDS这种数据结构。

```java
/**
 * SDS(Simple Dynamic String) 的Java模拟实现
 * Redis中字符串的底层实现
 */
public class SDS {
    private int len;        // 已使用长度
    private int free;       // 剩余可用长度
    private char[] buf;     // 字符数组

    /**
     * 构造函数
     * @param initString 初始字符串
     */
    public SDS(String initString) {
        if (initString == null) {
            initString = "";
        }

        this.len = initString.length();
        this.free = len;  // 预分配相同大小的空间
        this.buf = new char[len + free + 1];  // +1 为null终止符

        // 复制字符串内容
        for (int i = 0; i < len; i++) {
            buf[i] = initString.charAt(i);
        }
        buf[len] = '\0';  // null终止符
    }

    /**
     * 追加字符串 - 动态扩容机制
     * @param appendStr 要追加的字符串
     */
    public void append(String appendStr) {
        if (appendStr == null || appendStr.isEmpty()) {
            return;
        }

        int appendLen = appendStr.length();
        int newLen = len + appendLen;

        // 检查是否需要扩容
        if (free < appendLen) {
            // Redis的空间预分配策略
            expandCapacity(newLen);
        }

        // 追加新内容
        for (int i = 0; i < appendLen; i++) {
            buf[len + i] = appendStr.charAt(i);
        }

        // 更新长度信息
        free -= appendLen;
        len += appendLen;
        buf[len] = '\0';  // 更新null终止符位置
    }

    /**
     * Redis的空间预分配策略
     * @param newLen 新长度
     */
    private void expandCapacity(int newLen) {
        int newCapacity;

        // Redis的扩容策略：
        // 1. 如果新长度小于1MB，则分配新长度的2倍空间
        // 2. 如果新长度大于等于1MB，则额外分配1MB空间
        if (newLen < 1024 * 1024) {
            newCapacity = newLen * 2;
        } else {
            newCapacity = newLen + 1024 * 1024;
        }

        // 创建新数组并复制内容
        char[] newBuf = new char[newCapacity + 1];
        System.arraycopy(buf, 0, newBuf, 0, len);

        this.buf = newBuf;
        this.free = newCapacity - len;

        System.out.println("SDS扩容: 新容量=" + newCapacity + ", 可用空间=" + free);
    }

    /**
     * 获取字符串长度 - O(1)时间复杂度
     * @return 字符串长度
     */
    public int length() {
        return len;  // 直接返回保存的长度，不需要遍历
    }

    /**
     * 获取剩余空间
     * @return 剩余可用空间
     */
    public int getFreeSpace() {
        return free;
    }

    /**
     * 转换为Java字符串
     * @return Java字符串
     */
    @Override
    public String toString() {
        return new String(buf, 0, len);
    }

    /**
     * SDS的优势演示
     */
    public static void demonstrateSDSAdvantages() {
        System.out.println("=== SDS vs C字符串优势演示 ===");

        SDS sds = new SDS("Hello");
        System.out.println("初始SDS: " + sds);
        System.out.println("长度获取: O(1) -> " + sds.length());
        System.out.println("剩余空间: " + sds.getFreeSpace());

        // 多次追加操作
        String[] appends = {" Redis", " is", " awesome", "!"};

        for (String append : appends) {
            System.out.println("\n追加: \"" + append + "\"");
            sds.append(append);
            System.out.println("结果: " + sds);
            System.out.println("长度: " + sds.length() + ", 剩余: " + sds.getFreeSpace());
        }

        // 性能优势：
        // 1. 长度获取：O(1) vs C字符串的O(n)
        // 2. 空间预分配：减少内存重新分配次数
        // 3. 二进制安全：可以存储任何数据
        // 4. 缓冲区溢出保护：自动扩容
    }
}
```

### String类型的应用实现

```java
/**
 * Redis String类型的应用实现示例
 */
public class RedisStringApplications {

    /**
     * 分布式计数器
     */
    public static class DistributedCounter {
        private SDS counter;

        public DistributedCounter() {
            this.counter = new SDS("0");
        }

        public synchronized long increment() {
            long currentValue = Long.parseLong(counter.toString());
            currentValue++;

            // 更新SDS内容
            this.counter = new SDS(String.valueOf(currentValue));
            return currentValue;
        }

        public long getValue() {
            return Long.parseLong(counter.toString());
        }
    }

    /**
     * 缓存系统
     */
    public static class SimpleCache {
        private Map<String, SDS> cache;
        private Map<String, Long> expireTime;

        public SimpleCache() {
            this.cache = new ConcurrentHashMap<>();
            this.expireTime = new ConcurrentHashMap<>();
        }

        public void set(String key, String value, long ttlSeconds) {
            cache.put(key, new SDS(value));
            expireTime.put(key, System.currentTimeMillis() + ttlSeconds * 1000);
        }

        public String get(String key) {
            // 检查是否过期
            Long expireAt = expireTime.get(key);
            if (expireAt != null && System.currentTimeMillis() > expireAt) {
                cache.remove(key);
                expireTime.remove(key);
                return null;
            }

            SDS value = cache.get(key);
            return value != null ? value.toString() : null;
        }
    }
}
```

## 2. List类型 - QuickList(ziplist + linkedlist)

### QuickList结构设计

Redis3.2之后，List的底层实现改为QuickList，它是ziplist和linkedlist的结合。

```java
/**
 * QuickList的Java模拟实现
 * 结合了ziplist的内存效率和linkedlist的灵活性
 */
public class QuickList<T> {

    /**
     * QuickList节点
     */
    private static class QuickListNode<T> {
        ZipList<T> ziplist;           // 压缩列表
        QuickListNode<T> prev;        // 前驱节点
        QuickListNode<T> next;        // 后继节点
        int count;                    // 此节点中的元素个数

        QuickListNode() {
            this.ziplist = new ZipList<>();
            this.count = 0;
        }
    }

    /**
     * 压缩列表 - 内存紧凑的数据结构
     */
    private static class ZipList<T> {
        private static final int ZIPLIST_MAX_SIZE = 8192;  // 最大8KB
        private List<T> entries;

        ZipList() {
            this.entries = new ArrayList<>();
        }

        boolean isFull() {
            // 简化判断：假设每个元素平均占用100字节
            return entries.size() * 100 >= ZIPLIST_MAX_SIZE;
        }

        void addFirst(T element) {
            entries.add(0, element);
        }

        void addLast(T element) {
            entries.add(element);
        }

        T removeFirst() {
            return entries.isEmpty() ? null : entries.remove(0);
        }

        T removeLast() {
            return entries.isEmpty() ? null : entries.remove(entries.size() - 1);
        }

        boolean isEmpty() {
            return entries.isEmpty();
        }

        int size() {
            return entries.size();
        }

        T get(int index) {
            return entries.get(index);
        }
    }

    private QuickListNode<T> head;    // 头节点
    private QuickListNode<T> tail;    // 尾节点
    private int count;                // 总元素个数
    private int nodeCount;            // 节点个数

    public QuickList() {
        this.head = null;
        this.tail = null;
        this.count = 0;
        this.nodeCount = 0;
    }

    /**
     * 左侧插入(lpush)
     * @param element 要插入的元素
     */
    public void lpush(T element) {
        if (head == null || head.ziplist.isFull()) {
            // 创建新节点
            QuickListNode<T> newNode = new QuickListNode<>();
            newNode.ziplist.addFirst(element);
            newNode.count = 1;

            if (head == null) {
                // 第一个节点
                head = tail = newNode;
            } else {
                // 插入到头部
                newNode.next = head;
                head.prev = newNode;
                head = newNode;
            }
            nodeCount++;
        } else {
            // 在现有头节点插入
            head.ziplist.addFirst(element);
            head.count++;
        }
        count++;
    }

    /**
     * 右侧插入(rpush)
     * @param element 要插入的元素
     */
    public void rpush(T element) {
        if (tail == null || tail.ziplist.isFull()) {
            // 创建新节点
            QuickListNode<T> newNode = new QuickListNode<>();
            newNode.ziplist.addLast(element);
            newNode.count = 1;

            if (tail == null) {
                // 第一个节点
                head = tail = newNode;
            } else {
                // 插入到尾部
                tail.next = newNode;
                newNode.prev = tail;
                tail = newNode;
            }
            nodeCount++;
        } else {
            // 在现有尾节点插入
            tail.ziplist.addLast(element);
            tail.count++;
        }
        count++;
    }

    /**
     * 左侧弹出(lpop)
     * @return 弹出的元素
     */
    public T lpop() {
        if (head == null) {
            return null;
        }

        T element = head.ziplist.removeFirst();
        head.count--;
        count--;

        // 如果节点为空，删除节点
        if (head.ziplist.isEmpty()) {
            QuickListNode<T> nextNode = head.next;
            if (nextNode != null) {
                nextNode.prev = null;
            } else {
                tail = null;  // 列表变空
            }
            head = nextNode;
            nodeCount--;
        }

        return element;
    }

    /**
     * 右侧弹出(rpop)
     * @return 弹出的元素
     */
    public T rpop() {
        if (tail == null) {
            return null;
        }

        T element = tail.ziplist.removeLast();
        tail.count--;
        count--;

        // 如果节点为空，删除节点
        if (tail.ziplist.isEmpty()) {
            QuickListNode<T> prevNode = tail.prev;
            if (prevNode != null) {
                prevNode.next = null;
            } else {
                head = null;  // 列表变空
            }
            tail = prevNode;
            nodeCount--;
        }

        return element;
    }

    /**
     * 获取指定位置的元素
     * @param index 索引
     * @return 元素
     */
    public T lindex(int index) {
        if (index < 0 || index >= count) {
            return null;
        }

        QuickListNode<T> current = head;
        int currentIndex = 0;

        while (current != null) {
            if (currentIndex + current.count > index) {
                // 元素在当前节点中
                int localIndex = index - currentIndex;
                return current.ziplist.get(localIndex);
            }
            currentIndex += current.count;
            current = current.next;
        }

        return null;
    }

    /**
     * 获取列表长度
     * @return 列表长度
     */
    public int size() {
        return count;
    }

    /**
     * 获取节点数
     * @return 节点数
     */
    public int getNodeCount() {
        return nodeCount;
    }

    /**
     * 打印QuickList结构信息
     */
    public void printStructure() {
        System.out.println("=== QuickList结构信息 ===");
        System.out.println("总元素数: " + count);
        System.out.println("节点数: " + nodeCount);

        QuickListNode<T> current = head;
        int nodeIndex = 0;

        while (current != null) {
            System.out.println("节点" + nodeIndex + ": " + current.count + "个元素");
            nodeIndex++;
            current = current.next;
        }
    }
}
```

### List类型的应用实现

```java
/**
 * Redis List类型的应用实现
 */
public class RedisListApplications {

    /**
     * 消息队列实现
     */
    public static class MessageQueue<T> {
        private QuickList<T> queue;

        public MessageQueue() {
            this.queue = new QuickList<>();
        }

        /**
         * 生产消息
         * @param message 消息
         */
        public void produce(T message) {
            queue.rpush(message);  // 右侧入队
            System.out.println("生产消息: " + message);
        }

        /**
         * 消费消息
         * @return 消息
         */
        public T consume() {
            T message = queue.lpop();  // 左侧出队
            if (message != null) {
                System.out.println("消费消息: " + message);
            }
            return message;
        }

        /**
         * 获取队列长度
         * @return 队列长度
         */
        public int getQueueLength() {
            return queue.size();
        }
    }

    /**
     * 最近访问记录
     */
    public static class RecentAccessLog {
        private QuickList<String> accessLog;
        private int maxSize;

        public RecentAccessLog(int maxSize) {
            this.accessLog = new QuickList<>();
            this.maxSize = maxSize;
        }

        /**
         * 记录访问
         * @param userId 用户ID
         */
        public void recordAccess(String userId) {
            // 添加新记录
            accessLog.lpush(userId);

            // 保持最大长度
            while (accessLog.size() > maxSize) {
                accessLog.rpop();
            }
        }

        /**
         * 获取最近访问记录
         * @param count 记录数
         * @return 访问记录列表
         */
        public List<String> getRecentAccess(int count) {
            List<String> result = new ArrayList<>();
            int size = Math.min(count, accessLog.size());

            for (int i = 0; i < size; i++) {
                String record = accessLog.lindex(i);
                if (record != null) {
                    result.add(record);
                }
            }

            return result;
        }
    }
}
```

## 3. Hash类型 - HashTable + 渐进式Rehash

### 渐进式Rehash的HashTable实现

```java
/**
 * Redis Hash类型的底层实现
 * 支持渐进式rehash的哈希表
 */
public class RedisHashTable<K, V> {

    /**
     * 哈希表节点
     */
    private static class HashNode<K, V> {
        K key;
        V value;
        HashNode<K, V> next;  // 链式解决冲突

        HashNode(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    /**
     * 字典结构
     */
    private static class Dict<K, V> {
        HashNode<K, V>[] table;   // 哈希表数组
        int size;                 // 当前元素个数
        int capacity;             // 容量
        int mask;                 // 掩码，等于capacity-1

        @SuppressWarnings("unchecked")
        Dict(int capacity) {
            this.capacity = capacity;
            this.table = new HashNode[capacity];
            this.size = 0;
            this.mask = capacity - 1;
        }
    }

    private Dict<K, V> ht0;          // 主哈希表
    private Dict<K, V> ht1;          // 辅助哈希表(用于rehash)
    private int rehashIndex;         // rehash进度，-1表示没有进行rehash
    private boolean isRehashing;     // 是否正在rehash

    private static final double LOAD_FACTOR_THRESHOLD = 1.0;  // 负载因子阈值

    public RedisHashTable() {
        this.ht0 = new Dict<>(4);  // 初始容量为4
        this.ht1 = null;
        this.rehashIndex = -1;
        this.isRehashing = false;
    }

    /**
     * 哈希函数
     * @param key 键
     * @return 哈希值
     */
    private int hash(K key) {
        // 简化的哈希函数
        return Math.abs(key.hashCode());
    }

    /**
     * 检查是否需要扩容
     * @return 是否需要扩容
     */
    private boolean needExpand() {
        double loadFactor = (double) ht0.size / ht0.capacity;
        return loadFactor >= LOAD_FACTOR_THRESHOLD;
    }

    /**
     * 开始渐进式rehash
     */
    private void startRehash() {
        if (isRehashing) return;

        // 创建新的哈希表，容量扩大一倍
        ht1 = new Dict<>(ht0.capacity * 2);
        rehashIndex = 0;
        isRehashing = true;

        System.out.println("开始渐进式rehash: " + ht0.capacity + " -> " + ht1.capacity);
    }

    /**
     * 执行一步rehash
     * @param stepCount 本次rehash的步数
     */
    private void rehashStep(int stepCount) {
        if (!isRehashing) return;

        int emptyVisits = 0;  // 连续访问到的空桶数
        int maxEmptyVisits = stepCount * 10;  // 最大空桶访问数

        while (stepCount > 0 && rehashIndex < ht0.capacity) {
            // 如果当前桶为空，继续下一个
            if (ht0.table[rehashIndex] == null) {
                rehashIndex++;
                emptyVisits++;

                // 避免在稀疏哈希表中花费太多时间
                if (emptyVisits > maxEmptyVisits) {
                    break;
                }
                continue;
            }

            // 迁移当前桶的所有节点
            HashNode<K, V> node = ht0.table[rehashIndex];
            while (node != null) {
                HashNode<K, V> next = node.next;

                // 计算在新表中的位置
                int newIndex = hash(node.key) & ht1.mask;

                // 插入到新表的头部
                node.next = ht1.table[newIndex];
                ht1.table[newIndex] = node;

                // 更新统计信息
                ht0.size--;
                ht1.size++;

                node = next;
            }

            // 清空旧桶
            ht0.table[rehashIndex] = null;
            rehashIndex++;
            stepCount--;
        }

        // 检查rehash是否完成
        if (rehashIndex >= ht0.capacity) {
            // Rehash完成，交换表
            Dict<K, V> temp = ht0;
            ht0 = ht1;
            ht1 = null;

            rehashIndex = -1;
            isRehashing = false;

            System.out.println("渐进式rehash完成，新容量: " + ht0.capacity);
        }
    }

    /**
     * 插入键值对
     * @param key 键
     * @param value 值
     */
    public void put(K key, V value) {
        // 如果正在rehash，执行一步rehash
        if (isRehashing) {
            rehashStep(1);
        }

        // 检查是否需要开始rehash
        if (!isRehashing && needExpand()) {
            startRehash();
        }

        // 确定插入到哪个表
        Dict<K, V> targetDict = isRehashing ? ht1 : ht0;
        int index = hash(key) & targetDict.mask;

        // 检查是否已存在
        HashNode<K, V> node = targetDict.table[index];
        while (node != null) {
            if (node.key.equals(key)) {
                node.value = value;  // 更新值
                return;
            }
            node = node.next;
        }

        // 插入新节点
        HashNode<K, V> newNode = new HashNode<>(key, value);
        newNode.next = targetDict.table[index];
        targetDict.table[index] = newNode;
        targetDict.size++;
    }

    /**
     * 获取值
     * @param key 键
     * @return 值
     */
    public V get(K key) {
        // 如果正在rehash，执行一步rehash
        if (isRehashing) {
            rehashStep(1);
        }

        // 先在ht0中查找
        int index0 = hash(key) & ht0.mask;
        HashNode<K, V> node = ht0.table[index0];
        while (node != null) {
            if (node.key.equals(key)) {
                return node.value;
            }
            node = node.next;
        }

        // 如果正在rehash，还需要在ht1中查找
        if (isRehashing) {
            int index1 = hash(key) & ht1.mask;
            node = ht1.table[index1];
            while (node != null) {
                if (node.key.equals(key)) {
                    return node.value;
                }
                node = node.next;
            }
        }

        return null;
    }

    /**
     * 删除键值对
     * @param key 键
     * @return 是否删除成功
     */
    public boolean remove(K key) {
        // 如果正在rehash，执行一步rehash
        if (isRehashing) {
            rehashStep(1);
        }

        // 在两个表中查找并删除
        Dict<K, V>[] tables = isRehashing ?
            new Dict[]{ht0, ht1} : new Dict[]{ht0};

        for (Dict<K, V> dict : tables) {
            if (dict == null) continue;

            int index = hash(key) & dict.mask;
            HashNode<K, V> prev = null;
            HashNode<K, V> current = dict.table[index];

            while (current != null) {
                if (current.key.equals(key)) {
                    // 找到了，删除节点
                    if (prev == null) {
                        dict.table[index] = current.next;
                    } else {
                        prev.next = current.next;
                    }
                    dict.size--;
                    return true;
                }
                prev = current;
                current = current.next;
            }
        }

        return false;
    }

    /**
     * 获取总元素数
     * @return 总元素数
     */
    public int size() {
        return ht0.size + (ht1 != null ? ht1.size : 0);
    }

    /**
     * 获取所有键
     * @return 键的集合
     */
    public Set<K> keySet() {
        Set<K> keys = new HashSet<>();

        // 遍历ht0
        for (HashNode<K, V> head : ht0.table) {
            HashNode<K, V> node = head;
            while (node != null) {
                keys.add(node.key);
                node = node.next;
            }
        }

        // 如果正在rehash，还要遍历ht1
        if (isRehashing && ht1 != null) {
            for (HashNode<K, V> head : ht1.table) {
                HashNode<K, V> node = head;
                while (node != null) {
                    keys.add(node.key);
                    node = node.next;
                }
            }
        }

        return keys;
    }

    /**
     * 打印哈希表状态
     */
    public void printStatus() {
        System.out.println("=== Hash表状态 ===");
        System.out.println("总元素数: " + size());
        System.out.println("主表容量: " + ht0.capacity + ", 元素数: " + ht0.size);

        if (isRehashing) {
            System.out.println("正在rehash...");
            System.out.println("辅助表容量: " + ht1.capacity + ", 元素数: " + ht1.size);
            System.out.println("rehash进度: " + rehashIndex + "/" + ht0.capacity);
        }

        double loadFactor = (double) ht0.size / ht0.capacity;
        System.out.println("负载因子: " + String.format("%.2f", loadFactor));
    }
}
```

## 4. Set类型 - IntSet + HashTable

### IntSet整数集合实现

```java
/**
 * Redis Set类型的IntSet实现
 * 当集合只包含整数且元素较少时使用
 */
public class IntSet {
    private static final int INTSET_ENC_INT16 = 2;  // 16位整数
    private static final int INTSET_ENC_INT32 = 4;  // 32位整数
    private static final int INTSET_ENC_INT64 = 8;  // 64位整数

    private int encoding;    // 编码方式
    private int length;      // 元素个数
    private byte[] contents; // 存储数组

    public IntSet() {
        this.encoding = INTSET_ENC_INT16;  // 默认使用16位
        this.length = 0;
        this.contents = new byte[0];
    }

    /**
     * 根据值确定所需的编码
     * @param value 整数值
     * @return 编码类型
     */
    private int getEncodingForValue(long value) {
        if (value >= Short.MIN_VALUE && value <= Short.MAX_VALUE) {
            return INTSET_ENC_INT16;
        } else if (value >= Integer.MIN_VALUE && value <= Integer.MAX_VALUE) {
            return INTSET_ENC_INT32;
        } else {
            return INTSET_ENC_INT64;
        }
    }

    /**
     * 升级编码并插入新值
     * @param value 新值
     */
    private void upgradeAndAdd(long value) {
        int oldEncoding = encoding;
        int newEncoding = getEncodingForValue(value);

        System.out.println("IntSet编码升级: " + oldEncoding + " -> " + newEncoding);

        // 创建新的contents数组
        byte[] newContents = new byte[(length + 1) * newEncoding];

        // 根据新值的大小决定插入位置
        boolean insertAtEnd = value > 0;
        int insertPos = insertAtEnd ? length : 0;

        // 复制并转换现有元素
        for (int i = 0; i < length; i++) {
            long oldValue = getValue(i, oldEncoding);
            int newPos = insertAtEnd ? i : i + 1;
            setValue(newContents, newPos, oldValue, newEncoding);
        }

        // 插入新值
        setValue(newContents, insertPos, value, newEncoding);

        // 更新IntSet状态
        this.encoding = newEncoding;
        this.contents = newContents;
        this.length++;
    }

    /**
     * 从指定位置获取值
     * @param pos 位置
     * @param encoding 编码方式
     * @return 值
     */
    private long getValue(int pos, int encoding) {
        if (encoding == INTSET_ENC_INT16) {
            short value = (short) ((contents[pos * 2] & 0xFF) |
                                 ((contents[pos * 2 + 1] & 0xFF) << 8));
            return value;
        } else if (encoding == INTSET_ENC_INT32) {
            int value = (contents[pos * 4] & 0xFF) |
                       ((contents[pos * 4 + 1] & 0xFF) << 8) |
                       ((contents[pos * 4 + 2] & 0xFF) << 16) |
                       ((contents[pos * 4 + 3] & 0xFF) << 24);
            return value;
        } else {
            // INT64处理类似但更复杂，这里简化
            return 0;
        }
    }

    /**
     * 在指定位置设置值
     * @param array 数组
     * @param pos 位置
     * @param value 值
     * @param encoding 编码方式
     */
    private void setValue(byte[] array, int pos, long value, int encoding) {
        if (encoding == INTSET_ENC_INT16) {
            array[pos * 2] = (byte) (value & 0xFF);
            array[pos * 2 + 1] = (byte) ((value >> 8) & 0xFF);
        } else if (encoding == INTSET_ENC_INT32) {
            array[pos * 4] = (byte) (value & 0xFF);
            array[pos * 4 + 1] = (byte) ((value >> 8) & 0xFF);
            array[pos * 4 + 2] = (byte) ((value >> 16) & 0xFF);
            array[pos * 4 + 3] = (byte) ((value >> 24) & 0xFF);
        }
        // INT64类似处理
    }

    /**
     * 二分查找元素位置
     * @param value 要查找的值
     * @return 位置，如果不存在返回负数
     */
    private int search(long value) {
        int min = 0, max = length - 1, mid = -1;

        if (length == 0) {
            return 0;
        }

        // 检查边界
        if (value > getValue(max, encoding)) {
            return length;  // 插入到末尾
        } else if (value < getValue(0, encoding)) {
            return 0;  // 插入到开头
        }

        // 二分查找
        while (max >= min) {
            mid = (min + max) / 2;
            long current = getValue(mid, encoding);

            if (current == value) {
                return mid;  // 找到了
            } else if (current < value) {
                min = mid + 1;
            } else {
                max = mid - 1;
            }
        }

        return min;  // 插入位置
    }

    /**
     * 添加元素
     * @param value 要添加的值
     * @return 是否添加成功
     */
    public boolean add(long value) {
        int requiredEncoding = getEncodingForValue(value);

        // 如果需要升级编码
        if (requiredEncoding > encoding) {
            upgradeAndAdd(value);
            return true;
        }

        int pos = search(value);
        if (pos < length && getValue(pos, encoding) == value) {
            return false;  // 元素已存在
        }

        // 扩展数组
        byte[] newContents = new byte[(length + 1) * encoding];

        // 复制元素并插入新值
        for (int i = 0; i < pos; i++) {
            setValue(newContents, i, getValue(i, encoding), encoding);
        }

        setValue(newContents, pos, value, encoding);

        for (int i = pos; i < length; i++) {
            setValue(newContents, i + 1, getValue(i, encoding), encoding);
        }

        this.contents = newContents;
        this.length++;
        return true;
    }

    /**
     * 检查元素是否存在
     * @param value 要检查的值
     * @return 是否存在
     */
    public boolean contains(long value) {
        int requiredEncoding = getEncodingForValue(value);
        if (requiredEncoding > encoding) {
            return false;  // 编码不匹配，肯定不存在
        }

        int pos = search(value);
        return pos < length && getValue(pos, encoding) == value;
    }

    /**
     * 获取集合大小
     * @return 集合大小
     */
    public int size() {
        return length;
    }

    /**
     * 获取所有元素
     * @return 元素列表
     */
    public List<Long> getAllElements() {
        List<Long> elements = new ArrayList<>();
        for (int i = 0; i < length; i++) {
            elements.add(getValue(i, encoding));
        }
        return elements;
    }

    /**
     * 演示IntSet的使用
     */
    public static void demonstrateIntSet() {
        System.out.println("=== IntSet演示 ===");

        IntSet intSet = new IntSet();

        // 添加16位整数
        System.out.println("添加16位整数...");
        intSet.add(1);
        intSet.add(10);
        intSet.add(100);
        System.out.println("当前编码: " + intSet.encoding);
        System.out.println("元素: " + intSet.getAllElements());

        // 添加32位整数，触发编码升级
        System.out.println("\n添加32位整数...");
        intSet.add(100000);
        System.out.println("当前编码: " + intSet.encoding);
        System.out.println("元素: " + intSet.getAllElements());

        // 测试查找
        System.out.println("\n查找测试:");
        System.out.println("包含10: " + intSet.contains(10));
        System.out.println("包含50: " + intSet.contains(50));
    }
}
```

## 5. ZSet类型 - SkipList + HashTable

### SkipList跳表实现

```java
/**
 * Redis ZSet类型的SkipList实现
 * 跳表是一种概率性数据结构，可以在O(log n)时间内完成查找、插入、删除操作
 */
public class SkipList<T> {
    private static final int MAX_LEVEL = 16;    // 最大层数
    private static final double P = 0.25;       // 层数增长概率

    /**
     * 跳表节点
     */
    private static class SkipListNode<T> {
        double score;                    // 分数
        T value;                        // 值
        SkipListNode<T>[] forward;      // 前进指针数组
        SkipListNode<T> backward;       // 后退指针
        int level;                      // 节点层数

        @SuppressWarnings("unchecked")
        SkipListNode(int level, double score, T value) {
            this.level = level;
            this.score = score;
            this.value = value;
            this.forward = new SkipListNode[level];
            this.backward = null;
        }
    }

    private SkipListNode<T> header;     // 头节点
    private SkipListNode<T> tail;       // 尾节点
    private int length;                 // 节点数量
    private int level;                  // 当前最高层数

    public SkipList() {
        this.header = new SkipListNode<>(MAX_LEVEL, 0, null);
        this.tail = null;
        this.length = 0;
        this.level = 1;
    }

    /**
     * 随机生成节点层数
     * @return 层数
     */
    private int randomLevel() {
        int level = 1;
        while (Math.random() < P && level < MAX_LEVEL) {
            level++;
        }
        return level;
    }

    /**
     * 插入节点
     * @param score 分数
     * @param value 值
     */
    public void insert(double score, T value) {
        SkipListNode<T>[] update = new SkipListNode[MAX_LEVEL];
        SkipListNode<T> current = header;

        // 从最高层开始向下查找插入位置
        for (int i = level - 1; i >= 0; i--) {
            while (current.forward[i] != null &&
                   (current.forward[i].score < score ||
                    (current.forward[i].score == score &&
                     compareValues(current.forward[i].value, value) < 0))) {
                current = current.forward[i];
            }
            update[i] = current;
        }

        current = current.forward[0];

        // 如果节点已存在且分数相同，更新值
        if (current != null && current.score == score &&
            compareValues(current.value, value) == 0) {
            current.value = value;
            return;
        }

        // 创建新节点
        int newLevel = randomLevel();
        if (newLevel > level) {
            for (int i = level; i < newLevel; i++) {
                update[i] = header;
            }
            level = newLevel;
        }

        SkipListNode<T> newNode = new SkipListNode<>(newLevel, score, value);

        // 更新前进指针
        for (int i = 0; i < newLevel; i++) {
            newNode.forward[i] = update[i].forward[i];
            update[i].forward[i] = newNode;
        }

        // 更新后退指针
        newNode.backward = (update[0] == header) ? null : update[0];
        if (newNode.forward[0] != null) {
            newNode.forward[0].backward = newNode;
        } else {
            tail = newNode;
        }

        length++;
        System.out.println("插入节点: score=" + score + ", value=" + value + ", level=" + newLevel);
    }

    /**
     * 删除节点
     * @param score 分数
     * @param value 值
     * @return 是否删除成功
     */
    public boolean delete(double score, T value) {
        SkipListNode<T>[] update = new SkipListNode[MAX_LEVEL];
        SkipListNode<T> current = header;

        // 查找要删除的节点
        for (int i = level - 1; i >= 0; i--) {
            while (current.forward[i] != null &&
                   (current.forward[i].score < score ||
                    (current.forward[i].score == score &&
                     compareValues(current.forward[i].value, value) < 0))) {
                current = current.forward[i];
            }
            update[i] = current;
        }

        current = current.forward[0];

        // 检查是否找到目标节点
        if (current != null && current.score == score &&
            compareValues(current.value, value) == 0) {

            // 更新前进指针
            for (int i = 0; i < level; i++) {
                if (update[i].forward[i] == current) {
                    update[i].forward[i] = current.forward[i];
                }
            }

            // 更新后退指针
            if (current.forward[0] != null) {
                current.forward[0].backward = current.backward;
            } else {
                tail = current.backward;
            }

            // 更新层数
            while (level > 1 && header.forward[level - 1] == null) {
                level--;
            }

            length--;
            System.out.println("删除节点: score=" + score + ", value=" + value);
            return true;
        }

        return false;
    }

    /**
     * 按分数范围查找
     * @param minScore 最小分数
     * @param maxScore 最大分数
     * @return 结果列表
     */
    public List<T> rangeByScore(double minScore, double maxScore) {
        List<T> result = new ArrayList<>();
        SkipListNode<T> current = header.forward[0];

        // 跳过分数小于minScore的节点
        while (current != null && current.score < minScore) {
            current = current.forward[0];
        }

        // 收集符合条件的节点
        while (current != null && current.score <= maxScore) {
            result.add(current.value);
            current = current.forward[0];
        }

        return result;
    }

    /**
     * 按排名范围查找
     * @param start 起始排名(0开始)
     * @param end 结束排名
     * @return 结果列表
     */
    public List<T> rangeByRank(int start, int end) {
        List<T> result = new ArrayList<>();

        if (start < 0 || start >= length || end < start) {
            return result;
        }

        SkipListNode<T> current = header.forward[0];

        // 跳到起始位置
        for (int i = 0; i < start && current != null; i++) {
            current = current.forward[0];
        }

        // 收集指定范围的节点
        for (int i = start; i <= end && current != null; i++) {
            result.add(current.value);
            current = current.forward[0];
        }

        return result;
    }

    /**
     * 获取节点排名
     * @param score 分数
     * @param value 值
     * @return 排名(0开始)，如果不存在返回-1
     */
    public int getRank(double score, T value) {
        int rank = 0;
        SkipListNode<T> current = header;

        for (int i = level - 1; i >= 0; i--) {
            while (current.forward[i] != null &&
                   (current.forward[i].score < score ||
                    (current.forward[i].score == score &&
                     compareValues(current.forward[i].value, value) <= 0))) {

                // 计算跨越的节点数
                if (i == 0) rank++;
                current = current.forward[i];
            }

            // 如果在第0层找到了目标节点
            if (i == 0 && current.score == score &&
                compareValues(current.value, value) == 0) {
                return rank - 1;  // 排名从0开始
            }
        }

        return -1;  // 未找到
    }

    /**
     * 比较两个值
     * @param v1 值1
     * @param v2 值2
     * @return 比较结果
     */
    @SuppressWarnings("unchecked")
    private int compareValues(T v1, T v2) {
        if (v1 instanceof Comparable && v2 instanceof Comparable) {
            return ((Comparable<T>) v1).compareTo(v2);
        }
        return v1.toString().compareTo(v2.toString());
    }

    /**
     * 获取长度
     * @return 长度
     */
    public int size() {
        return length;
    }

    /**
     * 打印跳表结构
     */
    public void printStructure() {
        System.out.println("=== SkipList结构 ===");
        System.out.println("长度: " + length + ", 最高层数: " + level);

        for (int i = level - 1; i >= 0; i--) {
            System.out.print("Level " + i + ": ");
            SkipListNode<T> current = header.forward[i];
            while (current != null) {
                System.out.print("[" + current.score + "," + current.value + "] ");
                current = current.forward[i];
            }
            System.out.println();
        }
    }
}
```

### Redis ZSet的完整实现

```java
/**
 * Redis ZSet(有序集合)的完整实现
 * 结合SkipList和HashTable，支持按分数和按成员快速访问
 */
public class RedisZSet<T> {
    private SkipList<T> skiplist;           // 跳表，支持范围查询
    private Map<T, Double> dict;            // 哈希表，支持O(1)查找

    public RedisZSet() {
        this.skiplist = new SkipList<>();
        this.dict = new HashMap<>();
    }

    /**
     * 添加成员
     * @param score 分数
     * @param member 成员
     * @return 是否是新增成员
     */
    public boolean zadd(double score, T member) {
        Double oldScore = dict.get(member);

        if (oldScore != null) {
            // 成员已存在，需要更新分数
            if (oldScore != score) {
                // 分数不同，需要在跳表中删除旧节点，插入新节点
                skiplist.delete(oldScore, member);
                skiplist.insert(score, member);
                dict.put(member, score);
            }
            return false;  // 不是新增成员
        } else {
            // 新成员
            skiplist.insert(score, member);
            dict.put(member, score);
            return true;
        }
    }

    /**
     * 删除成员
     * @param member 成员
     * @return 是否删除成功
     */
    public boolean zrem(T member) {
        Double score = dict.get(member);
        if (score != null) {
            skiplist.delete(score, member);
            dict.remove(member);
            return true;
        }
        return false;
    }

    /**
     * 获取成员分数
     * @param member 成员
     * @return 分数，如果不存在返回null
     */
    public Double zscore(T member) {
        return dict.get(member);
    }

    /**
     * 获取成员排名
     * @param member 成员
     * @return 排名(0开始)，如果不存在返回-1
     */
    public int zrank(T member) {
        Double score = dict.get(member);
        if (score != null) {
            return skiplist.getRank(score, member);
        }
        return -1;
    }

    /**
     * 按分数范围查询
     * @param minScore 最小分数
     * @param maxScore 最大分数
     * @return 成员列表
     */
    public List<T> zrangebyscore(double minScore, double maxScore) {
        return skiplist.rangeByScore(minScore, maxScore);
    }

    /**
     * 按排名范围查询
     * @param start 起始排名
     * @param end 结束排名
     * @return 成员列表
     */
    public List<T> zrange(int start, int end) {
        return skiplist.rangeByRank(start, end);
    }

    /**
     * 获取集合大小
     * @return 集合大小
     */
    public int zcard() {
        return dict.size();
    }

    /**
     * 增加成员分数
     * @param increment 增量
     * @param member 成员
     * @return 新分数
     */
    public double zincrby(double increment, T member) {
        Double oldScore = dict.get(member);
        double newScore = (oldScore != null ? oldScore : 0) + increment;

        if (oldScore != null) {
            skiplist.delete(oldScore, member);
        }

        skiplist.insert(newScore, member);
        dict.put(member, newScore);

        return newScore;
    }

    /**
     * 演示ZSet的使用
     */
    public static void demonstrateZSet() {
        System.out.println("=== Redis ZSet演示 ===");

        RedisZSet<String> zset = new RedisZSet<>();

        // 添加成员
        System.out.println("添加游戏玩家分数...");
        zset.zadd(1500, "Alice");
        zset.zadd(1200, "Bob");
        zset.zadd(1800, "Charlie");
        zset.zadd(1350, "David");
        zset.zadd(1600, "Eve");

        System.out.println("ZSet大小: " + zset.zcard());

        // 查询排行榜
        System.out.println("\n前3名玩家:");
        List<String> top3 = zset.zrange(0, 2);
        for (int i = 0; i < top3.size(); i++) {
            String player = top3.get(i);
            System.out.println((i + 1) + ". " + player + " (分数: " + zset.zscore(player) + ")");
        }

        // 按分数范围查询
        System.out.println("\n分数在1400-1700之间的玩家:");
        List<String> midRange = zset.zrangebyscore(1400, 1700);
        for (String player : midRange) {
            System.out.println(player + ": " + zset.zscore(player));
        }

        // 增加分数
        System.out.println("\nBob获得200分:");
        double newScore = zset.zincrby(200, "Bob");
        System.out.println("Bob新分数: " + newScore);
        System.out.println("Bob新排名: " + zset.zrank("Bob"));

        // 最终排行榜
        System.out.println("\n最终排行榜:");
        List<String> finalRanking = zset.zrange(0, -1);
        for (int i = 0; i < finalRanking.size(); i++) {
            String player = finalRanking.get(i);
            System.out.println((i + 1) + ". " + player +
                " (分数: " + zset.zscore(player) + ")");
        }
    }
}
```

## Redis数据结构选择策略

### 自动编码转换

Redis会根据数据的特点自动选择最优的底层数据结构：

```java
/**
 * Redis编码转换策略模拟
 */
public class RedisEncodingStrategy {

    /**
     * String类型编码选择
     */
    public static String chooseStringEncoding(String value) {
        // 尝试解析为整数
        try {
            long longValue = Long.parseLong(value);
            if (longValue >= Integer.MIN_VALUE && longValue <= Integer.MAX_VALUE) {
                return "INT";  // 整数编码
            }
        } catch (NumberFormatException e) {
            // 不是整数，继续判断
        }

        // 使用SDS编码
        return "EMBSTR";  // 嵌入式字符串或RAW
    }

    /**
     * List类型编码选择
     */
    public static String chooseListEncoding(int elementCount, int maxElementSize) {
        // Redis 3.2之前的策略
        if (elementCount <= 512 && maxElementSize <= 64) {
            return "ZIPLIST";  // 压缩列表
        } else {
            return "LINKEDLIST";  // 双向链表
        }

        // Redis 3.2之后统一使用QUICKLIST
        // return "QUICKLIST";
    }

    /**
     * Hash类型编码选择
     */
    public static String chooseHashEncoding(int fieldCount, int maxFieldSize, int maxValueSize) {
        if (fieldCount <= 512 &&
            maxFieldSize <= 64 &&
            maxValueSize <= 64) {
            return "ZIPLIST";  // 压缩列表
        } else {
            return "HASHTABLE";  // 哈希表
        }
    }

    /**
     * Set类型编码选择
     */
    public static String chooseSetEncoding(Set<Object> elements) {
        // 检查是否都是整数
        boolean allIntegers = elements.stream()
            .allMatch(e -> e instanceof Integer || e instanceof Long);

        if (allIntegers && elements.size() <= 512) {
            return "INTSET";  // 整数集合
        } else {
            return "HASHTABLE";  // 哈希表
        }
    }

    /**
     * ZSet类型编码选择
     */
    public static String chooseZSetEncoding(int elementCount, int maxElementSize) {
        if (elementCount <= 128 && maxElementSize <= 64) {
            return "ZIPLIST";  // 压缩列表
        } else {
            return "SKIPLIST";  // 跳表+哈希表
        }
    }

    /**
     * 演示编码选择
     */
    public static void demonstrateEncodingChoice() {
        System.out.println("=== Redis编码选择演示 ===");

        // String编码选择
        System.out.println("String '123': " + chooseStringEncoding("123"));
        System.out.println("String 'hello': " + chooseStringEncoding("hello"));

        // List编码选择
        System.out.println("List(元素数:100,最大元素:50字节): " +
            chooseListEncoding(100, 50));
        System.out.println("List(元素数:1000,最大元素:100字节): " +
            chooseListEncoding(1000, 100));

        // Hash编码选择
        System.out.println("Hash(字段数:200,最大键:30,最大值:40): " +
            chooseHashEncoding(200, 30, 40));
        System.out.println("Hash(字段数:1000,最大键:100,最大值:200): " +
            chooseHashEncoding(1000, 100, 200));

        // Set编码选择
        Set<Object> intSet = Set.of(1, 2, 3, 4, 5);
        Set<Object> strSet = Set.of("a", "b", "c", "d", "e");
        System.out.println("Set(整数集合,5个元素): " + chooseSetEncoding(intSet));
        System.out.println("Set(字符串集合,5个元素): " + chooseSetEncoding(strSet));

        // ZSet编码选择
        System.out.println("ZSet(元素数:50,最大元素:30字节): " +
            chooseZSetEncoding(50, 30));
        System.out.println("ZSet(元素数:500,最大元素:100字节): " +
            chooseZSetEncoding(500, 100));
    }
}
```

## 总结

Redis的高性能来源于其精妙的数据结构设计。每种数据类型都针对不同的使用场景选择了最优的底层实现：

### 🎯 核心设计原则

1. **内存效率优先**：使用压缩结构(ziplist、intset)节省内存
2. **自动优化**：根据数据特征自动选择最优编码
3. **渐进式操作**：避免阻塞，保证高可用性
4. **时间空间平衡**：在时间复杂度和空间复杂度间找到最佳平衡

### 🚀 性能关键技术

- **SDS动态字符串**：O(1)长度获取，空间预分配
- **QuickList**：结合ziplist和linkedlist的优势
- **渐进式rehash**：避免大数据量时的阻塞
- **SkipList跳表**：平衡树的概率性替代方案
- **编码转换**：根据数据特征动态优化存储结构

理解Redis底层数据结构的实现原理，有助于我们：
- 🎯 选择合适的数据类型和操作
- ⚡ 优化Redis的使用方式
- 🛠️ 设计高效的数据存储方案
- 📈 提升应用的整体性能

Redis的数据结构设计是计算机科学理论与工程实践完美结合的典范，值得每个开发者深入学习和借鉴！