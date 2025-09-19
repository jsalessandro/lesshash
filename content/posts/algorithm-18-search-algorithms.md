---
title: "算法详解：搜索算法大全 - 从线性到智能的查找艺术"
date: 2025-01-26T10:18:00+08:00
draft: false
tags: ["算法", "搜索算法", "二分查找", "哈希搜索", "Java"]
categories: ["算法"]
series: ["高级算法入门教程"]
author: "lesshash"
description: "全面深入解析搜索算法，从基础线性搜索到高级AI搜索，包含二分查找、哈希搜索、树搜索等多种实现，配有详细代码示例和性能分析，助你掌握查找的艺术"
---

## 🔍 搜索算法概览

### 搜索算法分类图
#### 流程图表


**关系流向：**
```
A[搜索算法] → B[基础搜索]
A → C[树搜索]
A → D[图搜索]
A → E[智能搜索]
B → B1[线性搜索]
```

### 现实生活中的搜索场景

搜索无处不在，从日常生活到复杂的计算机系统：

1. **搜索引擎** - Google、百度使用复杂的搜索算法处理数十亿网页
2. **数据库查询** - SQL查询优化器选择最佳搜索策略
3. **推荐系统** - 电商平台通过搜索算法匹配用户偏好
4. **游戏AI** - 国际象棋、围棋AI使用智能搜索决定最佳落子
5. **路径规划** - 导航软件寻找最短路径
6. **文本搜索** - 文档编辑器中的查找功能

## 📊 基础搜索算法

### 1. 线性搜索（Linear Search）

线性搜索是最基础的搜索算法，逐个检查每个元素。

#### 算法实现

```java
/**
 * 线性搜索实现
 * 时间复杂度：O(n)
 * 空间复杂度：O(1)
 */
public class LinearSearch {

    /**
     * 基础线性搜索
     */
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i;  // 返回找到元素的索引
            }
        }
        return -1;  // 未找到返回-1
    }

    /**
     * 改进的线性搜索 - 哨兵版本
     * 减少循环中的边界检查
     */
    public static int sentinelLinearSearch(int[] arr, int target) {
        int n = arr.length;
        int last = arr[n - 1];  // 保存最后一个元素
        arr[n - 1] = target;    // 设置哨兵

        int i = 0;
        while (arr[i] != target) {
            i++;
        }

        arr[n - 1] = last;  // 恢复最后一个元素

        if (i < n - 1 || arr[n - 1] == target) {
            return i;
        }
        return -1;
    }

    /**
     * 递归版本线性搜索
     */
    public static int recursiveLinearSearch(int[] arr, int target, int index) {
        if (index >= arr.length) {
            return -1;
        }
        if (arr[index] == target) {
            return index;
        }
        return recursiveLinearSearch(arr, target, index + 1);
    }
}
```

#### 性能分析

```java
/**
 * 线性搜索性能测试
 */
public class LinearSearchPerformance {

    public static void performanceTest() {
        int[] sizes = {1000, 10000, 100000, 1000000};

        for (int size : sizes) {
            int[] arr = generateArray(size);
            int target = arr[size - 1];  // 最坏情况：搜索最后一个元素

            long startTime = System.nanoTime();
            int result = LinearSearch.linearSearch(arr, target);
            long endTime = System.nanoTime();

            System.out.printf("数组大小: %d, 耗时: %.2f ms%n",
                            size, (endTime - startTime) / 1_000_000.0);
        }
    }

    private static int[] generateArray(int size) {
        int[] arr = new int[size];
        for (int i = 0; i < size; i++) {
            arr[i] = i + 1;
        }
        return arr;
    }
}
```

### 2. 二分搜索（Binary Search）

二分搜索是在有序数组中查找元素的高效算法。

#### 核心思想图解

#### 流程图表


**关系流向：**
```
A[有序数组] → B{比较中间元素}
B →|target < mid| C[搜索左半部分]
B →|target > mid| D[搜索右半部分]
B →|target == mid| E[找到目标]
C → F{继续二分}
```

#### 算法实现

```java
/**
 * 二分搜索的多种实现
 */
public class BinarySearch {

    /**
     * 迭代版本二分搜索
     * 时间复杂度：O(log n)
     * 空间复杂度：O(1)
     */
    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;  // 防止溢出

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }

    /**
     * 递归版本二分搜索
     */
    public static int recursiveBinarySearch(int[] arr, int target, int left, int right) {
        if (left > right) {
            return -1;
        }

        int mid = left + (right - left) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            return recursiveBinarySearch(arr, target, mid + 1, right);
        } else {
            return recursiveBinarySearch(arr, target, left, mid - 1);
        }
    }

    /**
     * 查找第一个出现的位置
     */
    public static int findFirst(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        int result = -1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                result = mid;
                right = mid - 1;  // 继续在左半部分查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    /**
     * 查找最后一个出现的位置
     */
    public static int findLast(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        int result = -1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                result = mid;
                left = mid + 1;  // 继续在右半部分查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    /**
     * 查找插入位置
     */
    public static int findInsertPosition(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return left;
    }
}
```

### 3. 插值搜索（Interpolation Search）

插值搜索在均匀分布的有序数组中表现更优。

