---
title: "数据结构入门教程：二分查找算法详解与Java实现"
date: 2025-01-28T15:30:00+08:00
draft: false
tags: ["数据结构", "二分查找", "Java", "算法"]
categories: ["编程教程"]
series: ["数据结构入门教程"]
description: "全面掌握二分查找算法，包含基础二分查找、变种查找、二分答案等高级应用，配有详细图解和实战案例"
---

## 🎯 引言：分而治之的查找艺术

想象一下在字典中查找单词的过程：你不会从第一页开始逐页翻阅，而是先翻到中间，根据字母顺序决定往前还是往后，然后继续对剩余部分重复这个过程。这就是**二分查找**的基本思想！

**二分查找（Binary Search）**是一种在有序数组中查找特定元素的高效算法。它每次将搜索范围缩小一半，时间复杂度仅为 O(log n)，是查找算法中的经典之作。

#### 流程图表


**关系流向：**
```
A["有序数组 [1,3,5,7,9,11,13,15]"] → B["查找目标: 7"]
B → C["中间位置: arr[3] = 7"]
C → D["比较结果"]
D → E["找到目标!"]
```

## 🔍 二分查找基础实现

### 经典二分查找

```java
/**
 * 二分查找基础实现
 * 时间复杂度：O(log n)
 * 空间复杂度：O(1)
 */
public class BinarySearch {

    /**
     * 基础二分查找（迭代版本）
     * @param arr 有序数组
     * @param target 目标值
     * @return 目标值的索引，未找到返回-1
     */
    public static int binarySearchIterative(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        System.out.println("查找目标: " + target);
        System.out.println("数组: " + Arrays.toString(arr));

        while (left <= right) {
            int mid = left + (right - left) / 2; // 防止溢出

            System.out.printf("搜索范围: [%d, %d], 中间位置: %d, 中间值: %d%n",
                            left, right, mid, arr[mid]);

            if (arr[mid] == target) {
                System.out.println("找到目标，位置: " + mid);
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
                System.out.println("目标在右半部分");
            } else {
                right = mid - 1;
                System.out.println("目标在左半部分");
            }
        }

        System.out.println("未找到目标");
        return -1;
    }

    /**
     * 递归版本的二分查找
     * @param arr 有序数组
     * @param target 目标值
     * @param left 左边界
     * @param right 右边界
     * @return 目标值的索引，未找到返回-1
     */
    public static int binarySearchRecursive(int[] arr, int target, int left, int right) {
        if (left > right) {
            return -1; // 未找到
        }

        int mid = left + (right - left) / 2;
        System.out.printf("递归查找: [%d, %d], 中间位置: %d, 中间值: %d%n",
                        left, right, mid, arr[mid]);

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            return binarySearchRecursive(arr, target, mid + 1, right);
        } else {
            return binarySearchRecursive(arr, target, left, mid - 1);
        }
    }

    /**
     * 二分查找的边界处理模板
     * 这是最不容易出错的写法
     */
    public static int binarySearchTemplate(int[] arr, int target) {
        int left = 0;
        int right = arr.length; // 注意：这里是length，不是length-1

        while (left < right) { // 注意：这里是<，不是<=
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid; // 注意：这里是mid，不是mid-1
            }
        }

        return -1;
    }
}
```

### 二分查找的变种

