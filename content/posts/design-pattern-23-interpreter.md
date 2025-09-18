---
title: "设计模式入门教程23：解释器模式 - 为语言创建解释器"
date: 2024-12-23T10:23:00+08:00
draft: false
tags: ["设计模式", "解释器模式", "Java", "编程教程"]
categories: ["设计模式"]
series: ["设计模式入门教程"]
---

## 🎯 什么是解释器模式？

解释器模式（Interpreter Pattern）是一种行为型设计模式，它给定一个语言，定义它的文法的一种表示，并定义一个解释器，这个解释器使用该表示来解释语言中的句子。解释器模式主要用于处理简单的语言和语法解析。

### 🌟 现实生活中的例子

想象一下**计算器的表达式解析**：
- **表达式**："1 + 2 * 3"
- **文法规则**：数字、加号、乘号、括号等
- **解释器**：按照数学运算规则计算结果
- **结果**：7

又比如**SQL查询解析**：
- **SQL语句**："SELECT name FROM users WHERE age > 18"
- **文法定义**：SELECT、FROM、WHERE等关键字的语法规则
- **解释器**：将SQL转换为数据库操作
- **执行**：返回符合条件的数据

这就是解释器模式的应用场景！

## 🏗️ 模式结构

```java
// 抽象表达式
abstract class Expression {
    public abstract int interpret(Context context);
}

// 终结符表达式
class NumberExpression extends Expression {
    private int number;

    public NumberExpression(int number) {
        this.number = number;
    }

    @Override
    public int interpret(Context context) {
        return number;
    }
}

// 非终结符表达式
class AddExpression extends Expression {
    private Expression left;
    private Expression right;

    public AddExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public int interpret(Context context) {
        return left.interpret(context) + right.interpret(context);
    }
}

// 上下文
class Context {
    // 存储解释器需要的全局信息
}
```

## 💡 核心组件详解

### 1. 抽象表达式（AbstractExpression）
```java
// 抽象表达式接口
interface Expression {
    Object interpret(Context context);
    String toString();
}

// 布尔表达式基类
abstract class BooleanExpression implements Expression {
    @Override
    public abstract Boolean interpret(Context context);
}

// 数值表达式基类
abstract class NumericExpression implements Expression {
    @Override
    public abstract Double interpret(Context context);
}

// 字符串表达式基类
abstract class StringExpression implements Expression {
    @Override
    public abstract String interpret(Context context);
}
```

### 2. 终结符表达式（TerminalExpression）
```java
// 数字常量表达式
class NumberConstant extends NumericExpression {
    private double value;

    public NumberConstant(double value) {
        this.value = value;
    }

    @Override
    public Double interpret(Context context) {
        System.out.println("解释数字常量：" + value);
        return value;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}

// 变量表达式
class VariableExpression extends NumericExpression {
    private String variableName;

    public VariableExpression(String variableName) {
        this.variableName = variableName;
    }

    @Override
    public Double interpret(Context context) {
        Double value = context.getVariable(variableName);
        System.out.println("解释变量 " + variableName + " = " + value);
        return value != null ? value : 0.0;
    }

    @Override
    public String toString() {
        return variableName;
    }
}

// 布尔常量表达式
class BooleanConstant extends BooleanExpression {
    private boolean value;

    public BooleanConstant(boolean value) {
        this.value = value;
    }

    @Override
    public Boolean interpret(Context context) {
        System.out.println("解释布尔常量：" + value);
        return value;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}

// 字符串常量表达式
class StringConstant extends StringExpression {
    private String value;

    public StringConstant(String value) {
        this.value = value;
    }

    @Override
    public String interpret(Context context) {
        System.out.println("解释字符串常量：\"" + value + "\"");
        return value;
    }

    @Override
    public String toString() {
        return "\"" + value + "\"";
    }
}
```

