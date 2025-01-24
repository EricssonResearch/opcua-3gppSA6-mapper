package com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions;

import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsStringWithScanner;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class ApiPutFunction {
    public void execute(String urlParam, String value, String putParamSwitch, String numberId) {
        HttpURLConnection connection = null;
        OutputStream os = null;

        try {
            URL url = new URL(urlParam);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("PUT");
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json");

            os = connection.getOutputStream();

            byte[] input;
            if (putParamSwitch.equals("JSONPATH")) {
                input = readJsonFromFile(value, numberId).getBytes();
            } else if(putParamSwitch.equals("DATA")){
                input = value.getBytes();
            } else {
                input = "Problem with JSONPATH/DATA parameters!".getBytes();
            }

            os.write(input, 0, input.length);

            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("HTTP error code: " + responseCode);
            }
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        } finally {
            if (os != null) {
                try {
                    os.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private String readJsonFromFile(String filePath, String numberId) {
        String unreplacedContent = new ReadFileAsStringWithScanner().execute(filePath);
        String replacedContent = unreplacedContent.replace("HereComesTheNumberID", numberId);
        return replacedContent;
    }
}
