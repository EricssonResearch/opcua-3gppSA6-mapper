package com.ur.urcap.daemon.impl.Proxy.CommunicationWithCAPIF.Functions;

import java.io.ByteArrayInputStream;
import java.io.FileOutputStream;
import java.security.KeyFactory;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.spec.PKCS8EncodedKeySpec;

import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.CustomBase64Decoder;

public class ExportToPfxFormat implements FunctionForCAPIF
{
    @Override
    public void doOperation(String certificationStringParam){
        String key = "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCSknsXMAiTMVjE\n" + //
                     "sptbniUixAE0hDPnNAi9FkMVys7hAtHaNBSmz2CIFYQOKH77jsmIEnIz7PVaQSHt\n" + //
                     "v6ahmFBOGPsv08qAkdGFTWh4elITXH+vvjv0nkX4IVGoWjm/10L7bMZ8/gSxKs1+\n" + //
                     "ncwr8pAeweEzNK3zzXEAez6nb9twz6x38GVcLgnoTXLoeTeiAjuSrjjd9xihQdnH\n" + //
                     "0KVRJug69drVlI9XF0JXrEpGtpR0Ap+Ewaf6li0kOw2nwaD8E3w1eZhTOX20OGN6\n" + //
                     "4jGvg3fwuBbeBEcs0hrxpw714Fy1bD0APbQlbMUBe++axugE9zbCw5VyyaVwJuKw\n" + //
                     "xEpfgnIpAgMBAAECggEACs11TqlcIG5qd/N1Ts8ni9noACpe4ZiXV578lRkW8++E\n" + //
                     "xEZtX+P4iIm+wK+3DYGhvyp430naGsD30rF62FMaVr8xmCijC/nIoutTGqS38t8G\n" + //
                     "Ns+C/2Lrjj+fvemJyGasSaKOjdIc9L/OWG7MiE/+05LU2bTKvfrIwXvT4NGg2ei1\n" + //
                     "NDO8vS5fRHYZ1LyCyrCDetP2aYrTlPao20hmU4IDyh4N17wLuPgijC+AuqR2Xic0\n" + //
                     "Mk4ofZ/6Y3oN0rrov2yG7IXjMJQI469IQ6TJLlyFc8tQIF5Y3CMMCMuVMq5m33bq\n" + //
                     "/6bow4/VYFG8mPzy7lQLQ8YeEPsgDKL0pB4zqDr7ZwKBgQDJRJoG2PSaEOt6DIKV\n" + //
                     "84to73oD9x9lOSrmaH2/NzL3mwLXP2Is4nmLzEDQvA0UhTZe9c0n6OoE3uRZ1gAu\n" + //
                     "JIe3zXTJSK4/ysmePUZL1js5bKtuHBrcSCOupWRuJXbaXK5uqISDHUgHiRw3bq8y\n" + //
                     "g8SZY/JOBPyJhVlKhmhNCYMi9wKBgQC6bjJ//tLpH6EG4ux0O2StzUoHrvV2cyUj\n" + //
                     "RRxGvAt92sdsZaVKmIW/SlLy8tv5HJqblfn6m7aY/vUYbN3AfMJ4teLZz5Y//CH3\n" + //
                     "jPchHyk/uhh7gxufiD65i5bfVyRt54tDbyVDc2/1prUyD5W4q4UNOmvhXym5saIc\n" + //
                     "U5WNCnSr3wKBgQCs8MaM5bVgAPPlfoRixs9ejo/AgoK2nqWvL9AFEzA3NDn/rJX2\n" + //
                     "TW/1YL+83Ck9Ha33cKwlA+y53LBIRSsIexknJWKZZltbsysFTk9t8JoZILg5N+sY\n" + //
                     "puAKPFGMl6KFxSeZLDIY23s+BmF5fCEMfc7botbclUpN/IgaEl3i/C5zRwKBgHsx\n" + //
                     "lKdmEaNBZlwxmgTYtpfvH2tiXwwN3M2ovp2zZ3icGMn1hTt8/GzCxXuLpnbAQx5r\n" + //
                     "BcxoF0qUuAuS7RpklvHDZ4t9FJFloGCAQ1Ic0FovNDxyD8/k7WYY6vLdF9KUfj9q\n" + //
                     "c9pVrvdKWVQiXlKw7PQn1eAQzXbK/g/v39Raw2xLAoGBAILTLY3sGBNkFCVhJlyZ\n" + //
                     "DaIwkbtnpCBT2T7DUupw51aLhh4rnuJ5wA3uGdRqoKVYSc9DuOwB/yNFGuQDElxQ\n" + //
                     "jfKlX0X5xItaxZ5FR4EvGCnqBJl6JM3QekzhXtq5VdY5zIf/HHqFYebcMFrkEicZ\n" + //
                     "uuAZd4wa+jn9SR9mUYtS+Lq+";

        key = key.replaceAll("\\s+", "");
        byte[] privateKeyBytes = CustomBase64Decoder.decode(key);

        try {
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(privateKeyBytes);
            PrivateKey privateKey = keyFactory.generatePrivate(keySpec);

            certificationStringParam = certificationStringParam.replaceAll("\\s+", "");
            byte[] certificateBytes = CustomBase64Decoder.decode(certificationStringParam);
            CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
            X509Certificate certificate = (X509Certificate) certificateFactory.generateCertificate(new ByteArrayInputStream(certificateBytes));

            KeyStore keyStore = KeyStore.getInstance("PKCS12");

            keyStore.load(null, null);
            keyStore.setKeyEntry("alias", privateKey, "password".toCharArray(), new Certificate[]{certificate});

            FileOutputStream fos = new FileOutputStream("exposer.pfx");
            keyStore.store(fos, "password".toCharArray());

        }
        catch (Exception exception)
        {
            exception.printStackTrace();
        }
    }
}
