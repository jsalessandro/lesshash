---
title: "剖析搜索引擎背后的经典数据结构和算法"
date: 2024-12-20T10:00:00+08:00
lastmod: 2024-12-20T10:00:00+08:00
draft: false
keywords: [搜索引擎, 倒排索引, 哈希表, 字典树, PageRank, TF-IDF, 数据结构, 算法]
description: "深入剖析搜索引擎背后的核心数据结构和算法，包括倒排索引、字典树、哈希表、PageRank算法等关键技术实现"
tags: [数据结构, 算法, 搜索引擎, 倒排索引, PageRank]
categories: [数据结构与算法]
author: "张三"
---

搜索引擎是当今互联网的核心基础设施，每天处理数十亿次查询请求。在这些看似简单的搜索框背后，隐藏着极其复杂而精妙的数据结构和算法。本文将深入剖析搜索引擎的核心技术，揭示其背后的数据结构和算法原理。

## 搜索引擎架构概览

现代搜索引擎主要由以下几个核心组件构成：

1. **网络爬虫（Web Crawler）**：负责发现和抓取网页内容
2. **索引构建器（Indexer）**：将抓取的内容转换为可搜索的索引结构
3. **查询处理器（Query Processor）**：处理用户查询并返回相关结果
4. **排序算法（Ranking Algorithm）**：对搜索结果进行相关性排序

每个组件都依赖特定的数据结构和算法来实现高效的信息检索。

## 核心数据结构详解

### 1. 倒排索引（Inverted Index）

倒排索引是搜索引擎最核心的数据结构，它将文档中的每个词汇映射到包含该词汇的文档列表。

#### 倒排索引结构

