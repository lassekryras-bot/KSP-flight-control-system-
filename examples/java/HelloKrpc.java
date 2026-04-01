import krpc.client.Connection;
import krpc.client.RPCException;
import krpc.client.services.SpaceCenter;
import krpc.client.services.SpaceCenter.Vessel;

import java.io.IOException;

public class HelloKrpc {
    public static void main(String[] args) throws IOException, RPCException {
        try (Connection connection = Connection.newInstance("Hello from Java")) {
            SpaceCenter spaceCenter = SpaceCenter.newInstance(connection);
            Vessel vessel = spaceCenter.getActiveVessel();
            System.out.println("Active vessel: " + vessel.getName());
        }
    }
}
