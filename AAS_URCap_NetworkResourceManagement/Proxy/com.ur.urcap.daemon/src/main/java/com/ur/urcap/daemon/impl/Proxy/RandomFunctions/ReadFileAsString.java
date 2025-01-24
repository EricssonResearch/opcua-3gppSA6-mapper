package com.ur.urcap.daemon.impl.Proxy.RandomFunctions;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ReadFileAsString {
    public String execute(String filePath) {
        try {
            InputStreamReader inputReader = new InputStreamReader(Files.newInputStream(Paths.get(filePath)));
            BufferedReader reader = new BufferedReader(inputReader);

            StringBuilder content = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }

            String fileContent = content.toString();

            reader.close();
            inputReader.close();

            return fileContent;
        } catch (IOException e) {
            e.printStackTrace();
        }

        return "";
    }
}