```java
public class InvertedIndex {
    // 词汇表，存储词汇到倒排列表的映射
    private Map<String, PostingList> dictionary;

    // 文档存储，存储文档ID到文档内容的映射
    private Map<Integer, Document> documentStore;

    public InvertedIndex() {
        this.dictionary = new HashMap<>();
        this.documentStore = new HashMap<>();
    }

    // 倒排列表，存储包含特定词汇的文档信息
    public static class PostingList {
        private List<Posting> postings;
        private int documentFrequency; // 文档频率

        public PostingList() {
            this.postings = new ArrayList<>();
            this.documentFrequency = 0;
        }

        public void addPosting(Posting posting) {
            postings.add(posting);
            documentFrequency++;
        }

        public List<Posting> getPostings() {
            return postings;
        }
    }

    // 倒排记录，存储单个文档中词汇的信息
    public static class Posting {
        private int documentId;           // 文档ID
        private int termFrequency;        // 词频
        private List<Integer> positions;  // 词汇在文档中的位置

        public Posting(int documentId) {
            this.documentId = documentId;
            this.termFrequency = 0;
            this.positions = new ArrayList<>();
        }

        public void addPosition(int position) {
            positions.add(position);
            termFrequency++;
        }

        // 计算TF-IDF得分
        public double calculateTfIdf(int totalDocuments, int documentFrequency) {
            double tf = 1.0 + Math.log(termFrequency);
            double idf = Math.log((double) totalDocuments / documentFrequency);
            return tf * idf;
        }
    }

    // 添加文档到索引
    public void addDocument(int documentId, String content) {
        Document doc = new Document(documentId, content);
        documentStore.put(documentId, doc);

        String[] terms = content.toLowerCase().split("\\s+");
        Map<String, List<Integer>> termPositions = new HashMap<>();

        // 记录每个词汇的位置
        for (int i = 0; i < terms.length; i++) {
            String term = terms[i];
            termPositions.computeIfAbsent(term, k -> new ArrayList<>()).add(i);
        }

        // 构建倒排索引
        for (Map.Entry<String, List<Integer>> entry : termPositions.entrySet()) {
            String term = entry.getKey();
            List<Integer> positions = entry.getValue();

            PostingList postingList = dictionary.computeIfAbsent(term, k -> new PostingList());
            Posting posting = new Posting(documentId);

            for (int position : positions) {
                posting.addPosition(position);
            }

            postingList.addPosting(posting);
        }
    }

    // 搜索查询
    public List<SearchResult> search(String query) {
        String[] queryTerms = query.toLowerCase().split("\\s+");
        List<SearchResult> results = new ArrayList<>();

        // 获取包含所有查询词的文档
        Set<Integer> candidateDocuments = getCandidateDocuments(queryTerms);

        // 计算每个候选文档的相关性得分
        for (int docId : candidateDocuments) {
            double score = calculateDocumentScore(docId, queryTerms);
            if (score > 0) {
                results.add(new SearchResult(docId, score, documentStore.get(docId)));
            }
        }

        // 按得分降序排序
        results.sort((a, b) -> Double.compare(b.getScore(), a.getScore()));
        return results;
    }

    // 获取候选文档集合
    private Set<Integer> getCandidateDocuments(String[] queryTerms) {
        Set<Integer> candidates = null;

        for (String term : queryTerms) {
            PostingList postingList = dictionary.get(term);
            if (postingList == null) {
                return new HashSet<>(); // 如果有词汇不存在，返回空集合
            }

            Set<Integer> termDocuments = postingList.getPostings().stream()
                    .map(posting -> posting.documentId)
                    .collect(Collectors.toSet());

            if (candidates == null) {
                candidates = termDocuments;
            } else {
                candidates.retainAll(termDocuments); // 求交集
            }
        }

        return candidates != null ? candidates : new HashSet<>();
    }

    // 计算文档相关性得分
    private double calculateDocumentScore(int documentId, String[] queryTerms) {
        double score = 0.0;
        int totalDocuments = documentStore.size();

        for (String term : queryTerms) {
            PostingList postingList = dictionary.get(term);
            if (postingList != null) {
                // 找到对应文档的倒排记录
                for (Posting posting : postingList.getPostings()) {
                    if (posting.documentId == documentId) {
                        score += posting.calculateTfIdf(totalDocuments,
                                postingList.documentFrequency);
                        break;
                    }
                }
            }
        }

        return score;
    }
}

// 文档类
class Document {
    private int id;
    private String content;
    private String title;
    private String url;

    public Document(int id, String content) {
        this.id = id;
        this.content = content;
    }

    // getter和setter方法
    public int getId() { return id; }
    public String getContent() { return content; }
    public String getTitle() { return title; }
    public String getUrl() { return url; }
}

// 搜索结果类
class SearchResult {
    private int documentId;
    private double score;
    private Document document;

    public SearchResult(int documentId, double score, Document document) {
        this.documentId = documentId;
        this.score = score;
        this.document = document;
    }

    public double getScore() { return score; }
    public Document getDocument() { return document; }
}
```

### 2. 字典树（Trie）用于查询建议

字典树在搜索引擎中主要用于实现查询自动补全和拼写检查功能。

