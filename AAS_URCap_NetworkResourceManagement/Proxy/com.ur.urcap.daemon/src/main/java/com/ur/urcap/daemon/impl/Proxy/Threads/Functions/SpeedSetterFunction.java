package com.ur.urcap.daemon.impl.Proxy.Threads.Functions;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsString;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.getLocalIPAddress;


public class SpeedSetterFunction extends ThreadFunction {
    private final String aasServersIpAddress = "AASServerIP"; //yourHostsIpAddress

    private String assSpeedPercentageUrl;

    private final String numberIdFilePath = "/home/ur/ursim-current/.urcaps/NumberID.txt";

    private String numberId;

    private float lastActualSpeed = actualSpeed;

    @Override
    public void setActualSpeed(float actualSpeedParam) {
        actualSpeed = actualSpeedParam;
    }

    public SpeedSetterFunction() {
        this.numberId = new ReadFileAsString().execute(this.numberIdFilePath).replace("\n", "");
        this.assSpeedPercentageUrl = "http://" + this.aasServersIpAddress + ":4001/aasServer/shells/eclipse.basyx.aas.robot"
                + this.numberId + "/aas/submodels/robotDynamic" + this.numberId + "/submodel/submodelElements/robotSpeedPercentage"
                + this.numberId + "/value";
    }

    @Override
    public void doOperation() {
        while (true) {
            if (this.lastActualSpeed != actualSpeed) {
                //Set the speed data of the robot in it's aas
                sendSpeedToRobotsController();

                System.out.println("Actual speed:   " + actualSpeed + "\nlastActualSpeed:   " + this.lastActualSpeed);
                this.lastActualSpeed = actualSpeed;
            } else {
                //Sleep the thread. the loop needs an else, because without it, it doesn't work. Furthermore, it is more power efficient.
                try {
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }

    private void sendSpeedToRobotsController() {
        try {
            Socket socket = new Socket(new getLocalIPAddress().getLocalIP(), 30003);
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            //Send Speed Data to the UR Controller!
            out.println("set speed " + actualSpeed);

            out.close();
            socket.close();
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }

    public void closeSocket() throws IOException {

    }
}
