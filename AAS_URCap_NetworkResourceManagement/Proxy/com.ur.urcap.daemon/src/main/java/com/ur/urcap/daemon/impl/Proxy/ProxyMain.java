package com.ur.urcap.daemon.impl.Proxy;

public class ProxyMain {
    public static void main(String[] args) {
        Proxy p = new Proxy();
        p.startAllServicesOfTcpCommunication();
    }
}
