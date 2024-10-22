package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class GetResponseBodyForAccessTokenAndID implements FunctionForCAPIF
{

    private String responseBody;
    private URL url;

    public String getResponseBody()
    {
        return this.responseBody;
    }

    public GetResponseBodyForAccessTokenAndID(URL URLParam)
    {
        this.url = URLParam;
    }

    @Override
    public void doOperation(String jsonsDataParam)
    {
        try {
            HttpURLConnection connection = (HttpURLConnection) this.url.openConnection();

            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setDoOutput(true);


            OutputStream os = connection.getOutputStream();
            byte[] input = jsonsDataParam.getBytes("ISO-8859-1");
            os.write(input, 0, input.length);


            BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream(), "ISO-8859-1"));
            StringBuilder responseBody = new StringBuilder();
            String responseLine = null;

            while ((responseLine = br.readLine()) != null) {
                responseBody.append(responseLine.trim());
            }
            this.responseBody = String.valueOf(responseBody);
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
    }
}
