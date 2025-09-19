---
title: "数据结构详解：树(Tree) - 层次分明的数据王国"
date: 2025-01-06T10:06:00+08:00
tags: ["数据结构", "树", "Tree", "Java", "算法"]
categories: ["数据结构"]
series: ["数据结构入门教程"]
author: "lesshash"
---

# 数据结构详解：树(Tree) - 层次分明的数据王国

## 引言

在计算机科学的世界里，数据结构如同建筑的骨架，支撑着整个程序的运行。今天我们要探讨的是一种既优雅又强大的数据结构——树(Tree)。树是一种非线性的数据结构，它以其层次分明的特点，在各种算法和应用中发挥着重要作用。

## 1. 树的基本概念

### 1.1 什么是树？

树是一种分层的数据结构，由节点(Node)和边(Edge)组成。它模拟了现实世界中树的结构，有根、有分支、有叶子。在计算机科学中，树通常是倒置的，根在上方，叶子在下方。

#### 流程图表


**关系流向：**
```
A[根节点 Root] → B[节点 B]
A → C[节点 C]
B → D[节点 D]
B → E[节点 E]
C → F[节点 F]
```

### 1.2 树的术语

- **节点(Node)**: 树中的基本单元，包含数据和指向子节点的引用
- **根节点(Root)**: 树的顶部节点，没有父节点
- **父节点(Parent)**: 有子节点的节点
- **子节点(Child)**: 某个节点的直接下级节点
- **叶子节点(Leaf)**: 没有子节点的节点
- **内部节点(Internal Node)**: 有子节点的节点
- **边(Edge)**: 连接两个节点的链接
- **路径(Path)**: 从一个节点到另一个节点的节点序列
- **深度(Depth)**: 从根节点到某个节点的边数
- **高度(Height)**: 从某个节点到最远叶子节点的边数
- **层次(Level)**: 节点的深度 + 1
- **度(Degree)**: 节点的子节点数量

### 1.3 树的特性

1. **唯一根节点**: 每棵树有且仅有一个根节点
2. **无环结构**: 树中不存在环路
3. **连通性**: 任意两个节点之间存在唯一路径
4. **层次性**: 节点按层次排列，形成清晰的层级关系

## 2. 现实生活中的树结构

### 2.1 家族族谱

#### 流程图表


**关系流向：**
```
爷爷 → 父亲
爷爷 → 叔叔
父亲 → 我
父亲 → 弟弟
叔叔 → 堂兄
```

家族族谱是树结构的完美体现，每个人都有明确的辈分关系，形成清晰的层次结构。

### 2.2 文件系统

#### 流程图表


**关系流向：**
```
根目录["/"] → home["home/"]
根目录 → usr["usr/"]
根目录 → var["var/"]
home → user1["user1/"]
home → user2["user2/"]
```

计算机的文件系统是树结构的典型应用，每个目录可以包含子目录和文件，形成层次化的存储结构。

### 2.3 公司组织架构

#### 流程图表


**关系流向：**
```
CEO[CEO] → CTO[CTO]
CEO → CFO[CFO]
CEO → CMO[CMO]
CTO → 开发部[开发部]
CTO → 测试部[测试部]
```

公司的组织架构也是典型的树结构，体现了权力和责任的层级关系。

## 3. 树的类型

### 3.1 二叉树 (Binary Tree)

二叉树是每个节点最多有两个子节点的树，这两个子节点分别称为左子节点和右子节点。

#### 流程图表


**关系流向：**
```
A[1] → B[2]
A → C[3]
B → D[4]
B → E[5]
C → F[6]
```

**Java实现：**

