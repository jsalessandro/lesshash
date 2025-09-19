---
title: "数据结构入门教程：排序算法综述与Java实现"
date: 2025-01-28T14:45:00+08:00
draft: false
tags: ["数据结构", "排序算法", "Java", "算法"]
categories: ["编程教程"]
series: ["数据结构入门教程"]
description: "全面解析经典排序算法，包含冒泡排序、选择排序、插入排序、归并排序、快速排序、堆排序等的原理分析与Java实现"
---

## 🔄 引言：数据的有序之美

想象一下图书馆里的书籍——如果所有的书都按照某种规律整齐排列，我们就能快速找到需要的书籍。这就是排序的魅力！**排序（Sorting）**是计算机科学中最基础也是最重要的算法之一，它将一组数据按照特定的顺序重新排列。

排序不仅能让数据更有序，更重要的是它为后续的查找、插入、删除等操作奠定了基础。一个排序良好的数据集合，能够显著提高算法的执行效率。

#### 流程图表


**关系流向：**
```
A["无序数据<br/>[64, 34, 25, 12, 22, 11, 90]"] → B["排序算法"]
B → C["有序数据<br/>[11, 12, 22, 25, 34, 64, 90]"]
```

## 📊 排序算法分类

排序算法可以从多个维度进行分类：

### 按稳定性分类
- **稳定排序**：相等元素的相对位置保持不变
- **不稳定排序**：相等元素的相对位置可能改变

### 按时间复杂度分类
- **O(n²) 算法**：冒泡、选择、插入排序
- **O(n log n) 算法**：归并、快速、堆排序
- **O(n) 算法**：计数、桶、基数排序（特定条件下）

### 按空间复杂度分类
- **原地排序**：空间复杂度 O(1)
- **非原地排序**：需要额外的存储空间

## 🎯 基础排序算法

### 1. 冒泡排序（Bubble Sort）

冒泡排序就像水中的气泡，小的元素会逐渐"浮"到前面。

```java
/**
 * 冒泡排序实现
 * 时间复杂度：O(n²)
 * 空间复杂度：O(1)
 * 稳定性：稳定
 */
public class BubbleSort {

    /**
     * 基础冒泡排序
     */
    public static void bubbleSortBasic(int[] arr) {
        int n = arr.length;
        System.out.println("开始冒泡排序: " + Arrays.toString(arr));

        for (int i = 0; i < n - 1; i++) {
            System.out.println("\n第 " + (i + 1) + " 轮冒泡:");

            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    // 交换相邻元素
                    swap(arr, j, j + 1);
                    System.out.println("交换 " + arr[j + 1] + " 和 " + arr[j] +
                                     ": " + Arrays.toString(arr));
                }
            }

            System.out.println("第 " + (i + 1) + " 轮结束: " + Arrays.toString(arr));
        }
    }

    /**
     * 优化版冒泡排序（提前终止）
     */
    public static void bubbleSortOptimized(int[] arr) {
        int n = arr.length;
        boolean swapped;

        for (int i = 0; i < n - 1; i++) {
            swapped = false;

            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    swap(arr, j, j + 1);
                    swapped = true;
                }
            }

            // 如果这一轮没有交换，说明已经有序
            if (!swapped) {
                System.out.println("数组已有序，提前结束排序");
                break;
            }
        }
    }

    /**
     * 双向冒泡排序（鸡尾酒排序）
     */
    public static void cocktailSort(int[] arr) {
        int left = 0;
        int right = arr.length - 1;
        boolean swapped = true;

        while (left < right && swapped) {
            swapped = false;

            // 从左到右冒泡
            for (int i = left; i < right; i++) {
                if (arr[i] > arr[i + 1]) {
                    swap(arr, i, i + 1);
                    swapped = true;
                }
            }
            right--;

            // 从右到左冒泡
            for (int i = right; i > left; i--) {
                if (arr[i] < arr[i - 1]) {
                    swap(arr, i, i - 1);
                    swapped = true;
                }
            }
            left++;
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

### 2. 选择排序（Selection Sort）

选择排序每次从未排序部分选择最小元素，放到已排序部分的末尾。

```java
/**
 * 选择排序实现
 * 时间复杂度：O(n²)
 * 空间复杂度：O(1)
 * 稳定性：不稳定
 */
public class SelectionSort {

