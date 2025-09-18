---
title: "设计模式入门教程22：迭代器模式 - 优雅地遍历集合元素"
date: 2024-12-22T10:22:00+08:00
draft: false
tags: ["设计模式", "迭代器模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是迭代器模式？

迭代器模式（Iterator Pattern）是一种行为型设计模式，它提供一种方法来顺序访问聚合对象中的各个元素，而不需要暴露该对象的内部表示。迭代器模式将遍历算法从集合类中分离出来，使得遍历算法可以独立于集合而变化。

### 🌟 现实生活中的例子

想象一下**电视遥控器的频道切换**：
- **遥控器**：作为迭代器，提供"上一个"、"下一个"频道功能
- **电视**：内部有频道列表，但不需要知道遥控器如何切换
- **统一接口**：无论是按钮遥控器还是语音遥控器，切换频道的方式是一致的

又比如**图书馆的书籍浏览**：
- **书架**：存储书籍的集合
- **索引卡片**：提供按作者、按主题、按时间等不同遍历方式
- **读者**：通过索引卡片找书，不需要知道书架的具体结构

这就是迭代器模式的精髓！

## 🏗️ 模式结构

```java
// 迭代器接口
interface Iterator<T> {
    boolean hasNext();
    T next();
    void remove(); // 可选操作
}

// 聚合接口
interface Iterable<T> {
    Iterator<T> createIterator();
}

// 具体迭代器
class ConcreteIterator<T> implements Iterator<T> {
    private List<T> items;
    private int position = 0;

    public ConcreteIterator(List<T> items) {
        this.items = items;
    }

    @Override
    public boolean hasNext() {
        return position < items.size();
    }

    @Override
    public T next() {
        if (hasNext()) {
            return items.get(position++);
        }
        throw new NoSuchElementException();
    }

    @Override
    public void remove() {
        if (position > 0) {
            items.remove(--position);
        }
    }
}

// 具体聚合
class ConcreteAggregate<T> implements Iterable<T> {
    private List<T> items = new ArrayList<>();

    public void addItem(T item) {
        items.add(item);
    }

    @Override
    public Iterator<T> createIterator() {
        return new ConcreteIterator<>(items);
    }
}
```

## 💡 核心组件详解

### 1. 迭代器接口（Iterator）
```java
// 增强的迭代器接口
interface EnhancedIterator<T> {
    // 基本遍历操作
    boolean hasNext();
    T next();

    // 反向遍历
    boolean hasPrevious();
    T previous();

    // 位置操作
    int nextIndex();
    int previousIndex();

    // 修改操作
    void remove();
    void set(T element);
    void add(T element);

    // 重置操作
    void reset();
}
```

### 2. 具体迭代器（ConcreteIterator）
```java
// 双向链表迭代器
class DoublyLinkedListIterator<T> implements EnhancedIterator<T> {
    private DoublyLinkedList<T> list;
    private Node<T> current;
    private Node<T> lastReturned;
    private int currentIndex;

    public DoublyLinkedListIterator(DoublyLinkedList<T> list) {
        this.list = list;
        this.current = list.getHead();
        this.lastReturned = null;
        this.currentIndex = 0;
    }

    @Override
    public boolean hasNext() {
        return current != null;
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException("没有下一个元素");
        }

        lastReturned = current;
        T data = current.getData();
        current = current.getNext();
        currentIndex++;

        System.out.println("迭代到元素：" + data + " (位置: " + (currentIndex - 1) + ")");
        return data;
    }

    @Override
    public boolean hasPrevious() {
        return currentIndex > 0;
    }

    @Override
    public T previous() {
        if (!hasPrevious()) {
            throw new NoSuchElementException("没有前一个元素");
        }

        if (current == null) {
            current = list.getTail();
        } else {
            current = current.getPrevious();
        }

        currentIndex--;
        lastReturned = current;

        T data = current.getData();
        System.out.println("反向迭代到元素：" + data + " (位置: " + currentIndex + ")");
        return data;
    }

    @Override
    public int nextIndex() {
        return currentIndex;
    }

    @Override
    public int previousIndex() {
        return currentIndex - 1;
    }

    @Override
    public void remove() {
        if (lastReturned == null) {
            throw new IllegalStateException("无法删除：没有调用next()或previous()");
        }

        Node<T> toRemove = lastReturned;

        if (toRemove == current) {
            current = current.getNext();
        } else {
            currentIndex--;
        }

        list.removeNode(toRemove);
        lastReturned = null;

        System.out.println("删除元素：" + toRemove.getData());
    }

    @Override
    public void set(T element) {
        if (lastReturned == null) {
            throw new IllegalStateException("无法设置：没有调用next()或previous()");
        }

        T oldData = lastReturned.getData();
        lastReturned.setData(element);

        System.out.println("设置元素：" + oldData + " -> " + element);
    }

    @Override
    public void add(T element) {
        Node<T> newNode = new Node<>(element);

        if (current == null) {
            // 在末尾添加
            list.append(element);
        } else {
            // 在当前位置前添加
            list.insertBefore(current, element);
        }

        currentIndex++;
        lastReturned = null;

        System.out.println("添加元素：" + element + " (位置: " + (currentIndex - 1) + ")");
    }

    @Override
    public void reset() {
        current = list.getHead();
        lastReturned = null;
        currentIndex = 0;
        System.out.println("迭代器已重置");
    }
}

// 数组迭代器
class ArrayIterator<T> implements EnhancedIterator<T> {
    private T[] array;
    private int currentIndex;
    private int lastReturnedIndex;
    private final int size;

    public ArrayIterator(T[] array) {
        this.array = array;
        this.currentIndex = 0;
        this.lastReturnedIndex = -1;
        this.size = array.length;
    }

    @Override
    public boolean hasNext() {
        return currentIndex < size;
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        lastReturnedIndex = currentIndex;
        T element = array[currentIndex++];

        System.out.println("迭代到数组元素：" + element + " [" + lastReturnedIndex + "]");
        return element;
    }

    @Override
    public boolean hasPrevious() {
        return currentIndex > 0;
    }

    @Override
    public T previous() {
        if (!hasPrevious()) {
            throw new NoSuchElementException();
        }

        lastReturnedIndex = --currentIndex;
        T element = array[currentIndex];

        System.out.println("反向迭代到数组元素：" + element + " [" + currentIndex + "]");
        return element;
    }

    @Override
    public int nextIndex() {
        return currentIndex;
    }

    @Override
    public int previousIndex() {
        return currentIndex - 1;
    }

    @Override
    public void remove() {
        if (lastReturnedIndex < 0) {
            throw new IllegalStateException();
        }

        // 数组删除需要移动元素
        System.arraycopy(array, lastReturnedIndex + 1, array, lastReturnedIndex,
                        size - lastReturnedIndex - 1);
        array[size - 1] = null;

        if (lastReturnedIndex < currentIndex) {
            currentIndex--;
        }

        lastReturnedIndex = -1;
        System.out.println("删除数组元素 [" + lastReturnedIndex + "]");
    }

    @Override
    public void set(T element) {
        if (lastReturnedIndex < 0) {
            throw new IllegalStateException();
        }

        T oldElement = array[lastReturnedIndex];
        array[lastReturnedIndex] = element;

        System.out.println("设置数组元素：" + oldElement + " -> " + element);
    }

    @Override
    public void add(T element) {
        throw new UnsupportedOperationException("数组迭代器不支持add操作");
    }

    @Override
    public void reset() {
        currentIndex = 0;
        lastReturnedIndex = -1;
        System.out.println("数组迭代器已重置");
    }
}

// 过滤迭代器
class FilterIterator<T> implements Iterator<T> {
    private Iterator<T> iterator;
    private Predicate<T> filter;
    private T nextElement;
    private boolean hasNextElement;

    public FilterIterator(Iterator<T> iterator, Predicate<T> filter) {
        this.iterator = iterator;
        this.filter = filter;
        findNext();
    }

    private void findNext() {
        hasNextElement = false;
        while (iterator.hasNext()) {
            T element = iterator.next();
            if (filter.test(element)) {
                nextElement = element;
                hasNextElement = true;
                break;
            }
        }
    }

    @Override
    public boolean hasNext() {
        return hasNextElement;
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        T current = nextElement;
        findNext();

        System.out.println("过滤迭代到：" + current);
        return current;
    }

    @Override
    public void remove() {
        iterator.remove();
    }
}
```

### 3. 聚合接口（Aggregate）
```java
// 增强的聚合接口
interface EnhancedIterable<T> {
    // 基本迭代器
    EnhancedIterator<T> iterator();

    // 反向迭代器
    EnhancedIterator<T> reverseIterator();

    // 过滤迭代器
    Iterator<T> filterIterator(Predicate<T> filter);

    // 范围迭代器
    Iterator<T> rangeIterator(int fromIndex, int toIndex);

    // 并行迭代器（简化版）
    Stream<T> parallelStream();

    // 基本操作
    void add(T element);
    boolean remove(T element);
    int size();
    boolean isEmpty();
}
```

### 4. 具体聚合（ConcreteAggregate）
```java
// 双向链表节点
class Node<T> {
    private T data;
    private Node<T> next;
    private Node<T> previous;

    public Node(T data) {
        this.data = data;
    }

    // Getters and Setters
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    public Node<T> getNext() { return next; }
    public void setNext(Node<T> next) { this.next = next; }
    public Node<T> getPrevious() { return previous; }
    public void setPrevious(Node<T> previous) { this.previous = previous; }
}

// 双向链表实现
class DoublyLinkedList<T> implements EnhancedIterable<T> {
    private Node<T> head;
    private Node<T> tail;
    private int size;

    public DoublyLinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }

    @Override
    public void add(T element) {
        append(element);
    }

    public void append(T data) {
        Node<T> newNode = new Node<>(data);

        if (head == null) {
            head = tail = newNode;
        } else {
            tail.setNext(newNode);
            newNode.setPrevious(tail);
            tail = newNode;
        }

        size++;
        System.out.println("添加元素：" + data + " (总数: " + size + ")");
    }

    public void prepend(T data) {
        Node<T> newNode = new Node<>(data);

        if (head == null) {
            head = tail = newNode;
        } else {
            newNode.setNext(head);
            head.setPrevious(newNode);
            head = newNode;
        }

        size++;
        System.out.println("前置添加元素：" + data);
    }

    public void insertBefore(Node<T> target, T data) {
        if (target == null) return;

        Node<T> newNode = new Node<>(data);
        Node<T> prev = target.getPrevious();

        newNode.setNext(target);
        newNode.setPrevious(prev);
        target.setPrevious(newNode);

        if (prev != null) {
            prev.setNext(newNode);
        } else {
            head = newNode;
        }

        size++;
    }

    @Override
    public boolean remove(T element) {
        Node<T> current = head;

        while (current != null) {
            if (Objects.equals(current.getData(), element)) {
                removeNode(current);
                return true;
            }
            current = current.getNext();
        }

        return false;
    }

    public void removeNode(Node<T> node) {
        if (node == null) return;

        Node<T> prev = node.getPrevious();
        Node<T> next = node.getNext();

        if (prev != null) {
            prev.setNext(next);
        } else {
            head = next;
        }

        if (next != null) {
            next.setPrevious(prev);
        } else {
            tail = prev;
        }

        size--;
        System.out.println("删除节点：" + node.getData() + " (剩余: " + size + ")");
    }

    @Override
    public EnhancedIterator<T> iterator() {
        return new DoublyLinkedListIterator<>(this);
    }

    @Override
    public EnhancedIterator<T> reverseIterator() {
        return new ReverseDoublyLinkedListIterator<>(this);
    }

    @Override
    public Iterator<T> filterIterator(Predicate<T> filter) {
        return new FilterIterator<>(iterator(), filter);
    }

    @Override
    public Iterator<T> rangeIterator(int fromIndex, int toIndex) {
        return new RangeIterator<>(this, fromIndex, toIndex);
    }

    @Override
    public Stream<T> parallelStream() {
        List<T> list = new ArrayList<>();
        Node<T> current = head;
        while (current != null) {
            list.add(current.getData());
            current = current.getNext();
        }
        return list.parallelStream();
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public boolean isEmpty() {
        return size == 0;
    }

    // 辅助方法
    public Node<T> getHead() { return head; }
    public Node<T> getTail() { return tail; }

    public void display() {
        System.out.println("=== 链表内容 ===");
        Node<T> current = head;
        int index = 0;
        while (current != null) {
            System.out.println(index + ": " + current.getData());
            current = current.getNext();
            index++;
        }
        System.out.println("总数: " + size);
        System.out.println("===============");
    }
}

// 反向迭代器
class ReverseDoublyLinkedListIterator<T> implements EnhancedIterator<T> {
    private DoublyLinkedList<T> list;
    private Node<T> current;
    private Node<T> lastReturned;
    private int currentIndex;

    public ReverseDoublyLinkedListIterator(DoublyLinkedList<T> list) {
        this.list = list;
        this.current = list.getTail();
        this.lastReturned = null;
        this.currentIndex = list.size() - 1;
    }

    @Override
    public boolean hasNext() {
        return current != null;
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        lastReturned = current;
        T data = current.getData();
        current = current.getPrevious();
        currentIndex--;

        System.out.println("反向迭代到：" + data + " (位置: " + (currentIndex + 1) + ")");
        return data;
    }

    @Override
    public boolean hasPrevious() {
        return currentIndex < list.size() - 1;
    }

    @Override
    public T previous() {
        if (!hasPrevious()) {
            throw new NoSuchElementException();
        }

        if (current == null) {
            current = list.getHead();
        } else {
            current = current.getNext();
        }

        currentIndex++;
        lastReturned = current;

        T data = current.getData();
        System.out.println("反向迭代器前进到：" + data);
        return data;
    }

    @Override
    public int nextIndex() {
        return currentIndex;
    }

    @Override
    public int previousIndex() {
        return currentIndex + 1;
    }

    @Override
    public void remove() {
        if (lastReturned == null) {
            throw new IllegalStateException();
        }

        Node<T> toRemove = lastReturned;

        if (toRemove == current) {
            current = current.getPrevious();
        } else {
            currentIndex++;
        }

        list.removeNode(toRemove);
        lastReturned = null;
    }

    @Override
    public void set(T element) {
        if (lastReturned == null) {
            throw new IllegalStateException();
        }

        lastReturned.setData(element);
    }

    @Override
    public void add(T element) {
        // 反向迭代器的add操作比较复杂，这里简化实现
        throw new UnsupportedOperationException("反向迭代器不支持add操作");
    }

    @Override
    public void reset() {
        current = list.getTail();
        lastReturned = null;
        currentIndex = list.size() - 1;
        System.out.println("反向迭代器已重置");
    }
}

// 范围迭代器
class RangeIterator<T> implements Iterator<T> {
    private DoublyLinkedList<T> list;
    private Node<T> current;
    private int currentIndex;
    private final int endIndex;

    public RangeIterator(DoublyLinkedList<T> list, int fromIndex, int toIndex) {
        this.list = list;
        this.endIndex = Math.min(toIndex, list.size());
        this.currentIndex = Math.max(0, fromIndex);

        // 移动到起始位置
        this.current = list.getHead();
        for (int i = 0; i < currentIndex && current != null; i++) {
            current = current.getNext();
        }

        System.out.println("范围迭代器：[" + fromIndex + ", " + endIndex + ")");
    }

    @Override
    public boolean hasNext() {
        return current != null && currentIndex < endIndex;
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        T data = current.getData();
        current = current.getNext();
        currentIndex++;

        System.out.println("范围迭代到：" + data + " (位置: " + (currentIndex - 1) + ")");
        return data;
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("范围迭代器不支持remove操作");
    }
}
```

## 🎮 实际应用示例

### 示例1：音乐播放列表管理
```java
// 歌曲类
class Song {
    private String title;
    private String artist;
    private String album;
    private int duration; // 秒
    private String genre;

    public Song(String title, String artist, String album, int duration, String genre) {
        this.title = title;
        this.artist = artist;
        this.album = album;
        this.duration = duration;
        this.genre = genre;
    }

    @Override
    public String toString() {
        return title + " - " + artist + " (" + formatDuration(duration) + ")";
    }

    private String formatDuration(int seconds) {
        int minutes = seconds / 60;
        int secs = seconds % 60;
        return String.format("%d:%02d", minutes, secs);
    }

    // Getters
    public String getTitle() { return title; }
    public String getArtist() { return artist; }
    public String getAlbum() { return album; }
    public int getDuration() { return duration; }
    public String getGenre() { return genre; }
}

// 播放模式枚举
enum PlayMode {
    SEQUENTIAL,  // 顺序播放
    SHUFFLE,     // 随机播放
    REPEAT_ONE,  // 单曲循环
    REPEAT_ALL   // 列表循环
}

// 播放列表迭代器接口
interface PlaylistIterator extends Iterator<Song> {
    void setPlayMode(PlayMode mode);
    PlayMode getPlayMode();
    Song getCurrentSong();
    void reset();
    boolean hasPrevious();
    Song previous();
}

// 顺序播放迭代器
class SequentialPlaylistIterator implements PlaylistIterator {
    private List<Song> playlist;
    private int currentIndex;
    private PlayMode playMode;

    public SequentialPlaylistIterator(List<Song> playlist) {
        this.playlist = new ArrayList<>(playlist);
        this.currentIndex = 0;
        this.playMode = PlayMode.SEQUENTIAL;
    }

    @Override
    public boolean hasNext() {
        switch (playMode) {
            case SEQUENTIAL:
                return currentIndex < playlist.size();
            case REPEAT_ALL:
                return !playlist.isEmpty();
            case REPEAT_ONE:
                return currentIndex < playlist.size();
            default:
                return currentIndex < playlist.size();
        }
    }

    @Override
    public Song next() {
        if (playlist.isEmpty()) {
            throw new NoSuchElementException("播放列表为空");
        }

        Song song;
        switch (playMode) {
            case SEQUENTIAL:
                if (currentIndex >= playlist.size()) {
                    throw new NoSuchElementException("播放列表已结束");
                }
                song = playlist.get(currentIndex++);
                break;

            case REPEAT_ALL:
                if (currentIndex >= playlist.size()) {
                    currentIndex = 0; // 循环到开始
                }
                song = playlist.get(currentIndex++);
                break;

            case REPEAT_ONE:
                if (currentIndex < playlist.size()) {
                    song = playlist.get(currentIndex);
                    // 单曲循环不增加索引
                } else {
                    throw new NoSuchElementException("播放列表已结束");
                }
                break;

            default:
                song = playlist.get(currentIndex++);
        }

        System.out.println("播放下一首：" + song);
        return song;
    }

    @Override
    public boolean hasPrevious() {
        return currentIndex > 0 || playMode == PlayMode.REPEAT_ALL;
    }

    @Override
    public Song previous() {
        if (playlist.isEmpty()) {
            throw new NoSuchElementException("播放列表为空");
        }

        Song song;
        switch (playMode) {
            case SEQUENTIAL:
                if (currentIndex <= 0) {
                    throw new NoSuchElementException("已是第一首");
                }
                song = playlist.get(--currentIndex);
                break;

            case REPEAT_ALL:
                if (currentIndex <= 0) {
                    currentIndex = playlist.size();
                }
                song = playlist.get(--currentIndex);
                break;

            case REPEAT_ONE:
                song = playlist.get(currentIndex);
                break;

            default:
                song = playlist.get(--currentIndex);
        }

        System.out.println("播放上一首：" + song);
        return song;
    }

    @Override
    public void setPlayMode(PlayMode mode) {
        this.playMode = mode;
        System.out.println("播放模式切换为：" + mode);
    }

    @Override
    public PlayMode getPlayMode() {
        return playMode;
    }

    @Override
    public Song getCurrentSong() {
        if (currentIndex > 0 && currentIndex <= playlist.size()) {
            return playlist.get(currentIndex - 1);
        }
        return null;
    }

    @Override
    public void reset() {
        currentIndex = 0;
        System.out.println("播放位置已重置");
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("播放时不支持删除歌曲");
    }
}

// 随机播放迭代器
class ShufflePlaylistIterator implements PlaylistIterator {
    private List<Song> playlist;
    private List<Integer> shuffledIndices;
    private int currentPosition;
    private Random random;

    public ShufflePlaylistIterator(List<Song> playlist) {
        this.playlist = new ArrayList<>(playlist);
        this.random = new Random();
        shuffle();
    }

    private void shuffle() {
        shuffledIndices = new ArrayList<>();
        for (int i = 0; i < playlist.size(); i++) {
            shuffledIndices.add(i);
        }
        Collections.shuffle(shuffledIndices, random);
        currentPosition = 0;
        System.out.println("播放列表已随机打乱");
    }

    @Override
    public boolean hasNext() {
        return currentPosition < shuffledIndices.size();
    }

    @Override
    public Song next() {
        if (!hasNext()) {
            // 重新洗牌
            shuffle();
            if (!hasNext()) {
                throw new NoSuchElementException("播放列表为空");
            }
        }

        int songIndex = shuffledIndices.get(currentPosition++);
        Song song = playlist.get(songIndex);
        System.out.println("随机播放：" + song);
        return song;
    }

    @Override
    public boolean hasPrevious() {
        return currentPosition > 0;
    }

    @Override
    public Song previous() {
        if (!hasPrevious()) {
            throw new NoSuchElementException("没有上一首");
        }

        int songIndex = shuffledIndices.get(--currentPosition);
        Song song = playlist.get(songIndex);
        System.out.println("随机上一首：" + song);
        return song;
    }

    @Override
    public void setPlayMode(PlayMode mode) {
        if (mode != PlayMode.SHUFFLE) {
            throw new UnsupportedOperationException("随机迭代器只支持随机模式");
        }
    }

    @Override
    public PlayMode getPlayMode() {
        return PlayMode.SHUFFLE;
    }

    @Override
    public Song getCurrentSong() {
        if (currentPosition > 0 && currentPosition <= shuffledIndices.size()) {
            int songIndex = shuffledIndices.get(currentPosition - 1);
            return playlist.get(songIndex);
        }
        return null;
    }

    @Override
    public void reset() {
        shuffle();
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("随机播放时不支持删除");
    }
}

// 播放列表类
class Playlist implements Iterable<Song> {
    private String name;
    private List<Song> songs;
    private PlayMode defaultPlayMode;

    public Playlist(String name) {
        this.name = name;
        this.songs = new ArrayList<>();
        this.defaultPlayMode = PlayMode.SEQUENTIAL;
    }

    public void addSong(Song song) {
        songs.add(song);
        System.out.println("添加歌曲到播放列表 \"" + name + "\"：" + song);
    }

    public void removeSong(Song song) {
        if (songs.remove(song)) {
            System.out.println("从播放列表移除：" + song);
        }
    }

    public void removeSong(int index) {
        if (index >= 0 && index < songs.size()) {
            Song removed = songs.remove(index);
            System.out.println("从播放列表移除：" + removed);
        }
    }

    @Override
    public Iterator<Song> iterator() {
        return createIterator(defaultPlayMode);
    }

    public PlaylistIterator createIterator(PlayMode playMode) {
        switch (playMode) {
            case SHUFFLE:
                return new ShufflePlaylistIterator(songs);
            default:
                SequentialPlaylistIterator iterator = new SequentialPlaylistIterator(songs);
                iterator.setPlayMode(playMode);
                return iterator;
        }
    }

    // 按艺术家过滤
    public Iterator<Song> iteratorByArtist(String artist) {
        return songs.stream()
                .filter(song -> song.getArtist().equalsIgnoreCase(artist))
                .iterator();
    }

    // 按专辑过滤
    public Iterator<Song> iteratorByAlbum(String album) {
        return songs.stream()
                .filter(song -> song.getAlbum().equalsIgnoreCase(album))
                .iterator();
    }

    // 按风格过滤
    public Iterator<Song> iteratorByGenre(String genre) {
        return songs.stream()
                .filter(song -> song.getGenre().equalsIgnoreCase(genre))
                .iterator();
    }

    public void showPlaylist() {
        System.out.println("=== 播放列表：" + name + " ===");
        if (songs.isEmpty()) {
            System.out.println("播放列表为空");
        } else {
            for (int i = 0; i < songs.size(); i++) {
                System.out.println((i + 1) + ". " + songs.get(i));
            }
        }
        System.out.println("总计：" + songs.size() + " 首歌曲");
        System.out.println("=========================");
    }

    // Getters and Setters
    public String getName() { return name; }
    public void setDefaultPlayMode(PlayMode mode) { this.defaultPlayMode = mode; }
    public PlayMode getDefaultPlayMode() { return defaultPlayMode; }
    public int size() { return songs.size(); }
    public boolean isEmpty() { return songs.isEmpty(); }
}

// 音乐播放器
class MusicPlayer {
    private Playlist currentPlaylist;
    private PlaylistIterator iterator;
    private Song currentSong;
    private boolean isPlaying;

    public void loadPlaylist(Playlist playlist, PlayMode playMode) {
        this.currentPlaylist = playlist;
        this.iterator = playlist.createIterator(playMode);
        this.isPlaying = false;
        System.out.println("已加载播放列表：" + playlist.getName() + " (模式：" + playMode + ")");
    }

    public void play() {
        if (iterator != null && iterator.hasNext()) {
            currentSong = iterator.next();
            isPlaying = true;
            System.out.println("🎵 正在播放：" + currentSong);
        } else {
            System.out.println("没有歌曲可播放");
        }
    }

    public void playNext() {
        if (iterator != null && iterator.hasNext()) {
            currentSong = iterator.next();
            System.out.println("🎵 播放下一首：" + currentSong);
        } else {
            System.out.println("没有下一首歌曲");
            isPlaying = false;
        }
    }

    public void playPrevious() {
        if (iterator != null && iterator.hasPrevious()) {
            currentSong = iterator.previous();
            System.out.println("🎵 播放上一首：" + currentSong);
        } else {
            System.out.println("没有上一首歌曲");
        }
    }

    public void stop() {
        isPlaying = false;
        System.out.println("⏹️ 停止播放");
    }

    public void changePlayMode(PlayMode mode) {
        if (currentPlaylist != null) {
            iterator = currentPlaylist.createIterator(mode);
            System.out.println("播放模式已切换为：" + mode);
        }
    }

    public void showStatus() {
        System.out.println("=== 播放器状态 ===");
        System.out.println("当前歌曲：" + (currentSong != null ? currentSong : "无"));
        System.out.println("播放状态：" + (isPlaying ? "播放中" : "停止"));
        System.out.println("播放模式：" + (iterator != null ? iterator.getPlayMode() : "未设置"));
        System.out.println("================");
    }
}

// 使用示例
public class MusicPlayerExample {
    public static void main(String[] args) throws InterruptedException {
        // 创建播放列表
        Playlist myPlaylist = new Playlist("我的收藏");

        // 添加歌曲
        myPlaylist.addSong(new Song("夜曲", "周杰伦", "十一月的萧邦", 237, "流行"));
        myPlaylist.addSong(new Song("青花瓷", "周杰伦", "我很忙", 228, "中国风"));
        myPlaylist.addSong(new Song("稻香", "周杰伦", "魔杰座", 223, "流行"));
        myPlaylist.addSong(new Song("告白气球", "周杰伦", "周杰伦的床边故事", 203, "流行"));
        myPlaylist.addSong(new Song("晴天", "周杰伦", "叶惠美", 269, "流行"));

        myPlaylist.showPlaylist();

        // 创建音乐播放器
        MusicPlayer player = new MusicPlayer();

        // 顺序播放模式
        System.out.println("\n=== 顺序播放模式 ===");
        player.loadPlaylist(myPlaylist, PlayMode.SEQUENTIAL);
        player.play();
        Thread.sleep(1000);
        player.playNext();
        Thread.sleep(1000);
        player.playNext();
        Thread.sleep(1000);
        player.playPrevious();

        // 随机播放模式
        System.out.println("\n=== 随机播放模式 ===");
        player.changePlayMode(PlayMode.SHUFFLE);
        player.play();
        Thread.sleep(1000);
        player.playNext();
        Thread.sleep(1000);
        player.playNext();

        // 单曲循环模式
        System.out.println("\n=== 单曲循环模式 ===");
        player.changePlayMode(PlayMode.REPEAT_ONE);
        player.play();
        Thread.sleep(1000);
        player.playNext(); // 还是同一首
        Thread.sleep(1000);
        player.playNext(); // 还是同一首

        // 按艺术家过滤
        System.out.println("\n=== 按艺术家过滤 ===");
        Iterator<Song> artistIterator = myPlaylist.iteratorByArtist("周杰伦");
        while (artistIterator.hasNext()) {
            Song song = artistIterator.next();
            System.out.println("周杰伦的歌曲：" + song);
        }

        player.showStatus();
    }
}
```

### 示例2：文件系统目录遍历
```java
// 文件系统节点接口
interface FileSystemNode {
    String getName();
    long getSize();
    boolean isDirectory();
    Date getLastModified();
    String getPath();
}

// 文件类
class FileNode implements FileSystemNode {
    private String name;
    private long size;
    private Date lastModified;
    private String path;

    public FileNode(String name, long size, String path) {
        this.name = name;
        this.size = size;
        this.path = path;
        this.lastModified = new Date();
    }

    @Override
    public String getName() { return name; }

    @Override
    public long getSize() { return size; }

    @Override
    public boolean isDirectory() { return false; }

    @Override
    public Date getLastModified() { return lastModified; }

    @Override
    public String getPath() { return path; }

    @Override
    public String toString() {
        return "File: " + name + " (" + size + " bytes)";
    }
}

// 目录类
class DirectoryNode implements FileSystemNode, Iterable<FileSystemNode> {
    private String name;
    private String path;
    private List<FileSystemNode> children;
    private Date lastModified;

    public DirectoryNode(String name, String path) {
        this.name = name;
        this.path = path;
        this.children = new ArrayList<>();
        this.lastModified = new Date();
    }

    public void addChild(FileSystemNode child) {
        children.add(child);
        System.out.println("添加到目录 " + name + ": " + child.getName());
    }

    public void removeChild(FileSystemNode child) {
        children.remove(child);
    }

    @Override
    public String getName() { return name; }

    @Override
    public long getSize() {
        return children.stream()
                .mapToLong(FileSystemNode::getSize)
                .sum();
    }

    @Override
    public boolean isDirectory() { return true; }

    @Override
    public Date getLastModified() { return lastModified; }

    @Override
    public String getPath() { return path; }

    @Override
    public Iterator<FileSystemNode> iterator() {
        return new DirectoryIterator(children);
    }

    // 深度优先迭代器
    public Iterator<FileSystemNode> depthFirstIterator() {
        return new DepthFirstDirectoryIterator(this);
    }

    // 广度优先迭代器
    public Iterator<FileSystemNode> breadthFirstIterator() {
        return new BreadthFirstDirectoryIterator(this);
    }

    // 按类型过滤的迭代器
    public Iterator<FileSystemNode> fileOnlyIterator() {
        return new FilteredDirectoryIterator(this, node -> !node.isDirectory());
    }

    public Iterator<FileSystemNode> directoryOnlyIterator() {
        return new FilteredDirectoryIterator(this, FileSystemNode::isDirectory);
    }

    public List<FileSystemNode> getChildren() {
        return new ArrayList<>(children);
    }

    @Override
    public String toString() {
        return "Directory: " + name + " (" + children.size() + " items)";
    }
}

// 基础目录迭代器
class DirectoryIterator implements Iterator<FileSystemNode> {
    private List<FileSystemNode> nodes;
    private int currentIndex;

    public DirectoryIterator(List<FileSystemNode> nodes) {
        this.nodes = new ArrayList<>(nodes);
        this.currentIndex = 0;
    }

    @Override
    public boolean hasNext() {
        return currentIndex < nodes.size();
    }

    @Override
    public FileSystemNode next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        FileSystemNode node = nodes.get(currentIndex++);
        System.out.println("遍历到：" + node);
        return node;
    }

    @Override
    public void remove() {
        if (currentIndex > 0) {
            nodes.remove(--currentIndex);
        }
    }
}

// 深度优先迭代器
class DepthFirstDirectoryIterator implements Iterator<FileSystemNode> {
    private Stack<Iterator<FileSystemNode>> stack;
    private FileSystemNode nextNode;

    public DepthFirstDirectoryIterator(DirectoryNode root) {
        stack = new Stack<>();
        stack.push(Collections.singletonList(root).iterator());
        findNext();
    }

    private void findNext() {
        nextNode = null;

        while (!stack.isEmpty() && nextNode == null) {
            Iterator<FileSystemNode> current = stack.peek();

            if (current.hasNext()) {
                FileSystemNode node = current.next();
                nextNode = node;

                // 如果是目录，将其子节点压入栈
                if (node.isDirectory() && node instanceof DirectoryNode) {
                    DirectoryNode dir = (DirectoryNode) node;
                    if (!dir.getChildren().isEmpty()) {
                        stack.push(dir.iterator());
                    }
                }
            } else {
                stack.pop();
            }
        }
    }

    @Override
    public boolean hasNext() {
        return nextNode != null;
    }

    @Override
    public FileSystemNode next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        FileSystemNode current = nextNode;
        findNext();

        System.out.println("深度优先遍历：" + current);
        return current;
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("深度优先迭代器不支持删除");
    }
}

// 广度优先迭代器
class BreadthFirstDirectoryIterator implements Iterator<FileSystemNode> {
    private Queue<FileSystemNode> queue;

    public BreadthFirstDirectoryIterator(DirectoryNode root) {
        queue = new LinkedList<>();
        queue.offer(root);
    }

    @Override
    public boolean hasNext() {
        return !queue.isEmpty();
    }

    @Override
    public FileSystemNode next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        FileSystemNode node = queue.poll();

        // 如果是目录，将其子节点加入队列
        if (node.isDirectory() && node instanceof DirectoryNode) {
            DirectoryNode dir = (DirectoryNode) node;
            for (FileSystemNode child : dir.getChildren()) {
                queue.offer(child);
            }
        }

        System.out.println("广度优先遍历：" + node);
        return node;
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("广度优先迭代器不支持删除");
    }
}

// 过滤迭代器
class FilteredDirectoryIterator implements Iterator<FileSystemNode> {
    private Iterator<FileSystemNode> baseIterator;
    private Predicate<FileSystemNode> filter;
    private FileSystemNode nextNode;

    public FilteredDirectoryIterator(DirectoryNode root, Predicate<FileSystemNode> filter) {
        this.baseIterator = root.depthFirstIterator();
        this.filter = filter;
        findNext();
    }

    private void findNext() {
        nextNode = null;
        while (baseIterator.hasNext() && nextNode == null) {
            FileSystemNode candidate = baseIterator.next();
            if (filter.test(candidate)) {
                nextNode = candidate;
            }
        }
    }

    @Override
    public boolean hasNext() {
        return nextNode != null;
    }

    @Override
    public FileSystemNode next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }

        FileSystemNode current = nextNode;
        findNext();

        System.out.println("过滤遍历：" + current);
        return current;
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException("过滤迭代器不支持删除");
    }
}

// 文件系统使用示例
public class FileSystemExample {
    public static void main(String[] args) {
        // 构建文件系统结构
        DirectoryNode root = new DirectoryNode("root", "/");

        DirectoryNode documents = new DirectoryNode("documents", "/documents");
        DirectoryNode pictures = new DirectoryNode("pictures", "/pictures");
        DirectoryNode music = new DirectoryNode("music", "/music");

        // 添加文件
        documents.addChild(new FileNode("readme.txt", 1024, "/documents/readme.txt"));
        documents.addChild(new FileNode("report.pdf", 2048576, "/documents/report.pdf"));

        DirectoryNode projectDir = new DirectoryNode("project", "/documents/project");
        projectDir.addChild(new FileNode("main.java", 4096, "/documents/project/main.java"));
        projectDir.addChild(new FileNode("config.xml", 512, "/documents/project/config.xml"));
        documents.addChild(projectDir);

        pictures.addChild(new FileNode("vacation.jpg", 3145728, "/pictures/vacation.jpg"));
        pictures.addChild(new FileNode("family.png", 2097152, "/pictures/family.png"));

        music.addChild(new FileNode("song1.mp3", 5242880, "/music/song1.mp3"));
        music.addChild(new FileNode("song2.mp3", 4194304, "/music/song2.mp3"));

        root.addChild(documents);
        root.addChild(pictures);
        root.addChild(music);

        // 直接遍历根目录
        System.out.println("=== 直接遍历根目录 ===");
        for (FileSystemNode node : root) {
            System.out.println("- " + node);
        }

        // 深度优先遍历
        System.out.println("\n=== 深度优先遍历 ===");
        Iterator<FileSystemNode> dfsIterator = root.depthFirstIterator();
        while (dfsIterator.hasNext()) {
            FileSystemNode node = dfsIterator.next();
            String indent = "  ".repeat(node.getPath().split("/").length - 1);
            System.out.println(indent + "└─ " + node);
        }

        // 广度优先遍历
        System.out.println("\n=== 广度优先遍历 ===");
        Iterator<FileSystemNode> bfsIterator = root.breadthFirstIterator();
        while (bfsIterator.hasNext()) {
            bfsIterator.next();
        }

        // 只遍历文件
        System.out.println("\n=== 只遍历文件 ===");
        Iterator<FileSystemNode> fileIterator = root.fileOnlyIterator();
        while (fileIterator.hasNext()) {
            fileIterator.next();
        }

        // 只遍历目录
        System.out.println("\n=== 只遍历目录 ===");
        Iterator<FileSystemNode> dirIterator = root.directoryOnlyIterator();
        while (dirIterator.hasNext()) {
            dirIterator.next();
        }

        // 统计信息
        System.out.println("\n=== 统计信息 ===");
        System.out.println("根目录总大小：" + formatSize(root.getSize()));

        long totalFiles = 0;
        long totalDirs = 0;
        Iterator<FileSystemNode> allIterator = root.depthFirstIterator();
        while (allIterator.hasNext()) {
            FileSystemNode node = allIterator.next();
            if (node.isDirectory()) {
                totalDirs++;
            } else {
                totalFiles++;
            }
        }
        System.out.println("总文件数：" + totalFiles);
        System.out.println("总目录数：" + totalDirs);
    }

    private static String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024) + " KB";
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)) + " MB";
        return (bytes / (1024 * 1024 * 1024)) + " GB";
    }
}
```

## ✅ 优势分析

### 1. **统一接口**
为不同的聚合结构提供了统一的遍历接口。

### 2. **简化聚合类**
将遍历算法从聚合类中分离，简化了聚合类的接口。

### 3. **支持多种遍历**
可以为同一个聚合提供多种不同的遍历方式。

### 4. **符合单一职责原则**
遍历算法和聚合对象分别承担不同的职责。

## ⚠️ 注意事项

### 1. **迭代器失效**
```java
// 在迭代过程中修改集合可能导致迭代器失效
public class IteratorSafetyExample {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
        Iterator<String> iterator = list.iterator();

        while (iterator.hasNext()) {
            String item = iterator.next();
            if ("B".equals(item)) {
                // 正确的删除方式
                iterator.remove();
                // 错误的删除方式 - 会导致ConcurrentModificationException
                // list.remove(item);
            }
        }
    }
}
```

### 2. **内存泄漏**
长期持有迭代器引用可能导致内存泄漏。

### 3. **线程安全**
迭代器通常不是线程安全的，需要额外的同步措施。

## 🆚 与其他模式对比

| 特性 | 迭代器模式 | 组合模式 | 访问者模式 |
|------|----------|----------|-----------|
| 目的 | 遍历元素 | 组织结构 | 操作元素 |
| 关注点 | 访问顺序 | 整体部分 | 算法操作 |
| 扩展性 | 遍历算法 | 结构类型 | 操作类型 |
| 封装性 | 遍历逻辑 | 树形结构 | 访问逻辑 |

## 🎯 实战建议

### 1. **何时使用迭代器模式**
- 需要访问聚合对象的内容而不暴露其内部表示
- 需要支持多种遍历方式
- 需要为遍历不同的聚合结构提供统一接口
- 想要简化聚合接口

### 2. **设计原则**
```java
// 好的迭代器设计
public interface SafeIterator<T> extends Iterator<T> {
    // 提供状态检查
    boolean isValid();

    // 提供异常安全的操作
    Optional<T> tryNext();

    // 支持重置
    void reset();

    // 提供位置信息
    int getPosition();
}

// 支持并发的迭代器
public class ConcurrentSafeIterator<T> implements Iterator<T> {
    private final CopyOnWriteArrayList<T> snapshot;
    private int position = 0;

    public ConcurrentSafeIterator(List<T> original) {
        this.snapshot = new CopyOnWriteArrayList<>(original);
    }

    @Override
    public boolean hasNext() {
        return position < snapshot.size();
    }

    @Override
    public T next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        return snapshot.get(position++);
    }
}
```

### 3. **性能优化**
```java
// 延迟加载迭代器
class LazyIterator<T> implements Iterator<T> {
    private Supplier<Iterator<T>> iteratorSupplier;
    private Iterator<T> actualIterator;

    public LazyIterator(Supplier<Iterator<T>> supplier) {
        this.iteratorSupplier = supplier;
    }

    private void ensureIterator() {
        if (actualIterator == null) {
            actualIterator = iteratorSupplier.get();
        }
    }

    @Override
    public boolean hasNext() {
        ensureIterator();
        return actualIterator.hasNext();
    }

    @Override
    public T next() {
        ensureIterator();
        return actualIterator.next();
    }
}
```

## 🧠 记忆技巧

**口诀：迭代遍历统一口**
- **迭**代访问不暴露
- **代**理遍历算法层
- **遍**历方式可多样
- **历**程控制很灵活
- **统**一接口好使用
- **一**次一个顺序访
- **口**径清晰职责明

**形象比喻：**
迭代器模式就像**电视遥控器**：
- 遥控器（迭代器）提供统一的换台接口
- 电视（聚合对象）内部有频道列表
- 不管什么品牌的遥控器，换台操作都类似
- 可以有不同的遥控方式（按键、语音、手势）

## 🎉 总结

迭代器模式是一种实用的设计模式，它为我们提供了统一、灵活的集合遍历机制。通过将遍历算法从集合类中分离，我们获得了更好的封装性和可扩展性，同时简化了集合类的接口。

**核心思想：** 🔄 统一遍历接口，让集合访问更优雅，遍历方式更灵活！

下一篇我们将学习**解释器模式**，看看如何为语言创建解释器！ 🚀