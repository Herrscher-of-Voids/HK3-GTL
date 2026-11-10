import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.nio.file.Path;

public class RebuildControllerFronts {
    private static final Path BLOCK_DIR = Path.of("").toAbsolutePath().normalize()
            .resolve("src/main/resources/assets/hk3gtl/textures/block");

    public static void main(String[] args) throws Exception {
        writeFront("honkai_absorption_tower", 0xFF0B1328, 0xFF153463, 0xFF2CC8FF, 0xFF96F0FF);
        writeFront("honkai_crystal_condenser", 0xFF0B1630, 0xFF27486E, 0xFF52D4FF, 0xFFE0FCFF);
        writeFront("soulium_smeltery", 0xFF14161B, 0xFF46525F, 0xFF5DD7FF, 0xFFD4E9F7);
        writeFront("abyss_research_analysis_matrix", 0xFF0D1125, 0xFF2B2C65, 0xFF7A70FF, 0xFFCBCCFF);
    }

    private static void writeFront(String name, int base, int panel, int glow, int accent) throws Exception {
        BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 16; y++) {
            for (int x = 0; x < 16; x++) {
                img.setRGB(x, y, base);
            }
        }

        frame(img, 1, 1, 14, 14, panel);
        frame(img, 2, 2, 13, 13, accent);
        fill(img, 4, 4, 11, 11, panel);
        fill(img, 5, 5, 10, 10, glow);
        fill(img, 6, 6, 9, 9, accent);

        img.setRGB(3, 4, accent);
        img.setRGB(12, 4, accent);
        img.setRGB(3, 11, accent);
        img.setRGB(12, 11, accent);

        img.setRGB(7, 7, 0xFFFFFFFF);
        img.setRGB(8, 7, 0xFFFFFFFF);
        img.setRGB(7, 8, 0xFFFFFFFF);
        img.setRGB(8, 8, 0xFFFFFFFF);

        ImageIO.write(img, "png", BLOCK_DIR.resolve(name + ".png").toFile());
        System.out.println("Updated front: " + name);
    }

    private static void frame(BufferedImage img, int x1, int y1, int x2, int y2, int color) {
        for (int x = x1; x <= x2; x++) {
            img.setRGB(x, y1, color);
            img.setRGB(x, y2, color);
        }
        for (int y = y1; y <= y2; y++) {
            img.setRGB(x1, y, color);
            img.setRGB(x2, y, color);
        }
    }

    private static void fill(BufferedImage img, int x1, int y1, int x2, int y2, int color) {
        for (int y = y1; y <= y2; y++) {
            for (int x = x1; x <= x2; x++) {
                img.setRGB(x, y, color);
            }
        }
    }
}
