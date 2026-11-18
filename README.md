# HK3GTL 1.1.0

面向 Minecraft 1.20.1、Forge 和 GregTech Leisure 增强版 3.9 的工业与剧情扩展。

更新内容见 [CHANGELOG.md](CHANGELOG.md)。安装时使用 GitHub Release 提供的 `HK3GTL-1.1.0.jar`。

## 从源码构建

此版本的源码包含生产 Java 代码、Gradle 配置及发布用游戏资源。结构和场景以游戏读取的压缩格式提供。

安装 JDK 21、JDK 17 和 Python 3.9 或更高版本，按 [libs/README.md](libs/README.md) 准备本地模组依赖。随后执行：

```powershell
.\gradlew.bat remapJar
```

正式 JAR 生成在 `build/libs/`。