    /**
     * 基础选择排序
     */
    public static void selectionSort(int[] arr) {
        int n = arr.length;
        System.out.println("开始选择排序: " + Arrays.toString(arr));

        for (int i = 0; i < n - 1; i++) {
            int minIndex = i;

            // 在未排序部分找到最小元素
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIndex]) {
                    minIndex = j;
                }
            }

            // 交换最小元素到当前位置
            if (minIndex != i) {
                System.out.println("第 " + (i + 1) + " 轮：将最小元素 " + arr[minIndex] +
                                 " 交换到位置 " + i);
                swap(arr, i, minIndex);
                System.out.println("当前状态: " + Arrays.toString(arr));
            }
        }
    }

    /**
     * 双向选择排序
     * 每次同时找到最小和最大元素
     */
    public static void doubleSelectionSort(int[] arr) {
        int left = 0;
        int right = arr.length - 1;

        while (left < right) {
            int minIndex = left;
            int maxIndex = right;

            // 同时找到最小和最大元素
            for (int i = left; i <= right; i++) {
                if (arr[i] < arr[minIndex]) {
                    minIndex = i;
                }
                if (arr[i] > arr[maxIndex]) {
                    maxIndex = i;
                }
            }

            // 处理特殊情况：最大元素在left位置
            if (maxIndex == left) {
                maxIndex = minIndex;
            }

            // 交换最小元素到左边
            swap(arr, left, minIndex);
            // 交换最大元素到右边
            swap(arr, right, maxIndex);

            left++;
            right--;
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

### 3. 插入排序（Insertion Sort）

插入排序就像整理手中的扑克牌，将每张牌插入到已排序牌组的正确位置。

```java
/**
 * 插入排序实现
 * 时间复杂度：最好O(n)，平均和最坏O(n²)
 * 空间复杂度：O(1)
 * 稳定性：稳定
 */
public class InsertionSort {

    /**
     * 基础插入排序
     */
    public static void insertionSort(int[] arr) {
        int n = arr.length;
        System.out.println("开始插入排序: " + Arrays.toString(arr));

        for (int i = 1; i < n; i++) {
            int current = arr[i];
            int j = i - 1;

            System.out.println("\n第 " + i + " 轮：插入元素 " + current);

            // 将当前元素插入到已排序部分的正确位置
            while (j >= 0 && arr[j] > current) {
                arr[j + 1] = arr[j];
                j--;
                System.out.println("移动元素: " + Arrays.toString(arr));
            }

            arr[j + 1] = current;
            System.out.println("插入完成: " + Arrays.toString(arr));
        }
    }

    /**
     * 二分插入排序
     * 使用二分查找定位插入位置
     */
    public static void binaryInsertionSort(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            int current = arr[i];
            int insertPos = binarySearch(arr, 0, i - 1, current);

            // 移动元素为插入腾出空间
            for (int j = i; j > insertPos; j--) {
                arr[j] = arr[j - 1];
            }

            arr[insertPos] = current;
        }
    }

    /**
     * 二分查找插入位置
     */
    private static int binarySearch(int[] arr, int left, int right, int target) {
        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] > target) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }

    /**
     * 希尔排序（插入排序的改进版）
     * 使用不同的间隔进行多轮插入排序
     */
    public static void shellSort(int[] arr) {
        int n = arr.length;

        // 使用Knuth序列: 1, 4, 13, 40, 121, ...
        int gap = 1;
        while (gap < n / 3) {
            gap = gap * 3 + 1;
        }

        while (gap >= 1) {
            System.out.println("使用间隔 " + gap + " 进行排序:");

            // 对每个子序列进行插入排序
            for (int i = gap; i < n; i++) {
                int current = arr[i];
                int j = i;

                while (j >= gap && arr[j - gap] > current) {
                    arr[j] = arr[j - gap];
                    j -= gap;
                }

                arr[j] = current;
            }

            System.out.println("间隔 " + gap + " 排序后: " + Arrays.toString(arr));
            gap = gap / 3;
        }
    }
}
```

## 🚀 高效排序算法

### 1. 归并排序（Merge Sort）

归并排序采用分治策略，将数组分成两半，分别排序后再合并。

```java
/**
 * 归并排序实现
 * 时间复杂度：O(n log n)
 * 空间复杂度：O(n)
 * 稳定性：稳定
 */
public class MergeSort {

    /**
     * 归并排序主函数
     */
    public static void mergeSort(int[] arr) {
        if (arr.length <= 1) return;

        int[] temp = new int[arr.length];
        mergeSortHelper(arr, temp, 0, arr.length - 1);
    }

    /**
     * 递归实现归并排序
     */
    private static void mergeSortHelper(int[] arr, int[] temp, int left, int right) {
        if (left >= right) return;

        int mid = left + (right - left) / 2;

        System.out.println("分治: [" + left + ", " + mid + "] 和 [" + (mid + 1) + ", " + right + "]");

        // 递归排序左半部分
        mergeSortHelper(arr, temp, left, mid);
        // 递归排序右半部分
        mergeSortHelper(arr, temp, mid + 1, right);

        // 合并两个有序子数组
        merge(arr, temp, left, mid, right);
    }

    /**
     * 合并两个有序子数组
     */
    private static void merge(int[] arr, int[] temp, int left, int mid, int right) {
        // 复制到临时数组
        for (int i = left; i <= right; i++) {
            temp[i] = arr[i];
        }

        int i = left;    // 左子数组指针
        int j = mid + 1; // 右子数组指针
        int k = left;    // 合并数组指针

        // 合并过程
        while (i <= mid && j <= right) {
            if (temp[i] <= temp[j]) {
                arr[k++] = temp[i++];
            } else {
                arr[k++] = temp[j++];
            }
        }

        // 复制剩余元素
        while (i <= mid) {
            arr[k++] = temp[i++];
        }
        while (j <= right) {
            arr[k++] = temp[j++];
        }

        System.out.println("合并结果: " + Arrays.toString(
            Arrays.copyOfRange(arr, left, right + 1)));
    }

    /**
     * 迭代版本的归并排序
     */
    public static void mergeSortIterative(int[] arr) {
        int n = arr.length;
        int[] temp = new int[n];

        // 子数组大小从1开始，每次翻倍
        for (int size = 1; size < n; size *= 2) {
            // 合并所有大小为size的相邻子数组
            for (int left = 0; left < n - size; left += 2 * size) {
                int mid = left + size - 1;
                int right = Math.min(left + 2 * size - 1, n - 1);

                merge(arr, temp, left, mid, right);
            }
            System.out.println("子数组大小 " + size + " 合并后: " + Arrays.toString(arr));
        }
    }
}
```

### 2. 快速排序（Quick Sort）

快速排序通过选择基准元素，将数组分为小于和大于基准的两部分。

```java
/**
 * 快速排序实现
 * 时间复杂度：平均O(n log n)，最坏O(n²)
 * 空间复杂度：O(log n)
 * 稳定性：不稳定
 */
public class QuickSort {

    /**
     * 快速排序主函数
     */
    public static void quickSort(int[] arr) {
        quickSortHelper(arr, 0, arr.length - 1);
    }

    /**
     * 递归实现快速排序
     */
    private static void quickSortHelper(int[] arr, int low, int high) {
        if (low < high) {
            // 分区，获取基准元素的最终位置
            int pivotIndex = partition(arr, low, high);

            System.out.println("基准元素 " + arr[pivotIndex] + " 的位置: " + pivotIndex);
            System.out.println("当前状态: " + Arrays.toString(arr));

            // 递归排序基准左侧
            quickSortHelper(arr, low, pivotIndex - 1);
            // 递归排序基准右侧
            quickSortHelper(arr, pivotIndex + 1, high);
        }
    }

    /**
     * Lomuto分区方案
     */
    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high]; // 选择最后一个元素作为基准
        int i = low - 1;       // 小于基准元素区域的右边界

        System.out.println("分区操作: 基准元素 = " + pivot);

        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }

        swap(arr, i + 1, high); // 将基准元素放到正确位置
        return i + 1;
    }

    /**
     * Hoare分区方案（双指针）
     */
    private static int partitionHoare(int[] arr, int low, int high) {
        int pivot = arr[low]; // 选择第一个元素作为基准
        int left = low - 1;
        int right = high + 1;

        while (true) {
            // 从左边找到大于等于基准的元素
            do {
                left++;
            } while (arr[left] < pivot);

            // 从右边找到小于等于基准的元素
            do {
                right--;
            } while (arr[right] > pivot);

            if (left >= right) {
                return right;
            }

            swap(arr, left, right);
        }
    }

    /**
     * 三路快排：处理重复元素优化
     */
    public static void quickSort3Way(int[] arr, int low, int high) {
        if (low >= high) return;

        int[] bounds = partition3Way(arr, low, high);
        int lt = bounds[0]; // 小于基准的区域右边界
        int gt = bounds[1]; // 大于基准的区域左边界

        quickSort3Way(arr, low, lt - 1);
        quickSort3Way(arr, gt + 1, high);
    }

    /**
     * 三路分区：将数组分为小于、等于、大于基准的三部分
     */
    private static int[] partition3Way(int[] arr, int low, int high) {
        int pivot = arr[low];
        int lt = low;      // arr[low...lt-1] < pivot
        int gt = high + 1; // arr[gt...high] > pivot
        int i = low + 1;   // arr[lt...i-1] == pivot

        while (i < gt) {
            if (arr[i] < pivot) {
                swap(arr, lt++, i++);
            } else if (arr[i] > pivot) {
                swap(arr, i, --gt);
            } else {
                i++;
            }
        }

        return new int[]{lt, gt};
    }

    /**
     * 随机化快速排序
     * 随机选择基准元素避免最坏情况
     */
    public static void randomizedQuickSort(int[] arr, int low, int high) {
        if (low < high) {
            // 随机选择基准元素
            int randomIndex = low + (int) (Math.random() * (high - low + 1));
            swap(arr, randomIndex, high);

            int pivotIndex = partition(arr, low, high);
            randomizedQuickSort(arr, low, pivotIndex - 1);
            randomizedQuickSort(arr, pivotIndex + 1, high);
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

### 3. 堆排序（Heap Sort）

堆排序利用堆的性质进行排序，首先建立最大堆，然后依次取出堆顶元素。

```java
/**
 * 堆排序实现
 * 时间复杂度：O(n log n)
 * 空间复杂度：O(1)
 * 稳定性：不稳定
 */
public class HeapSort {

    /**
     * 堆排序主函数
     */
    public static void heapSort(int[] arr) {
        int n = arr.length;

        System.out.println("开始堆排序: " + Arrays.toString(arr));

        // 构建最大堆
        buildMaxHeap(arr);
        System.out.println("构建最大堆: " + Arrays.toString(arr));

        // 依次取出堆顶元素（最大值）
        for (int i = n - 1; i > 0; i--) {
            // 将堆顶元素交换到数组末尾
            swap(arr, 0, i);
            System.out.println("交换堆顶到位置 " + i + ": " + Arrays.toString(arr));

            // 重新调整堆（堆大小减1）
            heapify(arr, 0, i);
            System.out.println("重新调整堆: " + Arrays.toString(arr));
        }
    }

    /**
     * 构建最大堆
     * 从最后一个非叶子节点开始，自底向上调整
     */
    private static void buildMaxHeap(int[] arr) {
        int n = arr.length;

        // 最后一个非叶子节点的索引
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, i, n);
        }
    }

    /**
     * 堆化操作：维护堆的性质
     * @param arr 数组
     * @param i 要调整的节点索引
     * @param heapSize 堆的大小
     */
    private static void heapify(int[] arr, int i, int heapSize) {
        int largest = i;       // 假设父节点最大
        int left = 2 * i + 1;  // 左子节点
        int right = 2 * i + 2; // 右子节点

        // 找到最大值的索引
        if (left < heapSize && arr[left] > arr[largest]) {
            largest = left;
        }

        if (right < heapSize && arr[right] > arr[largest]) {
            largest = right;
        }

        // 如果最大值不是父节点，进行交换并继续调整
        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, largest, heapSize);
        }
    }

    /**
     * 堆的可视化显示
     */
    public static void printHeap(int[] arr, int heapSize) {
        System.out.println("堆结构可视化:");

        int level = 0;
        int nodesInLevel = 1;
        int nodeCount = 0;

        for (int i = 0; i < heapSize; i++) {
            if (nodeCount == nodesInLevel) {
                System.out.println();
                level++;
                nodesInLevel *= 2;
                nodeCount = 0;

                // 打印缩进
                for (int j = 0; j < Math.pow(2, 3 - level); j++) {
                    System.out.print("  ");
                }
            }

            System.out.print(arr[i] + "  ");
            nodeCount++;
        }
        System.out.println("\n");
    }

    /**
     * 优先队列应用：Top K 问题
     */
    public static int[] findTopK(int[] arr, int k) {
        if (k >= arr.length) {
            int[] result = arr.clone();
            heapSort(result);
            return result;
        }

        // 使用最小堆维护Top K元素
        int[] minHeap = new int[k];
        System.arraycopy(arr, 0, minHeap, 0, k);
        buildMinHeap(minHeap);

        for (int i = k; i < arr.length; i++) {
            if (arr[i] > minHeap[0]) {
                minHeap[0] = arr[i];
                minHeapify(minHeap, 0, k);
            }
        }

        return minHeap;
    }

    private static void buildMinHeap(int[] arr) {
        for (int i = arr.length / 2 - 1; i >= 0; i--) {
            minHeapify(arr, i, arr.length);
        }
    }

    private static void minHeapify(int[] arr, int i, int heapSize) {
        int smallest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;

        if (left < heapSize && arr[left] < arr[smallest]) {
            smallest = left;
        }

        if (right < heapSize && arr[right] < arr[smallest]) {
            smallest = right;
        }

        if (smallest != i) {
            swap(arr, i, smallest);
            minHeapify(arr, smallest, heapSize);
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

## 📈 排序算法性能对比

### 性能分析工具

```java
/**
 * 排序算法性能分析工具
 */
public class SortingPerformanceAnalyzer {

    /**
     * 算法性能测试结果
     */
    public static class PerformanceResult {
        String algorithmName;
        long executionTime;
        int comparisons;
        int swaps;

        public PerformanceResult(String name, long time, int comps, int swaps) {
            this.algorithmName = name;
            this.executionTime = time;
            this.comparisons = comps;
            this.swaps = swaps;
        }

        @Override
        public String toString() {
            return String.format("%-15s: %8dns, %6d次比较, %6d次交换",
                               algorithmName, executionTime, comparisons, swaps);
        }
    }

    /**
     * 带计数的排序算法包装器
     */
    public static class SortingCounter {
        public int comparisons = 0;
        public int swaps = 0;

        public void resetCounters() {
            comparisons = 0;
            swaps = 0;
        }

        public boolean compare(int a, int b) {
            comparisons++;
            return a > b;
        }

        public void swap(int[] arr, int i, int j) {
            swaps++;
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }

    /**
     * 测试不同规模数据的性能
     */
    public static void benchmarkAlgorithms() {
        int[] sizes = {100, 1000, 5000, 10000};
        String[] dataTypes = {"随机数据", "已排序数据", "逆序数据", "部分有序数据"};

        System.out.println("排序算法性能对比分析");
        System.out.println("=".repeat(80));

        for (int size : sizes) {
            System.out.println("\n数据规模: " + size);
            System.out.println("-".repeat(60));

            for (String dataType : dataTypes) {
                System.out.println("\n" + dataType + ":");

                int[] testData = generateTestData(size, dataType);
                testAlgorithm("冒泡排序", testData.clone(), BubbleSort::bubbleSortOptimized);
                testAlgorithm("选择排序", testData.clone(), SelectionSort::selectionSort);
                testAlgorithm("插入排序", testData.clone(), InsertionSort::insertionSort);
                testAlgorithm("归并排序", testData.clone(), MergeSort::mergeSort);
                testAlgorithm("快速排序", testData.clone(), QuickSort::quickSort);
                testAlgorithm("堆排序", testData.clone(), HeapSort::heapSort);
            }
        }
    }

    /**
     * 生成测试数据
     */
    private static int[] generateTestData(int size, String type) {
        int[] data = new int[size];
        Random random = new Random(42); // 固定种子保证可重复性

        switch (type) {
            case "随机数据":
                for (int i = 0; i < size; i++) {
                    data[i] = random.nextInt(size * 10);
                }
                break;

            case "已排序数据":
                for (int i = 0; i < size; i++) {
                    data[i] = i;
                }
                break;

            case "逆序数据":
                for (int i = 0; i < size; i++) {
                    data[i] = size - i;
                }
                break;

            case "部分有序数据":
                // 80%有序，20%随机
                for (int i = 0; i < size; i++) {
                    data[i] = i;
                }
                int shuffleCount = size / 5;
                for (int i = 0; i < shuffleCount; i++) {
                    int idx1 = random.nextInt(size);
                    int idx2 = random.nextInt(size);
                    int temp = data[idx1];
                    data[idx1] = data[idx2];
                    data[idx2] = temp;
                }
                break;
        }

        return data;
    }

    /**
     * 测试单个算法性能
     */
    private static void testAlgorithm(String name, int[] data, Consumer<int[]> algorithm) {
        long startTime = System.nanoTime();
        algorithm.accept(data);
        long endTime = System.nanoTime();

        long executionTime = endTime - startTime;
        System.out.printf("  %-12s: %8.2f ms%n", name, executionTime / 1_000_000.0);
    }

    /**
     * 稳定性测试
     */
    public static void testStability() {
        System.out.println("排序算法稳定性测试");
        System.out.println("=".repeat(40));

        // 使用包含相等元素的测试数据
        Element[] testData = {
            new Element(3, "A"), new Element(1, "B"), new Element(3, "C"),
            new Element(2, "D"), new Element(1, "E"), new Element(2, "F")
        };

        System.out.println("原始数据: " + Arrays.toString(testData));

        // 测试各种排序算法的稳定性
        testStableSort("归并排序", testData.clone(), MergeSortStable::sort);
        testStableSort("插入排序", testData.clone(), InsertionSortStable::sort);
        testStableSort("快速排序", testData.clone(), QuickSortStable::sort);
    }

    private static void testStableSort(String name, Element[] data,
                                     Consumer<Element[]> algorithm) {
        algorithm.accept(data);
        boolean isStable = checkStability(data);
        System.out.println(name + " - " + Arrays.toString(data) +
                         " (稳定: " + isStable + ")");
    }

    private static boolean checkStability(Element[] data) {
        for (int i = 1; i < data.length; i++) {
            if (data[i].value == data[i-1].value) {
                if (data[i].originalIndex < data[i-1].originalIndex) {
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * 用于稳定性测试的元素类
     */
    static class Element {
        int value;
        String originalIndex;

        Element(int value, String index) {
            this.value = value;
            this.originalIndex = index;
        }

        @Override
        public String toString() {
            return value + originalIndex;
        }
    }
}
```

### 排序算法选择指南

```java
/**
 * 排序算法选择决策器
 */
public class SortingAlgorithmSelector {

    public enum DataCharacteristic {
        SMALL_SIZE,           // 小规模数据 (n < 50)
        LARGE_SIZE,           // 大规模数据 (n > 10000)
        MOSTLY_SORTED,        // 基本有序
        RANDOM,              // 随机分布
        MANY_DUPLICATES,     // 大量重复
        MEMORY_CONSTRAINED,  // 内存受限
        STABILITY_REQUIRED   // 需要稳定性
    }

    /**
     * 根据数据特征推荐排序算法
     */
    public static String recommendAlgorithm(DataCharacteristic... characteristics) {
        Set<DataCharacteristic> charSet = EnumSet.of(characteristics[0], characteristics);

        if (charSet.contains(DataCharacteristic.SMALL_SIZE)) {
            return "插入排序 - 小规模数据时简单高效";
        }

        if (charSet.contains(DataCharacteristic.MOSTLY_SORTED)) {
            return "插入排序 - 对于基本有序的数据最优";
        }

        if (charSet.contains(DataCharacteristic.STABILITY_REQUIRED)) {
            if (charSet.contains(DataCharacteristic.MEMORY_CONSTRAINED)) {
                return "归并排序变种 - 原地归并或使用较小的辅助空间";
            }
            return "归并排序 - 稳定且时间复杂度保证O(n log n)";
        }

        if (charSet.contains(DataCharacteristic.MANY_DUPLICATES)) {
            return "三路快速排序 - 专门优化重复元素的处理";
        }

        if (charSet.contains(DataCharacteristic.MEMORY_CONSTRAINED)) {
            return "堆排序 - 原地排序，空间复杂度O(1)";
        }

        if (charSet.contains(DataCharacteristic.LARGE_SIZE)) {
            return "快速排序 - 平均情况下最快的通用排序算法";
        }

        return "快速排序 - 通用场景下的最佳选择";
    }

    /**
     * 性能特征对比表
     */
    public static void printComparisonTable() {
        System.out.println("排序算法特征对比表");
        System.out.println("=".repeat(100));
        System.out.printf("%-12s %-12s %-12s %-12s %-8s %-8s %-10s%n",
                         "算法", "最好时间", "平均时间", "最坏时间", "空间", "稳定", "原地");
        System.out.println("-".repeat(100));

        String[][] data = {
            {"冒泡排序", "O(n)", "O(n²)", "O(n²)", "O(1)", "是", "是"},
            {"选择排序", "O(n²)", "O(n²)", "O(n²)", "O(1)", "否", "是"},
            {"插入排序", "O(n)", "O(n²)", "O(n²)", "O(1)", "是", "是"},
            {"归并排序", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", "是", "否"},
            {"快速排序", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)", "否", "是"},
            {"堆排序", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)", "否", "是"},
            {"希尔排序", "O(n log n)", "O(n^1.25)", "O(n²)", "O(1)", "否", "是"}
        };

        for (String[] row : data) {
            System.out.printf("%-12s %-12s %-12s %-12s %-8s %-8s %-10s%n",
                             row[0], row[1], row[2], row[3], row[4], row[5], row[6]);
        }
    }
}
```

## 🧪 完整测试示例

```java
/**
 * 排序算法综合测试
 */
public class SortingTest {
    public static void main(String[] args) {
        System.out.println("=== 排序算法综合测试 ===");

        testBasicSortingAlgorithms();
        testAdvancedSortingAlgorithms();
        testSpecialCases();
        SortingPerformanceAnalyzer.benchmarkAlgorithms();
        SortingPerformanceAnalyzer.testStability();
        SortingAlgorithmSelector.printComparisonTable();
    }

    private static void testBasicSortingAlgorithms() {
        System.out.println("\n1. 基础排序算法测试:");

        int[] testData = {64, 34, 25, 12, 22, 11, 90};

        System.out.println("冒泡排序:");
        BubbleSort.bubbleSortBasic(testData.clone());

        System.out.println("\n选择排序:");
        SelectionSort.selectionSort(testData.clone());

        System.out.println("\n插入排序:");
        InsertionSort.insertionSort(testData.clone());
    }

    private static void testAdvancedSortingAlgorithms() {
        System.out.println("\n2. 高级排序算法测试:");

        int[] testData = {38, 27, 43, 3, 9, 82, 10};

        System.out.println("归并排序:");
        int[] mergeData = testData.clone();
        MergeSort.mergeSort(mergeData);
        System.out.println("最终结果: " + Arrays.toString(mergeData));

        System.out.println("\n快速排序:");
        int[] quickData = testData.clone();
        QuickSort.quickSort(quickData);
        System.out.println("最终结果: " + Arrays.toString(quickData));

        System.out.println("\n堆排序:");
        int[] heapData = testData.clone();
        HeapSort.heapSort(heapData);
        System.out.println("最终结果: " + Arrays.toString(heapData));
    }

    private static void testSpecialCases() {
        System.out.println("\n3. 特殊情况测试:");

        // 测试空数组
        int[] emptyArray = {};
        QuickSort.quickSort(emptyArray);
        System.out.println("空数组排序: " + Arrays.toString(emptyArray));

        // 测试单元素数组
        int[] singleElement = {42};
        QuickSort.quickSort(singleElement);
        System.out.println("单元素数组: " + Arrays.toString(singleElement));

        // 测试已排序数组
        int[] sortedArray = {1, 2, 3, 4, 5};
        System.out.println("已排序数组插入排序测试:");
        InsertionSort.insertionSort(sortedArray.clone());

        // 测试重复元素
        int[] duplicateArray = {3, 1, 3, 2, 1, 2, 3};
        System.out.println("重复元素三路快排:");
        QuickSort.quickSort3Way(duplicateArray, 0, duplicateArray.length - 1);
        System.out.println("结果: " + Arrays.toString(duplicateArray));
    }
}
```

## 🎯 总结

排序算法是计算机科学的基石，每种算法都有其独特的优势和适用场景：

### 核心洞察
1. **没有万能的排序算法**：算法选择取决于具体场景
2. **时间与空间的权衡**：有些算法用空间换时间，有些则相反
3. **稳定性的重要性**：在某些场景下，稳定性比性能更重要
4. **输入数据的特征**：数据的初始状态大大影响算法性能

### 算法选择策略
- **小规模数据（n < 50）**：插入排序
- **需要稳定性**：归并排序
- **内存受限**：堆排序
- **一般情况**：快速排序
- **大量重复元素**：三路快速排序
- **基本有序**：插入排序

### 实际应用建议
1. **了解数据特征**：大小、分布、是否有序
2. **考虑稳定性需求**：是否需要保持相等元素的相对位置
3. **评估空间限制**：是否允许使用额外空间
4. **性能测试验证**：在实际数据上测试不同算法

掌握排序算法不仅能帮你解决具体问题，更重要的是培养分析问题、设计算法的思维方式。这些思维方式将在你的整个编程生涯中发挥重要作用！

---

*下一篇：《数据结构入门教程：线性排序算法详解与Java实现》*