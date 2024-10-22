package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization;

import java.net.MalformedURLException;
import java.net.URL;

import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions.GetResponseBodyForAccessTokenAndID;

public class GettingAccessToken implements CommandOfCAPIF
{

    private String jsonsData;
    private URL url;
    private final String responseTypeJsonID = "\"access_token\": \"";
    private String accessToken;

    public GettingAccessToken() throws MalformedURLException
    {
        this.jsonsData = "{\"username\":\"exposer\",\"password\":\"exposer\",\"role\":\"provider\"}";
        this.url = new URL("http://capifcore:8080/getauth");
    }

    public String getAccessToken()
    {
        return this.accessToken;
    }

    @Override
    public void doOperation() throws Exception
    {
        GetResponseBodyForAccessTokenAndID grbfati = new GetResponseBodyForAccessTokenAndID(this.url);
        grbfati.doOperation(this.jsonsData);

        StringBuilder responseBody = new StringBuilder(grbfati.getResponseBody());

        StringBuilder responseDataString = new StringBuilder();

        if(responseBody.toString().contains(this.responseTypeJsonID))
        {
            int startIndexOfCode = responseBody.indexOf(this.responseTypeJsonID) + this.responseTypeJsonID.length();

            for(int i = startIndexOfCode; responseBody.charAt(i) != '\"'; i++)
            {
                responseDataString.append(responseBody.charAt(i));
            }

            this.accessToken = responseDataString.toString();
        }
    }
}