```java
/**
 * 二分查找的各种变种
 * 处理重复元素和边界情况
 */
public class BinarySearchVariants {

    /**
     * 查找第一个等于目标值的位置
     * 适用于有重复元素的有序数组
     */
    public static int findFirst(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        int result = -1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                result = mid;
                right = mid - 1; // 继续在左半部分查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return result;
    }

    /**
     * 查找最后一个等于目标值的位置
     */
    public static int findLast(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        int result = -1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                result = mid;
                left = mid + 1; // 继续在右半部分查找
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return result;
    }

    /**
     * 查找第一个大于等于目标值的位置（下界）
     */
    public static int lowerBound(int[] arr, int target) {
        int left = 0;
        int right = arr.length;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    /**
     * 查找第一个大于目标值的位置（上界）
     */
    public static int upperBound(int[] arr, int target) {
        int left = 0;
        int right = arr.length;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    /**
     * 查找目标值的范围（第一个和最后一个位置）
     */
    public static int[] searchRange(int[] arr, int target) {
        int first = findFirst(arr, target);
        if (first == -1) {
            return new int[]{-1, -1};
        }

        int last = findLast(arr, target);
        return new int[]{first, last};
    }

    /**
     * 查找插入位置
     * 在有序数组中找到插入target后仍保持有序的位置
     */
    public static int searchInsert(int[] arr, int target) {
        return lowerBound(arr, target);
    }

    /**
     * 在旋转排序数组中查找元素
     */
    public static int searchInRotatedArray(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                return mid;
            }

            // 判断哪一部分是有序的
            if (nums[left] <= nums[mid]) {
                // 左半部分有序
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                // 右半部分有序
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }

        return -1;
    }

    /**
     * 查找峰值元素
     * 峰值元素是指其值大于左右相邻值的元素
     */
    public static int findPeakElement(int[] nums) {
        int left = 0;
        int right = nums.length - 1;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (nums[mid] > nums[mid + 1]) {
                // 峰值在左侧（包括mid）
                right = mid;
            } else {
                // 峰值在右侧
                left = mid + 1;
            }
        }

        return left;
    }
}
```

## 🎮 二分答案

二分答案是二分查找的高级应用，用于求解最优化问题。

### 二分答案模板

```java
/**
 * 二分答案算法实现
 * 用于求解最优化问题
 */
public class BinaryAnswer {

    /**
     * 二分答案通用模板
     * @param left 答案的最小可能值
     * @param right 答案的最大可能值
     * @param checker 检查函数，判断某个值是否满足条件
     * @param findMinimum 是否查找最小值（true）还是最大值（false）
     * @return 最优答案
     */
    public static int binaryAnswer(int left, int right,
                                  IntPredicate checker, boolean findMinimum) {
        while (left < right) {
            int mid = left + (right - left) / 2;

            if (findMinimum) {
                // 查找最小的满足条件的值
                if (checker.test(mid)) {
                    right = mid;
                } else {
                    left = mid + 1;
                }
            } else {
                // 查找最大的满足条件的值
                if (checker.test(mid)) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }
        }

        return findMinimum ? left : left - 1;
    }

    /**
     * 案例1：分割数组的最大值
     * 给定一个数组和分割数m，将数组分成m个非空连续子数组，
     * 使得这m个子数组各自和的最大值最小
     */
    public static int splitArray(int[] nums, int m) {
        int left = Arrays.stream(nums).max().orElse(0); // 最小可能的最大值
        int right = Arrays.stream(nums).sum(); // 最大可能的最大值

        System.out.println("分割数组问题:");
        System.out.println("数组: " + Arrays.toString(nums));
        System.out.println("分割数: " + m);
        System.out.println("搜索范围: [" + left + ", " + right + "]");

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (canSplit(nums, m, mid)) {
                System.out.println("最大和 " + mid + " 可以分割");
                right = mid;
            } else {
                System.out.println("最大和 " + mid + " 无法分割");
                left = mid + 1;
            }
        }

        System.out.println("最小的最大子数组和: " + left);
        return left;
    }

    /**
     * 检查是否可以将数组分成m个子数组，且每个子数组和不超过maxSum
     */
    private static boolean canSplit(int[] nums, int m, int maxSum) {
        int count = 1; // 至少需要一个子数组
        int currentSum = 0;

        for (int num : nums) {
            if (currentSum + num > maxSum) {
                count++;
                currentSum = num;
                if (count > m) {
                    return false;
                }
            } else {
                currentSum += num;
            }
        }

        return true;
    }

    /**
     * 案例2：第K小的距离对
     * 给定整数数组，返回所有数对的第K小距离
     */
    public static int smallestDistancePair(int[] nums, int k) {
        Arrays.sort(nums);

        int left = 0;
        int right = nums[nums.length - 1] - nums[0];

        System.out.println("第K小距离对问题:");
        System.out.println("数组: " + Arrays.toString(nums));
        System.out.println("K: " + k);

        while (left < right) {
            int mid = left + (right - left) / 2;
            int count = countPairsWithDistanceLEQ(nums, mid);

            System.out.println("距离 " + mid + " 的对数: " + count);

            if (count < k) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    /**
     * 计算距离小于等于target的数对个数
     */
    private static int countPairsWithDistanceLEQ(int[] nums, int target) {
        int count = 0;
        int left = 0;

        for (int right = 1; right < nums.length; right++) {
            while (nums[right] - nums[left] > target) {
                left++;
            }
            count += right - left;
        }

        return count;
    }

    /**
     * 案例3：爱吃香蕉的珂珂
     * 珂珂有H小时吃香蕉，找到她可以在H小时内吃掉所有香蕉的最小速度
     */
    public static int minEatingSpeed(int[] piles, int h) {
        int left = 1;
        int right = Arrays.stream(piles).max().orElse(1);

        System.out.println("爱吃香蕉的珂珂问题:");
        System.out.println("香蕉堆: " + Arrays.toString(piles));
        System.out.println("时间限制: " + h + " 小时");

        while (left < right) {
            int mid = left + (right - left) / 2;
            int timeNeeded = calculateTimeNeeded(piles, mid);

            System.out.println("速度 " + mid + " 需要时间: " + timeNeeded);

            if (timeNeeded <= h) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }

        System.out.println("最小吃香蕉速度: " + left);
        return left;
    }

    /**
     * 计算以指定速度吃香蕉需要的时间
     */
    private static int calculateTimeNeeded(int[] piles, int speed) {
        int time = 0;
        for (int pile : piles) {
            time += (pile + speed - 1) / speed; // 向上取整
        }
        return time;
    }
}
```

