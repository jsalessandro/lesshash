---
title: "算法详解：堆和堆排序 - 完全二叉树的优先队列艺术"
date: 2025-01-16T10:08:00+08:00
tags: ["算法", "堆", "堆排序", "Heap", "Java", "数据结构"]
categories: ["算法"]
series: ["高级算法入门教程"]
author: "lesshash"
---

## 引言

在计算机科学的世界里，堆（Heap）是一种既优雅又高效的数据结构。它不仅是优先队列的完美实现，更是许多高级算法的基石。从操作系统的任务调度到图算法中的最短路径，从数据库的查询优化到机器学习的特征选择，堆的身影无处不在。

今天，我们将深入探索堆这个奇妙的数据结构，从基本概念到高级应用，从理论分析到实际编程，带你全面掌握堆的精髓。

## 1. 堆的基本概念

### 1.1 什么是堆？

堆是一种特殊的完全二叉树，它满足堆性质：
- **最大堆（Max Heap）**：父节点的值总是大于等于其子节点的值
- **最小堆（Min Heap）**：父节点的值总是小于等于其子节点的值

### 1.2 堆的可视化表示

让我们通过一个最大堆的例子来理解：

```
        50
       /  \
     30    40
    / \   / \
   15 20 25 35
  /
 10
```

这个堆可以用数组表示为：`[50, 30, 40, 15, 20, 25, 35, 10]`

**重要的索引关系：**
- 对于索引为 `i` 的节点：
  - 父节点索引：`(i-1)/2`
  - 左子节点索引：`2*i+1`
  - 右子节点索引：`2*i+2`

### 1.3 生活中的堆例子

#### 医院急诊系统
想象一个医院的急诊科，病人按照病情严重程度排队：
- 心脏病发作（优先级：10）
- 骨折（优先级：5）
- 感冒发烧（优先级：2）

无论什么时候有新病人到达，系统都会自动调整，确保最紧急的病人总是排在最前面。

#### 任务调度系统
操作系统中的进程调度也是堆的经典应用：
```
高优先级任务    │ 系统进程 (优先级: 9)
              │ 实时应用 (优先级: 7)
普通任务       │ 用户程序 (优先级: 5)
              │ 后台服务 (优先级: 3)
低优先级任务    │ 垃圾回收 (优先级: 1)
```

## 2. 堆的核心操作

### 2.1 向上调整（Heapify Up）

当插入新元素时，我们需要维护堆性质：

```java
/**
 * 向上调整，维护堆性质
 * @param index 需要调整的节点索引
 */
private void heapifyUp(int index) {
    while (index > 0) {
        int parentIndex = (index - 1) / 2;
        if (heap[index] <= heap[parentIndex]) {
            break; // 已满足堆性质
        }
        swap(index, parentIndex);
        index = parentIndex;
    }
}
```

### 2.2 向下调整（Heapify Down）

当删除根节点时，我们需要重新调整堆：

```java
/**
 * 向下调整，维护堆性质
 * @param index 需要调整的节点索引
 */
private void heapifyDown(int index) {
    int size = heap.size();
    while (true) {
        int largest = index;
        int leftChild = 2 * index + 1;
        int rightChild = 2 * index + 2;

        // 找到最大的节点
        if (leftChild < size && heap[leftChild] > heap[largest]) {
            largest = leftChild;
        }
        if (rightChild < size && heap[rightChild] > heap[largest]) {
            largest = rightChild;
        }

        if (largest == index) {
            break; // 已满足堆性质
        }

        swap(index, largest);
        index = largest;
    }
}
```

## 3. 完整的堆实现

### 3.1 最大堆实现