### 3. 非终结符表达式（NonterminalExpression）
```java
// 加法表达式
class AddExpression extends NumericExpression {
    private NumericExpression left;
    private NumericExpression right;

    public AddExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Double interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);
        double result = leftValue + rightValue;
        System.out.println("解释加法：" + leftValue + " + " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " + " + right + ")";
    }
}

// 减法表达式
class SubtractExpression extends NumericExpression {
    private NumericExpression left;
    private NumericExpression right;

    public SubtractExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Double interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);
        double result = leftValue - rightValue;
        System.out.println("解释减法：" + leftValue + " - " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " - " + right + ")";
    }
}

// 乘法表达式
class MultiplyExpression extends NumericExpression {
    private NumericExpression left;
    private NumericExpression right;

    public MultiplyExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Double interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);
        double result = leftValue * rightValue;
        System.out.println("解释乘法：" + leftValue + " * " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " * " + right + ")";
    }
}

// 除法表达式
class DivideExpression extends NumericExpression {
    private NumericExpression left;
    private NumericExpression right;

    public DivideExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Double interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);

        if (rightValue == 0) {
            throw new ArithmeticException("除零错误");
        }

        double result = leftValue / rightValue;
        System.out.println("解释除法：" + leftValue + " / " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " / " + right + ")";
    }
}

// 逻辑与表达式
class AndExpression extends BooleanExpression {
    private BooleanExpression left;
    private BooleanExpression right;

    public AndExpression(BooleanExpression left, BooleanExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Boolean interpret(Context context) {
        boolean leftValue = left.interpret(context);
        boolean rightValue = right.interpret(context);
        boolean result = leftValue && rightValue;
        System.out.println("解释逻辑与：" + leftValue + " && " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " && " + right + ")";
    }
}

// 逻辑或表达式
class OrExpression extends BooleanExpression {
    private BooleanExpression left;
    private BooleanExpression right;

    public OrExpression(BooleanExpression left, BooleanExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Boolean interpret(Context context) {
        boolean leftValue = left.interpret(context);
        boolean rightValue = right.interpret(context);
        boolean result = leftValue || rightValue;
        System.out.println("解释逻辑或：" + leftValue + " || " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " || " + right + ")";
    }
}

// 逻辑非表达式
class NotExpression extends BooleanExpression {
    private BooleanExpression expression;

    public NotExpression(BooleanExpression expression) {
        this.expression = expression;
    }

    @Override
    public Boolean interpret(Context context) {
        boolean value = expression.interpret(context);
        boolean result = !value;
        System.out.println("解释逻辑非：!" + value + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "!" + expression;
    }
}

// 比较表达式
class GreaterThanExpression extends BooleanExpression {
    private NumericExpression left;
    private NumericExpression right;

    public GreaterThanExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Boolean interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);
        boolean result = leftValue > rightValue;
        System.out.println("解释大于比较：" + leftValue + " > " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " > " + right + ")";
    }
}

class LessThanExpression extends BooleanExpression {
    private NumericExpression left;
    private NumericExpression right;

    public LessThanExpression(NumericExpression left, NumericExpression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Boolean interpret(Context context) {
        double leftValue = left.interpret(context);
        double rightValue = right.interpret(context);
        boolean result = leftValue < rightValue;
        System.out.println("解释小于比较：" + leftValue + " < " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " < " + right + ")";
    }
}

class EqualsExpression extends BooleanExpression {
    private Expression left;
    private Expression right;

    public EqualsExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Boolean interpret(Context context) {
        Object leftValue = left.interpret(context);
        Object rightValue = right.interpret(context);
        boolean result = Objects.equals(leftValue, rightValue);
        System.out.println("解释等于比较：" + leftValue + " == " + rightValue + " = " + result);
        return result;
    }

    @Override
    public String toString() {
        return "(" + left + " == " + right + ")";
    }
}
```

### 4. 上下文（Context）
```java
// 解释器上下文
class Context {
    private Map<String, Object> variables;
    private Map<String, Expression> functions;

    public Context() {
        this.variables = new HashMap<>();
        this.functions = new HashMap<>();
        initializeBuiltInFunctions();
    }

    // 变量管理
    public void setVariable(String name, Object value) {
        variables.put(name, value);
        System.out.println("设置变量 " + name + " = " + value);
    }

    public Double getVariable(String name) {
        Object value = variables.get(name);
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        return null;
    }

    public Object getVariableValue(String name) {
        return variables.get(name);
    }

    public boolean hasVariable(String name) {
        return variables.containsKey(name);
    }

    // 函数管理
    public void defineFunction(String name, Expression expression) {
        functions.put(name, expression);
        System.out.println("定义函数：" + name);
    }

    public Expression getFunction(String name) {
        return functions.get(name);
    }

    public boolean hasFunction(String name) {
        return functions.containsKey(name);
    }

    // 初始化内置函数
    private void initializeBuiltInFunctions() {
        // 这里可以添加内置函数，如sin, cos, sqrt等
        // 简化实现，仅作示例
    }

    public void showVariables() {
        System.out.println("=== 当前变量 ===");
        if (variables.isEmpty()) {
            System.out.println("无变量");
        } else {
            for (Map.Entry<String, Object> entry : variables.entrySet()) {
                System.out.println(entry.getKey() + " = " + entry.getValue());
            }
        }
        System.out.println("===============");
    }

    public void showFunctions() {
        System.out.println("=== 当前函数 ===");
        if (functions.isEmpty()) {
            System.out.println("无自定义函数");
        } else {
            for (String name : functions.keySet()) {
                System.out.println(name + "()");
            }
        }
        System.out.println("===============");
    }
}
```

## 🎮 实际应用示例

