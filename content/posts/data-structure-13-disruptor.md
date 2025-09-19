---
title: "剖析高性能队列Disruptor背后的数据结构和算法"
date: 2024-12-20T11:00:00+08:00
lastmod: 2024-12-20T11:00:00+08:00
draft: false
keywords: [Disruptor, 高性能队列, 无锁编程, 环形缓冲区, 内存屏障, LMAX, 数据结构]
description: "深入剖析LMAX Disruptor高性能队列框架的核心数据结构和算法，揭示其无锁设计、环形缓冲区、序列器等关键技术"
tags: [数据结构, 算法, Disruptor, 队列, 高性能, 无锁编程]
categories: [数据结构与算法]
author: "张三"
---

Disruptor是由LMAX交易所开发的一个高性能队列框架，能够在单线程中每秒处理600万订单。它通过巧妙的数据结构设计和无锁算法，实现了远超传统队列的性能。本文将深入剖析Disruptor背后的核心技术原理。

## Disruptor概述

### 传统队列的性能瓶颈

传统的队列实现（如ArrayBlockingQueue、LinkedBlockingQueue）存在以下性能问题：

1. **锁竞争**：多线程访问需要加锁，导致线程阻塞
2. **内存分配**：动态分配对象产生垃圾回收压力
3. **缓存失效**：数据结构不友好，导致CPU缓存命中率低
4. **伪共享**：多个线程修改同一缓存行的不同变量

### Disruptor的核心优势

Disruptor通过以下技术突破了传统队列的性能瓶颈：

1. **无锁设计**：使用CAS操作替代锁机制
2. **环形缓冲区**：预分配固定大小的数组，避免垃圾回收
3. **缓存友好**：优化内存布局，提高缓存命中率
4. **批量处理**：支持批量读取和处理事件
5. **等待策略**：多种等待策略适应不同场景

## 核心数据结构详解

### 1. 环形缓冲区（RingBuffer）

环形缓冲区是Disruptor的核心数据结构，使用数组实现固定大小的循环队列。

```java
public final class RingBuffer<E> implements Cursored, EventSequencer<E>, EventSink<E> {
    // 缓冲区大小必须是2的幂次方，便于使用位运算优化
    private final int bufferSize;
    private final int indexMask; // bufferSize - 1，用于位运算取模

    // 存储事件的数组
    private final Object[] entries;

    // 序列器，管理生产者序列
    private final Sequencer sequencer;

    // 事件工厂，用于创建事件对象
    private final EventFactory<E> eventFactory;

    public RingBuffer(EventFactory<E> eventFactory, Sequencer sequencer) {
        this.eventFactory = eventFactory;
        this.sequencer = sequencer;
        this.bufferSize = sequencer.getBufferSize();
        this.indexMask = bufferSize - 1;
        this.entries = new Object[sequencer.getBufferSize()];

        // 预填充所有位置，避免运行时分配对象
        fill(eventFactory);
    }

    // 预填充环形缓冲区
    private void fill(EventFactory<E> eventFactory) {
        for (int i = 0; i < bufferSize; i++) {
            entries[i] = eventFactory.newInstance();
        }
    }

    // 获取指定序列位置的事件（使用位运算优化）
    @SuppressWarnings("unchecked")
    protected final E elementAt(long sequence) {
        return (E) entries[(int) sequence & indexMask];
    }

    // 获取下一个可写入的序列号
    public long next() {
        return sequencer.next();
    }

    // 获取n个连续的序列号
    public long next(int n) {
        return sequencer.next(n);
    }

    // 发布事件，使其对消费者可见
    public void publish(long sequence) {
        sequencer.publish(sequence);
    }

    // 批量发布事件
    public void publish(long lo, long hi) {
        sequencer.publish(lo, hi);
    }

    // 获取当前可读取的最大序列号
    public long getCursor() {
        return sequencer.getCursor();
    }

    // 检查指定序列是否可用
    public boolean isAvailable(long sequence) {
        return sequencer.isAvailable(sequence);
    }

    // 添加网关序列（用于多消费者场景）
    public void addGatingSequences(Sequence... gatingSequences) {
        sequencer.addGatingSequences(gatingSequences);
    }

    // 获取最小的网关序列值
    public long getMinimumGatingSequence() {
        return sequencer.getMinimumGatingSequence();
    }

    // 移除网关序列
    public boolean removeGatingSequence(Sequence sequence) {
        return sequencer.removeGatingSequence(sequence);
    }

    // 创建屏障，用于消费者等待数据
    public SequenceBarrier newBarrier(Sequence... sequencesToTrack) {
        return sequencer.newBarrier(sequencesToTrack);
    }

    // 事件发布器，提供便捷的事件发布API
    public <A> void publishEvent(EventTranslator<E> translator) {
        long sequence = sequencer.next();
        translateAndPublish(translator, sequence);
    }

    public <A> void publishEvent(EventTranslatorOneArg<E, A> translator, A arg0) {
        long sequence = sequencer.next();
        translateAndPublish(translator, sequence, arg0);
    }

    // 事件转换和发布
    private <A> void translateAndPublish(EventTranslatorOneArg<E, A> translator,
                                        long sequence, A arg0) {
        try {
            translator.translateTo(elementAt(sequence), sequence, arg0);
        } finally {
            sequencer.publish(sequence);
        }
    }
}

// 事件工厂接口
public interface EventFactory<T> {
    T newInstance();
}

// 事件转换器接口
public interface EventTranslator<T> {
    void translateTo(T event, long sequence);
}

public interface EventTranslatorOneArg<T, A> {
    void translateTo(T event, long sequence, A arg0);
}
```