```java
public class BinaryTreeNode {
    int data;
    BinaryTreeNode left;
    BinaryTreeNode right;

    public BinaryTreeNode(int data) {
        this.data = data;
        this.left = null;
        this.right = null;
    }
}

public class BinaryTree {
    private BinaryTreeNode root;

    public BinaryTree() {
        this.root = null;
    }

    // 插入节点（层序插入）
    public void insert(int data) {
        if (root == null) {
            root = new BinaryTreeNode(data);
            return;
        }

        Queue<BinaryTreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            BinaryTreeNode current = queue.poll();

            if (current.left == null) {
                current.left = new BinaryTreeNode(data);
                break;
            } else {
                queue.offer(current.left);
            }

            if (current.right == null) {
                current.right = new BinaryTreeNode(data);
                break;
            } else {
                queue.offer(current.right);
            }
        }
    }

    // 获取树的高度
    public int getHeight(BinaryTreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + Math.max(getHeight(node.left), getHeight(node.right));
    }

    // 计算节点数量
    public int countNodes(BinaryTreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + countNodes(node.left) + countNodes(node.right);
    }
}
```

### 3.2 二叉搜索树 (Binary Search Tree, BST)

二叉搜索树是一种特殊的二叉树，满足以下性质：
- 左子树的所有节点值小于根节点值
- 右子树的所有节点值大于根节点值
- 左右子树也都是二叉搜索树

#### 流程图表


**关系流向：**
```
A[8] → B[3]
A → C[15]
B → D[1]
B → E[6]
E → F[4]
```

**Java实现：**

```java
public class BinarySearchTree {
    private BinaryTreeNode root;

    public BinarySearchTree() {
        this.root = null;
    }

    // 插入节点
    public void insert(int data) {
        root = insertRec(root, data);
    }

    private BinaryTreeNode insertRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return new BinaryTreeNode(data);
        }

        if (data < node.data) {
            node.left = insertRec(node.left, data);
        } else if (data > node.data) {
            node.right = insertRec(node.right, data);
        }

        return node;
    }

    // 搜索节点
    public boolean search(int data) {
        return searchRec(root, data);
    }

    private boolean searchRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return false;
        }

        if (data == node.data) {
            return true;
        }

        if (data < node.data) {
            return searchRec(node.left, data);
        } else {
            return searchRec(node.right, data);
        }
    }

    // 删除节点
    public void delete(int data) {
        root = deleteRec(root, data);
    }

    private BinaryTreeNode deleteRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return null;
        }

        if (data < node.data) {
            node.left = deleteRec(node.left, data);
        } else if (data > node.data) {
            node.right = deleteRec(node.right, data);
        } else {
            // 要删除的节点
            if (node.left == null) {
                return node.right;
            } else if (node.right == null) {
                return node.left;
            }

            // 有两个子节点的情况
            node.data = findMin(node.right);
            node.right = deleteRec(node.right, node.data);
        }

        return node;
    }

    private int findMin(BinaryTreeNode node) {
        while (node.left != null) {
            node = node.left;
        }
        return node.data;
    }
}
```

### 3.3 平衡二叉树 (AVL Tree)

AVL树是一种自平衡的二叉搜索树，任何节点的两个子树的高度差不超过1。

#### 流程图表


**关系流向：**
```
A[10] → B[5]
A → C[15]
B → D[2]
B → E[8]
C → F[12]
```

**平衡因子** = 左子树高度 - 右子树高度，AVL树中平衡因子只能是-1、0、1。

### 3.4 红黑树 (Red-Black Tree)

红黑树是一种自平衡的二叉搜索树，每个节点都有颜色属性（红色或黑色）。

**红黑树的性质：**
1. 每个节点是红色或黑色
2. 根节点是黑色
3. 所有叶子节点（NIL）是黑色
4. 红色节点的子节点必须是黑色
5. 从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点

### 3.5 B树 (B-Tree)

B树是一种多路搜索树，常用于数据库和文件系统的索引结构。

#### 流程图表


**关系流向：**
```
A["[10, 20]"] → B["[5, 8]"]
A → C["[15, 18]"]
A → D["[25, 30]"]
B → E["[1, 3]"]
B → F["[6, 7]"]
```

## 4. 树的遍历算法

树的遍历是指按照某种规则访问树中的每个节点。主要有四种遍历方式：

### 4.1 前序遍历 (Preorder Traversal)

访问顺序：根节点 → 左子树 → 右子树

