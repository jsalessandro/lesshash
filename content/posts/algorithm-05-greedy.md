---
title: "算法详解：贪心算法 - 局部最优的全局智慧"
date: 2025-01-13T10:05:00+08:00
tags: ["算法", "贪心算法", "Greedy", "Java", "优化"]
categories: ["算法"]
series: ["高级算法入门教程"]
author: "lesshash"
---

# 算法详解：贪心算法 - 局部最优的全局智慧

贪心算法（Greedy Algorithm）是一种在每一步选择中都采取在当前状态下最好或最优选择的算法思想。它的核心思想是通过一系列局部最优选择来构造全局最优解。虽然贪心算法并不总是能得到全局最优解，但对于某些特定问题，它能够以简单高效的方式找到最优解。

## 1. 贪心算法基本概念

### 1.1 核心思想

贪心算法的基本思想是：
- 将问题分解为若干个子问题
- 对每个子问题求解，得到子问题的局部最优解
- 将子问题的局部最优解合成原来问题的一个解

```
贪心选择决策树示意图：

                   开始
                    |
            [做出贪心选择]
                    |
                子问题1
                    |
            [做出贪心选择]
                    |
                子问题2
                    |
                   ...
                    |
            [做出贪心选择]
                    |
                  结束
```

### 1.2 贪心算法特点

1. **贪心选择性质**：每一步都做出当前看起来最好的选择
2. **最优子结构**：问题的最优解包含子问题的最优解
3. **无回溯**：一旦做出选择，就不再改变
4. **自顶向下**：从问题的顶层开始，逐步向下分解

### 1.3 算法模板

```java
public class GreedyTemplate {
    public int greedy(int[] input) {
        // 1. 初始化
        int result = 0;

        // 2. 排序（如果需要）
        Arrays.sort(input);

        // 3. 贪心选择
        for (int i = 0; i < input.length; i++) {
            if (canSelect(input[i])) {
                // 做出贪心选择
                result += select(input[i]);
            }
        }

        return result;
    }

    private boolean canSelect(int item) {
        // 判断是否可以选择该项
        return true;
    }

    private int select(int item) {
        // 执行选择操作
        return item;
    }
}
```

## 2. 经典问题与解决方案

### 2.1 零钱兑换问题（硬币找零）

**问题描述**：给定不同面额的硬币和一个总金额，计算可以凑成总金额所需的最少硬币个数。

```java
public class CoinChange {
    /**
     * 贪心算法解决零钱兑换（仅适用于标准币制）
     * 时间复杂度：O(n log n)
     * 空间复杂度：O(1)
     */
    public int coinChangeGreedy(int[] coins, int amount) {
        // 按面额从大到小排序
        Arrays.sort(coins);
        reverse(coins);

        int count = 0;
        int i = 0;

        while (amount > 0 && i < coins.length) {
            if (amount >= coins[i]) {
                // 计算当前面额可以使用的最大数量
                int num = amount / coins[i];
                count += num;
                amount -= num * coins[i];
            }
            i++;
        }

        return amount == 0 ? count : -1;
    }

    private void reverse(int[] arr) {
        int left = 0, right = arr.length - 1;
        while (left < right) {
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        CoinChange solution = new CoinChange();
        int[] coins = {1, 5, 10, 25};
        int amount = 67;

        System.out.println("最少硬币数：" + solution.coinChangeGreedy(coins, amount));
        // 输出：最少硬币数：6 (25*2 + 10*1 + 5*1 + 1*2)
    }
}
```

### 2.2 活动选择问题

**问题描述**：有n个活动，每个活动都有开始时间和结束时间，选择最多的活动使得它们互不冲突。

```java
public class ActivitySelection {
    static class Activity {
        int start;
        int end;
        int index;

        Activity(int start, int end, int index) {
            this.start = start;
            this.end = end;
            this.index = index;
        }
    }

    /**
     * 活动选择问题 - 贪心算法
     * 策略：按结束时间排序，每次选择最早结束的活动
     * 时间复杂度：O(n log n)
     * 空间复杂度：O(n)
     */
    public List<Integer> activitySelection(int[] start, int[] end) {
        int n = start.length;
        List<Activity> activities = new ArrayList<>();

        // 创建活动列表
        for (int i = 0; i < n; i++) {
            activities.add(new Activity(start[i], end[i], i));
        }

        // 按结束时间排序
        activities.sort((a, b) -> a.end - b.end);

        List<Integer> selected = new ArrayList<>();
        int lastEndTime = 0;

        for (Activity activity : activities) {
            // 如果当前活动的开始时间不早于上一个活动的结束时间
            if (activity.start >= lastEndTime) {
                selected.add(activity.index);
                lastEndTime = activity.end;
            }
        }

        return selected;
    }

    public static void main(String[] args) {
        ActivitySelection solution = new ActivitySelection();

        int[] start = {1, 3, 0, 5, 8, 5};
        int[] end = {2, 4, 6, 7, 9, 9};

        List<Integer> result = solution.activitySelection(start, end);
        System.out.println("选中的活动索引：" + result);

        // 打印选中的活动详情
        System.out.println("选中的活动详情：");
        for (int i : result) {
            System.out.println("活动" + i + ": [" + start[i] + ", " + end[i] + "]");
        }
    }
}
```

