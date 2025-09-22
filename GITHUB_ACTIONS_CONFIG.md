# GitHub Actions 配置说明

## 当前配置状态

✅ **已禁用自动触发**: push到main/master分支不会自动执行GitHub Actions
✅ **保留手动触发**: 可以在GitHub网页上手动执行工作流

## 配置方法

### 方法一：完全禁用自动触发（当前使用）

文件：`.github/workflows/hugo.yaml`

```yaml
on:
  # 在推送到默认分支时运行 - 已禁用自动触发
  # push:
  #   branches:
  #     - main
  #     - master

  # 允许手动运行工作流
  workflow_dispatch:
```

**使用方式**：
- ✅ 不会自动执行GitHub Actions
- ✅ 可以手动触发：GitHub仓库页面 → Actions → Deploy Hugo site to Pages → Run workflow

### 方法二：基于Commit Message的条件触发

文件：`.github/workflows/hugo-conditional.yaml`

**使用方式**：
- 🔄 **自动执行**：正常commit和push
- ⏸️ **跳过执行**：在commit message中添加 `[skip ci]` 或 `[ci skip]`

**示例**：
```bash
# 这个commit会触发Actions
git commit -m "更新文章内容"

# 这个commit会跳过Actions
git commit -m "更新文章内容 [skip ci]"
git commit -m "修复typo [ci skip]"
```

## 切换配置

### 启用自动触发
1. 编辑 `.github/workflows/hugo.yaml`
2. 取消注释push配置：
```yaml
on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:
```

### 使用条件触发
1. 删除或重命名 `hugo.yaml`
2. 将 `hugo-conditional.yaml` 重命名为 `hugo.yaml`

## 手动触发工作流

1. 访问GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Deploy Hugo site to Pages"
4. 点击 "Run workflow" 按钮
5. 选择分支（通常是main）
6. 点击绿色的 "Run workflow" 按钮

## 查看工作流状态

- 🟢 **成功**: 绿色对勾
- 🔴 **失败**: 红色X
- 🟡 **进行中**: 黄色圆圈
- ⚫ **跳过**: 灰色横线

---

💡 **建议**: 使用方法一（完全禁用自动触发）可以避免不必要的资源消耗，只在需要时手动部署。