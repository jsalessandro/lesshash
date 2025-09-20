---
title: "使用数据结构和算法实现一个短网址系统"
date: 2024-12-20T13:00:00+08:00
lastmod: 2024-12-20T13:00:00+08:00
draft: false
keywords: [短网址, URL缩短, 哈希算法, Base62编码, 布隆过滤器, 缓存, 数据结构, 算法]
description: "详细剖析短网址系统的设计与实现，涵盖Base62编码、哈希算法、布隆过滤器、LRU缓存等核心数据结构和算法"
tags: [数据结构, 算法, 短网址, 系统设计, 哈希, 缓存]
categories: [数据结构与算法]
author: "lesshash"
---

短网址系统是一个看似简单但涉及多种数据结构和算法的经典系统设计案例。本文将深入剖析如何使用各种数据结构和算法来构建一个高性能、高可用的短网址服务，类似于bit.ly、t.co等知名服务。

## 系统需求分析

### 功能需求

1. **URL缩短**：将长URL转换为短URL
2. **URL还原**：通过短URL重定向到原始URL
3. **自定义短链**：支持用户自定义短链别名
4. **统计分析**：点击量、来源分析等统计功能
5. **有效期管理**：支持设置链接过期时间
6. **批量操作**：批量生成和管理短链

### 非功能需求

1. **高性能**：支持高并发读写操作
2. **高可用**：99.9%以上的可用性
3. **低延迟**：亚秒级响应时间
4. **可扩展**：支持水平扩展
5. **数据一致性**：保证数据的准确性
6. **安全性**：防止恶意URL和滥用

### 技术挑战

1. **唯一性保证**：如何保证生成的短链唯一
2. **编码算法**：选择合适的编码方案
3. **存储优化**：海量数据的存储和查询优化
4. **缓存策略**：提高热点数据访问速度
5. **分布式一致性**：多节点环境下的数据一致性

## 核心算法设计

### 1. Base62编码算法

Base62编码使用62个字符（0-9, a-z, A-Z）来表示数字，能够用较短的字符串表示较大的数字。

```java
public class Base62Encoder {
    private static final String ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private static final int BASE = ALPHABET.length();

    // 将数字编码为Base62字符串
    public static String encode(long number) {
        if (number == 0) {
            return String.valueOf(ALPHABET.charAt(0));
        }

        StringBuilder result = new StringBuilder();
        while (number > 0) {
            result.append(ALPHABET.charAt((int) (number % BASE)));
            number /= BASE;
        }

        return result.reverse().toString();
    }

    // 将Base62字符串解码为数字
    public static long decode(String encoded) {
        long result = 0;
        long power = 1;

        for (int i = encoded.length() - 1; i >= 0; i--) {
            char c = encoded.charAt(i);
            int index = ALPHABET.indexOf(c);
            if (index == -1) {
                throw new IllegalArgumentException("Invalid character in encoded string: " + c);
            }
            result += index * power;
            power *= BASE;
        }

        return result;
    }

    // 生成指定长度的随机Base62字符串
    public static String generateRandom(int length) {
        StringBuilder result = new StringBuilder();
        Random random = new SecureRandom();

        for (int i = 0; i < length; i++) {
            result.append(ALPHABET.charAt(random.nextInt(BASE)));
        }

        return result.toString();
    }

    // 计算指定长度可以表示的最大数字
    public static long getMaxValue(int length) {
        return (long) Math.pow(BASE, length) - 1;
    }

    // 计算表示指定数字需要的最小长度
    public static int getMinLength(long number) {
        if (number == 0) {
            return 1;
        }
        return (int) Math.ceil(Math.log(number + 1) / Math.log(BASE));
    }
}

// Base62编码器的测试和基准测试
public class Base62EncoderTest {
    public static void main(String[] args) {
        // 基本测试
        testBasicEncodeDecode();

        // 性能测试
        performanceBenchmark();

        // 容量计算
        calculateCapacity();
    }

    private static void testBasicEncodeDecode() {
        System.out.println("=== Base62 编码解码测试 ===");

        long[] testNumbers = {0, 1, 61, 62, 3843, 238327, 14776335};

        for (long number : testNumbers) {
            String encoded = Base62Encoder.encode(number);
            long decoded = Base62Encoder.decode(encoded);

            System.out.printf("数字: %d, 编码: %s, 解码: %d, 正确: %b%n",
                            number, encoded, decoded, number == decoded);
        }
    }

    private static void performanceBenchmark() {
        System.out.println("\n=== 性能基准测试 ===");

        int iterations = 1000000;
        long[] numbers = new long[iterations];
        Random random = new Random();

        // 生成测试数据
        for (int i = 0; i < iterations; i++) {
            numbers[i] = Math.abs(random.nextLong() % 1000000000L);
        }

        // 编码性能测试
        long startTime = System.nanoTime();
        for (long number : numbers) {
            Base62Encoder.encode(number);
        }
        long encodingTime = System.nanoTime() - startTime;

        // 编码并解码性能测试
        String[] encoded = new String[iterations];
        startTime = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            encoded[i] = Base62Encoder.encode(numbers[i]);
        }
        long bothTime = System.nanoTime() - startTime;

        startTime = System.nanoTime();
        for (String enc : encoded) {
            Base62Encoder.decode(enc);
        }
        long decodingTime = System.nanoTime() - startTime;

        System.out.printf("编码 %d 次耗时: %.2f ms (%.2f ns/op)%n",
                         iterations, encodingTime / 1e6, (double) encodingTime / iterations);
        System.out.printf("解码 %d 次耗时: %.2f ms (%.2f ns/op)%n",
                         iterations, decodingTime / 1e6, (double) decodingTime / iterations);
    }

    private static void calculateCapacity() {
        System.out.println("\n=== 容量计算 ===");

        for (int length = 1; length <= 10; length++) {
            long maxValue = Base62Encoder.getMaxValue(length);
            System.out.printf("长度 %d: 最大值 %,d (%s)%n",
                            length, maxValue, formatNumber(maxValue));
        }
    }

    private static String formatNumber(long number) {
        if (number < 1_000L) return String.valueOf(number);
        if (number < 1_000_000L) return String.format("%.1fK", number / 1_000.0);
        if (number < 1_000_000_000L) return String.format("%.1fM", number / 1_000_000.0);
        if (number < 1_000_000_000_000L) return String.format("%.1fB", number / 1_000_000_000.0);
        return String.format("%.1fT", number / 1_000_000_000_000.0);
    }
}
```

### 2. 哈希算法与冲突解决

为了生成短链和防止冲突，我们需要设计合适的哈希算法。