### 2.3 霍夫曼编码

**问题描述**：给定一组字符及其频率，构造霍夫曼树实现最优编码。

```java
public class HuffmanCoding {
    static class Node implements Comparable<Node> {
        char ch;
        int freq;
        Node left, right;

        Node(char ch, int freq) {
            this.ch = ch;
            this.freq = freq;
        }

        Node(int freq, Node left, Node right) {
            this.ch = '\0'; // 内部节点
            this.freq = freq;
            this.left = left;
            this.right = right;
        }

        @Override
        public int compareTo(Node other) {
            return this.freq - other.freq;
        }

        boolean isLeaf() {
            return left == null && right == null;
        }
    }

    /**
     * 构建霍夫曼树
     * 时间复杂度：O(n log n)
     * 空间复杂度：O(n)
     */
    public Node buildHuffmanTree(char[] chars, int[] freq) {
        PriorityQueue<Node> pq = new PriorityQueue<>();

        // 将所有字符加入优先队列
        for (int i = 0; i < chars.length; i++) {
            pq.offer(new Node(chars[i], freq[i]));
        }

        // 构建霍夫曼树
        while (pq.size() > 1) {
            Node node1 = pq.poll();
            Node node2 = pq.poll();

            Node merged = new Node(node1.freq + node2.freq, node1, node2);
            pq.offer(merged);
        }

        return pq.poll();
    }

    /**
     * 生成霍夫曼编码
     */
    public Map<Character, String> generateCodes(Node root) {
        Map<Character, String> codes = new HashMap<>();
        if (root != null) {
            if (root.isLeaf()) {
                codes.put(root.ch, "0"); // 只有一个字符的特殊情况
            } else {
                generateCodes(root, "", codes);
            }
        }
        return codes;
    }

    private void generateCodes(Node node, String code, Map<Character, String> codes) {
        if (node.isLeaf()) {
            codes.put(node.ch, code);
        } else {
            generateCodes(node.left, code + "0", codes);
            generateCodes(node.right, code + "1", codes);
        }
    }

    public static void main(String[] args) {
        HuffmanCoding huffman = new HuffmanCoding();

        char[] chars = {'a', 'b', 'c', 'd', 'e', 'f'};
        int[] freq = {5, 9, 12, 13, 16, 45};

        Node root = huffman.buildHuffmanTree(chars, freq);
        Map<Character, String> codes = huffman.generateCodes(root);

        System.out.println("霍夫曼编码：");
        for (Map.Entry<Character, String> entry : codes.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }

        // 计算平均编码长度
        double avgLength = 0;
        int totalFreq = Arrays.stream(freq).sum();
        for (int i = 0; i < chars.length; i++) {
            avgLength += (freq[i] * codes.get(chars[i]).length()) / (double) totalFreq;
        }
        System.out.printf("平均编码长度：%.2f\n", avgLength);
    }
}
```

## 3. 高级应用案例

### 3.1 分数背包问题

**问题描述**：给定一个背包容量和若干物品（每个物品有重量和价值），物品可以分割，求背包能装入的最大价值。