### 示例1：简单计算器解释器
```java
// 词法分析器
class Lexer {
    private String input;
    private int position;
    private char currentChar;

    public Lexer(String input) {
        this.input = input;
        this.position = 0;
        this.currentChar = input.length() > 0 ? input.charAt(0) : '\0';
    }

    private void advance() {
        position++;
        if (position >= input.length()) {
            currentChar = '\0';
        } else {
            currentChar = input.charAt(position);
        }
    }

    private void skipWhitespace() {
        while (currentChar != '\0' && Character.isWhitespace(currentChar)) {
            advance();
        }
    }

    private double number() {
        StringBuilder result = new StringBuilder();
        while (currentChar != '\0' && (Character.isDigit(currentChar) || currentChar == '.')) {
            result.append(currentChar);
            advance();
        }
        return Double.parseDouble(result.toString());
    }

    private String identifier() {
        StringBuilder result = new StringBuilder();
        while (currentChar != '\0' && (Character.isLetterOrDigit(currentChar) || currentChar == '_')) {
            result.append(currentChar);
            advance();
        }
        return result.toString();
    }

    public Token nextToken() {
        while (currentChar != '\0') {
            if (Character.isWhitespace(currentChar)) {
                skipWhitespace();
                continue;
            }

            if (Character.isDigit(currentChar)) {
                return new Token(TokenType.NUMBER, number());
            }

            if (Character.isLetter(currentChar)) {
                String id = identifier();
                return new Token(TokenType.IDENTIFIER, id);
            }

            switch (currentChar) {
                case '+':
                    advance();
                    return new Token(TokenType.PLUS, "+");
                case '-':
                    advance();
                    return new Token(TokenType.MINUS, "-");
                case '*':
                    advance();
                    return new Token(TokenType.MULTIPLY, "*");
                case '/':
                    advance();
                    return new Token(TokenType.DIVIDE, "/");
                case '(':
                    advance();
                    return new Token(TokenType.LPAREN, "(");
                case ')':
                    advance();
                    return new Token(TokenType.RPAREN, ")");
                case '=':
                    advance();
                    if (currentChar == '=') {
                        advance();
                        return new Token(TokenType.EQUALS, "==");
                    }
                    return new Token(TokenType.ASSIGN, "=");
                case '>':
                    advance();
                    return new Token(TokenType.GREATER, ">");
                case '<':
                    advance();
                    return new Token(TokenType.LESS, "<");
                default:
                    throw new RuntimeException("无效字符：" + currentChar);
            }
        }

        return new Token(TokenType.EOF, null);
    }
}

// 令牌类型
enum TokenType {
    NUMBER, IDENTIFIER, PLUS, MINUS, MULTIPLY, DIVIDE,
    LPAREN, RPAREN, ASSIGN, EQUALS, GREATER, LESS, EOF
}

// 令牌类
class Token {
    private TokenType type;
    private Object value;

    public Token(TokenType type, Object value) {
        this.type = type;
        this.value = value;
    }

    public TokenType getType() { return type; }
    public Object getValue() { return value; }

    @Override
    public String toString() {
        return "Token(" + type + ", " + value + ")";
    }
}

// 语法分析器
class Parser {
    private Lexer lexer;
    private Token currentToken;

    public Parser(Lexer lexer) {
        this.lexer = lexer;
        this.currentToken = lexer.nextToken();
    }

    private void eat(TokenType tokenType) {
        if (currentToken.getType() == tokenType) {
            currentToken = lexer.nextToken();
        } else {
            throw new RuntimeException("期望 " + tokenType + " 但得到 " + currentToken.getType());
        }
    }

    private NumericExpression factor() {
        Token token = currentToken;

        if (token.getType() == TokenType.NUMBER) {
            eat(TokenType.NUMBER);
            return new NumberConstant((Double) token.getValue());
        } else if (token.getType() == TokenType.IDENTIFIER) {
            eat(TokenType.IDENTIFIER);
            return new VariableExpression((String) token.getValue());
        } else if (token.getType() == TokenType.LPAREN) {
            eat(TokenType.LPAREN);
            NumericExpression node = expression();
            eat(TokenType.RPAREN);
            return node;
        }

        throw new RuntimeException("无效的因子");
    }

    private NumericExpression term() {
        NumericExpression node = factor();

        while (currentToken.getType() == TokenType.MULTIPLY ||
               currentToken.getType() == TokenType.DIVIDE) {
            Token token = currentToken;
            if (token.getType() == TokenType.MULTIPLY) {
                eat(TokenType.MULTIPLY);
                node = new MultiplyExpression(node, factor());
            } else if (token.getType() == TokenType.DIVIDE) {
                eat(TokenType.DIVIDE);
                node = new DivideExpression(node, factor());
            }
        }

        return node;
    }

    private NumericExpression expression() {
        NumericExpression node = term();

        while (currentToken.getType() == TokenType.PLUS ||
               currentToken.getType() == TokenType.MINUS) {
            Token token = currentToken;
            if (token.getType() == TokenType.PLUS) {
                eat(TokenType.PLUS);
                node = new AddExpression(node, term());
            } else if (token.getType() == TokenType.MINUS) {
                eat(TokenType.MINUS);
                node = new SubtractExpression(node, term());
            }
        }

        return node;
    }

    private Expression comparison() {
        NumericExpression left = expression();

        if (currentToken.getType() == TokenType.GREATER) {
            eat(TokenType.GREATER);
            NumericExpression right = expression();
            return new GreaterThanExpression(left, right);
        } else if (currentToken.getType() == TokenType.LESS) {
            eat(TokenType.LESS);
            NumericExpression right = expression();
            return new LessThanExpression(left, right);
        } else if (currentToken.getType() == TokenType.EQUALS) {
            eat(TokenType.EQUALS);
            Expression right = expression();
            return new EqualsExpression(left, right);
        }

        return left;
    }

    private Expression assignment() {
        if (currentToken.getType() == TokenType.IDENTIFIER) {
            String varName = (String) currentToken.getValue();
            eat(TokenType.IDENTIFIER);

            if (currentToken.getType() == TokenType.ASSIGN) {
                eat(TokenType.ASSIGN);
                Expression value = comparison();
                return new AssignmentExpression(varName, value);
            } else {
                // 重新创建变量表达式
                return new VariableExpression(varName);
            }
        }

        return comparison();
    }

    public Expression parse() {
        Expression node = assignment();
        if (currentToken.getType() != TokenType.EOF) {
            throw new RuntimeException("解析未完成，剩余令牌：" + currentToken);
        }
        return node;
    }
}

// 赋值表达式
class AssignmentExpression implements Expression {
    private String variableName;
    private Expression valueExpression;

    public AssignmentExpression(String variableName, Expression valueExpression) {
        this.variableName = variableName;
        this.valueExpression = valueExpression;
    }

    @Override
    public Object interpret(Context context) {
        Object value = valueExpression.interpret(context);
        context.setVariable(variableName, value);
        System.out.println("赋值：" + variableName + " = " + value);
        return value;
    }

    @Override
    public String toString() {
        return variableName + " = " + valueExpression;
    }
}

// 计算器解释器
class Calculator {
    private Context context;

    public Calculator() {
        this.context = new Context();
    }

    public Object evaluate(String expression) {
        try {
            System.out.println("计算表达式：" + expression);

            Lexer lexer = new Lexer(expression);
            Parser parser = new Parser(lexer);
            Expression ast = parser.parse();

            System.out.println("抽象语法树：" + ast);

            Object result = ast.interpret(context);
            System.out.println("结果：" + result);
            System.out.println();

            return result;
        } catch (Exception e) {
            System.err.println("错误：" + e.getMessage());
            return null;
        }
    }

    public void setVariable(String name, double value) {
        context.setVariable(name, value);
    }

    public void showVariables() {
        context.showVariables();
    }
}

// 计算器使用示例
public class CalculatorExample {
    public static void main(String[] args) {
        Calculator calculator = new Calculator();

        System.out.println("=== 基本算术运算 ===");
        calculator.evaluate("2 + 3");
        calculator.evaluate("10 - 4");
        calculator.evaluate("3 * 4");
        calculator.evaluate("15 / 3");
        calculator.evaluate("2 + 3 * 4");
        calculator.evaluate("(2 + 3) * 4");

        System.out.println("=== 变量操作 ===");
        calculator.evaluate("x = 10");
        calculator.evaluate("y = 20");
        calculator.evaluate("x + y");
        calculator.evaluate("x * y");
        calculator.evaluate("z = x + y * 2");

        calculator.showVariables();

        System.out.println("=== 比较运算 ===");
        calculator.evaluate("x > y");
        calculator.evaluate("x < y");
        calculator.evaluate("x == 10");
        calculator.evaluate("y == 20");

        System.out.println("=== 复杂表达式 ===");
        calculator.evaluate("result = (x + y) * 2 - 5");
        calculator.evaluate("result > 50");
    }
}
```