```java
public class URLHashGenerator {
    private final MessageDigest md5Digest;
    private final MessageDigest sha256Digest;

    public URLHashGenerator() {
        try {
            this.md5Digest = MessageDigest.getInstance("MD5");
            this.sha256Digest = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Hash algorithm not available", e);
        }
    }

    // 使用MD5生成短链
    public String generateShortUrlByMD5(String longUrl, int length) {
        byte[] hash = md5Digest.digest(longUrl.getBytes(StandardCharsets.UTF_8));
        long hashValue = 0;

        // 取hash的前8个字节转换为long
        for (int i = 0; i < Math.min(8, hash.length); i++) {
            hashValue = (hashValue << 8) + (hash[i] & 0xff);
        }

        // 确保为正数
        hashValue = Math.abs(hashValue);

        String shortUrl = Base62Encoder.encode(hashValue);

        // 截取指定长度
        if (shortUrl.length() > length) {
            shortUrl = shortUrl.substring(0, length);
        } else if (shortUrl.length() < length) {
            // 不足长度时用随机字符填充
            shortUrl = shortUrl + Base62Encoder.generateRandom(length - shortUrl.length());
        }

        return shortUrl;
    }

    // 使用SHA-256生成短链（多个候选）
    public List<String> generateShortUrlCandidates(String longUrl, int count, int length) {
        Set<String> candidates = new HashSet<>();

        // 原始URL
        candidates.add(generateShortUrlBySHA256(longUrl, length));

        // 添加盐值生成更多候选
        for (int i = 1; candidates.size() < count && i <= count * 2; i++) {
            String saltedUrl = longUrl + "#salt" + i;
            candidates.add(generateShortUrlBySHA256(saltedUrl, length));
        }

        return new ArrayList<>(candidates);
    }

    private String generateShortUrlBySHA256(String input, int length) {
        byte[] hash = sha256Digest.digest(input.getBytes(StandardCharsets.UTF_8));

        // 使用hash的不同部分生成多个可能的短链
        long hashValue = 0;
        for (int i = 0; i < Math.min(8, hash.length); i++) {
            hashValue = (hashValue << 8) + (hash[i] & 0xff);
        }

        hashValue = Math.abs(hashValue);
        String shortUrl = Base62Encoder.encode(hashValue);

        return adjustLength(shortUrl, length);
    }

    private String adjustLength(String shortUrl, int targetLength) {
        if (shortUrl.length() > targetLength) {
            return shortUrl.substring(0, targetLength);
        } else if (shortUrl.length() < targetLength) {
            return shortUrl + Base62Encoder.generateRandom(targetLength - shortUrl.length());
        }
        return shortUrl;
    }

    // 一致性哈希生成器（用于分布式场景）
    public static class ConsistentHashGenerator {
        private final TreeMap<Long, String> ring;
        private final int virtualNodes;
        private final MessageDigest md5;

        public ConsistentHashGenerator(List<String> nodes, int virtualNodes) {
            this.ring = new TreeMap<>();
            this.virtualNodes = virtualNodes;
            try {
                this.md5 = MessageDigest.getInstance("MD5");
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(e);
            }

            // 初始化一致性哈希环
            for (String node : nodes) {
                addNode(node);
            }
        }

        public void addNode(String node) {
            for (int i = 0; i < virtualNodes; i++) {
                String virtualNode = node + "#" + i;
                long hash = hash(virtualNode);
                ring.put(hash, node);
            }
        }

        public void removeNode(String node) {
            for (int i = 0; i < virtualNodes; i++) {
                String virtualNode = node + "#" + i;
                long hash = hash(virtualNode);
                ring.remove(hash);
            }
        }

        public String getNode(String key) {
            if (ring.isEmpty()) {
                return null;
            }

            long hash = hash(key);
            Map.Entry<Long, String> entry = ring.ceilingEntry(hash);

            if (entry == null) {
                // 超过最大值，返回第一个节点
                entry = ring.firstEntry();
            }

            return entry.getValue();
        }

        private long hash(String key) {
            md5.reset();
            byte[] digest = md5.digest(key.getBytes(StandardCharsets.UTF_8));

            long hash = 0;
            for (int i = 0; i < 4; i++) {
                hash <<= 8;
                hash |= ((int) digest[i]) & 0xFF;
            }

            return hash;
        }
    }
}
```

### 3. 布隆过滤器优化

使用布隆过滤器来快速检测URL是否已存在，减少数据库查询。

