---
title: "设计模式入门教程18：状态模式 - 让对象状态转换更优雅"
date: 2024-12-18T10:18:00+08:00
draft: false
tags: ["设计模式", "状态模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是状态模式？

状态模式（State Pattern）是一种行为型设计模式，它允许对象在内部状态改变时改变它的行为。对象看起来好像修改了它的类。状态模式将状态封装成独立的类，并将动作委托到代表当前状态的对象。

### 🌟 现实生活中的例子

想象一下**电梯的运行**：
- **状态**：停止、上升、下降、开门、关门
- **行为**：每个状态下按按钮的反应不同
- **转换**：停止→开门→关门→上升→停止

又比如**手机的状态**：
- **锁定状态**：只能滑动解锁
- **解锁状态**：可以操作各种功能
- **通话状态**：只能操作通话相关功能

这就是状态模式的应用场景！

## 🏗️ 模式结构

```java
// 状态接口
interface State {
    void handleRequest(Context context);
}

// 具体状态A
class ConcreteStateA implements State {
    @Override
    public void handleRequest(Context context) {
        System.out.println("处理状态A的请求");
        // 可能转换到其他状态
        context.setState(new ConcreteStateB());
    }
}

// 具体状态B
class ConcreteStateB implements State {
    @Override
    public void handleRequest(Context context) {
        System.out.println("处理状态B的请求");
        context.setState(new ConcreteStateA());
    }
}

// 上下文类
class Context {
    private State state;

    public Context(State state) {
        this.state = state;
    }

    public void setState(State state) {
        this.state = state;
    }

    public void request() {
        state.handleRequest(this);
    }
}
```

## 💡 核心组件详解

### 1. 抽象状态（State）
```java
// 播放器状态接口
interface PlayerState {
    void play(MusicPlayer player);
    void pause(MusicPlayer player);
    void stop(MusicPlayer player);
    void next(MusicPlayer player);
    void previous(MusicPlayer player);
    String getStateName();
}
```

### 2. 具体状态（ConcreteState）
```java
// 停止状态
class StoppedState implements PlayerState {
    @Override
    public void play(MusicPlayer player) {
        System.out.println("开始播放音乐");
        player.setState(new PlayingState());
        player.getCurrentSong().play();
    }

    @Override
    public void pause(MusicPlayer player) {
        System.out.println("当前已停止，无法暂停");
    }

    @Override
    public void stop(MusicPlayer player) {
        System.out.println("当前已停止");
    }

    @Override
    public void next(MusicPlayer player) {
        System.out.println("切换到下一首");
        player.nextSong();
        // 停止状态下切歌后自动开始播放
        player.setState(new PlayingState());
        player.getCurrentSong().play();
    }

    @Override
    public void previous(MusicPlayer player) {
        System.out.println("切换到上一首");
        player.previousSong();
        // 停止状态下切歌后自动开始播放
        player.setState(new PlayingState());
        player.getCurrentSong().play();
    }

    @Override
    public String getStateName() {
        return "停止";
    }
}

// 播放状态
class PlayingState implements PlayerState {
    @Override
    public void play(MusicPlayer player) {
        System.out.println("当前正在播放");
    }

    @Override
    public void pause(MusicPlayer player) {
        System.out.println("暂停播放");
        player.setState(new PausedState());
        player.getCurrentSong().pause();
    }

    @Override
    public void stop(MusicPlayer player) {
        System.out.println("停止播放");
        player.setState(new StoppedState());
        player.getCurrentSong().stop();
    }

    @Override
    public void next(MusicPlayer player) {
        System.out.println("切换到下一首并播放");
        player.getCurrentSong().stop();
        player.nextSong();
        player.getCurrentSong().play();
    }

    @Override
    public void previous(MusicPlayer player) {
        System.out.println("切换到上一首并播放");
        player.getCurrentSong().stop();
        player.previousSong();
        player.getCurrentSong().play();
    }

    @Override
    public String getStateName() {
        return "播放中";
    }
}

// 暂停状态
class PausedState implements PlayerState {
    @Override
    public void play(MusicPlayer player) {
        System.out.println("继续播放");
        player.setState(new PlayingState());
        player.getCurrentSong().resume();
    }

    @Override
    public void pause(MusicPlayer player) {
        System.out.println("当前已暂停");
    }

    @Override
    public void stop(MusicPlayer player) {
        System.out.println("停止播放");
        player.setState(new StoppedState());
        player.getCurrentSong().stop();
    }

    @Override
    public void next(MusicPlayer player) {
        System.out.println("切换到下一首");
        player.nextSong();
        // 暂停状态下切歌后开始播放
        player.setState(new PlayingState());
        player.getCurrentSong().play();
    }

    @Override
    public void previous(MusicPlayer player) {
        System.out.println("切换到上一首");
        player.previousSong();
        // 暂停状态下切歌后开始播放
        player.setState(new PlayingState());
        player.getCurrentSong().play();
    }

    @Override
    public String getStateName() {
        return "暂停";
    }
}
```

### 3. 上下文（Context）
```java
// 音乐播放器上下文
class MusicPlayer {
    private PlayerState state;
    private List<Song> playlist;
    private int currentIndex;

    public MusicPlayer() {
        this.state = new StoppedState();
        this.playlist = new ArrayList<>();
        this.currentIndex = 0;
        initializePlaylist();
    }

    private void initializePlaylist() {
        playlist.add(new Song("夜曲", "周杰伦"));
        playlist.add(new Song("青花瓷", "周杰伦"));
        playlist.add(new Song("稻香", "周杰伦"));
        playlist.add(new Song("告白气球", "周杰伦"));
    }

    public void setState(PlayerState state) {
        System.out.println("状态从 [" + this.state.getStateName() + "] 切换到 [" + state.getStateName() + "]");
        this.state = state;
    }

    public void play() {
        state.play(this);
    }

    public void pause() {
        state.pause(this);
    }

    public void stop() {
        state.stop(this);
    }

    public void next() {
        state.next(this);
    }

    public void previous() {
        state.previous(this);
    }

    public void nextSong() {
        if (currentIndex < playlist.size() - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // 循环播放
        }
    }

    public void previousSong() {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = playlist.size() - 1; // 循环播放
        }
    }

    public Song getCurrentSong() {
        return playlist.get(currentIndex);
    }

    public String getCurrentState() {
        return state.getStateName();
    }

    public void showStatus() {
        System.out.println("=== 播放器状态 ===");
        System.out.println("当前状态: " + getCurrentState());
        System.out.println("当前歌曲: " + getCurrentSong());
        System.out.println("播放列表位置: " + (currentIndex + 1) + "/" + playlist.size());
        System.out.println("=================");
    }
}

// 歌曲类
class Song {
    private String title;
    private String artist;

    public Song(String title, String artist) {
        this.title = title;
        this.artist = artist;
    }

    public void play() {
        System.out.println("♪ 正在播放: " + this);
    }

    public void pause() {
        System.out.println("⏸ 暂停: " + this);
    }

    public void resume() {
        System.out.println("▶ 继续播放: " + this);
    }

    public void stop() {
        System.out.println("⏹ 停止: " + this);
    }

    @Override
    public String toString() {
        return title + " - " + artist;
    }
}
```

## 🎮 实际应用示例

### 示例1：订单状态管理
```java
// 订单状态接口
interface OrderState {
    void payOrder(OrderContext order);
    void shipOrder(OrderContext order);
    void deliverOrder(OrderContext order);
    void cancelOrder(OrderContext order);
    void returnOrder(OrderContext order);
    String getStatusName();
    String getDescription();
}

// 待支付状态
class PendingPaymentState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单支付成功！");
        order.setState(new PaidState());
        order.setPaymentTime(LocalDateTime.now());
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单未支付，无法发货");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单未支付，无法配送");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("取消订单");
        order.setState(new CancelledState());
        order.setCancelTime(LocalDateTime.now());
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("订单未支付，无法退货");
    }

    @Override
    public String getStatusName() {
        return "待支付";
    }

    @Override
    public String getDescription() {
        return "订单已创建，等待用户支付";
    }
}

// 已支付状态
class PaidState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单已支付，无需重复支付");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("开始发货...");
        order.setState(new ShippedState());
        order.setShipTime(LocalDateTime.now());
        order.generateTrackingNumber();
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单未发货，无法配送");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单已支付，开始退款流程");
        order.setState(new CancelledState());
        order.setCancelTime(LocalDateTime.now());
        order.processRefund();
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("订单未收货，无法退货");
    }

    @Override
    public String getStatusName() {
        return "已支付";
    }

    @Override
    public String getDescription() {
        return "订单已支付，准备发货";
    }
}

// 已发货状态
class ShippedState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单已支付");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单已发货");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单配送完成！");
        order.setState(new DeliveredState());
        order.setDeliveryTime(LocalDateTime.now());
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单已发货，无法直接取消，请联系客服");
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("订单未收货，无法退货");
    }

    @Override
    public String getStatusName() {
        return "已发货";
    }

    @Override
    public String getDescription() {
        return "订单正在运输途中";
    }
}

// 已配送状态
class DeliveredState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单已支付");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单已发货");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单已配送");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单已配送，无法取消，可以申请退货");
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("申请退货，等待审核...");
        order.setState(new ReturnRequestedState());
        order.setReturnRequestTime(LocalDateTime.now());
    }

    @Override
    public String getStatusName() {
        return "已配送";
    }

    @Override
    public String getDescription() {
        return "订单已送达，交易完成";
    }
}

// 退货申请状态
class ReturnRequestedState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单在退货流程中");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单在退货流程中");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单在退货流程中");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单在退货流程中");
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("退货申请已处理，退款完成");
        order.setState(new ReturnedState());
        order.setReturnTime(LocalDateTime.now());
        order.processRefund();
    }

    @Override
    public String getStatusName() {
        return "退货申请中";
    }

    @Override
    public String getDescription() {
        return "用户已申请退货，等待处理";
    }
}

// 已退货状态
class ReturnedState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单已退货");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单已退货");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单已退货");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单已退货");
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("订单已退货");
    }

    @Override
    public String getStatusName() {
        return "已退货";
    }

    @Override
    public String getDescription() {
        return "订单已退货，退款已处理";
    }
}

// 已取消状态
class CancelledState implements OrderState {
    @Override
    public void payOrder(OrderContext order) {
        System.out.println("订单已取消，无法支付");
    }

    @Override
    public void shipOrder(OrderContext order) {
        System.out.println("订单已取消，无法发货");
    }

    @Override
    public void deliverOrder(OrderContext order) {
        System.out.println("订单已取消，无法配送");
    }

    @Override
    public void cancelOrder(OrderContext order) {
        System.out.println("订单已取消");
    }

    @Override
    public void returnOrder(OrderContext order) {
        System.out.println("订单已取消，无法退货");
    }

    @Override
    public String getStatusName() {
        return "已取消";
    }

    @Override
    public String getDescription() {
        return "订单已取消";
    }
}

// 订单上下文
class OrderContext {
    private String orderId;
    private OrderState state;
    private double amount;
    private String product;
    private LocalDateTime createTime;
    private LocalDateTime paymentTime;
    private LocalDateTime shipTime;
    private LocalDateTime deliveryTime;
    private LocalDateTime cancelTime;
    private LocalDateTime returnRequestTime;
    private LocalDateTime returnTime;
    private String trackingNumber;

    public OrderContext(String orderId, String product, double amount) {
        this.orderId = orderId;
        this.product = product;
        this.amount = amount;
        this.createTime = LocalDateTime.now();
        this.state = new PendingPaymentState();
    }

    public void setState(OrderState state) {
        System.out.println("订单状态从 [" + this.state.getStatusName() + "] 变更为 [" + state.getStatusName() + "]");
        this.state = state;
    }

    // 订单操作方法
    public void pay() {
        state.payOrder(this);
    }

    public void ship() {
        state.shipOrder(this);
    }

    public void deliver() {
        state.deliverOrder(this);
    }

    public void cancel() {
        state.cancelOrder(this);
    }

    public void requestReturn() {
        state.returnOrder(this);
    }

    // 业务方法
    public void generateTrackingNumber() {
        this.trackingNumber = "TN" + System.currentTimeMillis();
        System.out.println("生成物流单号：" + trackingNumber);
    }

    public void processRefund() {
        System.out.println("处理退款：¥" + amount);
    }

    public void showOrderInfo() {
        System.out.println("=== 订单信息 ===");
        System.out.println("订单号：" + orderId);
        System.out.println("商品：" + product);
        System.out.println("金额：¥" + amount);
        System.out.println("当前状态：" + state.getStatusName());
        System.out.println("状态描述：" + state.getDescription());
        if (trackingNumber != null) {
            System.out.println("物流单号：" + trackingNumber);
        }
        System.out.println("创建时间：" + createTime);
        if (paymentTime != null) System.out.println("支付时间：" + paymentTime);
        if (shipTime != null) System.out.println("发货时间：" + shipTime);
        if (deliveryTime != null) System.out.println("配送时间：" + deliveryTime);
        if (cancelTime != null) System.out.println("取消时间：" + cancelTime);
        if (returnRequestTime != null) System.out.println("退货申请时间：" + returnRequestTime);
        if (returnTime != null) System.out.println("退货完成时间：" + returnTime);
        System.out.println("================");
    }

    // Getters and Setters
    public String getOrderId() { return orderId; }
    public OrderState getState() { return state; }
    public double getAmount() { return amount; }
    public String getProduct() { return product; }

    public void setPaymentTime(LocalDateTime paymentTime) { this.paymentTime = paymentTime; }
    public void setShipTime(LocalDateTime shipTime) { this.shipTime = shipTime; }
    public void setDeliveryTime(LocalDateTime deliveryTime) { this.deliveryTime = deliveryTime; }
    public void setCancelTime(LocalDateTime cancelTime) { this.cancelTime = cancelTime; }
    public void setReturnRequestTime(LocalDateTime returnRequestTime) { this.returnRequestTime = returnRequestTime; }
    public void setReturnTime(LocalDateTime returnTime) { this.returnTime = returnTime; }
}

// 使用示例
public class OrderManagementExample {
    public static void main(String[] args) {
        // 创建订单
        OrderContext order = new OrderContext("ORD001", "iPhone 15 Pro", 7999.0);
        order.showOrderInfo();

        System.out.println("\n=== 正常订单流程 ===");
        // 支付订单
        order.pay();
        order.showOrderInfo();

        // 发货
        order.ship();
        order.showOrderInfo();

        // 配送
        order.deliver();
        order.showOrderInfo();

        System.out.println("\n=== 创建另一个订单并测试退货流程 ===");
        OrderContext order2 = new OrderContext("ORD002", "MacBook Pro", 15999.0);

        // 完成整个购买流程
        order2.pay();
        order2.ship();
        order2.deliver();

        // 申请退货
        order2.requestReturn();

        // 处理退货
        order2.requestReturn();
        order2.showOrderInfo();

        System.out.println("\n=== 测试取消订单 ===");
        OrderContext order3 = new OrderContext("ORD003", "iPad Air", 4799.0);
        order3.cancel(); // 在待支付状态下取消

        OrderContext order4 = new OrderContext("ORD004", "Apple Watch", 2999.0);
        order4.pay();
        order4.cancel(); // 在已支付状态下取消
    }
}
```

### 示例2：游戏角色状态
```java
// 角色状态接口
interface CharacterState {
    void move(GameCharacter character);
    void attack(GameCharacter character);
    void defend(GameCharacter character);
    void useSkill(GameCharacter character);
    void rest(GameCharacter character);
    String getStateName();
    boolean canMove();
    boolean canAttack();
    boolean canDefend();
}

// 正常状态
class NormalState implements CharacterState {
    @Override
    public void move(GameCharacter character) {
        System.out.println(character.getName() + " 正常移动");
        character.decreaseStamina(5);
        checkStaminaAndTransition(character);
    }

    @Override
    public void attack(GameCharacter character) {
        System.out.println(character.getName() + " 发动攻击！造成伤害：100");
        character.decreaseStamina(15);
        checkStaminaAndTransition(character);
    }

    @Override
    public void defend(GameCharacter character) {
        System.out.println(character.getName() + " 进入防御姿态");
        character.setState(new DefendingState());
    }

    @Override
    public void useSkill(GameCharacter character) {
        if (character.getMana() >= 20) {
            System.out.println(character.getName() + " 释放技能！强力攻击！");
            character.decreaseMana(20);
            character.decreaseStamina(25);
            checkStaminaAndTransition(character);
        } else {
            System.out.println("魔法值不足，无法释放技能");
        }
    }

    @Override
    public void rest(GameCharacter character) {
        System.out.println(character.getName() + " 开始休息");
        character.setState(new RestingState());
    }

    @Override
    public String getStateName() {
        return "正常";
    }

    @Override
    public boolean canMove() { return true; }

    @Override
    public boolean canAttack() { return true; }

    @Override
    public boolean canDefend() { return true; }

    private void checkStaminaAndTransition(GameCharacter character) {
        if (character.getStamina() <= 10) {
            System.out.println(character.getName() + " 体力不支，进入疲劳状态");
            character.setState(new TiredState());
        }
    }
}

// 疲劳状态
class TiredState implements CharacterState {
    @Override
    public void move(GameCharacter character) {
        System.out.println(character.getName() + " 缓慢移动（疲劳状态）");
        character.decreaseStamina(2);
        if (character.getStamina() <= 0) {
            System.out.println(character.getName() + " 体力耗尽，昏倒了！");
            character.setState(new UnconsciousState());
        }
    }

    @Override
    public void attack(GameCharacter character) {
        System.out.println(character.getName() + " 无力攻击，伤害减半：50");
        character.decreaseStamina(10);
        if (character.getStamina() <= 0) {
            System.out.println(character.getName() + " 体力耗尽，昏倒了！");
            character.setState(new UnconsciousState());
        }
    }

    @Override
    public void defend(GameCharacter character) {
        System.out.println(character.getName() + " 勉强防御");
        character.setState(new DefendingState());
    }

    @Override
    public void useSkill(GameCharacter character) {
        System.out.println("太疲劳了，无法集中精神释放技能");
    }

    @Override
    public void rest(GameCharacter character) {
        System.out.println(character.getName() + " 开始休息恢复体力");
        character.setState(new RestingState());
    }

    @Override
    public String getStateName() {
        return "疲劳";
    }

    @Override
    public boolean canMove() { return true; }

    @Override
    public boolean canAttack() { return true; }

    @Override
    public boolean canDefend() { return true; }
}

// 防御状态
class DefendingState implements CharacterState {
    private int defendTurns = 0;

    @Override
    public void move(GameCharacter character) {
        System.out.println(character.getName() + " 退出防御姿态并移动");
        character.setState(getNextState(character));
        character.getState().move(character);
    }

    @Override
    public void attack(GameCharacter character) {
        System.out.println(character.getName() + " 退出防御姿态并攻击");
        character.setState(getNextState(character));
        character.getState().attack(character);
    }

    @Override
    public void defend(GameCharacter character) {
        defendTurns++;
        System.out.println(character.getName() + " 继续防御，减少50%伤害（第" + defendTurns + "回合）");
        character.increaseStamina(5); // 防御时恢复少量体力

        if (defendTurns >= 3) {
            System.out.println("防御时间过长，退出防御状态");
            character.setState(getNextState(character));
        }
    }

    @Override
    public void useSkill(GameCharacter character) {
        System.out.println("防御状态下无法释放技能");
    }

    @Override
    public void rest(GameCharacter character) {
        System.out.println(character.getName() + " 退出防御姿态并休息");
        character.setState(new RestingState());
    }

    @Override
    public String getStateName() {
        return "防御中";
    }

    @Override
    public boolean canMove() { return true; }

    @Override
    public boolean canAttack() { return true; }

    @Override
    public boolean canDefend() { return true; }

    private CharacterState getNextState(GameCharacter character) {
        if (character.getStamina() <= 10) {
            return new TiredState();
        } else {
            return new NormalState();
        }
    }
}

// 休息状态
class RestingState implements CharacterState {
    private int restTurns = 0;

    @Override
    public void move(GameCharacter character) {
        System.out.println(character.getName() + " 结束休息并移动");
        character.setState(new NormalState());
        character.getState().move(character);
    }

    @Override
    public void attack(GameCharacter character) {
        System.out.println(character.getName() + " 结束休息并攻击");
        character.setState(new NormalState());
        character.getState().attack(character);
    }

    @Override
    public void defend(GameCharacter character) {
        System.out.println(character.getName() + " 结束休息并防御");
        character.setState(new DefendingState());
    }

    @Override
    public void useSkill(GameCharacter character) {
        System.out.println("休息状态下无法释放技能");
    }

    @Override
    public void rest(GameCharacter character) {
        restTurns++;
        System.out.println(character.getName() + " 继续休息（第" + restTurns + "回合）");
        character.increaseStamina(20);
        character.increaseMana(10);

        if (character.getStamina() >= character.getMaxStamina()) {
            System.out.println("体力已完全恢复！");
            character.setState(new NormalState());
        }
    }

    @Override
    public String getStateName() {
        return "休息中";
    }

    @Override
    public boolean canMove() { return true; }

    @Override
    public boolean canAttack() { return true; }

    @Override
    public boolean canDefend() { return true; }
}

// 昏迷状态
class UnconsciousState implements CharacterState {
    private int unconsciousTurns = 0;

    @Override
    public void move(GameCharacter character) {
        System.out.println(character.getName() + " 已昏迷，无法移动");
    }

    @Override
    public void attack(GameCharacter character) {
        System.out.println(character.getName() + " 已昏迷，无法攻击");
    }

    @Override
    public void defend(GameCharacter character) {
        System.out.println(character.getName() + " 已昏迷，无法防御");
    }

    @Override
    public void useSkill(GameCharacter character) {
        System.out.println(character.getName() + " 已昏迷，无法释放技能");
    }

    @Override
    public void rest(GameCharacter character) {
        unconsciousTurns++;
        System.out.println(character.getName() + " 昏迷中...（第" + unconsciousTurns + "回合）");
        character.increaseStamina(5);

        if (unconsciousTurns >= 3 && character.getStamina() > 20) {
            System.out.println(character.getName() + " 苏醒了！但仍然很疲劳");
            character.setState(new TiredState());
        }
    }

    @Override
    public String getStateName() {
        return "昏迷";
    }

    @Override
    public boolean canMove() { return false; }

    @Override
    public boolean canAttack() { return false; }

    @Override
    public boolean canDefend() { return false; }
}

// 游戏角色类
class GameCharacter {
    private String name;
    private CharacterState state;
    private int stamina;
    private int maxStamina;
    private int mana;
    private int maxMana;

    public GameCharacter(String name) {
        this.name = name;
        this.maxStamina = 100;
        this.stamina = maxStamina;
        this.maxMana = 50;
        this.mana = maxMana;
        this.state = new NormalState();
    }

    // 状态操作
    public void setState(CharacterState state) {
        System.out.println(name + " 状态从 [" + this.state.getStateName() + "] 变为 [" + state.getStateName() + "]");
        this.state = state;
    }

    // 行动方法
    public void move() {
        state.move(this);
    }

    public void attack() {
        state.attack(this);
    }

    public void defend() {
        state.defend(this);
    }

    public void useSkill() {
        state.useSkill(this);
    }

    public void rest() {
        state.rest(this);
    }

    // 属性管理
    public void decreaseStamina(int amount) {
        stamina = Math.max(0, stamina - amount);
    }

    public void increaseStamina(int amount) {
        stamina = Math.min(maxStamina, stamina + amount);
    }

    public void decreaseMana(int amount) {
        mana = Math.max(0, mana - amount);
    }

    public void increaseMana(int amount) {
        mana = Math.min(maxMana, mana + amount);
    }

    public void showStatus() {
        System.out.println("=== " + name + " 状态 ===");
        System.out.println("当前状态: " + state.getStateName());
        System.out.println("体力: " + stamina + "/" + maxStamina);
        System.out.println("魔法: " + mana + "/" + maxMana);
        System.out.println("可移动: " + (state.canMove() ? "是" : "否"));
        System.out.println("可攻击: " + (state.canAttack() ? "是" : "否"));
        System.out.println("可防御: " + (state.canDefend() ? "是" : "否"));
        System.out.println("================");
    }

    // Getters
    public String getName() { return name; }
    public CharacterState getState() { return state; }
    public int getStamina() { return stamina; }
    public int getMaxStamina() { return maxStamina; }
    public int getMana() { return mana; }
    public int getMaxMana() { return maxMana; }
}

// 使用示例
public class GameCharacterExample {
    public static void main(String[] args) {
        GameCharacter warrior = new GameCharacter("勇者阿尔托");
        warrior.showStatus();

        System.out.println("\n=== 战斗序列 ===");

        // 连续攻击消耗体力
        warrior.attack();
        warrior.attack();
        warrior.useSkill();
        warrior.attack();
        warrior.showStatus();

        // 进入疲劳状态后的行为
        System.out.println("\n=== 疲劳状态测试 ===");
        warrior.attack();
        warrior.move();
        warrior.showStatus();

        // 防御状态测试
        System.out.println("\n=== 防御状态测试 ===");
        warrior.defend();
        warrior.defend();
        warrior.defend();
        warrior.defend(); // 超过3回合自动退出
        warrior.showStatus();

        // 休息恢复
        System.out.println("\n=== 休息恢复测试 ===");
        warrior.rest();
        warrior.rest();
        warrior.rest();
        warrior.rest();
        warrior.showStatus();

        // 测试昏迷状态
        System.out.println("\n=== 昏迷状态测试 ===");
        // 先消耗所有体力
        while (warrior.getStamina() > 0) {
            warrior.attack();
        }
        warrior.showStatus();

        // 尝试在昏迷状态下行动
        warrior.move();
        warrior.attack();
        warrior.defend();

        // 休息恢复
        warrior.rest();
        warrior.rest();
        warrior.rest();
        warrior.showStatus();
    }
}
```

## ⚡ 高级应用

### 状态机的可视化管理
```java
// 状态转换记录
class StateTransition {
    private String fromState;
    private String toState;
    private String trigger;
    private LocalDateTime timestamp;

    public StateTransition(String fromState, String toState, String trigger) {
        this.fromState = fromState;
        this.toState = toState;
        this.trigger = trigger;
        this.timestamp = LocalDateTime.now();
    }

    @Override
    public String toString() {
        return String.format("[%s] %s → %s (触发器: %s)",
                timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss")),
                fromState, toState, trigger);
    }
}

// 增强的上下文类
class EnhancedContext {
    private State currentState;
    private List<StateTransition> history = new ArrayList<>();
    private Map<String, Set<String>> allowedTransitions = new HashMap<>();

    public EnhancedContext(State initialState) {
        this.currentState = initialState;
        initializeTransitionRules();
    }

    private void initializeTransitionRules() {
        // 定义允许的状态转换
        allowedTransitions.put("stopped", Set.of("playing"));
        allowedTransitions.put("playing", Set.of("paused", "stopped"));
        allowedTransitions.put("paused", Set.of("playing", "stopped"));
    }

    public boolean setState(State newState, String trigger) {
        String currentStateName = currentState.getClass().getSimpleName();
        String newStateName = newState.getClass().getSimpleName();

        // 检查是否允许这种转换
        if (isTransitionAllowed(currentStateName, newStateName)) {
            history.add(new StateTransition(currentStateName, newStateName, trigger));
            this.currentState = newState;
            return true;
        } else {
            System.out.println("不允许从 " + currentStateName + " 转换到 " + newStateName);
            return false;
        }
    }

    private boolean isTransitionAllowed(String from, String to) {
        Set<String> allowed = allowedTransitions.get(from.toLowerCase());
        return allowed != null && allowed.contains(to.toLowerCase());
    }

    public void showTransitionHistory() {
        System.out.println("=== 状态转换历史 ===");
        for (StateTransition transition : history) {
            System.out.println(transition);
        }
    }
}
```

### 与观察者模式结合
```java
interface StateChangeListener {
    void onStateChanged(String oldState, String newState, String context);
}

class ObservableStateMachine {
    private State currentState;
    private List<StateChangeListener> listeners = new ArrayList<>();

    public void addStateChangeListener(StateChangeListener listener) {
        listeners.add(listener);
    }

    public void setState(State newState, String trigger) {
        String oldState = currentState != null ? currentState.getClass().getSimpleName() : "None";
        String newStateName = newState.getClass().getSimpleName();

        this.currentState = newState;

        // 通知所有监听器
        for (StateChangeListener listener : listeners) {
            listener.onStateChanged(oldState, newStateName, trigger);
        }
    }
}
```

## ✅ 优势分析

### 1. **消除条件语句**
将复杂的if-else或switch语句替换为多态，使代码更清晰。

### 2. **状态逻辑封装**
每个状态的行为被封装在独立的类中，便于维护和扩展。

### 3. **状态转换明确**
状态间的转换关系更加明确，容易理解和调试。

### 4. **符合开闭原则**
新增状态不需要修改现有代码。

## ⚠️ 注意事项

### 1. **避免状态爆炸**
```java
// 错误示例：为每个细微差别创建状态
class VerySpecificState implements State {
    // 避免创建过于具体的状态
}

// 正确做法：使用参数化状态
class ParameterizedState implements State {
    private StateParameter parameter;

    public ParameterizedState(StateParameter parameter) {
        this.parameter = parameter;
    }
}
```

### 2. **状态共享问题**
状态对象通常应该是无状态的，或者使用原型模式创建新实例。

### 3. **内存管理**
注意状态对象的生命周期，避免内存泄漏。

## 🆚 与其他模式对比

| 特性 | 状态模式 | 策略模式 | 命令模式 |
|------|----------|----------|----------|
| 目的 | 管理状态 | 选择算法 | 封装请求 |
| 转换 | 内部转换 | 外部选择 | 不涉及 |
| 上下文依赖 | 强依赖 | 弱依赖 | 无依赖 |
| 状态记忆 | 有状态 | 无状态 | 有历史 |

## 🎯 实战建议

### 1. **何时使用状态模式**
- 对象行为依赖于其状态
- 有复杂的状态转换逻辑
- 存在大量条件语句判断状态
- 状态转换规则复杂

### 2. **设计原则**
```java
// 好的状态设计
interface State {
    void handleAction(Context context, Action action);
    boolean canTransitionTo(Class<? extends State> targetState);
    String getStateName();
}

// 避免状态类之间的强耦合
class GoodState implements State {
    @Override
    public void handleAction(Context context, Action action) {
        // 处理逻辑
        if (shouldTransition(action)) {
            context.setState(createNextState());
        }
    }

    private State createNextState() {
        // 通过工厂或其他方式创建下一个状态
        return StateFactory.createState("nextState");
    }
}
```

### 3. **与Spring状态机结合**
```java
@Configuration
@EnableStateMachine
public class StateMachineConfig extends StateMachineConfigurerAdapter<States, Events> {

    @Override
    public void configure(StateMachineStateConfigurer<States, Events> states)
            throws Exception {
        states
            .withStates()
                .initial(States.PENDING)
                .state(States.PAID)
                .state(States.SHIPPED)
                .end(States.DELIVERED);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
            throws Exception {
        transitions
            .withExternal()
                .source(States.PENDING).target(States.PAID).event(Events.PAY)
                .and()
            .withExternal()
                .source(States.PAID).target(States.SHIPPED).event(Events.SHIP)
                .and()
            .withExternal()
                .source(States.SHIPPED).target(States.DELIVERED).event(Events.DELIVER);
    }
}
```

## 🧠 记忆技巧

**口诀：状态改变行为变**
- **状**态封装成类别
- **态**度决定行为
- **改**变状态要谨慎
- **变**化逻辑要清晰
- **行**动依赖当前态
- **为**每状态定规则

**形象比喻：**
状态模式就像**人的情绪状态**：
- 高兴时：说话幽默，行动积极
- 生气时：语言尖锐，动作急躁
- 疲劳时：反应迟缓，动作缓慢
- 同样的刺激，不同状态下的反应完全不同

## 🎉 总结

状态模式是一种优雅的设计模式，它让对象的行为随状态改变而改变，消除了复杂的条件判断语句。通过将状态封装成独立的类，我们获得了更好的可维护性和可扩展性。

**核心思想：** 🎭 让对象的行为随状态而变，让状态转换更加优雅可控！

下一篇我们将学习**访问者模式**，看看如何在不修改元素类的情况下定义新的操作！ 🚀