```java
import java.util.*;

/**
 * 最大堆的完整实现
 * 支持动态扩容和常见操作
 */
public class MaxHeap {
    private List<Integer> heap;

    public MaxHeap() {
        this.heap = new ArrayList<>();
    }

    public MaxHeap(int[] array) {
        this.heap = new ArrayList<>();
        for (int value : array) {
            heap.add(value);
        }
        buildHeap();
    }

    /**
     * 从数组构建堆 - O(n) 时间复杂度
     */
    private void buildHeap() {
        // 从最后一个非叶子节点开始向下调整
        for (int i = (heap.size() - 2) / 2; i >= 0; i--) {
            heapifyDown(i);
        }
    }

    /**
     * 插入元素 - O(log n)
     */
    public void insert(int value) {
        heap.add(value);
        heapifyUp(heap.size() - 1);
    }

    /**
     * 提取最大值 - O(log n)
     */
    public int extractMax() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("堆为空");
        }

        int max = heap.get(0);
        int lastElement = heap.remove(heap.size() - 1);

        if (!heap.isEmpty()) {
            heap.set(0, lastElement);
            heapifyDown(0);
        }

        return max;
    }

    /**
     * 查看最大值 - O(1)
     */
    public int peek() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("堆为空");
        }
        return heap.get(0);
    }

    /**
     * 获取堆大小
     */
    public int size() {
        return heap.size();
    }

    /**
     * 判断是否为空
     */
    public boolean isEmpty() {
        return heap.isEmpty();
    }

    /**
     * 向上调整
     */
    private void heapifyUp(int index) {
        while (index > 0) {
            int parentIndex = (index - 1) / 2;
            if (heap.get(index) <= heap.get(parentIndex)) {
                break;
            }
            swap(index, parentIndex);
            index = parentIndex;
        }
    }

    /**
     * 向下调整
     */
    private void heapifyDown(int index) {
        int size = heap.size();
        while (true) {
            int largest = index;
            int leftChild = 2 * index + 1;
            int rightChild = 2 * index + 2;

            if (leftChild < size && heap.get(leftChild) > heap.get(largest)) {
                largest = leftChild;
            }
            if (rightChild < size && heap.get(rightChild) > heap.get(largest)) {
                largest = rightChild;
            }

            if (largest == index) {
                break;
            }

            swap(index, largest);
            index = largest;
        }
    }

    /**
     * 交换两个元素
     */
    private void swap(int i, int j) {
        Collections.swap(heap, i, j);
    }

    /**
     * 打印堆的可视化表示
     */
    public void printHeap() {
        if (heap.isEmpty()) {
            System.out.println("堆为空");
            return;
        }

        int level = 0;
        int count = 0;
        int levelSize = 1;

        for (int i = 0; i < heap.size(); i++) {
            System.out.printf("%4d", heap.get(i));
            count++;

            if (count == levelSize) {
                System.out.println();
                level++;
                count = 0;
                levelSize *= 2;
            }
        }
        System.out.println();
    }
}
```

### 3.2 最小堆实现

```java
/**
 * 最小堆实现
 * 只需要修改比较逻辑即可
 */
public class MinHeap {
    private List<Integer> heap;

    public MinHeap() {
        this.heap = new ArrayList<>();
    }

    // 其他方法与MaxHeap相似，只需修改比较逻辑

    /**
     * 向上调整（最小堆版本）
     */
    private void heapifyUp(int index) {
        while (index > 0) {
            int parentIndex = (index - 1) / 2;
            if (heap.get(index) >= heap.get(parentIndex)) {
                break;
            }
            swap(index, parentIndex);
            index = parentIndex;
        }
    }

    /**
     * 向下调整（最小堆版本）
     */
    private void heapifyDown(int index) {
        int size = heap.size();
        while (true) {
            int smallest = index;
            int leftChild = 2 * index + 1;
            int rightChild = 2 * index + 2;

            if (leftChild < size && heap.get(leftChild) < heap.get(smallest)) {
                smallest = leftChild;
            }
            if (rightChild < size && heap.get(rightChild) < heap.get(smallest)) {
                smallest = rightChild;
            }

            if (smallest == index) {
                break;
            }

            swap(index, smallest);
            index = smallest;
        }
    }

    // 其他方法实现...
}
```