```java
public class FractionalKnapsack {
    static class Item {
        int value;
        int weight;
        double ratio; // 价值密度

        Item(int value, int weight) {
            this.value = value;
            this.weight = weight;
            this.ratio = (double) value / weight;
        }
    }

    /**
     * 分数背包问题 - 贪心算法
     * 策略：按价值密度排序，优先选择价值密度高的物品
     * 时间复杂度：O(n log n)
     * 空间复杂度：O(n)
     */
    public double fractionalKnapsack(int[] values, int[] weights, int capacity) {
        int n = values.length;
        Item[] items = new Item[n];

        // 创建物品列表并计算价值密度
        for (int i = 0; i < n; i++) {
            items[i] = new Item(values[i], weights[i]);
        }

        // 按价值密度降序排序
        Arrays.sort(items, (a, b) -> Double.compare(b.ratio, a.ratio));

        double maxValue = 0;
        int currentCapacity = capacity;

        for (Item item : items) {
            if (currentCapacity >= item.weight) {
                // 完全装入该物品
                maxValue += item.value;
                currentCapacity -= item.weight;
            } else if (currentCapacity > 0) {
                // 部分装入该物品
                maxValue += item.value * ((double) currentCapacity / item.weight);
                break;
            }
        }

        return maxValue;
    }

    /**
     * 详细版本，显示装入过程
     */
    public void fractionalKnapsackDetailed(int[] values, int[] weights, int capacity) {
        int n = values.length;
        Item[] items = new Item[n];

        for (int i = 0; i < n; i++) {
            items[i] = new Item(values[i], weights[i]);
        }

        Arrays.sort(items, (a, b) -> Double.compare(b.ratio, a.ratio));

        System.out.println("物品按价值密度排序：");
        for (int i = 0; i < items.length; i++) {
            System.out.printf("物品%d: 价值=%d, 重量=%d, 密度=%.2f\n",
                i, items[i].value, items[i].weight, items[i].ratio);
        }

        double maxValue = 0;
        int currentCapacity = capacity;

        System.out.println("\n装入过程：");
        for (int i = 0; i < items.length; i++) {
            if (currentCapacity >= items[i].weight) {
                maxValue += items[i].value;
                currentCapacity -= items[i].weight;
                System.out.printf("完全装入物品%d，剩余容量=%d，当前价值=%.2f\n",
                    i, currentCapacity, maxValue);
            } else if (currentCapacity > 0) {
                double fraction = (double) currentCapacity / items[i].weight;
                maxValue += items[i].value * fraction;
                System.out.printf("部分装入物品%d（%.2f%%），最终价值=%.2f\n",
                    i, fraction * 100, maxValue);
                break;
            }
        }
    }

    public static void main(String[] args) {
        FractionalKnapsack solution = new FractionalKnapsack();

        int[] values = {60, 100, 120};
        int[] weights = {10, 20, 30};
        int capacity = 50;

        double result = solution.fractionalKnapsack(values, weights, capacity);
        System.out.println("最大价值：" + result);

        System.out.println("\n详细过程：");
        solution.fractionalKnapsackDetailed(values, weights, capacity);
    }
}
```

### 3.2 区间调度问题

**问题描述**：给定若干个区间，选择最多的区间使得它们互不重叠。

```java
public class IntervalScheduling {
    static class Interval {
        int start;
        int end;

        Interval(int start, int end) {
            this.start = start;
            this.end = end;
        }

        @Override
        public String toString() {
            return "[" + start + ", " + end + "]";
        }
    }

    /**
     * 区间调度问题 - 贪心算法
     * 策略：按结束时间排序，每次选择最早结束的区间
     * 时间复杂度：O(n log n)
     * 空间复杂度：O(1)
     */
    public int intervalScheduling(int[][] intervals) {
        if (intervals.length == 0) return 0;

        // 按结束时间排序
        Arrays.sort(intervals, (a, b) -> a[1] - b[1]);

        int count = 1;
        int end = intervals[0][1];

        for (int i = 1; i < intervals.length; i++) {
            // 如果当前区间的开始时间不早于上一个区间的结束时间
            if (intervals[i][0] >= end) {
                count++;
                end = intervals[i][1];
            }
        }

        return count;
    }

    /**
     * 返回具体的调度方案
     */
    public List<Interval> getSchedule(int[][] intervals) {
        List<Interval> result = new ArrayList<>();
        if (intervals.length == 0) return result;

        // 创建区间对象并排序
        List<Interval> list = new ArrayList<>();
        for (int[] interval : intervals) {
            list.add(new Interval(interval[0], interval[1]));
        }

        list.sort((a, b) -> a.end - b.end);

        result.add(list.get(0));
        int end = list.get(0).end;

        for (int i = 1; i < list.size(); i++) {
            if (list.get(i).start >= end) {
                result.add(list.get(i));
                end = list.get(i).end;
            }
        }

        return result;
    }

    /**
     * 区间调度的变种：最小会议室数量
     */
    public int minMeetingRooms(int[][] intervals) {
        if (intervals.length == 0) return 0;

        // 将开始和结束时间分别排序
        int[] starts = new int[intervals.length];
        int[] ends = new int[intervals.length];

        for (int i = 0; i < intervals.length; i++) {
            starts[i] = intervals[i][0];
            ends[i] = intervals[i][1];
        }

        Arrays.sort(starts);
        Arrays.sort(ends);

        int rooms = 0;
        int maxRooms = 0;
        int i = 0, j = 0;

        while (i < starts.length) {
            if (starts[i] < ends[j]) {
                rooms++;
                maxRooms = Math.max(maxRooms, rooms);
                i++;
            } else {
                rooms--;
                j++;
            }
        }

        return maxRooms;
    }

    public static void main(String[] args) {
        IntervalScheduling solution = new IntervalScheduling();

        int[][] intervals = {{1, 3}, {2, 4}, {3, 6}, {5, 7}, {8, 9}};

        System.out.println("最多可调度区间数：" + solution.intervalScheduling(intervals));

        List<Interval> schedule = solution.getSchedule(intervals);
        System.out.println("调度方案：" + schedule);

        System.out.println("需要的最少会议室数：" + solution.minMeetingRooms(intervals));
    }
}
```