```java
public class SearchSuggestionTrie {
    private TrieNode root;

    public SearchSuggestionTrie() {
        this.root = new TrieNode();
    }

    // Trie节点
    private static class TrieNode {
        private Map<Character, TrieNode> children;
        private boolean isEndOfWord;
        private int frequency; // 查询频率
        private Set<String> suggestions; // 热门建议

        public TrieNode() {
            this.children = new HashMap<>();
            this.isEndOfWord = false;
            this.frequency = 0;
            this.suggestions = new TreeSet<>();
        }
    }

    // 插入查询词汇
    public void insert(String query, int frequency) {
        TrieNode current = root;

        for (char ch : query.toCharArray()) {
            current.children.putIfAbsent(ch, new TrieNode());
            current = current.children.get(ch);

            // 更新热门建议
            current.suggestions.add(query);
            if (current.suggestions.size() > 10) {
                // 保持只有前10个建议
                String leastFrequent = current.suggestions.iterator().next();
                current.suggestions.remove(leastFrequent);
            }
        }

        current.isEndOfWord = true;
        current.frequency += frequency;
    }

    // 获取自动补全建议
    public List<String> getAutoComplete(String prefix) {
        TrieNode current = root;

        // 找到前缀对应的节点
        for (char ch : prefix.toCharArray()) {
            current = current.children.get(ch);
            if (current == null) {
                return new ArrayList<>();
            }
        }

        // 收集所有以该前缀开始的词汇
        List<String> suggestions = new ArrayList<>();
        collectSuggestions(current, prefix, suggestions);

        // 按频率排序
        suggestions.sort((a, b) -> {
            int freqA = getQueryFrequency(a);
            int freqB = getQueryFrequency(b);
            return Integer.compare(freqB, freqA);
        });

        return suggestions.subList(0, Math.min(suggestions.size(), 10));
    }

    // 递归收集建议
    private void collectSuggestions(TrieNode node, String prefix, List<String> suggestions) {
        if (node.isEndOfWord) {
            suggestions.add(prefix);
        }

        for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
            collectSuggestions(entry.getValue(), prefix + entry.getKey(), suggestions);
        }
    }

    // 获取查询频率
    public int getQueryFrequency(String query) {
        TrieNode current = root;

        for (char ch : query.toCharArray()) {
            current = current.children.get(ch);
            if (current == null) {
                return 0;
            }
        }

        return current.frequency;
    }

    // 拼写检查和纠错
    public List<String> getSpellingSuggestions(String query, int maxDistance) {
        List<String> suggestions = new ArrayList<>();
        findSimilarWords(root, "", query, 0, maxDistance, suggestions);
        return suggestions;
    }

    // 使用编辑距离查找相似词汇
    private void findSimilarWords(TrieNode node, String current, String target,
                                  int distance, int maxDistance, List<String> suggestions) {
        if (distance > maxDistance) {
            return;
        }

        if (node.isEndOfWord && distance <= maxDistance) {
            suggestions.add(current);
        }

        for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
            char ch = entry.getKey();
            TrieNode child = entry.getValue();

            // 递归探索不同的编辑操作
            if (current.length() < target.length()) {
                if (ch == target.charAt(current.length())) {
                    // 匹配
                    findSimilarWords(child, current + ch, target, distance, maxDistance, suggestions);
                } else {
                    // 替换
                    findSimilarWords(child, current + ch, target, distance + 1, maxDistance, suggestions);
                }
            }

            // 插入
            findSimilarWords(child, current + ch, target, distance + 1, maxDistance, suggestions);
        }

        // 删除操作
        if (current.length() < target.length()) {
            findSimilarWords(node, current, target.substring(1), distance + 1, maxDistance, suggestions);
        }
    }
}
```

### 3. 布隆过滤器（Bloom Filter）

布隆过滤器在搜索引擎中用于快速判断某个URL是否已被爬取，避免重复爬取。

```java
public class BloomFilter {
    private BitSet bitSet;
    private int size;
    private int hashFunctionCount;

    public BloomFilter(int expectedElements, double falsePositiveRate) {
        this.size = calculateOptimalSize(expectedElements, falsePositiveRate);
        this.hashFunctionCount = calculateOptimalHashFunctions(expectedElements, size);
        this.bitSet = new BitSet(size);
    }

    // 计算最优位数组大小
    private int calculateOptimalSize(int expectedElements, double falsePositiveRate) {
        return (int) (-expectedElements * Math.log(falsePositiveRate) / (Math.log(2) * Math.log(2)));
    }

    // 计算最优哈希函数数量
    private int calculateOptimalHashFunctions(int expectedElements, int size) {
        return Math.max(1, (int) Math.round((double) size / expectedElements * Math.log(2)));
    }

    // 添加元素
    public void add(String url) {
        for (int i = 0; i < hashFunctionCount; i++) {
            int hash = hash(url, i);
            bitSet.set(Math.abs(hash % size));
        }
    }

    // 检查元素是否可能存在
    public boolean mightContain(String url) {
        for (int i = 0; i < hashFunctionCount; i++) {
            int hash = hash(url, i);
            if (!bitSet.get(Math.abs(hash % size))) {
                return false;
            }
        }
        return true;
    }

    // 多个哈希函数
    private int hash(String url, int seed) {
        int hash = 0;
        for (char c : url.toCharArray()) {
            hash = hash * 31 + c + seed * 17;
        }
        return hash;
    }
}

// URL去重管理器
public class URLDeduplicator {
    private BloomFilter bloomFilter;
    private Set<String> exactUrls; // 精确存储，用于最终验证

    public URLDeduplicator(int expectedUrls) {
        this.bloomFilter = new BloomFilter(expectedUrls, 0.01); // 1%误判率
        this.exactUrls = new HashSet<>();
    }

    // 检查URL是否已被处理
    public boolean isProcessed(String url) {
        // 首先使用布隆过滤器快速检查
        if (!bloomFilter.mightContain(url)) {
            return false;
        }

        // 布隆过滤器可能存在，进行精确检查
        return exactUrls.contains(url);
    }

    // 标记URL为已处理
    public void markAsProcessed(String url) {
        bloomFilter.add(url);
        exactUrls.add(url);
    }
}
```

