import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Random;

public class NetworkBandwidthSenderServer {
    public static void main(String[] args) {
        ServerSocket serverSocket = null;
        Socket clientSocket = null;
        DataOutputStream out = null;

        try {
            serverSocket = new ServerSocket(9000);
            System.out.println("Server is looking for client on port 9000...");

            clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getInetAddress());

            out = new DataOutputStream(clientSocket.getOutputStream());

            Random random = new Random();
            int data = 100;

            while (true) {
                int rand = random.nextInt(10);
                
                if (rand % 5 == 0)
                {
                    if (data == 1000)
                    {
                        data = 100;
                    }
                    else if (data == 100)
                    {
                        data = 1000;
                    }
                }

                out.writeInt(data);
                System.out.println("Sent: " + data);
                Thread.sleep(1000);
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                if (out != null) out.close();
                if (clientSocket != null) clientSocket.close();
                if (serverSocket != null) serverSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
