int x;
void setup() {
 Serial.begin(9600);
}
void loop() {
 while (Serial.available())
  {
     x = Serial.readString().toInt();
    Serial.println(x + 1);
  }
}