### 2. 序列器（Sequencer）

序列器负责管理生产者和消费者的序列，是Disruptor无锁设计的核心。

```java
// 单生产者序列器
public final class SingleProducerSequencer implements Sequencer {
    private final int bufferSize;
    private final WaitStrategy waitStrategy;

    // 当前生产者序列（使用volatile保证可见性）
    private volatile long cursor = Sequence.INITIAL_VALUE;

    // 网关序列数组，记录所有消费者的进度
    private volatile Sequence[] gatingSequences = new Sequence[0];

    // 缓存的网关序列最小值，避免重复计算
    private long cachedValue = Sequence.INITIAL_VALUE;
    private long nextValue = Sequence.INITIAL_VALUE;

    public SingleProducerSequencer(int bufferSize, WaitStrategy waitStrategy) {
        if (bufferSize < 1 || !isPowerOfTwo(bufferSize)) {
            throw new IllegalArgumentException("bufferSize must be a positive power of 2");
        }
        this.bufferSize = bufferSize;
        this.waitStrategy = waitStrategy;
    }

    @Override
    public long next() {
        return next(1);
    }

    @Override
    public long next(int n) {
        if (n < 1) {
            throw new IllegalArgumentException("n must be > 0");
        }

        long nextValue = this.nextValue;
        long nextSequence = nextValue + n;
        long wrapPoint = nextSequence - bufferSize;
        long cachedGatingSequence = this.cachedValue;

        // 检查是否会追上最慢的消费者
        if (wrapPoint > cachedGatingSequence || cachedGatingSequence > nextValue) {
            long minSequence;

            // 自旋等待，直到有足够的空间
            while (wrapPoint > (minSequence = getMinimumGatingSequence())) {
                LockSupport.parkNanos(1L); // 短暂停顿，避免CPU空转
            }

            this.cachedValue = minSequence;
        }

        this.nextValue = nextSequence;
        return nextSequence;
    }

    @Override
    public void publish(long sequence) {
        cursor = sequence;
        waitStrategy.signalAllWhenBlocking();
    }

    @Override
    public void publish(long lo, long hi) {
        publish(hi);
    }

    @Override
    public long getCursor() {
        return cursor;
    }

    @Override
    public boolean isAvailable(long sequence) {
        return sequence <= cursor;
    }

    @Override
    public long getMinimumGatingSequence() {
        Sequence[] gatingSequences = this.gatingSequences;
        long minimum = cursor;

        for (Sequence sequence : gatingSequences) {
            long value = sequence.get();
            minimum = Math.min(minimum, value);
        }

        return minimum;
    }

    // 添加消费者序列
    @Override
    public void addGatingSequences(Sequence... gatingSequences) {
        SequenceGroups.addSequences(this, SEQUENCE_UPDATER, this, gatingSequences);
    }

    // 移除消费者序列
    @Override
    public boolean removeGatingSequence(Sequence sequence) {
        return SequenceGroups.removeSequence(this, SEQUENCE_UPDATER, sequence);
    }

    // 创建序列屏障
    @Override
    public SequenceBarrier newBarrier(Sequence... sequencesToTrack) {
        return new ProcessingSequenceBarrier(this, waitStrategy, cursor, sequencesToTrack);
    }

    // 原子更新器，用于原子地更新gatingSequences数组
    private static final AtomicReferenceFieldUpdater<SingleProducerSequencer, Sequence[]> SEQUENCE_UPDATER =
            AtomicReferenceFieldUpdater.newUpdater(SingleProducerSequencer.class, Sequence[].class, "gatingSequences");

    private boolean isPowerOfTwo(int x) {
        return (x & (x - 1)) == 0;
    }
}

// 多生产者序列器
public final class MultiProducerSequencer implements Sequencer {
    private final int bufferSize;
    private final WaitStrategy waitStrategy;
    private volatile long cursor = Sequence.INITIAL_VALUE;
    private volatile Sequence[] gatingSequences = new Sequence[0];

    // 用于标记每个位置是否已发布的数组
    private final int[] availableBuffer;
    private final int indexMask;
    private final int indexShift;

    public MultiProducerSequencer(int bufferSize, WaitStrategy waitStrategy) {
        this.bufferSize = bufferSize;
        this.waitStrategy = waitStrategy;
        this.availableBuffer = new int[bufferSize];
        this.indexMask = bufferSize - 1;
        this.indexShift = log2(bufferSize);
        initializeAvailableBuffer();
    }

    private void initializeAvailableBuffer() {
        for (int i = availableBuffer.length - 1; i != 0; i--) {
            setAvailableBufferValue(i, -1);
        }
        setAvailableBufferValue(0, -1);
    }

    @Override
    public long next() {
        return next(1);
    }

    @Override
    public long next(int n) {
        if (n < 1) {
            throw new IllegalArgumentException("n must be > 0");
        }

        long current;
        long next;

        do {
            current = cursor;
            next = current + n;
            long wrapPoint = next - bufferSize;
            long cachedGatingSequence = getMinimumGatingSequence();

            if (wrapPoint > cachedGatingSequence) {
                LockSupport.parkNanos(1L);
                continue;
            }
        } while (!cursor.compareAndSet(current, next)); // CAS操作保证原子性

        return next;
    }

    @Override
    public void publish(long sequence) {
        setAvailable(sequence);
        waitStrategy.signalAllWhenBlocking();
    }

    @Override
    public void publish(long lo, long hi) {
        for (long l = lo; l <= hi; l++) {
            setAvailable(l);
        }
        waitStrategy.signalAllWhenBlocking();
    }

    private void setAvailable(final long sequence) {
        setAvailableBufferValue(calculateIndex(sequence), calculateAvailabilityFlag(sequence));
    }

    private void setAvailableBufferValue(int index, int flag) {
        long bufferAddress = (index * SCALE) + BASE;
        UNSAFE.putOrderedInt(availableBuffer, bufferAddress, flag);
    }

    @Override
    public boolean isAvailable(long sequence) {
        int index = calculateIndex(sequence);
        int flag = calculateAvailabilityFlag(sequence);
        long bufferAddress = (index * SCALE) + BASE;
        return UNSAFE.getIntVolatile(availableBuffer, bufferAddress) == flag;
    }

    private int calculateIndex(long sequence) {
        return ((int) sequence) & indexMask;
    }

    private int calculateAvailabilityFlag(long sequence) {
        return (int) (sequence >>> indexShift);
    }

    // Unsafe操作，用于直接操作内存
    private static final Unsafe UNSAFE;
    private static final long BASE;
    private static final long SCALE;

    static {
        try {
            UNSAFE = getUnsafe();
            BASE = UNSAFE.arrayBaseOffset(int[].class);
            SCALE = UNSAFE.arrayIndexScale(int[].class);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static Unsafe getUnsafe() {
        try {
            Field field = Unsafe.class.getDeclaredField("theUnsafe");
            field.setAccessible(true);
            return (Unsafe) field.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static int log2(int i) {
        int r = 0;
        while ((i >>= 1) != 0) {
            ++r;
        }
        return r;
    }
}
```

