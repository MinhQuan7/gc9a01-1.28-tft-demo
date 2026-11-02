#define DTG_WIFI_GATEWAY_ONLY 1
#define DTG_FEATURE_NOCODE 0
#define DTG_FEATURE_MODBUS 0

#include <dtg.h>

#include "display_scene.h"
#include "light_scene.h"
#include "secrets.h"

DtgWiFi dtg(PROJECT_ID, GW_ALIAS, MQTT_USER, MQTT_PASS, CLIENT_ID);

namespace
{

void applyLightDownlink(const char *streamId, DtgParam &param)
{
  const bool on = param.getBool();
  displaySceneRequest(lightSceneFromDownlink(streamId, on));
  dtg.publish(streamId, on ? 1 : 0, true);
}

}  // namespace

DTG_LISTEN("den_1")
{
  applyLightDownlink("den_1", param);
}

DTG_LISTEN("den_2")
{
  applyLightDownlink("den_2", param);
}

DTG_LISTEN("den_3")
{
  applyLightDownlink("den_3", param);
}

DTG_LISTEN("den_all")
{
  applyLightDownlink("den_all", param);
}

DTG_CONNECTED()
{
  if (ENABLE_DEBUG)
    Serial.printf("DTG MQTT connected host=%s:%u client=%s\n", MQTT_HOST,
                  static_cast<unsigned>(MQTT_PORT), CLIENT_ID);
}

void setup()
{
  Serial.begin(115200);
  delay(80);

  displaySceneBegin();
  displaySceneService();

  if (ENABLE_DEBUG)
  {
    dtg.setBootStream(&Serial);
    dtg.setLogStream(&Serial);
  }
  // DtgWiFi always targets DTG_MQTT_HOST; MQTT_PORT only selects TLS (8883) vs plain (1883).
  dtg.begin(WIFI_SSID, WIFI_PASS, MQTT_PORT == 8883, false);
  dtg.enableHubCmd();
}

void loop()
{
  dtg.run();
  displaySceneService();
}