## 4. 贪心算法正确性证明

### 4.1 证明技巧

贪心算法的正确性通常需要证明两个性质：

1. **贪心选择性质**：局部最优选择能导致全局最优解
2. **最优子结构性质**：原问题的最优解包含子问题的最优解

### 4.2 证明方法

#### 方法一：交换论证（Exchange Argument）

```java
/**
 * 活动选择问题的正确性证明示例
 * 证明思路：任何最优解都可以通过交换得到我们的贪心解
 */
public class ProofExample {
    /**
     * 证明贪心选择的正确性
     *
     * 定理：对于活动选择问题，按结束时间排序并选择最早结束的活动是最优的
     *
     * 证明：
     * 设A = {a1, a2, ..., ak}是某个最优解
     * 设G = {g1, g2, ..., gm}是贪心算法的解
     *
     * 如果A != G，考虑第一个不同的活动
     * 设gi是贪心算法选择的第i个活动，ai是最优解中对应位置的活动
     *
     * 由于贪心算法选择最早结束的活动，有：gi.end <= ai.end
     *
     * 我们可以将最优解中的ai替换为gi，得到新解A'
     * A'仍然是可行解（因为gi结束更早，不会与后续活动冲突）
     * |A'| = |A|，所以A'也是最优解
     *
     * 重复这个过程，最终可以得到贪心解G也是最优解
     */
    public void proofByExchange() {
        System.out.println("交换论证法证明贪心算法正确性：");
        System.out.println("1. 假设存在最优解A不同于贪心解G");
        System.out.println("2. 找到第一个不同的选择");
        System.out.println("3. 证明可以用贪心选择替换最优解中的选择");
        System.out.println("4. 替换后仍为最优解");
        System.out.println("5. 重复此过程直到得到贪心解");
    }
}
```

#### 方法二：归纳法证明

```java
/**
 * 归纳法证明贪心算法正确性
 */
public class InductionProof {
    /**
     * 证明分数背包问题贪心算法的正确性
     *
     * 基础情况：n=1时，只有一个物品，贪心算法显然正确
     *
     * 归纳假设：对于k个物品，贪心算法得到最优解
     *
     * 归纳步骤：对于k+1个物品，设贪心算法选择价值密度最高的物品x
     * - 如果x完全装入，剩余问题是k个物品的子问题，由归纳假设知贪心算法最优
     * - 如果x部分装入，则其他物品都不能装入，贪心选择显然最优
     */
    public void proofByInduction() {
        System.out.println("归纳法证明贪心算法正确性：");
        System.out.println("1. 基础情况：问题规模为1时算法正确");
        System.out.println("2. 归纳假设：规模为k时算法正确");
        System.out.println("3. 归纳步骤：证明规模为k+1时算法仍正确");
        System.out.println("4. 结合贪心选择性质完成证明");
    }
}
```

## 5. 贪心算法 vs 动态规划

### 5.1 对比分析

| 特征 | 贪心算法 | 动态规划 |
|------|---------|---------|
| 决策方式 | 局部最优 | 全局最优 |
| 回溯性 | 不回溯 | 可能需要回溯 |
| 子问题重叠 | 不一定 | 必须有 |
| 时间复杂度 | 通常较低 | 通常较高 |
| 空间复杂度 | 通常O(1) | 通常O(n)或更高 |
| 适用范围 | 特定问题 | 更广泛 |

### 5.2 选择策略