```java
public class URLBloomFilter {
    private final BitSet bitSet;
    private final int size;
    private final int hashFunctionCount;
    private final MessageDigest[] digestFunctions;

    public URLBloomFilter(int expectedElements, double falsePositiveRate) {
        this.size = calculateOptimalSize(expectedElements, falsePositiveRate);
        this.hashFunctionCount = calculateOptimalHashFunctions(expectedElements, size);
        this.bitSet = new BitSet(size);

        // 初始化多个哈希函数
        this.digestFunctions = new MessageDigest[hashFunctionCount];
        try {
            for (int i = 0; i < hashFunctionCount; i++) {
                digestFunctions[i] = MessageDigest.getInstance("SHA-256");
            }
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }

    // 计算最优位数组大小
    private int calculateOptimalSize(int expectedElements, double falsePositiveRate) {
        return (int) (-expectedElements * Math.log(falsePositiveRate) / (Math.log(2) * Math.log(2)));
    }

    // 计算最优哈希函数数量
    private int calculateOptimalHashFunctions(int expectedElements, int size) {
        return Math.max(1, (int) Math.round((double) size / expectedElements * Math.log(2)));
    }

    // 添加URL到布隆过滤器
    public void add(String url) {
        for (int i = 0; i < hashFunctionCount; i++) {
            int hash = hash(url, i);
            bitSet.set(Math.abs(hash % size));
        }
    }

    // 检查URL是否可能存在
    public boolean mightContain(String url) {
        for (int i = 0; i < hashFunctionCount; i++) {
            int hash = hash(url, i);
            if (!bitSet.get(Math.abs(hash % size))) {
                return false;
            }
        }
        return true;
    }

    // 生成多个哈希值
    private int hash(String url, int seed) {
        MessageDigest digest = digestFunctions[seed % digestFunctions.length];
        digest.reset();
        digest.update(url.getBytes(StandardCharsets.UTF_8));
        digest.update(String.valueOf(seed).getBytes(StandardCharsets.UTF_8));

        byte[] hashBytes = digest.digest();
        int hash = 0;

        // 将字节数组转换为int
        for (int i = 0; i < Math.min(4, hashBytes.length); i++) {
            hash = (hash << 8) | (hashBytes[i] & 0xFF);
        }

        return hash;
    }

    // 获取当前误判率估计
    public double getCurrentFalsePositiveRate() {
        int setBits = bitSet.cardinality();
        return Math.pow((double) setBits / size, hashFunctionCount);
    }

    // 重置布隆过滤器
    public void clear() {
        bitSet.clear();
    }

    // 获取统计信息
    public BloomFilterStats getStats() {
        BloomFilterStats stats = new BloomFilterStats();
        stats.setSize(size);
        stats.setHashFunctionCount(hashFunctionCount);
        stats.setBitsSet(bitSet.cardinality());
        stats.setCurrentFalsePositiveRate(getCurrentFalsePositiveRate());
        return stats;
    }

    public static class BloomFilterStats {
        private int size;
        private int hashFunctionCount;
        private int bitsSet;
        private double currentFalsePositiveRate;

        // getter和setter方法
        public int getSize() { return size; }
        public void setSize(int size) { this.size = size; }

        public int getHashFunctionCount() { return hashFunctionCount; }
        public void setHashFunctionCount(int hashFunctionCount) { this.hashFunctionCount = hashFunctionCount; }

        public int getBitsSet() { return bitsSet; }
        public void setBitsSet(int bitsSet) { this.bitsSet = bitsSet; }

        public double getCurrentFalsePositiveRate() { return currentFalsePositiveRate; }
        public void setCurrentFalsePositiveRate(double currentFalsePositiveRate) {
            this.currentFalsePositiveRate = currentFalsePositiveRate;
        }
    }

    // 分布式布隆过滤器
    public static class DistributedBloomFilter {
        private final RedisTemplate<String, String> redisTemplate;
        private final String keyPrefix;
        private final int size;
        private final int hashFunctionCount;

        private static final String LUA_SCRIPT_ADD = """
            local key = KEYS[1]
            local positions = cjson.decode(ARGV[1])

            for i, pos in ipairs(positions) do
                redis.call('setbit', key, pos, 1)
            end

            redis.call('expire', key, 86400)
            return 1
            """;

        private static final String LUA_SCRIPT_CHECK = """
            local key = KEYS[1]
            local positions = cjson.decode(ARGV[1])

            for i, pos in ipairs(positions) do
                if redis.call('getbit', key, pos) == 0 then
                    return 0
                end
            end

            return 1
            """;

        private final RedisScript<Long> addScript;
        private final RedisScript<Long> checkScript;

        public DistributedBloomFilter(RedisTemplate<String, String> redisTemplate,
                                    String keyPrefix,
                                    int expectedElements,
                                    double falsePositiveRate) {
            this.redisTemplate = redisTemplate;
            this.keyPrefix = keyPrefix;
            this.size = calculateOptimalSize(expectedElements, falsePositiveRate);
            this.hashFunctionCount = calculateOptimalHashFunctions(expectedElements, size);
            this.addScript = new DefaultRedisScript<>(LUA_SCRIPT_ADD, Long.class);
            this.checkScript = new DefaultRedisScript<>(LUA_SCRIPT_CHECK, Long.class);
        }

        public void add(String url) {
            String key = keyPrefix + ":bloom";
            List<Integer> positions = calculatePositions(url);

            List<String> keys = Collections.singletonList(key);
            String positionsJson = JsonUtils.toJson(positions);

            redisTemplate.execute(addScript, keys, positionsJson);
        }

        public boolean mightContain(String url) {
            String key = keyPrefix + ":bloom";
            List<Integer> positions = calculatePositions(url);

            List<String> keys = Collections.singletonList(key);
            String positionsJson = JsonUtils.toJson(positions);

            Long result = redisTemplate.execute(checkScript, keys, positionsJson);
            return result != null && result == 1;
        }

        private List<Integer> calculatePositions(String url) {
            List<Integer> positions = new ArrayList<>();

            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");

                for (int i = 0; i < hashFunctionCount; i++) {
                    digest.reset();
                    digest.update(url.getBytes(StandardCharsets.UTF_8));
                    digest.update(String.valueOf(i).getBytes(StandardCharsets.UTF_8));

                    byte[] hash = digest.digest();
                    int hashInt = Math.abs(ByteBuffer.wrap(hash).getInt());
                    positions.add(hashInt % size);
                }
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException("SHA-256 not available", e);
            }

            return positions;
        }

        private int calculateOptimalSize(int expectedElements, double falsePositiveRate) {
            return (int) (-expectedElements * Math.log(falsePositiveRate) / (Math.log(2) * Math.log(2)));
        }

        private int calculateOptimalHashFunctions(int expectedElements, int size) {
            return Math.max(1, (int) Math.round((double) size / expectedElements * Math.log(2)));
        }
    }
}
```

## 核心数据结构实现

### 1. URL映射存储结构

