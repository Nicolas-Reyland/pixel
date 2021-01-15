/* Pixel Project function in C */
#include <stdio.h>
#include <stdint.h>
#include <math.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// these are to be modified by a python script (and this has to be re-compiled)
#define SENSITIVITY 60
#define SRC_IMG_PATH "/home/ilu_vatar_/Pictures/Nic Ames/nick-ames-aftermath-noise-bright.jpg"
#define BG_IMG_PATH "/home/ilu_vatar_/Pictures/giant_wave_girl_resized.jpg"
#define RESULT_IMG_PATH "/home/ilu_vatar_/Pictures/output.jpg"
static const int TESTRGB[] = {123, 123, 123};

/* TODO:
 * optimize the code ?
 *
 */

int pixel_match(uint8_t (*rgb_source)[], int bpp) {
	for (register int i = 0; i < bpp; i++) {
		if (abs((*rgb_source)[i] - TESTRGB[i]) > SENSITIVITY) {
			return 0;
		}
	}

	return 1;
}

void pixelFunction() {

	// int gray_channels = channels == 4 ? 2 : 1; gray_channles = 2 if channels == 4 else 1

	int width1, height1, bpp1;
	unsigned char *img1 = stbi_load(SRC_IMG_PATH, &width1, &height1, &bpp1, 0);
	if (img1 == NULL) {
		printf("Error in loading image 1\n");
		exit(1);
	}
	size_t imsize = width1 * height1 * bpp1;
	//stbi_image_free(img1);
	int width2, height2, bpp2;
	unsigned char *img2 = stbi_load(BG_IMG_PATH, &width2, &height2, &bpp2, 0);
	if (img2 == NULL) {
		printf("Error in loading image 2\n");
		exit(1);
	}
	//stbi_image_free(img2);
	unsigned char *img3 = malloc(imsize);
	if (img3 == NULL) {
		printf("Unable to allocate memory for image 3\n");
		exit(1);
	}
	if (bpp1 != bpp2) {
		printf("RGB/RGBA cross-assigning implemented");
		exit(1);
	}

	for(unsigned char *p = img1, *pg = img3, *pg2 = img2; p != img1 + imsize; p += bpp1, pg += bpp2, pg2 += bpp2) {
		uint8_t pixel[] = {*p, *(p + 1), *(p + 2)};
		if (pixel_match(&pixel, bpp1)) {
			for (int i = 0; i < bpp1; i++) {
				*(pg + i) = *(pg2 + i);
			}
		} else {
			for (int i = 0; i < bpp1; i++) {
				*(pg + i) = *(p + i);
			}
		}
		/*
		*pg 	  = (uint8_t)fmin(0.393 * *p + 0.769 * *(p + 1) + 0.189 * *(p + 2), 255.0);			// red
		*(pg + 1) = (uint8_t)fmin(0.349 * *p + 0.686 * *(p + 1) + 0.168 * *(p + 2), 255.0);			// green
		*(pg + 2) = (uint8_t)fmin(0.272 * *p + 0.534 * *(p + 1) + 0.131 * *(p + 2), 255.0);			// blue
		*/
	}

	stbi_write_jpg(RESULT_IMG_PATH, width1, height1, bpp1, img3, 100);
}

int main() {
	pixelFunction();
	printf("pixelf: done\n");
	return 0;
}
