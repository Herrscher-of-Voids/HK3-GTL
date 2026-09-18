# HK3-GTL

崩坏三 × 格雷科技现代版扩展模组，面向 GTL 整合包的终局及 MAX 后阶段，包含崩坏能工业、文明研究与巨构设施等内容。

当前源码版本：`0.4.0-beta.1`。运行环境：Minecraft `1.20.1`、Forge `47.4.16`、Java `17`。

## 使用

`releases/hk3gtl-0.4.0-beta.1.jar` 为随仓库提供的现有构建产物。请备份存档后，将其放入配齐前置模组的实例的 `mods/` 目录。本模组依赖 GTL 环境，完整依赖声明见 `src/main/resources/META-INF/mods.toml`。

## 构建

准备 Java 17，并按 `libs/README.md` 放置本地依赖后运行：

```powershell
.\gradlew.bat build
```

Linux/macOS 可运行 `bash gradlew build`。构建结果位于 `build/libs/`。

## 许可

仓库保留已有 `LICENSE`、`LICENSE.txt` 及 `CREDITS.txt`。当前模组元数据声明为 `All Rights Reserved`，与仓库已有 MIT 许可文件存在不一致；授权范围需由作者明确。第三方内容的许可与署名归各自作者所有。