```java
/**
 * 插值搜索实现
 * 适用于数据均匀分布的有序数组
 */
public class InterpolationSearch {

    /**
     * 插值搜索
     * 时间复杂度：平均O(log log n)，最坏O(n)
     * 空间复杂度：O(1)
     */
    public static int interpolationSearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right && target >= arr[left] && target <= arr[right]) {
            if (left == right) {
                if (arr[left] == target) return left;
                return -1;
            }

            // 插值公式：基于线性插值估算位置
            int pos = left + ((target - arr[left]) * (right - left)) /
                           (arr[right] - arr[left]);

            if (arr[pos] == target) {
                return pos;
            } else if (arr[pos] < target) {
                left = pos + 1;
            } else {
                right = pos - 1;
            }
        }
        return -1;
    }

    /**
     * 性能对比测试
     */
    public static void performanceComparison() {
        int[] uniformArray = generateUniformArray(1000000);
        int target = uniformArray[750000];

        // 二分搜索测试
        long startTime = System.nanoTime();
        int result1 = BinarySearch.binarySearch(uniformArray, target);
        long binaryTime = System.nanoTime() - startTime;

        // 插值搜索测试
        startTime = System.nanoTime();
        int result2 = interpolationSearch(uniformArray, target);
        long interpolationTime = System.nanoTime() - startTime;

        System.out.printf("二分搜索耗时: %.2f ms%n", binaryTime / 1_000_000.0);
        System.out.printf("插值搜索耗时: %.2f ms%n", interpolationTime / 1_000_000.0);
        System.out.printf("性能提升: %.2fx%n", (double)binaryTime / interpolationTime);
    }

    private static int[] generateUniformArray(int size) {
        int[] arr = new int[size];
        for (int i = 0; i < size; i++) {
            arr[i] = i * 2;  // 均匀分布
        }
        return arr;
    }
}
```

### 4. 指数搜索（Exponential Search）

指数搜索适用于无界或大数组的搜索。

```java
/**
 * 指数搜索实现
 * 特别适用于搜索范围未知的情况
 */
public class ExponentialSearch {

    /**
     * 指数搜索
     * 时间复杂度：O(log n)
     * 空间复杂度：O(1)
     */
    public static int exponentialSearch(int[] arr, int target) {
        if (arr[0] == target) {
            return 0;
        }

        // 找到范围
        int bound = 1;
        while (bound < arr.length && arr[bound] < target) {
            bound *= 2;
        }

        // 在找到的范围内进行二分搜索
        int left = bound / 2;
        int right = Math.min(bound, arr.length - 1);

        return BinarySearch.binarySearchRange(arr, target, left, right);
    }

    /**
     * 无界数组搜索
     * 当不知道数组确切大小时使用
     */
    public static int unboundedSearch(int[] arr, int target) {
        int bound = 1;

        // 找到上界，注意处理数组边界
        try {
            while (arr[bound] < target) {
                bound *= 2;
            }
        } catch (ArrayIndexOutOfBoundsException e) {
            // 找到实际的右边界
            int left = bound / 2;
            int right = left;
            while (right < arr.length && arr[right] < target) {
                right++;
            }
            bound = right;
        }

        int left = bound / 2;
        int right = Math.min(bound, arr.length - 1);

        return BinarySearch.binarySearchRange(arr, target, left, right);
    }

    /**
     * 在指定范围内的二分搜索
     */
    public static int binarySearchRange(int[] arr, int target, int left, int right) {
        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}
```

## 🗂️ 哈希搜索

哈希搜索通过哈希函数实现O(1)平均时间复杂度的搜索。

### 哈希表实现

```java
/**
 * 自定义哈希表实现
 * 演示哈希搜索的原理
 */
public class HashSearch<K, V> {
    private static final int DEFAULT_CAPACITY = 16;
    private static final double LOAD_FACTOR = 0.75;

    private Entry<K, V>[] buckets;
    private int size;
    private int capacity;

    // 链表节点
    static class Entry<K, V> {
        K key;
        V value;
        Entry<K, V> next;

        Entry(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    @SuppressWarnings("unchecked")
    public HashSearch() {
        this.capacity = DEFAULT_CAPACITY;
        this.buckets = new Entry[capacity];
        this.size = 0;
    }

    /**
     * 哈希函数
     */
    private int hash(K key) {
        if (key == null) return 0;
        return Math.abs(key.hashCode()) % capacity;
    }

    /**
     * 插入键值对
     */
    public void put(K key, V value) {
        if (size >= capacity * LOAD_FACTOR) {
            resize();
        }

        int index = hash(key);
        Entry<K, V> newEntry = new Entry<>(key, value);

        if (buckets[index] == null) {
            buckets[index] = newEntry;
        } else {
            // 解决冲突：链地址法
            Entry<K, V> current = buckets[index];
            while (current != null) {
                if (current.key.equals(key)) {
                    current.value = value;  // 更新值
                    return;
                }
                if (current.next == null) {
                    current.next = newEntry;
                    break;
                }
                current = current.next;
            }
        }
        size++;
    }

    /**
     * 哈希搜索
     * 平均时间复杂度：O(1)
     * 最坏时间复杂度：O(n)
     */
    public V get(K key) {
        int index = hash(key);
        Entry<K, V> current = buckets[index];

        while (current != null) {
            if (current.key.equals(key)) {
                return current.value;
            }
            current = current.next;
        }
        return null;  // 未找到
    }

    /**
     * 检查是否包含键
     */
    public boolean containsKey(K key) {
        return get(key) != null;
    }

    /**
     * 删除键值对
     */
    public V remove(K key) {
        int index = hash(key);
        Entry<K, V> current = buckets[index];
        Entry<K, V> prev = null;

        while (current != null) {
            if (current.key.equals(key)) {
                if (prev == null) {
                    buckets[index] = current.next;
                } else {
                    prev.next = current.next;
                }
                size--;
                return current.value;
            }
            prev = current;
            current = current.next;
        }
        return null;
    }

    /**
     * 扩容
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        Entry<K, V>[] oldBuckets = buckets;
        capacity *= 2;
        buckets = new Entry[capacity];
        size = 0;

        for (Entry<K, V> head : oldBuckets) {
            while (head != null) {
                put(head.key, head.value);
                head = head.next;
            }
        }
    }

    /**
     * 获取负载因子
     */
    public double getLoadFactor() {
        return (double) size / capacity;
    }
}
```