```java
public void preorderTraversal(BinaryTreeNode node) {
    if (node != null) {
        System.out.print(node.data + " ");  // 访问根节点
        preorderTraversal(node.left);       // 遍历左子树
        preorderTraversal(node.right);      // 遍历右子树
    }
}

// 非递归实现
public void preorderIterative(BinaryTreeNode root) {
    if (root == null) return;

    Stack<BinaryTreeNode> stack = new Stack<>();
    stack.push(root);

    while (!stack.isEmpty()) {
        BinaryTreeNode current = stack.pop();
        System.out.print(current.data + " ");

        // 先压入右子树，再压入左子树
        if (current.right != null) {
            stack.push(current.right);
        }
        if (current.left != null) {
            stack.push(current.left);
        }
    }
}
```

### 4.2 中序遍历 (Inorder Traversal)

访问顺序：左子树 → 根节点 → 右子树

```java
public void inorderTraversal(BinaryTreeNode node) {
    if (node != null) {
        inorderTraversal(node.left);        // 遍历左子树
        System.out.print(node.data + " ");  // 访问根节点
        inorderTraversal(node.right);       // 遍历右子树
    }
}

// 非递归实现
public void inorderIterative(BinaryTreeNode root) {
    Stack<BinaryTreeNode> stack = new Stack<>();
    BinaryTreeNode current = root;

    while (current != null || !stack.isEmpty()) {
        // 一直向左走到底
        while (current != null) {
            stack.push(current);
            current = current.left;
        }

        // 处理栈顶元素
        current = stack.pop();
        System.out.print(current.data + " ");

        // 转向右子树
        current = current.right;
    }
}
```

### 4.3 后序遍历 (Postorder Traversal)

访问顺序：左子树 → 右子树 → 根节点

```java
public void postorderTraversal(BinaryTreeNode node) {
    if (node != null) {
        postorderTraversal(node.left);      // 遍历左子树
        postorderTraversal(node.right);     // 遍历右子树
        System.out.print(node.data + " ");  // 访问根节点
    }
}

// 非递归实现
public void postorderIterative(BinaryTreeNode root) {
    if (root == null) return;

    Stack<BinaryTreeNode> stack = new Stack<>();
    BinaryTreeNode lastVisited = null;
    BinaryTreeNode current = root;

    while (current != null || !stack.isEmpty()) {
        if (current != null) {
            stack.push(current);
            current = current.left;
        } else {
            BinaryTreeNode peek = stack.peek();

            // 如果右子树存在且未被访问过
            if (peek.right != null && lastVisited != peek.right) {
                current = peek.right;
            } else {
                System.out.print(peek.data + " ");
                lastVisited = stack.pop();
            }
        }
    }
}
```

### 4.4 层序遍历 (Level-order Traversal)

按层次从上到下、从左到右访问节点

```java
public void levelOrderTraversal(BinaryTreeNode root) {
    if (root == null) return;

    Queue<BinaryTreeNode> queue = new LinkedList<>();
    queue.offer(root);

    while (!queue.isEmpty()) {
        BinaryTreeNode current = queue.poll();
        System.out.print(current.data + " ");

        if (current.left != null) {
            queue.offer(current.left);
        }
        if (current.right != null) {
            queue.offer(current.right);
        }
    }
}

// 分层打印
public void levelOrderWithLevels(BinaryTreeNode root) {
    if (root == null) return;

    Queue<BinaryTreeNode> queue = new LinkedList<>();
    queue.offer(root);

    while (!queue.isEmpty()) {
        int levelSize = queue.size();

        for (int i = 0; i < levelSize; i++) {
            BinaryTreeNode current = queue.poll();
            System.out.print(current.data + " ");

            if (current.left != null) {
                queue.offer(current.left);
            }
            if (current.right != null) {
                queue.offer(current.right);
            }
        }
        System.out.println(); // 换行表示下一层
    }
}
```

### 4.5 遍历结果示例

对于下面的二叉树：

#### 流程图表


**关系流向：**
```
A[1] → B[2]
A → C[3]
B → D[4]
B → E[5]
C → F[6]
```