```java
public class URLMappingStore {
    // URL映射实体
    public static class URLMapping {
        private String shortUrl;
        private String longUrl;
        private String userId;
        private LocalDateTime createdAt;
        private LocalDateTime expiresAt;
        private long clickCount;
        private String customAlias;
        private Map<String, String> metadata;

        public URLMapping() {
            this.createdAt = LocalDateTime.now();
            this.clickCount = 0;
            this.metadata = new HashMap<>();
        }

        public URLMapping(String shortUrl, String longUrl, String userId) {
            this();
            this.shortUrl = shortUrl;
            this.longUrl = longUrl;
            this.userId = userId;
        }

        // getter和setter方法
        public String getShortUrl() { return shortUrl; }
        public void setShortUrl(String shortUrl) { this.shortUrl = shortUrl; }

        public String getLongUrl() { return longUrl; }
        public void setLongUrl(String longUrl) { this.longUrl = longUrl; }

        public String getUserId() { return userId; }
        public void setUserId(String userId) { this.userId = userId; }

        public LocalDateTime getCreatedAt() { return createdAt; }
        public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

        public LocalDateTime getExpiresAt() { return expiresAt; }
        public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }

        public long getClickCount() { return clickCount; }
        public void setClickCount(long clickCount) { this.clickCount = clickCount; }

        public void incrementClickCount() { this.clickCount++; }

        public String getCustomAlias() { return customAlias; }
        public void setCustomAlias(String customAlias) { this.customAlias = customAlias; }

        public Map<String, String> getMetadata() { return metadata; }
        public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }

        public boolean isExpired() {
            return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
        }
    }

    // 内存存储实现
    public static class InMemoryURLMappingStore {
        private final ConcurrentHashMap<String, URLMapping> shortToLongMap;
        private final ConcurrentHashMap<String, String> longToShortMap;
        private final ConcurrentHashMap<String, Set<String>> userUrlsMap;

        public InMemoryURLMappingStore() {
            this.shortToLongMap = new ConcurrentHashMap<>();
            this.longToShortMap = new ConcurrentHashMap<>();
            this.userUrlsMap = new ConcurrentHashMap<>();
        }

        public void save(URLMapping mapping) {
            shortToLongMap.put(mapping.getShortUrl(), mapping);
            longToShortMap.put(mapping.getLongUrl(), mapping.getShortUrl());

            if (mapping.getUserId() != null) {
                userUrlsMap.computeIfAbsent(mapping.getUserId(), k -> ConcurrentHashMap.newKeySet())
                          .add(mapping.getShortUrl());
            }
        }

        public URLMapping findByShortUrl(String shortUrl) {
            URLMapping mapping = shortToLongMap.get(shortUrl);
            if (mapping != null && mapping.isExpired()) {
                delete(shortUrl);
                return null;
            }
            return mapping;
        }

        public String findShortUrlByLongUrl(String longUrl) {
            return longToShortMap.get(longUrl);
        }

        public Set<String> findUrlsByUserId(String userId) {
            return userUrlsMap.getOrDefault(userId, Collections.emptySet());
        }

        public boolean exists(String shortUrl) {
            URLMapping mapping = shortToLongMap.get(shortUrl);
            return mapping != null && !mapping.isExpired();
        }

        public void delete(String shortUrl) {
            URLMapping mapping = shortToLongMap.remove(shortUrl);
            if (mapping != null) {
                longToShortMap.remove(mapping.getLongUrl());
                if (mapping.getUserId() != null) {
                    Set<String> userUrls = userUrlsMap.get(mapping.getUserId());
                    if (userUrls != null) {
                        userUrls.remove(shortUrl);
                    }
                }
            }
        }

        public void incrementClickCount(String shortUrl) {
            URLMapping mapping = shortToLongMap.get(shortUrl);
            if (mapping != null && !mapping.isExpired()) {
                mapping.incrementClickCount();
            }
        }

        public int size() {
            return shortToLongMap.size();
        }

        public void cleanup() {
            Set<String> expiredUrls = shortToLongMap.entrySet().stream()
                    .filter(entry -> entry.getValue().isExpired())
                    .map(Map.Entry::getKey)
                    .collect(Collectors.toSet());

            expiredUrls.forEach(this::delete);
        }
    }

    // Redis存储实现
    public static class RedisURLMappingStore {
        private final RedisTemplate<String, String> redisTemplate;
        private final String keyPrefix;

        private static final String LUA_SCRIPT_INCREMENT_CLICK = """
            local shortUrlKey = KEYS[1]
            local mapping = redis.call('get', shortUrlKey)

            if mapping then
                local data = cjson.decode(mapping)
                data.clickCount = (data.clickCount or 0) + 1
                redis.call('set', shortUrlKey, cjson.encode(data))
                return data.clickCount
            else
                return 0
            end
            """;

        private final RedisScript<Long> incrementClickScript;

        public RedisURLMappingStore(RedisTemplate<String, String> redisTemplate, String keyPrefix) {
            this.redisTemplate = redisTemplate;
            this.keyPrefix = keyPrefix;
            this.incrementClickScript = new DefaultRedisScript<>(LUA_SCRIPT_INCREMENT_CLICK, Long.class);
        }

        public void save(URLMapping mapping) {
            String shortUrlKey = keyPrefix + ":short:" + mapping.getShortUrl();
            String longUrlKey = keyPrefix + ":long:" + DigestUtils.sha256Hex(mapping.getLongUrl());
            String userKey = keyPrefix + ":user:" + mapping.getUserId();

            String mappingJson = JsonUtils.toJson(mapping);

            // 保存短链到长链的映射
            if (mapping.getExpiresAt() != null) {
                Duration ttl = Duration.between(LocalDateTime.now(), mapping.getExpiresAt());
                redisTemplate.opsForValue().set(shortUrlKey, mappingJson, ttl);
            } else {
                redisTemplate.opsForValue().set(shortUrlKey, mappingJson);
            }

            // 保存长链到短链的映射
            redisTemplate.opsForValue().set(longUrlKey, mapping.getShortUrl());

            // 保存用户的URL列表
            if (mapping.getUserId() != null) {
                redisTemplate.opsForSet().add(userKey, mapping.getShortUrl());
            }
        }

        public URLMapping findByShortUrl(String shortUrl) {
            String key = keyPrefix + ":short:" + shortUrl;
            String mappingJson = redisTemplate.opsForValue().get(key);

            if (mappingJson != null) {
                URLMapping mapping = JsonUtils.fromJson(mappingJson, URLMapping.class);
                if (mapping.isExpired()) {
                    delete(shortUrl);
                    return null;
                }
                return mapping;
            }

            return null;
        }

        public String findShortUrlByLongUrl(String longUrl) {
            String key = keyPrefix + ":long:" + DigestUtils.sha256Hex(longUrl);
            return redisTemplate.opsForValue().get(key);
        }

        public Set<String> findUrlsByUserId(String userId) {
            String key = keyPrefix + ":user:" + userId;
            return redisTemplate.opsForSet().members(key);
        }

        public boolean exists(String shortUrl) {
            String key = keyPrefix + ":short:" + shortUrl;
            return redisTemplate.hasKey(key);
        }

        public void delete(String shortUrl) {
            URLMapping mapping = findByShortUrl(shortUrl);
            if (mapping != null) {
                String shortUrlKey = keyPrefix + ":short:" + shortUrl;
                String longUrlKey = keyPrefix + ":long:" + DigestUtils.sha256Hex(mapping.getLongUrl());
                String userKey = keyPrefix + ":user:" + mapping.getUserId();

                redisTemplate.delete(shortUrlKey);
                redisTemplate.delete(longUrlKey);

                if (mapping.getUserId() != null) {
                    redisTemplate.opsForSet().remove(userKey, shortUrl);
                }
            }
        }

        public long incrementClickCount(String shortUrl) {
            String key = keyPrefix + ":short:" + shortUrl;
            List<String> keys = Collections.singletonList(key);

            Long newCount = redisTemplate.execute(incrementClickScript, keys);
            return newCount != null ? newCount : 0;
        }
    }
}
```

### 2. LRU缓存实现

为了提高热点数据的访问速度，实现一个LRU缓存。

```java
public class URLLRUCache<K, V> {
    private final int capacity;
    private final Map<K, Node<K, V>> cache;
    private final Node<K, V> head;
    private final Node<K, V> tail;

    // 双向链表节点
    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev;
        Node<K, V> next;
        long accessTime;

        Node(K key, V value) {
            this.key = key;
            this.value = value;
            this.accessTime = System.currentTimeMillis();
        }
    }

    public URLLRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new ConcurrentHashMap<>();

        // 创建虚拟头尾节点
        this.head = new Node<>(null, null);
        this.tail = new Node<>(null, null);
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K, V> node = cache.get(key);
        if (node != null) {
            // 更新访问时间并移动到链表头部
            node.accessTime = System.currentTimeMillis();
            moveToHead(node);
            return node.value;
        }
        return null;
    }

    public void put(K key, V value) {
        Node<K, V> existingNode = cache.get(key);

        if (existingNode != null) {
            // 更新现有节点
            existingNode.value = value;
            existingNode.accessTime = System.currentTimeMillis();
            moveToHead(existingNode);
        } else {
            // 添加新节点
            Node<K, V> newNode = new Node<>(key, value);

            if (cache.size() >= capacity) {
                // 删除最少使用的节点
                removeLeastUsed();
            }

            cache.put(key, newNode);
            addToHead(newNode);
        }
    }

    public V remove(K key) {
        Node<K, V> node = cache.remove(key);
        if (node != null) {
            removeFromList(node);
            return node.value;
        }
        return null;
    }

    public boolean containsKey(K key) {
        return cache.containsKey(key);
    }

    public int size() {
        return cache.size();
    }

    public void clear() {
        cache.clear();
        head.next = tail;
        tail.prev = head;
    }

    // 移动节点到链表头部
    private synchronized void moveToHead(Node<K, V> node) {
        removeFromList(node);
        addToHead(node);
    }

    // 添加节点到链表头部
    private synchronized void addToHead(Node<K, V> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    // 从链表中删除节点
    private synchronized void removeFromList(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    // 删除最少使用的节点
    private synchronized void removeLeastUsed() {
        Node<K, V> lastNode = tail.prev;
        if (lastNode != head) {
            cache.remove(lastNode.key);
            removeFromList(lastNode);
        }
    }

    // 获取缓存统计信息
    public CacheStats getStats() {
        CacheStats stats = new CacheStats();
        stats.setSize(cache.size());
        stats.setCapacity(capacity);

        // 计算平均访问时间
        long totalAccessTime = 0;
        long currentTime = System.currentTimeMillis();

        synchronized (this) {
            Node<K, V> current = head.next;
            while (current != tail) {
                totalAccessTime += (currentTime - current.accessTime);
                current = current.next;
            }
        }

        if (cache.size() > 0) {
            stats.setAverageAge(totalAccessTime / cache.size());
        }

        return stats;
    }

    public static class CacheStats {
        private int size;
        private int capacity;
        private long averageAge;

        public int getSize() { return size; }
        public void setSize(int size) { this.size = size; }

        public int getCapacity() { return capacity; }
        public void setCapacity(int capacity) { this.capacity = capacity; }

        public long getAverageAge() { return averageAge; }
        public void setAverageAge(long averageAge) { this.averageAge = averageAge; }

        public double getLoadFactor() {
            return capacity > 0 ? (double) size / capacity : 0.0;
        }
    }

    // 支持TTL的LRU缓存
    public static class TTLAwareLRUCache<K, V> extends URLLRUCache<K, V> {
        private final Map<K, Long> ttlMap;

        public TTLAwareLRUCache(int capacity) {
            super(capacity);
            this.ttlMap = new ConcurrentHashMap<>();
        }

        public void put(K key, V value, long ttlMillis) {
            super.put(key, value);
            if (ttlMillis > 0) {
                ttlMap.put(key, System.currentTimeMillis() + ttlMillis);
            }
        }

        @Override
        public V get(K key) {
            // 检查是否过期
            Long expireTime = ttlMap.get(key);
            if (expireTime != null && System.currentTimeMillis() > expireTime) {
                remove(key);
                return null;
            }

            return super.get(key);
        }

        @Override
        public V remove(K key) {
            ttlMap.remove(key);
            return super.remove(key);
        }

        @Override
        public void clear() {
            super.clear();
            ttlMap.clear();
        }

        // 清理过期的条目
        public void cleanupExpired() {
            long currentTime = System.currentTimeMillis();
            Set<K> expiredKeys = ttlMap.entrySet().stream()
                    .filter(entry -> entry.getValue() < currentTime)
                    .map(Map.Entry::getKey)
                    .collect(Collectors.toSet());

            expiredKeys.forEach(this::remove);
        }
    }
}
```

