#include <cassert>
#include <cstdio>

#include "../src/light_scene.h"

int main()
{
  assert(lightSceneFromDownlink("den_1", true) == LIGHT_SCENE_ROOM_1);
  assert(lightSceneFromDownlink("den_2", true) == LIGHT_SCENE_ROOM_2);
  assert(lightSceneFromDownlink("den_3", true) == LIGHT_SCENE_ROOM_3);
  assert(lightSceneFromDownlink("den_all", true) == LIGHT_SCENE_ALL);
  assert(lightSceneFromDownlink("DEN_1", true) == LIGHT_SCENE_ROOM_1);
  assert(lightSceneFromDownlink("den_1", false) == LIGHT_SCENE_OFF);
  assert(lightSceneFromDownlink("den_all", false) == LIGHT_SCENE_OFF);
  assert(lightSceneFromDownlink("unknown", true) == LIGHT_SCENE_OFF);
  assert(lightSceneFromDownlink(nullptr, true) == LIGHT_SCENE_OFF);
  std::puts("light_scene_test OK");
  return 0;
}
