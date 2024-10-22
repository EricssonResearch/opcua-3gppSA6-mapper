import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Random;

public class SpeedSenderServer {
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
            float data = 0.1f;

            while (true) {
                float rand = random.nextInt(10);
                
                if (rand % 10 == 0)
                {
                    if (data == 1.0f)
                    {
                        data = 0.1f;
                    }
                    else if (data == 0.1f)
                    {
                        data = 1.0f;
                    }
                }

                out.writeFloat(data);
                System.out.println("Sent: " + data);
                Thread.sleep(1000);
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
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