## 4. 堆排序算法

堆排序是一种基于堆的高效排序算法，具有 O(n log n) 的时间复杂度且为原地排序。

### 4.1 堆排序的核心思想

1. **构建最大堆**：将无序数组调整为最大堆
2. **逐步提取最大值**：将堆顶（最大值）与末尾元素交换，然后调整剩余部分为堆

### 4.2 堆排序的详细实现

```java
/**
 * 堆排序的完整实现
 */
public class HeapSort {

    /**
     * 堆排序主方法
     * @param arr 待排序数组
     */
    public static void heapSort(int[] arr) {
        int n = arr.length;

        // 第一阶段：构建最大堆
        System.out.println("=== 构建最大堆过程 ===");
        buildMaxHeap(arr);
        printArray(arr, "初始最大堆");

        // 第二阶段：逐步提取最大值
        System.out.println("\n=== 排序过程 ===");
        for (int i = n - 1; i > 0; i--) {
            // 将最大值（堆顶）移到数组末尾
            swap(arr, 0, i);
            System.out.printf("交换 arr[0]=%d 和 arr[%d]=%d: ", arr[i], i, arr[0]);
            printArray(arr, "");

            // 调整剩余部分为堆
            heapify(arr, i, 0);
            System.out.printf("调整后的堆: ");
            printArray(arr, "");
            System.out.println();
        }
    }

    /**
     * 构建最大堆
     */
    private static void buildMaxHeap(int[] arr) {
        int n = arr.length;
        // 从最后一个非叶子节点开始，向前调整
        for (int i = (n / 2) - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }
    }

    /**
     * 调整堆（向下调整）
     * @param arr 数组
     * @param heapSize 堆的大小
     * @param rootIndex 根节点索引
     */
    private static void heapify(int[] arr, int heapSize, int rootIndex) {
        int largest = rootIndex;
        int leftChild = 2 * rootIndex + 1;
        int rightChild = 2 * rootIndex + 2;

        // 找到最大值的索引
        if (leftChild < heapSize && arr[leftChild] > arr[largest]) {
            largest = leftChild;
        }
        if (rightChild < heapSize && arr[rightChild] > arr[largest]) {
            largest = rightChild;
        }

        // 如果最大值不是根节点，则交换并继续调整
        if (largest != rootIndex) {
            swap(arr, rootIndex, largest);
            heapify(arr, heapSize, largest);
        }
    }

    /**
     * 交换数组中的两个元素
     */
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }

    /**
     * 打印数组
     */
    private static void printArray(int[] arr, String description) {
        if (!description.isEmpty()) {
            System.out.print(description + ": ");
        }
        System.out.print("[");
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]);
            if (i < arr.length - 1) {
                System.out.print(", ");
            }
        }
        System.out.println("]");
    }

    /**
     * 测试堆排序
     */
    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90, 5};

        System.out.println("原始数组:");
        printArray(arr, "");

        System.out.println("\n开始堆排序...");
        heapSort(arr);

        System.out.println("排序结果:");
        printArray(arr, "");
    }
}
```

### 4.3 堆排序过程可视化

让我们通过一个具体例子来理解堆排序的过程：

**原始数组：** `[64, 34, 25, 12, 22, 11, 90, 5]`

**步骤1：构建最大堆**
```
原始数组:     64  34  25  12  22  11  90   5
构建最大堆:   90  34  64  12  22  11  25   5

    90
   /  \
  34   64
 / |   |  \
12 22  11  25
|
5
```

**步骤2：排序过程**
```
第1次: 交换90和5  -> [5, 34, 64, 12, 22, 11, 25, 90]
      调整堆     -> [64, 34, 25, 12, 22, 11, 5, 90]

第2次: 交换64和5  -> [5, 34, 25, 12, 22, 11, 64, 90]
      调整堆     -> [34, 22, 25, 12, 5, 11, 64, 90]

第3次: 交换34和11 -> [11, 22, 25, 12, 5, 34, 64, 90]
      调整堆     -> [25, 22, 11, 12, 5, 34, 64, 90]

...继续直到完全排序
```

