package com.ur.urcap.daemon.impl.Proxy.Threads;

import java.io.IOException;

import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.ThreadFunction;

public class ThreadForTCPCommunication extends Thread
{
    private final ThreadFunction function;

    public ThreadForTCPCommunication(ThreadFunction functionParam)
    {
        this.function = functionParam;
    }

    @Override
    public void run()
    {
        this.function.doOperation();
    }

    public void interrupt()
    {
        try
        {
            this.function.closeSocket();
        }
        catch(IOException ioe)
        {

        }
        finally
        {
            super.interrupt();
        }
    }
}
