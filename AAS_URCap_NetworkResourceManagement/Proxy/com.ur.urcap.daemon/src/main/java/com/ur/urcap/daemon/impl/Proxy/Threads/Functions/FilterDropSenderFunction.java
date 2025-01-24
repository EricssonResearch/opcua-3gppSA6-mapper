package com.ur.urcap.daemon.impl.Proxy.Threads.Functions;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class FilterDropSenderFunction extends ThreadFunction {
    private final int clientPort;

    private ServerSocket serverSocket;
    private Socket clientSocket;

    public FilterDropSenderFunction(int clientPortParam) {
        this.clientPort = clientPortParam;
    }

    @Override
    public void doOperation() {
        try {
            this.serverSocket = new ServerSocket(this.clientPort);
            this.clientSocket = this.serverSocket.accept();

            DataOutputStream out = new DataOutputStream(this.clientSocket.getOutputStream());

            long lastTime = System.currentTimeMillis();

            while (true) {
                if (actualSpeed == 0.1f) {
                    if (System.currentTimeMillis() - lastTime >= 20) {
                        out.writeUTF("\nCounter: " + counter + "\nByte: " + data);
                        lastTime = System.currentTimeMillis();

                        counter++;
                    }
                } else if (actualSpeed == 1.0f) {
                    if (System.currentTimeMillis() - lastTime >= 2) {
                        out.writeUTF("\nCounter: " + counter + "\nByte: " + data);
                        lastTime = System.currentTimeMillis();

                        counter++;
                    }
                }
                serverSocket.close();
            }
        } catch (IOException ioe) {
            ioe.printStackTrace();
        }
    }

    public void closeSocket() throws IOException {
        this.serverSocket.close();
        this.clientSocket.close();
    }
}