## 5. 堆的高级变种

### 5.1 二项堆（Binomial Heap）

二项堆是一种更复杂的堆结构，支持快速的合并操作：

```java
/**
 * 二项堆节点
 */
class BinomialNode {
    int key;
    int degree;
    BinomialNode parent;
    BinomialNode child;
    BinomialNode sibling;

    public BinomialNode(int key) {
        this.key = key;
        this.degree = 0;
        this.parent = null;
        this.child = null;
        this.sibling = null;
    }
}

/**
 * 二项堆实现（简化版）
 */
public class BinomialHeap {
    private BinomialNode head;

    /**
     * 合并两个二项堆 - O(log n)
     */
    public BinomialHeap union(BinomialHeap other) {
        BinomialHeap result = new BinomialHeap();
        result.head = merge(this.head, other.head);

        if (result.head == null) {
            return result;
        }

        // 确保每个度数最多只有一个根
        BinomialNode prev = null;
        BinomialNode curr = result.head;
        BinomialNode next = curr.sibling;

        while (next != null) {
            if (curr.degree != next.degree ||
                (next.sibling != null && next.sibling.degree == curr.degree)) {
                prev = curr;
                curr = next;
            } else {
                if (curr.key <= next.key) {
                    curr.sibling = next.sibling;
                    link(next, curr);
                } else {
                    if (prev == null) {
                        result.head = next;
                    } else {
                        prev.sibling = next;
                    }
                    link(curr, next);
                    curr = next;
                }
            }
            next = curr.sibling;
        }

        return result;
    }

    /**
     * 连接两个相同度数的二项树
     */
    private void link(BinomialNode child, BinomialNode parent) {
        child.parent = parent;
        child.sibling = parent.child;
        parent.child = child;
        parent.degree++;
    }

    /**
     * 合并两个二项堆的根链表
     */
    private BinomialNode merge(BinomialNode h1, BinomialNode h2) {
        if (h1 == null) return h2;
        if (h2 == null) return h1;

        BinomialNode head;
        if (h1.degree <= h2.degree) {
            head = h1;
            h1 = h1.sibling;
        } else {
            head = h2;
            h2 = h2.sibling;
        }

        BinomialNode tail = head;
        while (h1 != null && h2 != null) {
            if (h1.degree <= h2.degree) {
                tail.sibling = h1;
                h1 = h1.sibling;
            } else {
                tail.sibling = h2;
                h2 = h2.sibling;
            }
            tail = tail.sibling;
        }

        tail.sibling = (h1 != null) ? h1 : h2;
        return head;
    }
}
```

### 5.2 斐波那契堆（Fibonacci Heap）

斐波那契堆提供了更好的摊还时间复杂度，特别适用于图算法：

- **插入**: O(1) 摊还时间
- **查找最小值**: O(1)
- **合并**: O(1)
- **减小键值**: O(1) 摊还时间
- **删除最小值**: O(log n) 摊还时间

## 6. 堆的实际应用

### 6.1 Dijkstra 最短路径算法

```java
/**
 * 使用堆优化的Dijkstra算法
 */
public class DijkstraWithHeap {

    static class Edge {
        int to, weight;

        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }

    static class Node implements Comparable<Node> {
        int vertex, distance;

        Node(int vertex, int distance) {
            this.vertex = vertex;
            this.distance = distance;
        }

        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.distance, other.distance);
        }
    }

    /**
     * Dijkstra算法求单源最短路径
     * @param graph 图的邻接表表示
     * @param start 起始顶点
     * @return 到各顶点的最短距离
     */
    public static int[] dijkstra(List<List<Edge>> graph, int start) {
        int n = graph.size();
        int[] dist = new int[n];
        boolean[] visited = new boolean[n];

        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[start] = 0;

        // 使用优先队列（最小堆）
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(start, 0));

        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;

            if (visited[u]) continue;
            visited[u] = true;

            // 遍历所有邻接顶点
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                int weight = edge.weight;

                if (!visited[v] && dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    pq.offer(new Node(v, dist[v]));
                }
            }
        }

        return dist;
    }
}
```

