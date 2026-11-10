package com.sirin.hk3gtl.common.gui;

/** 中文说明：该处说明已按当前代码行为整理。*/
public record Hk3GuiFit(double scale, double left, double top) {
    /** 参数及返回值均使用GUI像素，不是帧缓冲像素。 / All dimensions and offsets use GUI pixels, not framebuffer pixels. */
    public static Hk3GuiFit centered(int screenWidth, int screenHeight, int width, int height, int margin) {
        if (screenWidth < 1 || screenHeight < 1 || width < 1 || height < 1 || margin < 0)
            throw new IllegalArgumentException("Invalid GUI dimensions");
        double scale = Math.min(1, Math.min(Math.max(1, screenWidth - 2.0 * margin) / width,
                Math.max(1, screenHeight - 2.0 * margin) / height));
        return new Hk3GuiFit(scale, (screenWidth - width * scale) / 2, (screenHeight - height * scale) / 2);
    }
    /** 屏幕→设计坐标；不截断，以保留面板外负坐标及拖动精度。 / Screen to design coordinates, retaining outside positions and drag precision. */
    public double x(double screenX) { return (screenX - left) / scale; }
    public double y(double screenY) { return (screenY - top) / scale; }
    /** 设计→屏幕坐标，供渲染裁剪边界使用。 / Design to screen coordinates for rendering and clipping. */
    public double screenX(double x) { return left + x * scale; }
    public double screenY(double y) { return top + y * scale; }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean contains(double x, double y, int width, int height) {
        return x(x) >= 0 && y(y) >= 0 && x(x) < width && y(y) < height;
    }
}