## 核心算法详解

### 1. PageRank算法

PageRank是搜索引擎排序的核心算法之一，用于评估网页的权威性。

```java
public class PageRankCalculator {
    private static final double DAMPING_FACTOR = 0.85;
    private static final double EPSILON = 1e-6;
    private static final int MAX_ITERATIONS = 100;

    // 图表示，存储页面间的链接关系
    private Map<String, Set<String>> graph; // 出链
    private Map<String, Set<String>> reverseGraph; // 入链
    private Map<String, Double> pageRanks;

    public PageRankCalculator() {
        this.graph = new HashMap<>();
        this.reverseGraph = new HashMap<>();
        this.pageRanks = new HashMap<>();
    }

    // 添加链接关系
    public void addLink(String fromPage, String toPage) {
        graph.computeIfAbsent(fromPage, k -> new HashSet<>()).add(toPage);
        reverseGraph.computeIfAbsent(toPage, k -> new HashSet<>()).add(fromPage);

        // 确保所有页面都在图中
        graph.putIfAbsent(toPage, new HashSet<>());
        reverseGraph.putIfAbsent(fromPage, new HashSet<>());
    }

    // 计算PageRank值
    public Map<String, Double> calculatePageRank() {
        Set<String> allPages = new HashSet<>(graph.keySet());
        int totalPages = allPages.size();

        // 初始化PageRank值
        double initialValue = 1.0 / totalPages;
        for (String page : allPages) {
            pageRanks.put(page, initialValue);
        }

        // 迭代计算
        for (int iteration = 0; iteration < MAX_ITERATIONS; iteration++) {
            Map<String, Double> newPageRanks = new HashMap<>();
            double maxChange = 0.0;

            for (String page : allPages) {
                double newRank = calculateNewPageRank(page, totalPages);
                newPageRanks.put(page, newRank);

                double change = Math.abs(newRank - pageRanks.get(page));
                maxChange = Math.max(maxChange, change);
            }

            pageRanks = newPageRanks;

            // 检查收敛
            if (maxChange < EPSILON) {
                System.out.println("PageRank收敛于第" + (iteration + 1) + "次迭代");
                break;
            }
        }

        return pageRanks;
    }

    // 计算单个页面的新PageRank值
    private double calculateNewPageRank(String page, int totalPages) {
        double rank = (1.0 - DAMPING_FACTOR) / totalPages;

        Set<String> incomingLinks = reverseGraph.get(page);
        if (incomingLinks != null) {
            for (String incomingPage : incomingLinks) {
                double incomingPageRank = pageRanks.get(incomingPage);
                int outgoingLinksCount = graph.get(incomingPage).size();

                if (outgoingLinksCount > 0) {
                    rank += DAMPING_FACTOR * (incomingPageRank / outgoingLinksCount);
                }
            }
        }

        return rank;
    }

    // 获取TopN页面
    public List<PageRankResult> getTopPages(int n) {
        List<PageRankResult> results = pageRanks.entrySet().stream()
                .map(entry -> new PageRankResult(entry.getKey(), entry.getValue()))
                .sorted((a, b) -> Double.compare(b.getPageRank(), a.getPageRank()))
                .collect(Collectors.toList());

        return results.subList(0, Math.min(n, results.size()));
    }
}

// PageRank结果类
class PageRankResult {
    private String page;
    private double pageRank;

    public PageRankResult(String page, double pageRank) {
        this.page = page;
        this.pageRank = pageRank;
    }

    public String getPage() { return page; }
    public double getPageRank() { return pageRank; }
}
```