## 短网址服务核心实现

### 1. 短网址生成服务

```java
@Service
public class URLShortenerService {
    private final URLMappingStore.RedisURLMappingStore mappingStore;
    private final URLHashGenerator hashGenerator;
    private final URLBloomFilter.DistributedBloomFilter bloomFilter;
    private final URLLRUCache<String, URLMappingStore.URLMapping> cache;
    private final AtomicLong idGenerator;

    private static final int DEFAULT_SHORT_URL_LENGTH = 7;
    private static final int MAX_RETRY_ATTEMPTS = 5;

    public URLShortenerService(RedisTemplate<String, String> redisTemplate) {
        this.mappingStore = new URLMappingStore.RedisURLMappingStore(redisTemplate, "url_shortener");
        this.hashGenerator = new URLHashGenerator();
        this.bloomFilter = new URLBloomFilter.DistributedBloomFilter(
                redisTemplate, "url_shortener", 10_000_000, 0.01);
        this.cache = new URLLRUCache<>(10000);
        this.idGenerator = new AtomicLong(System.currentTimeMillis());
    }

    // 缩短URL
    public ShortenResponse shortenUrl(ShortenRequest request) {
        // 验证输入
        validateShortenRequest(request);

        // 检查是否已存在
        String existingShortUrl = mappingStore.findShortUrlByLongUrl(request.getLongUrl());
        if (existingShortUrl != null) {
            URLMappingStore.URLMapping existing = mappingStore.findByShortUrl(existingShortUrl);
            if (existing != null && !existing.isExpired()) {
                return new ShortenResponse(existingShortUrl, existing);
            }
        }

        // 生成短链
        String shortUrl = generateShortUrl(request);

        // 创建映射
        URLMappingStore.URLMapping mapping = new URLMappingStore.URLMapping(
                shortUrl, request.getLongUrl(), request.getUserId());

        if (request.getExpiresAt() != null) {
            mapping.setExpiresAt(request.getExpiresAt());
        }

        if (request.getCustomAlias() != null) {
            mapping.setCustomAlias(request.getCustomAlias());
        }

        mapping.setMetadata(request.getMetadata());

        // 保存映射
        mappingStore.save(mapping);
        bloomFilter.add(shortUrl);
        cache.put(shortUrl, mapping);

        return new ShortenResponse(shortUrl, mapping);
    }

    // 解析短网址
    public ResolveResponse resolveUrl(String shortUrl) {
        // 先检查缓存
        URLMappingStore.URLMapping mapping = cache.get(shortUrl);

        if (mapping == null) {
            // 使用布隆过滤器快速检测
            if (!bloomFilter.mightContain(shortUrl)) {
                throw new URLNotFoundException("Short URL not found: " + shortUrl);
            }

            // 从存储中获取
            mapping = mappingStore.findByShortUrl(shortUrl);
            if (mapping == null) {
                throw new URLNotFoundException("Short URL not found: " + shortUrl);
            }

            // 加入缓存
            cache.put(shortUrl, mapping);
        }

        // 检查是否过期
        if (mapping.isExpired()) {
            mappingStore.delete(shortUrl);
            cache.remove(shortUrl);
            throw new URLExpiredException("Short URL has expired: " + shortUrl);
        }

        // 增加点击计数
        mappingStore.incrementClickCount(shortUrl);

        return new ResolveResponse(mapping.getLongUrl(), mapping);
    }

    // 生成短链
    private String generateShortUrl(ShortenRequest request) {
        // 如果指定了自定义别名
        if (request.getCustomAlias() != null) {
            String customShortUrl = request.getCustomAlias();
            if (mappingStore.exists(customShortUrl)) {
                throw new DuplicateShortUrlException("Custom alias already exists: " + customShortUrl);
            }
            return customShortUrl;
        }

        // 尝试多种生成策略
        String shortUrl = null;
        int attempts = 0;

        while (shortUrl == null && attempts < MAX_RETRY_ATTEMPTS) {
            attempts++;

            switch (request.getGenerationStrategy()) {
                case HASH_BASED:
                    shortUrl = generateHashBasedShortUrl(request.getLongUrl(), attempts);
                    break;
                case COUNTER_BASED:
                    shortUrl = generateCounterBasedShortUrl();
                    break;
                case RANDOM:
                default:
                    shortUrl = generateRandomShortUrl();
                    break;
            }

            // 检查是否已存在
            if (mappingStore.exists(shortUrl)) {
                shortUrl = null; // 重试
            }
        }

        if (shortUrl == null) {
            throw new ShortUrlGenerationException("Failed to generate unique short URL after " + attempts + " attempts");
        }

        return shortUrl;
    }

    private String generateHashBasedShortUrl(String longUrl, int attempt) {
        String input = longUrl;
        if (attempt > 1) {
            input += "#retry" + attempt;
        }
        return hashGenerator.generateShortUrlByMD5(input, DEFAULT_SHORT_URL_LENGTH);
    }

    private String generateCounterBasedShortUrl() {
        long id = idGenerator.incrementAndGet();
        return Base62Encoder.encode(id);
    }

    private String generateRandomShortUrl() {
        return Base62Encoder.generateRandom(DEFAULT_SHORT_URL_LENGTH);
    }

    private void validateShortenRequest(ShortenRequest request) {
        if (request.getLongUrl() == null || request.getLongUrl().trim().isEmpty()) {
            throw new IllegalArgumentException("Long URL cannot be null or empty");
        }

        if (!isValidUrl(request.getLongUrl())) {
            throw new IllegalArgumentException("Invalid URL format: " + request.getLongUrl());
        }

        if (request.getCustomAlias() != null) {
            if (!isValidCustomAlias(request.getCustomAlias())) {
                throw new IllegalArgumentException("Invalid custom alias: " + request.getCustomAlias());
            }
        }
    }

    private boolean isValidUrl(String url) {
        try {
            new URL(url);
            return true;
        } catch (MalformedURLException e) {
            return false;
        }
    }

    private boolean isValidCustomAlias(String alias) {
        return alias.matches("^[a-zA-Z0-9_-]+$") && alias.length() >= 3 && alias.length() <= 20;
    }

    // 获取用户的所有短链
    public List<URLMappingStore.URLMapping> getUserUrls(String userId) {
        Set<String> shortUrls = mappingStore.findUrlsByUserId(userId);
        List<URLMappingStore.URLMapping> mappings = new ArrayList<>();

        for (String shortUrl : shortUrls) {
            URLMappingStore.URLMapping mapping = mappingStore.findByShortUrl(shortUrl);
            if (mapping != null && !mapping.isExpired()) {
                mappings.add(mapping);
            }
        }

        return mappings;
    }

    // 删除短链
    public void deleteUrl(String shortUrl, String userId) {
        URLMappingStore.URLMapping mapping = mappingStore.findByShortUrl(shortUrl);

        if (mapping == null) {
            throw new URLNotFoundException("Short URL not found: " + shortUrl);
        }

        if (!mapping.getUserId().equals(userId)) {
            throw new UnauthorizedException("User not authorized to delete this URL");
        }

        mappingStore.delete(shortUrl);
        cache.remove(shortUrl);
    }

    // 获取统计信息
    public URLStats getUrlStats(String shortUrl) {
        URLMappingStore.URLMapping mapping = mappingStore.findByShortUrl(shortUrl);

        if (mapping == null) {
            throw new URLNotFoundException("Short URL not found: " + shortUrl);
        }

        URLStats stats = new URLStats();
        stats.setShortUrl(shortUrl);
        stats.setLongUrl(mapping.getLongUrl());
        stats.setClickCount(mapping.getClickCount());
        stats.setCreatedAt(mapping.getCreatedAt());
        stats.setExpiresAt(mapping.getExpiresAt());

        return stats;
    }
}

// 请求和响应类
class ShortenRequest {
    private String longUrl;
    private String userId;
    private String customAlias;
    private LocalDateTime expiresAt;
    private GenerationStrategy generationStrategy = GenerationStrategy.HASH_BASED;
    private Map<String, String> metadata = new HashMap<>();

    // getter和setter方法
    public String getLongUrl() { return longUrl; }
    public void setLongUrl(String longUrl) { this.longUrl = longUrl; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getCustomAlias() { return customAlias; }
    public void setCustomAlias(String customAlias) { this.customAlias = customAlias; }

    public LocalDateTime getExpiresAt() { return expiresAt; }
    public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }

    public GenerationStrategy getGenerationStrategy() { return generationStrategy; }
    public void setGenerationStrategy(GenerationStrategy generationStrategy) { this.generationStrategy = generationStrategy; }

    public Map<String, String> getMetadata() { return metadata; }
    public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }
}

class ShortenResponse {
    private String shortUrl;
    private URLMappingStore.URLMapping mapping;

    public ShortenResponse(String shortUrl, URLMappingStore.URLMapping mapping) {
        this.shortUrl = shortUrl;
        this.mapping = mapping;
    }

    public String getShortUrl() { return shortUrl; }
    public URLMappingStore.URLMapping getMapping() { return mapping; }
}

class ResolveResponse {
    private String longUrl;
    private URLMappingStore.URLMapping mapping;

    public ResolveResponse(String longUrl, URLMappingStore.URLMapping mapping) {
        this.longUrl = longUrl;
        this.mapping = mapping;
    }

    public String getLongUrl() { return longUrl; }
    public URLMappingStore.URLMapping getMapping() { return mapping; }
}

class URLStats {
    private String shortUrl;
    private String longUrl;
    private long clickCount;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;

    // getter和setter方法
    public String getShortUrl() { return shortUrl; }
    public void setShortUrl(String shortUrl) { this.shortUrl = shortUrl; }

    public String getLongUrl() { return longUrl; }
    public void setLongUrl(String longUrl) { this.longUrl = longUrl; }

    public long getClickCount() { return clickCount; }
    public void setClickCount(long clickCount) { this.clickCount = clickCount; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getExpiresAt() { return expiresAt; }
    public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }
}

enum GenerationStrategy {
    HASH_BASED,
    COUNTER_BASED,
    RANDOM
}

// 异常类
class URLNotFoundException extends RuntimeException {
    public URLNotFoundException(String message) { super(message); }
}

class URLExpiredException extends RuntimeException {
    public URLExpiredException(String message) { super(message); }
}

class DuplicateShortUrlException extends RuntimeException {
    public DuplicateShortUrlException(String message) { super(message); }
}

class ShortUrlGenerationException extends RuntimeException {
    public ShortUrlGenerationException(String message) { super(message); }
}

class UnauthorizedException extends RuntimeException {
    public UnauthorizedException(String message) { super(message); }
}
```