```java
public class AlgorithmChoice {
    /**
     * 何时选择贪心算法
     */
    public void whenToUseGreedy() {
        System.out.println("选择贪心算法的情况：");
        System.out.println("1. 问题具有贪心选择性质");
        System.out.println("2. 问题具有最优子结构");
        System.out.println("3. 局部最优能导致全局最优");
        System.out.println("4. 对效率要求较高");

        System.out.println("\n贪心算法适用的问题类型：");
        System.out.println("- 活动选择问题");
        System.out.println("- 分数背包问题");
        System.out.println("- 霍夫曼编码");
        System.out.println("- 最小生成树（Kruskal, Prim）");
        System.out.println("- 单源最短路径（Dijkstra）");
    }

    /**
     * 何时选择动态规划
     */
    public void whenToUseDP() {
        System.out.println("选择动态规划的情况：");
        System.out.println("1. 问题具有最优子结构");
        System.out.println("2. 子问题重叠");
        System.out.println("3. 贪心选择不能得到最优解");
        System.out.println("4. 需要考虑所有可能的选择");

        System.out.println("\n动态规划适用的问题类型：");
        System.out.println("- 0-1背包问题");
        System.out.println("- 最长公共子序列");
        System.out.println("- 编辑距离");
        System.out.println("- 硬币找零（非标准币制）");
        System.out.println("- 股票买卖问题");
    }

    /**
     * 对比示例：背包问题
     */
    public void knapsackComparison() {
        System.out.println("背包问题对比：");
        System.out.println("\n分数背包（可分割）：");
        System.out.println("- 贪心算法：按价值密度排序，总是选择密度最高的");
        System.out.println("- 时间复杂度：O(n log n)");
        System.out.println("- 能得到最优解");

        System.out.println("\n0-1背包（不可分割）：");
        System.out.println("- 动态规划：考虑每个物品选或不选的所有情况");
        System.out.println("- 时间复杂度：O(nW)");
        System.out.println("- 贪心算法不能保证最优解");
    }
}
```

## 6. 实际应用场景

### 6.1 任务调度系统

```java
public class TaskScheduler {
    static class Task {
        String name;
        int priority;
        int duration;
        int deadline;

        Task(String name, int priority, int duration, int deadline) {
            this.name = name;
            this.priority = priority;
            this.duration = duration;
            this.deadline = deadline;
        }
    }

    /**
     * 基于优先级的任务调度
     * 贪心策略：优先执行高优先级任务
     */
    public List<Task> scheduleBypriority(List<Task> tasks) {
        List<Task> schedule = new ArrayList<>(tasks);

        // 按优先级降序排序
        schedule.sort((a, b) -> b.priority - a.priority);

        return schedule;
    }

    /**
     * 基于截止时间的任务调度（Earliest Deadline First）
     * 贪心策略：优先执行截止时间最早的任务
     */
    public List<Task> scheduleByDeadline(List<Task> tasks) {
        List<Task> schedule = new ArrayList<>(tasks);

        // 按截止时间升序排序
        schedule.sort((a, b) -> a.deadline - b.deadline);

        return schedule;
    }

    /**
     * 最短处理时间优先（Shortest Processing Time First）
     * 贪心策略：优先执行处理时间最短的任务
     */
    public List<Task> scheduleBySPT(List<Task> tasks) {
        List<Task> schedule = new ArrayList<>(tasks);

        // 按处理时间升序排序
        schedule.sort((a, b) -> a.duration - b.duration);

        return schedule;
    }

    public static void main(String[] args) {
        TaskScheduler scheduler = new TaskScheduler();

        List<Task> tasks = Arrays.asList(
            new Task("任务A", 3, 4, 10),
            new Task("任务B", 1, 2, 6),
            new Task("任务C", 2, 6, 8),
            new Task("任务D", 3, 3, 12)
        );

        System.out.println("原始任务列表：");
        tasks.forEach(task -> System.out.println(task.name + " - 优先级:" +
            task.priority + ", 时长:" + task.duration + ", 截止:" + task.deadline));

        System.out.println("\n按优先级调度：");
        scheduler.scheduleBypriority(tasks).forEach(task -> System.out.print(task.name + " "));

        System.out.println("\n\n按截止时间调度：");
        scheduler.scheduleByDeadline(tasks).forEach(task -> System.out.print(task.name + " "));

        System.out.println("\n\n按处理时间调度：");
        scheduler.scheduleBySPT(tasks).forEach(task -> System.out.print(task.name + " "));
    }
}
```

### 6.2 网络路由算法