### 6.2 Top-K 问题解决方案

```java
/**
 * Top-K问题的高效解决方案
 */
public class TopKSolver {

    /**
     * 查找数组中第K大的元素
     * @param nums 数组
     * @param k 第k大
     * @return 第k大的元素
     */
    public static int findKthLargest(int[] nums, int k) {
        // 使用最小堆，保持堆大小为k
        PriorityQueue<Integer> minHeap = new PriorityQueue<>(k);

        for (int num : nums) {
            if (minHeap.size() < k) {
                minHeap.offer(num);
            } else if (num > minHeap.peek()) {
                minHeap.poll();
                minHeap.offer(num);
            }
        }

        return minHeap.peek();
    }

    /**
     * 查找数据流中的中位数
     */
    static class MedianFinder {
        private PriorityQueue<Integer> maxHeap; // 存储较小的一半
        private PriorityQueue<Integer> minHeap; // 存储较大的一半

        public MedianFinder() {
            maxHeap = new PriorityQueue<>((a, b) -> b - a); // 最大堆
            minHeap = new PriorityQueue<>(); // 最小堆
        }

        public void addNum(int num) {
            if (maxHeap.isEmpty() || num <= maxHeap.peek()) {
                maxHeap.offer(num);
            } else {
                minHeap.offer(num);
            }

            // 平衡两个堆的大小
            if (maxHeap.size() > minHeap.size() + 1) {
                minHeap.offer(maxHeap.poll());
            } else if (minHeap.size() > maxHeap.size() + 1) {
                maxHeap.offer(minHeap.poll());
            }
        }

        public double findMedian() {
            if (maxHeap.size() == minHeap.size()) {
                return (maxHeap.peek() + minHeap.peek()) / 2.0;
            } else if (maxHeap.size() > minHeap.size()) {
                return maxHeap.peek();
            } else {
                return minHeap.peek();
            }
        }
    }

    /**
     * 滑动窗口中的最大值
     */
    public static int[] maxSlidingWindow(int[] nums, int k) {
        if (nums.length == 0 || k == 0) return new int[0];

        int n = nums.length;
        int[] result = new int[n - k + 1];

        // 使用最大堆存储 (值, 索引) 对
        PriorityQueue<int[]> maxHeap = new PriorityQueue<>((a, b) -> b[0] - a[0]);

        for (int i = 0; i < n; i++) {
            maxHeap.offer(new int[]{nums[i], i});

            // 移除窗口外的元素
            while (!maxHeap.isEmpty() && maxHeap.peek()[1] <= i - k) {
                maxHeap.poll();
            }

            // 记录当前窗口的最大值
            if (i >= k - 1) {
                result[i - k + 1] = maxHeap.peek()[0];
            }
        }

        return result;
    }
}
```

### 6.3 任务调度系统