### 布隆过滤器

```java
/**
 * 布隆过滤器实现
 * 用于快速判断元素是否可能存在
 */
public class BloomFilter {
    private BitSet bitSet;
    private int bitSetSize;
    private int numHashFunctions;

    public BloomFilter(int expectedElements, double falsePositiveRate) {
        this.bitSetSize = (int) (-expectedElements * Math.log(falsePositiveRate)
                                / (Math.log(2) * Math.log(2)));
        this.numHashFunctions = (int) (bitSetSize * Math.log(2) / expectedElements);
        this.bitSet = new BitSet(bitSetSize);
    }

    /**
     * 添加元素
     */
    public void add(String element) {
        for (int i = 0; i < numHashFunctions; i++) {
            int hash = hash(element, i);
            bitSet.set(hash);
        }
    }

    /**
     * 检查元素是否可能存在
     */
    public boolean mightContain(String element) {
        for (int i = 0; i < numHashFunctions; i++) {
            int hash = hash(element, i);
            if (!bitSet.get(hash)) {
                return false;  // 肯定不存在
            }
        }
        return true;  // 可能存在
    }

    /**
     * 多重哈希函数
     */
    private int hash(String element, int seed) {
        int hash = element.hashCode();
        hash = hash ^ (hash >>> 16);
        hash = hash * (seed + 1);
        return Math.abs(hash) % bitSetSize;
    }
}
```

## 🌳 树搜索算法

### 二叉搜索树搜索

```java
/**
 * 二叉搜索树节点
 */
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode(int val) {
        this.val = val;
    }
}

/**
 * 二叉搜索树搜索算法
 */
public class BinarySearchTree {

    /**
     * 递归搜索
     * 时间复杂度：平均O(log n)，最坏O(n)
     */
    public static TreeNode searchRecursive(TreeNode root, int target) {
        if (root == null || root.val == target) {
            return root;
        }

        if (target < root.val) {
            return searchRecursive(root.left, target);
        } else {
            return searchRecursive(root.right, target);
        }
    }

    /**
     * 迭代搜索
     */
    public static TreeNode searchIterative(TreeNode root, int target) {
        TreeNode current = root;

        while (current != null && current.val != target) {
            if (target < current.val) {
                current = current.left;
            } else {
                current = current.right;
            }
        }
        return current;
    }

    /**
     * 查找最小值节点
     */
    public static TreeNode findMin(TreeNode root) {
        if (root == null) return null;

        while (root.left != null) {
            root = root.left;
        }
        return root;
    }

    /**
     * 查找最大值节点
     */
    public static TreeNode findMax(TreeNode root) {
        if (root == null) return null;

        while (root.right != null) {
            root = root.right;
        }
        return root;
    }

    /**
     * 查找后继节点
     */
    public static TreeNode findSuccessor(TreeNode root, int target) {
        TreeNode successor = null;

        while (root != null) {
            if (target < root.val) {
                successor = root;
                root = root.left;
            } else {
                root = root.right;
            }
        }
        return successor;
    }
}
```

### 深度优先搜索 (DFS)

```java
/**
 * 深度优先搜索实现
 */
public class DepthFirstSearch {

    /**
     * DFS递归实现
     */
    public static boolean dfsRecursive(TreeNode root, int target) {
        if (root == null) {
            return false;
        }

        if (root.val == target) {
            return true;
        }

        return dfsRecursive(root.left, target) ||
               dfsRecursive(root.right, target);
    }

    /**
     * DFS迭代实现（使用栈）
     */
    public static boolean dfsIterative(TreeNode root, int target) {
        if (root == null) return false;

        Stack<TreeNode> stack = new Stack<>();
        stack.push(root);

        while (!stack.isEmpty()) {
            TreeNode current = stack.pop();

            if (current.val == target) {
                return true;
            }

            if (current.right != null) {
                stack.push(current.right);
            }
            if (current.left != null) {
                stack.push(current.left);
            }
        }
        return false;
    }

    /**
     * DFS路径搜索
     */
    public static List<Integer> findPath(TreeNode root, int target) {
        List<Integer> path = new ArrayList<>();
        if (findPathHelper(root, target, path)) {
            return path;
        }
        return null;  // 未找到路径
    }

    private static boolean findPathHelper(TreeNode root, int target, List<Integer> path) {
        if (root == null) {
            return false;
        }

        path.add(root.val);

        if (root.val == target) {
            return true;
        }

        if (findPathHelper(root.left, target, path) ||
            findPathHelper(root.right, target, path)) {
            return true;
        }

        path.remove(path.size() - 1);  // 回溯
        return false;
    }
}
```

### 广度优先搜索 (BFS)

