package com.sirin.hk3gtl.common.communication;

/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
public enum Hk3FirstContactState {
    LOCKED, AVAILABLE, READ, ACCEPTED, DECLINED;

    public static final String LETTER_FACT = "CM-MAX-OTTO";
    public static final String ACCEPT_FACT = "CM-MAX-REPLY-ACCEPT";
    public static final String DECLINE_FACT = "CM-MAX-REPLY-DECLINE";

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3FirstContactState discover() { return this == LOCKED ? AVAILABLE : this; }

    /** 打开首信记录已读，关闭界面不会代表拒绝。 / Opening marks read; closing never means refusal. */
    public Hk3FirstContactState read() { return this == AVAILABLE ? READ : this; }

    /** 服务端单次提交；未读或已答复时保持原状态，返回值用于判断是否接受本次请求。 / Single server submission; unread or final states cannot change. */
    public Hk3FirstContactState reply(boolean accept) {
        return this == READ ? (accept ? ACCEPTED : DECLINED) : this;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean hasObservationData() { return this != LOCKED; }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public String replyFact() { return this == ACCEPTED ? ACCEPT_FACT : this == DECLINED ? DECLINE_FACT : ""; }
}