各种遍历的结果：
- **前序遍历**: 1 2 4 5 3 6 7
- **中序遍历**: 4 2 5 1 6 3 7
- **后序遍历**: 4 5 2 6 7 3 1
- **层序遍历**: 1 2 3 4 5 6 7

## 5. 完整的二叉搜索树实现

```java
import java.util.*;

public class CompleteBinarySearchTree {
    private BinaryTreeNode root;

    private class BinaryTreeNode {
        int data;
        BinaryTreeNode left;
        BinaryTreeNode right;

        public BinaryTreeNode(int data) {
            this.data = data;
            this.left = null;
            this.right = null;
        }
    }

    public CompleteBinarySearchTree() {
        this.root = null;
    }

    // 插入操作
    public void insert(int data) {
        root = insertRec(root, data);
    }

    private BinaryTreeNode insertRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return new BinaryTreeNode(data);
        }

        if (data < node.data) {
            node.left = insertRec(node.left, data);
        } else if (data > node.data) {
            node.right = insertRec(node.right, data);
        }

        return node;
    }

    // 查找操作
    public boolean search(int data) {
        return searchRec(root, data);
    }

    private boolean searchRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return false;
        }

        if (data == node.data) {
            return true;
        }

        return data < node.data ?
            searchRec(node.left, data) :
            searchRec(node.right, data);
    }

    // 删除操作
    public void delete(int data) {
        root = deleteRec(root, data);
    }

    private BinaryTreeNode deleteRec(BinaryTreeNode node, int data) {
        if (node == null) {
            return null;
        }

        if (data < node.data) {
            node.left = deleteRec(node.left, data);
        } else if (data > node.data) {
            node.right = deleteRec(node.right, data);
        } else {
            // 找到要删除的节点

            // 情况1：叶子节点或只有一个子节点
            if (node.left == null) {
                return node.right;
            } else if (node.right == null) {
                return node.left;
            }

            // 情况2：有两个子节点
            // 找到右子树中的最小值（中序后继）
            node.data = findMin(node.right);

            // 删除中序后继
            node.right = deleteRec(node.right, node.data);
        }

        return node;
    }

    private int findMin(BinaryTreeNode node) {
        while (node.left != null) {
            node = node.left;
        }
        return node.data;
    }

    private int findMax(BinaryTreeNode node) {
        while (node.right != null) {
            node = node.right;
        }
        return node.data;
    }

    // 获取树的高度
    public int getHeight() {
        return getHeight(root);
    }

    private int getHeight(BinaryTreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + Math.max(getHeight(node.left), getHeight(node.right));
    }

    // 验证是否为有效的BST
    public boolean isValidBST() {
        return isValidBST(root, Integer.MIN_VALUE, Integer.MAX_VALUE);
    }

    private boolean isValidBST(BinaryTreeNode node, int min, int max) {
        if (node == null) {
            return true;
        }

        if (node.data <= min || node.data >= max) {
            return false;
        }

        return isValidBST(node.left, min, node.data) &&
               isValidBST(node.right, node.data, max);
    }

    // 可视化打印树结构
    public void printTree() {
        printTree(root, "", true);
    }

    private void printTree(BinaryTreeNode node, String prefix, boolean isLast) {
        if (node != null) {
            System.out.println(prefix + (isLast ? "└── " : "├── ") + node.data);

            if (node.left != null || node.right != null) {
                if (node.left != null) {
                    printTree(node.left, prefix + (isLast ? "    " : "│   "),
                             node.right == null);
                }
                if (node.right != null) {
                    printTree(node.right, prefix + (isLast ? "    " : "│   "), true);
                }
            }
        }
    }

    // 所有遍历方法
    public void preorderTraversal() {
        System.out.print("前序遍历: ");
        preorderRec(root);
        System.out.println();
    }

    private void preorderRec(BinaryTreeNode node) {
        if (node != null) {
            System.out.print(node.data + " ");
            preorderRec(node.left);
            preorderRec(node.right);
        }
    }

    public void inorderTraversal() {
        System.out.print("中序遍历: ");
        inorderRec(root);
        System.out.println();
    }

    private void inorderRec(BinaryTreeNode node) {
        if (node != null) {
            inorderRec(node.left);
            System.out.print(node.data + " ");
            inorderRec(node.right);
        }
    }

    public void postorderTraversal() {
        System.out.print("后序遍历: ");
        postorderRec(root);
        System.out.println();
    }

    private void postorderRec(BinaryTreeNode node) {
        if (node != null) {
            postorderRec(node.left);
            postorderRec(node.right);
            System.out.print(node.data + " ");
        }
    }

    public void levelOrderTraversal() {
        System.out.print("层序遍历: ");
        if (root == null) return;

        Queue<BinaryTreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            BinaryTreeNode current = queue.poll();
            System.out.print(current.data + " ");

            if (current.left != null) {
                queue.offer(current.left);
            }
            if (current.right != null) {
                queue.offer(current.right);
            }
        }
        System.out.println();
    }
}
```

