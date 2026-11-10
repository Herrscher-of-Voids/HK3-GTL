import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Path;

/**
 * 【变更记录 #1】2026-09-30 02:20:26（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class RecolorGtTextures {
    private static final Path WORKSPACE = Path.of("").toAbsolutePath().normalize();
    private static final Path TARGET_ITEM_DIR = WORKSPACE.resolve("src/main/resources/assets/hk3gtl/textures/item");
    private static final Path TARGET_BLOCK_DIR = WORKSPACE.resolve("src/main/resources/assets/hk3gtl/textures/block");
    private static final String REF_DIR = "C:/Users/OWNER/.cursor/projects/c-Users-OWNER-Desktop-hk3gtl/assets/";

    private static final int[] PALETTE = new int[] {
            0xFF061032,
            0xFF0A1F5E,
            0xFF163B8C,
            0xFF1F5FBF,
            0xFF32A6FF,
            0xFF6AD6FF,
            0xFF9EE8FF,
            0xFF8E62E8,
            0xFFC8D6E8,
            0xFF7F8FA8
    };

    public static void main(String[] args) throws Exception {
        recolorItem("electric_motor_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_motor-3493ee00-4675-4207-957a-aeeb1fa2e3c4.png");
        recolorItem("electric_piston_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_piston-d2e0475a-45af-4944-8131-d6c681a30935.png");
        recolorItem("electric_pump_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_pump-a264f453-4d56-46af-97cb-dc891997d1ed.png");
        recolorItem("conveyor_module_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_conveyor_module-855d038a-bfcb-46f6-ba1a-7e1ccea63a75.png");
        recolorItem("robot_arm_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_robot_arm-43b0d915-2d5e-4412-a8bf-1d51f0914cad.png");
        recolorItem("field_generator_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_field_generator-d3175a72-9a4f-42ae-a51f-1f55698eff7c.png");
        recolorItem("emitter_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_emitter-227d37a4-8797-4ee6-be77-5cc1f672cf46.png");
        recolorItem("sensor_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_sensor-e8e04397-03a7-480c-b46a-64d7c8415423.png");
        recolorItem("fluid_regulator_hbv", "c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_fluid_regulator-cd7e6dbe-9e99-40ba-8a4e-390193c1880a.png");

        generateController("honkai_absorption_tower", 0xFF0B1020, 0xFF1D2C5A, 0xFF35B6FF, 0xFF88E4FF);
        generateController("honkai_crystal_condenser", 0xFF0A1328, 0xFF2C3F66, 0xFF49C7FF, 0xFFC7F2FF);
        generateController("soulium_smeltery", 0xFF11141A, 0xFF4A5866, 0xFF59C6FF, 0xFFB6D6F2);
    }

    private static void recolorItem(String targetName, String refFile) throws Exception {
        BufferedImage src = ImageIO.read(new File(REF_DIR + refFile));
        BufferedImage out = new BufferedImage(src.getWidth(), src.getHeight(), BufferedImage.TYPE_INT_ARGB);

        for (int y = 0; y < src.getHeight(); y++) {
            for (int x = 0; x < src.getWidth(); x++) {
                int argb = src.getRGB(x, y);
                int alpha = (argb >>> 24) & 0xFF;
                if (alpha == 0) {
                    out.setRGB(x, y, 0);
                    continue;
                }
                int r = (argb >>> 16) & 0xFF;
                int g = (argb >>> 8) & 0xFF;
                int b = argb & 0xFF;
                int brightness = (r * 30 + g * 59 + b * 11) / 100;
                int mapped = mapBrightness(brightness);
                out.setRGB(x, y, (alpha << 24) | (mapped & 0x00FFFFFF));
            }
        }

        ImageIO.write(out, "png", TARGET_ITEM_DIR.resolve(targetName + ".png").toFile());
        System.out.println("Wrote item texture: " + targetName);
    }

    private static int mapBrightness(int brightness) {
        int idx = Math.min(PALETTE.length - 1, Math.max(0, brightness / 26));
        return PALETTE[idx];
    }

    private static void generateController(String name, int bg, int panel, int glow, int accent) throws Exception {
        BufferedImage out = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 16; y++) {
            for (int x = 0; x < 16; x++) {
                out.setRGB(x, y, bg);
            }
        }

        for (int x = 1; x < 15; x++) {
            out.setRGB(x, 1, panel);
            out.setRGB(x, 14, panel);
        }
        for (int y = 1; y < 15; y++) {
            out.setRGB(1, y, panel);
            out.setRGB(14, y, panel);
        }

        for (int y = 4; y <= 11; y++) {
            for (int x = 4; x <= 11; x++) {
                out.setRGB(x, y, panel);
            }
        }
        for (int y = 5; y <= 10; y++) {
            for (int x = 5; x <= 10; x++) {
                out.setRGB(x, y, glow);
            }
        }
        for (int x = 2; x <= 13; x++) {
            out.setRGB(x, 3, accent);
            out.setRGB(x, 12, accent);
        }
        for (int y = 2; y <= 13; y++) {
            out.setRGB(3, y, accent);
            out.setRGB(12, y, accent);
        }
        out.setRGB(7, 7, 0xFFFFFFFF);
        out.setRGB(8, 7, 0xFFFFFFFF);
        out.setRGB(7, 8, 0xFFFFFFFF);
        out.setRGB(8, 8, 0xFFFFFFFF);

        ImageIO.write(out, "png", TARGET_BLOCK_DIR.resolve(name + ".png").toFile());
        System.out.println("Wrote controller texture: " + name);
    }
}
