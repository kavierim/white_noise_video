import sys
import pygame
import time
import numpy as np  # added numpy import

# Application parameters
WIDTH, HEIGHT = 800, 600
PIXEL_SIZE = 1  # Set pixel size (1 = 1x1, 2 = 2x2, etc.)
# Fast refresh rate (left side) and slow refresh rate (right side) in Hz.
FAST_RATE = 120    # left side update rate (Hz)
SLOW_RATE = 1     # right side update rate (Hz)
# Set the pixel color mode: "grayscale" for random gray values, "bw" for black and white
COLOR_MODE = "bw" # "grayscale" or "bw"
TICK_RATE = 120  # added tick rate parameter

def get_refresh_period(x):
    """Calculate refresh period for column x based on linear interpolation.
    
    x is the x-coordinate (in pixels) of the block column.
    """
    rate = FAST_RATE + (SLOW_RATE - FAST_RATE) * (x / (WIDTH - 1))
    return 1.0 / rate

def generate_noise_column(pixel_size):
    """Create a noise column surface of size (pixel_size, HEIGHT) with random pixels using numpy.
    
    The column is filled with blocks of size pixel_size x pixel_size and covers full window height.
    """
    blocks = int(np.ceil(HEIGHT / pixel_size))
    if COLOR_MODE == "bw":
        noise = np.random.choice([0, 255], size=(blocks,))
    else:
        noise = np.random.randint(0, 256, size=(blocks,))
    # Generate a 1D array of length HEIGHT by repeating each block value pixel_size times and slicing to HEIGHT
    repeated = np.repeat(noise, pixel_size)[:HEIGHT]  # shape: (HEIGHT,)
    # Expand horizontally to pixel_size columns: shape (HEIGHT, pixel_size)
    col = np.tile(repeated[:, None], (1, pixel_size))
    # Transpose to shape (pixel_size, HEIGHT) for proper orientation
    col = col.T
    # Stack to RGB channels: shape (pixel_size, HEIGHT, 3)
    col = np.stack([col]*3, axis=-1)
    return pygame.surfarray.make_surface(col)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("White Noise Refresh Rate Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    num_cols = WIDTH // PIXEL_SIZE
    # For each block column, compute next update time and store its noise column surface.
    next_update = [time.time() + get_refresh_period(i * PIXEL_SIZE) for i in range(num_cols)]
    noise_columns = [generate_noise_column(PIXEL_SIZE) for _ in range(num_cols)]
    
    paused = False

    # Prepare refresh rate labels (e.g. 60, 50, 40, ... Hz)
    rates = []
    r = FAST_RATE
    while r >= SLOW_RATE:
        rates.append(r)
        r -= 10

    running = True
    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Space key toggles pause/play
                if event.key == pygame.K_SPACE:
                    paused = not paused
                # Escape key to quit
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not paused:
            # Update block columns that need refreshing
            for i in range(num_cols):
                if current_time >= next_update[i]:
                    noise_columns[i] = generate_noise_column(PIXEL_SIZE)
                    next_update[i] = current_time + get_refresh_period(i * PIXEL_SIZE)
        
        # Draw noise columns onto screen
        for i in range(num_cols):
            screen.blit(noise_columns[i], (i * PIXEL_SIZE, 0))
        
        # Draw dark overlay at top for text readability
        top_annotation_height = 30
        overlay_top = pygame.Surface((WIDTH, top_annotation_height))
        overlay_top.set_alpha(150)
        overlay_top.fill((0, 0, 0))
        screen.blit(overlay_top, (0, 0))
        
        # Get fps value and choose text color depending on FPS.
        current_fps = clock.get_fps()
        color = (255, 0, 0) if round(current_fps) != 60 else (255, 255, 255)
        fps_text = font.render(f"FPS: {current_fps:.2f}", True, color)
        screen.blit(fps_text, (10, 10))
        
        # Draw reference lines and labels at the bottom for refresh rates.
        bottom_annotation_height = 30
        # Draw a semi-transparent overlay to ensure readability.
        overlay = pygame.Surface((WIDTH, bottom_annotation_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, HEIGHT - bottom_annotation_height))
        
        for rate in rates:
            # Invert the interpolation to get x position for a given rate:
            # rate = FAST_RATE + (SLOW_RATE - FAST_RATE) * (x/(WIDTH-1))
            # => x = ((rate - FAST_RATE) / (SLOW_RATE - FAST_RATE)) * (WIDTH-1)
            x = int(((rate - FAST_RATE) / (SLOW_RATE - FAST_RATE)) * (WIDTH - 1))
            # Draw a vertical tick line
            pygame.draw.line(screen, (255, 255, 255), (x, HEIGHT - bottom_annotation_height), (x, HEIGHT), 2)
            # Render and center the rate label below the tick line
            rate_text = font.render(f"{rate} Hz", True, (255, 255, 255))
            text_rect = rate_text.get_rect(center=(x, HEIGHT - bottom_annotation_height // 2))
            screen.blit(rate_text, text_rect)
        
        pygame.display.flip()
        clock.tick(TICK_RATE)  # limit main loop to TICK_RATE FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()