```java
/**
 * 广度优先搜索实现
 */
public class BreadthFirstSearch {

    /**
     * BFS基础实现
     */
    public static boolean bfs(TreeNode root, int target) {
        if (root == null) return false;

        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            TreeNode current = queue.poll();

            if (current.val == target) {
                return true;
            }

            if (current.left != null) {
                queue.offer(current.left);
            }
            if (current.right != null) {
                queue.offer(current.right);
            }
        }
        return false;
    }

    /**
     * 层次遍历搜索
     */
    public static int findLevel(TreeNode root, int target) {
        if (root == null) return -1;

        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        int level = 0;

        while (!queue.isEmpty()) {
            int size = queue.size();

            for (int i = 0; i < size; i++) {
                TreeNode current = queue.poll();

                if (current.val == target) {
                    return level;
                }

                if (current.left != null) {
                    queue.offer(current.left);
                }
                if (current.right != null) {
                    queue.offer(current.right);
                }
            }
            level++;
        }
        return -1;
    }

    /**
     * BFS最短路径搜索
     */
    public static int shortestPath(TreeNode root, int target) {
        if (root == null) return -1;
        if (root.val == target) return 0;

        Queue<TreeNode> queue = new LinkedList<>();
        Queue<Integer> distances = new LinkedList<>();
        Set<TreeNode> visited = new HashSet<>();

        queue.offer(root);
        distances.offer(0);
        visited.add(root);

        while (!queue.isEmpty()) {
            TreeNode current = queue.poll();
            int distance = distances.poll();

            TreeNode[] neighbors = {current.left, current.right};

            for (TreeNode neighbor : neighbors) {
                if (neighbor != null && !visited.contains(neighbor)) {
                    if (neighbor.val == target) {
                        return distance + 1;
                    }

                    queue.offer(neighbor);
                    distances.offer(distance + 1);
                    visited.add(neighbor);
                }
            }
        }
        return -1;
    }
}
```

## 🧠 智能搜索算法

### Minimax算法

```java
/**
 * Minimax算法实现
 * 用于博弈论中的决策搜索
 */
public class MinimaxAlgorithm {

    static class GameState {
        int[][] board;
        boolean isMaxPlayer;
        int depth;

        GameState(int[][] board, boolean isMaxPlayer, int depth) {
            this.board = board;
            this.isMaxPlayer = isMaxPlayer;
            this.depth = depth;
        }

        // 评估函数
        public int evaluate() {
            // 简化的评估函数，实际游戏中会更复杂
            int score = 0;
            for (int[] row : board) {
                for (int cell : row) {
                    score += cell;
                }
            }
            return score;
        }

        // 检查游戏是否结束
        public boolean isGameOver() {
            return depth >= 5;  // 简化条件
        }

        // 生成所有可能的下一步
        public List<GameState> generateMoves() {
            List<GameState> moves = new ArrayList<>();
            // 简化的移动生成，实际实现会根据具体游戏规则
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    if (board[i][j] == 0) {
                        int[][] newBoard = copyBoard(board);
                        newBoard[i][j] = isMaxPlayer ? 1 : -1;
                        moves.add(new GameState(newBoard, !isMaxPlayer, depth + 1));
                    }
                }
            }
            return moves;
        }

        private int[][] copyBoard(int[][] original) {
            int[][] copy = new int[original.length][];
            for (int i = 0; i < original.length; i++) {
                copy[i] = original[i].clone();
            }
            return copy;
        }
    }

    /**
     * Minimax算法核心
     */
    public static int minimax(GameState state, int depth, boolean isMaxPlayer) {
        if (depth == 0 || state.isGameOver()) {
            return state.evaluate();
        }

        if (isMaxPlayer) {
            int maxEval = Integer.MIN_VALUE;
            for (GameState child : state.generateMoves()) {
                int eval = minimax(child, depth - 1, false);
                maxEval = Math.max(maxEval, eval);
            }
            return maxEval;
        } else {
            int minEval = Integer.MAX_VALUE;
            for (GameState child : state.generateMoves()) {
                int eval = minimax(child, depth - 1, true);
                minEval = Math.min(minEval, eval);
            }
            return minEval;
        }
    }

    /**
     * 查找最佳移动
     */
    public static GameState findBestMove(GameState state, int depth) {
        int bestValue = Integer.MIN_VALUE;
        GameState bestMove = null;

        for (GameState child : state.generateMoves()) {
            int moveValue = minimax(child, depth - 1, false);
            if (moveValue > bestValue) {
                bestValue = moveValue;
                bestMove = child;
            }
        }
        return bestMove;
    }
}
```

### Alpha-Beta剪枝

