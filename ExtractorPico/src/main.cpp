#include <Arduino.h>
#include <AccelStepper.h>
#include <Stepper.h>

AccelStepper stepper(AccelStepper::FULL4WIRE, 8, 10, 9, 11);

typedef struct
{
  char direction; // 0:none 1:CW -1:CCW
  short speed;
} MotorData;

MotorData data;

void setup()
{
  Serial.begin(115200);
  data.direction = 0;
  data.speed = 0;

  stepper.setMaxSpeed(400.0);
  stepper.setAcceleration(100.0);
  stepper.setSpeed(data.direction * data.speed);

  Serial.flush();
}

void loop()
{
  if (Serial.available())
  {
    Serial.readBytes((byte *)&data, sizeof(MotorData));
    stepper.stop();
    if (data.direction != 0)
    {
      stepper.setSpeed(data.speed * (int8_t)data.direction);
    }
  }

  if (data.direction == 0)
  {
    stepper.stop();
  }
  else
  {
    stepper.runSpeed();
  }
}