### 3. 序列（Sequence）

序列是Disruptor中用于跟踪进度的原子计数器，通过内存填充避免伪共享问题。

```java
// 避免伪共享的序列实现
public class Sequence extends RhsPadding {
    static final long INITIAL_VALUE = -1L;
    private static final Unsafe UNSAFE;
    private static final long VALUE_OFFSET;

    static {
        UNSAFE = getUnsafe();
        try {
            VALUE_OFFSET = UNSAFE.objectFieldOffset(Value.class.getDeclaredField("value"));
        } catch (final Exception e) {
            throw new RuntimeException(e);
        }
    }

    public Sequence() {
        this(INITIAL_VALUE);
    }

    public Sequence(final long initialValue) {
        UNSAFE.putOrderedLong(this, VALUE_OFFSET, initialValue);
    }

    // 获取当前值
    public long get() {
        return value;
    }

    // 设置值
    public void set(final long value) {
        UNSAFE.putOrderedLong(this, VALUE_OFFSET, value);
    }

    // 原子设置值
    public void setVolatile(final long value) {
        UNSAFE.putLongVolatile(this, VALUE_OFFSET, value);
    }

    // CAS操作
    public boolean compareAndSet(final long expectedValue, final long newValue) {
        return UNSAFE.compareAndSwapLong(this, VALUE_OFFSET, expectedValue, newValue);
    }

    // 原子增加
    public long incrementAndGet() {
        return addAndGet(1L);
    }

    // 原子增加指定值
    public long addAndGet(final long increment) {
        long currentValue;
        long newValue;

        do {
            currentValue = get();
            newValue = currentValue + increment;
        } while (!compareAndSet(currentValue, newValue));

        return newValue;
    }

    @Override
    public String toString() {
        return Long.toString(get());
    }

    private static Unsafe getUnsafe() {
        try {
            Field field = Unsafe.class.getDeclaredField("theUnsafe");
            field.setAccessible(true);
            return (Unsafe) field.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}

// 内存填充类，防止伪共享
class LhsPadding {
    protected long p1, p2, p3, p4, p5, p6, p7;
}

class Value extends LhsPadding {
    protected volatile long value;
}

class RhsPadding extends Value {
    protected long p9, p10, p11, p12, p13, p14, p15;
}
```

### 4. 等待策略（WaitStrategy）

不同的等待策略适应不同的性能需求和延迟要求。

