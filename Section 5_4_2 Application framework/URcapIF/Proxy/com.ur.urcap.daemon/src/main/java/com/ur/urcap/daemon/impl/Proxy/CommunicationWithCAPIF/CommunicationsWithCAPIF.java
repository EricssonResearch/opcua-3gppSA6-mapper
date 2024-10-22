package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF;

import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization.AuthorizationBearer;
import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization.GettingAccessToken;
import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization.PublishedAPIs;
import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization.RegistrationWithID;


public class CommunicationsWithCAPIF
{
    private String ID;
    private String accessToken;

    public void authenticationAndAuthorization() throws Exception
    {
        RegistrationWithID rwi = new RegistrationWithID();
        rwi.doOperation();
        this.ID = rwi.getID();

        GettingAccessToken gat = new GettingAccessToken();
        gat.doOperation();
        this.accessToken = gat.getAccessToken();

        AuthorizationBearer ab = new AuthorizationBearer(this.accessToken);
        ab.doOperation();

        PublishedAPIs pa = new PublishedAPIs(this.ID);
        pa.doOperation();

    }
}