## 6. 树的平衡技术

### 6.1 AVL树的旋转操作

AVL树通过旋转操作来维持平衡：

```java
public class AVLTree {
    private AVLNode root;

    private class AVLNode {
        int data;
        int height;
        AVLNode left;
        AVLNode right;

        public AVLNode(int data) {
            this.data = data;
            this.height = 1;
        }
    }

    private int getHeight(AVLNode node) {
        return node == null ? 0 : node.height;
    }

    private int getBalance(AVLNode node) {
        return node == null ? 0 : getHeight(node.left) - getHeight(node.right);
    }

    private void updateHeight(AVLNode node) {
        if (node != null) {
            node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));
        }
    }

    // 右旋转
    private AVLNode rotateRight(AVLNode y) {
        AVLNode x = y.left;
        AVLNode T2 = x.right;

        // 执行旋转
        x.right = y;
        y.left = T2;

        // 更新高度
        updateHeight(y);
        updateHeight(x);

        return x;
    }

    // 左旋转
    private AVLNode rotateLeft(AVLNode x) {
        AVLNode y = x.right;
        AVLNode T2 = y.left;

        // 执行旋转
        y.left = x;
        x.right = T2;

        // 更新高度
        updateHeight(x);
        updateHeight(y);

        return y;
    }

    public void insert(int data) {
        root = insertRec(root, data);
    }

    private AVLNode insertRec(AVLNode node, int data) {
        // 1. 执行标准BST插入
        if (node == null) {
            return new AVLNode(data);
        }

        if (data < node.data) {
            node.left = insertRec(node.left, data);
        } else if (data > node.data) {
            node.right = insertRec(node.right, data);
        } else {
            return node; // 重复值不插入
        }

        // 2. 更新当前节点的高度
        updateHeight(node);

        // 3. 获取平衡因子
        int balance = getBalance(node);

        // 4. 如果不平衡，有四种情况需要处理

        // 左左情况
        if (balance > 1 && data < node.left.data) {
            return rotateRight(node);
        }

        // 右右情况
        if (balance < -1 && data > node.right.data) {
            return rotateLeft(node);
        }

        // 左右情况
        if (balance > 1 && data > node.left.data) {
            node.left = rotateLeft(node.left);
            return rotateRight(node);
        }

        // 右左情况
        if (balance < -1 && data < node.right.data) {
            node.right = rotateRight(node.right);
            return rotateLeft(node);
        }

        return node;
    }
}
```

### 6.2 旋转操作图解

**右旋转（LL情况）：**

#### 流程图表


**关系流向：**
```
Y1[Y] → X1[X]
Y1 → C1[C]
X1 → A1[A]
X1 → B1[B]
X2[X] → A2[A]
```

**左旋转（RR情况）：**

#### 流程图表


**关系流向：**
```
X3[X] → A3[A]
X3 → Y3[Y]
Y3 → B3[B]
Y3 → C3[C]
Y4[Y] → X4[X]
```

## 7. 性能分析

### 7.1 时间复杂度对比