```java
// 等待策略接口
public interface WaitStrategy {
    // 等待序列可用
    long waitFor(long sequence, Sequence cursor, Sequence dependentSequence,
                 SequenceBarrier barrier) throws AlertException, InterruptedException;

    // 唤醒所有等待的线程
    void signalAllWhenBlocking();
}

// 阻塞等待策略（延迟最低，CPU使用率最高）
public final class BlockingWaitStrategy implements WaitStrategy {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition processorNotifyCondition = lock.newCondition();

    @Override
    public long waitFor(long sequence, Sequence cursor, Sequence dependentSequence,
                        SequenceBarrier barrier) throws AlertException, InterruptedException {
        long availableSequence;

        if (cursor.get() < sequence) {
            lock.lock();
            try {
                while (cursor.get() < sequence) {
                    barrier.checkAlert();
                    processorNotifyCondition.await();
                }
            } finally {
                lock.unlock();
            }
        }

        while ((availableSequence = dependentSequence.get()) < sequence) {
            barrier.checkAlert();
        }

        return availableSequence;
    }

    @Override
    public void signalAllWhenBlocking() {
        lock.lock();
        try {
            processorNotifyCondition.signalAll();
        } finally {
            lock.unlock();
        }
    }
}

// 忙等待策略（延迟最低，CPU使用率最高）
public final class BusySpinWaitStrategy implements WaitStrategy {
    @Override
    public long waitFor(final long sequence, Sequence cursor, final Sequence dependentSequence,
                        final SequenceBarrier barrier) throws AlertException, InterruptedException {
        long availableSequence;

        while ((availableSequence = dependentSequence.get()) < sequence) {
            barrier.checkAlert();
            // 自旋等待，不进行任何操作
        }

        return availableSequence;
    }

    @Override
    public void signalAllWhenBlocking() {
        // 忙等待策略无需信号通知
    }
}

// 让步等待策略（平衡延迟和CPU使用率）
public final class YieldingWaitStrategy implements WaitStrategy {
    private static final int SPIN_TRIES = 100;

    @Override
    public long waitFor(final long sequence, Sequence cursor, final Sequence dependentSequence,
                        final SequenceBarrier barrier) throws AlertException, InterruptedException {
        long availableSequence;
        int counter = SPIN_TRIES;

        while ((availableSequence = dependentSequence.get()) < sequence) {
            counter = applyWaitMethod(barrier, counter);
        }

        return availableSequence;
    }

    private int applyWaitMethod(final SequenceBarrier barrier, int counter)
            throws AlertException {
        barrier.checkAlert();

        if (0 == counter) {
            Thread.yield(); // 让出CPU时间片
        } else {
            --counter;
        }

        return counter;
    }

    @Override
    public void signalAllWhenBlocking() {
        // 让步策略无需信号通知
    }
}

// 睡眠等待策略（延迟较高，CPU使用率低）
public final class SleepingWaitStrategy implements WaitStrategy {
    private static final int DEFAULT_RETRIES = 200;
    private static final long DEFAULT_SLEEP = 100;

    private final int retries;
    private final long sleepTimeNs;

    public SleepingWaitStrategy() {
        this(DEFAULT_RETRIES, DEFAULT_SLEEP);
    }

    public SleepingWaitStrategy(int retries, long sleepTimeNs) {
        this.retries = retries;
        this.sleepTimeNs = sleepTimeNs;
    }

    @Override
    public long waitFor(final long sequence, Sequence cursor, final Sequence dependentSequence,
                        final SequenceBarrier barrier) throws AlertException, InterruptedException {
        long availableSequence;
        int counter = retries;

        while ((availableSequence = dependentSequence.get()) < sequence) {
            counter = applyWaitMethod(barrier, counter);
        }

        return availableSequence;
    }

    private int applyWaitMethod(final SequenceBarrier barrier, int counter)
            throws AlertException {
        barrier.checkAlert();

        if (counter > 100) {
            --counter;
        } else if (counter > 0) {
            --counter;
            Thread.yield();
        } else {
            LockSupport.parkNanos(sleepTimeNs);
        }

        return counter;
    }

    @Override
    public void signalAllWhenBlocking() {
        // 睡眠策略无需信号通知
    }
}
```

## 事件处理器设计

### 1. 事件处理器接口

```java
// 事件处理器接口
public interface EventProcessor extends Runnable {
    // 获取处理器的序列
    Sequence getSequence();

    // 停止处理器
    void halt();

    // 检查处理器是否正在运行
    boolean isRunning();
}

// 批量事件处理器
public final class BatchEventProcessor<T> implements EventProcessor {
    private static final int IDLE = 0;
    private static final int HALTED = IDLE + 1;
    private static final int RUNNING = HALTED + 1;

    private final AtomicInteger running = new AtomicInteger(IDLE);
    private ExceptionHandler<? super T> exceptionHandler;

    private final DataProvider<T> dataProvider;
    private final SequenceBarrier sequenceBarrier;
    private final EventHandler<T> eventHandler;
    private final Sequence sequence = new Sequence(Sequence.INITIAL_VALUE);
    private final TimeoutHandler timeoutHandler;

    public BatchEventProcessor(DataProvider<T> dataProvider,
                              SequenceBarrier sequenceBarrier,
                              EventHandler<T> eventHandler) {
        this.dataProvider = dataProvider;
        this.sequenceBarrier = sequenceBarrier;
        this.eventHandler = eventHandler;

        if (eventHandler instanceof SequenceReportingEventHandler) {
            ((SequenceReportingEventHandler<?>) eventHandler).setSequenceCallback(sequence);
        }

        timeoutHandler = (eventHandler instanceof TimeoutHandler) ?
                        (TimeoutHandler) eventHandler : null;
    }

    @Override
    public Sequence getSequence() {
        return sequence;
    }

    @Override
    public void halt() {
        running.set(HALTED);
        sequenceBarrier.alert();
    }

    @Override
    public boolean isRunning() {
        return running.get() != IDLE;
    }

    @Override
    public void run() {
        if (running.compareAndSet(IDLE, RUNNING)) {
            sequenceBarrier.clearAlert();

            notifyStart();
            try {
                if (running.get() == RUNNING) {
                    processEvents();
                }
            } finally {
                notifyShutdown();
                running.set(IDLE);
            }
        } else {
            if (running.get() == RUNNING) {
                throw new IllegalStateException("Thread is already running");
            } else {
                earlyExit();
            }
        }
    }

    private void processEvents() {
        T event = null;
        long nextSequence = sequence.get() + 1L;

        while (true) {
            try {
                final long availableSequence = sequenceBarrier.waitFor(nextSequence);

                if (batchStartAware != null) {
                    batchStartAware.onBatchStart(availableSequence - nextSequence + 1);
                }

                while (nextSequence <= availableSequence) {
                    event = dataProvider.get(nextSequence);
                    eventHandler.onEvent(event, nextSequence, nextSequence == availableSequence);
                    nextSequence++;
                }

                sequence.set(availableSequence);
            } catch (final TimeoutException e) {
                notifyTimeout(sequence.get());
            } catch (final AlertException ex) {
                if (running.get() != RUNNING) {
                    break;
                }
            } catch (final Throwable ex) {
                exceptionHandler.handleEventException(ex, nextSequence, event);
                sequence.set(nextSequence);
                nextSequence++;
            }
        }
    }

    private void earlyExit() {
        notifyStart();
        notifyShutdown();
    }

    private void notifyTimeout(final long availableSequence) {
        try {
            if (timeoutHandler != null) {
                timeoutHandler.onTimeout(availableSequence);
            }
        } catch (Throwable e) {
            exceptionHandler.handleEventException(e, availableSequence, null);
        }
    }

    private void notifyStart() {
        if (eventHandler instanceof LifecycleAware) {
            try {
                ((LifecycleAware) eventHandler).onStart();
            } catch (final Throwable ex) {
                exceptionHandler.handleOnStartException(ex);
            }
        }
    }

    private void notifyShutdown() {
        if (eventHandler instanceof LifecycleAware) {
            try {
                ((LifecycleAware) eventHandler).onShutdown();
            } catch (final Throwable ex) {
                exceptionHandler.handleOnShutdownException(ex);
            }
        }
    }
}

// 事件处理器接口
public interface EventHandler<T> {
    void onEvent(T event, long sequence, boolean endOfBatch) throws Exception;
}

// 数据提供者接口
public interface DataProvider<T> {
    T get(long sequence);
}

// 序列报告事件处理器
public interface SequenceReportingEventHandler<T> extends EventHandler<T> {
    void setSequenceCallback(Sequence sequenceCallback);
}

// 生命周期感知接口
public interface LifecycleAware {
    void onStart();
    void onShutdown();
}

// 超时处理器
public interface TimeoutHandler {
    void onTimeout(long sequence) throws Exception;
}

// 批次开始感知接口
public interface BatchStartAware {
    void onBatchStart(long batchSize);
}
```

