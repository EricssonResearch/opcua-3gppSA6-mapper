package AASServer;

import org.eclipse.basyx.aas.manager.ConnectedAssetAdministrationShellManager;
import org.eclipse.basyx.aas.metamodel.api.parts.asset.AssetKind;
import org.eclipse.basyx.aas.metamodel.map.AssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.descriptor.CustomId;
import org.eclipse.basyx.aas.metamodel.map.parts.Asset;
import org.eclipse.basyx.aas.registration.proxy.AASRegistryProxy;
import org.eclipse.basyx.components.aas.AASServerComponent;
import org.eclipse.basyx.components.aas.configuration.AASServerBackend;
import org.eclipse.basyx.components.aas.configuration.BaSyxAASServerConfiguration;
import org.eclipse.basyx.components.configuration.BaSyxContextConfiguration;
import org.eclipse.basyx.components.registry.RegistryComponent;
import org.eclipse.basyx.components.registry.configuration.BaSyxRegistryConfiguration;
import org.eclipse.basyx.components.registry.configuration.RegistryBackend;
import org.eclipse.basyx.submodel.metamodel.api.identifier.IIdentifier;
import org.eclipse.basyx.submodel.metamodel.map.Submodel;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.paho.client.mqttv3.*;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;

public class AASServer {
    public static final String REGISTRYPATH = "http://0.0.0.0:4000/registry";
    public static final String AASSERVERPATH = "http://0.0.0.0:4001/aasServer";

    public static final ConnectedAssetAdministrationShellManager manager = new ConnectedAssetAdministrationShellManager(new AASRegistryProxy(REGISTRYPATH));

    //Network AAS's Components
    public static final IIdentifier NETWORKAASID = new CustomId("eclipse.basyx.aas.network");
    public static final IIdentifier NETWORKASSETID = new CustomId("eclipse.basyx.asset.network");
    public static final IIdentifier NETWORKDYNAMICSMID = new CustomId("eclipse.basyx.submodel.networkDynamic");

    //NetworkBandwidthSenderServer's data
    private static final String networkBandwidthSenderServersAddress = "127.0.0.1"; //yourHostsIpAddress
    private static final int networkBandwidthSenderServersPort = 9000;

    //Services
    private static Thread networkBandwidthClientService;
    private static Thread mqttSpeedPublisherService;

    private static int networkBandwidthValue = 1000;
    private static int networkLatencyValue = 100;

    //MQTT
    private static final String BROKER_URL = "tcp://BrokerIP:1883"; //yourHostsIpAddress
    private static final String TOPICBANDWIDTH = "network/bandwidth";
    private static final String TOPICLATENCY = "network/latency";

    //Thread synchronization
    private static final AtomicInteger isItPublishable = new AtomicInteger(0);

    public static void main(String[] args) {
        startRegistry();
        startAASServer();

        createNetworkAAS();

        createNetworkBandwidthClientService();
        createMqttSpeedPublisherService();

        networkBandwidthClientService.start();
        mqttSpeedPublisherService.start();
    }

    private static void createNetworkAAS() {
        Property networkNetworkBandwidth = new Property("networkNetworkBandwidth", 1000);
        Property networkNetworkLatency = new Property("networkNetworkLatency", 0);
        Property p = new Property();
        p.setValue(1);
        Asset networkAsset = new Asset("networkAsset", NETWORKASSETID, AssetKind.INSTANCE);
        AssetAdministrationShell networkAAS = new AssetAdministrationShell("network", NETWORKAASID, networkAsset);

        Submodel networkDynamicSM = new Submodel("networkDynamic", NETWORKDYNAMICSMID);

        networkDynamicSM.addSubmodelElement(networkNetworkBandwidth);
        networkDynamicSM.addSubmodelElement(networkNetworkLatency);

        manager.createAAS(networkAAS, AASSERVERPATH);

        manager.createSubmodel(networkAAS.getIdentification(), networkDynamicSM);
    }

    private static void createNetworkBandwidthClientService() {
        networkBandwidthClientService = new Thread(() -> {
            try {
                Socket socket = new Socket(networkBandwidthSenderServersAddress, networkBandwidthSenderServersPort);
                InputStream inputStream = socket.getInputStream();
                //TODO: Create AAS / Asset / Submodel / Properties for Network

                if (inputStream != null) {
                    DataInputStream dataInputStream = new DataInputStream(inputStream);
                    while (true) {
                        networkBandwidthValue = dataInputStream.readInt();
                        System.out.println(networkBandwidthValue);
                        manager.retrieveSubmodel(NETWORKAASID, NETWORKDYNAMICSMID).getSubmodelElement("networkNetworkBandwidth").setValue(networkBandwidthValue);

                        isItPublishable.set(1);
                        Thread.sleep(100);
                    }
                }
            } catch (IOException | InterruptedException e) {
                throw new RuntimeException(e);
            }
        });
    }

    private static void createMqttSpeedPublisherService() {
        mqttSpeedPublisherService = new Thread(() -> {
            try {
                MqttClient client = new MqttClient(BROKER_URL, "Publisher");
                MqttConnectOptions connOpts = new MqttConnectOptions();
                connOpts.setCleanSession(true);
                client.connect(connOpts);

                while (true) {
                    if (isItPublishable.get() == 1) {
                        MqttMessage messageOfSpeedValue = new MqttMessage(Float.toString((float) networkBandwidthValue / 1000).getBytes(StandardCharsets.UTF_8));
                        client.publish(TOPICBANDWIDTH, messageOfSpeedValue);

                        isItPublishable.set(0);
                    }
                }
            } catch (MqttException e) {
                throw new RuntimeException(e);
            }
        });
    }

    /**
     * Starts an empty registry at "http://localhost:4000"
     */
    private static void startRegistry() {
        BaSyxContextConfiguration contextConfig = new BaSyxContextConfiguration(4000, "/registry");
        BaSyxRegistryConfiguration registryConfig = new BaSyxRegistryConfiguration(RegistryBackend.MONGODB);
        RegistryComponent registry = new RegistryComponent(contextConfig, registryConfig);
        // Start the created server
        registry.startComponent();
    }

    /**
     * Startup an empty server at "http://localhost:4001/"
     */
    private static void startAASServer() {
        BaSyxContextConfiguration contextConfig = new BaSyxContextConfiguration(4001, "/aasServer");
        BaSyxAASServerConfiguration aasServerConfig = new BaSyxAASServerConfiguration(AASServerBackend.MONGODB, "", REGISTRYPATH);
        AASServerComponent aasServer = new AASServerComponent(contextConfig, aasServerConfig);
        // Start the created server
        aasServer.startComponent();
    }
}