## 🔍 二分查找在数据结构中的应用

### 二分查找树（Binary Search Tree）

```java
/**
 * 二分查找树实现
 * 结合二分查找思想的树结构
 */
public class BinarySearchTree {
    private TreeNode root;

    private static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;

        TreeNode(int val) {
            this.val = val;
        }
    }

    /**
     * 插入节点
     */
    public void insert(int val) {
        root = insertHelper(root, val);
    }

    private TreeNode insertHelper(TreeNode node, int val) {
        if (node == null) {
            return new TreeNode(val);
        }

        if (val < node.val) {
            node.left = insertHelper(node.left, val);
        } else if (val > node.val) {
            node.right = insertHelper(node.right, val);
        }

        return node;
    }

    /**
     * 查找节点（二分查找思想）
     */
    public boolean search(int val) {
        return searchHelper(root, val);
    }

    private boolean searchHelper(TreeNode node, int val) {
        if (node == null) {
            return false;
        }

        if (val == node.val) {
            return true;
        } else if (val < node.val) {
            return searchHelper(node.left, val);
        } else {
            return searchHelper(node.right, val);
        }
    }

    /**
     * 找到第K小的元素
     */
    public int kthSmallest(int k) {
        List<Integer> result = new ArrayList<>();
        inorderTraversal(root, result);
        return result.get(k - 1);
    }

    private void inorderTraversal(TreeNode node, List<Integer> result) {
        if (node == null) return;

        inorderTraversal(node.left, result);
        result.add(node.val);
        inorderTraversal(node.right, result);
    }

    /**
     * 验证是否为有效的二分查找树
     */
    public boolean isValidBST() {
        return isValidBSTHelper(root, Long.MIN_VALUE, Long.MAX_VALUE);
    }

    private boolean isValidBSTHelper(TreeNode node, long minVal, long maxVal) {
        if (node == null) return true;

        if (node.val <= minVal || node.val >= maxVal) {
            return false;
        }

        return isValidBSTHelper(node.left, minVal, node.val) &&
               isValidBSTHelper(node.right, node.val, maxVal);
    }
}
```

### 有序集合的二分查找

