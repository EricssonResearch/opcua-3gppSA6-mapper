package com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class ApiGetFunction
{
    public String execute(String urlParam)
    {
        try
        {
            URL url = new URL(urlParam);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            int responseCode = connection.getResponseCode();

            if(responseCode == HttpURLConnection.HTTP_OK)
            {
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String inputLine;
                StringBuilder response = new StringBuilder();

                while ((inputLine = in.readLine()) != null)
                {
                    response.append(inputLine);
                }
                in.close();

                return response.toString();
            }
            else
            {
                System.out.println("GET request not worked... " + responseCode);
                return "";
            }
        }
        catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
