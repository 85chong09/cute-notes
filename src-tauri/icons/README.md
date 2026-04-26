# 图标文件

此文件夹需要包含以下图标文件才能构建Tauri应用：

## 必需的图标文件

- `32x32.png` - 32x32像素的PNG图标
- `128x128.png` - 128x128像素的PNG图标
- `icon.icns` - macOS图标格式
- `icon.ico` - Windows图标格式

## 如何生成图标

### 方法1：使用Tauri CLI（推荐）

如果您有一个1024x1024像素的PNG源图标：

```powershell
cargo tauri icon path\to\your\1024px-icon.png
```

### 方法2：手动创建

1. 创建一个简单的32x32 PNG图标（可以用画图或其他工具）
2. 将其保存为 `32x32.png`

### 方法3：使用在线工具

- https://www.icoconverter.com/ - 将PNG转换为ICO
- https://cloudconvert.com/png-to-icns - 转换为ICNS格式

## 临时解决方案

如果您只是想测试开发版本，可以先使用最小配置。修改 `tauri.conf.json` 中的bundle配置以使用单个图标文件，或者先在开发模式下测试。