### 2. REST API控制器

```java
@RestController
@RequestMapping("/api/v1")
@Validated
public class URLShortenerController {
    private final URLShortenerService urlShortenerService;

    public URLShortenerController(URLShortenerService urlShortenerService) {
        this.urlShortenerService = urlShortenerService;
    }

    // 缩短URL
    @PostMapping("/shorten")
    public ResponseEntity<ShortenResponse> shortenUrl(@RequestBody @Valid ShortenRequest request,
                                                     HttpServletRequest httpRequest) {
        // 从请求中获取用户ID（实际应用中从JWT token获取）
        String userId = httpRequest.getHeader("X-User-Id");
        request.setUserId(userId);

        ShortenResponse response = urlShortenerService.shortenUrl(request);
        return ResponseEntity.ok(response);
    }

    // 重定向到原始URL
    @GetMapping("/{shortUrl}")
    public ResponseEntity<Void> redirect(@PathVariable String shortUrl,
                                       HttpServletRequest request,
                                       HttpServletResponse response) {
        try {
            ResolveResponse resolveResponse = urlShortenerService.resolveUrl(shortUrl);

            // 记录访问信息（可选）
            recordClickAnalytics(shortUrl, request);

            // 301永久重定向或302临时重定向
            return ResponseEntity.status(HttpStatus.FOUND)
                    .location(URI.create(resolveResponse.getLongUrl()))
                    .build();

        } catch (URLNotFoundException | URLExpiredException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // 获取URL信息（不重定向）
    @GetMapping("/{shortUrl}/info")
    public ResponseEntity<ResolveResponse> getUrlInfo(@PathVariable String shortUrl) {
        try {
            ResolveResponse response = urlShortenerService.resolveUrl(shortUrl);
            return ResponseEntity.ok(response);
        } catch (URLNotFoundException | URLExpiredException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // 获取URL统计信息
    @GetMapping("/{shortUrl}/stats")
    public ResponseEntity<URLStats> getUrlStats(@PathVariable String shortUrl) {
        try {
            URLStats stats = urlShortenerService.getUrlStats(shortUrl);
            return ResponseEntity.ok(stats);
        } catch (URLNotFoundException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // 获取用户的所有URL
    @GetMapping("/my-urls")
    public ResponseEntity<List<URLMappingStore.URLMapping>> getUserUrls(HttpServletRequest request) {
        String userId = request.getHeader("X-User-Id");
        if (userId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        List<URLMappingStore.URLMapping> userUrls = urlShortenerService.getUserUrls(userId);
        return ResponseEntity.ok(userUrls);
    }

    // 删除短链
    @DeleteMapping("/{shortUrl}")
    public ResponseEntity<Void> deleteUrl(@PathVariable String shortUrl,
                                        HttpServletRequest request) {
        String userId = request.getHeader("X-User-Id");
        if (userId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        try {
            urlShortenerService.deleteUrl(shortUrl, userId);
            return ResponseEntity.noContent().build();
        } catch (URLNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (UnauthorizedException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

    // 批量缩短URL
    @PostMapping("/batch-shorten")
    public ResponseEntity<List<ShortenResponse>> batchShortenUrls(
            @RequestBody @Valid BatchShortenRequest request,
            HttpServletRequest httpRequest) {

        String userId = httpRequest.getHeader("X-User-Id");
        List<ShortenResponse> responses = new ArrayList<>();

        for (String longUrl : request.getLongUrls()) {
            try {
                ShortenRequest shortenRequest = new ShortenRequest();
                shortenRequest.setLongUrl(longUrl);
                shortenRequest.setUserId(userId);
                shortenRequest.setGenerationStrategy(request.getGenerationStrategy());

                ShortenResponse response = urlShortenerService.shortenUrl(shortenRequest);
                responses.add(response);
            } catch (Exception e) {
                // 记录错误但继续处理其他URL
                ShortenResponse errorResponse = new ShortenResponse(null, null);
                errorResponse.setError(e.getMessage());
                responses.add(errorResponse);
            }
        }

        return ResponseEntity.ok(responses);
    }

    private void recordClickAnalytics(String shortUrl, HttpServletRequest request) {
        // 记录点击分析数据
        // 可以包括：IP地址、User-Agent、Referer、时间戳等
        String ip = getClientIP(request);
        String userAgent = request.getHeader("User-Agent");
        String referer = request.getHeader("Referer");

        // 异步记录到分析系统
        CompletableFuture.runAsync(() -> {
            // 实现分析数据记录逻辑
            System.out.printf("Click recorded: shortUrl=%s, ip=%s, userAgent=%s, referer=%s%n",
                            shortUrl, ip, userAgent, referer);
        });
    }

    private String getClientIP(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        String xRealIP = request.getHeader("X-Real-IP");
        if (xRealIP != null && !xRealIP.isEmpty()) {
            return xRealIP;
        }
        return request.getRemoteAddr();
    }

    // 异常处理
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException e) {
        ErrorResponse error = new ErrorResponse("INVALID_REQUEST", e.getMessage());
        return ResponseEntity.badRequest().body(error);
    }

    @ExceptionHandler(DuplicateShortUrlException.class)
    public ResponseEntity<ErrorResponse> handleDuplicateShortUrl(DuplicateShortUrlException e) {
        ErrorResponse error = new ErrorResponse("DUPLICATE_SHORT_URL", e.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }

    @ExceptionHandler(ShortUrlGenerationException.class)
    public ResponseEntity<ErrorResponse> handleShortUrlGeneration(ShortUrlGenerationException e) {
        ErrorResponse error = new ErrorResponse("GENERATION_FAILED", e.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

class BatchShortenRequest {
    @NotNull
    @Size(min = 1, max = 100)
    private List<String> longUrls;

    private GenerationStrategy generationStrategy = GenerationStrategy.HASH_BASED;

    // getter和setter方法
    public List<String> getLongUrls() { return longUrls; }
    public void setLongUrls(List<String> longUrls) { this.longUrls = longUrls; }

    public GenerationStrategy getGenerationStrategy() { return generationStrategy; }
    public void setGenerationStrategy(GenerationStrategy generationStrategy) { this.generationStrategy = generationStrategy; }
}

class ErrorResponse {
    private String code;
    private String message;
    private long timestamp;

    public ErrorResponse(String code, String message) {
        this.code = code;
        this.message = message;
        this.timestamp = System.currentTimeMillis();
    }

    // getter和setter方法
    public String getCode() { return code; }
    public String getMessage() { return message; }
    public long getTimestamp() { return timestamp; }
}
```

