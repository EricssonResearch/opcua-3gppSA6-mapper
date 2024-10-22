package com.ur.urcap.daemon.impl.Proxy.RandomFunctions;

public class CustomBase64Decoder
{
    private static final String base64Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    public static byte[] decode(String input) {
        String digits = input.replaceAll("[^" + base64Chars + "=]", "");
        int length = digits.length();
        int numGroups = length / 4;
        if (4 * numGroups != length)
            throw new IllegalArgumentException(
                    "Length of Base64 encoded input string is not a multiple of 4.");

        int missingBytesInLastGroup = 0;
        int numFullGroups = numGroups;
        if (length != 0) {
            if (digits.charAt(length - 1) == '=') {
                missingBytesInLastGroup++;
                numFullGroups--;
            }
            if (digits.charAt(length - 2) == '=')
                missingBytesInLastGroup++;
        }

        byte[] bytes = new byte[3 * numGroups - missingBytesInLastGroup];
        int j = 0;
        for (int i = 0; i < numFullGroups; i++) {
            int digit1 = base64Chars.indexOf(digits.charAt(j++));
            int digit2 = base64Chars.indexOf(digits.charAt(j++));
            int digit3 = base64Chars.indexOf(digits.charAt(j++));
            int digit4 = base64Chars.indexOf(digits.charAt(j++));

            int decodedTriplet = ((digit1 << 18) + (digit2 << 12) + (digit3 << 6) + digit4);
            bytes[i * 3] = (byte) (decodedTriplet >> 16);
            bytes[i * 3 + 1] = (byte) (decodedTriplet >> 8);
            bytes[i * 3 + 2] = (byte) (decodedTriplet);
        }

        if (missingBytesInLastGroup != 0) {
            int digit1 = base64Chars.indexOf(digits.charAt(j++));
            int digit2 = base64Chars.indexOf(digits.charAt(j++));
            int decodedTriplet = ((digit1 << 18) + (digit2 << 12));

            bytes[numFullGroups * 3] = (byte) (decodedTriplet >> 16);
            if (missingBytesInLastGroup == 1) {
                int digit3 = base64Chars.indexOf(digits.charAt(j++));
                int decodedPair = ((digit2 << 6) + digit3);
                bytes[numFullGroups * 3 + 1] = (byte) (decodedPair >> 4);
            }
        }
        return bytes;
    }
}
