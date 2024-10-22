package com.ur.urcap.daemon.impl.Proxy.Threads.Functions;

import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;

public class URControllerByteRecieverFunction extends ThreadFunction
{
    private final String urControllersAddress;
    private final int urControllersPort;

    private Socket socket;

    public URControllerByteRecieverFunction(String urControllersAddressParam, int urControllersPortParam)
    {
        this.urControllersAddress = urControllersAddressParam;
        this.urControllersPort = urControllersPortParam;
    }

    @Override
    public void doOperation()
    {
        try
        {
            this.socket = null;
            InputStream inputStream = null;

            this.socket = new Socket(urControllersAddress, urControllersPort);
            inputStream = this.socket.getInputStream();

            if(inputStream != null)
            {
                byte[] buffer = new byte[1220];
                int bytesRead;

                while ((bytesRead = inputStream.read(buffer)) != -1)
                {
                    String receivedData = new String(buffer, 0, bytesRead);
                    data = receivedData;
                }
            }
        }
        catch (IOException e)
        {
            throw new RuntimeException(e);
        }
    }

    public void closeSocket() throws IOException
    {
        this.socket.close();   
    }
}