### 示例2：简单SQL解释器
```java
// SQL令牌类型
enum SqlTokenType {
    SELECT, FROM, WHERE, AND, OR, EQUALS, GREATER, LESS,
    IDENTIFIER, STRING, NUMBER, COMMA, SEMICOLON, EOF
}

// SQL令牌
class SqlToken {
    private SqlTokenType type;
    private String value;

    public SqlToken(SqlTokenType type, String value) {
        this.type = type;
        this.value = value;
    }

    public SqlTokenType getType() { return type; }
    public String getValue() { return value; }

    @Override
    public String toString() {
        return "SqlToken(" + type + ", '" + value + "')";
    }
}

// SQL词法分析器
class SqlLexer {
    private String input;
    private int position;
    private char currentChar;

    private static final Map<String, SqlTokenType> KEYWORDS = Map.of(
        "SELECT", SqlTokenType.SELECT,
        "FROM", SqlTokenType.FROM,
        "WHERE", SqlTokenType.WHERE,
        "AND", SqlTokenType.AND,
        "OR", SqlTokenType.OR
    );

    public SqlLexer(String input) {
        this.input = input.toUpperCase();
        this.position = 0;
        this.currentChar = input.length() > 0 ? this.input.charAt(0) : '\0';
    }

    private void advance() {
        position++;
        if (position >= input.length()) {
            currentChar = '\0';
        } else {
            currentChar = input.charAt(position);
        }
    }

    private void skipWhitespace() {
        while (currentChar != '\0' && Character.isWhitespace(currentChar)) {
            advance();
        }
    }

    private String readString() {
        StringBuilder result = new StringBuilder();
        advance(); // 跳过开始的引号

        while (currentChar != '\0' && currentChar != '\'') {
            result.append(currentChar);
            advance();
        }

        if (currentChar == '\'') {
            advance(); // 跳过结束的引号
        }

        return result.toString();
    }

    private String readNumber() {
        StringBuilder result = new StringBuilder();
        while (currentChar != '\0' && (Character.isDigit(currentChar) || currentChar == '.')) {
            result.append(currentChar);
            advance();
        }
        return result.toString();
    }

    private String readIdentifier() {
        StringBuilder result = new StringBuilder();
        while (currentChar != '\0' && (Character.isLetterOrDigit(currentChar) || currentChar == '_')) {
            result.append(currentChar);
            advance();
        }
        return result.toString();
    }

    public SqlToken nextToken() {
        while (currentChar != '\0') {
            if (Character.isWhitespace(currentChar)) {
                skipWhitespace();
                continue;
            }

            if (currentChar == '\'') {
                return new SqlToken(SqlTokenType.STRING, readString());
            }

            if (Character.isDigit(currentChar)) {
                return new SqlToken(SqlTokenType.NUMBER, readNumber());
            }

            if (Character.isLetter(currentChar)) {
                String identifier = readIdentifier();
                SqlTokenType type = KEYWORDS.getOrDefault(identifier, SqlTokenType.IDENTIFIER);
                return new SqlToken(type, identifier);
            }

            switch (currentChar) {
                case '=':
                    advance();
                    return new SqlToken(SqlTokenType.EQUALS, "=");
                case '>':
                    advance();
                    return new SqlToken(SqlTokenType.GREATER, ">");
                case '<':
                    advance();
                    return new SqlToken(SqlTokenType.LESS, "<");
                case ',':
                    advance();
                    return new SqlToken(SqlTokenType.COMMA, ",");
                case ';':
                    advance();
                    return new SqlToken(SqlTokenType.SEMICOLON, ";");
                default:
                    throw new RuntimeException("无效的SQL字符：" + currentChar);
            }
        }

        return new SqlToken(SqlTokenType.EOF, null);
    }
}

// SQL表达式接口
interface SqlExpression {
    Object evaluate(SqlContext context);
    String toString();
}

// 选择表达式
class SelectExpression implements SqlExpression {
    private List<String> columns;
    private String tableName;
    private SqlExpression whereClause;

    public SelectExpression(List<String> columns, String tableName, SqlExpression whereClause) {
        this.columns = columns;
        this.tableName = tableName;
        this.whereClause = whereClause;
    }

    @Override
    public Object evaluate(SqlContext context) {
        System.out.println("执行SELECT查询：");
        System.out.println("  表：" + tableName);
        System.out.println("  列：" + columns);

        List<Map<String, Object>> table = context.getTable(tableName);
        if (table == null) {
            throw new RuntimeException("表不存在：" + tableName);
        }

        List<Map<String, Object>> result = new ArrayList<>();

        for (Map<String, Object> row : table) {
            // 设置当前行上下文
            context.setCurrentRow(row);

            // 检查WHERE条件
            boolean matches = true;
            if (whereClause != null) {
                Object whereResult = whereClause.evaluate(context);
                matches = whereResult instanceof Boolean ? (Boolean) whereResult : false;
            }

            if (matches) {
                Map<String, Object> resultRow = new HashMap<>();

                if (columns.contains("*")) {
                    resultRow.putAll(row);
                } else {
                    for (String column : columns) {
                        if (row.containsKey(column)) {
                            resultRow.put(column, row.get(column));
                        }
                    }
                }

                result.add(resultRow);
            }
        }

        System.out.println("查询结果：" + result.size() + " 行");
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("SELECT ").append(String.join(", ", columns));
        sb.append(" FROM ").append(tableName);
        if (whereClause != null) {
            sb.append(" WHERE ").append(whereClause);
        }
        return sb.toString();
    }
}

// 列引用表达式
class ColumnExpression implements SqlExpression {
    private String columnName;

    public ColumnExpression(String columnName) {
        this.columnName = columnName;
    }

    @Override
    public Object evaluate(SqlContext context) {
        Map<String, Object> currentRow = context.getCurrentRow();
        if (currentRow == null) {
            throw new RuntimeException("没有当前行上下文");
        }

        Object value = currentRow.get(columnName);
        System.out.println("获取列值：" + columnName + " = " + value);
        return value;
    }

    @Override
    public String toString() {
        return columnName;
    }
}

// SQL字面量表达式
class SqlLiteralExpression implements SqlExpression {
    private Object value;

    public SqlLiteralExpression(Object value) {
        this.value = value;
    }

    @Override
    public Object evaluate(SqlContext context) {
        return value;
    }

    @Override
    public String toString() {
        if (value instanceof String) {
            return "'" + value + "'";
        }
        return String.valueOf(value);
    }
}

// SQL比较表达式
class SqlComparisonExpression implements SqlExpression {
    private SqlExpression left;
    private String operator;
    private SqlExpression right;

    public SqlComparisonExpression(SqlExpression left, String operator, SqlExpression right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    @Override
    public Object evaluate(SqlContext context) {
        Object leftValue = left.evaluate(context);
        Object rightValue = right.evaluate(context);

        System.out.println("SQL比较：" + leftValue + " " + operator + " " + rightValue);

        switch (operator) {
            case "=":
                return Objects.equals(leftValue, rightValue);
            case ">":
                return compareValues(leftValue, rightValue) > 0;
            case "<":
                return compareValues(leftValue, rightValue) < 0;
            default:
                throw new RuntimeException("不支持的比较操作符：" + operator);
        }
    }

    @SuppressWarnings("unchecked")
    private int compareValues(Object left, Object right) {
        if (left instanceof Comparable && right instanceof Comparable) {
            return ((Comparable<Object>) left).compareTo(right);
        }
        throw new RuntimeException("无法比较值：" + left + " 和 " + right);
    }

    @Override
    public String toString() {
        return left + " " + operator + " " + right;
    }
}

// SQL逻辑表达式
class SqlLogicalExpression implements SqlExpression {
    private SqlExpression left;
    private String operator;
    private SqlExpression right;

    public SqlLogicalExpression(SqlExpression left, String operator, SqlExpression right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    @Override
    public Object evaluate(SqlContext context) {
        boolean leftValue = (Boolean) left.evaluate(context);
        boolean rightValue = (Boolean) right.evaluate(context);

        switch (operator) {
            case "AND":
                return leftValue && rightValue;
            case "OR":
                return leftValue || rightValue;
            default:
                throw new RuntimeException("不支持的逻辑操作符：" + operator);
        }
    }

    @Override
    public String toString() {
        return "(" + left + " " + operator + " " + right + ")";
    }
}

// SQL上下文
class SqlContext {
    private Map<String, List<Map<String, Object>>> tables;
    private Map<String, Object> currentRow;

    public SqlContext() {
        this.tables = new HashMap<>();
        initializeSampleData();
    }

    private void initializeSampleData() {
        // 创建用户表
        List<Map<String, Object>> users = new ArrayList<>();

        Map<String, Object> user1 = new HashMap<>();
        user1.put("ID", 1);
        user1.put("NAME", "张三");
        user1.put("AGE", 25);
        user1.put("CITY", "北京");
        users.add(user1);

        Map<String, Object> user2 = new HashMap<>();
        user2.put("ID", 2);
        user2.put("NAME", "李四");
        user2.put("AGE", 30);
        user2.put("CITY", "上海");
        users.add(user2);

        Map<String, Object> user3 = new HashMap<>();
        user3.put("ID", 3);
        user3.put("NAME", "王五");
        user3.put("AGE", 22);
        user3.put("CITY", "北京");
        users.add(user3);

        Map<String, Object> user4 = new HashMap<>();
        user4.put("ID", 4);
        user4.put("NAME", "赵六");
        user4.put("AGE", 35);
        user4.put("CITY", "深圳");
        users.add(user4);

        tables.put("USERS", users);

        System.out.println("初始化示例数据：USERS表包含 " + users.size() + " 条记录");
    }

    public List<Map<String, Object>> getTable(String tableName) {
        return tables.get(tableName.toUpperCase());
    }

    public void setCurrentRow(Map<String, Object> row) {
        this.currentRow = row;
    }

    public Map<String, Object> getCurrentRow() {
        return currentRow;
    }

    public void showTables() {
        System.out.println("=== 数据库表 ===");
        for (String tableName : tables.keySet()) {
            List<Map<String, Object>> table = tables.get(tableName);
            System.out.println(tableName + ": " + table.size() + " 行");
        }
        System.out.println("===============");
    }
}

// SQL解析器
class SqlParser {
    private SqlLexer lexer;
    private SqlToken currentToken;

    public SqlParser(SqlLexer lexer) {
        this.lexer = lexer;
        this.currentToken = lexer.nextToken();
    }

    private void eat(SqlTokenType tokenType) {
        if (currentToken.getType() == tokenType) {
            currentToken = lexer.nextToken();
        } else {
            throw new RuntimeException("期望 " + tokenType + " 但得到 " + currentToken.getType());
        }
    }

    private SqlExpression parseComparison() {
        SqlExpression left = parsePrimary();

        if (currentToken.getType() == SqlTokenType.EQUALS ||
            currentToken.getType() == SqlTokenType.GREATER ||
            currentToken.getType() == SqlTokenType.LESS) {

            String operator = currentToken.getValue();
            eat(currentToken.getType());
            SqlExpression right = parsePrimary();

            return new SqlComparisonExpression(left, operator, right);
        }

        return left;
    }

    private SqlExpression parseLogical() {
        SqlExpression left = parseComparison();

        while (currentToken.getType() == SqlTokenType.AND ||
               currentToken.getType() == SqlTokenType.OR) {
            String operator = currentToken.getValue();
            eat(currentToken.getType());
            SqlExpression right = parseComparison();
            left = new SqlLogicalExpression(left, operator, right);
        }

        return left;
    }

    private SqlExpression parsePrimary() {
        if (currentToken.getType() == SqlTokenType.IDENTIFIER) {
            String identifier = currentToken.getValue();
            eat(SqlTokenType.IDENTIFIER);
            return new ColumnExpression(identifier);
        } else if (currentToken.getType() == SqlTokenType.STRING) {
            String value = currentToken.getValue();
            eat(SqlTokenType.STRING);
            return new SqlLiteralExpression(value);
        } else if (currentToken.getType() == SqlTokenType.NUMBER) {
            String numberStr = currentToken.getValue();
            eat(SqlTokenType.NUMBER);
            try {
                if (numberStr.contains(".")) {
                    return new SqlLiteralExpression(Double.parseDouble(numberStr));
                } else {
                    return new SqlLiteralExpression(Integer.parseInt(numberStr));
                }
            } catch (NumberFormatException e) {
                throw new RuntimeException("无效的数字：" + numberStr);
            }
        }

        throw new RuntimeException("无效的表达式");
    }

    public SqlExpression parseSelect() {
        eat(SqlTokenType.SELECT);

        // 解析列名
        List<String> columns = new ArrayList<>();
        columns.add(currentToken.getValue());
        eat(SqlTokenType.IDENTIFIER);

        while (currentToken.getType() == SqlTokenType.COMMA) {
            eat(SqlTokenType.COMMA);
            columns.add(currentToken.getValue());
            eat(SqlTokenType.IDENTIFIER);
        }

        // FROM子句
        eat(SqlTokenType.FROM);
        String tableName = currentToken.getValue();
        eat(SqlTokenType.IDENTIFIER);

        // WHERE子句（可选）
        SqlExpression whereClause = null;
        if (currentToken.getType() == SqlTokenType.WHERE) {
            eat(SqlTokenType.WHERE);
            whereClause = parseLogical();
        }

        return new SelectExpression(columns, tableName, whereClause);
    }
}

// SQL解释器
class SqlInterpreter {
    private SqlContext context;

    public SqlInterpreter() {
        this.context = new SqlContext();
    }

    public Object execute(String sql) {
        try {
            System.out.println("执行SQL：" + sql);

            SqlLexer lexer = new SqlLexer(sql);
            SqlParser parser = new SqlParser(lexer);
            SqlExpression expression = parser.parseSelect();

            System.out.println("解析后的表达式：" + expression);

            Object result = expression.evaluate(context);

            if (result instanceof List) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> rows = (List<Map<String, Object>>) result;
                printResultSet(rows);
            }

            return result;
        } catch (Exception e) {
            System.err.println("SQL执行错误：" + e.getMessage());
            return null;
        }
    }

    private void printResultSet(List<Map<String, Object>> rows) {
        if (rows.isEmpty()) {
            System.out.println("查询结果为空");
            return;
        }

        // 打印表头
        Set<String> columns = rows.get(0).keySet();
        System.out.println("=== 查询结果 ===");
        for (String column : columns) {
            System.out.printf("%-10s", column);
        }
        System.out.println();
        System.out.println("-".repeat(columns.size() * 10));

        // 打印数据行
        for (Map<String, Object> row : rows) {
            for (String column : columns) {
                System.out.printf("%-10s", row.get(column));
            }
            System.out.println();
        }
        System.out.println("=================");
    }

    public void showTables() {
        context.showTables();
    }
}

// SQL解释器使用示例
public class SqlInterpreterExample {
    public static void main(String[] args) {
        SqlInterpreter interpreter = new SqlInterpreter();

        interpreter.showTables();

        System.out.println("\n=== SQL查询示例 ===");

        // 基本查询
        interpreter.execute("SELECT * FROM USERS");

        // 指定列查询
        interpreter.execute("SELECT NAME, AGE FROM USERS");

        // 带WHERE条件的查询
        interpreter.execute("SELECT * FROM USERS WHERE AGE > 25");

        // 字符串比较
        interpreter.execute("SELECT NAME, CITY FROM USERS WHERE CITY = '北京'");

        // 复合条件查询
        interpreter.execute("SELECT * FROM USERS WHERE AGE > 25 AND CITY = '北京'");

        // 或条件查询
        interpreter.execute("SELECT NAME, AGE FROM USERS WHERE AGE < 25 OR CITY = '上海'");
    }
}
```