```java
public class NetworkRouting {
    static class Edge {
        int to;
        int weight;

        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }

    /**
     * Dijkstra算法 - 单源最短路径
     * 贪心策略：每次选择距离最近的未访问节点
     * 时间复杂度：O((V + E) log V)
     */
    public int[] dijkstra(List<List<Edge>> graph, int start) {
        int n = graph.size();
        int[] dist = new int[n];
        boolean[] visited = new boolean[n];

        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[start] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
        pq.offer(new int[]{start, 0});

        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int u = current[0];

            if (visited[u]) continue;
            visited[u] = true;

            // 更新邻接节点的距离
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                int weight = edge.weight;

                if (!visited[v] && dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    pq.offer(new int[]{v, dist[v]});
                }
            }
        }

        return dist;
    }

    /**
     * 构建路由表
     */
    public void buildRoutingTable(List<List<Edge>> graph, int router) {
        int[] distances = dijkstra(graph, router);

        System.out.println("路由器 " + router + " 的路由表：");
        System.out.println("目标\t距离\t下一跳");
        System.out.println("--------------------");

        for (int i = 0; i < distances.length; i++) {
            if (i != router) {
                String distance = distances[i] == Integer.MAX_VALUE ? "∞" : String.valueOf(distances[i]);
                System.out.println(i + "\t" + distance + "\t" + getNextHop(graph, router, i));
            }
        }
    }

    private int getNextHop(List<List<Edge>> graph, int start, int target) {
        // 简化版本，实际实现需要记录路径
        for (Edge edge : graph.get(start)) {
            if (edge.to == target) {
                return target;
            }
        }
        return -1; // 需要更复杂的路径重构
    }

    public static void main(String[] args) {
        NetworkRouting routing = new NetworkRouting();

        // 构建网络图
        int n = 5;
        List<List<Edge>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }

        // 添加边（双向）
        addBidirectionalEdge(graph, 0, 1, 4);
        addBidirectionalEdge(graph, 0, 2, 2);
        addBidirectionalEdge(graph, 1, 2, 1);
        addBidirectionalEdge(graph, 1, 3, 5);
        addBidirectionalEdge(graph, 2, 3, 8);
        addBidirectionalEdge(graph, 2, 4, 10);
        addBidirectionalEdge(graph, 3, 4, 2);

        // 从节点0开始的最短路径
        int[] distances = routing.dijkstra(graph, 0);
        System.out.println("从节点0到各节点的最短距离：");
        for (int i = 0; i < distances.length; i++) {
            System.out.println("到节点" + i + ": " + distances[i]);
        }
    }

    private static void addBidirectionalEdge(List<List<Edge>> graph, int u, int v, int weight) {
        graph.get(u).add(new Edge(v, weight));
        graph.get(v).add(new Edge(u, weight));
    }
}
```

## 7. 常见贪心模式与实现策略

### 7.1 排序贪心模式

```java
public class SortingGreedyPatterns {
    /**
     * 模式1：按结束时间排序
     * 适用于：活动选择、区间调度等
     */
    public int maxNonOverlapIntervals(int[][] intervals) {
        if (intervals.length == 0) return 0;

        Arrays.sort(intervals, (a, b) -> a[1] - b[1]); // 按结束时间排序

        int count = 1;
        int end = intervals[0][1];

        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] >= end) {
                count++;
                end = intervals[i][1];
            }
        }

        return count;
    }

    /**
     * 模式2：按比值排序
     * 适用于：分数背包、性价比优化等
     */
    public double maxValueWithRatio(int[] values, int[] weights, int capacity) {
        int n = values.length;
        Integer[] indices = new Integer[n];
        for (int i = 0; i < n; i++) {
            indices[i] = i;
        }

        // 按价值密度降序排序
        Arrays.sort(indices, (i, j) ->
            Double.compare((double) values[j] / weights[j], (double) values[i] / weights[i]));

        double maxValue = 0;
        int remainingCapacity = capacity;

        for (int i : indices) {
            if (remainingCapacity >= weights[i]) {
                maxValue += values[i];
                remainingCapacity -= weights[i];
            } else if (remainingCapacity > 0) {
                maxValue += values[i] * ((double) remainingCapacity / weights[i]);
                break;
            }
        }

        return maxValue;
    }

    /**
     * 模式3：按差值排序
     * 适用于：任务分配、负载均衡等
     */
    public int assignTasks(int[] tasks, int[] workers) {
        Arrays.sort(tasks);
        Arrays.sort(workers);

        int assigned = 0;
        int i = 0, j = 0;

        while (i < tasks.length && j < workers.length) {
            if (workers[j] >= tasks[i]) {
                assigned++;
                i++;
            }
            j++;
        }

        return assigned;
    }
}
```

