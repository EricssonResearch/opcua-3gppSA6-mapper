package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization;

import java.net.MalformedURLException;
import java.net.URL;

import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions.GetResponseBodyForAccessTokenAndID;

public class RegistrationWithID implements CommandOfCAPIF{

    private String jsonsData;
    private URL url;
    private final String responseTypeJsonID = "\"id\": \"";
    private String ID;

    public RegistrationWithID() throws MalformedURLException
    {
        this.jsonsData = "{\"username\":\"exposer\",\"password\":\"exposer\",\"role\":\"provider\",\"description\":\"Exposer\",\"cn\":\"exposer\"}";
        this.url = new URL("http://capifcore:8080/register");
    }

    public String getID()
    {
        return this.ID;
    }

    @Override
    public void doOperation() throws Exception {
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

            this.ID = responseDataString.toString();
        }
    }
}
