package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions;

public class CleanAuthorizationResponse implements FunctionForCAPIF
{
    private String onlyTheCertificate;

    public String getOnlyTheCertificate()
    {
        return this.onlyTheCertificate;
    }

    @Override
    public void doOperation(String responseParam)
    {
        String responseWhithoutN = new String();
        responseWhithoutN = responseParam.replace("\\n", "\n");
        responseWhithoutN = responseWhithoutN.replace("{\"certificate\": \"", "");
        responseWhithoutN = responseWhithoutN.replace("\"}", "");

        String onlyCertificate = new String();
        int theFirstIndex = responseWhithoutN.indexOf("-----BEGIN CERTIFICATE-----") + "-----BEGIN CERTIFICATE-----".length() + 1;
        int theLastIndex = responseWhithoutN.indexOf("-----END CERTIFICATE-----") - 1;

        for(int i = theFirstIndex; i < theLastIndex; i++)
        {
            onlyCertificate = onlyCertificate + responseWhithoutN.charAt(i);
        }

        this.onlyTheCertificate = onlyCertificate;
    }
}
