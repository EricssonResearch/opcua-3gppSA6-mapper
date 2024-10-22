package com.ur.urcap.daemon.impl.Proxy.Threads.Functions;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.net.Socket;

import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.getLocalIPAddress;


public class SpeedRecieverFunction extends ThreadFunction
{
    private final String speedSenderServersAddress;
    private final int speedSenderServersPort;

    private Socket socket;

    public SpeedRecieverFunction(String speedSenderServersAddressParam, int speedSenderServersPortParam)
    {
        this.speedSenderServersAddress = speedSenderServersAddressParam;
        this.speedSenderServersPort = speedSenderServersPortParam;
    }

    @Override
    public void doOperation()
    {
        try
        {
            this.socket = null;
            InputStream inputStream = null;

            this.socket = new Socket(speedSenderServersAddress, speedSenderServersPort);
            inputStream = this.socket.getInputStream();

            if(inputStream != null)
            {
                DataInputStream dataInputStream = new DataInputStream(inputStream);

                while (true)
                {
                    float receivedData = dataInputStream.readFloat();
                    actualSpeed = receivedData;

                    String host = new getLocalIPAddress().getLocalIP();
                    int port = 30003;
        
                    try {
                        Socket socket = new Socket(host, port);
                        PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

                        out.println("set speed " + actualSpeed);

                        out.close();
                        socket.close();
                    } 
                    catch (IOException e)
                    {
                        System.out.println("Error: " + e.getMessage());
                    }
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
        
    }
}