```java
/**
 * 基于有序数组的集合实现
 * 使用二分查找优化操作
 */
public class OrderedSet {
    private List<Integer> data;

    public OrderedSet() {
        this.data = new ArrayList<>();
    }

    /**
     * 添加元素（保持有序）
     */
    public void add(int val) {
        int pos = BinarySearchVariants.lowerBound(
            data.stream().mapToInt(i -> i).toArray(), val);

        if (pos < data.size() && data.get(pos) == val) {
            return; // 元素已存在
        }

        data.add(pos, val);
    }

    /**
     * 删除元素
     */
    public boolean remove(int val) {
        int pos = BinarySearch.binarySearchIterative(
            data.stream().mapToInt(i -> i).toArray(), val);

        if (pos == -1) {
            return false;
        }

        data.remove(pos);
        return true;
    }

    /**
     * 查找元素
     */
    public boolean contains(int val) {
        return BinarySearch.binarySearchIterative(
            data.stream().mapToInt(i -> i).toArray(), val) != -1;
    }

    /**
     * 获取小于val的最大元素
     */
    public Integer lower(int val) {
        int pos = BinarySearchVariants.lowerBound(
            data.stream().mapToInt(i -> i).toArray(), val);

        return pos > 0 ? data.get(pos - 1) : null;
    }

    /**
     * 获取大于val的最小元素
     */
    public Integer higher(int val) {
        int pos = BinarySearchVariants.upperBound(
            data.stream().mapToInt(i -> i).toArray(), val);

        return pos < data.size() ? data.get(pos) : null;
    }

    /**
     * 获取范围内的元素
     */
    public List<Integer> range(int fromVal, int toVal) {
        int[] arr = data.stream().mapToInt(i -> i).toArray();
        int startPos = BinarySearchVariants.lowerBound(arr, fromVal);
        int endPos = BinarySearchVariants.upperBound(arr, toVal);

        return data.subList(startPos, endPos);
    }

    public void display() {
        System.out.println("OrderedSet: " + data);
    }
}
```

## 🎯 二分查找的优化技巧

### 缓存友好的二分查找

```java
/**
 * 缓存友好的二分查找优化
 */
public class CacheFriendlyBinarySearch {

    /**
     * 分块二分查找
     * 先用二分查找定位块，再在块内线性搜索
     */
    public static int blockBinarySearch(int[] arr, int target) {
        int blockSize = (int) Math.sqrt(arr.length);
        int numBlocks = (arr.length + blockSize - 1) / blockSize;

        // 二分查找定位块
        int left = 0, right = numBlocks - 1;
        int targetBlock = -1;

        while (left <= right) {
            int mid = left + (right - left) / 2;
            int blockStart = mid * blockSize;
            int blockEnd = Math.min(blockStart + blockSize - 1, arr.length - 1);

            if (arr[blockStart] <= target && target <= arr[blockEnd]) {
                targetBlock = mid;
                break;
            } else if (target < arr[blockStart]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }

        if (targetBlock == -1) return -1;

        // 在目标块内线性搜索
        int blockStart = targetBlock * blockSize;
        int blockEnd = Math.min(blockStart + blockSize, arr.length);

        for (int i = blockStart; i < blockEnd; i++) {
            if (arr[i] == target) {
                return i;
            }
        }

        return -1;
    }

    /**
     * 插值搜索（适用于均匀分布的数据）
     * 基于二分查找的改进
     */
    public static int interpolationSearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right && target >= arr[left] && target <= arr[right]) {
            if (left == right) {
                return arr[left] == target ? left : -1;
            }

            // 使用插值公式计算位置
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
     * 指数搜索（适用于无界数组）
     */
    public static int exponentialSearch(int[] arr, int target) {
        if (arr[0] == target) {
            return 0;
        }

        // 找到搜索范围
        int bound = 1;
        while (bound < arr.length && arr[bound] < target) {
            bound *= 2;
        }

        // 在范围内进行二分查找
        return BinarySearch.binarySearchIterative(
            Arrays.copyOfRange(arr, bound / 2, Math.min(bound + 1, arr.length)),
            target
        ) + bound / 2;
    }
}
```

## 🧪 完整测试示例