### 7.2 优先队列贪心模式

```java
public class PriorityQueueGreedyPatterns {
    /**
     * 模式1：最小堆贪心
     * 适用于：合并成本最小化、霍夫曼编码等
     */
    public int minCostToMergeStones(int[] stones) {
        int n = stones.length;
        if (n < 2) return 0;

        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int stone : stones) {
            pq.offer(stone);
        }

        int totalCost = 0;
        while (pq.size() > 1) {
            int first = pq.poll();
            int second = pq.poll();
            int cost = first + second;
            totalCost += cost;
            pq.offer(cost);
        }

        return totalCost;
    }

    /**
     * 模式2：最大堆贪心
     * 适用于：最大化收益、资源分配等
     */
    public int maxProfitJobScheduling(int[] difficulty, int[] profit, int[] worker) {
        int n = difficulty.length;
        int m = worker.length;

        // 创建工作列表并按难度排序
        int[][] jobs = new int[n][2];
        for (int i = 0; i < n; i++) {
            jobs[i] = new int[]{difficulty[i], profit[i]};
        }
        Arrays.sort(jobs, (a, b) -> a[0] - b[0]);

        // 排序工人
        Arrays.sort(worker);

        int totalProfit = 0;
        int maxProfit = 0;
        int i = 0;

        for (int w : worker) {
            // 更新当前工人能做的最大收益工作
            while (i < n && jobs[i][0] <= w) {
                maxProfit = Math.max(maxProfit, jobs[i][1]);
                i++;
            }
            totalProfit += maxProfit;
        }

        return totalProfit;
    }

    /**
     * 模式3：双端队列贪心
     * 适用于：滑动窗口最优化等
     */
    public int[] maxSlidingWindow(int[] nums, int k) {
        Deque<Integer> deque = new ArrayDeque<>();
        int[] result = new int[nums.length - k + 1];

        for (int i = 0; i < nums.length; i++) {
            // 移除窗口外的元素
            while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
                deque.pollFirst();
            }

            // 维护递减队列
            while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
                deque.pollLast();
            }

            deque.offerLast(i);

            // 记录窗口最大值
            if (i >= k - 1) {
                result[i - k + 1] = nums[deque.peekFirst()];
            }
        }

        return result;
    }
}
```

### 7.3 状态机贪心模式

```java
public class StateMachineGreedyPatterns {
    /**
     * 模式1：股票交易（状态机+贪心）
     * 状态：持有股票、不持有股票
     */
    public int maxProfit(int[] prices) {
        if (prices.length < 2) return 0;

        int hold = -prices[0];  // 持有股票的最大收益
        int sold = 0;           // 不持有股票的最大收益

        for (int i = 1; i < prices.length; i++) {
            int prevHold = hold;
            int prevSold = sold;

            // 贪心选择：在每个状态下选择最优操作
            hold = Math.max(prevHold, prevSold - prices[i]); // 继续持有 vs 买入
            sold = Math.max(prevSold, prevHold + prices[i]);  // 继续不持有 vs 卖出
        }

        return sold;
    }

    /**
     * 模式2：跳跃游戏（状态机+贪心）
     * 状态：当前位置能到达的最远距离
     */
    public boolean canJump(int[] nums) {
        int maxReach = 0;

        for (int i = 0; i < nums.length; i++) {
            if (i > maxReach) return false;

            // 贪心选择：更新能到达的最远位置
            maxReach = Math.max(maxReach, i + nums[i]);

            if (maxReach >= nums.length - 1) return true;
        }

        return true;
    }

    /**
     * 最少跳跃次数
     */
    public int jump(int[] nums) {
        if (nums.length <= 1) return 0;

        int jumps = 0;
        int currentEnd = 0;
        int farthest = 0;

        for (int i = 0; i < nums.length - 1; i++) {
            farthest = Math.max(farthest, i + nums[i]);

            // 到达当前跳跃的边界
            if (i == currentEnd) {
                jumps++;
                currentEnd = farthest;
            }
        }

        return jumps;
    }
}
```

## 8. 实践建议与注意事项

### 8.1 设计贪心算法的步骤

1. **问题分析**：确定问题是否具有贪心选择性质
2. **策略设计**：设计贪心选择策略
3. **正确性证明**：证明贪心选择能导致最优解
4. **算法实现**：实现并优化算法
5. **测试验证**：通过测试用例验证正确性

### 8.2 常见陷阱

