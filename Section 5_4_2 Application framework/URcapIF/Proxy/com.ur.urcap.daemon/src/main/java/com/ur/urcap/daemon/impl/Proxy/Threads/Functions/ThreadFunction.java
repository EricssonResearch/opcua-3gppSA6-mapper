package com.ur.urcap.daemon.impl.Proxy.Threads.Functions;

import java.io.IOException;

public abstract class ThreadFunction
{
    protected static String data;
    protected static int counter = 0;
    protected static float actualSpeed = 0.0f;

    public abstract void doOperation();
    public abstract void closeSocket() throws IOException;
}
