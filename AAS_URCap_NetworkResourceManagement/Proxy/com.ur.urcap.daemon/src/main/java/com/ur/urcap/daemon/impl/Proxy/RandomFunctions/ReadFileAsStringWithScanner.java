package com.ur.urcap.daemon.impl.Proxy.RandomFunctions;

import java.io.InputStream;
import java.util.Scanner;

public class ReadFileAsStringWithScanner {
    public String execute(String fileNameAndPathInResources) {
        String fileAsString = "";

        try {
            InputStream is = getClass().getResourceAsStream(fileNameAndPathInResources);
            assert is != null;
            Scanner scanner = new Scanner(is);
            scanner.useDelimiter("\\R");

            StringBuilder fileContent = new StringBuilder();
            while (scanner.hasNext()) {
                fileContent.append(scanner.next()).append("\n");
            }

            fileAsString = fileContent.toString();
        } catch (Exception e) {
            e.printStackTrace();
        }

        return fileAsString;
    }
}