```java
/**
 * Alpha-Beta剪枝优化的Minimax算法
 */
public class AlphaBetaPruning {

    /**
     * Alpha-Beta剪枝算法
     * 显著减少搜索空间
     */
    public static int alphaBeta(MinimaxAlgorithm.GameState state, int depth,
                               int alpha, int beta, boolean isMaxPlayer) {
        if (depth == 0 || state.isGameOver()) {
            return state.evaluate();
        }

        if (isMaxPlayer) {
            int maxEval = Integer.MIN_VALUE;
            for (MinimaxAlgorithm.GameState child : state.generateMoves()) {
                int eval = alphaBeta(child, depth - 1, alpha, beta, false);
                maxEval = Math.max(maxEval, eval);
                alpha = Math.max(alpha, eval);

                if (beta <= alpha) {
                    break;  // Beta剪枝
                }
            }
            return maxEval;
        } else {
            int minEval = Integer.MAX_VALUE;
            for (MinimaxAlgorithm.GameState child : state.generateMoves()) {
                int eval = alphaBeta(child, depth - 1, alpha, beta, true);
                minEval = Math.min(minEval, eval);
                beta = Math.min(beta, eval);

                if (beta <= alpha) {
                    break;  // Alpha剪枝
                }
            }
            return minEval;
        }
    }

    /**
     * 使用Alpha-Beta剪枝查找最佳移动
     */
    public static MinimaxAlgorithm.GameState findBestMoveAB(
            MinimaxAlgorithm.GameState state, int depth) {
        int bestValue = Integer.MIN_VALUE;
        MinimaxAlgorithm.GameState bestMove = null;
        int alpha = Integer.MIN_VALUE;
        int beta = Integer.MAX_VALUE;

        for (MinimaxAlgorithm.GameState child : state.generateMoves()) {
            int moveValue = alphaBeta(child, depth - 1, alpha, beta, false);
            if (moveValue > bestValue) {
                bestValue = moveValue;
                bestMove = child;
            }
            alpha = Math.max(alpha, moveValue);
        }
        return bestMove;
    }

    /**
     * 性能对比测试
     */
    public static void performanceComparison() {
        int[][] board = new int[3][3];
        MinimaxAlgorithm.GameState state =
            new MinimaxAlgorithm.GameState(board, true, 0);

        int depth = 6;

        // 标准Minimax测试
        long startTime = System.nanoTime();
        MinimaxAlgorithm.GameState result1 =
            MinimaxAlgorithm.findBestMove(state, depth);
        long minimaxTime = System.nanoTime() - startTime;

        // Alpha-Beta剪枝测试
        startTime = System.nanoTime();
        MinimaxAlgorithm.GameState result2 = findBestMoveAB(state, depth);
        long alphaBetaTime = System.nanoTime() - startTime;

        System.out.printf("标准Minimax耗时: %.2f ms%n",
                         minimaxTime / 1_000_000.0);
        System.out.printf("Alpha-Beta剪枝耗时: %.2f ms%n",
                         alphaBetaTime / 1_000_000.0);
        System.out.printf("性能提升: %.2fx%n",
                         (double)minimaxTime / alphaBetaTime);
    }
}
```

### A*搜索算法

```java
/**
 * A*启发式搜索算法
 * 用于路径规划和图搜索
 */
public class AStarSearch {

    static class Node implements Comparable<Node> {
        int x, y;
        int gCost;  // 从起点到当前节点的实际代价
        int hCost;  // 从当前节点到终点的启发式代价
        int fCost;  // f = g + h
        Node parent;

        Node(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public void calculateFCost() {
            this.fCost = this.gCost + this.hCost;
        }

        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.fCost, other.fCost);
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Node node = (Node) obj;
            return x == node.x && y == node.y;
        }

        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }
    }

    /**
     * A*搜索算法实现
     */
    public static List<Node> aStar(int[][] grid, Node start, Node goal) {
        PriorityQueue<Node> openSet = new PriorityQueue<>();
        Set<Node> closedSet = new HashSet<>();

        start.gCost = 0;
        start.hCost = calculateHeuristic(start, goal);
        start.calculateFCost();

        openSet.offer(start);

        while (!openSet.isEmpty()) {
            Node current = openSet.poll();

            if (current.equals(goal)) {
                return reconstructPath(current);
            }

            closedSet.add(current);

            for (Node neighbor : getNeighbors(grid, current)) {
                if (closedSet.contains(neighbor) ||
                    grid[neighbor.x][neighbor.y] == 1) {  // 障碍物
                    continue;
                }

                int tentativeGCost = current.gCost + 1;

                if (!openSet.contains(neighbor)) {
                    openSet.offer(neighbor);
                } else if (tentativeGCost >= neighbor.gCost) {
                    continue;
                }

                neighbor.parent = current;
                neighbor.gCost = tentativeGCost;
                neighbor.hCost = calculateHeuristic(neighbor, goal);
                neighbor.calculateFCost();
            }
        }
        return null;  // 未找到路径
    }

    /**
     * 启发式函数 - 曼哈顿距离
     */
    private static int calculateHeuristic(Node a, Node b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }

    /**
     * 获取邻居节点
     */
    private static List<Node> getNeighbors(int[][] grid, Node node) {
        List<Node> neighbors = new ArrayList<>();
        int[][] directions = {{-1,0}, {1,0}, {0,-1}, {0,1}};  // 上下左右

        for (int[] dir : directions) {
            int newX = node.x + dir[0];
            int newY = node.y + dir[1];

            if (newX >= 0 && newX < grid.length &&
                newY >= 0 && newY < grid[0].length) {
                neighbors.add(new Node(newX, newY));
            }
        }
        return neighbors;
    }

    /**
     * 重构路径
     */
    private static List<Node> reconstructPath(Node node) {
        List<Node> path = new ArrayList<>();
        Node current = node;

        while (current != null) {
            path.add(0, current);
            current = current.parent;
        }
        return path;
    }

    /**
     * 打印路径
     */
    public static void printPath(int[][] grid, List<Node> path) {
        int[][] pathGrid = new int[grid.length][grid[0].length];

        // 复制原网格
        for (int i = 0; i < grid.length; i++) {
            System.arraycopy(grid[i], 0, pathGrid[i], 0, grid[i].length);
        }

        // 标记路径
        for (Node node : path) {
            if (pathGrid[node.x][node.y] == 0) {
                pathGrid[node.x][node.y] = 2;  // 路径标记
            }
        }

        // 打印网格
        for (int[] row : pathGrid) {
            for (int cell : row) {
                switch (cell) {
                    case 0: System.out.print(" . "); break;
                    case 1: System.out.print(" # "); break;
                    case 2: System.out.print(" * "); break;
                }
            }
            System.out.println();
        }
    }
}
```

## 📊 性能分析与算法选择

### 算法复杂度对比