```java
/**
 * 基于堆的任务调度系统
 */
public class TaskScheduler {

    static class Task implements Comparable<Task> {
        int id;
        int priority;
        long deadline;
        String description;

        public Task(int id, int priority, long deadline, String description) {
            this.id = id;
            this.priority = priority;
            this.deadline = deadline;
            this.description = description;
        }

        @Override
        public int compareTo(Task other) {
            // 首先按优先级排序，然后按截止时间
            if (this.priority != other.priority) {
                return other.priority - this.priority; // 高优先级在前
            }
            return Long.compare(this.deadline, other.deadline); // 早截止时间在前
        }

        @Override
        public String toString() {
            return String.format("Task{id=%d, priority=%d, deadline=%d, desc='%s'}",
                    id, priority, deadline, description);
        }
    }

    private PriorityQueue<Task> taskQueue;
    private int nextTaskId;

    public TaskScheduler() {
        this.taskQueue = new PriorityQueue<>();
        this.nextTaskId = 1;
    }

    /**
     * 添加新任务
     */
    public void addTask(int priority, long deadline, String description) {
        Task task = new Task(nextTaskId++, priority, deadline, description);
        taskQueue.offer(task);
        System.out.println("添加任务: " + task);
    }

    /**
     * 执行下一个任务
     */
    public Task executeNext() {
        if (taskQueue.isEmpty()) {
            System.out.println("没有待执行的任务");
            return null;
        }

        Task task = taskQueue.poll();
        System.out.println("执行任务: " + task);
        return task;
    }

    /**
     * 查看下一个任务
     */
    public Task peekNext() {
        return taskQueue.peek();
    }

    /**
     * 获取队列大小
     */
    public int getQueueSize() {
        return taskQueue.size();
    }

    /**
     * 演示任务调度
     */
    public static void main(String[] args) {
        TaskScheduler scheduler = new TaskScheduler();

        // 添加一些任务
        scheduler.addTask(5, System.currentTimeMillis() + 3600000, "处理用户注册");
        scheduler.addTask(9, System.currentTimeMillis() + 1800000, "系统安全扫描");
        scheduler.addTask(3, System.currentTimeMillis() + 7200000, "数据备份");
        scheduler.addTask(7, System.currentTimeMillis() + 900000, "发送邮件通知");
        scheduler.addTask(9, System.currentTimeMillis() + 600000, "处理紧急故障");

        System.out.println("\n=== 按优先级执行任务 ===");
        while (scheduler.getQueueSize() > 0) {
            scheduler.executeNext();
        }
    }
}
```

## 7. 性能分析与优化

### 7.1 时间复杂度分析

| 操作 | 二叉堆 | 二项堆 | 斐波那契堆 |
|------|--------|--------|------------|
| 构建堆 | O(n) | O(n) | O(n) |
| 插入 | O(log n) | O(log n) | O(1)* |
| 查找最值 | O(1) | O(log n) | O(1) |
| 删除最值 | O(log n) | O(log n) | O(log n)* |
| 合并 | O(n) | O(log n) | O(1) |
| 减小键值 | O(log n) | O(log n) | O(1)* |

*表示摊还时间复杂度

### 7.2 空间复杂度

- **二叉堆**: O(n) - 只需要数组存储
- **二项堆**: O(n) - 需要额外的指针
- **斐波那契堆**: O(n) - 需要更多的指针和标记

### 7.3 堆的优化技巧

#### 7.3.1 缓存优化

```java
/**
 * 缓存友好的堆实现
 */
public class CacheOptimizedHeap {
    private int[] heap;
    private int size;
    private int capacity;

    // 使用位运算优化索引计算
    private int parent(int i) { return (i - 1) >> 1; }
    private int leftChild(int i) { return (i << 1) + 1; }
    private int rightChild(int i) { return (i << 1) + 2; }

    // 预分配数组避免频繁扩容
    public CacheOptimizedHeap(int initialCapacity) {
        this.capacity = initialCapacity;
        this.heap = new int[capacity];
        this.size = 0;
    }

    // 批量插入优化
    public void insertBatch(int[] elements) {
        for (int element : elements) {
            if (size < capacity) {
                heap[size++] = element;
            }
        }
        // 批量调整，减少单次插入的开销
        for (int i = (size - 2) / 2; i >= 0; i--) {
            heapifyDown(i);
        }
    }
}
```

#### 7.3.2 多路堆优化