### 2. TF-IDF算法优化

改进的TF-IDF算法，考虑了文档长度归一化和查询词位置权重。

```java
public class AdvancedTfIdfCalculator {
    private InvertedIndex invertedIndex;
    private Map<Integer, DocumentVector> documentVectors;

    public AdvancedTfIdfCalculator(InvertedIndex invertedIndex) {
        this.invertedIndex = invertedIndex;
        this.documentVectors = new HashMap<>();
        precomputeDocumentVectors();
    }

    // 预计算文档向量
    private void precomputeDocumentVectors() {
        // 这里需要遍历所有文档，计算向量表示
        // 实际实现中会从倒排索引中获取文档信息
    }

    // 文档向量表示
    public static class DocumentVector {
        private Map<String, Double> termWeights;
        private double magnitude; // 向量模长

        public DocumentVector() {
            this.termWeights = new HashMap<>();
            this.magnitude = 0.0;
        }

        public void addTermWeight(String term, double weight) {
            termWeights.put(term, weight);
            magnitude += weight * weight;
        }

        public void normalize() {
            magnitude = Math.sqrt(magnitude);
            if (magnitude > 0) {
                for (Map.Entry<String, Double> entry : termWeights.entrySet()) {
                    entry.setValue(entry.getValue() / magnitude);
                }
            }
        }

        public double getMagnitude() { return magnitude; }
        public Map<String, Double> getTermWeights() { return termWeights; }
    }

    // 计算改进的TF值
    public double calculateEnhancedTF(int termFrequency, int documentLength, List<Integer> positions) {
        // 基础TF
        double tf = Math.log(1.0 + termFrequency);

        // 文档长度归一化
        double lengthNormalization = 1.0 / Math.sqrt(documentLength);

        // 位置权重（标题、开头段落权重更高）
        double positionWeight = calculatePositionWeight(positions, documentLength);

        return tf * lengthNormalization * positionWeight;
    }

    // 计算位置权重
    private double calculatePositionWeight(List<Integer> positions, int documentLength) {
        double weight = 1.0;

        for (int position : positions) {
            // 文档开头位置权重更高
            if (position < documentLength * 0.1) {
                weight *= 1.5;
            } else if (position < documentLength * 0.3) {
                weight *= 1.2;
            }
        }

        return Math.min(weight, 3.0); // 限制最大权重
    }

    // 计算查询与文档的相似度
    public double calculateSimilarity(String[] queryTerms, int documentId) {
        DocumentVector docVector = documentVectors.get(documentId);
        if (docVector == null) {
            return 0.0;
        }

        // 构建查询向量
        Map<String, Double> queryVector = buildQueryVector(queryTerms);

        // 计算余弦相似度
        double dotProduct = 0.0;
        double queryMagnitude = 0.0;

        for (Map.Entry<String, Double> entry : queryVector.entrySet()) {
            String term = entry.getKey();
            double queryWeight = entry.getValue();

            queryMagnitude += queryWeight * queryWeight;

            Double docWeight = docVector.getTermWeights().get(term);
            if (docWeight != null) {
                dotProduct += queryWeight * docWeight;
            }
        }

        queryMagnitude = Math.sqrt(queryMagnitude);

        if (queryMagnitude == 0 || docVector.getMagnitude() == 0) {
            return 0.0;
        }

        return dotProduct / (queryMagnitude * docVector.getMagnitude());
    }

    // 构建查询向量
    private Map<String, Double> buildQueryVector(String[] queryTerms) {
        Map<String, Integer> termCounts = new HashMap<>();

        // 统计查询词频
        for (String term : queryTerms) {
            termCounts.put(term, termCounts.getOrDefault(term, 0) + 1);
        }

        Map<String, Double> queryVector = new HashMap<>();
        int totalDocuments = documentVectors.size();

        for (Map.Entry<String, Integer> entry : termCounts.entrySet()) {
            String term = entry.getKey();
            int frequency = entry.getValue();

            // 获取文档频率
            int documentFrequency = getDocumentFrequency(term);

            if (documentFrequency > 0) {
                double tf = Math.log(1.0 + frequency);
                double idf = Math.log((double) totalDocuments / documentFrequency);
                queryVector.put(term, tf * idf);
            }
        }

        return queryVector;
    }

    // 获取词汇的文档频率
    private int getDocumentFrequency(String term) {
        // 从倒排索引中获取文档频率
        // 这里是简化实现
        return 1;
    }
}
```