## 性能优化和扩展

### 1. 性能基准测试

```java
public class URLShortenerBenchmark {
    private URLShortenerService urlShortenerService;
    private final Random random = new Random();

    @Setup
    public void setup() {
        // 初始化服务
        RedisTemplate<String, String> redisTemplate = createRedisTemplate();
        urlShortenerService = new URLShortenerService(redisTemplate);
    }

    // 测试URL缩短性能
    public void benchmarkShortenUrl() throws InterruptedException {
        int threadCount = 10;
        int iterationsPerThread = 1000;
        CountDownLatch latch = new CountDownLatch(threadCount);
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);

        long startTime = System.nanoTime();

        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < iterationsPerThread; j++) {
                        ShortenRequest request = new ShortenRequest();
                        request.setLongUrl("https://example.com/very/long/url/path/" + threadId + "/" + j);
                        request.setUserId("user" + threadId);

                        urlShortenerService.shortenUrl(request);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long endTime = System.nanoTime();

        long totalOperations = threadCount * iterationsPerThread;
        long totalTimeMs = (endTime - startTime) / 1_000_000;
        double operationsPerSecond = (double) totalOperations / totalTimeMs * 1000;

        System.out.printf("Shorten URL Benchmark:%n");
        System.out.printf("Total operations: %,d%n", totalOperations);
        System.out.printf("Total time: %,d ms%n", totalTimeMs);
        System.out.printf("Operations per second: %.2f%n", operationsPerSecond);

        executor.shutdown();
    }

    // 测试URL解析性能
    public void benchmarkResolveUrl() throws InterruptedException {
        // 先生成一些短链
        List<String> shortUrls = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            ShortenRequest request = new ShortenRequest();
            request.setLongUrl("https://example.com/url/" + i);
            request.setUserId("testuser");

            ShortenResponse response = urlShortenerService.shortenUrl(request);
            shortUrls.add(response.getShortUrl());
        }

        int threadCount = 20;
        int iterationsPerThread = 500;
        CountDownLatch latch = new CountDownLatch(threadCount);
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);

        long startTime = System.nanoTime();

        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                try {
                    for (int j = 0; j < iterationsPerThread; j++) {
                        String shortUrl = shortUrls.get(random.nextInt(shortUrls.size()));
                        urlShortenerService.resolveUrl(shortUrl);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        long endTime = System.nanoTime();

        long totalOperations = threadCount * iterationsPerThread;
        long totalTimeMs = (endTime - startTime) / 1_000_000;
        double operationsPerSecond = (double) totalOperations / totalTimeMs * 1000;

        System.out.printf("Resolve URL Benchmark:%n");
        System.out.printf("Total operations: %,d%n", totalOperations);
        System.out.printf("Total time: %,d ms%n", totalTimeMs);
        System.out.printf("Operations per second: %.2f%n", operationsPerSecond);

        executor.shutdown();
    }

    public static void main(String[] args) throws InterruptedException {
        URLShortenerBenchmark benchmark = new URLShortenerBenchmark();
        benchmark.setup();

        System.out.println("=== URL Shortener Performance Benchmark ===");
        benchmark.benchmarkShortenUrl();
        System.out.println();
        benchmark.benchmarkResolveUrl();
    }

    private RedisTemplate<String, String> createRedisTemplate() {
        // 创建Redis模板的模拟实现
        // 实际应用中应该使用真实的Redis连接
        return new RedisTemplate<>();
    }
}
```