```java
/**
 * d-ary堆（多路堆）实现
 * 通过增加分支因子来减少树的高度
 */
public class DaryHeap {
    private int[] heap;
    private int size;
    private int d; // 分支因子

    public DaryHeap(int capacity, int d) {
        this.heap = new int[capacity];
        this.size = 0;
        this.d = d;
    }

    private int parent(int i) {
        return (i - 1) / d;
    }

    private int kthChild(int i, int k) {
        return d * i + k;
    }

    /**
     * 向上调整（d-ary版本）
     */
    private void heapifyUp(int index) {
        int parentIndex = parent(index);
        if (index > 0 && heap[index] > heap[parentIndex]) {
            swap(index, parentIndex);
            heapifyUp(parentIndex);
        }
    }

    /**
     * 向下调整（d-ary版本）
     */
    private void heapifyDown(int index) {
        int maxChild = -1;
        int maxValue = heap[index];

        // 找到所有子节点中的最大值
        for (int k = 1; k <= d; k++) {
            int childIndex = kthChild(index, k);
            if (childIndex < size && heap[childIndex] > maxValue) {
                maxValue = heap[childIndex];
                maxChild = childIndex;
            }
        }

        if (maxChild != -1) {
            swap(index, maxChild);
            heapifyDown(maxChild);
        }
    }
}
```

## 8. 堆的扩展应用

### 8.1 外部排序

当数据量过大无法完全加载到内存时，可以使用堆进行外部排序：

```java
/**
 * 外部排序实现
 */
public class ExternalSort {

    /**
     * 多路归并排序
     * @param inputFiles 已排序的输入文件列表
     * @param outputFile 输出文件
     */
    public static void mergeFiles(List<String> inputFiles, String outputFile) {
        try {
            // 使用最小堆进行多路归并
            PriorityQueue<FileNode> minHeap = new PriorityQueue<>();
            List<BufferedReader> readers = new ArrayList<>();

            // 打开所有输入文件
            for (int i = 0; i < inputFiles.size(); i++) {
                BufferedReader reader = new BufferedReader(new FileReader(inputFiles.get(i)));
                readers.add(reader);

                String line = reader.readLine();
                if (line != null) {
                    minHeap.offer(new FileNode(Integer.parseInt(line), i));
                }
            }

            BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile));

            // 多路归并
            while (!minHeap.isEmpty()) {
                FileNode node = minHeap.poll();
                writer.write(node.value + "\n");

                // 从同一文件读取下一个数字
                String nextLine = readers.get(node.fileIndex).readLine();
                if (nextLine != null) {
                    minHeap.offer(new FileNode(Integer.parseInt(nextLine), node.fileIndex));
                }
            }

            // 关闭所有文件
            writer.close();
            for (BufferedReader reader : readers) {
                reader.close();
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    static class FileNode implements Comparable<FileNode> {
        int value;
        int fileIndex;

        FileNode(int value, int fileIndex) {
            this.value = value;
            this.fileIndex = fileIndex;
        }

        @Override
        public int compareTo(FileNode other) {
            return Integer.compare(this.value, other.value);
        }
    }
}
```

### 8.2 实时数据分析

```java
/**
 * 实时数据流分析器
 */
public class RealTimeAnalyzer {
    private PriorityQueue<Integer> minHeap; // 存储较大的50%
    private PriorityQueue<Integer> maxHeap; // 存储较小的50%
    private int windowSize;
    private Queue<Integer> window;

    public RealTimeAnalyzer(int windowSize) {
        this.windowSize = windowSize;
        this.minHeap = new PriorityQueue<>();
        this.maxHeap = new PriorityQueue<>((a, b) -> b - a);
        this.window = new LinkedList<>();
    }

    /**
     * 添加新数据点
     */
    public void addDataPoint(int value) {
        window.offer(value);

        // 维护滑动窗口大小
        if (window.size() > windowSize) {
            int removed = window.poll();
            removeFromHeaps(removed);
        }

        // 添加到堆中
        addToHeaps(value);

        // 输出当前统计信息
        System.out.printf("新数据: %d, 中位数: %.1f, 窗口大小: %d%n",
                value, getMedian(), window.size());
    }

    private void addToHeaps(int value) {
        if (maxHeap.isEmpty() || value <= maxHeap.peek()) {
            maxHeap.offer(value);
        } else {
            minHeap.offer(value);
        }
        balanceHeaps();
    }

    private void removeFromHeaps(int value) {
        if (maxHeap.contains(value)) {
            maxHeap.remove(value);
        } else {
            minHeap.remove(value);
        }
        balanceHeaps();
    }

    private void balanceHeaps() {
        if (maxHeap.size() > minHeap.size() + 1) {
            minHeap.offer(maxHeap.poll());
        } else if (minHeap.size() > maxHeap.size() + 1) {
            maxHeap.offer(minHeap.poll());
        }
    }

    private double getMedian() {
        if (maxHeap.size() == minHeap.size()) {
            return (maxHeap.peek() + minHeap.peek()) / 2.0;
        } else if (maxHeap.size() > minHeap.size()) {
            return maxHeap.peek();
        } else {
            return minHeap.peek();
        }
    }
}
```