| 操作 | 普通二叉树 | 二叉搜索树(平均) | 二叉搜索树(最坏) | AVL树 | 红黑树 |
|------|------------|------------------|------------------|-------|--------|
| 搜索 | O(n) | O(log n) | O(n) | O(log n) | O(log n) |
| 插入 | O(n) | O(log n) | O(n) | O(log n) | O(log n) |
| 删除 | O(n) | O(log n) | O(n) | O(log n) | O(log n) |

### 7.2 空间复杂度

所有树结构的空间复杂度都是 O(n)，其中 n 是节点数量。

### 7.3 性能测试代码

```java
public class TreePerformanceTest {
    public static void main(String[] args) {
        int[] testSizes = {1000, 10000, 100000};

        for (int size : testSizes) {
            System.out.println("测试数据规模: " + size);

            // 测试BST
            CompleteBinarySearchTree bst = new CompleteBinarySearchTree();
            long startTime = System.nanoTime();

            // 插入随机数据
            Random random = new Random();
            for (int i = 0; i < size; i++) {
                bst.insert(random.nextInt(size * 2));
            }

            long insertTime = System.nanoTime() - startTime;

            // 测试搜索
            startTime = System.nanoTime();
            for (int i = 0; i < 1000; i++) {
                bst.search(random.nextInt(size * 2));
            }
            long searchTime = System.nanoTime() - startTime;

            System.out.println("BST插入时间: " + insertTime / 1_000_000 + "ms");
            System.out.println("BST搜索时间: " + searchTime / 1_000_000 + "ms");
            System.out.println("树的高度: " + bst.getHeight());
            System.out.println("------------------------");
        }
    }
}
```

## 8. 树的实际应用

### 8.1 表达式树

用于表示数学表达式的树结构：

#### 流程图表


**关系流向：**
```
A[+] → B[*]
A → C[/]
B → D[2]
B → E[3]
C → F[8]
```

表达式: (2 * 3) + (8 / 4) = 8

```java
public class ExpressionTree {
    private class ExpressionNode {
        String value;
        ExpressionNode left;
        ExpressionNode right;

        public ExpressionNode(String value) {
            this.value = value;
        }

        public boolean isOperator() {
            return "+-*/".contains(value);
        }
    }

    public double evaluate(ExpressionNode node) {
        if (node == null) {
            return 0;
        }

        if (!node.isOperator()) {
            return Double.parseDouble(node.value);
        }

        double leftValue = evaluate(node.left);
        double rightValue = evaluate(node.right);

        switch (node.value) {
            case "+": return leftValue + rightValue;
            case "-": return leftValue - rightValue;
            case "*": return leftValue * rightValue;
            case "/": return leftValue / rightValue;
            default: throw new IllegalArgumentException("未知运算符: " + node.value);
        }
    }
}
```

### 8.2 决策树

用于机器学习和决策分析：

#### 流程图表


**关系流向：**
```
A[天气] → B[晴天]
A → C[阴天]
A → D[雨天]
B → E[去公园]
C → F[温度]
```

### 8.3 Trie树（前缀树）

用于字符串搜索和自动补全：

```java
public class Trie {
    private TrieNode root;

    private class TrieNode {
        Map<Character, TrieNode> children;
        boolean isEndOfWord;

        public TrieNode() {
            children = new HashMap<>();
            isEndOfWord = false;
        }
    }

    public Trie() {
        root = new TrieNode();
    }

    public void insert(String word) {
        TrieNode current = root;

        for (char ch : word.toCharArray()) {
            current.children.putIfAbsent(ch, new TrieNode());
            current = current.children.get(ch);
        }

        current.isEndOfWord = true;
    }

    public boolean search(String word) {
        TrieNode current = root;

        for (char ch : word.toCharArray()) {
            if (!current.children.containsKey(ch)) {
                return false;
            }
            current = current.children.get(ch);
        }

        return current.isEndOfWord;
    }

    public boolean startsWith(String prefix) {
        TrieNode current = root;

        for (char ch : prefix.toCharArray()) {
            if (!current.children.containsKey(ch)) {
                return false;
            }
            current = current.children.get(ch);
        }

        return true;
    }
}
```

## 9. 树的可视化和调试

### 9.1 树的图形化表示