### 2. 工作处理器（WorkProcessor）

工作处理器用于实现工作窃取模式，多个消费者竞争处理事件。

```java
public final class WorkProcessor<T> implements EventProcessor {
    private final AtomicInteger running = new AtomicInteger(IDLE);
    private final Sequence sequence = new Sequence(Sequence.INITIAL_VALUE);
    private final RingBuffer<T> ringBuffer;
    private final SequenceBarrier sequenceBarrier;
    private final WorkHandler<T> workHandler;
    private final ExceptionHandler<? super T> exceptionHandler;
    private final Sequence workSequence;

    private final EventReleaser eventReleaser = new EventReleaser() {
        @Override
        public void release() {
            sequence.set(Long.MAX_VALUE);
        }
    };

    public WorkProcessor(RingBuffer<T> ringBuffer,
                        SequenceBarrier sequenceBarrier,
                        WorkHandler<T> workHandler,
                        ExceptionHandler<? super T> exceptionHandler,
                        Sequence workSequence) {
        this.ringBuffer = ringBuffer;
        this.sequenceBarrier = sequenceBarrier;
        this.workHandler = workHandler;
        this.exceptionHandler = exceptionHandler;
        this.workSequence = workSequence;

        if (this.workHandler instanceof EventReleaseAware) {
            ((EventReleaseAware) this.workHandler).setEventReleaser(eventReleaser);
        }
    }

    @Override
    public Sequence getSequence() {
        return sequence;
    }

    @Override
    public void halt() {
        running.set(HALTED);
        sequenceBarrier.alert();
    }

    @Override
    public boolean isRunning() {
        return running.get() != IDLE;
    }

    @Override
    public void run() {
        if (!running.compareAndSet(IDLE, RUNNING)) {
            throw new IllegalStateException("Thread is already running");
        }
        sequenceBarrier.clearAlert();

        notifyStart();

        boolean processedSequence = true;
        long cachedAvailableSequence = Long.MIN_VALUE;
        long nextSequence = sequence.get();
        T event = null;

        while (true) {
            try {
                if (processedSequence) {
                    processedSequence = false;
                    do {
                        nextSequence = workSequence.get() + 1L;
                        sequence.set(nextSequence - 1L);
                    } while (!workSequence.compareAndSet(nextSequence - 1L, nextSequence));
                }

                if (cachedAvailableSequence >= nextSequence) {
                    event = ringBuffer.get(nextSequence);
                    workHandler.onEvent(event);
                    processedSequence = true;
                } else {
                    cachedAvailableSequence = sequenceBarrier.waitFor(nextSequence);
                }
            } catch (final TimeoutException e) {
                notifyTimeout(sequence.get());
            } catch (final AlertException ex) {
                if (!running.get() != RUNNING) {
                    break;
                }
            } catch (final Throwable ex) {
                exceptionHandler.handleEventException(ex, nextSequence, event);
                processedSequence = true;
            }
        }

        notifyShutdown();
        running.set(IDLE);
    }

    private void notifyTimeout(final long availableSequence) {
        try {
            if (workHandler instanceof TimeoutHandler) {
                ((TimeoutHandler) workHandler).onTimeout(availableSequence);
            }
        } catch (Throwable e) {
            exceptionHandler.handleEventException(e, availableSequence, null);
        }
    }

    private void notifyStart() {
        if (workHandler instanceof LifecycleAware) {
            try {
                ((LifecycleAware) workHandler).onStart();
            } catch (final Throwable ex) {
                exceptionHandler.handleOnStartException(ex);
            }
        }
    }

    private void notifyShutdown() {
        if (workHandler instanceof LifecycleAware) {
            try {
                ((LifecycleAware) workHandler).onShutdown();
            } catch (final Throwable ex) {
                exceptionHandler.handleOnShutdownException(ex);
            }
        }
    }
}

// 工作处理器接口
public interface WorkHandler<T> {
    void onEvent(T event) throws Exception;
}

// 事件释放感知接口
public interface EventReleaseAware {
    void setEventReleaser(EventReleaser eventReleaser);
}

// 事件释放器
public interface EventReleaser {
    void release();
}
```