## 9. 常见面试题与解答

### 9.1 实现一个支持 O(1) 时间获取最小值的栈

```java
/**
 * 支持O(1)获取最小值的栈
 */
public class MinStack {
    private Stack<Integer> stack;
    private Stack<Integer> minStack;

    public MinStack() {
        stack = new Stack<>();
        minStack = new Stack<>();
    }

    public void push(int val) {
        stack.push(val);
        if (minStack.isEmpty() || val <= minStack.peek()) {
            minStack.push(val);
        }
    }

    public void pop() {
        if (stack.isEmpty()) return;

        int popped = stack.pop();
        if (popped == minStack.peek()) {
            minStack.pop();
        }
    }

    public int top() {
        return stack.peek();
    }

    public int getMin() {
        return minStack.peek();
    }
}
```

### 9.2 合并 K 个有序链表

```java
/**
 * 使用堆合并K个有序链表
 */
public ListNode mergeKLists(ListNode[] lists) {
    if (lists == null || lists.length == 0) {
        return null;
    }

    PriorityQueue<ListNode> heap = new PriorityQueue<>((a, b) -> a.val - b.val);

    // 将每个链表的头节点加入堆
    for (ListNode head : lists) {
        if (head != null) {
            heap.offer(head);
        }
    }

    ListNode dummy = new ListNode(0);
    ListNode current = dummy;

    while (!heap.isEmpty()) {
        ListNode node = heap.poll();
        current.next = node;
        current = current.next;

        if (node.next != null) {
            heap.offer(node.next);
        }
    }

    return dummy.next;
}
```

## 10. 总结与最佳实践

### 10.1 何时使用堆？

1. **需要频繁获取最值**：如优先队列、任务调度
2. **Top-K 问题**：查找最大/最小的K个元素
3. **动态中位数**：数据流中位数维护
4. **图算法优化**：Dijkstra、Prim等算法
5. **外部排序**：内存有限的大数据排序

### 10.2 堆的优缺点

**优点：**
- 插入和删除效率高：O(log n)
- 空间效率好：可以用数组实现
- 适合动态数据：支持在线算法
- 实现相对简单

**缺点：**
- 不支持快速搜索：O(n) 时间复杂度
- 不保证有序遍历
- 删除任意元素复杂

### 10.3 性能优化建议

1. **选择合适的堆类型**：
   - 简单应用：二叉堆
   - 频繁合并：二项堆
   - 图算法：斐波那契堆

2. **实现优化**：
   - 使用位运算计算索引
   - 预分配足够的空间
   - 考虑缓存局部性

3. **算法选择**：
   - 小数据量：简单排序可能更快
   - 大数据量：堆排序稳定高效
   - 外部排序：必须使用堆

堆作为一种优雅而强大的数据结构，在现代计算机科学中扮演着重要角色。通过深入理解其原理和应用，我们可以在面对复杂问题时游刃有余，写出更加高效和优雅的代码。

无论是在算法竞赛、技术面试，还是实际项目开发中，堆都是不可或缺的利器。掌握堆的精髓，就是掌握了解决优先级和动态排序问题的金钥匙。