# import pygame
# import numpy as np
# import cv2
#
# # Load the test.npy file
# test_array = np.load("test.npy")
# test_image = cv2.imread("test.png").transpose(1, 0, 2)
#
# # Create pygame screen
# pygame.init()
# screen = pygame.display.set_mode((test_array.shape[1], test_array.shape[0]))
#
# # Blit the test_array to the screen
# pygame.surfarray.blit_array(screen, test_image)
# pygame.display.flip()
#
# # Wait for user input
# input()
#
# pygame.quit()

import cv2
import pygame
import numpy as np

OFFSET = 25

test_image = cv2.imread("test.png").transpose(1, 0, 2)
img_w, img_h, _ = test_image.shape

# Set up the Pygame window
pygame.init()
screen_width = 2 * img_w + 3 * OFFSET
screen_height = 2 * img_h + 3 * OFFSET
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Numpy Array Visualization')

# Create your numpy arrays (replace these with your own arrays)
# array1 = np.random.rand(100, 100, 3) * 255
# array2 = np.random.rand(100, 100, 3) * 255
# array3 = np.random.rand(100, 100, 3) * 255
# array4 = np.random.rand(100, 100, 3) * 255

# Calculate the size and position of each sub-plot
plot_width = screen_width // 2 + OFFSET // 2
plot_height = screen_height // 2 + OFFSET // 2

# Render the numpy arrays on the Pygame screen
screen.blit(pygame.surfarray.make_surface(test_image), (OFFSET, OFFSET))
screen.blit(pygame.surfarray.make_surface(test_image), (plot_width, OFFSET))
screen.blit(pygame.surfarray.make_surface(test_image), (OFFSET, plot_height))
screen.blit(pygame.surfarray.make_surface(test_image), (plot_width, plot_height))

# Update the Pygame display
pygame.display.flip()

# Wait for the user to close the window
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
pygame.quit()