```java
/**
 * 搜索算法性能分析工具
 */
public class SearchAlgorithmAnalysis {

    /**
     * 算法性能对比测试
     */
    public static void comprehensivePerformanceTest() {
        int[] sizes = {1000, 10000, 100000, 1000000};

        System.out.println("=== 搜索算法性能对比 ===");
        System.out.printf("%-15s %-10s %-10s %-10s %-10s%n",
                         "算法", "1K", "10K", "100K", "1M");

        for (int size : sizes) {
            int[] sortedArray = generateSortedArray(size);
            int target = sortedArray[size - 1];  // 最坏情况

            // 线性搜索
            long startTime = System.nanoTime();
            LinearSearch.linearSearch(sortedArray, target);
            long linearTime = System.nanoTime() - startTime;

            // 二分搜索
            startTime = System.nanoTime();
            BinarySearch.binarySearch(sortedArray, target);
            long binaryTime = System.nanoTime() - startTime;

            // 插值搜索
            startTime = System.nanoTime();
            InterpolationSearch.interpolationSearch(sortedArray, target);
            long interpolationTime = System.nanoTime() - startTime;

            // 指数搜索
            startTime = System.nanoTime();
            ExponentialSearch.exponentialSearch(sortedArray, target);
            long exponentialTime = System.nanoTime() - startTime;

            System.out.printf("线性搜索     %8.2f  ", linearTime / 1_000_000.0);
            System.out.printf("二分搜索     %8.2f  ", binaryTime / 1_000_000.0);
            System.out.printf("插值搜索     %8.2f  ", interpolationTime / 1_000_000.0);
            System.out.printf("指数搜索     %8.2f%n", exponentialTime / 1_000_000.0);
        }
    }

    /**
     * 算法选择指南
     */
    public static void algorithmSelectionGuide() {
        System.out.println("\n=== 搜索算法选择指南 ===");
        System.out.println("1. 数据未排序:");
        System.out.println("   - 小数据集(n<1000): 线性搜索");
        System.out.println("   - 大数据集: 哈希搜索或先排序再二分搜索");

        System.out.println("\n2. 数据已排序:");
        System.out.println("   - 均匀分布: 插值搜索");
        System.out.println("   - 一般情况: 二分搜索");
        System.out.println("   - 无界数据: 指数搜索");

        System.out.println("\n3. 特殊场景:");
        System.out.println("   - 频繁插入删除: 平衡二叉搜索树");
        System.out.println("   - 近似查询: 布隆过滤器");
        System.out.println("   - 路径规划: A*搜索");
        System.out.println("   - 博弈决策: Minimax + Alpha-Beta剪枝");
    }

    private static int[] generateSortedArray(int size) {
        int[] arr = new int[size];
        for (int i = 0; i < size; i++) {
            arr[i] = i + 1;
        }
        return arr;
    }
}
```

### 空间复杂度分析

```java
/**
 * 搜索算法空间复杂度分析
 */
public class SpaceComplexityAnalysis {

    /**
     * 递归深度分析
     */
    public static void recursionDepthAnalysis() {
        System.out.println("=== 递归搜索算法空间复杂度 ===");

        int[] sizes = {1000, 10000, 100000};

        for (int size : sizes) {
            TreeNode balancedTree = createBalancedTree(size);
            TreeNode skewedTree = createSkewedTree(size);

            int balancedDepth = getTreeDepth(balancedTree);
            int skewedDepth = getTreeDepth(skewedTree);

            System.out.printf("树大小: %d%n", size);
            System.out.printf("  平衡树递归深度: %d (空间: O(log n))%n", balancedDepth);
            System.out.printf("  倾斜树递归深度: %d (空间: O(n))%n", skewedDepth);
            System.out.println();
        }
    }

    private static TreeNode createBalancedTree(int size) {
        if (size <= 0) return null;

        TreeNode root = new TreeNode(size / 2);
        root.left = createBalancedTree(size / 2);
        root.right = createBalancedTree(size - size / 2 - 1);
        return root;
    }

    private static TreeNode createSkewedTree(int size) {
        if (size <= 0) return null;

        TreeNode root = new TreeNode(1);
        TreeNode current = root;

        for (int i = 2; i <= size; i++) {
            current.right = new TreeNode(i);
            current = current.right;
        }
        return root;
    }

    private static int getTreeDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(getTreeDepth(root.left), getTreeDepth(root.right));
    }
}
```

## 🚀 现代应用与优化

### 并行搜索

```java
/**
 * 并行搜索算法实现
 */
public class ParallelSearch {

    /**
     * 并行线性搜索
     */
    public static int parallelLinearSearch(int[] arr, int target) {
        return Arrays.stream(arr)
                    .parallel()
                    .boxed()
                    .collect(Collectors.toList())
                    .indexOf(target);
    }

    /**
     * 分块并行搜索
     */
    public static int chunkParallelSearch(int[] arr, int target, int numThreads) {
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Future<Integer>> futures = new ArrayList<>();

        int chunkSize = arr.length / numThreads;

        for (int i = 0; i < numThreads; i++) {
            int start = i * chunkSize;
            int end = (i == numThreads - 1) ? arr.length : (i + 1) * chunkSize;

            futures.add(executor.submit(() -> {
                for (int j = start; j < end; j++) {
                    if (arr[j] == target) {
                        return j;
                    }
                }
                return -1;
            }));
        }

        try {
            for (Future<Integer> future : futures) {
                int result = future.get();
                if (result != -1) {
                    executor.shutdown();
                    return result;
                }
            }
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }

        executor.shutdown();
        return -1;
    }

    /**
     * Fork-Join并行搜索
     */
    static class ForkJoinSearch extends RecursiveTask<Integer> {
        private final int[] arr;
        private final int target;
        private final int start;
        private final int end;
        private static final int THRESHOLD = 1000;

        public ForkJoinSearch(int[] arr, int target, int start, int end) {
            this.arr = arr;
            this.target = target;
            this.start = start;
            this.end = end;
        }

        @Override
        protected Integer compute() {
            if (end - start <= THRESHOLD) {
                // 直接搜索
                for (int i = start; i < end; i++) {
                    if (arr[i] == target) {
                        return i;
                    }
                }
                return -1;
            } else {
                // 分割任务
                int mid = start + (end - start) / 2;
                ForkJoinSearch leftTask = new ForkJoinSearch(arr, target, start, mid);
                ForkJoinSearch rightTask = new ForkJoinSearch(arr, target, mid, end);

                leftTask.fork();
                int rightResult = rightTask.compute();
                int leftResult = leftTask.join();

                return leftResult != -1 ? leftResult : rightResult;
            }
        }
    }

    public static int forkJoinSearch(int[] arr, int target) {
        ForkJoinPool pool = new ForkJoinPool();
        ForkJoinSearch task = new ForkJoinSearch(arr, target, 0, arr.length);
        return pool.invoke(task);
    }
}
```