```java
public class TreeVisualizer {
    public static void printBinaryTree(BinaryTreeNode root) {
        int height = getHeight(root);
        int width = (int) Math.pow(2, height) - 1;

        String[][] grid = new String[height][width];

        // 初始化网格
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                grid[i][j] = " ";
            }
        }

        // 填充网格
        fillGrid(root, grid, 0, 0, width - 1);

        // 打印网格
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                System.out.print(grid[i][j]);
            }
            System.out.println();
        }
    }

    private static void fillGrid(BinaryTreeNode node, String[][] grid,
                                int level, int left, int right) {
        if (node == null || level >= grid.length) {
            return;
        }

        int mid = (left + right) / 2;
        grid[level][mid] = String.valueOf(node.data);

        fillGrid(node.left, grid, level + 1, left, mid - 1);
        fillGrid(node.right, grid, level + 1, mid + 1, right);
    }

    private static int getHeight(BinaryTreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + Math.max(getHeight(node.left), getHeight(node.right));
    }
}
```

### 9.2 树的统计信息

```java
public class TreeStatistics {
    public static class TreeStats {
        int nodeCount;
        int leafCount;
        int internalNodeCount;
        int height;
        int maxDegree;

        @Override
        public String toString() {
            return String.format(
                "节点总数: %d\n叶子节点数: %d\n内部节点数: %d\n树高度: %d\n最大度数: %d",
                nodeCount, leafCount, internalNodeCount, height, maxDegree
            );
        }
    }

    public static TreeStats analyzeTree(BinaryTreeNode root) {
        TreeStats stats = new TreeStats();

        if (root == null) {
            return stats;
        }

        stats.nodeCount = countNodes(root);
        stats.leafCount = countLeaves(root);
        stats.internalNodeCount = stats.nodeCount - stats.leafCount;
        stats.height = getHeight(root);
        stats.maxDegree = getMaxDegree(root);

        return stats;
    }

    private static int countNodes(BinaryTreeNode node) {
        if (node == null) return 0;
        return 1 + countNodes(node.left) + countNodes(node.right);
    }

    private static int countLeaves(BinaryTreeNode node) {
        if (node == null) return 0;
        if (node.left == null && node.right == null) return 1;
        return countLeaves(node.left) + countLeaves(node.right);
    }

    private static int getHeight(BinaryTreeNode node) {
        if (node == null) return 0;
        return 1 + Math.max(getHeight(node.left), getHeight(node.right));
    }

    private static int getMaxDegree(BinaryTreeNode node) {
        if (node == null) return 0;

        int degree = 0;
        if (node.left != null) degree++;
        if (node.right != null) degree++;

        int leftMaxDegree = getMaxDegree(node.left);
        int rightMaxDegree = getMaxDegree(node.right);

        return Math.max(degree, Math.max(leftMaxDegree, rightMaxDegree));
    }
}
```

## 10. 总结

树是计算机科学中最重要的数据结构之一，它以其层次化的特点为各种算法和应用提供了强大的支持。通过本文的学习，我们深入了解了：

### 核心概念
- 树的基本术语和特性
- 不同类型的树结构及其特点
- 树的遍历算法和实现方式

### 实践技能
- 二叉搜索树的完整实现
- 平衡树的旋转操作
- 树的可视化和统计分析

### 应用场景
- 文件系统和目录结构
- 数据库索引和B树
- 表达式解析和决策树
- 字符串搜索和前缀匹配

### 性能特点
- 平均情况下的高效查找：O(log n)
- 通过平衡技术保证最坏情况性能
- 在有序数据处理中的优势

树结构的美妙之处在于它完美地平衡了效率和简洁性。无论是在系统设计还是算法实现中，掌握树的概念和操作都是每个程序员必备的基本功。继续探索和实践，你会发现树在解决复杂问题中的巨大威力。

在下一篇文章中，我们将探讨图(Graph)这一更加复杂和强大的数据结构，它将树的概念进一步扩展，为我们打开一个全新的数据世界。

---

*本文是《数据结构入门教程》系列的第六篇，完整的代码示例可以在项目的GitHub仓库中找到。*