## ✅ 优势分析

### 1. **易于扩展**
可以方便地添加新的语法规则和表达式类型。

### 2. **易于实现**
对于简单的语法，实现相对直观。

### 3. **易于修改**
可以独立修改和测试每个语法规则。

### 4. **符合开闭原则**
新增语法规则不需要修改现有代码。

## ⚠️ 注意事项

### 1. **性能问题**
```java
// 对于复杂语法，解释器性能可能较差
// 可以考虑编译为中间代码或使用其他解析技术
class OptimizedInterpreter {
    private Map<String, Object> cache = new HashMap<>();

    public Object interpret(String expression) {
        // 缓存解析结果
        if (cache.containsKey(expression)) {
            return cache.get(expression);
        }

        Object result = doInterpret(expression);
        cache.put(expression, result);
        return result;
    }

    private Object doInterpret(String expression) {
        // 实际解释逻辑
        return null;
    }
}
```

### 2. **复杂性增长**
语法规则增多时，类的数量会快速增长。

### 3. **调试困难**
复杂的表达式树可能难以调试。

## 🆚 与其他模式对比

| 特性 | 解释器模式 | 策略模式 | 命令模式 |
|------|----------|----------|----------|
| 目的 | 解释语言 | 选择算法 | 封装请求 |
| 结构 | 树形结构 | 平行结构 | 线性结构 |
| 扩展性 | 语法规则 | 算法策略 | 命令类型 |
| 复杂度 | 较高 | 中等 | 较低 |

