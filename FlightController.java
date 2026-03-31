public class FlightController {
    private double altitude;
    private double speed;
    
    public FlightController() {
        this.altitude = 0.0;
        this.speed = 0.0;
    }

    public void takeOff(double targetAltitude) {
        System.out.println("Taking off...");
        altitude = targetAltitude;
        speed = 250; // assuming a speed in units
        System.out.println("Reached altitude: " + altitude + " at speed: " + speed);
    }

    public void land() {
        System.out.println("Landing...");
        altitude = 0.0;
        speed = 0.0;
        System.out.println("Landed successfully.");
    }

    public void adjustSpeed(double newSpeed) {
        speed = newSpeed;
        System.out.println("Speed adjusted to: " + speed);
    }

    public double getAltitude() {
        return altitude;
    }

    public double getSpeed() {
        return speed;
    }

    public static void main(String[] args) {
        FlightController flightController = new FlightController();
        flightController.takeOff(10000); // Target altitude of 10,000 units
        flightController.adjustSpeed(300);
        flightController.land();
    }
}