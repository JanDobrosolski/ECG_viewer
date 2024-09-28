import pygame
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from utils.signal_loader import SignalReader, AppleWatchSignalReader
from utils.constants import *


class ECGViewer:
    def __init__(self, signal_reader: SignalReader, signal_path: str, window_size=1536, window_step=128):
        self.signal_reader = signal_reader
        self.signal_path = signal_path
        self.window_size = window_size
        self.window_step = window_step
        self.signal_generator = signal_reader.stream_normalized_signal(signal_path, window_size, window_step)
        self.current_window = next(self.signal_generator, None)
        self.playing = False

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ECG Signal Viewer")

    def draw_sidebar(self):
        # Draw the sidebar area
        pygame.draw.rect(self.screen, GREY, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # Draw the sidebar title
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Menu", True, BLACK)
        self.screen.blit(text_surface, (20, 20))

        # Draw the sidebar border
        pygame.draw.line(self.screen, BLACK, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)

        # Add placeholder for menu items

    def draw_menu(self):
        # Fill background
        self.screen.fill(GREY)

        # Draw sidebar and window border
        self.draw_sidebar()

    def draw_signal(self, window_rect):
        if not self.current_window:
            return

        # Create the matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(window_rect.width / 100, window_rect.height / 100), dpi=100)
        ax.plot(self.current_window, color='blue')
        ax.set_ylim(-0.1, 1.1)  # Match the scale to the normalized signal range
        ax.set_xlim(0, len(self.current_window))
        ax.grid()
        y_ticks = np.arange(0, 1.1, 0.1)
        ax.set_yticks(y_ticks)
        ax.set_xticklabels([])

        # Draw the figure on a canvas
        canvas = FigureCanvas(fig)
        canvas.draw()

        # Get the raw RGBA data from the buffer
        raw_data = canvas.buffer_rgba()

        # Convert the raw data to a pygame surface
        size = canvas.get_width_height()
        signal_surface = pygame.image.frombuffer(raw_data, size, "RGBA")

        # Blit the surface onto the pygame screen
        self.screen.blit(signal_surface, (window_rect.left, window_rect.top))

        # Close the figure to release memory
        plt.close(fig)

    def next_frame(self):
        self.current_window = next(self.signal_generator, None)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        # Define the signal display window dimensions
        window_rect = pygame.Rect(SIDEBAR_WIDTH + 5, SCREEN_HEIGHT * 0.05, (SCREEN_WIDTH - SIDEBAR_WIDTH) * 0.95,
                                  SCREEN_HEIGHT * 0.9)

        self.draw_menu()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.next_frame()
                    elif event.key == pygame.K_SPACE:
                        self.playing = not self.playing

            if self.playing:
                self.next_frame()
                time.sleep(AUTO_DELAY_TIME)  # Add delay between frames when playing

            self.draw_signal(window_rect)
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
