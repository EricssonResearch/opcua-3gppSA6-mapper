package com.ur.urcap.daemon.impl.Proxy;

import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.CommunicationsWithCAPIF;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.getLocalIPAddress;
import com.ur.urcap.daemon.impl.Proxy.Threads.ThreadForTCPCommunication;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.FilterDropSenderFunction;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.SpeedRecieverFunction;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.URControllerByteRecieverFunction;

public class Proxy
{
    private final String speedSenderServersAddress = "yourHostsIpAddress";
    private final int speedSenderServersPort = 9000;
    private final int clientPort = 9001;
    private final String urControllersAddress;
    private final int urControllersPort = 30013;

    private Thread urcbrf;
    private Thread sfrf;
    private Thread fdsf;

    public Proxy()
    {
        getLocalIPAddress glia = new getLocalIPAddress();
        glia.getLocalIP();
        this.urControllersAddress = glia.getLocalIP();

        this.urcbrf = new ThreadForTCPCommunication(new URControllerByteRecieverFunction(urControllersAddress, urControllersPort));
        this.sfrf = new ThreadForTCPCommunication(new SpeedRecieverFunction(speedSenderServersAddress, speedSenderServersPort));
        this.fdsf = new ThreadForTCPCommunication(new FilterDropSenderFunction(clientPort));
    }

    private void implementCommunicationWithCAPIF() throws Exception {
        CommunicationsWithCAPIF cwc = new CommunicationsWithCAPIF();
        cwc.authenticationAndAuthorization();
    }

    public void startAllServicesOfTcpCommunication()
    {
        try
        {
            implementCommunicationWithCAPIF();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }

        this.urcbrf = new ThreadForTCPCommunication(new URControllerByteRecieverFunction(urControllersAddress, urControllersPort));
        this.sfrf = new ThreadForTCPCommunication(new SpeedRecieverFunction(speedSenderServersAddress, speedSenderServersPort));
        this.fdsf = new ThreadForTCPCommunication(new FilterDropSenderFunction(clientPort));

        this.urcbrf.start();
        this.sfrf.start();
        this.fdsf.start();
    }

    public void stopAllServicesOfTcpCommunication()
    {
        this.urcbrf.interrupt();
        this.sfrf.interrupt();
        this.fdsf.interrupt();
    }
}
