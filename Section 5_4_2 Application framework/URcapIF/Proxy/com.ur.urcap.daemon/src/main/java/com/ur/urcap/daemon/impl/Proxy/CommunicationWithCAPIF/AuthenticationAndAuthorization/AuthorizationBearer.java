package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.AuthenticationAndAuthorization;

import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions.CleanAuthorizationResponse;
import com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions.ExportToPfxFormat;

public class AuthorizationBearer implements CommandOfCAPIF
{
    private String accessToken;
    public AuthorizationBearer(String accessTokenParam)
    {
        this.accessToken = accessTokenParam;
    }
    @Override
    public void doOperation() throws Exception
    {
        URL url = new URL("http://capifcore:8080/sign-csr");
        HttpURLConnection httpConn = (HttpURLConnection) url.openConnection();
        httpConn.setRequestMethod("POST");

        httpConn.setRequestProperty("AuthorizationBearer", "Bearer " + this.accessToken);
        httpConn.setRequestProperty("Content-Type", "application/json");

        httpConn.setDoOutput(true);
        OutputStreamWriter writer = new OutputStreamWriter(httpConn.getOutputStream());
        writer.write("{\n  \"csr\":  \"-----BEGIN CERTIFICATE REQUEST-----\\nMIIC0TCCAbkCAQAwgYsxEDAOBgNVBAMMB2V4cG9zZXIxFzAVBgNVBAoMDlRlbGVm\\nb25pY2EgSStEMRMwEQYDVQQLDApJbm5vdmF0aW9uMQ8wDQYDVQQHDAZNYWRyaWQx\\nDzANBgNVBAgMBk1hZHJpZDELMAkGA1UEBhMCRVMxGjAYBgkqhkiG9w0BCQEWC2lu\\nbm9AdGlkLmVzMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkpJ7FzAI\\nkzFYxLKbW54lIsQBNIQz5zQIvRZDFcrO4QLR2jQUps9giBWEDih++47JiBJyM+z1\\nWkEh7b+moZhQThj7L9PKgJHRhU1oeHpSE1x/r7479J5F+CFRqFo5v9dC+2zGfP4E\\nsSrNfp3MK/KQHsHhMzSt881xAHs+p2/bcM+sd/BlXC4J6E1y6Hk3ogI7kq443fcY\\noUHZx9ClUSboOvXa1ZSPVxdCV6xKRraUdAKfhMGn+pYtJDsNp8Gg/BN8NXmYUzl9\\ntDhjeuIxr4N38LgW3gRHLNIa8acO9eBctWw9AD20JWzFAXvvmsboBPc2wsOVcsml\\ncCbisMRKX4JyKQIDAQABoAAwDQYJKoZIhvcNAQELBQADggEBAIxZ1Sec9ATbqjhi\\nRz4rvhX8+myXhyfEw2MQ62jz5tpH4qIVZFtn+cZvU/ULySY10WHaBijGgx8fTaMh\\nvjQbc+p3PXmgtnmt1QmoOGjDTFa6vghqpxPLSUjjCUe8yj5y24gkOImY6Cv5rzzQ\\nlnTMkNvnGgpDgUeiqWcQNbwwge3zkzp9bVRgogTT+EDxiFnjTTF6iUG80sRtXMGr\\nD6sygLsF2zijGGfWoKRo/7aZTQxuCiCixceVFXegMfr+eACkOjV25Kso7hYBoEdP\\nkgUf5PNpl5uK3/rmPIrl/TeE0SnGGfCYP7QajE9ELRsBVmVDZJb7ZxUl1A4YydFY\\ni0QOM3Y=\\n-----END CERTIFICATE REQUEST-----\\n\",\n  \"mode\":  \"client\",\n  \"filename\": \"exposer\"\n}");
        writer.flush();
        writer.close();
        httpConn.getOutputStream().close();

        InputStream responseStream = httpConn.getResponseCode() / 100 == 2
                ? httpConn.getInputStream()
                : httpConn.getErrorStream();
        Scanner s = new Scanner(responseStream).useDelimiter("\\A");
        String response = s.hasNext() ? s.next() : "";

        CleanAuthorizationResponse car = new CleanAuthorizationResponse();
        car.doOperation(response);

        ExportToPfxFormat etpf = new ExportToPfxFormat();
        etpf.doOperation(car.getOnlyTheCertificate());

        s.close();
    }
}
