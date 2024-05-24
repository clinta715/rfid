#include <WebUSB.h>

#include <deprecated.h>
#include <MFRC522Extended.h>
#include <require_cpp11.h>

#include <SPI.h>
#include <MFRC522.h>
//#include <Wire.h>

#define RST_PIN         9           // Configurable, see typical pin layout above
#define SS_PIN          10          // Configurable, see typical pin layout above
#define RST             3

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.
//MFRC522 mfrc522(0x3C, RST);

char data;

WebUSB WebUSBSerial(1 /* http:// */, "localhost:8000/ui");

#define WebSerial WebUSBSerial

void setup() {
    Serial.begin(9600); // Initialize serial communications with the PC
    while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
    SPI.begin();        // Init SPI bus
    //Wire.begin();
    
    mfrc522.PCD_Init(); // Init MFRC522 card
    delay(4);  

    WebSerial.begin(9600);
    WebSerial.write("Dairyland Labs RFID\r\n");
    WebSerial.flush();
}

void loop() {
    data = Serial.read();

    if(data == 'W' ) write_loop();
    if(data == 'R' ) read_loop();
}

void write_loop() {
    byte dataBlock[16];
  
    mfrc522.PCD_Init(); // Init MFRC522 card
    delay(4);  
    mfrc522.PICC_IsNewCardPresent();

    if ( ! mfrc522.PICC_ReadCardSerial()) {
      Serial.println(F("Error reading card serial!"));
      return;
    }
    
    MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
    
    for(int x = 0; x < 4; x++ ) dataBlock[x] = Serial.read();
    write_sampleid( dataBlock );

    for(int x = 0; x < 4; x++ ) dataBlock[x] = Serial.read();
    write_productid( dataBlock );

    for(int x = 0; x < 12; x++ ) dataBlock[x] = Serial.read();
    write_barcode( dataBlock );

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    data = 'A';

    read_loop();
}

void read_sampleid(char *sampleid) 
{
      byte status;
      byte pageAddr      = 10;
      byte buffer[18];
      byte size = sizeof(buffer);

      status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(pageAddr, buffer, &size);
      if (status != MFRC522::STATUS_OK) {
          Serial.println(F("Error reading sample ID!"));
          strcpy( sampleid, "ERR!" );
          return;
      }

     for( int x = 0; x < 4; x++) sampleid[x] = (char)buffer[x];
     sampleid[4] = '\0';
}

void read_productid(char *productid) 
{
      byte status;
      byte pageAddr      = 20;
      byte buffer[18];
      byte size = sizeof(buffer);
     
      status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(pageAddr, buffer, &size);
      if (status != MFRC522::STATUS_OK) {
          Serial.println(F("Error reading product ID!"));
          strcpy( productid, "ERR!" );
          return;
      }
      
      for( int x = 0; x < 4; x++) productid[x] = (char)buffer[x];
      productid[4] = '\0';
}

void read_dabarcode(char *barcode) 
{
      byte status;
      byte pageAddr      = 30;
      byte buffer[18];
      byte size = sizeof(buffer);
      
      status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(pageAddr, buffer, &size);
      if (status != MFRC522::STATUS_OK) {
          Serial.println(F("Error reading barcode!"));
          strcpy( barcode, "ERR!" );
          return;
      }

     for( byte x = 0; x < 12; x++) barcode[x] = (char)buffer[x];
     barcode[12] = '\0';
}

void write_sampleid( byte sampleid[] ) 
{
      byte status;
      byte pageAddr       = 10;
      byte buffer[18];
      byte size = sizeof(buffer);
      byte trailerBlock = 7;

      for (int i=0; i < 4; i++) buffer[i] = sampleid[i];

      status = (MFRC522::StatusCode) mfrc522.MIFARE_Ultralight_Write(pageAddr, &buffer[0], 4);
      
      if (status != MFRC522::STATUS_OK) Serial.print(F("Error writing sample ID!"));
}

void write_productid( byte productid[] ) 
{
      byte status;
      byte pageAddr      = 20;
      byte buffer[18];
      byte size = sizeof(buffer);
      byte trailerBlock = 7;

      for (int i=0; i < 4; i++) buffer[i] = productid[i];

      status = (MFRC522::StatusCode) mfrc522.MIFARE_Ultralight_Write(pageAddr, &buffer[0], 4);
  
      if (status != MFRC522::STATUS_OK) return;
}

void write_barcode( byte barcode[] ) 
{
      byte status = MFRC522::STATUS_OK;
      byte pageAddr      = 30;
      byte buffer[18];
      byte size = sizeof(buffer);
      byte trailerBlock = 7;

      for (int i=0; i < 12; i++) buffer[i] = barcode[i];

      for (int i=0; i < 3; i++) status = (MFRC522::StatusCode) mfrc522.MIFARE_Write(pageAddr + i, &buffer[i*4], 16);
}

void read_loop() {
      char barcode[19];
      char productid[19];
      char sampleid[19];

      mfrc522.PCD_Init(); // Init MFRC522 card
      delay(4);  
      
      mfrc522.PICC_IsNewCardPresent();
      if ( ! mfrc522.PICC_ReadCardSerial()) {
        Serial.println(F("Unable to read card serial!"));
        strcpy( sampleid, "ERR!" );
        strcpy( productid, "ERR!" );
        strcpy( barcode, "ERR!" );
      } else {
        MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
        read_sampleid( sampleid );
        read_productid( productid );
        read_dabarcode( barcode );
      }
      
      Serial.print(F("SID:"));
      Serial.println( sampleid );
      Serial.print(F("PID:"));
      Serial.println( productid );
      Serial.print(F("BAR:"));
      Serial.println( barcode ); 

      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();

      data = 'A';
}
 