## Disruptor使用示例

### 1. 简单的生产者-消费者模式

```java
// 定义事件
public class OrderEvent {
    private long orderId;
    private String symbol;
    private double price;
    private int quantity;

    // getter和setter方法
    public long getOrderId() { return orderId; }
    public void setOrderId(long orderId) { this.orderId = orderId; }

    public String getSymbol() { return symbol; }
    public void setSymbol(String symbol) { this.symbol = symbol; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}

// 事件工厂
public class OrderEventFactory implements EventFactory<OrderEvent> {
    @Override
    public OrderEvent newInstance() {
        return new OrderEvent();
    }
}

// 事件处理器
public class OrderEventHandler implements EventHandler<OrderEvent> {
    private static final Logger logger = LoggerFactory.getLogger(OrderEventHandler.class);

    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) throws Exception {
        // 处理订单事件
        logger.info("Processing order: {} - {} {} @ {}",
                   event.getOrderId(), event.getSymbol(),
                   event.getQuantity(), event.getPrice());

        // 模拟处理时间
        Thread.sleep(1);
    }
}

// 事件发布器
public class OrderEventPublisher {
    private final RingBuffer<OrderEvent> ringBuffer;

    public OrderEventPublisher(RingBuffer<OrderEvent> ringBuffer) {
        this.ringBuffer = ringBuffer;
    }

    public void publishOrder(long orderId, String symbol, double price, int quantity) {
        // 使用事件转换器发布事件
        ringBuffer.publishEvent((event, sequence, args) -> {
            event.setOrderId((Long) args[0]);
            event.setSymbol((String) args[1]);
            event.setPrice((Double) args[2]);
            event.setQuantity((Integer) args[3]);
        }, orderId, symbol, price, quantity);
    }
}

// 主程序
public class DisruptorExample {
    public static void main(String[] args) throws InterruptedException {
        // 环形缓冲区大小，必须是2的幂次方
        int bufferSize = 1024;

        // 创建Disruptor
        Disruptor<OrderEvent> disruptor = new Disruptor<>(
                new OrderEventFactory(),
                bufferSize,
                Executors.defaultThreadFactory(),
                ProducerType.SINGLE,
                new YieldingWaitStrategy()
        );

        // 连接事件处理器
        disruptor.handleEventsWith(new OrderEventHandler());

        // 启动Disruptor
        disruptor.start();

        // 获取环形缓冲区
        RingBuffer<OrderEvent> ringBuffer = disruptor.getRingBuffer();

        // 创建事件发布器
        OrderEventPublisher publisher = new OrderEventPublisher(ringBuffer);

        // 发布事件
        for (int i = 0; i < 1000; i++) {
            publisher.publishOrder(i, "AAPL", 150.0 + i, 100);
        }

        Thread.sleep(1000);
        disruptor.shutdown();
    }
}
```

### 2. 多消费者链式处理

```java
// 风险检查处理器
public class RiskCheckHandler implements EventHandler<OrderEvent> {
    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
        // 风险检查逻辑
        if (event.getPrice() > 1000 || event.getQuantity() > 10000) {
            // 标记为高风险订单
            System.out.println("High risk order detected: " + event.getOrderId());
        }
    }
}

// 订单验证处理器
public class OrderValidationHandler implements EventHandler<OrderEvent> {
    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
        // 订单验证逻辑
        if (event.getSymbol() == null || event.getSymbol().isEmpty()) {
            System.out.println("Invalid order symbol: " + event.getOrderId());
        }
    }
}

// 订单执行处理器
public class OrderExecutionHandler implements EventHandler<OrderEvent> {
    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
        // 订单执行逻辑
        System.out.println("Executing order: " + event.getOrderId());
    }
}

// 多消费者处理链示例
public class MultiConsumerExample {
    public static void main(String[] args) {
        int bufferSize = 1024;

        Disruptor<OrderEvent> disruptor = new Disruptor<>(
                new OrderEventFactory(),
                bufferSize,
                Executors.defaultThreadFactory(),
                ProducerType.SINGLE,
                new BusySpinWaitStrategy()
        );

        // 并行处理：风险检查和订单验证同时进行
        disruptor.handleEventsWith(new RiskCheckHandler(), new OrderValidationHandler())
                 // 然后串行处理：订单执行
                 .then(new OrderExecutionHandler());

        disruptor.start();

        RingBuffer<OrderEvent> ringBuffer = disruptor.getRingBuffer();
        OrderEventPublisher publisher = new OrderEventPublisher(ringBuffer);

        // 发布测试事件
        for (int i = 0; i < 100; i++) {
            publisher.publishOrder(i, "TEST" + i, 100.0, 50);
        }

        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        disruptor.shutdown();
    }
}
```

### 3. 工作窃取模式

