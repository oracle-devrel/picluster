/*
 Circuit:
 * Ethernet shield attached to pins 10, 11, 12, 13
 * Solenoids pin 22, 24
*/

#include <SPI.h>
#include <Ethernet2.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

int ledPin = 22;

byte mac[] = {0xA8, 0x61, 0x0A, 0xAE, 0x12, 0x61};

EthernetServer server(80);

IPAddress ip();
//IPAddress ip(170, 20, 1, 20);

#define LED_COUNT  8
Adafruit_NeoPixel strip(LED_COUNT, ledPin, NEO_GRBW + NEO_KHZ800);

#define DELAYVAL 500

// NeoPixel brightness, 0 (min) to 255 (max)
#define BRIGHTNESS 50 // Set BRIGHTNESS to about 1/5 (max = 255)

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

//  pinMode(ledPin, OUTPUT);
//  digitalWrite(ledPin, LOW);
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.clear(); // Set all pixel colors to 'off'
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(BRIGHTNESS);
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
    Serial.println("connected");
    
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        content += c;
        if (c == '\n' && currentLineIsBlank) {
          client.println("HTTP/1.1 200 OK");
          //client.println("Content-Type: text/html");
          client.println("Content-Type: application/json");
          client.println("Connection: close");
          client.println("Refresh: 5");
          client.println();
          //client.println("<!DOCTYPE HTML>");
          //client.println("<html>");
          //client.println("</html>");
          client.println("{'status':'true'}");
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

    // Allocate the JSON document
    // https://arduinojson.org/v6/example/http-client/
    // https://arduinojson.org/v6/api/dynamicjsondocument/
    // Use arduinojson.org/v6/assistant to compute the capacity.
    //const size_t capacity = JSON_OBJECT_SIZE(4) + JSON_ARRAY_SIZE(5) + 60;
    //DynamicJsonDocument doc(capacity);
    DynamicJsonDocument doc(4096);
    
    // Parse JSON object
    DeserializationError error = deserializeJson(doc, client);
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      client.stop();
      return;
    }
    
    // Extract values
    // {"sensor":"yes", "time":"1234", "data": ["3.14", "6.92"]}
    Serial.println(F("Response:"));
    Serial.println(doc["sensor"].as<char*>());
    //Serial.println(doc["time"].as<long>());
    //Serial.println(doc["data"][0].as<long>());
    //Serial.println(doc["data"][1].as<long>());
    int index = doc["index"].as<long>();
    int r = doc["data"][0].as<long>();
    int g = doc["data"][1].as<long>();
    int b = doc["data"][2].as<long>();
    //int w = doc["data"][3].as<long>();

    // for (int i = 0; i < 3; i++) {
    //   Serial.println(doc["data"][i].as<char*>());

    // }
      
    // close the connection:
    client.stop();
    Serial.println("client disconnected");

    //strip.clear(); // Set all pixel colors to 'off'
    
    Serial.println(r);
    Serial.println(g);
    Serial.println(b);
    // The first NeoPixel in a strand is #0, second is 1, all the way up
    // to the count of pixels minus one.
    // for(int i = 0; i < LED_COUNT; i++) { // For each pixel...
    //   Serial.println("led");

    //   // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    //   // Here we're using a moderately bright green color:
    //   //strip.setPixelColor(i, r, g, b);
    //   strip.setPixelColor(i, r, g, b);

    //   strip.show();   // Send the updated pixel colors to the hardware.

    //   delay(DELAYVAL); // Pause before next pass through loop
    // }
    strip.setPixelColor(index, r, g, b);
    strip.show();   // Send the updated pixel colors to the hardware.
  }
}
