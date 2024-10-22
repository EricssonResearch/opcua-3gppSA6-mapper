import java.io.DataInputStream;
import java.io.IOException;
import java.net.Socket;

public class App {
    public static void main(String[] args)
    {
        String proxysAddress = "yourVMsIpAddress";
        int proxysPort = 9001;

        try
        {
            Socket socket = new Socket(proxysAddress, proxysPort);
            DataInputStream dataInputStream = new DataInputStream(socket.getInputStream());

            while (true)
            {
                try
                {
                    String receivedData = dataInputStream.readUTF();
                    System.out.println("Received data: " + receivedData);
                }
                catch (IOException e)
                {
                    System.err.println("Connection lost: " + e.getMessage());
                    break;
                }
            }

            socket.close();
        }
        catch (IOException e)
        {
            System.err.println("Unable to connect to the Proxy: " + e.getMessage());
        }
    }
}