### 缓存优化搜索

```java
/**
 * 缓存友好的搜索算法
 */
public class CacheOptimizedSearch {

    /**
     * 块搜索 - 优化缓存局部性
     */
    public static int blockSearch(int[] arr, int target) {
        int blockSize = (int) Math.sqrt(arr.length);

        // 找到目标块
        int blockIndex = 0;
        while (blockIndex < arr.length && arr[blockIndex] < target) {
            blockIndex += blockSize;
        }

        // 在块内线性搜索
        int start = Math.max(0, blockIndex - blockSize);
        int end = Math.min(arr.length, blockIndex);

        for (int i = start; i < end; i++) {
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }

    /**
     * 预取优化的二分搜索
     */
    public static int prefetchBinarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            // 预取相邻数据
            if (mid > 0) {
                // 预取左侧数据
                int prefetch = arr[mid - 1];
            }
            if (mid < arr.length - 1) {
                // 预取右侧数据
                int prefetch = arr[mid + 1];
            }

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}
```

## 📈 实战应用案例

### 搜索引擎核心算法

```java
/**
 * 简化的搜索引擎实现
 * 展示多种搜索算法的组合使用
 */
public class SearchEngine {

    static class Document {
        String id;
        String content;
        Map<String, Integer> termFrequency;

        Document(String id, String content) {
            this.id = id;
            this.content = content;
            this.termFrequency = buildTermFrequency(content);
        }

        private Map<String, Integer> buildTermFrequency(String content) {
            Map<String, Integer> tf = new HashMap<>();
            String[] words = content.toLowerCase().split("\\s+");

            for (String word : words) {
                tf.put(word, tf.getOrDefault(word, 0) + 1);
            }
            return tf;
        }
    }

    static class SearchResult implements Comparable<SearchResult> {
        Document document;
        double score;

        SearchResult(Document document, double score) {
            this.document = document;
            this.score = score;
        }

        @Override
        public int compareTo(SearchResult other) {
            return Double.compare(other.score, this.score);  // 降序
        }
    }

    private List<Document> documents;
    private Map<String, Set<Document>> invertedIndex;
    private BloomFilter bloomFilter;

    public SearchEngine() {
        this.documents = new ArrayList<>();
        this.invertedIndex = new HashMap<>();
        this.bloomFilter = new BloomFilter(10000, 0.01);
    }

    /**
     * 添加文档到搜索引擎
     */
    public void addDocument(Document doc) {
        documents.add(doc);

        // 构建倒排索引
        for (String term : doc.termFrequency.keySet()) {
            invertedIndex.computeIfAbsent(term, k -> new HashSet<>()).add(doc);
            bloomFilter.add(term);  // 添加到布隆过滤器
        }
    }

    /**
     * 搜索文档
     */
    public List<SearchResult> search(String query, int limit) {
        String[] terms = query.toLowerCase().split("\\s+");
        Set<Document> candidates = new HashSet<>();

        // 使用布隆过滤器快速过滤
        for (String term : terms) {
            if (bloomFilter.mightContain(term)) {
                Set<Document> termDocs = invertedIndex.get(term);
                if (termDocs != null) {
                    if (candidates.isEmpty()) {
                        candidates.addAll(termDocs);
                    } else {
                        candidates.retainAll(termDocs);  // 交集
                    }
                }
            }
        }

        // 计算相关性得分
        List<SearchResult> results = new ArrayList<>();
        for (Document doc : candidates) {
            double score = calculateTfIdfScore(doc, terms);
            results.add(new SearchResult(doc, score));
        }

        // 排序并返回前N个结果
        Collections.sort(results);
        return results.stream().limit(limit).collect(Collectors.toList());
    }

    /**
     * TF-IDF得分计算
     */
    private double calculateTfIdfScore(Document doc, String[] terms) {
        double score = 0.0;
        int totalDocs = documents.size();

        for (String term : terms) {
            int tf = doc.termFrequency.getOrDefault(term, 0);
            if (tf > 0) {
                int docsWithTerm = invertedIndex.get(term).size();
                double idf = Math.log((double) totalDocs / docsWithTerm);
                score += tf * idf;
            }
        }
        return score;
    }
}
```

### 推荐系统搜索算法

