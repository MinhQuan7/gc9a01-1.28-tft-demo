#include "display_scene.h"

#include "demo_images.h"

#include <TFT_eSPI.h>

namespace
{

TFT_eSPI tft;

volatile uint8_t g_pendingScene = LIGHT_SCENE_OFF;
volatile uint8_t g_sceneDirty = 1;
uint8_t g_shownScene = 0xFF;

const uint8_t *imageForScene(uint8_t scene)
{
  switch (scene)
  {
  case LIGHT_SCENE_ROOM_1:
    return img_1phongsang_map;
  case LIGHT_SCENE_ROOM_2:
    return img_2phongsang_map;
  case LIGHT_SCENE_ROOM_3:
    return img_3phongsang_map;
  case LIGHT_SCENE_ALL:
    return img_tatcasang_map;
  case LIGHT_SCENE_OFF:
  default:
    return img_toiom_map;
  }
}

void blitScene(uint8_t scene)
{
  const uint8_t *pixels = imageForScene(scene);
  tft.pushImage(0, 0, DEMO_IMAGE_WIDTH, DEMO_IMAGE_HEIGHT,
                reinterpret_cast<const uint16_t *>(pixels));
}

}  // namespace

void displaySceneBegin()
{
  tft.init();
  tft.setRotation(0);
  tft.setSwapBytes(true);
  tft.fillScreen(TFT_BLACK);
  g_pendingScene = LIGHT_SCENE_OFF;
  g_shownScene = 0xFF;
  g_sceneDirty = 1;
}

void displaySceneRequest(LightScene scene)
{
  g_pendingScene = static_cast<uint8_t>(scene);
  g_sceneDirty = 1;
}

void displaySceneService()
{
  if (g_sceneDirty == 0)
  {
    return;
  }

  const uint8_t scene = g_pendingScene;
  if (scene == g_shownScene)
  {
    g_sceneDirty = 0;
    return;
  }

  blitScene(scene);
  g_shownScene = scene;
  if (g_pendingScene == scene)
  {
    g_sceneDirty = 0;
  }
}