## 🎯 实战建议

### 1. **何时使用解释器模式**
- 语法相对简单且稳定
- 效率不是关键考虑因素
- 需要频繁地解释执行表达式
- 想要将语法规则表示为类

### 2. **设计原则**
```java
// 好的解释器设计
public abstract class Expression {
    // 提供公共的解释接口
    public abstract Object interpret(Context context);

    // 提供表达式优化接口
    public Expression optimize() {
        return this;
    }

    // 提供表达式验证接口
    public boolean validate(Context context) {
        return true;
    }

    // 提供调试信息
    public String getDebugInfo() {
        return this.toString();
    }
}
```

### 3. **性能优化**
```java
// 使用享元模式优化常量表达式
class ConstantExpressionFactory {
    private static final Map<Object, Expression> constants = new HashMap<>();

    public static Expression getConstant(Object value) {
        return constants.computeIfAbsent(value, v -> new ConstantExpression(v));
    }
}

// 编译时优化
class CompilingInterpreter {
    public Expression compile(String source) {
        Expression ast = parse(source);
        return optimize(ast);
    }

    private Expression optimize(Expression expr) {
        // 常量折叠、死代码消除等优化
        return expr;
    }
}
```

## 🧠 记忆技巧

**口诀：解释语言树结构**
- **解**析文法定规则
- **释**义表达有层次
- **语**法规则类来表
- **言**简意赅好理解
- **树**形结构递归解
- **结**点对应文法式
- **构**建解释器体系

**形象比喻：**
解释器模式就像**翻译官**：
- 源语言（输入表达式）需要翻译
- 文法规则（翻译规则）指导翻译过程
- 解释器（翻译官）按规则执行翻译
- 目标语言（执行结果）是最终输出

## 🎉 总结

解释器模式是一种专门用于语言处理的设计模式，它为简单语言的解释提供了优雅的解决方案。虽然对于复杂语言可能不是最佳选择，但在特定场景下（如DSL、配置文件解析、表达式计算等）仍然非常有用。

**核心思想：** 🗣️ 将语言的文法规则表示为类的层次结构，让每个规则负责解释对应的语言结构！

至此，我们已经完成了所有23种GOF设计模式的详细讲解。下一篇将是**设计模式总结篇**，为这个系列画上完美的句号！ 🎊