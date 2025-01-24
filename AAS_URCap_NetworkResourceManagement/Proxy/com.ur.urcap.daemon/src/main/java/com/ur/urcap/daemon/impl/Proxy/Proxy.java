package com.ur.urcap.daemon.impl.Proxy;

import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions.ApiPutFunction;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsString;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsStringWithScanner;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.io.IOException;

import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.Registration;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.getLocalIPAddress;
import com.ur.urcap.daemon.impl.Proxy.Threads.ThreadForTCPCommunication;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.FilterDropSenderFunction;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.SpeedSetterFunction;
import com.ur.urcap.daemon.impl.Proxy.Threads.Functions.URControllerByteReceiverFunction;

public class Proxy {
    private final int clientPort = 9001;
    private final String urControllersAddress;
    private final int urControllersPort = 30013;
    private float speedData;
    private String clientId;
    private String assSpeedPercentageUrl;
    private final String aasServersIpAddress = "AASServerIP"; //yourHostsIpAddress
    private String numberId;

    private ThreadForTCPCommunication urcbrf;
    private ThreadForTCPCommunication sfrf;
    private ThreadForTCPCommunication fdsf;
    private Thread mqttThread;
    private Thread aasPropertySpeedSetter;

    public Proxy() {
        getLocalIPAddress glia = new getLocalIPAddress();
        glia.getLocalIP();
        this.urControllersAddress = glia.getLocalIP();

        try {
            new Registration().execute();
        } catch (Exception e) {
            e.printStackTrace();
        }

        this.numberId = new ReadFileAsString().execute("/home/ur/ursim-current/.urcaps/NumberID.txt").replace("\n", "");
        this.clientId = "Robot".concat(this.numberId);

        this.urcbrf = new ThreadForTCPCommunication(new URControllerByteReceiverFunction(urControllersAddress, urControllersPort));
        this.sfrf = new ThreadForTCPCommunication(new SpeedSetterFunction());
        this.fdsf = new ThreadForTCPCommunication(new FilterDropSenderFunction(clientPort));
        
        this.assSpeedPercentageUrl = "http://" + this.aasServersIpAddress + ":4001/aasServer/shells/eclipse.basyx.aas.robot"
                + this.numberId + "/aas/submodels/robotDynamic" + this.numberId + "/submodel/submodelElements/robotSpeedPercentage"
                + this.numberId;

        initAasCommunications();
    }

    public void startAllServicesOfTcpCommunication() {
        this.urcbrf = new ThreadForTCPCommunication(new URControllerByteReceiverFunction(urControllersAddress, urControllersPort));
        this.sfrf = new ThreadForTCPCommunication(new SpeedSetterFunction());
        this.fdsf = new ThreadForTCPCommunication(new FilterDropSenderFunction(clientPort));

        initAasCommunications();

        this.urcbrf.start();
        this.sfrf.start();
        this.fdsf.start();
        this.mqttThread.start();

        this.aasPropertySpeedSetter = new Thread(() -> {
            while (true) {
                String json = new ReadFileAsStringWithScanner().execute("/JSONs/AasServersJSONs/submodelElementSpeedPercentage.json").replace("HereComesTheNumberID", this.numberId).replace("\"value\": 0.0,", "\"value\": " + this.speedData + ",").replace("\"value\": 1.0,", "\"value\": " + this.speedData + ",").replace("\"value\": 0.1,", "\"value\": " + this.speedData + ",");
                new ApiPutFunction().execute(this.assSpeedPercentageUrl, json, "DATA", this.numberId);
                }
        });

        this.aasPropertySpeedSetter.start();
    }

    public void stopAllServicesOfTcpCommunication() {
        this.urcbrf.interrupt();
        this.sfrf.interrupt();
        this.fdsf.interrupt();
        this.mqttThread.interrupt();
        this.aasPropertySpeedSetter.interrupt();
    }

    private void initAasCommunications() {
        this.mqttThread = new Thread(() -> {
            try {
                System.out.println("This is it:   " + this.clientId);
                MqttClient client = new MqttClient("tcp://BrokerIP:1883", this.clientId);  //yourHostsIpAddress
                MqttConnectOptions connOpts = new MqttConnectOptions();
                connOpts.setCleanSession(true);
                client.connect(connOpts);

                // Subscribe to the topic
                client.subscribe("network/bandwidth", new IMqttMessageListener() {
                    @Override
                    public void messageArrived(String topic, MqttMessage message) throws Exception {
                        speedData = Float.valueOf(new String(message.getPayload()));
                        sfrf.setActualSpeed(speedData);
                    }
                });

                // Keep the client running until you press Ctrl+C
                System.in.read();

            } catch (IOException | MqttException e) {
                throw new RuntimeException(e);
            }
        });
    }
}