### 2. 系统监控和指标

```java
@Component
public class URLShortenerMetrics {
    private final MeterRegistry meterRegistry;
    private final Counter shortenCounter;
    private final Counter resolveCounter;
    private final Timer shortenTimer;
    private final Timer resolveTimer;
    private final Gauge cacheHitRatio;
    private final AtomicLong cacheHits = new AtomicLong(0);
    private final AtomicLong cacheMisses = new AtomicLong(0);

    public URLShortenerMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.shortenCounter = Counter.builder("url.shorten.requests")
                .description("Number of URL shorten requests")
                .register(meterRegistry);
        this.resolveCounter = Counter.builder("url.resolve.requests")
                .description("Number of URL resolve requests")
                .register(meterRegistry);
        this.shortenTimer = Timer.builder("url.shorten.duration")
                .description("URL shorten request duration")
                .register(meterRegistry);
        this.resolveTimer = Timer.builder("url.resolve.duration")
                .description("URL resolve request duration")
                .register(meterRegistry);
        this.cacheHitRatio = Gauge.builder("url.cache.hit.ratio")
                .description("Cache hit ratio")
                .register(meterRegistry, this, URLShortenerMetrics::calculateCacheHitRatio);
    }

    public void recordShortenRequest(long durationMs, boolean success) {
        shortenCounter.increment(
                Tags.of(Tag.of("success", String.valueOf(success)))
        );
        shortenTimer.record(durationMs, TimeUnit.MILLISECONDS);
    }

    public void recordResolveRequest(long durationMs, boolean success, boolean cacheHit) {
        resolveCounter.increment(
                Tags.of(
                        Tag.of("success", String.valueOf(success)),
                        Tag.of("cache_hit", String.valueOf(cacheHit))
                )
        );
        resolveTimer.record(durationMs, TimeUnit.MILLISECONDS);

        if (cacheHit) {
            cacheHits.incrementAndGet();
        } else {
            cacheMisses.incrementAndGet();
        }
    }

    private double calculateCacheHitRatio() {
        long hits = cacheHits.get();
        long misses = cacheMisses.get();
        long total = hits + misses;
        return total > 0 ? (double) hits / total : 0.0;
    }

    public SystemMetrics getSystemMetrics() {
        SystemMetrics metrics = new SystemMetrics();
        metrics.setShortenRequestsTotal((long) shortenCounter.count());
        metrics.setResolveRequestsTotal((long) resolveCounter.count());
        metrics.setAverageShortenDuration(shortenTimer.mean(TimeUnit.MILLISECONDS));
        metrics.setAverageResolveDuration(resolveTimer.mean(TimeUnit.MILLISECONDS));
        metrics.setCacheHitRatio(calculateCacheHitRatio());
        return metrics;
    }

    public static class SystemMetrics {
        private long shortenRequestsTotal;
        private long resolveRequestsTotal;
        private double averageShortenDuration;
        private double averageResolveDuration;
        private double cacheHitRatio;

        // getter和setter方法
        public long getShortenRequestsTotal() { return shortenRequestsTotal; }
        public void setShortenRequestsTotal(long shortenRequestsTotal) { this.shortenRequestsTotal = shortenRequestsTotal; }

        public long getResolveRequestsTotal() { return resolveRequestsTotal; }
        public void setResolveRequestsTotal(long resolveRequestsTotal) { this.resolveRequestsTotal = resolveRequestsTotal; }

        public double getAverageShortenDuration() { return averageShortenDuration; }
        public void setAverageShortenDuration(double averageShortenDuration) { this.averageShortenDuration = averageShortenDuration; }

        public double getAverageResolveDuration() { return averageResolveDuration; }
        public void setAverageResolveDuration(double averageResolveDuration) { this.averageResolveDuration = averageResolveDuration; }

        public double getCacheHitRatio() { return cacheHitRatio; }
        public void setCacheHitRatio(double cacheHitRatio) { this.cacheHitRatio = cacheHitRatio; }
    }
}
```

## 应用场景和最佳实践

### 应用场景

1. **社交媒体**：Twitter、微博等字符限制平台
2. **营销推广**：追踪点击效果的营销链接
3. **移动应用**：减少QR码复杂度
4. **邮件营销**：美化邮件中的链接
5. **API服务**：为第三方提供短链服务

### 最佳实践

1. **编码策略选择**
   - Base62提供较好的字符密度
   - 考虑避免容易混淆的字符
   - 预留字符用于特殊用途

2. **存储优化**
   - 使用Redis集群提高性能
   - 实现数据库分片策略
   - 定期清理过期数据

3. **安全考虑**
   - 实现恶意URL检测
   - 添加访问频率限制
   - 记录详细的访问日志

4. **高可用设计**
   - 多数据中心部署
   - 实现故障转移机制
   - 数据备份和恢复策略

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 缩短延迟 | <100ms | URL缩短响应时间 |
| 解析延迟 | <50ms | URL解析响应时间 |
| 缓存命中率 | >90% | 热点数据缓存效果 |
| 可用性 | 99.9% | 系统整体可用性 |
| 吞吐量 | >10K QPS | 系统处理能力 |

## 总结

短网址系统虽然概念简单，但其实现涉及多种核心数据结构和算法：

1. **编码算法**：Base62编码实现高效的数字到字符串转换
2. **哈希算法**：MD5、SHA-256保证URL唯一性和分布均匀
3. **布隆过滤器**：快速检测URL存在性，减少存储查询
4. **LRU缓存**：提高热点数据访问速度
5. **一致性哈希**：支持分布式部署和扩展

这些技术的合理组合，构建了一个高性能、高可用的短网址服务系统。通过深入理解这些数据结构和算法的原理，我们可以设计出更加优秀的系统架构，并为其他类似的系统设计提供有价值的参考。

短网址系统的设计不仅仅是技术实现，更是对系统架构、性能优化、数据结构选择的综合考验，体现了计算机科学中"简单问题，复杂解决方案"的经典案例。