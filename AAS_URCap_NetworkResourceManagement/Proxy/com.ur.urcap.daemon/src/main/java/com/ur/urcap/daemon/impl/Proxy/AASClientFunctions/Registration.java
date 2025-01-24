package com.ur.urcap.daemon.impl.Proxy.AASClientFunctions;

import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions.ApiGetFunction;
import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions.ApiPutFunction;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsString;

import java.io.*;

public class Registration {
    private String basicRobotAASID = "eclipse.basyx.aas.robot";
    private String basicRobotAssetID = "eclipse.basyx.asset.robot";

    private String basicRobotDynamicSMID = "eclipse.basyx.submodel.robotDynamic";
    private String basicRobotStaticSMID = "eclipse.basyx.submodel.robotStatic";
    private String basicRobotDynamicSMIDShort = "robotDynamic";
    private String basicRobotStaticSMIDShort = "robotStatic";

    private String basicRobotNetworkLatencyIDShort = "robotNetworkLatency";
    private String basicRobotNetworkBandwidthIDShort = "robotNetworkBandwidth";
    private String basicRobotSpeedPercentageIDShort = "robotSpeedPercentage";

    private final String directoryPath = "/DataFiles";
    private final String fileName = "NumberID.txt";
    private final String textForCounter = "AssetAdministrationShellDescriptor";

    private String numberId = "";

    //AAS registration attributes
    private final String aasRegistryUrlBasic = "http://AASRegistryIP:4000/registry/api/v1/registry"; //yourHostsIpAddress
    private final String aasServerUrlBasic = "http://AASServerIP:4001/aasServer/shells"; //yourHostsIpAddress

    private final String aasRegistryServerJsonPath = "/JSONs/RegistryServersJSONs/aas.json";
    private final String submodelDynamicRegistryServerJsonPath = "/JSONs/RegistryServersJSONs/submodelDynamic.json";
    private final String submodelStaticRegistryServerJsonPath = "/JSONs/RegistryServersJSONs/submodelStatic.json";

    //AAS Server
    private final String aasAasServerJsonPath = "/JSONs/AasServersJSONs/aas.json";
    private final String submodelDynamicAasServerJsonPath = "/JSONs/AasServersJSONs/submodelDynamic.json";
    private final String submodelStaticAasServerJsonPath = "/JSONs/AasServersJSONs/submodelStatic.json";
    private final String submodelElementLatencyAasServerJsonPath = "/JSONs/AasServersJSONs/submodelElementNetworkLatency.json";
    private final String submodelElementBandwidthAasServerJsonPath = "/JSONs/AasServersJSONs/submodelElementNetworkBandwidth.json";
    private final String submodelElementSpeedAasServerJsonPath = "/JSONs/AasServersJSONs/submodelElementSpeedPercentage.json";

    public void execute() throws Exception {
        String pathWithFileName = "/home/ur/ursim-current/.urcaps/" + this.fileName;

        if (!(new ReadFileAsString().execute(pathWithFileName).contains("HereComesTheNumberID"))) {
            this.numberId = new ReadFileAsString().execute(pathWithFileName).replace("\n", "");
        } else {
            generateNumberId(pathWithFileName);
            init_Ids();

            //Register aas & submodels to the registry server.
            new ApiPutFunction().execute(this.aasRegistryUrlBasic + "/" + this.basicRobotAASID, this.aasRegistryServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasRegistryUrlBasic + "/" + this.basicRobotAASID + "/submodels/" + this.basicRobotDynamicSMID, this.submodelDynamicRegistryServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasRegistryUrlBasic + "/" + this.basicRobotAASID + "/submodels/" + this.basicRobotStaticSMID, this.submodelStaticRegistryServerJsonPath, "JSONPATH", numberId);

            //Register aas & submodels & properties to the AAS Server.
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID, this.aasAasServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID + "/aas/submodels/" + this.basicRobotDynamicSMIDShort, this.submodelDynamicAasServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID + "/aas/submodels/" + this.basicRobotStaticSMIDShort, this.submodelStaticAasServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID + "/aas/submodels/" + this.basicRobotDynamicSMIDShort + "/submodel/submodelElements/" + this.basicRobotNetworkLatencyIDShort, this.submodelElementLatencyAasServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID + "/aas/submodels/" + this.basicRobotDynamicSMIDShort + "/submodel/submodelElements/" + this.basicRobotNetworkBandwidthIDShort, this.submodelElementBandwidthAasServerJsonPath, "JSONPATH", numberId);
            new ApiPutFunction().execute(this.aasServerUrlBasic + "/" + this.basicRobotAASID + "/aas/submodels/" + this.basicRobotDynamicSMIDShort + "/submodel/submodelElements/" + this.basicRobotSpeedPercentageIDShort, this.submodelElementSpeedAasServerJsonPath, "JSONPATH", numberId);
        }
    }

    private void init_Ids() {
        this.basicRobotAASID = this.basicRobotAASID + this.numberId;
        this.basicRobotAssetID = this.basicRobotAssetID + this.numberId;

        this.basicRobotDynamicSMID = this.basicRobotDynamicSMID + this.numberId;
        this.basicRobotStaticSMID = this.basicRobotStaticSMID + this.numberId;
        this.basicRobotDynamicSMIDShort = this.basicRobotDynamicSMIDShort + this.numberId;
        this.basicRobotStaticSMIDShort = this.basicRobotStaticSMIDShort + this.numberId;

        this.basicRobotNetworkLatencyIDShort = this.basicRobotNetworkLatencyIDShort + this.numberId;
        this.basicRobotNetworkBandwidthIDShort = this.basicRobotNetworkBandwidthIDShort + this.numberId;
        this.basicRobotSpeedPercentageIDShort = this.basicRobotSpeedPercentageIDShort + this.numberId;

    }

    private void generateNumberId(String pathWithFileName) throws Exception {
        //Create numberId.
        long count = countOccurrences(new ApiGetFunction().execute(this.aasRegistryUrlBasic), this.textForCounter);
        this.numberId = String.valueOf(count);
        
        // Write numberId into file.
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(pathWithFileName, false));
            writer.write(this.numberId);
            writer.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private int countOccurrences(String text, String searchText) {
        if (text == null || searchText == null || searchText.isEmpty()) {
            return 0;
        }

        int count = 0;
        int index = 0;

        while ((index = text.indexOf(searchText, index)) != -1) {
            count++;
            index += searchText.length();
        }

        return count;
    }
}
