/*
 Circuit:
 * Ethernet shield attached to pins 10, 11, 12, 13
 * Solenoids pin 22, 24
*/

#include <SPI.h>
#include <Ethernet2.h>

int resetSolenoidPin = 22;
int powerSolenoidPin = 24;

byte mac[] = {0xA8, 0x61, 0x0A, 0xAE, 0x12, 0x61};

EthernetServer server(80);

IPAddress ip();//192, 168, 3, 104);

void setup() {
  // Open serial communications and wait for port to open.
  Serial.begin(9600);

  // Start Ethernet connection.
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    for (;;) ;
  }

  // Start server.
  server.begin();
  Serial.print("server is at ");
  Serial.println(Ethernet.localIP());

  pinMode(resetSolenoidPin, OUTPUT);
  pinMode(powerSolenoidPin, OUTPUT);
  digitalWrite(resetSolenoidPin, LOW);
  digitalWrite(powerSolenoidPin, LOW);
}

void loop() {
  // DHCP support
  switch (Ethernet.maintain()) {
    case 1:
      // Renewed fail
      Serial.println("Error: renewed fail");
      break;

    case 2:
      // Renewed success
      Serial.println("Renewed success");
      //print your local IP address:
      Serial.print("My IP address: ");
      Serial.println(Ethernet.localIP());
      break;

    case 3:
      // Rebind fail
      Serial.println("Error: rebind fail");
      break;

    case 4:
      // Rebind success
      Serial.println("Rebind success");
      //print your local IP address:
      Serial.print("My IP address: ");
      Serial.println(Ethernet.localIP());
      break;

    default:
      // Nothing happened
      break;
  }

  // HTTP Support
  // Usage: curl http://<IPAddress>\?reset=1\&power=0
  EthernetClient client = server.available();
  
  if (client) {
    Serial.println("new client");
    // http request ends with a blank line
    boolean currentLineIsBlank = true;

    String content;
    
    while (client.connected()) {
      Serial.println("connected");
      
      if (client.available()) {
        char c = client.read();
        content += c;
        if (c == '\n' && currentLineIsBlank) {
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");
          client.println("Refresh: 5");
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          client.println("</html>");
          break;
        }
        if (c == '\n') {
          currentLineIsBlank = true;
        }
        else if (c != '\r') {
          currentLineIsBlank = false;
        }
      }
    }

    Serial.println("content");
    Serial.println(content);
    
    // give the web browser time to receive the data
    delay(1);
    
    // close the connection:
    client.stop(); //client.close();
    Serial.println("client disconnected");

    // Parse GET
    ParseGet(content);
  }
}

void switchSolenoid(int pin) {
    digitalWrite(pin, HIGH); // Switch Solenoid ON
    delay(1000);             // Wait 1 Second
    digitalWrite(pin, LOW);  // Switch Solenoid OFF
    delay(1000);             // Wait 1 Second
}

void ParseGet(String content) {
  Serial.println("ParseGet");
  Serial.println(content);
  int getIndex = content.indexOf("GET");

  if (getIndex == 0) {
    Serial.println("find GET");
    // Literally the laziest way to check for the value of the arguments.
    boolean resetState = content.indexOf("?reset=1&") > 0;
    boolean powerState = content.indexOf("&power=1") > 0;

    if (resetState) {
      switchSolenoid(resetSolenoidPin);
      Serial.println("reset");
    }

    if (powerState) {
      switchSolenoid(powerSolenoidPin);
      Serial.println("power");
    }
  }
}
