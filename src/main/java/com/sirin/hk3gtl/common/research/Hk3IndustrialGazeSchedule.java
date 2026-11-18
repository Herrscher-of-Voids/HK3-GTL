package com.sirin.hk3gtl.common.research;

 






public final class Hk3IndustrialGazeSchedule {
    private Hk3IndustrialGazeSchedule() {}

    public static boolean throttles(double gaze, long gameTime, long position) {
        int allowed = gaze < 200 ? 100 : gaze < 500 ? 95 : gaze < 800 ? 75 : gaze < 1000 ? 60 : 50;
        return (Math.floorMod(gameTime, 100L) + Math.floorMod(position, 100L)) % 100L >= allowed;
    }
}
