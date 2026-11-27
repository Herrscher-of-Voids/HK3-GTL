package com.sirin.hk3gtl.common.compat.stargate;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.util.UUID;
import java.util.function.Consumer;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.fml.ModList;
import net.povstalec.sgjourney.common.block_entities.stargate.AbstractStargateEntity;
import net.povstalec.sgjourney.common.data.StargateNetwork;
import net.povstalec.sgjourney.common.sgjourney.Address;
import net.povstalec.sgjourney.common.sgjourney.StargateConnection;
import net.povstalec.sgjourney.common.sgjourney.StargateInfo;
import net.povstalec.sgjourney.common.sgjourney.stargate.SGJourneyStargate;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;

public final class Hk3StargateApi {
    private static final String PACKAGE = "net.povstalec.sgjourney.common.";
    private static final String NEW_CONNECTION = "events.custom.StargateConnectionEvent";
    private static final boolean MODERN = Files.isRegularFile(ModList.get().getModFileById("sgjourney").getFile()
            .findResource((PACKAGE + NEW_CONNECTION).replace('.', '/') + ".class"));

    private Hk3StargateApi() {}

    public static void registerConnectionEvents() {
        String name = MODERN ? NEW_CONNECTION : "events.custom.ConnectionEvent";
        Method connection = method(type(name), "getStargateConnection");
        listen(name + "$Establish", event -> Hk3StargateQuestEvents.connected(call(connection, event)));
        listen(name + "$Terminate", event -> Hk3StargateQuestEvents.terminated(call(connection, event)));
    }

    private static void listen(String name, Consumer<Event> listener) {
        listen(type(name).asSubclass(Event.class), listener);
    }

    private static <E extends Event> void listen(Class<E> event, Consumer<? super E> listener) {
        MinecraftForge.EVENT_BUS.addListener(EventPriority.LOWEST, false, event, listener::accept);
    }

    public static Vec3 position(MinecraftServer server, Stargate gate) {
        return MODERN ? call(Modern.POSITION, gate) : gate.getPosition(server);
    }

    public static Vec3 forward(MinecraftServer server, Stargate gate) {
        return MODERN ? call(Modern.FORWARD, gate) : gate.getForward(server);
    }

    public static Vec3 up(MinecraftServer server, Stargate gate) {
        return MODERN ? call(Modern.UP, gate) : gate.getUp(server);
    }

    public static Vec3 right(MinecraftServer server, Stargate gate) {
        return MODERN ? call(Modern.RIGHT, gate) : gate.getRight(server);
    }

    static boolean isDhdMenu(AbstractContainerMenu menu) {
        return DhdMenu.TYPE.isInstance(menu);
    }

    private static final class DhdMenu {
        private static final Class<?> TYPE = type(MODERN ? "menu.dhd.AbstractDHDMenu" : "menu.AbstractDHDMenu");
    }

    static boolean registered(MinecraftServer server, Stargate gate) {
        return MODERN ? call(Modern.LOADED, gate) : gate.isValid(server);
    }

    static AbstractStargateEntity blockEntity(MinecraftServer server, Stargate gate) {
        if (MODERN) return Modern.BLOCK_GATE.isInstance(gate) ? call(Modern.ENTITY, gate, server) : null;
        return gate instanceof SGJourneyStargate nativeGate ? nativeGate.getStargateEntity(server) : null;
    }

    public static int openTime(StargateNetwork network, UUID connectionId) {
        if (!MODERN) return network.getOpenTime(connectionId);
        StargateConnection connection = call(Modern.CONNECTION, network, connectionId);
        return connection == null ? 0 : connection.getOpenTime();
    }