### 3. 查询优化算法

实现查询扩展和同义词处理，提高搜索召回率。

```java
public class QueryExpansionProcessor {
    private Map<String, Set<String>> synonyms;
    private Map<String, Double> termImportance;
    private WordEmbedding wordEmbedding;

    public QueryExpansionProcessor() {
        this.synonyms = new HashMap<>();
        this.termImportance = new HashMap<>();
        this.wordEmbedding = new WordEmbedding();
        loadSynonyms();
    }

    // 加载同义词词典
    private void loadSynonyms() {
        // 从文件或数据库加载同义词
        synonyms.put("搜索", Set.of("检索", "查找", "寻找"));
        synonyms.put("算法", Set.of("方法", "技术", "策略"));
        synonyms.put("数据结构", Set.of("数据组织", "存储结构"));
    }

    // 查询扩展
    public ExpandedQuery expandQuery(String originalQuery) {
        String[] terms = originalQuery.toLowerCase().split("\\s+");
        Set<String> expandedTerms = new HashSet<>();
        Map<String, Double> termWeights = new HashMap<>();

        // 添加原始查询词
        for (String term : terms) {
            expandedTerms.add(term);
            termWeights.put(term, 1.0);
        }

        // 添加同义词
        for (String term : terms) {
            Set<String> synonymList = synonyms.get(term);
            if (synonymList != null) {
                for (String synonym : synonymList) {
                    expandedTerms.add(synonym);
                    termWeights.put(synonym, 0.8); // 同义词权重略低
                }
            }
        }

        // 添加相关词（基于词向量）
        for (String term : terms) {
            List<String> similarTerms = wordEmbedding.findSimilarWords(term, 3);
            for (String similarTerm : similarTerms) {
                expandedTerms.add(similarTerm);
                termWeights.put(similarTerm, 0.6); // 相关词权重更低
            }
        }

        return new ExpandedQuery(originalQuery, expandedTerms, termWeights);
    }

    // 查询重写
    public String rewriteQuery(String query) {
        // 处理常见拼写错误
        query = correctSpelling(query);

        // 处理查询意图
        query = processQueryIntent(query);

        return query;
    }

    // 拼写纠错
    private String correctSpelling(String query) {
        String[] terms = query.split("\\s+");
        StringBuilder corrected = new StringBuilder();

        for (String term : terms) {
            String correctedTerm = findBestCorrection(term);
            corrected.append(correctedTerm).append(" ");
        }

        return corrected.toString().trim();
    }

    // 查找最佳拼写纠正
    private String findBestCorrection(String term) {
        // 使用编辑距离算法查找最相似的正确词汇
        int minDistance = Integer.MAX_VALUE;
        String bestCorrection = term;

        // 这里应该遍历词典中的所有词汇
        // 简化实现
        Map<String, String> corrections = Map.of(
            "搜索引擎", "搜索引擎",
            "algorigm", "algorithm",
            "数据结构", "数据结构"
        );

        for (String correctWord : corrections.keySet()) {
            int distance = calculateEditDistance(term, correctWord);
            if (distance < minDistance && distance <= 2) {
                minDistance = distance;
                bestCorrection = correctWord;
            }
        }

        return bestCorrection;
    }

    // 计算编辑距离
    private int calculateEditDistance(String s1, String s2) {
        int m = s1.length();
        int n = s2.length();
        int[][] dp = new int[m + 1][n + 1];

        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(Math.min(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1]);
                }
            }
        }

        return dp[m][n];
    }

    // 处理查询意图
    private String processQueryIntent(String query) {
        // 识别特殊查询模式
        if (query.matches(".*什么是.*")) {
            return query + " 定义 解释";
        } else if (query.matches(".*如何.*") || query.matches(".*怎么.*")) {
            return query + " 方法 步骤 教程";
        } else if (query.matches(".*价格.*") || query.matches(".*多少钱.*")) {
            return query + " 价格 费用 成本";
        }

        return query;
    }
}

// 扩展查询结果
class ExpandedQuery {
    private String originalQuery;
    private Set<String> expandedTerms;
    private Map<String, Double> termWeights;

    public ExpandedQuery(String originalQuery, Set<String> expandedTerms, Map<String, Double> termWeights) {
        this.originalQuery = originalQuery;
        this.expandedTerms = expandedTerms;
        this.termWeights = termWeights;
    }

    public String getOriginalQuery() { return originalQuery; }
    public Set<String> getExpandedTerms() { return expandedTerms; }
    public Map<String, Double> getTermWeights() { return termWeights; }
}

// 简化的词向量实现
class WordEmbedding {
    private Map<String, List<Double>> vectors;

    public WordEmbedding() {
        this.vectors = new HashMap<>();
        // 加载预训练的词向量
    }

    public List<String> findSimilarWords(String word, int count) {
        // 计算余弦相似度，返回最相似的词汇
        List<String> similar = new ArrayList<>();
        // 简化实现
        similar.add(word + "_related1");
        similar.add(word + "_related2");
        return similar.subList(0, Math.min(count, similar.size()));
    }
}
```

