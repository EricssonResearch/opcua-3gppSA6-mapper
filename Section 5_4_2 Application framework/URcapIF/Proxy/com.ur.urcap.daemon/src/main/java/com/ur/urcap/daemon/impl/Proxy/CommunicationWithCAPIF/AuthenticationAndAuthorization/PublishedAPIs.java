package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization;

import javax.net.ssl.*;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.KeyStore;

public class PublishedAPIs implements CommandOfCAPIF
{
    private String ID;

    public PublishedAPIs(String IDParam)
    {
        this. ID = IDParam;
    }

    @Override
    public void doOperation() throws Exception
    {
        String apiUrl = "https://capifcore/published-apis/v1/" + this.ID + "/service-apis";

        FileInputStream certFIS = new FileInputStream("exposer.pfx");

        String json = "{\n  \"apiName\": \"3gpp-monitoring-event\",\n  \"aefProfiles\": [\n    {\n      \"aefId\": \"string\",\n      \"versions\": [\n        {\n          \"apiVersion\": \"v1\",\n          \"expiry\": \"2024-11-30T10:32:02.004Z\",\n          \"resources\": [\n            {\n              \"resourceName\": \"string\",\n              \"commType\": \"REQUEST_RESPONSE\",\n              \"uri\": \"string\",\n              \"custOpName\": \"string\",\n              \"operations\": [\n                \"GET\"\n              ],\n              \"description\": \"string\"\n            }\n          ],\n          \"custOperations\": [\n            {\n              \"commType\": \"REQUEST_RESPONSE\",\n              \"custOpName\": \"string\",\n              \"operations\": [\n                \"GET\"\n              ],\n              \"description\": \"string\"\n            }\n          ]\n        }\n      ],\n      \"protocol\": \"HTTP_1_1\",\n      \"dataFormat\": \"JSON\",\n      \"securityMethods\": [\"PSK\"],\n      \"interfaceDescriptions\": [\n        {\n          \"ipv4Addr\": \"string\",\n          \"port\": 65535,\n          \"securityMethods\": [\"PSK\"]\n        },\n        {\n          \"ipv4Addr\": \"string\",\n          \"port\": 65535,\n          \"securityMethods\": [\"PSK\"]\n        }\n      ]\n    }\n  ],\n  \"description\": \"string\",\n  \"supportedFeatures\": \"fffff\",\n  \"shareableInfo\": {\n    \"isShareable\": true,\n    \"capifProvDoms\": [\n      \"string\"\n    ]\n  },\n  \"serviceAPICategory\": \"string\",\n  \"apiSuppFeats\": \"fffff\",\n  \"pubApiPath\": {\n    \"ccfIds\": [\n      \"string\"\n    ]\n  },\n  \"ccfId\": \"string\"\n}";
        FileInputStream caCertInputStream = new FileInputStream("ca.jks");

        HttpsURLConnection connection = null;
        try {
            KeyStore keyStore = KeyStore.getInstance("PKCS12");
            keyStore.load(certFIS, "password".toCharArray());
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStore, "password".toCharArray());

            KeyStore trustStore = KeyStore.getInstance("JKS");
            trustStore.load(caCertInputStream, "jksjks".toCharArray());
            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);

            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(keyManagerFactory.getKeyManagers(), trustManagerFactory.getTrustManagers(), null);

            SSLContext.setDefault(sslContext);

            HostnameVerifier allHostsValid = new HostnameVerifier() {
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            };
            HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);

            connection = (HttpsURLConnection) new URL(apiUrl).openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setSSLSocketFactory(sslContext.getSocketFactory());

            connection.setDoOutput(true);

            connection.getOutputStream().write(json.getBytes());
            connection.getOutputStream().close();
            BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream(), "ISO-8859-1"));
            StringBuilder responsebody = new StringBuilder();
            String respLine = null;

            while ((respLine = br.readLine()) != null)
            {
                responsebody.append(respLine.trim());
            }
        }
        catch (IOException e) {
            try
            {
                BufferedReader br = new BufferedReader(new InputStreamReader(((HttpURLConnection) connection).getErrorStream()));
                String line;
                StringBuilder response = new StringBuilder();
                while ((line = br.readLine()) != null) {
                    response.append(line);
                }
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        }
        finally
        {
            if (connection != null)
            {
                connection.disconnect();
            }
        }
        certFIS.close();
    }
}