```java
/**
 * 二分查找算法综合测试
 */
public class BinarySearchTest {
    public static void main(String[] args) {
        System.out.println("=== 二分查找算法综合测试 ===");

        testBasicBinarySearch();
        testBinarySearchVariants();
        testBinaryAnswer();
        testBinarySearchTree();
        testOrderedSet();
        testOptimizations();
    }

    private static void testBasicBinarySearch() {
        System.out.println("\n1. 基础二分查找测试:");

        int[] arr = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
        int target = 7;

        System.out.println("迭代版本:");
        int result1 = BinarySearch.binarySearchIterative(arr, target);

        System.out.println("\n递归版本:");
        int result2 = BinarySearch.binarySearchRecursive(arr, target, 0, arr.length - 1);

        System.out.println("结果: " + result1 + ", " + result2);
    }

    private static void testBinarySearchVariants() {
        System.out.println("\n2. 二分查找变种测试:");

        int[] arr = {1, 2, 2, 2, 3, 4, 4, 5, 5, 5, 6};
        int target = 2;

        System.out.println("数组: " + Arrays.toString(arr));
        System.out.println("目标: " + target);

        int first = BinarySearchVariants.findFirst(arr, target);
        int last = BinarySearchVariants.findLast(arr, target);
        int lower = BinarySearchVariants.lowerBound(arr, target);
        int upper = BinarySearchVariants.upperBound(arr, target);

        System.out.println("第一个位置: " + first);
        System.out.println("最后位置: " + last);
        System.out.println("下界: " + lower);
        System.out.println("上界: " + upper);

        // 测试旋转数组
        int[] rotated = {4, 5, 6, 7, 0, 1, 2};
        int rotatedResult = BinarySearchVariants.searchInRotatedArray(rotated, 0);
        System.out.println("旋转数组中查找0: " + rotatedResult);
    }

    private static void testBinaryAnswer() {
        System.out.println("\n3. 二分答案测试:");

        // 分割数组测试
        int[] nums = {7, 2, 5, 10, 8};
        int m = 2;
        int result = BinaryAnswer.splitArray(nums, m);

        // 香蕉问题测试
        int[] piles = {3, 6, 7, 11};
        int h = 8;
        int speed = BinaryAnswer.minEatingSpeed(piles, h);
    }

    private static void testBinarySearchTree() {
        System.out.println("\n4. 二分查找树测试:");

        BinarySearchTree bst = new BinarySearchTree();
        int[] values = {5, 3, 7, 2, 4, 6, 8};

        for (int val : values) {
            bst.insert(val);
        }

        System.out.println("查找5: " + bst.search(5));
        System.out.println("查找10: " + bst.search(10));
        System.out.println("第3小元素: " + bst.kthSmallest(3));
        System.out.println("是否为有效BST: " + bst.isValidBST());
    }

    private static void testOrderedSet() {
        System.out.println("\n5. 有序集合测试:");

        OrderedSet set = new OrderedSet();
        int[] values = {5, 2, 8, 1, 9, 3};

        for (int val : values) {
            set.add(val);
        }

        set.display();
        System.out.println("包含5: " + set.contains(5));
        System.out.println("小于5的最大元素: " + set.lower(5));
        System.out.println("大于5的最小元素: " + set.higher(5));
        System.out.println("范围[3,7]: " + set.range(3, 7));
    }

    private static void testOptimizations() {
        System.out.println("\n6. 优化技术测试:");

        int[] largeArr = new int[1000000];
        for (int i = 0; i < largeArr.length; i++) {
            largeArr[i] = i * 2;
        }

        int target = 999998;

        // 比较不同搜索算法的性能
        long start = System.nanoTime();
        int result1 = BinarySearch.binarySearchIterative(largeArr, target);
        long time1 = System.nanoTime() - start;

        start = System.nanoTime();
        int result2 = CacheFriendlyBinarySearch.blockBinarySearch(largeArr, target);
        long time2 = System.nanoTime() - start;

        start = System.nanoTime();
        int result3 = CacheFriendlyBinarySearch.interpolationSearch(largeArr, target);
        long time3 = System.nanoTime() - start;

        System.out.println("普通二分查找: " + time1 / 1000.0 + " μs, 结果: " + result1);
        System.out.println("分块二分查找: " + time2 / 1000.0 + " μs, 结果: " + result2);
        System.out.println("插值搜索: " + time3 / 1000.0 + " μs, 结果: " + result3);
    }
}
```

## 🎯 总结

二分查找是一种优雅而强大的算法，体现了"分而治之"的编程思想：

### 核心特点
1. **效率高**：O(log n) 时间复杂度，显著优于线性查找
2. **适用范围广**：不仅用于数组查找，还有很多变种应用
3. **思想简单**：每次排除一半搜索空间
4. **边界处理重要**：正确处理边界是关键

### 应用场景
- **有序数组查找**：最基础的应用
- **二分答案**：求解最优化问题
- **数据结构**：BST、有序集合等
- **算法优化**：降低时间复杂度

### 实现要点
1. **防止整数溢出**：使用 `left + (right - left) / 2`
2. **边界条件**：明确开闭区间的定义
3. **循环不变式**：保持搜索区间的性质
4. **变种应用**：根据具体问题调整判断条件

二分查找不仅是一个基础算法，更是一种重要的问题解决思路。掌握二分查找的各种变种和应用，将极大提升你解决复杂问题的能力！

---

*下一篇：《数据结构入门教程：跳表数据结构详解与Java实现》*