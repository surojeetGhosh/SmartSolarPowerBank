/*
  ZMPT101B - AC Voltage sensor
  Calculate Voltage

  modified on 7 Sep 2020
  by Mohammad Reza Akbari @ Electropeak
  Home
*/


double sensorValue1 = 0;
double sensorValue2 = 0;
int crosscount = 0;
int climb_flag = 0;
int val[100];
int max_v = 0;
double VmaxD = 0;
double VeffD = 0;
double Veff = 0;
double vCalliberation = 73;
double timePower = 0.00138889;
int kilo = 1e3;
double voltage;
double current;

void setup() {
  Serial.begin(9600);
}

void loop() {

  voltage = calculateVoltage();
  current = calculateCurrent();
  // Serial.println(current);
  Serial.println((voltage * current * timePower)/1e3, 8); // 1 unit = 1 kwh;
  delay(5000);
}

float calculateCurrent() {
  unsigned int x=0;
  float AcsValue=0.0,Samples=0.0,AvgAcs=0.0,AcsValueF=0.0;

  for (int x = 0; x < 150; x++){ 
    AcsValue = analogRead(A1);        
    Samples = Samples + AcsValue;  
    delay (3); 
  }
  AvgAcs=Samples/150.0;
  AcsValueF = (2.5 - (AvgAcs * (5.0 / 1024.0)) )/0.066;
  return AcsValueF;
}

float calculateVoltage() {
  for ( int i = 0; i < 100; i++ ) {
    sensorValue1 = analogRead(A0);
    if (sensorValue1 > 511) {
      val[i] = sensorValue1;
    }
    else {
      val[i] = 0;
    }
    delay(1);
  }

  max_v = 0;

  for ( int i = 0; i < 100; i++ )
  {
    if ( val[i] > max_v )
    {
      max_v = val[i];
    }
    val[i] = 0;
  }
  if (max_v != 0) {


    VmaxD = max_v;
    VeffD = VmaxD / sqrt(2);
    Veff = (((VeffD - 420.76) / -90.24) * -210.2) + 210.2;
  }
  else {
    Veff = 0;
  }
  
  VmaxD = 0;
  return Veff - vCalliberation;

}
