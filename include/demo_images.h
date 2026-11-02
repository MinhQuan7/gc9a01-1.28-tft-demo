#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DEMO_IMAGE_WIDTH 240
#define DEMO_IMAGE_HEIGHT 240
#define DEMO_IMAGE_BYTES (DEMO_IMAGE_WIDTH * DEMO_IMAGE_HEIGHT * 2)

extern const uint8_t img_1phongsang_map[];
extern const uint8_t img_2phongsang_map[];
extern const uint8_t img_3phongsang_map[];
extern const uint8_t img_tatcasang_map[];
extern const uint8_t img_toiom_map[];

#ifdef __cplusplus
}
#endif