```java
/**
 * 基于协同过滤的推荐系统
 * 使用高效搜索算法查找相似用户和物品
 */
public class RecommendationSystem {

    static class User {
        int id;
        Map<Integer, Double> ratings;  // 物品ID -> 评分

        User(int id) {
            this.id = id;
            this.ratings = new HashMap<>();
        }
    }

    static class Similarity implements Comparable<Similarity> {
        int userId;
        double similarity;

        Similarity(int userId, double similarity) {
            this.userId = userId;
            this.similarity = similarity;
        }

        @Override
        public int compareTo(Similarity other) {
            return Double.compare(other.similarity, this.similarity);
        }
    }

    private Map<Integer, User> users;
    private Map<Integer, Set<Integer>> itemUsers;  // 物品 -> 评价用户集合

    public RecommendationSystem() {
        this.users = new HashMap<>();
        this.itemUsers = new HashMap<>();
    }

    public void addRating(int userId, int itemId, double rating) {
        User user = users.computeIfAbsent(userId, User::new);
        user.ratings.put(itemId, rating);

        itemUsers.computeIfAbsent(itemId, k -> new HashSet<>()).add(userId);
    }

    /**
     * 使用A*搜索查找最相似的用户
     */
    public List<Similarity> findSimilarUsers(int userId, int k) {
        User targetUser = users.get(userId);
        if (targetUser == null) return new ArrayList<>();

        // 使用优先队列进行启发式搜索
        PriorityQueue<Similarity> candidates = new PriorityQueue<>();

        for (User otherUser : users.values()) {
            if (otherUser.id == userId) continue;

            double similarity = calculateCosineSimilarity(targetUser, otherUser);
            if (similarity > 0) {
                candidates.offer(new Similarity(otherUser.id, similarity));
            }
        }

        // 返回前k个最相似的用户
        return candidates.stream().limit(k).collect(Collectors.toList());
    }

    /**
     * 计算余弦相似度
     */
    private double calculateCosineSimilarity(User user1, User user2) {
        Set<Integer> commonItems = new HashSet<>(user1.ratings.keySet());
        commonItems.retainAll(user2.ratings.keySet());

        if (commonItems.isEmpty()) return 0.0;

        double sum1 = 0.0, sum2 = 0.0, sum1Sq = 0.0, sum2Sq = 0.0, pSum = 0.0;

        for (int itemId : commonItems) {
            double rating1 = user1.ratings.get(itemId);
            double rating2 = user2.ratings.get(itemId);

            sum1 += rating1;
            sum2 += rating2;
            sum1Sq += rating1 * rating1;
            sum2Sq += rating2 * rating2;
            pSum += rating1 * rating2;
        }

        double num = pSum - (sum1 * sum2 / commonItems.size());
        double den = Math.sqrt((sum1Sq - sum1 * sum1 / commonItems.size()) *
                              (sum2Sq - sum2 * sum2 / commonItems.size()));

        return den == 0 ? 0 : num / den;
    }

    /**
     * 生成推荐列表
     */
    public List<Integer> recommend(int userId, int numRecommendations) {
        List<Similarity> similarUsers = findSimilarUsers(userId, 50);
        Map<Integer, Double> itemScores = new HashMap<>();

        User targetUser = users.get(userId);
        Set<Integer> ratedItems = targetUser.ratings.keySet();

        // 基于相似用户的评分预测物品得分
        for (Similarity sim : similarUsers) {
            User similarUser = users.get(sim.userId);

            for (Map.Entry<Integer, Double> entry : similarUser.ratings.entrySet()) {
                int itemId = entry.getKey();
                if (!ratedItems.contains(itemId)) {
                    double score = entry.getValue() * sim.similarity;
                    itemScores.put(itemId, itemScores.getOrDefault(itemId, 0.0) + score);
                }
            }
        }

        // 按得分排序并返回推荐
        return itemScores.entrySet().stream()
                .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
                .limit(numRecommendations)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }
}
```

## 💡 总结与展望

### 算法选择决策树

#### 流程图表


**关系流向：**
```
A[搜索问题] → B{数据是否有序?}
B →|是| C{数据分布如何?}
B →|否| D{数据量大小?}
C →|均匀分布| E[插值搜索 O(log log n)]
C →|一般分布| F[二分搜索 O(log n)]
```

### 现代发展趋势

1. **机器学习驱动的搜索**
   - 学习用户偏好和行为模式
   - 个性化搜索结果排序
   - 语义搜索和向量检索

2. **分布式搜索系统**
   - 大规模数据的并行处理
   - 分片和副本策略
   - 一致性哈希和负载均衡

3. **近似搜索算法**
   - 局部敏感哈希(LSH)
   - 随机投影和降维技术
   - 量化和压缩搜索

4. **硬件优化搜索**
   - GPU并行搜索算法
   - SIMD指令集优化
   - 缓存感知算法设计

搜索算法作为计算机科学的基础，不断演进以适应新的应用需求。从基础的线性搜索到现代AI驱动的智能搜索，每种算法都有其独特的应用场景和优化空间。

掌握各种搜索算法的原理、实现和适用场景，能够帮助我们在面对不同问题时选择最合适的解决方案，是每个程序员必备的技能。随着技术的发展，搜索算法将继续在人工智能、大数据处理、推荐系统等领域发挥重要作用。

---

> 💡 **学习建议**:
> 1. 从基础算法开始，逐步掌握每种搜索方法的核心思想
> 2. 多做编程练习，加深对算法实现的理解
> 3. 关注算法的实际应用场景，培养选择合适算法的判断力
> 4. 跟进新技术发展，了解现代搜索系统的设计思路

**参考资源:**
- 《算法导论》- 搜索算法理论基础
- 《数据结构与算法分析》- 实现细节和性能分析
- ElasticSearch源码 - 现代搜索引擎实现
- TensorFlow/PyTorch - 机器学习搜索算法