```java
public class CommonTraps {
    /**
     * 陷阱1：贪心策略选择错误
     * 错误示例：0-1背包问题用贪心算法
     */
    public int wrongKnapsack01(int[] values, int[] weights, int capacity) {
        // 错误：按价值密度贪心选择完整物品
        // 这种方法不能保证得到最优解
        return -1; // 应该用动态规划
    }

    /**
     * 陷阱2：没有考虑所有约束条件
     * 正确的区间调度需要考虑开始时间约束
     */
    public int correctIntervalScheduling(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> a[1] - b[1]); // 按结束时间排序

        int count = 1;
        int lastEnd = intervals[0][1];

        for (int i = 1; i < intervals.length; i++) {
            // 正确：检查开始时间是否不早于上一个活动的结束时间
            if (intervals[i][0] >= lastEnd) {
                count++;
                lastEnd = intervals[i][1];
            }
        }

        return count;
    }

    /**
     * 陷阱3：边界条件处理不当
     */
    public List<Integer> robustGreedy(int[] input) {
        List<Integer> result = new ArrayList<>();

        // 正确：处理空输入
        if (input == null || input.length == 0) {
            return result;
        }

        // 正确：处理单元素情况
        if (input.length == 1) {
            result.add(input[0]);
            return result;
        }

        // 主要逻辑
        Arrays.sort(input);
        for (int val : input) {
            if (isValid(val)) {
                result.add(val);
            }
        }

        return result;
    }

    private boolean isValid(int val) {
        return val > 0;
    }
}
```

### 8.3 性能优化技巧

```java
public class OptimizationTips {
    /**
     * 技巧1：选择合适的数据结构
     */
    public class EfficientGreedy {
        // 使用优先队列优化选择过程
        public int optimizedSelection(int[] items) {
            PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());

            for (int item : items) {
                pq.offer(item);
            }

            int result = 0;
            while (!pq.isEmpty() && canSelect()) {
                result += pq.poll();
            }

            return result;
        }

        private boolean canSelect() {
            return true; // 简化的选择条件
        }
    }

    /**
     * 技巧2：避免不必要的排序
     */
    public int partialSortOptimization(int[] arr, int k) {
        // 使用快速选择找到第k大元素，避免完全排序
        return quickSelect(arr, 0, arr.length - 1, k);
    }

    private int quickSelect(int[] arr, int left, int right, int k) {
        if (left == right) return arr[left];

        int pivotIndex = partition(arr, left, right);

        if (k == pivotIndex) {
            return arr[k];
        } else if (k < pivotIndex) {
            return quickSelect(arr, left, pivotIndex - 1, k);
        } else {
            return quickSelect(arr, pivotIndex + 1, right, k);
        }
    }

    private int partition(int[] arr, int left, int right) {
        int pivot = arr[right];
        int i = left;

        for (int j = left; j < right; j++) {
            if (arr[j] >= pivot) {
                swap(arr, i, j);
                i++;
            }
        }

        swap(arr, i, right);
        return i;
    }

    private void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }

    /**
     * 技巧3：空间优化
     */
    public int spaceOptimizedGreedy(int[] input) {
        // 原地操作，减少额外空间使用
        int result = 0;
        int current = 0;

        for (int val : input) {
            if (val > current) {
                result += val - current;
                current = val;
            }
        }

        return result;
    }
}
```

## 结语

贪心算法以其简洁的思想和高效的执行成为算法设计中的重要工具。通过本文的深入探讨，我们了解了贪心算法的核心概念、实现技巧、正确性证明方法以及实际应用场景。

**关键要点回顾**：

1. **核心思想**：在每一步都做出当前最优选择，通过局部最优达到全局最优
2. **适用条件**：问题必须具有贪心选择性质和最优子结构
3. **常见模式**：排序贪心、优先队列贪心、状态机贪心等
4. **证明方法**：交换论证法、归纳法等
5. **实际应用**：任务调度、网络路由、资源分配等领域

**实践建议**：

- 在应用贪心算法前，务必验证问题是否满足贪心选择性质
- 选择合适的贪心策略是成功的关键
- 注意边界条件和特殊情况的处理
- 合理选择数据结构以优化算法性能

贪心算法虽然不是万能的，但在适合的问题域中，它能够以优雅简洁的方式解决复杂问题。掌握贪心算法的精髓，不仅能够提升我们的算法设计能力，更能培养我们在面对复杂问题时"化繁为简"的智慧。

希望本文能够帮助读者深入理解贪心算法，在实际编程和问题解决中灵活运用这一强大的算法思想。记住，最好的算法往往是最简单的算法，而贪心算法正是这种简洁智慧的完美体现。