## 性能优化策略

### 1. 索引压缩

为了减少存储空间和提高I/O效率，搜索引擎使用多种索引压缩技术。

```java
public class CompressedIndex {
    // Variable Byte编码
    public static byte[] encodeVariableByte(int number) {
        List<Byte> bytes = new ArrayList<>();

        while (number >= 128) {
            bytes.add((byte) (number % 128));
            number /= 128;
        }
        bytes.add((byte) (number + 128)); // 最后一个字节最高位设为1

        byte[] result = new byte[bytes.size()];
        for (int i = 0; i < bytes.size(); i++) {
            result[i] = bytes.get(i);
        }
        return result;
    }

    public static int decodeVariableByte(byte[] bytes, int offset) {
        int number = 0;
        int shift = 0;

        for (int i = offset; i < bytes.length; i++) {
            byte b = bytes[i];
            if (b < 128) {
                number += (b << shift);
                shift += 7;
            } else {
                number += ((b - 128) << shift);
                break;
            }
        }

        return number;
    }

    // Delta编码（差值编码）
    public static int[] deltaEncode(int[] numbers) {
        if (numbers.length == 0) return numbers;

        int[] encoded = new int[numbers.length];
        encoded[0] = numbers[0];

        for (int i = 1; i < numbers.length; i++) {
            encoded[i] = numbers[i] - numbers[i - 1];
        }

        return encoded;
    }

    public static int[] deltaDecode(int[] encoded) {
        if (encoded.length == 0) return encoded;

        int[] decoded = new int[encoded.length];
        decoded[0] = encoded[0];

        for (int i = 1; i < encoded.length; i++) {
            decoded[i] = decoded[i - 1] + encoded[i];
        }

        return decoded;
    }
}
```

### 2. 并行处理

使用多线程和分布式处理来提高查询响应速度。

```java
public class ParallelSearchEngine {
    private final int threadPoolSize;
    private final ExecutorService executor;
    private final List<InvertedIndex> shards;

    public ParallelSearchEngine(int threadPoolSize, List<InvertedIndex> shards) {
        this.threadPoolSize = threadPoolSize;
        this.executor = Executors.newFixedThreadPool(threadPoolSize);
        this.shards = shards;
    }

    // 并行搜索
    public List<SearchResult> parallelSearch(String query, int topK) {
        List<Future<List<SearchResult>>> futures = new ArrayList<>();

        // 在每个分片上并行执行搜索
        for (InvertedIndex shard : shards) {
            Future<List<SearchResult>> future = executor.submit(() -> {
                return shard.search(query);
            });
            futures.add(future);
        }

        // 合并结果
        List<SearchResult> allResults = new ArrayList<>();
        for (Future<List<SearchResult>> future : futures) {
            try {
                allResults.addAll(future.get());
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }

        // 排序并返回TopK结果
        allResults.sort((a, b) -> Double.compare(b.getScore(), a.getScore()));
        return allResults.subList(0, Math.min(topK, allResults.size()));
    }

    // 关闭线程池
    public void shutdown() {
        executor.shutdown();
    }
}
```