```java
// 工作处理器
public class OrderWorkHandler implements WorkHandler<OrderEvent> {
    private final String name;

    public OrderWorkHandler(String name) {
        this.name = name;
    }

    @Override
    public void onEvent(OrderEvent event) throws Exception {
        System.out.printf("Worker %s processing order %d%n", name, event.getOrderId());

        // 模拟处理时间
        Thread.sleep(10);
    }
}

// 工作窃取模式示例
public class WorkStealingExample {
    public static void main(String[] args) throws InterruptedException {
        int bufferSize = 1024;
        int workerCount = 4;

        Disruptor<OrderEvent> disruptor = new Disruptor<>(
                new OrderEventFactory(),
                bufferSize,
                Executors.defaultThreadFactory(),
                ProducerType.SINGLE,
                new BusySpinWaitStrategy()
        );

        // 创建工作处理器数组
        OrderWorkHandler[] handlers = new OrderWorkHandler[workerCount];
        for (int i = 0; i < workerCount; i++) {
            handlers[i] = new OrderWorkHandler("Worker-" + i);
        }

        // 配置工作窃取模式
        disruptor.handleEventsWithWorkerPool(handlers);

        disruptor.start();

        RingBuffer<OrderEvent> ringBuffer = disruptor.getRingBuffer();
        OrderEventPublisher publisher = new OrderEventPublisher(ringBuffer);

        // 发布大量事件进行负载均衡测试
        for (int i = 0; i < 1000; i++) {
            publisher.publishOrder(i, "WORK" + i, 50.0, 25);
        }

        Thread.sleep(2000);
        disruptor.shutdown();
    }
}
```

## 性能优化技术详解

### 1. 内存屏障和缓存一致性

Disruptor使用内存屏障确保在多核处理器上的正确性和性能。

```java
// 内存屏障实现示例
public class MemoryBarrierExample {
    private volatile long value;

    // LoadLoad屏障
    public long readValue() {
        return value; // volatile读自动插入LoadLoad屏障
    }

    // StoreStore屏障
    public void writeValue(long newValue) {
        value = newValue; // volatile写自动插入StoreStore屏障
    }

    // 使用Unsafe的有序写入，避免完整的内存屏障
    private static final Unsafe UNSAFE = getUnsafe();
    private static final long VALUE_OFFSET;

    static {
        try {
            VALUE_OFFSET = UNSAFE.objectFieldOffset(
                MemoryBarrierExample.class.getDeclaredField("value"));
        } catch (Exception ex) {
            throw new Error(ex);
        }
    }

    // 有序写入（比volatile写更轻量）
    public void putOrderedValue(long newValue) {
        UNSAFE.putOrderedLong(this, VALUE_OFFSET, newValue);
    }

    private static Unsafe getUnsafe() {
        try {
            Field field = Unsafe.class.getDeclaredField("theUnsafe");
            field.setAccessible(true);
            return (Unsafe) field.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 2. 缓存行填充避免伪共享

```java
// 缓存行填充策略
public abstract class CachePadding {
    // 缓存行通常是64字节，使用long填充（8字节 × 8 = 64字节）
    protected long p1, p2, p3, p4, p5, p6, p7;
}

public class PaddedAtomicLong extends CachePadding {
    private volatile long value;
    protected long p9, p10, p11, p12, p13, p14, p15; // 右侧填充

    public long get() {
        return value;
    }

    public void set(long newValue) {
        value = newValue;
    }

    // CAS操作
    private static final Unsafe UNSAFE = getUnsafe();
    private static final long VALUE_OFFSET;

    static {
        try {
            VALUE_OFFSET = UNSAFE.objectFieldOffset(
                PaddedAtomicLong.class.getDeclaredField("value"));
        } catch (Exception ex) {
            throw new Error(ex);
        }
    }

    public boolean compareAndSet(long expect, long update) {
        return UNSAFE.compareAndSwapLong(this, VALUE_OFFSET, expect, update);
    }