    static Component dialError(AbstractStargateEntity gate, Address address) {
        if (MODERN) {
            Object result = call(Modern.DIAL, gate, address, false, Modern.EXECUTE);
            StargateInfo.Feedback feedback = call(Modern.FEEDBACK, result);
            return feedback.isError() ? call(Modern.FEEDBACK_MESSAGE, result) : null;
        }
        var feedback = gate.engageStargate(address, false);
        return feedback.isError() ? feedback.getFeedbackMessage() : null;
    }

    static void update(AbstractStargateEntity gate) {
        if (MODERN) call(Modern.UPDATE, gate);
        else gate.updateStargate(true);
    }

    static void charge(AbstractStargateEntity gate) {
        long capacity = gate.getEnergyCapacity();
        if (MODERN) {
            Object storage = get(Modern.ENERGY_STORAGE, gate);
            if (Hk3StargateApi.<Long>call(Modern.STORED_ENERGY, storage) >= capacity) return;
            call(Modern.SET_ENERGY, storage, capacity);
        } else {
            if (gate.getEnergyStored() >= capacity) return;
            gate.setEnergy(capacity);
        }
        gate.setChanged();
    }

    private static final class Modern {
        private static final Class<?> BLOCK_GATE = type("sgjourney.stargate.BlockEntityStargate");
        private static final Class<?> ACTION = type("sgjourney.Dialing$Action");
        private static final Class<?> RESULT = type("sgjourney.StargateInfo$FeedbackMessage");
        private static final Object EXECUTE = call(method(ACTION, "valueOf", String.class), null, "EXECUTE");
        private static final Method POSITION = method(Stargate.class, "getPosition");
        private static final Method FORWARD = method(Stargate.class, "getForward");
        private static final Method UP = method(Stargate.class, "getUp");
        private static final Method RIGHT = method(Stargate.class, "getRight");
        private static final Method LOADED = method(Stargate.class, "isLoaded");
        private static final Method ENTITY = method(BLOCK_GATE, "getStargateEntity", MinecraftServer.class);
        private static final Method CONNECTION = method(StargateNetwork.class, "getConnection", UUID.class);
        private static final Method DIAL = method(AbstractStargateEntity.class, "engageStargate", Address.class, boolean.class, ACTION);
        private static final Method UPDATE = method(AbstractStargateEntity.class, "updateStargate");
        private static final Field ENERGY_STORAGE = field(AbstractStargateEntity.class, "energyStorage");
        private static final Method STORED_ENERGY = method(ENERGY_STORAGE.getType(), "getTrueEnergyStored");
        private static final Method SET_ENERGY = method(ENERGY_STORAGE.getType(), "setEnergy", long.class);
        private static final Method FEEDBACK = method(RESULT, "feedback");
        private static final Method FEEDBACK_MESSAGE = method(RESULT, "getMessageComponent");
    }

    private static Class<?> type(String name) {
        try {
            return Class.forName(PACKAGE + name, false, Stargate.class.getClassLoader());
        } catch (ClassNotFoundException e) {
            throw new IllegalStateException("星门之旅缺少接口 " + name, e);
        }
    }

    private static Method method(Class<?> owner, String name, Class<?>... parameters) {
        try {
            return owner.getMethod(name, parameters);
        } catch (NoSuchMethodException e) {
            throw new IllegalStateException("星门之旅接口不匹配 " + owner.getName() + "." + name, e);
        }
    }

    private static Field field(Class<?> owner, String name) {
        try {
            return owner.getField(name);
        } catch (NoSuchFieldException e) {
            throw new IllegalStateException("星门之旅接口不匹配 " + owner.getName() + "." + name, e);
        }
    }

    private static Object get(Field field, Object owner) {
        try {
            return field.get(owner);
        } catch (IllegalAccessException e) {
            throw new IllegalStateException("星门之旅接口读取失败 " + field, e);
        }
    }

    @SuppressWarnings("unchecked")
    private static <T> T call(Method method, Object owner, Object... args) {
        try {
            return (T) method.invoke(owner, args);
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("星门之旅接口调用失败 " + method, e);
        }
    }
}