## 缓存策略

搜索引擎使用多级缓存来提高响应速度。

```java
public class SearchCache {
    private final LRUCache<String, List<SearchResult>> queryCache;
    private final LRUCache<String, PostingList> termCache;
    private final long cacheTTL;

    public SearchCache(int maxSize, long ttlMillis) {
        this.queryCache = new LRUCache<>(maxSize);
        this.termCache = new LRUCache<>(maxSize * 10);
        this.cacheTTL = ttlMillis;
    }

    // LRU缓存实现
    private static class LRUCache<K, V> {
        private final int maxSize;
        private final LinkedHashMap<K, CacheEntry<V>> cache;

        public LRUCache(int maxSize) {
            this.maxSize = maxSize;
            this.cache = new LinkedHashMap<K, CacheEntry<V>>(16, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                    return size() > maxSize;
                }
            };
        }

        public synchronized V get(K key) {
            CacheEntry<V> entry = cache.get(key);
            if (entry != null && !entry.isExpired()) {
                return entry.getValue();
            } else {
                cache.remove(key);
                return null;
            }
        }

        public synchronized void put(K key, V value, long ttl) {
            cache.put(key, new CacheEntry<>(value, System.currentTimeMillis() + ttl));
        }
    }

    // 缓存条目
    private static class CacheEntry<V> {
        private final V value;
        private final long expireTime;

        public CacheEntry(V value, long expireTime) {
            this.value = value;
            this.expireTime = expireTime;
        }

        public V getValue() { return value; }

        public boolean isExpired() {
            return System.currentTimeMillis() > expireTime;
        }
    }

    // 获取缓存的查询结果
    public List<SearchResult> getCachedResults(String query) {
        return queryCache.get(query);
    }

    // 缓存查询结果
    public void cacheResults(String query, List<SearchResult> results) {
        queryCache.put(query, results, cacheTTL);
    }

    // 获取缓存的倒排列表
    public PostingList getCachedPostingList(String term) {
        return termCache.get(term);
    }

    // 缓存倒排列表
    public void cachePostingList(String term, PostingList postingList) {
        termCache.put(term, postingList, cacheTTL);
    }
}
```

## 应用场景和性能分析

### 应用场景

1. **Web搜索引擎**：Google、百度等通用搜索引擎
2. **企业内部搜索**：文档检索、知识管理系统
3. **电商搜索**：商品搜索、推荐系统
4. **日志分析**：ELK（Elasticsearch, Logstash, Kibana）栈
5. **代码搜索**：GitHub、GitLab代码搜索功能

### 性能分析

| 数据结构/算法 | 时间复杂度 | 空间复杂度 | 适用场景 |
|--------------|-----------|-----------|----------|
| 倒排索引 | O(k + log n) | O(n·m) | 核心索引结构 |
| Trie树 | O(m) | O(ALPHABET_SIZE·N) | 自动补全 |
| 布隆过滤器 | O(k) | O(m) | 快速去重判断 |
| PageRank | O(n²) | O(n) | 权威性排序 |
| TF-IDF | O(n·m) | O(n·m) | 相关性计算 |

其中：
- n：文档数量
- m：平均文档长度
- k：查询词数量

## 总结

搜索引擎背后的数据结构和算法是现代信息检索技术的核心。本文详细分析了：

1. **核心数据结构**：倒排索引、字典树、布隆过滤器等，为高效检索提供基础
2. **关键算法**：PageRank、TF-IDF、查询扩展等，实现智能排序和相关性计算
3. **性能优化**：索引压缩、并行处理、多级缓存等，提升系统响应速度
4. **实际应用**：从通用搜索到垂直搜索的各种场景

这些技术的巧妙结合，使得搜索引擎能够在毫秒级别的时间内，从海量数据中找到用户最需要的信息。随着大数据和人工智能技术的发展，搜索引擎将继续演进，为用户提供更智能、更精准的搜索体验。

理解这些底层原理，不仅有助于我们更好地使用搜索引擎，也为开发高性能的信息检索系统提供了坚实的理论基础和实践指导。