    private static Unsafe getUnsafe() {
        try {
            Field field = Unsafe.class.getDeclaredField("theUnsafe");
            field.setAccessible(true);
            return (Unsafe) field.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 3. 批量处理优化

```java
// 批量事件处理器
public class BatchOptimizedEventHandler implements EventHandler<OrderEvent> {
    private final List<OrderEvent> batch = new ArrayList<>();
    private final int batchSize;

    public BatchOptimizedEventHandler(int batchSize) {
        this.batchSize = batchSize;
    }

    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) throws Exception {
        // 将事件添加到批次中
        batch.add(cloneEvent(event));

        // 当达到批次大小或序列结束时处理批次
        if (batch.size() >= batchSize || endOfBatch) {
            processBatch(batch);
            batch.clear();
        }
    }

    private void processBatch(List<OrderEvent> events) {
        // 批量处理，减少系统调用和锁竞争
        System.out.printf("Processing batch of %d orders%n", events.size());

        // 例如：批量数据库插入、批量网络调用等
        for (OrderEvent event : events) {
            // 具体处理逻辑
        }
    }

    private OrderEvent cloneEvent(OrderEvent original) {
        OrderEvent clone = new OrderEvent();
        clone.setOrderId(original.getOrderId());
        clone.setSymbol(original.getSymbol());
        clone.setPrice(original.getPrice());
        clone.setQuantity(original.getQuantity());
        return clone;
    }
}
```

## 性能基准测试

### 1. 性能测试框架

```java
public class DisruptorBenchmark {
    private static final int BUFFER_SIZE = 1024 * 1024;
    private static final long ITERATIONS = 1000L * 1000L * 100L;

    public void testThroughput() throws InterruptedException {
        // 创建Disruptor
        Disruptor<ValueEvent> disruptor = new Disruptor<>(
                ValueEvent::new,
                BUFFER_SIZE,
                Executors.defaultThreadFactory(),
                ProducerType.SINGLE,
                new BusySpinWaitStrategy()
        );

        CountDownLatch latch = new CountDownLatch(1);

        // 性能测试处理器
        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            if (sequence == ITERATIONS - 1) {
                latch.countDown();
            }
        });

        RingBuffer<ValueEvent> ringBuffer = disruptor.getRingBuffer();
        disruptor.start();

        long startTime = System.nanoTime();

        // 发布事件
        for (long i = 0; i < ITERATIONS; i++) {
            long sequence = ringBuffer.next();
            ValueEvent event = ringBuffer.get(sequence);
            event.setValue(i);
            ringBuffer.publish(sequence);
        }

        latch.await();
        long duration = System.nanoTime() - startTime;

        disruptor.shutdown();

        long opsPerSecond = (ITERATIONS * 1000000000L) / duration;
        System.out.printf("Throughput: %,d ops/sec%n", opsPerSecond);
    }

    public void testLatency() throws InterruptedException {
        Disruptor<TimestampedEvent> disruptor = new Disruptor<>(
                TimestampedEvent::new,
                BUFFER_SIZE,
                Executors.defaultThreadFactory(),
                ProducerType.SINGLE,
                new BusySpinWaitStrategy()
        );

        final long[] latencies = new long[(int) ITERATIONS];
        final AtomicInteger counter = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(1);

        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            long endTime = System.nanoTime();
            long latency = endTime - event.getTimestamp();
            int index = counter.getAndIncrement();

            if (index < latencies.length) {
                latencies[index] = latency;
            }

            if (sequence == ITERATIONS - 1) {
                latch.countDown();
            }
        });

        RingBuffer<TimestampedEvent> ringBuffer = disruptor.getRingBuffer();
        disruptor.start();

        // 发布事件并记录时间戳
        for (long i = 0; i < ITERATIONS; i++) {
            long sequence = ringBuffer.next();
            TimestampedEvent event = ringBuffer.get(sequence);
            event.setTimestamp(System.nanoTime());
            ringBuffer.publish(sequence);
        }

        latch.await();
        disruptor.shutdown();

        // 计算延迟统计
        Arrays.sort(latencies);
        System.out.printf("Min latency: %,d ns%n", latencies[0]);
        System.out.printf("50th percentile: %,d ns%n", latencies[latencies.length / 2]);
        System.out.printf("99th percentile: %,d ns%n", latencies[(int) (latencies.length * 0.99)]);
        System.out.printf("Max latency: %,d ns%n", latencies[latencies.length - 1]);
    }

    // 测试事件类
    public static class ValueEvent {
        private long value;

        public long getValue() { return value; }
        public void setValue(long value) { this.value = value; }
    }

    public static class TimestampedEvent {
        private long timestamp;

        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    }

    public static void main(String[] args) throws InterruptedException {
        DisruptorBenchmark benchmark = new DisruptorBenchmark();

        System.out.println("=== Throughput Test ===");
        benchmark.testThroughput();

        System.out.println("\n=== Latency Test ===");
        benchmark.testLatency();
    }
}
```

## 应用场景和最佳实践

### 应用场景

1. **金融交易系统**：高频交易、订单处理、风险管理
2. **游戏服务器**：玩家行为处理、实时事件分发
3. **日志系统**：高吞吐量日志写入、异步处理
4. **消息中间件**：内部队列实现、事件分发
5. **大数据处理**：流式数据处理、ETL管道

### 最佳实践

1. **选择合适的等待策略**
   - BusySpinWaitStrategy：延迟敏感场景
   - YieldingWaitStrategy：平衡延迟和CPU使用率
   - SleepingWaitStrategy：CPU资源受限场景

2. **合理设置缓冲区大小**
   - 必须是2的幂次方
   - 考虑内存使用和延迟要求
   - 通常1024到1024*1024之间

3. **避免在事件处理器中进行阻塞操作**
   - 使用异步I/O
   - 将阻塞操作移到其他线程

4. **合理设计事件对象**
   - 避免频繁对象创建
   - 使用对象池或重用策略

### 性能对比

| 队列类型 | 吞吐量(ops/sec) | 延迟(μs) | 内存使用 | 适用场景 |
|----------|----------------|----------|----------|----------|
| ArrayBlockingQueue | 5M | 500-1000 | 中等 | 通用场景 |
| LinkedBlockingQueue | 3M | 800-1500 | 高 | 无界队列 |
| ConcurrentLinkedQueue | 8M | 200-500 | 中等 | 非阻塞场景 |
| Disruptor | 25M+ | 50-200 | 低 | 高性能场景 |

## 总结

Disruptor通过巧妙的数据结构设计和算法优化，实现了卓越的性能：

1. **环形缓冲区**：避免内存分配和垃圾回收开销
2. **无锁设计**：使用CAS操作替代传统锁机制
3. **缓存友好**：优化内存布局，减少缓存失效
4. **批量处理**：提高吞吐量，减少系统调用
5. **内存屏障**：保证多核环境下的正确性

这些技术的结合使得Disruptor在高并发、低延迟场景下表现出色，为构建高性能系统提供了强有力的工具。理解Disruptor的设计原理，不仅有助于更好地使用该框架，也为设计其他高性能系统提供了宝贵的经验和启发。