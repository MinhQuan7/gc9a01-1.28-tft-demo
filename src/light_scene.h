#pragma once

#include <stdint.h>

enum LightScene : uint8_t
{
  LIGHT_SCENE_OFF = 0,
  LIGHT_SCENE_ROOM_1 = 1,
  LIGHT_SCENE_ROOM_2 = 2,
  LIGHT_SCENE_ROOM_3 = 3,
  LIGHT_SCENE_ALL = 4,
};

inline bool lightStreamEquals(const char *left, const char *right)
{
  if (left == nullptr || right == nullptr)
  {
    return false;
  }
  while (*left != '\0' && *right != '\0')
  {
    unsigned char a = static_cast<unsigned char>(*left++);
    unsigned char b = static_cast<unsigned char>(*right++);
    if (a >= 'A' && a <= 'Z')
    {
      a = static_cast<unsigned char>(a + 32);
    }
    if (b >= 'A' && b <= 'Z')
    {
      b = static_cast<unsigned char>(b + 32);
    }
    if (a != b)
    {
      return false;
    }
  }
  return *left == *right;
}

inline LightScene lightSceneFromDownlink(const char *streamId, bool on)
{
  if (!on)
  {
    return LIGHT_SCENE_OFF;
  }
  if (lightStreamEquals(streamId, "den_1"))
  {
    return LIGHT_SCENE_ROOM_1;
  }
  if (lightStreamEquals(streamId, "den_2"))
  {
    return LIGHT_SCENE_ROOM_2;
  }
  if (lightStreamEquals(streamId, "den_3"))
  {
    return LIGHT_SCENE_ROOM_3;
  }
  if (lightStreamEquals(streamId, "den_all"))
  {
    return LIGHT_SCENE_ALL;
  }
  return LIGHT_SCENE_OFF;
}
